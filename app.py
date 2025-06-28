from flask import render_template, session, request, redirect, url_for, flash
import json
from datetime import datetime, timedelta
from app import create_app
from app import db
from app.models.familia import Familia
from app.models.atendimento import Atendimento
from sqlalchemy import func, or_
from app.models.endereco import Endereco
from app.models.composicao_familiar import ComposicaoFamiliar
from app.models.contato import Contato
from app.models.condicoes_moradia import CondicaoMoradia
from app.models.saude_familiar import SaudeFamiliar
from app.models.emprego_provedor import EmpregoProvedor
from app.models.renda_familiar import RendaFamiliar
from app.models.educacao_entrevistado import EducacaoEntrevistado

app = create_app()

ETAPAS = [
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
    "encerramento",
]


def reset_atendimento_sessao():
    """Remove informações de atendimento da sessão."""
    session.pop("cadastro", None)
    session.pop("cadastro_inicio", None)
    session.pop("familia_id", None)


def _bool_to_sim_nao(valor):
    if valor is None:
        return None
    return "Sim" if valor else "Não"

@app.route("/")
def home():
    """Renderiza a página inicial."""
    return render_template("index.html")

@app.route("/menu_atendimento")
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

@app.route("/atendimento_nova_familia")
def atendimento_nova_familia():
    reset_atendimento_sessao()
    return redirect(url_for("atendimento_etapa1"))

@app.route("/retomar_atendimento")
def retomar_atendimento():
    cadastro = session.get("cadastro")
    inicio_str = session.get("cadastro_inicio")
    if cadastro and inicio_str:
        try:
            inicio = datetime.fromisoformat(inicio_str)
            if datetime.utcnow() - inicio < timedelta(hours=1):
                return redirect(url_for("atendimento_etapa1"))
        except ValueError:
            pass
    reset_atendimento_sessao()
    error_msg = ("Nenhum atendimento em andamento foi encontrado ou o tempo expirou. "
                 "Inicie um novo atendimento usando a opção \"Atender família\".")
    return render_template("atendimento/etapa0_menu.html", error_msg=error_msg, auto_open=False)


