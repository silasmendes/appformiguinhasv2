import pytest
from app import create_app

_familia_id = None
_demanda_id = None

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client

def criar_familia(client):
    global _familia_id
    if not _familia_id:
        payload = {
            "nome_responsavel": "Teste Pytest",
            "autoriza_uso_imagem": True
        }
        resp = client.post("/familias", json=payload)
        assert resp.status_code == 201
        _familia_id = resp.get_json()["familia_id"]
    return _familia_id


def test_post_demanda_status_default(client):
    familia_id = criar_familia(client)
    payload = {
        "familia_id": familia_id,
        "demanda_tipo_id": 1,
        "descricao": "Teste demanda",
        "data_identificacao": "2024-01-01"
    }
    resp = client.post("/demandas", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "Em análise"
    global _demanda_id
    _demanda_id = data["demanda_id"]


def test_post_demanda_status_invalido(client):
    familia_id = criar_familia(client)
    payload = {
        "familia_id": familia_id,
        "demanda_tipo_id": 1,
        "status": "Invalido",
        "data_identificacao": "2024-01-01"
    }
    resp = client.post("/demandas", json=payload)
    assert resp.status_code == 400


def test_post_demanda_tipo_invalido(client):
    familia_id = criar_familia(client)
    payload = {
        "familia_id": familia_id,
        "demanda_tipo_id": 999,
        "data_identificacao": "2024-01-01"
    }
    resp = client.post("/demandas", json=payload)
    assert resp.status_code == 400


def test_put_demanda_status_invalido(client):
    global _demanda_id
    update_payload = {"status": "Nao existe"}
    resp = client.put(f"/demandas/{_demanda_id}", json=update_payload)
    assert resp.status_code == 400


def test_cleanup_demanda_familia(client):
    global _familia_id, _demanda_id
    if _demanda_id:
        client.delete(f"/demandas/{_demanda_id}")
    if _familia_id:
        client.delete(f"/familias/{_familia_id}")
