from flask import render_template, session, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required
from app.routes.usuarios import admin_required
import json
import os
import pandas as pd
from io import BytesIO
from datetime import datetime
from app import create_app
from app import db
from app.models.familia import Familia
from app.models.atendimento import Atendimento
from sqlalchemy import func, or_, text
from app.utils.fluxo_atendimento import (
    get_cadastro,
    reset_atendimento_sessao,
    carregar_cadastro_familia,
)

app = create_app()

@app.route("/")
@login_required
def home():
    """Renderiza a página inicial."""
    return render_template("index.html")

@app.route("/menu_atendimento")
@login_required
def menu_atendimento():
    termo = request.args.get("q", "").strip()
    resultados = None
    auto_open = False
    if termo:
        query = Familia.query
        # Busca tanto por CPF quanto por nome (similar à query T-SQL fornecida)
        query = query.filter(
            or_(
                Familia.cpf.ilike(f"%{termo}%"),
                Familia.nome_responsavel.ilike(f"%{termo}%")
            )
        )
        familias = query.all()
        resultados = []
        for familia in familias:
            ultimo = db.session.query(func.max(Atendimento.data_hora_atendimento)).filter_by(familia_id=familia.familia_id).scalar()
            resultados.append({
                "familia_id": familia.familia_id,
                "nome_responsavel": familia.nome_responsavel,
                "data_nascimento": familia.data_nascimento,
                "cpf": familia.cpf,
                "ultimo_atendimento": ultimo.date() if ultimo else None,
            })
        auto_open = True
    return render_template("atendimento/etapa0_menu.html", resultados=resultados, auto_open=auto_open)


@app.route("/gerenciar_demandas", methods=["GET"])
@login_required
def gerenciar_demandas_busca():
    """Exibe página de busca de família para gerenciar demandas."""
    reset_atendimento_sessao()
    termo = request.args.get("q", "").strip()
    resultados = None
    if termo:
        query = Familia.query.filter(
            or_(
                Familia.cpf.ilike(f"%{termo}%"),
                Familia.nome_responsavel.ilike(f"%{termo}%")
            )
        )
        familias = query.all()
        resultados = []
        for familia in familias:
            ultimo = db.session.query(func.max(Atendimento.data_hora_atendimento)).filter_by(familia_id=familia.familia_id).scalar()
            resultados.append({
                "familia_id": familia.familia_id,
                "nome_responsavel": familia.nome_responsavel,
                "cpf": familia.cpf,
                "ultimo_atendimento": ultimo.date() if ultimo else None,
            })
    return render_template("demandas/busca_familia.html", resultados=resultados)


@app.route("/gerenciar_demandas/<int:familia_id>", methods=["GET", "POST"])
@login_required
def gerenciar_demandas_familia(familia_id):
    """Permite atualização direta das demandas da família."""
    if request.method == "POST":
        cadastro = get_cadastro()
        cadastro.update(request.form.to_dict(flat=True))
        demandas_json = request.form.get("demandas_json")
        if demandas_json:
            try:
                cadastro["demandas"] = json.loads(demandas_json)
            except Exception:
                cadastro["demandas"] = []
        session["cadastro"] = cadastro
        flash("Demandas atualizadas", "success")
        return redirect(url_for("gerenciar_demandas_familia", familia_id=familia_id))

    reset_atendimento_sessao()
    cadastro = carregar_cadastro_familia(familia_id)
    if cadastro is None:
        flash("Família não encontrada", "danger")
        return redirect(url_for("gerenciar_demandas_busca"))
    return render_template("demandas/gerenciar.html")


@app.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """Renderiza a página do dashboard."""
    
    # Calcular número de famílias com demandas ativas dinamicamente
    sql_demandas_ativas = text(
        """
        SELECT COUNT(DISTINCT f.familia_id) as total_demandas_ativas
        FROM familias f
        JOIN enderecos e ON f.familia_id = e.familia_id
        JOIN demanda_familia df ON f.familia_id = df.familia_id
        JOIN demanda_tipo dt ON df.demanda_tipo_id = dt.demanda_tipo_id
        JOIN (
            SELECT de1.*
            FROM demanda_etapa de1
            INNER JOIN (
                SELECT demanda_id, MAX(etapa_id) AS max_etapa_id
                FROM demanda_etapa
                GROUP BY demanda_id
            ) m ON de1.demanda_id = m.demanda_id AND de1.etapa_id = m.max_etapa_id
        ) de ON df.demanda_id = de.demanda_id
        """
    )
    
    resultado_demandas = db.session.execute(sql_demandas_ativas).mappings().first()
    total_demandas_ativas = resultado_demandas['total_demandas_ativas'] if resultado_demandas else 0
    
    # Calcular número de famílias atendidas nos últimos 30 dias dinamicamente
    sql_familias_atendidas_30_dias = text(
        """
        SELECT COUNT(DISTINCT f.familia_id) as total_familias_atendidas_30_dias
        FROM familias f
        JOIN atendimentos a ON f.familia_id = a.familia_id
        WHERE a.data_hora_atendimento >= DATEADD(DAY, -30, GETDATE())
        """
    )
    
    resultado_atendidas = db.session.execute(sql_familias_atendidas_30_dias).mappings().first()
    total_familias_atendidas_30_dias = resultado_atendidas['total_familias_atendidas_30_dias'] if resultado_atendidas else 0
    
    # Dados mock para demonstração (outros valores podem ser calculados dinamicamente no futuro)
    dados_dashboard = {
        'total_familias': 48,
        'familias_atendidas_30_dias': total_familias_atendidas_30_dias,
        'entregas_cestas_30_dias': 24,
        'bairro_mais_atendimentos': 'Campo Belo',
        'familias_demandas_ativas': total_demandas_ativas,
        'familias_maior_vulnerabilidade': 7
    }
    return render_template("dashboards/dashboard.html", dados=dados_dashboard)