@app.route("/atendimento_familia/<int:familia_id>")
def atendimento_familia(familia_id):
    """Carrega dados de uma família existente para iniciar o atendimento."""
    reset_atendimento_sessao()
    familia = db.session.get(Familia, familia_id)
    if not familia:
        flash("Família não encontrada", "danger")
        return redirect(url_for("menu_atendimento"))

    cadastro = get_cadastro()
    session["familia_id"] = familia_id

    cadastro.update({
        "nome_responsavel": familia.nome_responsavel,
        "data_nascimento": familia.data_nascimento.strftime('%d/%m/%Y') if familia.data_nascimento else None,
        "genero": familia.genero,
        "genero_autodeclarado": familia.genero_autodeclarado,
        "estado_civil": familia.estado_civil,
        "rg": familia.rg,
        "cpf": familia.cpf,
    })
    if familia.autoriza_uso_imagem is not None:
        cadastro["autoriza_uso_imagem"] = _bool_to_sim_nao(familia.autoriza_uso_imagem)

    endereco = Endereco.query.filter_by(familia_id=familia_id).first()
    if endereco:
        cadastro.update({
            "preenchimento_manual": endereco.preenchimento_manual,
            "cep": endereco.cep,
            "logradouro": endereco.logradouro,
            "numero": endereco.numero,
            "complemento": endereco.complemento,
            "bairro": endereco.bairro,
            "cidade": endereco.cidade,
            "estado": endereco.estado,
            "ponto_referencia": endereco.ponto_referencia,
        })

    comp = ComposicaoFamiliar.query.filter_by(familia_id=familia_id).first()
    if comp:
        cadastro.update({
            "total_residentes": comp.total_residentes,
            "quantidade_bebes": comp.quantidade_bebes,
            "quantidade_criancas": comp.quantidade_criancas,
            "quantidade_adolescentes": comp.quantidade_adolescentes,
            "quantidade_adultos": comp.quantidade_adultos,
            "quantidade_idosos": comp.quantidade_idosos,
            "motivo_ausencia_escola": comp.motivo_ausencia_escola,
        })
        if comp.tem_menores_na_escola is not None:
            cadastro["menores_na_escola"] = _bool_to_sim_nao(comp.tem_menores_na_escola)

    contato = Contato.query.filter_by(familia_id=familia_id).first()
    if contato:
        cadastro.update({
            "telefone_principal": contato.telefone_principal,
            "telefone_principal_whatsapp": contato.telefone_principal_whatsapp,
            "telefone_principal_nome_contato": contato.telefone_principal_nome_contato,
            "telefone_alternativo": contato.telefone_alternativo,
            "telefone_alternativo_whatsapp": contato.telefone_alternativo_whatsapp,
            "telefone_alternativo_nome_contato": contato.telefone_alternativo_nome_contato,
            "email_responsavel": contato.email_responsavel,
        })

    cond = CondicaoMoradia.query.filter_by(familia_id=familia_id).first()
    if cond:
        cadastro.update({
            "tipo_moradia": cond.tipo_moradia,
            "valor_aluguel": str(cond.valor_aluguel) if cond.valor_aluguel is not None else None,
            "num_camas": cond.quantidade_camas,
            "num_tvs": cond.quantidade_tvs,
            "num_ventiladores": cond.quantidade_ventiladores,
        })
        if cond.tem_agua_encanada is not None:
            cadastro["agua_encanada"] = _bool_to_sim_nao(cond.tem_agua_encanada)
        if cond.tem_rede_esgoto is not None:
            cadastro["rede_esgoto"] = _bool_to_sim_nao(cond.tem_rede_esgoto)
        if cond.tem_energia_eletrica is not None:
            cadastro["energia_eletrica"] = _bool_to_sim_nao(cond.tem_energia_eletrica)
        if cond.tem_fogao is not None:
            cadastro["tem_fogao"] = _bool_to_sim_nao(cond.tem_fogao)
        if cond.tem_geladeira is not None:
            cadastro["tem_geladeira"] = _bool_to_sim_nao(cond.tem_geladeira)

    saude = SaudeFamiliar.query.filter_by(familia_id=familia_id).first()
    if saude:
        cadastro.update({
            "descricao_doenca_cronica": saude.descricao_doenca_cronica,
            "descricao_medicacao": saude.descricao_medicacao,
            "descricao_deficiencia": saude.descricao_deficiencia,
        })
        if saude.tem_doenca_cronica is not None:
            cadastro["tem_doenca_cronica"] = _bool_to_sim_nao(saude.tem_doenca_cronica)
        if saude.usa_medicacao_continua is not None:
            cadastro["usa_medicacao_continua"] = _bool_to_sim_nao(saude.usa_medicacao_continua)
        if saude.tem_deficiencia is not None:
            cadastro["tem_deficiencia"] = _bool_to_sim_nao(saude.tem_deficiencia)
        if saude.recebe_bpc is not None:
            cadastro["recebe_bpc"] = _bool_to_sim_nao(saude.recebe_bpc)

    emprego = EmpregoProvedor.query.filter_by(familia_id=familia_id).first()
    if emprego:
        cadastro.update({
            "relacao_provedor_familia": emprego.relacao_provedor_familia,
            "descricao_provedor_externo": emprego.descricao_provedor_externo,
            "situacao_emprego": emprego.situacao_emprego,
            "descricao_situacao_emprego_outro": emprego.descricao_situacao_emprego_outro,
            "profissao_provedor": emprego.profissao_provedor,
            "experiencia_profissional": emprego.experiencia_profissional,
            "formacao_profissional": emprego.formacao_profissional,
            "habilidades_relevantes": emprego.habilidades_relevantes,
        })

    renda = RendaFamiliar.query.filter_by(familia_id=familia_id).first()
    if renda:
        cadastro.update({
            "gastos_supermercado": str(renda.gastos_supermercado) if renda.gastos_supermercado is not None else None,
            "gastos_energia_eletrica": str(renda.gastos_energia_eletrica) if renda.gastos_energia_eletrica is not None else None,
            "gastos_agua": str(renda.gastos_agua) if renda.gastos_agua is not None else None,
            "valor_botija_gas": str(renda.valor_botijao_gas) if renda.valor_botijao_gas is not None else None,
            "duracao_botija_gas": renda.duracao_botijao_gas,
            "gastos_gas": str(renda.gastos_gas) if renda.gastos_gas is not None else None,
            "gastos_transporte": str(renda.gastos_transporte) if renda.gastos_transporte is not None else None,
            "gastos_medicamentos": str(renda.gastos_medicamentos) if renda.gastos_medicamentos is not None else None,
            "gastos_conta_celular": str(renda.gastos_celular) if renda.gastos_celular is not None else None,
            "gastos_outros": str(renda.gastos_outros) if renda.gastos_outros is not None else None,
            "renda_arrimo": str(renda.renda_provedor_principal) if renda.renda_provedor_principal is not None else None,
            "renda_outros_familiares": str(renda.renda_outros_moradores) if renda.renda_outros_moradores is not None else None,
            "auxilio_parentes_amigos": str(renda.ajuda_terceiros) if renda.ajuda_terceiros is not None else None,
            "descricao_beneficios": renda.descricao_beneficios,
            "valor_total_beneficios": str(renda.valor_beneficios) if renda.valor_beneficios is not None else None,
            "renda_familiar_total": str(renda.renda_total_familiar) if renda.renda_total_familiar is not None else None,
            "total_gastos": str(renda.gastos_totais) if renda.gastos_totais is not None else None,
            "saldo": str(renda.saldo_mensal) if renda.saldo_mensal is not None else None,
        })
        if renda.possui_cadastro_unico is not None:
            cadastro["cadastro_unico"] = _bool_to_sim_nao(renda.possui_cadastro_unico)
        if renda.recebe_beneficios_governo is not None:
            cadastro["recebe_beneficio"] = _bool_to_sim_nao(renda.recebe_beneficios_governo)

    educacao = EducacaoEntrevistado.query.filter_by(familia_id=familia_id).first()
    if educacao:
        cadastro.update({
            "nivel_escolaridade": educacao.nivel_escolaridade,
            "curso_ou_serie_atual": educacao.curso_ou_serie_atual,
        })
        if educacao.estuda_atualmente is not None:
            cadastro["estuda_atualmente"] = _bool_to_sim_nao(educacao.estuda_atualmente)

    session["cadastro"] = cadastro
    return redirect(url_for("atendimento_etapa1"))


