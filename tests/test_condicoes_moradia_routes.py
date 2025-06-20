import pytest
from app import create_app

_familia_id_condicao = None
_moradia_id_gerada = None


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client


def test_post_condicao_moradia(client):
    global _familia_id_condicao, _moradia_id_gerada

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
    _familia_id_condicao = data["familia_id"]

    payload = {
        "familia_id": _familia_id_condicao,
        "tipo_moradia": "Alugada",
        "valor_aluguel": 500.0,
        "tem_agua_encanada": True,
        "tem_rede_esgoto": True,
        "tem_energia_eletrica": True,
        "tem_fogao": True,
        "tem_geladeira": True,
        "quantidade_camas": 3,
        "quantidade_tvs": 1,
        "quantidade_ventiladores": 2,
    }

    response = client.post("/condicoes_moradia", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "moradia_id" in data
    _moradia_id_gerada = data["moradia_id"]


def test_get_condicoes_moradia(client):
    response = client.get("/condicoes_moradia")
    assert response.status_code == 200


def test_get_condicao_moradia_por_id(client):
    global _moradia_id_gerada
    response = client.get(f"/condicoes_moradia/{_moradia_id_gerada}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["moradia_id"] == _moradia_id_gerada


def test_put_condicao_moradia(client):
    global _moradia_id_gerada
    update_payload = {
        "tipo_moradia": "Própria"
    }
    response = client.put(
        f"/condicoes_moradia/{_moradia_id_gerada}", json=update_payload
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["tipo_moradia"] == "Própria"


def test_upsert_condicao_campos_vazios(client):
    """Garante que o upsert trata campos vazios sem erro."""
    global _familia_id_condicao

    payload = {"quantidade_ventiladores": ""}
    response = client.put(
        f"/condicoes_moradia/upsert/familia/{_familia_id_condicao}",
        json=payload,
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("quantidade_ventiladores") is None


def test_delete_condicao_moradia(client):
    global _moradia_id_gerada
    response = client.delete(f"/condicoes_moradia/{_moradia_id_gerada}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["mensagem"] == "Condição de moradia deletada com sucesso"


def test_get_condicao_moradia_depois_do_delete(client):
    global _moradia_id_gerada
    response = client.get(f"/condicoes_moradia/{_moradia_id_gerada}")
    assert response.status_code == 404
    data = response.get_json()
    assert data["mensagem"] == "Condição de moradia não encontrada"


def test_cleanup_familia(client):
    global _familia_id_condicao
    if _familia_id_condicao:
        client.delete(f"/familias/{_familia_id_condicao}")
