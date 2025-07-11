import pytest
from app import create_app

_familia_id = None
_demanda1_id = None
_demanda2_id = None


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_cadastro_completo(client):
    # Cadastro de família
    familia_payload = {
        "nome_responsavel": "Ana de Teste",
        "data_nascimento": "1985-05-10",
        "genero": "Feminino",
        "estado_civil": "Casada(o)",
        "rg": "123456789",
        "cpf": "829.438.580-80",
        "autoriza_uso_imagem": True,
    }

    resp_familia = client.post("/familias", json=familia_payload)
    assert resp_familia.status_code == 201
    familia_id = resp_familia.get_json()["familia_id"]

    # Endereço
    endereco_payload = {
        "familia_id": familia_id,
        "cep": "13010-000",
        "preenchimento_manual": True,
        "logradouro": "Rua das Flores",
        "numero": "123",
        "complemento": "Casa",
        "bairro": "Centro",
        "cidade": "Campinas",
        "estado": "SP",
        "ponto_referencia": "Próximo à praça central",
    }
    resp_endereco = client.post("/enderecos", json=endereco_payload)
    assert resp_endereco.status_code == 201
    endereco_id = resp_endereco.get_json()["endereco_id"]

    # Contato
    contato_payload = {
        "familia_id": familia_id,
        "telefone_principal": "(19) 98765-4321",
        "telefone_principal_whatsapp": True,
        "telefone_principal_nome_contato": "Ana",
        "telefone_alternativo": "(19) 5588-5678",
        "telefone_alternativo_whatsapp": False,
        "telefone_alternativo_nome_contato": "Carlos",
        "email_responsavel": "ana@example.com",
    }
    resp_contato = client.post("/contatos", json=contato_payload)
    assert resp_contato.status_code == 201
    contato_id = resp_contato.get_json()["contato_id"]

    # Composição Familiar
    composicao_payload = {
        "familia_id": familia_id,
        "total_residentes": 4,
        "quantidade_bebes": 0,
        "quantidade_criancas": 1,
        "quantidade_adolescentes": 1,
        "quantidade_adultos": 2,
        "quantidade_idosos": 0,
        "tem_menores_na_escola": True,
        "motivo_ausencia_escola": "",
    }
    resp_composicao = client.post("/composicao_familiar", json=composicao_payload)
    assert resp_composicao.status_code == 201
    composicao_id = resp_composicao.get_json()["composicao_id"]

    # Condições de Moradia
    moradia_payload = {
        "familia_id": familia_id,
        "tipo_moradia": "Alugada",
        "valor_aluguel": 800.0,
        "tem_agua_encanada": True,
        "tem_rede_esgoto": True,
        "tem_energia_eletrica": True,
        "tem_fogao": True,
        "tem_geladeira": True,
        "quantidade_camas": 3,
        "quantidade_tvs": 1,
        "quantidade_ventiladores": 2,
    }
    resp_moradia = client.post("/condicoes_moradia", json=moradia_payload)
    assert resp_moradia.status_code == 201
    moradia_id = resp_moradia.get_json()["moradia_id"]

    # Educação do Entrevistado
    educacao_payload = {
        "familia_id": familia_id,
        "nivel_escolaridade": "Ensino Médio",
        "estuda_atualmente": "Não",
        "curso_ou_serie_atual": "",
    }
    resp_educacao = client.post("/educacao_entrevistado", json=educacao_payload)
    assert resp_educacao.status_code == 201
    educacao_id = resp_educacao.get_json()["educacao_id"]

    # Emprego do Provedor
    emprego_payload = {
        "familia_id": familia_id,
        "relacao_provedor_familia": "Pai",
        "descricao_provedor_externo": "Trabalho formal",
        "situacao_emprego": "Ativo",
        "descricao_situacao_emprego_outro": "",
        "profissao_provedor": "Motorista",
        "experiencia_profissional": "10 anos",
        "formacao_profissional": "Ensino Médio",
        "habilidades_relevantes": "CNH D",
    }
    resp_emprego = client.post("/emprego_provedor", json=emprego_payload)
    assert resp_emprego.status_code == 201
    emprego_id = resp_emprego.get_json()["emprego_id"]

    # Renda Familiar
    renda_payload = {
        "familia_id": familia_id,
        "gastos_supermercado": 600.0,
        "gastos_energia_eletrica": 120.0,
        "gastos_agua": 80.0,
        "valor_botijao_gas": 110.0,
        "duracao_botijao_gas": 30.0,
        "gastos_gas": 40.0,
        "gastos_transporte": 200.0,
        "gastos_medicamentos": 50.0,
        "gastos_celular": 60.0,
        "gastos_outros": 100.0,
        "renda_provedor_principal": 2500.0,
        "renda_outros_moradores": 500.0,
        "ajuda_terceiros": 0.0,
        "possui_cadastro_unico": True,
        "recebe_beneficios_governo": False,
        "descricao_beneficios": "",
        "valor_beneficios": 0.0,
        "renda_total_familiar": 3000.0,
        "gastos_totais": 1250.0,
        "saldo_mensal": 1750.0,
    }
    resp_renda = client.post("/renda_familiar", json=renda_payload)
    assert resp_renda.status_code == 201
    renda_id = resp_renda.get_json()["renda_id"]

    # Saúde / Necessidades Especiais
    saude_payload = {
        "familia_id": familia_id,
        "tem_doenca_cronica": False,
        "descricao_doenca_cronica": "",
        "usa_medicacao_continua": False,
        "descricao_medicacao": "",
        "tem_deficiencia": False,
        "descricao_deficiencia": "",
        "recebe_bpc": False,
    }
    resp_saude = client.post("/saude_familiar", json=saude_payload)
    assert resp_saude.status_code == 201
    saude_id = resp_saude.get_json()["saude_id"]

    # Verificações finais de GET
    assert client.get(f"/familias/{familia_id}").status_code == 200
    assert client.get(f"/enderecos/{endereco_id}").status_code == 200
    assert client.get(f"/contatos/{contato_id}").status_code == 200
    assert client.get(f"/composicao_familiar/{composicao_id}").status_code == 200
    assert client.get(f"/condicoes_moradia/{moradia_id}").status_code == 200
    assert client.get(f"/educacao_entrevistado/{educacao_id}").status_code == 200
    assert client.get(f"/emprego_provedor/{emprego_id}").status_code == 200
    assert client.get(f"/renda_familiar/{renda_id}").status_code == 200
    assert client.get(f"/saude_familiar/{saude_id}").status_code == 200

    global _familia_id
    _familia_id = familia_id


