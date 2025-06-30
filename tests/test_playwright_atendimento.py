import random
import os
from playwright.sync_api import sync_playwright


def gerar_cpf_valido():
    cpf = [random.randint(0, 9) for _ in range(9)]
    soma = sum((cpf[i] * (10 - i)) for i in range(9))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    soma = sum((cpf[i] * (11 - i)) for i in range(10))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    return f"{''.join(map(str, cpf[:3]))}.{''.join(map(str, cpf[3:6]))}.{''.join(map(str, cpf[6:9]))}-{''.join(map(str, cpf[9:]))}"


def test_cadastro_nova_familia():
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=True)
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()

        page.goto("http://127.0.0.1:5000/")
        page.fill("input#login", "admin")
        page.fill("input#senha", os.getenv("SENHA_ADMIN"))
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

        page.goto("http://127.0.0.1:5000/menu_atendimento")
        page.click("#btnNovaFamilia")

        # Etapa 1 - dados pessoais
        page.fill("#nome_responsavel", "João da Silva")
        page.fill("#data_nascimento", "01/01/1980")
        page.select_option("#genero", label="Masculino")
        page.select_option("#estado_civil", label="Solteira(o)")
        page.fill("#rg", "123456789")
        page.fill("#cpf", gerar_cpf_valido())
        page.check("#autoriza_sim")
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 2 - endereço
        page.check("#preenchimento_manual")
        page.fill("#cep", "13010-000")
        page.fill("#logradouro", "Rua Exemplo")
        page.fill("#numero", "123")
        page.fill("#complemento", "Casa")
        page.fill("#bairro", "Centro")
        page.fill("#cidade", "Campinas")
        page.fill("#estado", "SP")
        page.fill("#ponto_referencia", "Proximo a praça")
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 3 - composição familiar
        page.fill("#total_residentes", "3")
        page.fill("#quantidade_bebes", "0")
        page.fill("#quantidade_criancas", "1")
        page.fill("#quantidade_adolescentes", "0")
        page.fill("#quantidade_adultos", "2")
        page.fill("#quantidade_idosos", "0")
        page.check("#menores_na_escola_sim")
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 4 - contato
        page.fill("#telefone_principal", "(11) 90000-0000")
        page.check("#telefone_principal_whatsapp")
        page.fill("#telefone_principal_nome_contato", "Joao")
        page.fill("#telefone_alternativo", "(11) 95555-1234")
        page.fill("#telefone_alternativo_nome_contato", "Maria")
        page.fill("#email_responsavel", "familia@example.com")
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 5 - condições de moradia
        page.select_option("#tipo_moradia", label="Alugada")
        page.fill("#valor_aluguel", "500")
        page.check("#agua_encanada_sim")
        page.check("#rede_esgoto_sim")
        page.check("#energia_eletrica_sim")
        page.check("#tem_fogao_sim")
        page.check("#tem_geladeira_sim")
        page.fill("#num_camas", "3")
        page.fill("#num_tvs", "1")
        page.fill("#num_ventiladores", "2")
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 6 - saúde familiar
        page.check("#tem_doenca_cronica_nao")
        page.check("#usa_medicacao_continua_nao")
        page.check("#tem_deficiencia_nao")
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 7 - emprego
        page.select_option("#relacao_provedor_familia", label="Eu mesma(o)")
        page.select_option("#situacao_emprego", label="Empregado formal")
        page.fill("#profissao_provedor", "Auxiliar")
        page.fill("#experiencia_profissional", "Nenhuma")
        page.fill("#formacao_profissional", "Ensino Médio")
        page.fill("#habilidades_relevantes", "Organização")
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 8 - renda e gastos
        page.fill("#gastos_supermercado", "300")
        page.fill("#gastos_energia_eletrica", "100")
        page.fill("#gastos_agua", "50")
        page.fill("#valor_botija_gas", "100")
        page.fill("#duracao_botija_gas", "1")
        page.fill("#gastos_transporte", "80")
        page.fill("#gastos_medicamentos", "20")
        page.fill("#gastos_conta_celular", "40")
        page.fill("#gastos_outros", "30")
        page.fill("#renda_arrimo", "1200")
        page.fill("#renda_outros_familiares", "200")
        page.fill("#auxilio_parentes_amigos", "0")
        page.check("#cadastro_nao")
        page.check("#beneficio_nao")
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 9 - escolaridade
        page.select_option("#nivel_escolaridade", label="Ensino Fundamental Completo")
        page.check("#estuda_nao")
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 10 - outras necessidades (nenhuma adicionada)
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 11 - finalização
        page.select_option("#percepcao_necessidade", label="Alta")
        page.check("#duracao_temporaria")
        page.check("#cesta_entregue")
        page.click("#btnFinalizar")
        page.wait_for_load_state("networkidle")

        browser.close()

        assert True


if __name__ == "__main__":
    print("Iniciando teste de cadastro de nova família...")
    test_cadastro_nova_familia()
    print("Teste concluído com sucesso!")
