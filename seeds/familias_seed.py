"""Dados fictícios para testar os CPFs anunciados na modal de atendimento."""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func

from app import db
from app.models.familia import Familia
from app.models.endereco import Endereco
from app.models.contato import Contato
from app.models.composicao_familiar import ComposicaoFamiliar
from app.models.condicoes_moradia import CondicaoMoradia
from app.models.saude_familiar import SaudeFamiliar
from app.models.emprego_provedor import EmpregoProvedor
from app.models.renda_familiar import RendaFamiliar
from app.models.educacao_entrevistado import EducacaoEntrevistado
from app.models.atendimento import Atendimento


FAMILIAS_TESTE = (
    ("525.067.333-37", "Ana Silva (Teste)", date(1988, 3, 12), "Feminino"),
    ("928.105.770-05", "Carlos Santos (Teste)", date(1980, 7, 24), "Masculino"),
    ("955.314.618-01", "Mariana Costa (Teste)", date(1993, 11, 5), "Feminino"),
    ("742.691.086-57", "Paulo Oliveira (Teste)", date(1975, 1, 18), "Masculino"),
)


MODELOS_COMPLEMENTARES = (
    Endereco, Contato, ComposicaoFamiliar, CondicaoMoradia, SaudeFamiliar,
    EmpregoProvedor, RendaFamiliar, EducacaoEntrevistado, Atendimento,
)


def _normalizar_textos_vazios(registro):
    """Usa o mesmo texto vazio enviado pelos formulários para campos sem valor."""
    for coluna in registro.__table__.columns:
        if coluna.nullable and isinstance(coluna.type, db.String):
            valor = getattr(registro, coluna.name)
            if valor is None or valor == "None":
                setattr(registro, coluna.name, "")


def seed_familias():
    """Cria famílias ausentes e corrige textos vazios sem sobrescrever dados preenchidos."""
    criadas = 0
    cpf_normalizado = func.replace(func.replace(Familia.cpf, '.', ''), '-', '')
    for indice, (cpf, nome, nascimento, genero) in enumerate(FAMILIAS_TESTE):
        existente = Familia.query.filter(cpf_normalizado == cpf.replace('.', '').replace('-', '')).first()
        if existente:
            _normalizar_textos_vazios(existente)
            for modelo in MODELOS_COMPLEMENTARES:
                for registro in modelo.query.filter_by(familia_id=existente.familia_id):
                    _normalizar_textos_vazios(registro)
            continue
        familia = Familia(
            cpf=cpf, nome_responsavel=nome, data_nascimento=nascimento,
            genero=genero, estado_civil="Solteira(o)",
            nome_mae="Responsável materna (Teste)", nome_pai="Responsável paterno (Teste)",
            autoriza_uso_imagem=False, status_cadastro="finalizado",
        )
        _normalizar_textos_vazios(familia)
        db.session.add(familia)
        db.session.flush()
        familia_id = familia.familia_id
        complementares = [
            Endereco(familia_id=familia_id, preenchimento_manual=True,
                     cep="13010-000", logradouro="Rua Fictícia", numero=str(100 + indice),
                     bairro="Centro", cidade="Campinas", estado="SP",
                     complemento="Endereço fictício para testes"),
            Contato(familia_id=familia_id, email_responsavel=f"familia.teste{indice + 1}@example.com"),
            ComposicaoFamiliar(familia_id=familia_id, total_residentes=4,
                              quantidade_bebes=0, quantidade_criancas=1,
                              quantidade_adolescentes=1, quantidade_adultos=2,
                              quantidade_idosos=0, tem_menores_na_escola=True),
            CondicaoMoradia(familia_id=familia_id, tipo_moradia="Alugada",
                           valor_aluguel=700, tem_agua_encanada=True, tem_rede_esgoto=True,
                           tem_energia_eletrica=True, tem_fogao=True, tem_geladeira=True,
                           quantidade_camas=3, quantidade_tvs=1, quantidade_ventiladores=1),
            SaudeFamiliar(familia_id=familia_id, tem_doenca_cronica=False,
                          usa_medicacao_continua=False, tem_deficiencia=False, recebe_bpc=False),
            EmpregoProvedor(familia_id=familia_id, relacao_provedor_familia="Próprio entrevistado",
                            situacao_emprego="Empregado", profissao_provedor="Auxiliar de serviços gerais"),
            RendaFamiliar(familia_id=familia_id, renda_provedor_principal=1800,
                          renda_outros_moradores=0, ajuda_terceiros=0, valor_beneficios=0,
                          renda_total_familiar=1800, gastos_supermercado=600,
                          gastos_energia_eletrica=90, gastos_agua=50,
                          valor_botijao_gas=100, duracao_botijao_gas=2, gastos_gas=50,
                          gastos_transporte=40, gastos_celular=55,
                          gastos_totais=1585, saldo_mensal=215,
                          possui_cadastro_unico=True, recebe_beneficios_governo=False),
            EducacaoEntrevistado(familia_id=familia_id, nivel_escolaridade="Ensino Médio Completo",
                                 estuda_atualmente="Não"),
            Atendimento(familia_id=familia_id, percepcao_necessidade="Alta" if indice == 0 else "Média",
                        duracao_necessidade="Temporária", motivo_duracao="Atendimento fictício para testes",
                        tipo_atendimento="Atendimento na base", cesta_entregue=indice == 0,
                        data_entrega_cesta=date.today() if indice == 0 else None,
                        data_hora_atendimento=datetime.now(timezone.utc) - timedelta(days=indice * 7)),
        ]
        for registro in complementares:
            _normalizar_textos_vazios(registro)
        db.session.add_all(complementares)
        criadas += 1
    db.session.commit()
    return criadas
