#!/usr/bin/env python3
"""
Teste do resumo otimizado da família
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.utils.resumo_familia import gerar_resumo_familia

# Dados de teste mais realistas
dados_teste = {
    'total_residentes': 5,
    'quantidade_adultos': 2,
    'quantidade_criancas': 2,
    'quantidade_bebes': 1,
    'renda_familiar_total': 600.00,
    'agua_encanada': 'Não',
    'rede_esgoto': 'Não',
    'tem_geladeira': 'Não',
    'filho_creche': 'Não',
    'descricao_medicacao': 'Hipertensão e diabetes do responsável',
    'tipo_trabalho': 'Informal',
    'situacao_moradia': 'Aluguel',
    'demandas': [
        {'categoria': 'Moradia', 'prioridade': 'Alta'},
        {'categoria': 'Alimentação', 'prioridade': 'Alta'},
        {'categoria': 'Saúde', 'prioridade': 'Média'}
    ]
}

def testar_resumo_otimizado():
    """Testa a geração do resumo otimizado"""
    app = create_app()
    
    with app.app_context():
        print("=== Teste do Resumo Otimizado ===")
        print("\nDados da família:")
        print(f"- {dados_teste['total_residentes']} pessoas")
        print(f"- Renda: R$ {dados_teste['renda_familiar_total']}")
        print(f"- Água/Esgoto: {dados_teste['agua_encanada']}/{dados_teste['rede_esgoto']}")
        print(f"- Demandas: {len(dados_teste['demandas'])} ({[d['prioridade'] for d in dados_teste['demandas']]})")
        
        print("\n=== Resumo Gerado ===")
        resumo = gerar_resumo_familia(dados_teste)
        print(f"Resumo: {resumo}")
        print(f"Tamanho: {len(resumo)} caracteres")
        
        # Verificar se contém formatação markdown
        if '**' in resumo or '*' in resumo:
            print("✓ Contém formatação Markdown")
        else:
            print("⚠ Não contém formatação Markdown")
        
        # Verificar tamanho
        if len(resumo) <= 500:
            print("✓ Tamanho adequado (≤ 500 caracteres)")
        else:
            print(f"⚠ Muito longo ({len(resumo)} caracteres)")

if __name__ == "__main__":
    testar_resumo_otimizado()
