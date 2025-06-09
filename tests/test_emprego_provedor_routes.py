import pytest
from app import create_app

_familia_id_emprego = None
_emprego_id_gerado = None


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client


def test_post_emprego_provedor(client):
    global _familia_id_emprego, _emprego_id_gerado

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
    _familia_id_emprego = data["familia_id"]

    payload = {
        "familia_id": _familia_id_emprego,
        "relacao_provedor_familia": "Pai",
        "descricao_provedor_externo": "Emprego formal",
        "situacao_emprego": "Ativo",
        "descricao_situacao_emprego_outro": "",
        "profissao_provedor": "Pedreiro",
        "experiencia_profissional": "5 anos",
        "formacao_profissional": "Ensino Fundamental",
        "habilidades_relevantes": "Alvenaria",
    }

    response = client.post("/emprego_provedor", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "emprego_id" in data
    _emprego_id_gerado = data["emprego_id"]


def test_get_empregos(client):
    response = client.get("/emprego_provedor")
    assert response.status_code == 200


def test_get_emprego_por_id(client):
    global _emprego_id_gerado
    response = client.get(f"/emprego_provedor/{_emprego_id_gerado}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["emprego_id"] == _emprego_id_gerado


def test_put_emprego(client):
    global _emprego_id_gerado
    update_payload = {"situacao_emprego": "Desempregado"}
    response = client.put(f"/emprego_provedor/{_emprego_id_gerado}", json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["situacao_emprego"] == "Desempregado"


def test_delete_emprego(client):
    global _emprego_id_gerado
    response = client.delete(f"/emprego_provedor/{_emprego_id_gerado}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["mensagem"] == "Emprego provedor deletado com sucesso"


def test_get_emprego_depois_do_delete(client):
    global _emprego_id_gerado
    response = client.get(f"/emprego_provedor/{_emprego_id_gerado}")
    assert response.status_code == 404
    data = response.get_json()
    assert data["mensagem"] == "Emprego provedor não encontrado"


def test_cleanup_familia(client):
    global _familia_id_emprego
    if _familia_id_emprego:
        client.delete(f"/familias/{_familia_id_emprego}")
