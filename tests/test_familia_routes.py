import pytest
from app import create_app

_familia_id_gerada = None

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            yield client

# Teste de criação de família
def test_post_familia(client):
    global _familia_id_gerada

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

# Teste de busca de família por ID
def test_get_familia_por_id(client):
    global _familia_id_gerada
    response = client.get(f"/familias/{_familia_id_gerada}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["familia_id"] == _familia_id_gerada
    assert data["nome_responsavel"] == "Teste Pytest"

# Teste de atualização de família
def test_put_familia(client):
    global _familia_id_gerada

    update_payload = {
        "nome_responsavel": "Maria Atualizada",
        "estado_civil": "Casada(o)"
    }

    response = client.put(f"/familias/{_familia_id_gerada}", json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["nome_responsavel"] == "Maria Atualizada"
    assert data["estado_civil"] == "Casada(o)"

# Teste de exclusão de família
def test_delete_familia(client):
    global _familia_id_gerada

    response = client.delete(f"/familias/{_familia_id_gerada}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["mensagem"] == "Família deletada com sucesso"

# Teste de busca de família após exclusão
def test_get_familia_depois_do_delete(client):
    global _familia_id_gerada

    response = client.get(f"/familias/{_familia_id_gerada}")
    assert response.status_code == 404
    data = response.get_json()
    assert data["mensagem"] == "Família não encontrada"

# Teste de criação de família com CPF inválido
def test_post_familia_cpf_invalido(client):
    payload = {
        "nome_responsavel": "CPF Inválido",
        "data_nascimento": "1990-01-01",
        "genero": "Feminino",
        "estado_civil": "Solteira(o)",
        "rg": "123456789",
        "cpf": "123.456.789-00",  # CPF inválido de propósito
        "autoriza_uso_imagem": True
    }

    response = client.post("/familias", json=payload)
    assert response.status_code == 400

    data = response.get_json()
    assert "cpf" in data  # deve haver erro no campo cpf
    assert data["cpf"] == ["CPF inválido."]



def test_post_familia_somente_campos_obrigatorios(client):
    global _familia_id_gerada

    payload = {
        "nome_responsavel": "Teste Pytest",        
        "autoriza_uso_imagem": True
    }

    response = client.post("/familias", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert "familia_id" in data

    _familia_id_gerada = data["familia_id"]