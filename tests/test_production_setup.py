import secrets

from click.testing import CliRunner
import pytest
from werkzeug.security import check_password_hash

from app import create_app, db
from app.models.familia import Familia
from app.models.usuario import Usuario
from app.models.demanda_tipo import DemandaTipo


@pytest.fixture
def production_app(tmp_path):
    app = create_app({
        'TESTING': True, 'ENV': 'production', 'DEBUG': True,
        'SECRET_KEY': secrets.token_hex(32),
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{(tmp_path / 'main.db').as_posix()}",
        'SQLALCHEMY_PRE_CADASTRO_URI': f"sqlite:///{(tmp_path / 'pre.db').as_posix()}",
        'SESSION_FILE_DIR': str(tmp_path / 'sessions'),
    })
    yield app
    with app.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.mark.parametrize('secret', ['', 'dev', 'SUBSTITUA_POR_UM_SEGREDO_ALEATORIO',
                                    'chave-ficticia-de-desenvolvimento-troque-em-producao'])
def test_production_rejects_missing_or_example_secret(secret):
    with pytest.raises(ValueError, match='SECRET_KEY'):
        create_app({'ENV': 'production', 'SECRET_KEY': secret})


def test_production_disables_debug_and_secures_cookies(production_app):
    assert production_app.debug is False
    for prefix in ('SESSION', 'REMEMBER'):
        assert production_app.config[f'{prefix}_COOKIE_SECURE'] is True
        assert production_app.config[f'{prefix}_COOKIE_HTTPONLY'] is True
        assert production_app.config[f'{prefix}_COOKIE_SAMESITE'] == 'Lax'


def test_initialization_without_demo_is_idempotent_and_persists_login(production_app, monkeypatch):
    import manage
    monkeypatch.setattr(manage, 'app', production_app)
    runner = CliRunner()
    result = runner.invoke(manage.initialize, ['--admin-password', 'My-own-test-password-123'])
    assert result.exit_code == 0, result.output
    with production_app.app_context():
        assert Familia.query.count() == 0
        assert DemandaTipo.query.count() == 7
        assert check_password_hash(Usuario.query.one().senha_hash, 'My-own-test-password-123')
    monkeypatch.delenv('SENHA_ADMIN', raising=False)
    result = runner.invoke(manage.initialize, [])
    assert result.exit_code == 0, result.output
    # This factory-only test needs the redirect target normally registered by main.py.
    production_app.add_url_rule('/menu_atendimento', endpoint='menu_atendimento', view_func=lambda: 'ok')
    client = production_app.test_client()
    response = client.post('/login', base_url='https://localhost',
                           data={'login': 'admin', 'senha': 'My-own-test-password-123'})
    assert response.status_code == 302
    cookie = response.headers['Set-Cookie']
    assert 'Secure' in cookie and 'HttpOnly' in cookie and 'SameSite=Lax' in cookie
    # Create a second application against the same files, simulating a restart.
    restarted = create_app(dict(production_app.config))
    with restarted.app_context():
        assert Usuario.query.count() == 1
        assert Familia.query.count() == 0
        db.session.remove()
        db.engine.dispose()


def test_demo_requires_explicit_flag(production_app, monkeypatch):
    import manage
    monkeypatch.setattr(manage, 'app', production_app)
    result = CliRunner().invoke(manage.initialize,
                               ['--admin-password', 'My-own-test-password-123', '--with-demo-data'])
    assert result.exit_code == 0, result.output
    with production_app.app_context():
        assert Familia.query.count() == 4


@pytest.mark.parametrize('password', ['short', 'FormiguinhasLocal123!', 'SUBSTITUA_POR_UMA_SENHA_FORTE'])
def test_production_rejects_initial_example_password(production_app, monkeypatch, password):
    import manage
    monkeypatch.setattr(manage, 'app', production_app)
    result = CliRunner().invoke(manage.initialize, ['--admin-password', password])
    assert result.exit_code != 0
    assert 'senha de produção' in result.output
