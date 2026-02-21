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
from app.utils.pre_cadastro import buscar_pre_cadastros, converter_pre_cadastro_para_sessao

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
                "nome_mae": familia.nome_mae,
                "nome_pai": familia.nome_pai,
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
    
    # Calcular número de entregas de cestas nos últimos 30 dias dinamicamente
    sql_entregas_cestas_30_dias = text(
        """
        SELECT COUNT(*) as total_entregas_cestas_30_dias
        FROM atendimentos a
        WHERE a.data_hora_atendimento >= DATEADD(DAY, -30, GETDATE())
        AND a.cesta_entregue = 1
        """
    )
    
    resultado_cestas = db.session.execute(sql_entregas_cestas_30_dias).mappings().first()
    total_entregas_cestas_30_dias = resultado_cestas['total_entregas_cestas_30_dias'] if resultado_cestas else 0
    
    # Calcular número de famílias sem atendimento nos últimos 3 meses (cadastradas no último ano)
    sql_familias_sem_atendimento_recente = text(
        """
        SELECT COUNT(*) as total_familias_sem_atendimento_recente
        FROM familias f
        LEFT JOIN (
            SELECT 
                familia_id, 
                MAX(data_hora_atendimento) as ultima_data_atendimento
            FROM atendimentos 
            GROUP BY familia_id
        ) ultimo_atendimento ON f.familia_id = ultimo_atendimento.familia_id
        WHERE f.data_hora_log_utc >= DATEADD(YEAR, -1, GETDATE())
        AND (
            ultimo_atendimento.ultima_data_atendimento IS NULL 
            OR ultimo_atendimento.ultima_data_atendimento < DATEADD(DAY, -90, GETDATE())
        )
        """
    )
    
    resultado_sem_atendimento = db.session.execute(sql_familias_sem_atendimento_recente).mappings().first()
    total_familias_sem_atendimento_recente = resultado_sem_atendimento['total_familias_sem_atendimento_recente'] if resultado_sem_atendimento else 0
    
    # Calcular número de famílias em situação de maior vulnerabilidade (percepção alta)
    sql_familias_maior_vulnerabilidade = text(
        """
        SELECT COUNT(DISTINCT f.familia_id) as total_familias_maior_vulnerabilidade
        FROM familias f
        INNER JOIN atendimentos a ON f.familia_id = a.familia_id
        WHERE a.percepcao_necessidade = 'Alta'
        """
    )
    
    resultado_vulnerabilidade = db.session.execute(sql_familias_maior_vulnerabilidade).mappings().first()
    total_familias_maior_vulnerabilidade = resultado_vulnerabilidade['total_familias_maior_vulnerabilidade'] if resultado_vulnerabilidade else 0
    
    # Calcular número total de famílias cadastradas
    sql_total_familias = text(
        """
        SELECT COUNT(*) as total_familias
        FROM familias
        """
    )
    
    resultado_total_familias = db.session.execute(sql_total_familias).mappings().first()
    total_familias = resultado_total_familias['total_familias'] if resultado_total_familias else 0
    
    # Dados do dashboard calculados dinamicamente
    dados_dashboard = {
        'total_familias': total_familias,
        'familias_atendidas_30_dias': total_familias_atendidas_30_dias,
        'entregas_cestas_30_dias': total_entregas_cestas_30_dias,
        'familias_sem_atendimento_recente': total_familias_sem_atendimento_recente,
        'familias_demandas_ativas': total_demandas_ativas,
        'familias_maior_vulnerabilidade': total_familias_maior_vulnerabilidade
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
                a.data_entrega_cesta,
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


@app.route("/dashboard/entregas-cestas-30-dias")
@login_required
@admin_required
def dashboard_entregas_cestas_30_dias():
    """Lista de entregas de cestas realizadas nos últimos 30 dias."""
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
            a.data_entrega_cesta,
            a.data_hora_atendimento
        FROM familias f
        LEFT JOIN enderecos e ON f.familia_id = e.familia_id
        LEFT JOIN contatos c ON f.familia_id = c.familia_id
        INNER JOIN atendimentos a ON f.familia_id = a.familia_id
        WHERE a.data_hora_atendimento >= DATEADD(DAY, -30, GETDATE())
        AND a.cesta_entregue = 1
        ORDER BY a.data_hora_atendimento DESC
        """
    )

    resultados = db.session.execute(sql).mappings().all()
    entregas = [dict(r) for r in resultados]
    return render_template("dashboards/entregas_cestas_30_dias.html", entregas=entregas)


@app.route("/dashboard/familias-sem-atendimento-recente")
@login_required
@admin_required
def dashboard_familias_sem_atendimento_recente():
    """Lista de famílias cadastradas no último ano sem atendimento nos últimos 3 meses."""
    sql = text(
        """
        SELECT 
            f.familia_id, 
            f.nome_responsavel, 
            f.cpf, 
            e.bairro,
            c.telefone_principal, 
            c.email_responsavel,
            f.data_hora_log_utc as data_cadastro,
            ultimo_atendimento.ultima_data_atendimento
        FROM familias f
        LEFT JOIN enderecos e ON f.familia_id = e.familia_id
        LEFT JOIN contatos c ON f.familia_id = c.familia_id
        LEFT JOIN (
            SELECT 
                familia_id, 
                MAX(data_hora_atendimento) as ultima_data_atendimento
            FROM atendimentos 
            GROUP BY familia_id
        ) ultimo_atendimento ON f.familia_id = ultimo_atendimento.familia_id
        WHERE f.data_hora_log_utc >= DATEADD(YEAR, -1, GETDATE())
        AND (
            ultimo_atendimento.ultima_data_atendimento IS NULL 
            OR ultimo_atendimento.ultima_data_atendimento < DATEADD(DAY, -90, GETDATE())
        )
        ORDER BY f.data_hora_log_utc DESC
        """
    )

    resultados = db.session.execute(sql).mappings().all()
    familias = [dict(r) for r in resultados]
    return render_template("dashboards/familias_sem_atendimento_recente.html", familias=familias)


@app.route("/dashboard/familias-maior-vulnerabilidade")
@login_required
@admin_required
def dashboard_familias_maior_vulnerabilidade():
    """Lista de famílias em situação de maior vulnerabilidade (percepção alta)."""
    sql = text(
        """
        SELECT 
            f.familia_id,
            f.nome_responsavel,
            f.cpf,
            e.bairro,
            c.telefone_principal,
            c.email_responsavel,
            ultimo_atendimento.percepcao_necessidade,
            ultimo_atendimento.cesta_entregue,
            ultimo_atendimento.data_entrega_cesta,
            ultimo_atendimento.data_hora_atendimento,
            ultimo_atendimento.motivo_duracao
        FROM familias f
        LEFT JOIN enderecos e ON f.familia_id = e.familia_id
        LEFT JOIN contatos c ON f.familia_id = c.familia_id
        INNER JOIN (
            SELECT 
                a1.familia_id,
                a1.percepcao_necessidade,
                a1.cesta_entregue,
                a1.data_entrega_cesta,
                a1.data_hora_atendimento,
                a1.motivo_duracao,
                ROW_NUMBER() OVER (PARTITION BY a1.familia_id ORDER BY a1.data_hora_atendimento DESC) as rn
            FROM atendimentos a1
            WHERE a1.percepcao_necessidade = 'Alta'
        ) ultimo_atendimento ON f.familia_id = ultimo_atendimento.familia_id AND ultimo_atendimento.rn = 1
        ORDER BY ultimo_atendimento.data_hora_atendimento DESC
        """
    )

    resultados = db.session.execute(sql).mappings().all()
    familias = [dict(r) for r in resultados]
    return render_template("dashboards/familias_maior_vulnerabilidade.html", familias=familias)


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


@app.route("/dashboard/familias-atendidas-30-dias/download")
@login_required
@admin_required
def download_familias_atendidas_30_dias():
    """Download de arquivo Excel com dados completos das famílias atendidas nos últimos 30 dias."""
    try:
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
        WHERE EXISTS (
            SELECT 1 FROM atendimentos a2
            WHERE a2.familia_id = f.familia_id
              AND a2.data_hora_atendimento >= DATEADD(DAY, -30, GETDATE())
        )
        """

        sql_query = text(sql_query_string)
        resultados = db.session.execute(sql_query).mappings().all()
        if not resultados:
            return jsonify({"error": "Nenhum dado encontrado para exportação"}), 404

        dados = [dict(r) for r in resultados]
        df = pd.DataFrame(dados)

        for column in df.columns:
            if df[column].dtype == 'object':
                sample_values = df[column].dropna().head(5)
                if len(sample_values) > 0:
                    first_value = sample_values.iloc[0]
                    if hasattr(first_value, 'tzinfo') and first_value.tzinfo is not None:
                        df[column] = pd.to_datetime(df[column], errors='ignore').dt.tz_localize(None)
            elif 'datetime64[ns, ' in str(df[column].dtype):
                df[column] = df[column].dt.tz_localize(None)

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
        colunas_existentes = {k: v for k, v in colunas_pt.items() if k in df.columns}
        df = df.rename(columns=colunas_existentes)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Dados_Familias', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Dados_Familias']
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

        data_atual = datetime.now().strftime("%Y_%m_%d")
        nome_arquivo = f"familias_atendidas_30_dias_{data_atual}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar arquivo: {str(e)}"}), 500


