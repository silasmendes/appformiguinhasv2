import os
import random
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pytest
import requests
from dotenv import load_dotenv
from playwright.sync_api import Page, expect, sync_playwright

load_dotenv()

DEFAULT_LOCAL_URL = "http://127.0.0.1:5000"
DEFAULT_PROD_URL = "https://formiguinhasbr-a4g2cxeycmh8f7gy.brazilsouth-01.azurewebsites.net"
STEP_TIMEOUT = 45_000
API_WAIT_SECONDS = 20

RUN_COUNT = max(1, int(os.getenv("ATENDIMENTO_RUNS", "1")))

pytestmark = pytest.mark.e2e


def _str_to_bool(value: Optional[str], default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_base_url() -> str:
    explicit = os.getenv("ATENDIMENTO_BASE_URL")
    if explicit:
        return explicit.rstrip("/")
    target = os.getenv("ATENDIMENTO_TARGET", "local").strip().lower()
    if target in {"prod", "production", "remote", "azure"}:
        return os.getenv("ATENDIMENTO_PROD_URL", DEFAULT_PROD_URL).rstrip("/")
    return DEFAULT_LOCAL_URL


def _resolve_headless() -> bool:
    return _str_to_bool(os.getenv("PLAYWRIGHT_HEADLESS", "1"), True)


def _resolve_slow_mo() -> int:
    raw = os.getenv("PLAYWRIGHT_SLOW_MO")
    if not raw:
        return 0
    try:
        return max(0, int(raw))
    except ValueError:
        return 0


@pytest.fixture(scope="session")
def base_url() -> str:
    return _resolve_base_url()


@pytest.fixture(scope="session")
def admin_login() -> str:
    return os.getenv("USUARIO_ADMIN", "admin")


@pytest.fixture(scope="session")
def senha_admin() -> str:
    senha = os.getenv("SENHA_ADMIN")
    if not senha:
        pytest.skip("Configure a variavel de ambiente SENHA_ADMIN para executar o teste E2E.")
    return senha


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=_resolve_headless(),
            slow_mo=_resolve_slow_mo()
        )
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


def texto_aleatorio(prefix: str) -> str:
    return f"{prefix} {random.randint(1000, 9999)}"


def gerar_cpf_valido() -> str:
    cpf = [random.randint(0, 9) for _ in range(9)]
    soma = sum((cpf[i] * (10 - i)) for i in range(9))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    soma = sum((cpf[i] * (11 - i)) for i in range(10))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    numeros = "".join(str(d) for d in cpf)
    return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"


def gerar_data_nascimento(min_idade: int = 21, max_idade: int = 58) -> str:
    idade = random.randint(min_idade, max_idade)
    dias_extra = random.randint(0, 364)
    nascimento = datetime.utcnow() - timedelta(days=idade * 365 + dias_extra)
    return nascimento.strftime("%d/%m/%Y")


def gerar_dados_pessoa() -> Dict[str, Any]:
    nomes_fem = ["Maria", "Ana", "Julia", "Mariana", "Patricia", "Claudia"]
    nomes_masc = ["Joao", "Jose", "Carlos", "Marcos", "Ricardo", "Paulo"]
    sobrenomes = ["Silva", "Santos", "Oliveira", "Costa", "Almeida", "Fernandes"]
    genero = random.choice(["Feminino", "Masculino"])
    nome = f"{random.choice(nomes_fem if genero == 'Feminino' else nomes_masc)} {random.choice(sobrenomes)} {random.choice(sobrenomes)}"
    estado_civil = random.choice(["Casada(o)", "Solteira(o)", "Uni\u00e3o Est\u00e1vel"])
    return {
        "nome": nome,
        "data_nascimento": gerar_data_nascimento(),
        "genero": genero,
        "genero_autodeclarado": "",
        "estado_civil": estado_civil,
        "rg": f"{random.randint(10_000_000, 99_999_999)}",
        "cpf": gerar_cpf_valido(),
        "nome_mae": f"{random.choice(nomes_fem)} {random.choice(sobrenomes)}",
        "nome_pai": f"{random.choice(nomes_masc)} {random.choice(sobrenomes)}",
        "autoriza_imagem": True
    }


