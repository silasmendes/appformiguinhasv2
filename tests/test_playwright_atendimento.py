import random
import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright


def texto_aleatorio(prefix="Descricao"):
    return f"{prefix} {random.randint(1000, 9999)}"


def gerar_cpf_valido():
    cpf = [random.randint(0, 9) for _ in range(9)]
    soma = sum((cpf[i] * (10 - i)) for i in range(9))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    soma = sum((cpf[i] * (11 - i)) for i in range(10))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    return f"{''.join(map(str, cpf[:3]))}.{''.join(map(str, cpf[3:6]))}.{''.join(map(str, cpf[6:9]))}-{''.join(map(str, cpf[9:]))}"


def gerar_dados_pessoa():
    """Gera dados aleatórios realistas para uma pessoa"""
    nomes_masculinos = [
        "João", "José", "Antonio", "Francisco", "Carlos", "Paulo", "Pedro", "Lucas", "Luiz", "Marcos",
        "Luis", "Gabriel", "Rafael", "Daniel", "Marcelo", "Bruno", "Eduardo", "Felipe", "Raimundo", "Rodrigo"
    ]
    
    nomes_femininos = [
        "Maria", "Ana", "Francisca", "Antonia", "Adriana", "Juliana", "Marcia", "Fernanda", "Patricia", "Aline",
        "Sandra", "Camila", "Amanda", "Bruna", "Jessica", "Leticia", "Julia", "Luciana", "Vanessa", "Mariana"
    ]
    
    sobrenomes = [
        "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes",
        "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa"
    ]
    
    genero = random.choice(["Masculino", "Feminino", "Outro"])
    if genero == "Masculino":
        nome = random.choice(nomes_masculinos)
        genero_autodeclarado = ""
    elif genero == "Feminino":
        nome = random.choice(nomes_femininos)
        genero_autodeclarado = ""
    else:
        nome = random.choice(nomes_femininos + nomes_masculinos)
        genero_autodeclarado = random.choice([
            "Não binárie",
            "Transgênero",
            "Prefere não declarar"
        ])
    
    sobrenome1 = random.choice(sobrenomes)
    sobrenome2 = random.choice(sobrenomes)
    nome_completo = f"{nome} {sobrenome1} {sobrenome2}"
    
    # Data de nascimento entre 18 e 65 anos
    hoje = datetime.now()
    idade = random.randint(18, 65)
    data_nascimento = hoje - timedelta(days=idade * 365 + random.randint(0, 365))
    data_nascimento_str = data_nascimento.strftime("%d/%m/%Y")
    
    estado_civil = random.choice(["Solteira(o)", "Casada(o)", "União Estável", "Divorciada(o)", "Viúva(o)"])
    
    return {
        "nome": nome_completo,
        "data_nascimento": data_nascimento_str,
        "genero": genero,
        "genero_autodeclarado": genero_autodeclarado,
        "estado_civil": estado_civil
    }


def gerar_endereco():
    """Gera dados de endereço aleatórios realistas"""
    logradouros = [
        "Rua das Flores", "Avenida Brasil", "Rua Santos Dumont", "Rua São José", "Avenida Paulista",
        "Rua do Comércio", "Rua Santa Rita", "Avenida Central", "Rua Nova", "Rua da Esperança",
        "Rua São João", "Avenida das Nações", "Rua do Sol", "Rua da Paz", "Rua Benedito Silva"
    ]
    
    bairros = [
        "Centro", "Vila Nova", "Jardim América", "São José", "Santa Rita", "Vila Real", "Parque Industrial",
        "Cidade Nova", "Alto da Serra", "Vila Esperança", "Jardim das Flores", "Santa Maria"
    ]
    
    cidades_sp = [
        "São Paulo", "Campinas", "São Bernardo do Campo", "Santo André", "Osasco", "Sorocaba",
        "Ribeirão Preto", "Santos", "Mauá", "São José dos Campos", "Diadema", "Carapicuíba"
    ]
    
    return {
        "cep": f"{random.randint(10000, 99999):05d}-{random.randint(0, 999):03d}",
        "logradouro": random.choice(logradouros),
        "numero": str(random.randint(1, 9999)),
        "complemento": random.choice(["Casa", "Apartamento", "Fundos", "Casa A", "Casa B", ""]),
        "bairro": random.choice(bairros),
        "cidade": random.choice(cidades_sp),
        "estado": "SP",
        "ponto_referencia": random.choice([
            "Próximo ao mercado", "Em frente à escola", "Ao lado da farmácia", 
            "Próximo à igreja", "Perto do posto de saúde", "Próximo ao ponto de ônibus"
        ])
    }


