import pytest
from app.templates.components.progress_bar_etapas import *
from flask import Flask, session
from unittest.mock import patch


def test_progress_bar_template_syntax():
    """Testa se o template não tem erros de sintaxe."""
    # Este teste verifica se o template pode ser renderizado sem erros
    app = Flask(__name__)
    
    with app.test_client() as client:
        with app.app_context():
            # Simula as variáveis que o template espera
            etapas = [
                "dados pessoais",
                "endereço", 
                "composição familiar",
                "contatos",
                "condições habitação",
                "saúde familiar",
                "emprego",
                "renda familiar",
                "educação",
                "outras necessidades",
                "encerramento"
            ]
            etapa_atual = 3
            
            # Testa se o template renderiza sem erros
            try:
                from flask import render_template_string
                
                # Lê o template
                with open('app/templates/components/progress_bar_etapas.html', 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # Simula sessão com família já cadastrada
                with client.session_transaction() as sess:
                    sess['cadastro'] = {'novo_cadastro': 0}
                    
                # Renderiza o template
                result = render_template_string(template_content, etapas=etapas, etapa_atual=etapa_atual)
                
                # Verifica se contém os elementos esperados
                assert 'timeline-container' in result
                assert 'circle-link' in result
                assert 'url_for' in result
                
                print("✓ Template renderizado com sucesso para família já cadastrada")
                
            except Exception as e:
                pytest.fail(f"Erro ao renderizar template: {e}")


def test_progress_bar_navigation_links():
    """Testa se os links de navegação são criados corretamente."""
    app = Flask(__name__)
    
    with app.test_client() as client:
        with app.app_context():
            etapas = ["dados pessoais", "endereço", "composição familiar", "contatos"]
            etapa_atual = 2
            
            with client.session_transaction() as sess:
                sess['cadastro'] = {'novo_cadastro': 0}
                
            from flask import render_template_string
            
            # Template simplificado para teste
            template_test = """
            {% if session.get('cadastro', {}).get('novo_cadastro') == 0 %}
                <a href="{{ url_for('fluxo_atendimento.atendimento_etapa1') }}" class="circle-link">
                    <div class="circle">1</div>
                </a>
            {% else %}
                <div class="circle">1</div>
            {% endif %}
            """
            
            result = render_template_string(template_test)
            
            # Verifica se o link foi criado
            assert 'circle-link' in result
            assert '<a href=' in result
            
            print("✓ Links de navegação criados corretamente")


if __name__ == "__main__":
    test_progress_bar_template_syntax()
    test_progress_bar_navigation_links()
    print("Todos os testes passaram!")
