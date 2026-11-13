"""Exercise real SQLite files, authentication, reports and pre-registration."""
from datetime import date, datetime, timedelta
import importlib.util
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse

from openpyxl import load_workbook

import pytest
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash

from app import db
from config import Config


@pytest.fixture
def local_app(tmp_path, monkeypatch):
    # A fresh application and two databases per test: no ordering dependencies.
    directory = tmp_path
    import socket

    def reject_network(*args, **kwargs):
        pytest.fail('O teste integrado tentou acessar a rede; use dados locais ou um stub explícito.')

    monkeypatch.setattr(socket.socket, 'connect', reject_network)
    monkeypatch.setattr(socket.socket, 'connect_ex', reject_network)
    overrides = {
        'TESTING': True, 'ENV': 'development',
        'SECRET_KEY': 'isolated-test-secret', 'SESSION_COOKIE_SECURE': False,
        'OPENAI_API_KEY': '',
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{(directory / 'main.db').as_posix()}",
        'SQLALCHEMY_PRE_CADASTRO_URI': f"sqlite:///{(directory / 'pre.db').as_posix()}",
        'SESSION_FILE_DIR': str(directory / 'sessions'),
    }
    for key, value in overrides.items():
        monkeypatch.setattr(Config, key, value, raising=False)
    import app.utils.template_helpers as helpers
    monkeypatch.setattr(helpers, 'gerar_resumo_familia', lambda cadastro: '')
    try:
        # Execute main's real route registration without reusing a cached main.app.
        spec = importlib.util.spec_from_file_location(
            'sqlite_test_main', Path(__file__).resolve().parents[1] / 'main.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        app = module.app
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
    assert client.get(f'/familias/{family_id}').json['nome_responsavel'] == 'Updated'
    assert client.get(f'/familias/{family_id}').json['autoriza_uso_imagem'] is True
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
    assert 'attachment' in response.headers['Content-Disposition']
    workbook = load_workbook(BytesIO(response.data), read_only=True, data_only=True)
    try:
        rows = list(workbook.active.values)
        assert len(rows) >= 2, f'{report}: exportação sem registros'
        names = {value for row in rows[1:] for value in row if isinstance(value, str)}
        expected = ({'No recent attendance', 'Old attendance'}
                    if report == 'familias-sem-atendimento-recente'
                    else {'SQLite Family', 'No recent attendance', 'Old attendance'}
                    if report == 'familias-cadastradas' else {'SQLite Family'})
        assert names & {'SQLite Family', 'No recent attendance', 'Old attendance'} == expected
        assert len(rows) == len(expected) + 1, f'{report}: linhas ausentes ou duplicadas'
    finally:
        workbook.close()


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

@pytest.mark.parametrize('path', ['/', '/dashboard', '/menu_atendimento',
                                 '/atendimento/etapa1', '/dashboard/familias-cadastradas/download'])
def test_private_pages_require_login(local_app, path):
    response = local_app.test_client().get(path)
    assert response.status_code == 302
    assert urlparse(response.location).path == '/login'


def test_wrong_password_and_logout_remove_access(local_app):
    client = local_app.test_client()
    response = client.post('/login', data={'login': 'admin', 'senha': 'wrong-password'})
    assert response.status_code == 200
    assert 'Credenciais inválidas' in response.get_data(as_text=True)
    assert urlparse(client.get('/dashboard').location).path == '/login'
    client.post('/login', data={'login': 'admin', 'senha': 'test-password'})
    assert client.get('/dashboard').status_code == 200
    client.get('/logout')
    assert urlparse(client.get('/dashboard').location).path == '/login'


@pytest.mark.parametrize('report,expected', [
    ('familias-atendidas-30-dias', {'SQLite Family'}),
    ('entregas-cestas-30-dias', {'SQLite Family'}),
    ('familias-sem-atendimento-recente', {'No recent attendance', 'Old attendance'}),
    ('familias-maior-vulnerabilidade', {'SQLite Family'}),
    ('demandas-ativas', {'SQLite Family'}),
    ('painel-demandas', {'SQLite Family'}),
])
def test_report_includes_only_matching_families(client, report, expected):
    response = client.get(f'/dashboard/{report}')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for name in {'SQLite Family', 'No recent attendance', 'Old attendance'}:
        assert (name in html) == (name in expected), (report, name)


def test_attendance_persists_and_uses_logged_in_operator(client, local_app):
    family = client.post('/familias', json={'nome_responsavel': 'Attendance Example'}).json
    payload = {'familia_id': family['familia_id'], 'percepcao_necessidade': 'Alta',
               'cesta_entregue': True, 'data_entrega_cesta': date.today().isoformat(),
               'usuario_atendente_id': 99999}
    response = client.post('/atendimentos', json=payload)
    assert response.status_code == 201, response.json
    attendance_id = response.json['atendimento_id']
    with local_app.app_context():
        from app.models.usuario import Usuario
        operator_id = Usuario.query.filter_by(login='admin').one().id
        db.session.remove()
    saved = client.get(f'/atendimentos/{attendance_id}').json
    assert saved['familia_id'] == family['familia_id']
    assert saved['usuario_atendente_id'] == operator_id
    assert saved['cesta_entregue'] is True
    assert saved['data_entrega_cesta'] == payload['data_entrega_cesta']
    assert [r['atendimento_id'] for r in client.get(
        f"/atendimentos?familia_id={family['familia_id']}").json] == [attendance_id]
    invalid = client.post('/atendimentos', json={**payload, 'percepcao_necessidade': 'Invalid'})
    assert invalid.status_code == 400
    assert len(client.get(f"/atendimentos?familia_id={family['familia_id']}").json) == 1


@pytest.mark.parametrize('route,id_key,values', [
    ('enderecos', 'endereco_id', {'bairro': 'Bairro Integração', 'preenchimento_manual': True}),
    ('contatos', 'contato_id', {'email_responsavel': 'integration@example.com',
                               'telefone_principal_whatsapp': False}),
    ('composicao_familiar', 'composicao_id', {'total_residentes': 4, 'quantidade_criancas': 2}),
    ('condicoes_moradia', 'moradia_id', {'tipo_moradia': 'Alugada', 'tem_agua_encanada': True}),
    ('educacao_entrevistado', 'educacao_id', {'nivel_escolaridade': 'Ensino Médio',
                                          'estuda_atualmente': 'Não'}),
    ('emprego_provedor', 'emprego_id', {'profissao_provedor': 'Motorista'}),
    ('renda_familiar', 'renda_id', {'renda_total_familiar': '3000.50', 'possui_cadastro_unico': True}),
    ('saude_familiar', 'saude_id', {'tem_doenca_cronica': True,
                                  'descricao_doenca_cronica': 'Hipertensão'}),
])
def test_registration_sections_preserve_values_and_family_link(client, local_app, route, id_key, values):
    family_id = client.post('/familias', json={'nome_responsavel': 'Cadastro Integração'}).json['familia_id']
    response = client.post(f'/{route}', json={'familia_id': family_id, **values})
    assert response.status_code == 201, response.json
    record_id = response.json[id_key]
    with local_app.app_context():
        db.session.remove()
    saved = client.get(f'/{route}/{record_id}')
    assert saved.status_code == 200
    assert saved.json['familia_id'] == family_id
    for key, value in values.items():
        assert saved.json[key] == value, (route, key)
    # Loading the family's actual form must recover the data from the database.
    assert client.get(f'/atendimento_familia/{family_id}').status_code == 302
    field = next(iter(values))
    session_field = {'renda_total_familiar': 'renda_familiar_total'}.get(field, field)
    expected_form_value = 'Sim' if field == 'tem_doenca_cronica' else values[field]
    with client.session_transaction() as session:
        assert session['cadastro'][session_field] == expected_form_value
    assert client.get('/atendimento/etapa1').status_code == 200


def test_family_survives_application_restart(client, local_app):
    from app import create_app
    family_id = client.post('/familias', json={'nome_responsavel': 'Persistência após reinício'}).json['familia_id']
    restarted = create_app(dict(local_app.config))
    try:
        response = restarted.test_client().get(f'/familias/{family_id}')
        assert response.status_code == 200
        assert response.json['nome_responsavel'] == 'Persistência após reinício'
    finally:
        with restarted.app_context():
            db.session.remove()
            db.engine.dispose()
        restarted.extensions['pre_cadastro_engine'].dispose()


def test_demand_creation_records_initial_history_and_rejects_invalid_type(client, local_app):
    from app.models.demanda_etapa import DemandaEtapa
    from app.models.demanda_familia import DemandaFamilia
    from app.models.usuario import Usuario
    family_id = client.post('/familias', json={'nome_responsavel': 'Demandas Integração'}).json['familia_id']
    payload = {'familia_id': family_id, 'demanda_tipo_id': 1,
               'descricao': 'Medicamento necessário', 'data_identificacao': date.today().isoformat()}
    response = client.post('/demandas', json=payload)
    assert response.status_code == 201, response.json
    demand_id = response.json['demanda_id']
    assert response.json['status'] == 'Em análise'
    with local_app.app_context():
        db.session.remove()
        history = DemandaEtapa.query.filter_by(demanda_id=demand_id).one()
        assert history.status_atual == 'Em análise'
        assert history.usuario_atendente_id == Usuario.query.filter_by(login='admin').one().id
    assert client.post('/demandas', json={**payload, 'demanda_tipo_id': 999}).status_code == 400
    with local_app.app_context():
        assert DemandaFamilia.query.filter_by(familia_id=family_id).count() == 1
        assert DemandaEtapa.query.filter_by(demanda_id=demand_id).count() == 1