@app.route("/dashboard/entregas-cestas-30-dias/download")
@login_required
@admin_required
def download_entregas_cestas_30_dias():
    """Download de arquivo Excel com dados completos das entregas de cestas nos últimos 30 dias."""
    try:
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
            a.*,
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
        INNER JOIN atendimentos a ON f.familia_id = a.familia_id
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
                a2.*
            FROM atendimentos a2
            WHERE a2.familia_id = f.familia_id
            FOR JSON PATH
        ) AS atendimentos_json(atendimentos)
        WHERE a.data_hora_atendimento >= DATEADD(DAY, -30, GETDATE())
        AND a.cesta_entregue = 1
        ORDER BY a.data_hora_atendimento DESC
        """

        sql_query = text(sql_query_string)
        resultados = db.session.execute(sql_query).mappings().all()
        if not resultados:
            return jsonify({"error": "Nenhum dado encontrado para exportação"}), 404

        dados = [dict(r) for r in resultados]
        df = pd.DataFrame(dados)

        # Tratamento de timezone para colunas datetime
        for column in df.columns:
            if df[column].dtype == 'object':
                sample_values = df[column].dropna().head(5)
                if len(sample_values) > 0:
                    first_value = sample_values.iloc[0]
                    if hasattr(first_value, 'tzinfo') and first_value.tzinfo is not None:
                        df[column] = pd.to_datetime(df[column], errors='ignore').dt.tz_localize(None)
            elif 'datetime64[ns, ' in str(df[column].dtype):
                df[column] = df[column].dt.tz_localize(None)

        # Renomeação das colunas para português
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
            'cep': 'CEP',
            'data_hora_atendimento': 'Data do Atendimento',
            'percepcao_necessidade': 'Percepção de Necessidade',
            'cesta_entregue': 'Cesta Entregue',
            'data_entrega_cesta': 'Data de Entrega da Cesta',
            'observacoes': 'Observações'
        }
        colunas_existentes = {k: v for k, v in colunas_pt.items() if k in df.columns}
        df = df.rename(columns=colunas_existentes)

        # Criação do arquivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Entregas_Cestas', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Entregas_Cestas']
            
            # Ajuste automático das colunas
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

        data_atual = datetime.now().strftime("%Y_%m_%d")
        nome_arquivo = f"entregas_cestas_30_dias_{data_atual}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar arquivo: {str(e)}"}), 500


@app.route("/dashboard/familias-sem-atendimento-recente/download")
@login_required
@admin_required
def download_familias_sem_atendimento_recente():
    """Download de arquivo Excel com dados completos das famílias sem atendimento recente."""
    try:
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
            ultimo_atendimento.ultima_data_atendimento,
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
        LEFT JOIN (
            SELECT 
                familia_id, 
                MAX(data_hora_atendimento) as ultima_data_atendimento
            FROM atendimentos 
            GROUP BY familia_id
        ) ultimo_atendimento ON f.familia_id = ultimo_atendimento.familia_id
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
        WHERE f.data_hora_log_utc >= DATEADD(YEAR, -1, GETDATE())
        AND (
            ultimo_atendimento.ultima_data_atendimento IS NULL 
            OR ultimo_atendimento.ultima_data_atendimento < DATEADD(DAY, -90, GETDATE())
        )
        ORDER BY f.data_hora_log_utc DESC
        """

        sql_query = text(sql_query_string)
        resultados = db.session.execute(sql_query).mappings().all()
        if not resultados:
            return jsonify({"error": "Nenhum dado encontrado para exportação"}), 404

        dados = [dict(r) for r in resultados]
        df = pd.DataFrame(dados)

        # Tratamento de timezone para colunas datetime
        for column in df.columns:
            if df[column].dtype == 'object':
                sample_values = df[column].dropna().head(5)
                if len(sample_values) > 0:
                    first_value = sample_values.iloc[0]
                    if hasattr(first_value, 'tzinfo') and first_value.tzinfo is not None:
                        df[column] = pd.to_datetime(df[column], errors='ignore').dt.tz_localize(None)
            elif 'datetime64[ns, ' in str(df[column].dtype):
                df[column] = df[column].dt.tz_localize(None)

        # Renomeação das colunas para português
        colunas_pt = {
            'familia_id': 'ID Família',
            'nome_responsavel': 'Nome do Responsável',
            'cpf': 'CPF',
            'data_nascimento': 'Data de Nascimento',
            'telefone_principal': 'Telefone Principal',
            'email': 'Email',
            'data_cadastro': 'Data de Cadastro',
            'data_hora_log_utc': 'Data do Cadastro',
            'logradouro': 'Logradouro',
            'numero': 'Número',
            'complemento': 'Complemento',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'Estado',
            'cep': 'CEP',
            'ultima_data_atendimento': 'Último Atendimento',
            'email_responsavel': 'Email do Responsável'
        }
        colunas_existentes = {k: v for k, v in colunas_pt.items() if k in df.columns}
        df = df.rename(columns=colunas_existentes)

        # Criação do arquivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Familias_Sem_Atendimento', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Familias_Sem_Atendimento']
            
            # Ajuste automático das colunas
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

        data_atual = datetime.now().strftime("%Y_%m_%d")
        nome_arquivo = f"familias_sem_atendimento_recente_{data_atual}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar arquivo: {str(e)}"}), 500