def gerar_composicao_familiar():
    """Gera dados de composição familiar aleatórios"""
    total_residentes = random.randint(2, 8)
    
    # Distribuir os residentes por faixa etária
    bebes = random.randint(0, min(2, total_residentes - 1))
    criancas = random.randint(0, min(3, total_residentes - bebes - 1))
    adolescentes = random.randint(0, min(2, total_residentes - bebes - criancas - 1))
    idosos = random.randint(0, min(2, total_residentes - bebes - criancas - adolescentes - 1))
    adultos = total_residentes - bebes - criancas - adolescentes - idosos
    
    if adultos < 1:  # Garantir pelo menos 1 adulto
        adultos = 1
        total_residentes = bebes + criancas + adolescentes + adultos + idosos
    
    return {
        "total_residentes": str(total_residentes),
        "quantidade_bebes": str(bebes),
        "quantidade_criancas": str(criancas),
        "quantidade_adolescentes": str(adolescentes),
        "quantidade_adultos": str(adultos),
        "quantidade_idosos": str(idosos),
        "menores_na_escola": random.choice(["sim", "nao"]) if (criancas + adolescentes) > 0 else "nao"
    }


def gerar_contato():
    """Gera dados de contato aleatórios"""
    ddd = random.choice(["11", "12", "13", "14", "15", "16", "17", "18", "19"])
    
    telefone_principal = f"({ddd}) 9{random.randint(1000, 9999):04d}-{random.randint(0, 9999):04d}"
    telefone_alternativo = f"({ddd}) 9{random.randint(1000, 9999):04d}-{random.randint(0, 9999):04d}"
    
    nomes_contato = ["João", "Maria", "José", "Ana", "Carlos", "Patricia", "Pedro", "Sandra"]
    
    email_providers = ["gmail.com", "hotmail.com", "yahoo.com.br", "outlook.com"]
    email = f"familia{random.randint(100, 999)}@{random.choice(email_providers)}"
    
    return {
        "telefone_principal": telefone_principal,
        "telefone_principal_nome": random.choice(nomes_contato),
        "telefone_alternativo": telefone_alternativo,
        "telefone_alternativo_nome": random.choice(nomes_contato),
        "email": email
    }


def gerar_condicoes_moradia():
    """Gera dados de condições de moradia aleatórios"""
    tipo_moradia = random.choice([
        "Própria",
        "Alugada",
        "Cedida",
        "Financiada",
        "Ocupação",
        "Situação de rua",
    ])
    valor_aluguel = str(random.randint(300, 1200)) if tipo_moradia == "Alugada" else "0"
    
    return {
        "tipo_moradia": tipo_moradia,
        "valor_aluguel": valor_aluguel,
        "agua_encanada": random.choice(["sim", "nao"]),
        "rede_esgoto": random.choice(["sim", "nao"]),
        "energia_eletrica": "sim",  # Assumindo que sempre tem energia
        "tem_fogao": random.choice(["sim", "nao"]),
        "tem_geladeira": random.choice(["sim", "nao"]),
        "num_camas": str(random.randint(1, 6)),
        "num_tvs": str(random.randint(0, 3)),
        "num_ventiladores": str(random.randint(0, 5))
    }


