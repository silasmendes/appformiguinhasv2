"""Exercise real SQLite files, authentication, reports and pre-registration."""
from datetime import date, datetime, timedelta
import importlib

import pytest
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash

from app import db
from config import Config


@pytest.fixture(scope='module')
def local_app(tmp_path_factory):
    directory = tmp_path_factory.mktemp('sqlite')
    overrides = {
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{(directory / 'main.db').as_posix()}",
        'SQLALCHEMY_PRE_CADASTRO_URI': f"sqlite:///{(directory / 'pre.db').as_posix()}",
        'SESSION_FILE_DIR': str(directory / 'sessions'),
    }
    original = {key: getattr(Config, key) for key in overrides}
    for key, value in overrides.items():
        setattr(Config, key, value)
    try:
        app = importlib.import_module('main').app
        app.config['TESTING'] = True
        from app.models.usuario import Usuario
        from app.models.familia import Familia
        from app.models.endereco import Endereco
        from app.models.atendimento import Atendimento
        from app.models.demanda_tipo import DemandaTipo
        from app.models.demanda_familia import DemandaFamilia
        from app.models.demanda_etapa import DemandaEtapa
        with app.app_context():
            db.create_all()
            db.session.add(Usuario(login='admin', nome_completo='Local Admin', tipo='admin',
                                   senha_hash=generate_password_hash('test-password')))
            family = Familia(nome_responsavel='SQLite Family', cpf='794.134.270-70')
            db.session.add(family)
            db.session.flush()
            db.session.add(Endereco(familia_id=family.familia_id, bairro='Centro'))
            db.session.add(Atendimento(familia_id=family.familia_id, cesta_entregue=True,
                                      percepcao_necessidade='Alta', data_entrega_cesta=date.today()))
            db.session.add(Familia(nome_responsavel='No recent attendance'))
            old_family = Familia(nome_responsavel='Old attendance')
            db.session.add(old_family)
            db.session.flush()
            db.session.add(Atendimento(familia_id=old_family.familia_id,
                                      data_hora_atendimento=datetime.now() - timedelta(days=100)))
            db.session.add(DemandaTipo(demanda_tipo_id=1, demanda_tipo_nome='Medicamentos'))
            demand = DemandaFamilia(familia_id=family.familia_id, demanda_tipo_id=1,
                                    data_identificacao=date.today(), prioridade='Alta')
            db.session.add(demand)
            db.session.flush()
            db.session.add(DemandaEtapa(demanda_id=demand.demanda_id, status_atual='Em análise'))
            db.session.commit()
            engine = create_engine(app.config['SQLALCHEMY_PRE_CADASTRO_URI'])
            db.metadata.create_all(engine)
            with engine.begin() as conn:
                conn.execute(Familia.__table__.insert().values(
                    nome_responsavel='Pre-registration Example', cpf='123.456.789-00'))
            engine.dispose()
        yield app
    finally:
        if 'app' in locals():
            with app.app_context():
                db.session.remove()
                db.engine.dispose()
            pre_engine = app.extensions.get('pre_cadastro_engine')
            if pre_engine:
                pre_engine.dispose()
        for key, value in original.items():
            setattr(Config, key, value)


@pytest.fixture
def client(local_app):
    with local_app.test_client() as client:
        response = client.post('/login', data={'login': 'admin', 'senha': 'test-password'})
        assert response.status_code == 302
        yield client


def test_family_crud_and_persistence(client, local_app):
    response = client.post('/familias', json={'nome_responsavel': 'Local CRUD',
                                            'autoriza_uso_imagem': True})
    assert response.status_code == 201
    family_id = response.json['familia_id']
    with local_app.app_context():
        db.session.remove()
    assert client.get(f'/familias/{family_id}').json['nome_responsavel'] == 'Local CRUD'
    assert client.put(f'/familias/{family_id}', json={'nome_responsavel': 'Updated'}).status_code == 200
    assert client.delete(f'/familias/{family_id}').status_code == 200
    assert client.get(f'/familias/{family_id}').status_code == 404


@pytest.mark.parametrize('path', [
    '/', '/menu_atendimento?q=SQLite', '/dashboard',
    '/dashboard/demandas-ativas', '/dashboard/familias-cadastradas',
    '/dashboard/familias-atendidas-30-dias', '/dashboard/entregas-cestas-30-dias',
    '/dashboard/familias-sem-atendimento-recente',
    '/dashboard/familias-maior-vulnerabilidade', '/dashboard/painel-demandas',
])
def test_pages_with_sqlite_records(client, path):
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.parametrize('report', [
    'painel-demandas', 'familias-cadastradas', 'familias-atendidas-30-dias',
    'entregas-cestas-30-dias', 'familias-sem-atendimento-recente',
    'demandas-ativas', 'familias-maior-vulnerabilidade',
])
def test_excel_exports(client, report):
    response = client.get(f'/dashboard/{report}/download')
    assert response.status_code == 200
    assert response.data.startswith(b'PK')


def test_pre_registration_uses_separate_sqlite_database(local_app):
    from app.utils.pre_cadastro import buscar_pre_cadastros, converter_pre_cadastro_para_sessao
    with local_app.app_context():
        results = buscar_pre_cadastros('Pre-registration')
        assert len(results) == 1
        converted = converter_pre_cadastro_para_sessao(results[0]['dados_completos'])
        assert converted['nome_responsavel'] == 'Pre-registration Example'
        assert buscar_pre_cadastros('SQLite Family') == []


def test_initialization_preserves_existing_admin(local_app, monkeypatch):
    from click.testing import CliRunner
    import manage
    from app.models.usuario import Usuario
    monkeypatch.setattr(manage, 'app', local_app)
    with local_app.app_context():
        original_hash = Usuario.query.filter_by(login='admin').one().senha_hash
    runner = CliRunner()
    for _ in range(2):
        result = runner.invoke(manage.initialize, ['--admin-password', 'different-password'])
        assert result.exit_code == 0, result.output
    with local_app.app_context():
        assert Usuario.query.filter_by(login='admin').one().senha_hash == original_hash


def test_seed_forms_do_not_render_none(client, local_app, monkeypatch):
    import re
    import app.utils.template_helpers as helpers
    from seeds.familias_seed import seed_familias, FAMILIAS_TESTE
    from app.models.familia import Familia
    monkeypatch.setattr(helpers, 'gerar_resumo_familia', lambda cadastro: '')
    with local_app.app_context():
        seed_familias()
        ids = [Familia.query.filter_by(cpf=cpf).one().familia_id for cpf, *_ in FAMILIAS_TESTE]
        # Simulate a pre-fix seed that was opened and saved with the text "None".
        family = db.session.get(Familia, ids[0])
        family.rg = 'None'
        db.session.commit()
    for family_id in ids:
        assert client.get(f'/atendimento_familia/{family_id}').status_code == 302
        with client.session_transaction() as session:
            assert session['cadastro']['rg'] == ''
        for step in range(1, 10):
            response = client.get(f'/atendimento/etapa{step}')
            assert response.status_code == 200
            html = response.get_data(as_text=True)
            assert not re.search(r'value=[\"\']None[\"\']', html), (family_id, step)
            assert not re.search(r'<textarea\b[^>]*>\s*None\s*</textarea>', html), (family_id, step)
