from flask import render_template, session, request, redirect, url_for, flash
from flask_login import login_required
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
def dashboard():
    """Renderiza a página do dashboard."""
    # Dados mock para demonstração
    dados_dashboard = {
        'total_familias': 48,
        'familias_atendidas_30_dias': 26,
        'entregas_cestas_30_dias': 24,
        'bairro_mais_atendimentos': 'Campo Belo',
        'familias_demandas_ativas': 5,
        'familias_maior_vulnerabilidade': 7
    }
    return render_template("dashboards/dashboard.html", dados=dados_dashboard)


@app.route("/dashboard/demandas-ativas")
@login_required
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


if __name__ == "__main__":
    app.run(debug=True)
