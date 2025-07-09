#!/usr/bin/env python3
"""
Script para testar a rota de download via HTTP
"""

import requests
import os
from datetime import datetime

def test_download_route():
    """Testa a rota de download diretamente"""
    
    # URL base do servidor (pode precisar ajustar se estiver rodando em outra porta)
    base_url = "http://localhost:5000"
    download_url = f"{base_url}/dashboard/familias-cadastradas/download"
    
    print("🔍 Testando rota de download via HTTP...")
    
    try:
        # Fazer requisição para a rota de download
        print(f"Fazendo requisição para: {download_url}")
        
        response = requests.get(
            download_url,
            headers={
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            },
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {response.headers.get('content-length', 'N/A')}")
        
        if response.status_code == 200:
            # Verificar se é realmente um arquivo Excel
            content_type = response.headers.get('content-type', '')
            if 'spreadsheetml' in content_type or 'excel' in content_type:
                print("✅ Resposta é um arquivo Excel válido!")
                
                # Salvar arquivo para teste
                filename = f"test_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                file_size = os.path.getsize(filename)
                print(f"✅ Arquivo salvo como {filename} (tamanho: {file_size} bytes)")
                
                # Remover arquivo de teste
                os.remove(filename)
                print("✅ Arquivo de teste removido")
                
                return True
            else:
                print(f"❌ Resposta não é um arquivo Excel. Content-Type: {content_type}")
                print("Primeiros 500 caracteres da resposta:")
                print(response.text[:500])
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print("Resposta:")
            print(response.text[:500])
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor. Certifique-se de que a aplicação está rodando em http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_download_route()
    if success:
        print("\n🎉 Teste da rota de download concluído com sucesso!")
    else:
        print("\n💥 Teste da rota de download falhou!")
        print("\nPara testar, execute primeiro a aplicação Flask:")
        print("python app.py")
        print("E então execute este teste em outro terminal.")