@app.route("/dashboard/demandas-ativas")
@login_required
@admin_required
def dashboard_demandas_ativas():
    """Lista de famílias com demandas ativas."""
    sql = text(
        """
        SELECT f.familia_id, f.nome_responsavel, f.cpf, e.bairro,
               df.descricao, df.data_identificacao, dt.demanda_tipo_nome,
               de.status_atual, df.prioridade, de.data_atualizacao,
               COALESCE(de.observacao, 'Análise da demanda ainda não iniciada') AS observacao
        FROM familias f
        JOIN enderecos e ON f.familia_id = e.familia_id
        JOIN demanda_familia df ON f.familia_id = df.familia_id
        JOIN demanda_tipo dt ON df.demanda_tipo_id = dt.demanda_tipo_id
        JOIN (
            SELECT de1.*
            FROM demanda_etapa de1
            INNER JOIN (
                SELECT demanda_id, MAX(etapa_id) AS max_etapa_id
                FROM demanda_etapa
                GROUP BY demanda_id
            ) m ON de1.demanda_id = m.demanda_id AND de1.etapa_id = m.max_etapa_id
        ) de ON df.demanda_id = de.demanda_id
        ORDER BY df.prioridade ASC
        """
    )

    resultados = db.session.execute(sql).mappings().all()
    demandas = [dict(r) for r in resultados]
    return render_template("dashboards/demandas_ativas.html", demandas=demandas)


@app.route("/dashboard/familias-cadastradas")
@login_required
@admin_required
def dashboard_familias_cadastradas():
    """Página para download de dados das famílias cadastradas."""
    return render_template("dashboards/familias_cadastradas.html")


@app.route("/dashboard/familias-atendidas-30-dias")
@login_required
@admin_required
def dashboard_familias_atendidas_30_dias():
    """Lista de famílias atendidas nos últimos 30 dias."""
    sql = text(
        """
            SELECT 
                f.familia_id, 
                f.nome_responsavel, 
                f.cpf, 
                e.bairro,
                c.telefone_principal, 
                c.email_responsavel,
                a.percepcao_necessidade, 
                a.cesta_entregue, 
                a.data_hora_atendimento
            FROM familias f
            LEFT JOIN enderecos e ON f.familia_id = e.familia_id
            LEFT JOIN contatos c ON f.familia_id = c.familia_id
            INNER JOIN atendimentos a ON f.familia_id = a.familia_id
            WHERE a.data_hora_atendimento >= DATEADD(DAY, -30, GETDATE())
            ORDER BY a.data_hora_atendimento DESC;
        """
    )

    resultados = db.session.execute(sql).mappings().all()
    familias = [dict(r) for r in resultados]
    return render_template("dashboards/familias_atendidas_30_dias.html", familias=familias)


@app.route("/dashboard/em-desenvolvimento")
@login_required
@admin_required
def dashboard_em_desenvolvimento():
    """Página temporária para funcionalidades em desenvolvimento."""
    return render_template("dashboards/em_desenvolvimento.html")


