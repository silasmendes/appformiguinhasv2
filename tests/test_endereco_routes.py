import pytest
from app import create_app

_familia_id_endereco = None
_endereco_id_gerado = None


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client


def test_post_endereco(client):
    global _familia_id_endereco, _endereco_id_gerado

    payload_familia = {
        "nome_responsavel": "Teste Pytest",
        "data_nascimento": "1990-01-01",
        "genero": "Masculino",
        "estado_civil": "Solteira(o)",
        "rg": "999999999",
        "cpf": "794.134.270-70",
        "autoriza_uso_imagem": True,
    }

    response = client.post("/familias", json=payload_familia)
    assert response.status_code == 201
    data = response.get_json()
    _familia_id_endereco = data["familia_id"]

    payload = {
        "familia_id": _familia_id_endereco,
        "cep": "12345678",
        "preenchimento_manual": False,
        "logradouro": "Rua Teste",
        "numero": "100",
        "complemento": "Ap 1",
        "bairro": "Centro",
        "cidade": "Cidade Teste",
        "estado": "Estado Teste",
        "ponto_referencia": "Perto de algo",
    }

    response = client.post("/enderecos", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "endereco_id" in data
    _endereco_id_gerado = data["endereco_id"]


def test_get_enderecos(client):
    response = client.get("/enderecos")
    assert response.status_code == 200


def test_get_endereco_por_id(client):
    global _endereco_id_gerado
    response = client.get(f"/enderecos/{_endereco_id_gerado}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["endereco_id"] == _endereco_id_gerado


def test_put_endereco(client):
    global _endereco_id_gerado
    update_payload = {"numero": "200"}
    response = client.put(f"/enderecos/{_endereco_id_gerado}", json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["numero"] == "200"


def test_delete_endereco(client):
    global _endereco_id_gerado
    response = client.delete(f"/enderecos/{_endereco_id_gerado}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["mensagem"] == "Endereço deletado com sucesso"


def test_get_endereco_depois_do_delete(client):
    global _endereco_id_gerado
    response = client.get(f"/enderecos/{_endereco_id_gerado}")
    assert response.status_code == 404
    data = response.get_json()
    assert data["mensagem"] == "Endereço não encontrado"


def test_cleanup_familia(client):
    global _familia_id_endereco
    if _familia_id_endereco:
        client.delete(f"/familias/{_familia_id_endereco}")
