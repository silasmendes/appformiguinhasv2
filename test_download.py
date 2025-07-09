#!/usr/bin/env python3
"""
Script de teste para verificar a funcionalidade de download.
"""

import os
import sys
import pandas as pd
from io import BytesIO

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def test_download():
    """Testa a funcionalidade de download."""
    
    # Criar aplicação
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Testando funcionalidade de download...")
            
            # Verificar se o arquivo SQL existe
            sql_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "reference_inputs",
                "sql",
                "migracao_familias_e_relacionamentos.sql",
            )
            
            if not os.path.exists(sql_path):
                print(f"❌ Arquivo SQL não encontrado: {sql_path}")
                return False
                
            print(f"✅ Arquivo SQL encontrado: {sql_path}")
            
            # Ler query SQL
            with open(sql_path, "r", encoding="utf-8") as f:
                sql_content = f.read()
            
            print(f"✅ Query SQL lida com sucesso ({len(sql_content)} caracteres)")
            print(f"Primeiras linhas da query:")
            print("=" * 50)
            for i, line in enumerate(sql_content.split('\n')[:10]):
                print(f"{i+1:2d}: {line}")
            print("=" * 50)
            
            # Testar conexão com o banco
            try:
                sql_query = text(sql_content)
                print("✅ Query SQL parseada com sucesso")
                
                # Executar query
                print("🔄 Executando query...")
                resultados = db.session.execute(sql_query).mappings().all()
                print(f"✅ Query executada com sucesso! {len(resultados)} registros encontrados.")
                
                if len(resultados) == 0:
                    print("⚠️  Nenhum registro encontrado na query")
                    return True
                
                # Testar conversão para DataFrame
                dados = [dict(r) for r in resultados]
                df = pd.DataFrame(dados)
                print(f"✅ DataFrame criado com {len(df)} linhas e {len(df.columns)} colunas")
                
                # Converter campos de datetime com timezone para timezone-unaware
                for column in df.columns:
                    if df[column].dtype == 'object':
                        # Verificar se a coluna contém datetimes com timezone
                        sample_values = df[column].dropna().head(5)
                        if len(sample_values) > 0:
                            first_value = sample_values.iloc[0]
                            if hasattr(first_value, 'tzinfo') and first_value.tzinfo is not None:
                                print(f"Convertendo coluna {column} para timezone-unaware...")
                                df[column] = pd.to_datetime(df[column], errors='ignore').dt.tz_localize(None)
                    elif 'datetime64[ns, ' in str(df[column].dtype):
                        print(f"Convertendo coluna {column} para timezone-unaware...")
                        df[column] = df[column].dt.tz_localize(None)
                
                # Mostrar algumas colunas
                print(f"Colunas encontradas: {list(df.columns)[:10]}...")
                
                # Testar criação do Excel
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Dados_Familias', index=False)
                
                output.seek(0)
                excel_size = len(output.getvalue())
                print(f"✅ Arquivo Excel criado com sucesso! Tamanho: {excel_size} bytes")
                
                return True
                
            except Exception as db_error:
                print(f"❌ Erro na execução da query: {str(db_error)}")
                import traceback
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"❌ Erro geral: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_download()
    if success:
        print("\n🎉 Teste concluído com sucesso!")
    else:
        print("\n💥 Teste falhou!")
        sys.exit(1)
