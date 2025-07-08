from flask import render_template, session, request, redirect, url_for, flash
from flask_login import login_required
from app.routes.usuarios import admin_required
import json
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
    
    # Dados mock para demonstração (outros valores podem ser calculados dinamicamente no futuro)
    dados_dashboard = {
        'total_familias': 48,
        'familias_atendidas_30_dias': 26,
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
    from datetime import datetime
    import pandas as pd
    from io import BytesIO
    from flask import send_file
    
    try:
        # Query simplificada para evitar problemas com JSON no SQL Server
        sql_query = text("""
            SELECT 
                f.familia_id,
                f.nome_responsavel,
                f.cpf,
                f.data_nascimento,
                f.telefone_principal,
                f.email,
                f.data_cadastro,
                e.logradouro,
                e.numero,
                e.complemento,
                e.bairro,
                e.cidade,
                e.estado,
                e.cep,
                c.telefone_alternativo,
                c.telefone_emergencia,
                c.contato_emergencia_nome,
                cf.total_pessoas,
                cf.criancas_0_5,
                cf.criancas_6_12,
                cf.adolescentes_13_17,
                cf.adultos_18_59,
                cf.idosos_60_mais,
                cm.tipo_moradia,
                cm.situacao_moradia,
                cm.num_comodos,
                ed.escolaridade,
                ed.sabe_ler_escrever,
                ep.situacao_trabalho,
                ep.profissao,
                ep.renda_mensal,
                rf.renda_total_familiar,
                rf.beneficios_sociais,
                sf.problema_saude_familia,
                sf.medicacao_continua,
                sf.deficiencia_familia
            FROM familias f
            LEFT JOIN enderecos e ON f.familia_id = e.familia_id
            LEFT JOIN contatos c ON f.familia_id = c.familia_id
            LEFT JOIN composicao_familiar cf ON f.familia_id = cf.familia_id
            LEFT JOIN condicoes_moradia cm ON f.familia_id = cm.familia_id
            LEFT JOIN educacao_entrevistado ed ON f.familia_id = ed.familia_id
            LEFT JOIN emprego_provedor ep ON f.familia_id = ep.familia_id
            LEFT JOIN renda_familiar rf ON f.familia_id = rf.familia_id
            LEFT JOIN saude_familiar sf ON f.familia_id = sf.familia_id
            ORDER BY f.familia_id
        """)
        
        # Executar query e converter para DataFrame
        resultados = db.session.execute(sql_query).mappings().all()
        
        if not resultados:
            flash("Nenhum dado encontrado para exportação.", "warning")
            return redirect(url_for("dashboard_familias_cadastradas"))
        
        # Converter para lista de dicionários
        dados = [dict(r) for r in resultados]
        
        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        # Renomear colunas para português
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
            'telefone_alternativo': 'Telefone Alternativo',
            'telefone_emergencia': 'Telefone Emergência',
            'contato_emergencia_nome': 'Nome Contato Emergência',
            'total_pessoas': 'Total de Pessoas',
            'criancas_0_5': 'Crianças 0-5 anos',
            'criancas_6_12': 'Crianças 6-12 anos',
            'adolescentes_13_17': 'Adolescentes 13-17 anos',
            'adultos_18_59': 'Adultos 18-59 anos',
            'idosos_60_mais': 'Idosos 60+ anos',
            'tipo_moradia': 'Tipo de Moradia',
            'situacao_moradia': 'Situação da Moradia',
            'num_comodos': 'Número de Cômodos',
            'escolaridade': 'Escolaridade',
            'sabe_ler_escrever': 'Sabe Ler/Escrever',
            'situacao_trabalho': 'Situação de Trabalho',
            'profissao': 'Profissão',
            'renda_mensal': 'Renda Mensal',
            'renda_total_familiar': 'Renda Total Familiar',
            'beneficios_sociais': 'Benefícios Sociais',
            'problema_saude_familia': 'Problemas de Saúde',
            'medicacao_continua': 'Medicação Contínua',
            'deficiencia_familia': 'Deficiência na Família'
        }
        
        # Aplicar nomes das colunas em português
        df = df.rename(columns=colunas_pt)
        
        # Criar buffer em memória para o arquivo Excel
        output = BytesIO()
        
        # Criar arquivo Excel
        with pd.ExcelWriter(output, engine='openpyxl', options={'remove_timezone': True}) as writer:
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
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Gerar nome do arquivo com data atual
        data_atual = datetime.now().strftime("%Y_%m_%d")
        nome_arquivo = f"migracao_familias_{data_atual}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"Erro detalhado: {str(e)}")  # Para debug
        flash(f"Erro ao gerar arquivo: {str(e)}", "danger")
        return redirect(url_for("dashboard_familias_cadastradas"))


if __name__ == "__main__":
    app.run(debug=True)
