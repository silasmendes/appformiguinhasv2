from app import create_app, db
from app.models.familia import Familia
import json

def test_busca_familias_por_cpf():
    app = create_app()
    
    with app.app_context():
        # Primeiro, vamos ver quantas famílias existem no banco
        total_familias = Familia.query.count()
        print(f"Total de famílias no banco: {total_familias}")
        
        # Vamos ver algumas famílias para conferir os dados
        familias_sample = Familia.query.limit(5).all()
        print("\nPrimeiras 5 famílias no banco:")
        for f in familias_sample:
            print(f"ID: {f.familia_id}, Nome: {f.nome_responsavel}, CPF: {f.cpf}")
        
        # Cria um cliente de teste
        client = app.test_client()
        
        # Define o termo de busca (parte do CPF)
        termo = '086.483'
        
        # Faz a requisição GET simulando acesso à rota /busca?q=086.483
        print(f"\nFazendo busca por: '{termo}'")
        response = client.get(f"/familias/busca?q={termo}")
        
        print(f"Status da resposta: {response.status_code}")
        print(f"Headers da resposta: {dict(response.headers)}")
        
        # Converte resposta JSON
        resultados = response.get_json()
        
        print(f"Resultados da busca por '{termo}': {resultados}")
        print(f"Número de resultados: {len(resultados) if resultados else 0}")

def test_busca_familias_por_nome():
    app = create_app()
    
    with app.app_context():
        client = app.test_client()
        
        # Teste com nome
        termo = 'Silas'
        print(f"\n--- Testando busca por nome: '{termo}' ---")
        response = client.get(f"/familias/busca?q={termo}")
        
        print(f"Status da resposta: {response.status_code}")
        resultados = response.get_json()
        print(f"Resultados da busca por '{termo}': {resultados}")
        print(f"Número de resultados: {len(resultados) if resultados else 0}")

if __name__ == "__main__":
    print("=== Teste de busca de famílias ===")
    test_busca_familias_por_cpf()
    test_busca_familias_por_nome()
