import pytest
from app import create_app

_familia_id_composicao = None
_composicao_id_gerado = None


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client


def test_post_composicao_familiar(client):
    global _familia_id_composicao, _composicao_id_gerado

    payload = {
        "nome_responsavel": "Teste Pytest",
        "data_nascimento": "1990-01-01",
        "genero": "Masculino",
        "estado_civil": "Solteira(o)",
        "rg": "999999999",
        "cpf": "794.134.270-70",
        "autoriza_uso_imagem": True,
    }

    response = client.post("/familias", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    _familia_id_composicao = data["familia_id"]

    payload = {
        "familia_id": _familia_id_composicao,
        "total_residentes": 4,
        "quantidade_bebes": 1,
        "quantidade_criancas": 1,
        "quantidade_adolescentes": 1,
        "quantidade_adultos": 1,
        "quantidade_idosos": 0,
        "tem_menores_na_escola": True,
        "motivo_ausencia_escola": "N/A",
    }

    response = client.post("/composicao_familiar", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "composicao_id" in data
    _composicao_id_gerado = data["composicao_id"]


def test_get_composicoes(client):
    response = client.get("/composicao_familiar")
    assert response.status_code == 200


def test_get_composicao_por_id(client):
    global _composicao_id_gerado
    response = client.get(f"/composicao_familiar/{_composicao_id_gerado}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["composicao_id"] == _composicao_id_gerado


def test_put_composicao(client):
    global _composicao_id_gerado
    update_payload = {"total_residentes": 5}
    response = client.put(
        f"/composicao_familiar/{_composicao_id_gerado}", json=update_payload
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["total_residentes"] == 5


def test_delete_composicao(client):
    global _composicao_id_gerado
    response = client.delete(f"/composicao_familiar/{_composicao_id_gerado}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["mensagem"] == "Composicao deletada com sucesso"


def test_get_composicao_depois_do_delete(client):
    global _composicao_id_gerado
    response = client.get(f"/composicao_familiar/{_composicao_id_gerado}")
    assert response.status_code == 404
    data = response.get_json()
    assert data["mensagem"] == "Composicao familiar não encontrada"


def test_cleanup_familia(client):
    global _familia_id_composicao
    if _familia_id_composicao:
        client.delete(f"/familias/{_familia_id_composicao}")
