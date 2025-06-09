import pytest
from app import create_app

_familia_id_contato = None
_contato_id_gerado = None


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client


def test_post_contato(client):
    global _familia_id_gerada, _contato_id_gerado

    payload = {
        "nome_responsavel": "Teste Pytest",
        "data_nascimento": "1990-01-01",
        "genero": "Masculino",
        "estado_civil": "Solteira(o)",
        "rg": "999999999",
        "cpf": "794.134.270-70",
        "autoriza_uso_imagem": True
    }

    response = client.post("/familias", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert "familia_id" in data

    _familia_id_gerada = data["familia_id"]

    payload = {
        "familia_id": _familia_id_gerada,
        "telefone_principal": "11999999999",
        "telefone_principal_whatsapp": True,
        "telefone_principal_nome_contato": "Responsavel",
        "telefone_alternativo": "11888888888",
        "telefone_alternativo_whatsapp": False,
        "telefone_alternativo_nome_contato": "Alternativo",
        "email_responsavel": "email@exemplo.com",
    }

    response = client.post("/contatos", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "contato_id" in data
    _contato_id_gerado = data["contato_id"]


def test_get_contatos(client):
    response = client.get("/contatos")
    assert response.status_code == 200


def test_get_contato_por_id(client):
    global _contato_id_gerado
    response = client.get(f"/contatos/{_contato_id_gerado}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["contato_id"] == _contato_id_gerado


def test_put_contato(client):
    global _contato_id_gerado
    update_payload = {
        "telefone_principal_nome_contato": "Nome Atualizado",
    }
    response = client.put(f"/contatos/{_contato_id_gerado}", json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["telefone_principal_nome_contato"] == "Nome Atualizado"


def test_delete_contato(client):
    global _contato_id_gerado
    response = client.delete(f"/contatos/{_contato_id_gerado}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["mensagem"] == "Contato deletado com sucesso"


def test_get_contato_depois_do_delete(client):
    global _contato_id_gerado
    response = client.get(f"/contatos/{_contato_id_gerado}")
    assert response.status_code == 404
    data = response.get_json()
    assert data["mensagem"] == "Contato não encontrado"


def test_cleanup_familia(client):
    global _familia_id_contato
    if _familia_id_contato:
        client.delete(f"/familias/{_familia_id_contato}")