@app.route("/dashboard/familias-cadastradas/download")
@login_required
@admin_required
def download_familias_cadastradas():
    """Download de arquivo Excel com dados completos das famílias."""
    try:
        print(f"Iniciando download de famílias - Ambiente: {os.name}")
        print(f"Diretório atual: {os.getcwd()}")
        print(f"Arquivo main.py: {os.path.abspath(__file__)}")
        
        # Query SQL embarcada para garantir compatibilidade cross-platform
        sql_query_string = """
        SELECT 
            f.*, 
            e.*, 
            c.*, 
            cf.*, 
            cm.*, 
            ed.*, 
            ep.*, 
            rf.*, 
            sf.*,
            demandas_json.demandas,
            atendimentos_json.atendimentos
        FROM familias f
        LEFT JOIN enderecos e ON f.familia_id = e.familia_id
        LEFT JOIN contatos c ON f.familia_id = c.familia_id
        LEFT JOIN composicao_familiar cf ON f.familia_id = cf.familia_id
        LEFT JOIN condicoes_moradia cm ON f.familia_id = cm.familia_id
        LEFT JOIN educacao_entrevistado ed ON f.familia_id = ed.familia_id
        LEFT JOIN emprego_provedor ep ON f.familia_id = ep.familia_id
        LEFT JOIN renda_familiar rf ON f.familia_id = rf.familia_id
        LEFT JOIN saude_familiar sf ON f.familia_id = sf.familia_id
        OUTER APPLY (
            SELECT 
                df.demanda_id,
                df.familia_id,
                df.demanda_tipo_id,
                dt.demanda_tipo_nome,
                df.status,
                df.descricao,
                df.data_identificacao,
                df.prioridade,
                de.data_atualizacao,
                de.status_atual,
                de.observacao,
                de.usuario_atualizacao
            FROM demanda_familia df
            INNER JOIN demanda_tipo dt ON df.demanda_tipo_id = dt.demanda_tipo_id
            INNER JOIN demanda_etapa de ON df.demanda_id = de.demanda_id
            WHERE df.familia_id = f.familia_id
            FOR JSON PATH
        ) AS demandas_json(demandas)
        OUTER APPLY (
            SELECT 
                a.*
            FROM atendimentos a
            WHERE a.familia_id = f.familia_id
            FOR JSON PATH
        ) AS atendimentos_json(atendimentos)
        """
        
        print("Usando query SQL embarcada...")
        try:
            sql_query = text(sql_query_string)
        except Exception as e:
            print(f"Erro ao criar query SQL: {str(e)}")
            return jsonify({"error": "Erro na consulta SQL"}), 500
        
        print("Executando query SQL...")
        try:
            resultados = db.session.execute(sql_query).mappings().all()
            print(f"Query executada com sucesso. {len(resultados)} registros encontrados.")
        except Exception as e:
            print(f"Erro ao executar query SQL: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Erro na execução da consulta: {str(e)}"}), 500
        
        if not resultados:
            print("Nenhum dado encontrado na base de dados.")
            return jsonify({"error": "Nenhum dado encontrado para exportação"}), 404
        
        # Converter para lista de dicionários
        try:
            dados = [dict(r) for r in resultados]
            print(f"Dados convertidos: {len(dados)} registros")
        except Exception as e:
            print(f"Erro ao converter dados: {str(e)}")
            return jsonify({"error": "Erro ao processar dados"}), 500
        
        # Criar DataFrame
        try:
            df = pd.DataFrame(dados)
            print(f"DataFrame criado com {len(df)} linhas e {len(df.columns)} colunas.")
        except Exception as e:
            print(f"Erro ao criar DataFrame: {str(e)}")
            return jsonify({"error": "Erro ao criar planilha"}), 500
        
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
        
        # Renomear colunas para português (mapeamento básico - pode ser expandido)
        colunas_pt = {
            'familia_id': 'ID Família',
            'nome_responsavel': 'Nome do Responsável',
            'cpf': 'CPF',
            'data_nascimento': 'Data de Nascimento',
            'telefone_principal': 'Telefone Principal',
            'email': 'Email',
            'data_cadastro': 'Data de Cadastro',
            'logradouro': 'Logradouro',
            'numero': 'Número',
            'complemento': 'Complemento',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'Estado',
            'cep': 'CEP'
        }
        
        # Aplicar renomeação apenas para colunas que existem
        colunas_existentes = {k: v for k, v in colunas_pt.items() if k in df.columns}
        df = df.rename(columns=colunas_existentes)
        
        print("Criando arquivo Excel...")
        try:
            # Criar buffer em memória para o arquivo Excel
            output = BytesIO()
            
            # Criar arquivo Excel
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Aba principal com todos os dados
                df.to_excel(writer, sheet_name='Dados_Familias', index=False)
                
                # Obter o workbook e worksheet para formatação
                workbook = writer.book
                worksheet = writer.sheets['Dados_Familias']
                
                # Ajustar largura das colunas
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if cell.value and len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max(max_length + 2, 10), 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            print("Arquivo Excel criado com sucesso.")
        except Exception as e:
            print(f"Erro ao criar arquivo Excel: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Erro ao gerar arquivo Excel: {str(e)}"}), 500
        
        # Gerar nome do arquivo com data atual
        try:
            data_atual = datetime.now().strftime("%Y_%m_%d")
            nome_arquivo = f"migracao_familias_{data_atual}.xlsx"
            
            print(f"Enviando arquivo: {nome_arquivo}")
            return send_file(
                output,
                as_attachment=True,
                download_name=nome_arquivo,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            print(f"Erro ao enviar arquivo: {str(e)}")
            return jsonify({"error": f"Erro ao enviar arquivo: {str(e)}"}), 500
        
    except FileNotFoundError as e:
        print(f"Erro de arquivo não encontrado: {str(e)}")
        return jsonify({
            "error": "Arquivo de consulta não encontrado"
        }), 500
    except Exception as e:
        print(f"Erro detalhado no download: {str(e)}")
        import traceback
        traceback.print_exc()
        # Retornar erro em JSON para requisições AJAX
        return jsonify({
            "error": f"Erro ao gerar arquivo: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