def test_demanda_criar_multiplas_para_familia(client):
    global _familia_id, _demanda1_id, _demanda2_id

    assert _familia_id is not None

    payload1 = {
        "familia_id": _familia_id,
        "demanda_tipo_id": 4,
        "descricao": "Av\u00f4 precisa de rem\u00e9dio para controlar press\u00e3o alta.",
        "data_identificacao": "2024-01-01",
    }
    resp1 = client.post("/demandas", json=payload1)
    assert resp1.status_code == 201
    data1 = resp1.get_json()
    assert data1["status"] == "Em análise"
    _demanda1_id = data1["demanda_id"]

    payload2 = {
        "familia_id": _familia_id,
        "demanda_tipo_id": 5,
        "descricao": "Filho mais novo nao conseguiu vaga em creche.",
        "data_identificacao": "2024-01-02",
    }
    resp2 = client.post("/demandas", json=payload2)
    assert resp2.status_code == 201
    data2 = resp2.get_json()
    assert data2["status"] == "Em análise"
    _demanda2_id = data2["demanda_id"]


def test_demanda_etapa_atualiza_status(client):
    global _demanda1_id
    assert _demanda1_id is not None

    etapa_payload = {
        "demanda_id": _demanda1_id,
        "status_atual": "Encaminhada",
        "observacao": "Requisicao encaminhada para farmacia da familia na regiao. Aguardando resposta para concluirmos esta demanda",
    }

    resp_etapa = client.post("/demanda_etapas", json=etapa_payload)
    assert resp_etapa.status_code == 201

    update_resp = client.put(f"/demandas/{_demanda1_id}", json={"status": "Encaminhada"})
    assert update_resp.status_code in [200, 201, 204]

    resp_get = client.get(f"/demandas/{_demanda1_id}")
    assert resp_get.status_code == 200
    assert resp_get.get_json()["status"] == "Encaminhada"


def test_demanda_tipo_invalido(client):
    global _familia_id
    assert _familia_id is not None

    payload = {
        "familia_id": _familia_id,
        "demanda_tipo_id": 9,
        "descricao": "Familia precisa de uma geladeira.",
        "data_identificacao": "2024-01-03",
    }

    resp = client.post("/demandas", json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "demanda_tipo_id" in data