def get_cadastro():
    if "cadastro" not in session:
        session["cadastro"] = {}
    return session["cadastro"]


@app.route("/atendimento/etapa1", methods=["GET", "POST"])
def atendimento_etapa1():
    """Exibe a primeira etapa do atendimento à família."""
    cadastro = get_cadastro()
    if "cadastro_inicio" not in session:
        session["cadastro_inicio"] = datetime.utcnow().isoformat()
    if request.method == "POST":
        form_data = request.form.to_dict(flat=True)
        cadastro.update(form_data)
        session["cadastro"] = cadastro
        if form_data.get("familia_id"):
            session["familia_id"] = form_data["familia_id"]
        return redirect(url_for("atendimento_etapa2"))
    return render_template(
        "atendimento/etapa1_dados_pessoais.html",
        etapa_atual=1,
        etapas=ETAPAS,
    )


@app.route("/atendimento/etapa2", methods=["GET", "POST"])
def atendimento_etapa2():
    """Exibe a segunda etapa do atendimento à família."""
    cadastro = get_cadastro()
    if request.method == "POST":
        cadastro.update(request.form.to_dict(flat=True))
        session["cadastro"] = cadastro
        return redirect(url_for("atendimento_etapa3"))
    return render_template(
        "atendimento/etapa2_endereco.html",
        etapa_atual=2,
        etapas=ETAPAS,
    )


@app.route("/atendimento/etapa3", methods=["GET", "POST"])
def atendimento_etapa3():
    """Exibe a terceira etapa do atendimento à família."""
    cadastro = get_cadastro()
    if request.method == "POST":
        cadastro.update(request.form.to_dict(flat=True))
        session["cadastro"] = cadastro
        return redirect(url_for("atendimento_etapa4"))
    return render_template(
        "atendimento/etapa3_composicao_familiar.html",
        etapa_atual=3,
        etapas=ETAPAS,
    )


