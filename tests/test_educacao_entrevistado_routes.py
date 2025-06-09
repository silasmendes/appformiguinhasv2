import pytest
from app import create_app

_familia_id_educacao = None
_educacao_id_gerada = None


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client


def test_post_educacao_entrevistado(client):
    global _familia_id_educacao, _educacao_id_gerada

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
    _familia_id_educacao = data["familia_id"]

    payload = {
        "familia_id": _familia_id_educacao,
        "nivel_escolaridade": "Ensino Médio",
        "estuda_atualmente": "Sim",
        "curso_ou_serie_atual": "3º ano",
    }

    response = client.post("/educacao_entrevistado", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "educacao_id" in data
    _educacao_id_gerada = data["educacao_id"]


def test_get_educacoes(client):
    response = client.get("/educacao_entrevistado")
    assert response.status_code == 200


def test_get_educacao_por_id(client):
    global _educacao_id_gerada
    response = client.get(f"/educacao_entrevistado/{_educacao_id_gerada}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["educacao_id"] == _educacao_id_gerada


def test_put_educacao(client):
    global _educacao_id_gerada
    update_payload = {"nivel_escolaridade": "Superior"}
    response = client.put(
        f"/educacao_entrevistado/{_educacao_id_gerada}", json=update_payload
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["nivel_escolaridade"] == "Superior"


def test_delete_educacao(client):
    global _educacao_id_gerada
    response = client.delete(f"/educacao_entrevistado/{_educacao_id_gerada}")
    assert response.status_code == 200
    data = response.get_json()
    assert (
        data["mensagem"]
        == "Educação do entrevistado deletada com sucesso"
    )


def test_get_educacao_depois_do_delete(client):
    global _educacao_id_gerada
    response = client.get(f"/educacao_entrevistado/{_educacao_id_gerada}")
    assert response.status_code == 404
    data = response.get_json()
    assert data["mensagem"] == "Educação do entrevistado não encontrada"


def test_cleanup_familia(client):
    global _familia_id_educacao
    if _familia_id_educacao:
        client.delete(f"/familias/{_familia_id_educacao}")
