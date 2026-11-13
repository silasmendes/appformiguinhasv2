import importlib
import sys
from unittest.mock import patch

import pytest

from app import create_app, db
from app.models.familia import Familia
from app.models.contato import Contato


@pytest.fixture
def ficha_app(tmp_path):
    app = create_app({
        'TESTING': True, 'ENV': 'development', 'SECRET_KEY': 'teste-ficha',
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'SQLALCHEMY_PRE_CADASTRO_URI': 'sqlite://',
        'SESSION_FILE_DIR': str(tmp_path), 'LOGIN_DISABLED': True,
    })
    previous = sys.modules.pop('main', None)
    with patch('app.create_app', return_value=app):
        importlib.import_module('main')
    with app.app_context():
        db.create_all()
        db.session.add(Familia(familia_id=5, nome_responsavel='<script>alert(1)</script>', autoriza_uso_imagem=False))
        db.session.add(Contato(familia_id=5, telefone_principal='99999', telefone_principal_whatsapp=False))
        db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()
    sys.modules.pop('main', None)
    if previous is not None:
        sys.modules['main'] = previous


def test_ficha_preserva_sessao_e_escapa_dados(ficha_app):
    client = ficha_app.test_client()
    contexto = {'familia_id': 99, 'cadastro': {'nome_responsavel': 'Outra família', 'novo_cadastro': 0}, 'cadastro_inicio': '2026-11-13', 'resumo_expandido': 0}
    with client.session_transaction() as sess:
        sess.update(contexto)
    response = client.get('/familia/5')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html
    assert '99999' in html
    assert 'Não informado' in html
    assert '>Não<' in html
    assert 'href="/atendimento_familia/5"' in html
    assert 'Nenhuma demanda ativa registrada.' in html
    assert 'familySummaryContent' not in html
    with client.session_transaction() as sess:
        for key, value in contexto.items():
            assert sess[key] == value


def test_ficha_inexistente(ficha_app):
    assert ficha_app.test_client().get('/familia/999').status_code == 404


def test_ficha_exige_login(ficha_app):
    ficha_app.config['LOGIN_DISABLED'] = False
    response = ficha_app.test_client().get('/familia/5')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