def gerar_renda_gastos():
    """Gera dados de renda e gastos aleatórios realistas para famílias carentes no Brasil"""
    # Renda baseada no salário mínimo brasileiro (R$ 1.412 em 2024)
    renda_arrimo = random.randint(800, 2500)  # De pouco mais que meio salário mínimo até quase 2 salários
    renda_outros = random.randint(0, 800)     # Renda complementar de outros familiares
    auxilio = random.randint(0, 600)          # Auxílios diversos (Bolsa Família, etc.)
    
    # Gastos realistas para famílias carentes brasileiras
    return {
        "gastos_supermercado": str(random.randint(400, 800)),        # R$ 400-800 por mês para alimentação
        "gastos_energia_eletrica": str(random.randint(80, 250)),     # R$ 80-250 conta de luz
        "gastos_agua": str(random.randint(40, 120)),                 # R$ 40-120 conta de água
        "valor_botija_gas": str(random.randint(90, 130)),            # R$ 90-130 botijão de gás
        "duracao_botija_gas": str(random.randint(20, 45)),           # 20-45 dias duração do gás
        "gastos_transporte": str(random.randint(100, 350)),          # R$ 100-350 transporte público
        "gastos_medicamentos": str(random.randint(50, 300)),         # R$ 50-300 medicamentos
        "gastos_conta_celular": str(random.randint(30, 80)),         # R$ 30-80 conta de celular
        "gastos_outros": str(random.randint(80, 250)),               # R$ 80-250 outros gastos
        "renda_arrimo": str(renda_arrimo),
        "renda_outros_familiares": str(renda_outros),
        "auxilio_parentes_amigos": str(auxilio)
    }