def gerar_endereco() -> Dict[str, str]:
    return {
        "cep": "13083-852",
        "logradouro": random.choice([
            "Rua das Acacias",
            "Rua Sao Jose",
            "Avenida Brasil",
            "Rua Projetada 5"
        ]),
        "numero": str(random.randint(10, 999)),
        "complemento": "Casa 2",
        "bairro": random.choice(["Jardim Paulista", "Centro", "Vila Nova"]),
        "cidade": "Campinas",
        "estado": "SP",
        "ponto_referencia": "Perto da escola municipal"
    }


def gerar_composicao() -> Dict[str, Any]:
    return {
        "total_residentes": 5,
        "quantidade_bebes": 0,
        "quantidade_criancas": 2,
        "quantidade_adolescentes": 1,
        "quantidade_adultos": 2,
        "quantidade_idosos": 0,
        "menores_na_escola": False,
        "motivo_ausencia": texto_aleatorio("Busca vaga em creche")
    }


def gerar_contato() -> Dict[str, str]:
    ddd = random.choice(["11", "12", "19"])
    telefone = f"({ddd}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    telefone_alt = f"({ddd}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    return {
        "telefone_principal": telefone,
        "telefone_principal_nome": "Responsavel",
        "telefone_alternativo": telefone_alt,
        "telefone_alternativo_nome": "Conjuge",
        "email": f"familia{random.randint(1000,9999)}@exemplo.com"
    }


def gerar_moradia() -> Dict[str, Any]:
    return {
        "tipo": "Alugada",
        "valor_aluguel": 650,
        "agua": True,
        "esgoto": True,
        "energia": True,
        "fogao": True,
        "geladeira": True,
        "camas": 3,
        "tvs": 1,
        "ventiladores": 2
    }


def gerar_saude() -> Dict[str, Any]:
    return {
        "tem_doenca_cronica": True,
        "descricao_doenca": texto_aleatorio("Consulta medica"),
        "usa_medicacao": True,
        "descricao_medicacao": texto_aleatorio("Remedio controlado"),
        "tem_deficiencia": True,
        "descricao_deficiencia": "Deficiencia motora leve",
        "recebe_bpc": False
    }


def gerar_emprego() -> Dict[str, Any]:
    return {
        "relacao": "Provedor n\u00e3o familiar",
        "descricao_provedor_externo": "Vizinho que auxilia",
        "situacao": "Outro",
        "descricao_situacao": "Trabalha por diarias",
        "profissao": "Auxiliar de servicos",
        "experiencia": "Mais de 5 anos em limpeza",
        "formacao": "Cursos de cuidador",
        "habilidades": "Cozinha comunitaria e costura"
    }


def gerar_renda() -> Dict[str, Any]:
    return {
        "gastos_supermercado": 650,
        "gastos_energia": 180,
        "gastos_agua": 90,
        "valor_botija": 120,
        "duracao_botija": 2,
        "gastos_transporte": 150,
        "gastos_medicamentos": 110,
        "gastos_celular": 60,
        "gastos_outros": 140,
        "renda_arrimo": 1200,
        "renda_outros": 350,
        "ajuda_terceiros": 200,
        "cadastro_unico": True,
        "recebe_beneficio": True,
        "descricao_beneficios": "Bolsa Familia e auxilio moradia",
        "valor_beneficios": 350
    }


def gerar_educacao() -> Dict[str, Any]:
    return {
        "nivel": "Ensino M\u00e9dio Completo",
        "estuda": True,
        "curso": "Curso tecnico em andamento"
    }


def gerar_demanda() -> Dict[str, str]:
    return {
        "descricao": texto_aleatorio("Necessidade de eletrodomestico"),
        "categoria": "Equipamentos para casa",
        "prioridade": "Alta"
    }


def gerar_atendimento() -> Dict[str, Any]:
    visita = random.choice([True, False])
    return {
        "percepcao": "Media",
        "duracao": "Tempor\u00e1ria",
        "motivo": texto_aleatorio("Situacao de desemprego"),
        "cesta_entregue": True,
        "data_cesta": datetime.utcnow().strftime("%d/%m/%Y"),
        "tipo_atendimento": "Visita domiciliar" if visita else "Atendimento na base",
        "data_visita": datetime.utcnow().strftime("%d/%m/%Y") if visita else "",
        "notas_visita": texto_aleatorio("Observacao da visita") if visita else ""
    }


def gerar_dataset() -> Dict[str, Any]:
    return {
        "pessoa": gerar_dados_pessoa(),
        "endereco": gerar_endereco(),
        "composicao": gerar_composicao(),
        "contato": gerar_contato(),
        "moradia": gerar_moradia(),
        "saude": gerar_saude(),
        "emprego": gerar_emprego(),
        "renda": gerar_renda(),
        "educacao": gerar_educacao(),
        "demanda": gerar_demanda(),
        "atendimento": gerar_atendimento()
    }


def _type_digits(page: Page, selector: str, digits: str) -> None:
    page.click(selector)
    page.fill(selector, "")
    page.type(selector, digits)


def _fill_masked_date(page: Page, selector: str, date_br: str) -> None:
    digits = re.sub(r"\D", "", date_br)
    _type_digits(page, selector, digits)


def _fill_currency(page: Page, selector: str, valor_reais: int) -> None:
    cents = int(valor_reais * 100)
    _type_digits(page, selector, str(cents))


def _wait_for_step(page: Page, etapa: int) -> None:
    page.wait_for_url(f"**/atendimento/etapa{etapa}", timeout=STEP_TIMEOUT)


def _click_when_enabled(page: Page, selector: str = "#btnProxima") -> None:
    """Wait for the next-step button to be enabled before clicking."""
    botao = page.locator(selector)
    expect(botao).to_be_enabled(timeout=STEP_TIMEOUT)
    botao.click()


def realizar_login(page: Page, base_url: str, usuario: str, senha: str) -> None:
    page.goto(f"{base_url}/login", wait_until="networkidle")
    page.fill("input#login", usuario)
    page.fill("input#senha", senha)
    page.click("button[type='submit']")
    page.wait_for_url("**/menu_atendimento", timeout=STEP_TIMEOUT)


def iniciar_novo_atendimento(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/menu_atendimento", wait_until="networkidle")
    page.click("#btnNovaFamilia")
    _wait_for_step(page, 1)


def preencher_etapa1(page: Page, pessoa: Dict[str, Any]) -> None:
    page.fill("#nome_responsavel", pessoa["nome"])
    _fill_masked_date(page, "#data_nascimento", pessoa["data_nascimento"])
    page.select_option("#genero", label=pessoa["genero"])
    if pessoa["genero"] == "Outro" and pessoa["genero_autodeclarado"]:
        page.fill("#genero_autodeclarado", pessoa["genero_autodeclarado"])
    page.select_option("#estado_civil", label=pessoa["estado_civil"])
    page.fill("#rg", pessoa["rg"])
    _type_digits(page, "#cpf", re.sub(r"\D", "", pessoa["cpf"]))
    page.fill("#nome_mae", pessoa["nome_mae"])
    page.fill("#nome_pai", pessoa["nome_pai"])
    if pessoa["autoriza_imagem"]:
        page.check("#autoriza_sim")
    else:
        page.check("#autoriza_nao")
    _click_when_enabled(page)
    _wait_for_step(page, 2)


def preencher_etapa2(page: Page, endereco: Dict[str, Any]) -> None:
    page.check("#preenchimento_manual")
    _type_digits(page, "#cep", re.sub(r"\D", "", endereco["cep"]))
    page.fill("#logradouro", endereco["logradouro"])
    page.fill("#numero", endereco["numero"])
    page.fill("#complemento", endereco["complemento"])
    page.fill("#bairro", endereco["bairro"])
    page.fill("#cidade", endereco["cidade"])
    page.fill("#estado", endereco["estado"])
    page.fill("#ponto_referencia", endereco["ponto_referencia"])
    _click_when_enabled(page)
    _wait_for_step(page, 3)


def preencher_etapa3(page: Page, composicao: Dict[str, Any]) -> None:
    page.fill("#total_residentes", str(composicao["total_residentes"]))
    page.fill("#quantidade_bebes", str(composicao["quantidade_bebes"]))
    page.fill("#quantidade_criancas", str(composicao["quantidade_criancas"]))
    page.fill("#quantidade_adolescentes", str(composicao["quantidade_adolescentes"]))
    page.fill("#quantidade_adultos", str(composicao["quantidade_adultos"]))
    page.fill("#quantidade_idosos", str(composicao["quantidade_idosos"]))
    page.wait_for_timeout(200)
    if composicao["quantidade_criancas"] + composicao["quantidade_adolescentes"] > 0:
        alvo = "#menores_na_escola_sim" if composicao["menores_na_escola"] else "#menores_na_escola_nao"
        page.check(alvo)
        if not composicao["menores_na_escola"]:
            page.fill("#motivo_ausencia_escola", composicao["motivo_ausencia"])
    _click_when_enabled(page)
    _wait_for_step(page, 4)


def preencher_etapa4(page: Page, contato: Dict[str, str]) -> None:
    _type_digits(page, "#telefone_principal", re.sub(r"\D", "", contato["telefone_principal"]))
    page.check("#telefone_principal_whatsapp")
    page.fill("#telefone_principal_nome_contato", contato["telefone_principal_nome"])
    _type_digits(page, "#telefone_alternativo", re.sub(r"\D", "", contato["telefone_alternativo"]))
    page.fill("#telefone_alternativo_nome_contato", contato["telefone_alternativo_nome"])
    page.fill("#email_responsavel", contato["email"])
    _click_when_enabled(page)
    _wait_for_step(page, 5)


def preencher_etapa5(page: Page, moradia: Dict[str, Any]) -> None:
    page.select_option("#tipo_moradia", label=moradia["tipo"])
    page.wait_for_timeout(200)
    if moradia["tipo"] == "Alugada":
        page.wait_for_selector("#valor_aluguel_container:not(.d-none)")
        _fill_currency(page, "#valor_aluguel", moradia["valor_aluguel"])
    page.check("#agua_encanada_sim" if moradia["agua"] else "#agua_encanada_nao")
    page.check("#rede_esgoto_sim" if moradia["esgoto"] else "#rede_esgoto_nao")
    page.check("#energia_eletrica_sim" if moradia["energia"] else "#energia_eletrica_nao")
    page.check("#tem_fogao_sim" if moradia["fogao"] else "#tem_fogao_nao")
    page.check("#tem_geladeira_sim" if moradia["geladeira"] else "#tem_geladeira_nao")
    page.fill("#num_camas", str(moradia["camas"]))
    page.fill("#num_tvs", str(moradia["tvs"]))
    page.fill("#num_ventiladores", str(moradia["ventiladores"]))
    _click_when_enabled(page)
    _wait_for_step(page, 6)


def preencher_etapa6(page: Page, saude: Dict[str, Any]) -> None:
    page.check("#tem_doenca_cronica_sim" if saude["tem_doenca_cronica"] else "#tem_doenca_cronica_nao")
    if saude["tem_doenca_cronica"]:
        page.fill("#descricao_doenca_cronica", saude["descricao_doenca"])
    page.check("#usa_medicacao_continua_sim" if saude["usa_medicacao"] else "#usa_medicacao_continua_nao")
    if saude["usa_medicacao"]:
        page.fill("#descricao_medicacao", saude["descricao_medicacao"])
    page.check("#tem_deficiencia_sim" if saude["tem_deficiencia"] else "#tem_deficiencia_nao")
    if saude["tem_deficiencia"]:
        page.fill("#descricao_deficiencia", saude["descricao_deficiencia"])
        page.check("#recebe_bpc_sim" if saude["recebe_bpc"] else "#recebe_bpc_nao")
    _click_when_enabled(page)
    _wait_for_step(page, 7)


def preencher_etapa7(page: Page, emprego: Dict[str, Any]) -> None:
    page.select_option("#relacao_provedor_familia", label=emprego["relacao"])
    if emprego["relacao"] == "Provedor n\u00e3o familiar":
        page.fill("#descricao_provedor_externo", emprego["descricao_provedor_externo"])
    page.select_option("#situacao_emprego", label=emprego["situacao"])
    if emprego["situacao"] == "Outro":
        page.fill("#descricao_situacao_emprego_outro", emprego["descricao_situacao"])
    page.fill("#profissao_provedor", emprego["profissao"])
    page.fill("#experiencia_profissional", emprego["experiencia"])
    page.fill("#formacao_profissional", emprego["formacao"])
    page.fill("#habilidades_relevantes", emprego["habilidades"])
    _click_when_enabled(page)
    _wait_for_step(page, 8)


def preencher_etapa8(page: Page, renda: Dict[str, Any]) -> None:
    _fill_currency(page, "#gastos_supermercado", renda["gastos_supermercado"])
    _fill_currency(page, "#gastos_energia_eletrica", renda["gastos_energia"])
    _fill_currency(page, "#gastos_agua", renda["gastos_agua"])
    _fill_currency(page, "#valor_botija_gas", renda["valor_botija"])
    page.fill("#duracao_botija_gas", str(renda["duracao_botija"]))
    _fill_currency(page, "#gastos_transporte", renda["gastos_transporte"])
    _fill_currency(page, "#gastos_medicamentos", renda["gastos_medicamentos"])
    _fill_currency(page, "#gastos_conta_celular", renda["gastos_celular"])
    _fill_currency(page, "#gastos_outros", renda["gastos_outros"])
    _fill_currency(page, "#renda_arrimo", renda["renda_arrimo"])
    _fill_currency(page, "#renda_outros_familiares", renda["renda_outros"])
    _fill_currency(page, "#auxilio_parentes_amigos", renda["ajuda_terceiros"])
    page.check("#cadastro_sim" if renda["cadastro_unico"] else "#cadastro_nao")
    alvo = "#beneficio_sim" if renda["recebe_beneficio"] else "#beneficio_nao"
    page.check(alvo)
    if renda["recebe_beneficio"]:
        page.wait_for_timeout(200)
        page.fill("#descricao_beneficios", renda["descricao_beneficios"])
        _fill_currency(page, "#valor_total_beneficios", renda["valor_beneficios"])
    _click_when_enabled(page)
    _wait_for_step(page, 9)


def preencher_etapa9(page: Page, educacao: Dict[str, Any]) -> None:
    page.select_option("#nivel_escolaridade", label=educacao["nivel"])
    page.check("#estuda_sim" if educacao["estuda"] else "#estuda_nao")
    if educacao["estuda"]:
        page.fill("#curso_ou_serie_atual", educacao["curso"])
    _click_when_enabled(page)
    _wait_for_step(page, 10)


def preencher_etapa10(page: Page, demanda: Dict[str, str]) -> None:
    page.click("#adicionarNecessidade")
    item = page.locator(".necessidade-item").last
    item.locator("input.descricao").fill(demanda["descricao"])
    item.locator("select.categoria").select_option(value=demanda["categoria"])
    item.locator("select.prioridade").select_option(value=demanda["prioridade"])
    _click_when_enabled(page)
    _wait_for_step(page, 11)


def preencher_etapa11(page: Page, atendimento: Dict[str, Any]) -> None:
    # Tipo de atendimento
    if atendimento["tipo_atendimento"] == "Visita domiciliar":
        page.check("#tipo_visita")
        page.wait_for_function("document.getElementById('dataVisitaContainer').style.display !== 'none'")
        _fill_masked_date(page, "#data_visita", atendimento["data_visita"])
        if atendimento.get("notas_visita"):
            page.fill("#notas_visita", atendimento["notas_visita"])
    else:
        page.check("#tipo_base")

    page.select_option("#percepcao_necessidade", value=atendimento["percepcao"])
    alvo = "#duracao_temporaria" if atendimento["duracao"] == "Tempor\u00e1ria" else "#duracao_permanente"
    page.check(alvo)
    page.fill("#motivo_duracao", atendimento["motivo"])
    if atendimento["cesta_entregue"]:
        page.check("#cesta_entregue")
        page.wait_for_function("document.getElementById('dataEntregaCestaContainer').style.display !== 'none'")
        _fill_masked_date(page, "#data_entrega_cesta", atendimento["data_cesta"])
    page.click("#btnFinalizar")
    page.wait_for_url("**/menu_atendimento", timeout=STEP_TIMEOUT)


def executar_fluxo(page: Page, base_url: str, usuario: str, senha: str, dataset: Dict[str, Any]) -> Dict[str, Any]:
    realizar_login(page, base_url, usuario, senha)
    iniciar_novo_atendimento(page, base_url)
    preencher_etapa1(page, dataset["pessoa"])
    preencher_etapa2(page, dataset["endereco"])
    preencher_etapa3(page, dataset["composicao"])
    preencher_etapa4(page, dataset["contato"])
    preencher_etapa5(page, dataset["moradia"])
    preencher_etapa6(page, dataset["saude"])
    preencher_etapa7(page, dataset["emprego"])
    preencher_etapa8(page, dataset["renda"])
    preencher_etapa9(page, dataset["educacao"])
    preencher_etapa10(page, dataset["demanda"])
    preencher_etapa11(page, dataset["atendimento"])
    page.wait_for_timeout(1000)
    familia_id_raw = page.evaluate("sessionStorage.getItem('familia_id')")
    familia_id = int(familia_id_raw) if familia_id_raw and familia_id_raw.isdigit() else None
    assert familia_id is not None, "familia_id n\u00e3o foi definido na sessionStorage."
    assert "Menu de Atendimento" in page.inner_text("body"), "Tela final n\u00e3o apresentou o menu esperado."
    return {
        "familia_id": familia_id,
        "cpf": dataset["pessoa"]["cpf"],
        "nome": dataset["pessoa"]["nome"]
    }


def buscar_familia_por_cpf(base_url: str, cpf: str) -> Optional[Dict[str, Any]]:
    try:
        resposta = requests.get(
            f"{base_url}/familias/busca",
            params={"q": cpf},
            timeout=10
        )
        resposta.raise_for_status()
    except requests.RequestException:
        return None
    for familia in resposta.json():
        if familia.get("cpf") == cpf:
            return familia
    return None


def aguardar_familia_no_backend(base_url: str, cpf: str) -> Optional[Dict[str, Any]]:
    deadline = time.time() + API_WAIT_SECONDS
    while time.time() < deadline:
        encontrado = buscar_familia_por_cpf(base_url, cpf)
        if encontrado:
            return encontrado
        time.sleep(2)
    return None


@pytest.mark.parametrize("execucao", range(RUN_COUNT))
def test_fluxo_atendimento_end_to_end(page: Page, base_url: str, admin_login: str, senha_admin: str, execucao: int) -> None:
    dataset = gerar_dataset()
    resultado = executar_fluxo(page, base_url, admin_login, senha_admin, dataset)
    familia = aguardar_familia_no_backend(base_url, resultado["cpf"])
    assert familia is not None, f"N\u00e3o encontrei a fam\u00edlia com CPF {resultado['cpf']} pelo endpoint de busca."
    assert int(familia["familia_id"]) == resultado["familia_id"]
    assert familia["nome_responsavel"].split()[0] in resultado["nome"]