@app.route("/dashboard/demandas-ativas/download")
@login_required
@admin_required
def download_demandas_ativas():
    """Download de arquivo Excel com dados completos das demandas ativas."""
    try:
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
            df.*,
            dt.demanda_tipo_nome,
            de.status_atual,
            de.data_atualizacao,
            de.observacao as observacao_etapa,
            de.usuario_atualizacao,
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
        INNER JOIN demanda_familia df ON f.familia_id = df.familia_id
        INNER JOIN demanda_tipo dt ON df.demanda_tipo_id = dt.demanda_tipo_id
        INNER JOIN (
            SELECT de1.*
            FROM demanda_etapa de1
            INNER JOIN (
                SELECT demanda_id, MAX(etapa_id) AS max_etapa_id
                FROM demanda_etapa
                GROUP BY demanda_id
            ) m ON de1.demanda_id = m.demanda_id AND de1.etapa_id = m.max_etapa_id
        ) de ON df.demanda_id = de.demanda_id
        OUTER APPLY (
            SELECT
                a.*
            FROM atendimentos a
            WHERE a.familia_id = f.familia_id
            FOR JSON PATH
        ) AS atendimentos_json(atendimentos)
        ORDER BY df.prioridade ASC
        """

        sql_query = text(sql_query_string)
        resultados = db.session.execute(sql_query).mappings().all()
        if not resultados:
            return jsonify({"error": "Nenhum dado encontrado para exportação"}), 404

        dados = [dict(r) for r in resultados]
        df = pd.DataFrame(dados)

        # Tratamento de timezone para colunas datetime
        for column in df.columns:
            if df[column].dtype == 'object':
                sample_values = df[column].dropna().head(5)
                if len(sample_values) > 0:
                    first_value = sample_values.iloc[0]
                    if hasattr(first_value, 'tzinfo') and first_value.tzinfo is not None:
                        df[column] = pd.to_datetime(df[column], errors='ignore').dt.tz_localize(None)
            elif 'datetime64[ns, ' in str(df[column].dtype):
                df[column] = df[column].dt.tz_localize(None)

        # Renomeação das colunas para português
        colunas_pt = {
            'familia_id': 'ID Família',
            'nome_responsavel': 'Nome do Responsável',
            'cpf': 'CPF',
            'data_nascimento': 'Data de Nascimento',
            'telefone_principal': 'Telefone Principal',
            'email': 'Email',
            'data_cadastro': 'Data de Cadastro',
            'data_hora_log_utc': 'Data do Cadastro',
            'logradouro': 'Logradouro',
            'numero': 'Número',
            'complemento': 'Complemento',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'Estado',
            'cep': 'CEP',
            'email_responsavel': 'Email do Responsável',
            'demanda_id': 'ID Demanda',
            'descricao': 'Descrição da Demanda',
            'data_identificacao': 'Data de Identificação',
            'prioridade': 'Prioridade',
            'demanda_tipo_nome': 'Tipo de Demanda',
            'status_atual': 'Status Atual',
            'data_atualizacao': 'Data da Última Atualização',
            'observacao_etapa': 'Observações da Etapa',
            'usuario_atualizacao': 'Usuário da Última Atualização'
        }
        colunas_existentes = {k: v for k, v in colunas_pt.items() if k in df.columns}
        df = df.rename(columns=colunas_existentes)

        # Criação do arquivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Demandas_Ativas', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Demandas_Ativas']
            
            # Ajuste automático das colunas
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

        data_atual = datetime.now().strftime("%Y_%m_%d")
        nome_arquivo = f"demandas_ativas_{data_atual}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar arquivo: {str(e)}"}), 500


@app.route("/dashboard/familias-maior-vulnerabilidade/download")
@login_required
@admin_required
def download_familias_maior_vulnerabilidade():
    """Download de arquivo Excel com dados completos das famílias em maior vulnerabilidade."""
    # FUNÇÃO CORRIGIDA - SEM OBSERVACOES
    try:
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
            ultimo_atendimento.percepcao_necessidade,
            ultimo_atendimento.cesta_entregue,
            ultimo_atendimento.data_entrega_cesta,
            ultimo_atendimento.data_hora_atendimento,
            ultimo_atendimento.motivo_duracao,
            ultimo_atendimento.duracao_necessidade,
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
        INNER JOIN (
            SELECT 
                a1.familia_id,
                a1.percepcao_necessidade,
                a1.cesta_entregue,
                a1.data_entrega_cesta,
                a1.data_hora_atendimento,
                a1.motivo_duracao,
                a1.duracao_necessidade,
                ROW_NUMBER() OVER (PARTITION BY a1.familia_id ORDER BY a1.data_hora_atendimento DESC) as rn
            FROM atendimentos a1
            WHERE a1.percepcao_necessidade = 'Alta'
        ) ultimo_atendimento ON f.familia_id = ultimo_atendimento.familia_id AND ultimo_atendimento.rn = 1
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
        ORDER BY ultimo_atendimento.data_hora_atendimento DESC
        """

        sql_query = text(sql_query_string)
        resultados = db.session.execute(sql_query).mappings().all()
        if not resultados:
            return jsonify({"error": "Nenhum dado encontrado para exportação"}), 404

        dados = [dict(r) for r in resultados]
        df = pd.DataFrame(dados)

        # Tratamento de timezone para colunas datetime
        for column in df.columns:
            if df[column].dtype == 'object':
                sample_values = df[column].dropna().head(5)
                if len(sample_values) > 0:
                    first_value = sample_values.iloc[0]
                    if hasattr(first_value, 'tzinfo') and first_value.tzinfo is not None:
                        df[column] = pd.to_datetime(df[column], errors='ignore').dt.tz_localize(None)
            elif 'datetime64[ns, ' in str(df[column].dtype):
                df[column] = df[column].dt.tz_localize(None)

        # Renomeação das colunas para português
        colunas_pt = {
            'familia_id': 'ID Família',
            'nome_responsavel': 'Nome do Responsável',
            'cpf': 'CPF',
            'data_nascimento': 'Data de Nascimento',
            'telefone_principal': 'Telefone Principal',
            'email': 'Email',
            'data_cadastro': 'Data de Cadastro',
            'data_hora_log_utc': 'Data do Cadastro',
            'logradouro': 'Logradouro',
            'numero': 'Número',
            'complemento': 'Complemento',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'Estado',
            'cep': 'CEP',
            'email_responsavel': 'Email do Responsável',
            'percepcao_necessidade': 'Percepção de Necessidade',
            'cesta_entregue': 'Cesta Entregue',
            'data_entrega_cesta': 'Data de Entrega da Cesta',
            'data_hora_atendimento': 'Data do Atendimento',
            'motivo_duracao': 'Motivo/Duração',
            'duracao_necessidade': 'Duração da Necessidade'
        }
        colunas_existentes = {k: v for k, v in colunas_pt.items() if k in df.columns}
        df = df.rename(columns=colunas_existentes)

        # Criação do arquivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Familias_Alta_Vulnerabilidade', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Familias_Alta_Vulnerabilidade']
            
            # Ajuste automático das colunas
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

        data_atual = datetime.now().strftime("%Y_%m_%d")
        nome_arquivo = f"familias_maior_vulnerabilidade_{data_atual}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar arquivo: {str(e)}"}), 500