def test_cadastro_nova_familia():
    # Gerar dados aleatórios para o teste
    dados_pessoa = gerar_dados_pessoa()
    endereco = gerar_endereco()
    composicao = gerar_composicao_familiar()
    contato = gerar_contato()
    moradia = gerar_condicoes_moradia()
    renda_gastos = gerar_renda_gastos()
    
    print(f"Testando com dados da família: {dados_pessoa['nome']}")
    
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
        page.fill("#nome_responsavel", dados_pessoa["nome"])
        
        # Preencher data de nascimento contornando a máscara dd/mm/aaaa
        page.click("#data_nascimento")
        page.keyboard.press("Control+a")  # Selecionar tudo
        page.keyboard.press("Delete")     # Deletar conteúdo
        
        # Digitar apenas os números da data (sem as barras)
        data_apenas_numeros = dados_pessoa["data_nascimento"].replace("/", "")
        for char in data_apenas_numeros:
            page.keyboard.press(char)
            page.wait_for_timeout(50)  # Pequena pausa entre cada dígito
        
        page.select_option("#genero", label=dados_pessoa["genero"])
        if dados_pessoa["genero"] == "Outro":
            page.fill("#genero_autodeclarado", dados_pessoa["genero_autodeclarado"])
        page.select_option("#estado_civil", label=dados_pessoa["estado_civil"])
        page.fill("#rg", f"{random.randint(100000000, 999999999)}")
        page.fill("#cpf", gerar_cpf_valido())
        page.check("#autoriza_sim")
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 2 - endereço
        page.check("#preenchimento_manual")
        page.fill("#cep", endereco["cep"])
        page.fill("#logradouro", endereco["logradouro"])
        page.fill("#numero", endereco["numero"])
        page.fill("#complemento", endereco["complemento"])
        page.fill("#bairro", endereco["bairro"])
        page.fill("#cidade", endereco["cidade"])
        page.fill("#estado", endereco["estado"])
        page.fill("#ponto_referencia", endereco["ponto_referencia"])
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 3 - composição familiar
        page.fill("#total_residentes", composicao["total_residentes"])
        page.fill("#quantidade_bebes", composicao["quantidade_bebes"])
        page.fill("#quantidade_criancas", composicao["quantidade_criancas"])
        page.fill("#quantidade_adolescentes", composicao["quantidade_adolescentes"])
        page.fill("#quantidade_adultos", composicao["quantidade_adultos"])
        page.fill("#quantidade_idosos", composicao["quantidade_idosos"])
        
        # Selecionar se menores estão na escola baseado na composição
        if composicao["menores_na_escola"] == "sim":
            page.check("#menores_na_escola_sim")
        else:
            page.check("#menores_na_escola_nao")
            page.fill("#motivo_ausencia_escola", texto_aleatorio("Motivo"))
            
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 4 - contato
        page.fill("#telefone_principal", contato["telefone_principal"])
        page.check("#telefone_principal_whatsapp")
        page.fill("#telefone_principal_nome_contato", contato["telefone_principal_nome"])
        page.fill("#telefone_alternativo", contato["telefone_alternativo"])
        page.fill("#telefone_alternativo_nome_contato", contato["telefone_alternativo_nome"])
        page.fill("#email_responsavel", contato["email"])
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 5 - condições de moradia
        page.select_option("#tipo_moradia", label=moradia["tipo_moradia"])
        if moradia["tipo_moradia"] == "Alugada":
            page.fill("#valor_aluguel", moradia["valor_aluguel"])
        
        # Marcar checkboxes baseado nos dados gerados
        if moradia["agua_encanada"] == "sim":
            page.check("#agua_encanada_sim")
        else:
            page.check("#agua_encanada_nao")
            
        if moradia["rede_esgoto"] == "sim":
            page.check("#rede_esgoto_sim")
        else:
            page.check("#rede_esgoto_nao")
            
        if moradia["energia_eletrica"] == "sim":
            page.check("#energia_eletrica_sim")
        else:
            page.check("#energia_eletrica_nao")
            
        if moradia["tem_fogao"] == "sim":
            page.check("#tem_fogao_sim")
        else:
            page.check("#tem_fogao_nao")
            
        if moradia["tem_geladeira"] == "sim":
            page.check("#tem_geladeira_sim")
        else:
            page.check("#tem_geladeira_nao")
            
        page.fill("#num_camas", moradia["num_camas"])
        page.fill("#num_tvs", moradia["num_tvs"])
        page.fill("#num_ventiladores", moradia["num_ventiladores"])
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 6 - saúde familiar
        doenca_cronica = random.choice(["sim", "nao"])
        medicacao = random.choice(["sim", "nao"])
        deficiencia = random.choice(["sim", "nao"])
        
        if doenca_cronica == "sim":
            page.check("#tem_doenca_cronica_sim")
            page.fill("#descricao_doenca_cronica", texto_aleatorio("Doenca"))
        else:
            page.check("#tem_doenca_cronica_nao")
            
        if medicacao == "sim":
            page.check("#usa_medicacao_continua_sim")
            page.fill("#descricao_medicacao", texto_aleatorio("Medicacao"))
        else:
            page.check("#usa_medicacao_continua_nao")
            
        if deficiencia == "sim":
            page.check("#tem_deficiencia_sim")
            page.fill("#descricao_deficiencia", texto_aleatorio("Deficiencia"))
            if random.choice(["sim", "nao"]) == "sim":
                page.check("#recebe_bpc_sim")
            else:
                page.check("#recebe_bpc_nao")
        else:
            page.check("#tem_deficiencia_nao")
            
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 7 - emprego
        relacao_provedor = random.choice([
            "Eu mesma(o)",
            "Cônjuge/Companheira(o)",
            "Filho(a)",
            "Outro familiar",
            "Provedor não familiar",
        ])
        situacao_emprego = random.choice([
            "Empregado formal",
            "Empregado informal"
        ])
        
        profissoes = [
            "Auxiliar de limpeza", "Vendedor", "Cozinheira", "Pedreiro", "Motorista",
            "Doméstica", "Segurança", "Operador", "Auxiliar", "Diarista"
        ]
        
        page.select_option("#relacao_provedor_familia", label=relacao_provedor)
        if relacao_provedor == "Provedor não familiar":
            page.fill("#descricao_provedor_externo", texto_aleatorio("Provedor"))

        page.select_option("#situacao_emprego", label=situacao_emprego)
        if situacao_emprego == "Outro":
            page.fill("#descricao_situacao_emprego_outro", texto_aleatorio("Emprego"))
        page.fill("#profissao_provedor", random.choice(profissoes))
        page.fill("#experiencia_profissional", random.choice([
            "Mais de 5 anos", "2 a 5 anos", "1 a 2 anos", "Menos de 1 ano", "Nenhuma"
        ]))
        page.fill("#formacao_profissional", random.choice([
            "Ensino Fundamental Incompleto", "Ensino Fundamental Completo",
            "Ensino Médio Incompleto", "Ensino Médio Completo", "Superior Incompleto"
        ]))
        page.fill("#habilidades_relevantes", random.choice([
            "Organização", "Comunicação", "Trabalho em equipe", "Pontualidade",
            "Responsabilidade", "Criatividade", "Liderança"
        ]))
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 8 - renda e gastos
        page.fill("#gastos_supermercado", renda_gastos["gastos_supermercado"])
        page.fill("#gastos_energia_eletrica", renda_gastos["gastos_energia_eletrica"])
        page.fill("#gastos_agua", renda_gastos["gastos_agua"])
        page.fill("#valor_botija_gas", renda_gastos["valor_botija_gas"])
        page.fill("#duracao_botija_gas", renda_gastos["duracao_botija_gas"])
        page.fill("#gastos_transporte", renda_gastos["gastos_transporte"])
        page.fill("#gastos_medicamentos", renda_gastos["gastos_medicamentos"])
        page.fill("#gastos_conta_celular", renda_gastos["gastos_conta_celular"])
        page.fill("#gastos_outros", renda_gastos["gastos_outros"])
        page.fill("#renda_arrimo", renda_gastos["renda_arrimo"])
        page.fill("#renda_outros_familiares", renda_gastos["renda_outros_familiares"])
        page.fill("#auxilio_parentes_amigos", renda_gastos["auxilio_parentes_amigos"])
        
        # Cadastros e benefícios aleatórios
        cadastro_governo = random.choice(["sim", "nao"])
        beneficio_governo = random.choice(["sim", "nao"])
        
        if cadastro_governo == "sim":
            page.check("#cadastro_sim")
        else:
            page.check("#cadastro_nao")
            
        if beneficio_governo == "sim":
            page.check("#beneficio_sim")
            page.fill("#descricao_beneficios", texto_aleatorio("Beneficio"))
            page.fill("#valor_total_beneficios", str(random.randint(50, 400)))
        else:
            page.check("#beneficio_nao")
            
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 9 - escolaridade
        nivel_escolaridade = random.choice([
            "Analfabeto", "Ensino Fundamental Incompleto", "Ensino Fundamental Completo"
        ])
        estuda_atualmente = random.choice(["sim", "nao"])
        
        page.select_option("#nivel_escolaridade", label=nivel_escolaridade)
        
        if estuda_atualmente == "sim":
            page.check("#estuda_sim")
            page.fill("#curso_ou_serie_atual", texto_aleatorio("Curso"))
        else:
            page.check("#estuda_nao")
            
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 10 - outras necessidades (nenhuma adicionada)
        page.click("#btnProxima")
        page.wait_for_load_state("networkidle")

        # Etapa 11 - finalização
        percepcao = random.choice(["Baixa", "Média", "Alta"])
        page.select_option("#percepcao_necessidade", label=percepcao)
        page.check("#duracao_temporaria")
        page.fill("#motivo_duracao", texto_aleatorio("Motivo duracao"))
        page.check("#cesta_entregue")
        page.click("#btnFinalizar")
        page.wait_for_load_state("networkidle")

        browser.close()
        
        print(f"Cadastro concluído para: {dados_pessoa['nome']}")
        print(f"Endereço: {endereco['logradouro']}, {endereco['numero']} - {endereco['bairro']}")
        print(f"Família com {composicao['total_residentes']} pessoas")
        print(f"Renda principal: R$ {renda_gastos['renda_arrimo']}")

        assert True


def test_multiplos_cadastros():
    """Executa múltiplos testes com dados diferentes"""
    num_testes = 57  # Pode ajustar o número de testes
    
    for i in range(num_testes):
        print(f"\n--- Executando teste {i+1}/{num_testes} ---")
        try:
            test_cadastro_nova_familia()
            print(f"✅ Teste {i+1} concluído com sucesso!")
        except Exception as e:
            print(f"❌ Erro no teste {i+1}: {str(e)}")
            raise e


if __name__ == "__main__":
    print("Iniciando teste de cadastro de nova família com dados randômicos...")
    print("=" * 60)
    
    # Para executar apenas um teste
    # test_cadastro_nova_familia()
    
    # Para executar múltiplos testes (descomente a linha abaixo)
    test_multiplos_cadastros()
    
    print("\n" + "=" * 60)
    print("Todos os testes concluídos com sucesso!")
