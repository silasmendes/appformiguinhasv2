import pytest
from app import create_app

_familia_id_saude = None
_saude_id_gerado = None

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client

def test_post_saude_familiar(client):
    global _familia_id_saude, _saude_id_gerado

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
    _familia_id_saude = data["familia_id"]

    payload = {
        "familia_id": _familia_id_saude,
        "tem_doenca_cronica": True,
        "descricao_doenca_cronica": "Diabetes",
        "usa_medicacao_continua": True,
        "descricao_medicacao": "Insulina",
        "tem_deficiencia": False,
        "descricao_deficiencia": None,
        "recebe_bpc": False,
    }

    response = client.post("/saude_familiar", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "saude_id" in data
    _saude_id_gerado = data["saude_id"]


def test_get_saudes(client):
    response = client.get("/saude_familiar")
    assert response.status_code == 200


def test_get_saude_por_id(client):
    global _saude_id_gerado
    response = client.get(f"/saude_familiar/{_saude_id_gerado}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["saude_id"] == _saude_id_gerado


def test_put_saude(client):
    global _saude_id_gerado
    update_payload = {"recebe_bpc": True}
    response = client.put(f"/saude_familiar/{_saude_id_gerado}", json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["recebe_bpc"] is True


def test_delete_saude(client):
    global _saude_id_gerado
    response = client.delete(f"/saude_familiar/{_saude_id_gerado}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["mensagem"] == "Saude familiar deletada com sucesso"


def test_get_saude_depois_do_delete(client):
    global _saude_id_gerado
    response = client.get(f"/saude_familiar/{_saude_id_gerado}")
    assert response.status_code == 404
    data = response.get_json()
    assert data["mensagem"] == "Saude familiar não encontrada"


def test_cleanup_familia(client):
    global _familia_id_saude
    if _familia_id_saude:
        client.delete(f"/familias/{_familia_id_saude}")
