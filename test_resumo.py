#!/usr/bin/env python3
"""
Teste simples para verificar o funcionamento do resumo da família
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.utils.resumo_familia import gerar_resumo_familia

# Dados de exemplo para teste
dados_teste = {
    'total_residentes': 4,
    'quantidade_adultos': 2,
    'quantidade_criancas': 2,
    'renda_familiar_total': 800,
    'agua_encanada': 'Não',
    'rede_esgoto': 'Não',
    'tem_geladeira': 'Não',
    'filho_creche': 'Não',
    'descricao_medicacao': 'Diabetes e hipertensão',
    'tipo_trabalho': 'Informal',
    'demandas': [
        {'categoria': 'Moradia', 'prioridade': 'Alta'},
        {'categoria': 'Saúde', 'prioridade': 'Média'}
    ],
    'bairro': 'Periferia',
    'cidade': 'São Paulo'
}

def testar_resumo():
    """Testa a geração do resumo da família"""
    app = create_app()
    
    with app.app_context():
        print("=== Teste do Resumo da Família ===")
        print("\nDados de entrada (sem PII):")
        print(f"- Total residentes: {dados_teste['total_residentes']}")
        print(f"- Renda familiar: R$ {dados_teste['renda_familiar_total']}")
        print(f"- Água encanada: {dados_teste['agua_encanada']}")
        print(f"- Rede de esgoto: {dados_teste['rede_esgoto']}")
        print(f"- Tem geladeira: {dados_teste['tem_geladeira']}")
        print(f"- Filho na creche: {dados_teste['filho_creche']}")
        print(f"- Medicação: {dados_teste['descricao_medicacao']}")
        print(f"- Tipo trabalho: {dados_teste['tipo_trabalho']}")
        print(f"- Demandas: {len(dados_teste['demandas'])} demandas")
        
        print("\n=== Resumo Gerado ===")
        resumo = gerar_resumo_familia(dados_teste)
        print(f"Resumo: {resumo}")
        
        print(f"\nTamanho do resumo: {len(resumo)} caracteres")

if __name__ == "__main__":
    testar_resumo()
