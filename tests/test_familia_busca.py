import pytest
import json
from app import create_app, db
from app.models.familia import Familia
from datetime import date


@pytest.fixture
def app():
    """Cria uma instância da aplicação para testes usando o banco real."""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Cliente de teste para fazer requisições."""
    return app.test_client()


class TestFamiliaBusca:
    """Testes para a funcionalidade de busca de famílias no banco real."""
    
    def test_busca_por_nome_silas(self, client):
        """Testa busca pelo nome 'Silas' no banco real."""
        response = client.get('/familias/busca?q=Silas')
        
        assert response.status_code == 200, f"Status code inesperado: {response.status_code}"
        
        data = json.loads(response.data)
        print(f"\nResultado da busca por 'Silas': {data}")
        
        # Verifica se pelo menos um resultado foi encontrado
        assert len(data) > 0, "Nenhum resultado encontrado para 'Silas'"
        
        # Verifica se o primeiro resultado contém 'Silas' no nome
        first_result = data[0]
        assert 'Silas' in first_result['nome_responsavel'], f"Nome não contém 'Silas': {first_result['nome_responsavel']}"
    
    def test_busca_por_cpf_com_mascara(self, client):
        """Testa busca pelo CPF '086.483.387-35' no banco real."""
        response = client.get('/familias/busca?q=086.483.387-35')
        
        assert response.status_code == 200, f"Status code inesperado: {response.status_code}"
        
        data = json.loads(response.data)
        print(f"\nResultado da busca por CPF '086.483.387-35': {data}")
        
        # Verifica se pelo menos um resultado foi encontrado
        assert len(data) > 0, "Nenhum resultado encontrado para CPF '086.483.387-35'"
        
        # Verifica se o CPF está correto
        first_result = data[0]
        assert first_result['cpf'] == '086.483.387-35', f"CPF incorreto: {first_result['cpf']}"
    
    def test_busca_por_cpf_sem_mascara(self, client):
        """Testa busca pelo CPF '08648338735' (sem máscara) no banco real."""
        response = client.get('/familias/busca?q=08648338735')
        
        assert response.status_code == 200, f"Status code inesperado: {response.status_code}"
        
        data = json.loads(response.data)
        print(f"\nResultado da busca por CPF sem máscara '08648338735': {data}")
        
        # Deve encontrar o mesmo resultado que a busca com máscara
        assert len(data) > 0, "Nenhum resultado encontrado para CPF sem máscara '08648338735'"
    
    def test_debug_banco_dados(self, app):
        """Teste para debug: verifica dados no banco."""
        with app.app_context():
            # Conta total de famílias
            total_familias = Familia.query.count()
            print(f"\nTotal de famílias no banco: {total_familias}")
            
            # Lista primeiras 5 famílias
            familias = Familia.query.limit(5).all()
            print("\nPrimeiras 5 famílias no banco:")
            for f in familias:
                print(f"ID: {f.familia_id}, Nome: {f.nome_responsavel}, CPF: {f.cpf}")
            
            # Busca específica por 'Silas'
            familias_silas = Familia.query.filter(Familia.nome_responsavel.ilike('%Silas%')).all()
            print(f"\nFamílias com 'Silas' no nome: {len(familias_silas)}")
            for f in familias_silas:
                print(f"Nome: {f.nome_responsavel}, CPF: {f.cpf}")
            
            # Busca específica por CPF
            familia_cpf = Familia.query.filter(Familia.cpf.ilike('%086.483.387-35%')).first()
            if familia_cpf:
                print(f"\nFamília com CPF '086.483.387-35': {familia_cpf.nome_responsavel}")
            else:
                print("\nNenhuma família encontrada com CPF '086.483.387-35'")
            
            assert True  # Sempre passa, é só para debug
    
    def test_estrutura_resposta(self, client):
        """Testa se a estrutura da resposta está correta."""
        response = client.get('/familias/busca?q=a')  # Busca genérica
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if len(data) > 0:
            familia = data[0]
            
            # Verifica se todos os campos esperados estão presentes
            assert 'familia_id' in familia, "Campo 'familia_id' não encontrado"
            assert 'nome_responsavel' in familia, "Campo 'nome_responsavel' não encontrado"
            assert 'cpf' in familia, "Campo 'cpf' não encontrado"
            assert 'data_nascimento' in familia, "Campo 'data_nascimento' não encontrado"
            assert 'ultimo_atendimento' in familia, "Campo 'ultimo_atendimento' não encontrado"
            
            print(f"\nEstrutura da resposta OK: {familia.keys()}")
    
    def test_busca_case_insensitive(self, client):
        """Testa se a busca é case insensitive."""
        response_upper = client.get('/familias/busca?q=SILAS')
        response_lower = client.get('/familias/busca?q=silas')
        
        assert response_upper.status_code == 200
        assert response_lower.status_code == 200
        
        data_upper = json.loads(response_upper.data)
        data_lower = json.loads(response_lower.data)
        
        print(f"\nBusca 'SILAS': {len(data_upper)} resultados")
        print(f"Busca 'silas': {len(data_lower)} resultados")
        
        # Ambas devem retornar a mesma quantidade de resultados
        assert len(data_upper) == len(data_lower), "Busca não é case insensitive"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])  # -s para mostrar os prints
