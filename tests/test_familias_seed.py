from pathlib import Path
import re

import pytest

from app import create_app, db
from app.models.familia import Familia
from seeds.familias_seed import FAMILIAS_TESTE, MODELOS_COMPLEMENTARES, seed_familias
from app.models.endereco import Endereco
from app.models.contato import Contato
from app.models.composicao_familiar import ComposicaoFamiliar
from app.models.condicoes_moradia import CondicaoMoradia
from app.models.saude_familiar import SaudeFamiliar
from app.models.emprego_provedor import EmpregoProvedor
from app.models.renda_familiar import RendaFamiliar
from app.models.educacao_entrevistado import EducacaoEntrevistado
from app.models.atendimento import Atendimento
from app.utils.fluxo_atendimento import carregar_cadastro_familia


@pytest.fixture
def app(tmp_path):
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{(tmp_path / 'familias.db').as_posix()}",
        'SESSION_FILE_DIR': str(tmp_path / 'sessions'),
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.engine.dispose()


def test_seed_matches_modal_and_loads_complete_families(app):
    modal = Path(app.root_path) / app.template_folder / 'atendimento' / 'etapa0_menu.html'
    expected = set(re.findall(r'\d{3}\.\d{3}\.\d{3}-\d{2}', modal.read_text(encoding='utf-8')))
    assert expected == {row[0] for row in FAMILIAS_TESTE}
    assert seed_familias() == 4
    assert {family.cpf for family in Familia.query.all()} == expected
    for family in Familia.query.all():
        for model in (Endereco, Contato, ComposicaoFamiliar, CondicaoMoradia,
                      SaudeFamiliar, EmpregoProvedor, RendaFamiliar,
                      EducacaoEntrevistado, Atendimento):
            assert model.query.filter_by(familia_id=family.familia_id).count() == 1
        with app.test_request_context():
            cadastro = carregar_cadastro_familia(family.familia_id)
            assert cadastro['cpf'] == family.cpf
            assert cadastro['novo_cadastro'] == 0
        response = app.test_client().get('/familias/busca', query_string={'q': family.cpf})
        assert response.status_code == 200
        assert response.json[0]['familia_id'] == family.familia_id
        for record in [family] + [model.query.filter_by(familia_id=family.familia_id).one()
                                   for model in MODELOS_COMPLEMENTARES]:
            for column in record.__table__.columns:
                if column.nullable and isinstance(column.type, db.String):
                    assert getattr(record, column.name) not in (None, 'None')


def test_seed_preserves_edits_and_recognizes_unformatted_cpf(app):
    assert seed_familias() == 4
    family = Familia.query.filter_by(cpf=FAMILIAS_TESTE[0][0]).one()
    family.nome_responsavel = 'Nome alterado durante os testes'
    family.cpf = re.sub(r'\D', '', family.cpf)
    db.session.commit()
    assert seed_familias() == 0
    assert Familia.query.count() == 4
    assert Atendimento.query.count() == 4
    assert family.nome_responsavel == 'Nome alterado durante os testes'


def test_seed_adds_missing_families_without_changing_existing_data(app):
    existing = Familia(cpf=FAMILIAS_TESTE[1][0], nome_responsavel='Cadastro existente')
    unrelated = Familia(cpf='111.111.111-11', nome_responsavel='Outra família')
    db.session.add_all([existing, unrelated])
    db.session.commit()
    assert seed_familias() == 3
    assert Familia.query.count() == 5
    assert existing.nome_responsavel == 'Cadastro existente'
    assert unrelated.nome_responsavel == 'Outra família'
    assert Atendimento.query.filter_by(familia_id=existing.familia_id).count() == 0


def test_seed_repairs_legacy_empty_text_without_changing_filled_values(app):
    seed_familias()
    family = Familia.query.filter_by(cpf=FAMILIAS_TESTE[0][0]).one()
    family.rg = 'None'
    family.genero_autodeclarado = None
    contact = Contato.query.filter_by(familia_id=family.familia_id).one()
    contact.telefone_principal = None
    contact.telefone_alternativo_nome_contato = 'None'
    address = Endereco.query.filter_by(familia_id=family.familia_id).one()
    address.ponto_referencia = 'Referência editada pelo usuário'
    other = Familia(nome_responsavel='Cadastro manual', rg=None)
    db.session.add(other)
    db.session.commit()
    assert seed_familias() == 0
    assert family.rg == ''
    assert family.genero_autodeclarado == ''
    assert contact.telefone_principal == ''
    assert contact.telefone_alternativo_nome_contato == ''
    assert address.ponto_referencia == 'Referência editada pelo usuário'
    assert other.rg is None


def test_loading_absent_values_preserves_zero_and_false(app):
    from app.utils.fluxo_atendimento import normalizar_campos_formulario
    assert normalizar_campos_formulario({
        'rg': None, 'telefone': 'None', 'total': 0, 'autoriza': False,
        'demandas': [{'observacao': None}],
    }) == {'rg': '', 'telefone': '', 'total': 0, 'autoriza': False,
           'demandas': [{'observacao': ''}]}
    family = Familia(nome_responsavel='Cadastro sem opcionais', rg=None)
    db.session.add(family)
    db.session.commit()
    with app.test_request_context():
        cadastro = carregar_cadastro_familia(family.familia_id)
        assert cadastro['rg'] == ''
        assert cadastro['nome_mae'] == ''
