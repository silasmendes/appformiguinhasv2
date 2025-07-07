from flask import session
from datetime import datetime
from app import db
from app.models.familia import Familia
from app.models.endereco import Endereco
from app.models.composicao_familiar import ComposicaoFamiliar
from app.models.contato import Contato
from app.models.condicoes_moradia import CondicaoMoradia
from app.models.saude_familiar import SaudeFamiliar
from app.models.emprego_provedor import EmpregoProvedor
from app.models.renda_familiar import RendaFamiliar
from app.models.educacao_entrevistado import EducacaoEntrevistado
from app.models.demanda_familia import DemandaFamilia
from app.models.demanda_etapa import DemandaEtapa
from app.models.demanda_tipo import DemandaTipo
from sqlalchemy import func, and_

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


def get_cadastro():
    if "cadastro" not in session:
        session["cadastro"] = {}
    return session["cadastro"]


def carregar_cadastro_familia(familia_id):
    """Carrega dados da família e de demandas ativas para a sessão."""
    familia = db.session.get(Familia, familia_id)
    if not familia:
        return None

    cadastro = {}
    cadastro["novo_cadastro"] = 0

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

    ult_etapa = (
        db.session.query(
            DemandaEtapa.demanda_id,
            func.max(DemandaEtapa.etapa_id).label("etapa_id")
        )
        .group_by(DemandaEtapa.demanda_id)
        .subquery()
    )

    active_statuses = [
        "Em análise",
        "Em andamento",
        "Encaminhada",
        "Aguardando resposta",
        "Suspensa",
    ]

    demandas_rows = (
        db.session.query(
            DemandaFamilia.demanda_id,
            DemandaTipo.demanda_tipo_nome,
            DemandaFamilia.descricao,
            DemandaFamilia.prioridade,
            DemandaEtapa.status_atual,
            DemandaEtapa.observacao,
        )
        .join(ult_etapa, DemandaFamilia.demanda_id == ult_etapa.c.demanda_id)
        .join(
            DemandaEtapa,
            and_(
                DemandaEtapa.demanda_id == ult_etapa.c.demanda_id,
                DemandaEtapa.etapa_id == ult_etapa.c.etapa_id,
            ),
        )
        .join(DemandaTipo, DemandaTipo.demanda_tipo_id == DemandaFamilia.demanda_tipo_id)
        .filter(DemandaFamilia.familia_id == familia_id)
        .filter(DemandaFamilia.status.in_(active_statuses))
        .all()
    )

    cadastro["demandas"] = [
        {
            "demanda_id": row.demanda_id,
            "categoria": row.demanda_tipo_nome,
            "descricao": row.descricao,
            "prioridade": row.prioridade,
            "status_atual": row.status_atual,
            "observacao": row.observacao,
        }
        for row in demandas_rows
    ]

    session["cadastro"] = cadastro
    session["familia_id"] = familia_id
    return cadastro