@app.route("/atendimento/etapa4", methods=["GET", "POST"])
def atendimento_etapa4():
    """Exibe a quarta etapa do atendimento à família."""
    cadastro = get_cadastro()
    if request.method == "POST":
        cadastro.update(request.form.to_dict(flat=True))
        session["cadastro"] = cadastro
        return redirect(url_for("atendimento_etapa5"))
    return render_template(
        "atendimento/etapa4_contato.html",
        etapa_atual=4,
        etapas=ETAPAS,
    )


@app.route("/atendimento/etapa5", methods=["GET", "POST"])
def atendimento_etapa5():
    """Exibe a quinta etapa do atendimento à família."""
    cadastro = get_cadastro()
    if request.method == "POST":
        cadastro.update(request.form.to_dict(flat=True))
        session["cadastro"] = cadastro
        return redirect(url_for("atendimento_etapa6"))
    return render_template(
        "atendimento/etapa5_condicoes_habitacionais.html",
        etapa_atual=5,
        etapas=ETAPAS,
    )


@app.route("/atendimento/etapa6", methods=["GET", "POST"])
def atendimento_etapa6():
    """Exibe a sexta etapa do atendimento à família."""
    cadastro = get_cadastro()
    if request.method == "POST":
        cadastro.update(request.form.to_dict(flat=True))
        session["cadastro"] = cadastro
        return redirect(url_for("atendimento_etapa7"))
    return render_template(
        "atendimento/etapa6_saude_familiar.html",
        etapa_atual=6,
        etapas=ETAPAS,
    )


@app.route("/atendimento/etapa7", methods=["GET", "POST"])
def atendimento_etapa7():
    """Exibe a sétima etapa do atendimento à família."""
    cadastro = get_cadastro()
    if request.method == "POST":
        cadastro.update(request.form.to_dict(flat=True))
        session["cadastro"] = cadastro
        return redirect(url_for("atendimento_etapa8"))
    return render_template(
        "atendimento/etapa7_emprego_e_habilidades.html",
        etapa_atual=7,
        etapas=ETAPAS,
    )


@app.route("/atendimento/etapa8", methods=["GET", "POST"])
def atendimento_etapa8():
    """Exibe a oitava etapa do atendimento à família."""
    cadastro = get_cadastro()
    if request.method == "POST":
        cadastro.update(request.form.to_dict(flat=True))
        session["cadastro"] = cadastro
        return redirect(url_for("atendimento_etapa9"))
    return render_template(
        "atendimento/etapa8_renda_e_gastos.html",
        etapa_atual=8,
        etapas=ETAPAS,
    )


@app.route("/atendimento/etapa9", methods=["GET", "POST"])
def atendimento_etapa9():
    """Exibe a nona etapa do atendimento à família."""
    cadastro = get_cadastro()
    if request.method == "POST":
        cadastro.update(request.form.to_dict(flat=True))
        session["cadastro"] = cadastro
        return redirect(url_for("atendimento_etapa10"))
    return render_template(
        "atendimento/etapa9_escolaridade.html",
        etapa_atual=9,
        etapas=ETAPAS,
    )


@app.route("/atendimento/etapa10", methods=["GET", "POST"])
def atendimento_etapa10():
    """Exibe a décima etapa do atendimento à família."""
    cadastro = get_cadastro()
    if request.method == "POST":
        cadastro.update(request.form.to_dict(flat=True))
        demandas_json = request.form.get("demandas_json")
        if demandas_json:
            try:
                cadastro["demandas"] = json.loads(demandas_json)
            except Exception:
                cadastro["demandas"] = []
        session["cadastro"] = cadastro
        return redirect(url_for("atendimento_etapa11"))
    return render_template(
        "atendimento/etapa10_outras_necessidades.html",
        etapa_atual=10,
        etapas=ETAPAS,
    )


@app.route("/atendimento/etapa11", methods=["GET", "POST"])
def atendimento_etapa11():
    """Exibe a etapa final do atendimento à família."""
    cadastro = get_cadastro()
    if request.method == "POST":
        cadastro.update(request.form.to_dict(flat=True))
        session["cadastro"] = cadastro
        reset_atendimento_sessao()
        return redirect(url_for("home"))
    return render_template(
        "atendimento/etapa11_atendimento.html",
        etapa_atual=11,
        etapas=ETAPAS,
    )


if __name__ == "__main__":
    app.run(debug=True)
