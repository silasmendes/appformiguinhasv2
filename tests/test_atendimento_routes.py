import pytest
from app import create_app

_familia_id_atendimento = None
_atendimento_id_gerado = None

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_post_atendimento(client):
    global _familia_id_atendimento, _atendimento_id_gerado

    payload_familia = {
        "nome_responsavel": "Teste Pytest",
        "autoriza_uso_imagem": True
    }
    resp = client.post("/familias", json=payload_familia)
    assert resp.status_code == 201
    _familia_id_atendimento = resp.get_json()["familia_id"]

    payload = {
        "familia_id": _familia_id_atendimento,
        "usuario_atendente_id": 1,
        "percepcao_necessidade": "Alta",
        "duracao_necessidade": "Temporária",
        "motivo_duracao": "Teste",
        "cesta_entregue": True,
        "data_entrega_cesta": "2026-02-21"
    }
    resp = client.post("/atendimentos", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert "atendimento_id" in data
    _atendimento_id_gerado = data["atendimento_id"]


def test_get_atendimentos(client):
    resp = client.get("/atendimentos")
    assert resp.status_code == 200


def test_get_atendimento_por_id(client):
    global _atendimento_id_gerado
    resp = client.get(f"/atendimentos/{_atendimento_id_gerado}")
    assert resp.status_code == 200
    assert resp.get_json()["atendimento_id"] == _atendimento_id_gerado


def test_put_atendimento(client):
    global _atendimento_id_gerado
    update_payload = {"percepcao_necessidade": "Media"}
    resp = client.put(f"/atendimentos/{_atendimento_id_gerado}", json=update_payload)
    assert resp.status_code == 200
    assert resp.get_json()["percepcao_necessidade"] == "Media"


def test_cleanup_familia(client):
    global _familia_id_atendimento
    if _familia_id_atendimento:
        client.delete(f"/familias/{_familia_id_atendimento}")

