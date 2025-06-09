import pytest
from decimal import Decimal
from app import create_app

_familia_id_renda = None
_renda_id_gerada = None


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client


def test_post_renda_familiar(client):
    global _familia_id_renda, _renda_id_gerada

    payload_familia = {
        "nome_responsavel": "Teste Pytest",
        "data_nascimento": "1990-01-01",
        "genero": "Masculino",
        "estado_civil": "Solteiro",
        "rg": "999999999",
        "cpf": "794.134.270-70",
        "autoriza_uso_imagem": True,
    }

    response = client.post("/familias", json=payload_familia)
    assert response.status_code == 201
    data = response.get_json()
    _familia_id_renda = data["familia_id"]

    payload = {
        "familia_id": _familia_id_renda,
        "gastos_supermercado": 100.0,
        "gastos_energia_eletrica": 50.0,
        "gastos_agua": 30.0,
        "valor_botijao_gas": 120.0,
        "duracao_botijao_gas": 30.0,
        "gastos_gas": 40.0,
        "gastos_transporte": 60.0,
        "gastos_medicamentos": 20.0,
        "gastos_celular": 35.0,
        "gastos_outros": 10.0,
        "renda_provedor_principal": 1500.0,
        "renda_outros_moradores": 500.0,
        "ajuda_terceiros": 100.0,
        "possui_cadastro_unico": True,
        "recebe_beneficios_governo": False,
        "descricao_beneficios": "",
        "valor_beneficios": 0.0,
        "renda_total_familiar": 2000.0,
        "gastos_totais": 500.0,
        "saldo_mensal": 1500.0,
    }

    response = client.post("/renda_familiar", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "renda_id" in data
    _renda_id_gerada = data["renda_id"]


def test_get_rendas(client):
    response = client.get("/renda_familiar")
    assert response.status_code == 200


def test_get_renda_por_id(client):
    global _renda_id_gerada
    response = client.get(f"/renda_familiar/{_renda_id_gerada}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["renda_id"] == _renda_id_gerada


def test_put_renda(client):
    global _renda_id_gerada
    update_payload = {"gastos_supermercado": 150.0}
    response = client.put(f"/renda_familiar/{_renda_id_gerada}", json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert Decimal(data["gastos_supermercado"]) == Decimal("150.00")


def test_delete_renda(client):
    global _renda_id_gerada
    response = client.delete(f"/renda_familiar/{_renda_id_gerada}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["mensagem"] == "Renda familiar deletada com sucesso"


def test_get_renda_depois_do_delete(client):
    global _renda_id_gerada
    response = client.get(f"/renda_familiar/{_renda_id_gerada}")
    assert response.status_code == 404
    data = response.get_json()
    assert data["mensagem"] == "Renda familiar não encontrada"


def test_cleanup_familia(client):
    global _familia_id_renda
    if _familia_id_renda:
        client.delete(f"/familias/{_familia_id_renda}")