@app.route("/buscar_pre_cadastro")
@login_required
def buscar_pre_cadastro():
    """Busca pré-cadastros no banco de dados de pré-cadastro."""
    termo = request.args.get("q", "").strip()
    
    if not termo:
        return jsonify({"resultados": []})
    
    try:
        resultados = buscar_pre_cadastros(termo)
        return jsonify({"resultados": resultados})
    except Exception as e:
        print(f"Erro ao buscar pré-cadastros: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500


@app.route("/carregar_pre_cadastro", methods=["POST"])
@login_required
def carregar_pre_cadastro():
    """Carrega dados do pré-cadastro na sessão para iniciar atendimento."""
    try:
        dados_familia = request.get_json()
        if not dados_familia or not dados_familia.get('dados_completos'):
            return jsonify({"success": False, "message": "Dados inválidos"})
        
        # Resetar sessão de atendimento
        reset_atendimento_sessao()
        
        # Converter dados do pré-cadastro para formato da sessão
        cadastro = converter_pre_cadastro_para_sessao(dados_familia['dados_completos'])
        
        # Salvar na sessão
        session['cadastro'] = cadastro
        session['cadastro_inicio'] = datetime.utcnow().isoformat()
        
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Erro ao carregar pré-cadastro: {str(e)}")
        return jsonify({"success": False, "message": "Erro interno do servidor"})


if __name__ == "__main__":
    app.run(debug=True)
