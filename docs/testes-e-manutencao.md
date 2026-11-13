# Testes após alterações no sistema

Uma alteração pode funcionar na tela modificada e causar problemas em outro lugar: mudar um campo do cadastro, por exemplo, pode afetar a gravação no banco, o carregamento do atendimento e uma exportação Excel. Isso vale para alterações feitas manualmente, com Codex, com Claude Code ou com outra ferramenta.

Execute a suíte de regressão antes de aceitar mudanças substanciais e antes de publicar uma versão. Considere substanciais as mudanças em modelos ou estrutura do banco, rotas, autenticação, cadastro, atendimento, demandas, relatórios, configuração, dependências e inicialização. Execute também os testes específicos da funcionalidade alterada.

## Validação do servidor e teste completo no navegador

Há duas formas complementares de verificar a aplicação: testes do servidor com bancos temporários e o fluxo completo via Playwright. O teste de cadastro completo por API é um terceiro arquivo, antigo, e não deve ser confundido com o Playwright.

| Arquivo | O que verifica | Limites e segurança |
| --- | --- | --- |
| `tests/test_sqlite_local.py` | Login, senha incorreta, logout, acesso às páginas protegidas selecionadas; criação, leitura, atualização e exclusão de família; persistência em uma nova instância da aplicação; valores e vínculo das oito seções complementares; carregamento de campos no formulário; atendimento com identificação do usuário autenticado; demanda com histórico inicial; rejeição dos dados inválidos selecionados; filtros dos relatórios; registros e quantidade de linhas dos sete arquivos Excel; separação do pré-cadastro; preservação da senha do administrador; campos sem o texto indevido `None`. | Usa uma aplicação e dois bancos SQLite temporários por cenário, bloqueia conexões de rede e substitui a geração de resumos. Não testa navegador, JavaScript, cliques ou todos os campos e regras de negócio. |
| `tests/test_sqlite_concurrency.py` | WAL e tempo de espera em novas conexões, dez escritores concorrentes e leitura durante uma escrita, nos dois bancos. | Usa arquivos temporários. Não simula edições simultâneas do mesmo cadastro por pessoas nem impede sobrescrita de dados. |
| `tests/test_production_setup.py` | Segredos e senhas iniciais de produção, cookies seguros, inicialização repetida, persistência do login e inclusão explícita de dados de demonstração. | Usa bancos temporários. Não comprova proxy, HTTPS, backup ou deploy real. |
| `tests/test_validation_command.py` | Isolamento do ambiente do subprocesso, seleção dos testes, limpeza temporária, preservação do ambiente do usuário, propagação de falhas ou ausência de testes e execução com a pasta temporária padrão do pytest indisponível. | Verifica o comando único, sem testar a interface. |
| `tests/test_playwright_atendimento.py` | Login e preenchimento das onze etapas no navegador, botões, campos condicionais, máscaras e chamadas reais ao servidor; retorno ao menu e busca da família por CPF no backend. | Grava dados fictícios no servidor escolhido. Requer servidor, senha e Chromium. Não compara todos os campos persistidos. Mantido sem alterações e fora do CI automático. |
| `tests/test_integracao_cadastro_completo.py` | Envia os dados pessoais e as oito seções complementares pelas APIs, consulta os registros criados, cria duas demandas para a mesma família, registra uma etapa, atualiza explicitamente o status da demanda e rejeita uma categoria inválida. | Na versão atual, usa a configuração normal da aplicação, sem criar bancos temporários nem preparar tabelas e categorias. Os cenários compartilham IDs globais e dependem da ordem. Não prepara login, embora a criação de demandas e etapas exija autenticação. A maioria das verificações confere apenas códigos HTTP. |

## Como executar a validação automática do servidor

No PowerShell, na raiz do repositório, com as dependências instaladas conforme o README:

```powershell
.venv\Scripts\python.exe scripts/validate.py
```

Em Linux/macOS, ative o ambiente virtual e use `python scripts/validate.py`. Não é necessário iniciar o Flask, preparar dados de demonstração ou fornecer credenciais de OpenAI/SendGrid.

O comando executa apenas os quatro arquivos de servidor revisados na tabela. Prepara variáveis de ambiente temporárias antes de importar a aplicação, desativa credenciais externas no subprocesso e não altera o `.env` ou o ambiente do terminal. As fixtures também preparam seus próprios bancos. Plugins externos do pytest e argumentos automáticos locais são desativados para manter a seleção explícita.

O pytest recebe uma pasta temporária exclusiva por execução, sem usar a pasta compartilhada `pytest-of-<usuário>`. Isso evita erros de acesso a essa pasta no Windows e permite execuções independentes. O servidor pode continuar online: a validação não se conecta a ele nem usa seus bancos.

O resultado esperado é uma linha final com `passed`, sem `failed` nem `ERROR`. A quantidade pode aumentar conforme novos cenários forem adicionados. Avisos (`warnings`) não são falhas, mas devem ser avaliados quando relacionados à mudança ou a uma atualização de dependências.

Para ver mais detalhes de uma falha:

```powershell
.venv\Scripts\python.exe scripts/validate.py --verbose
```

## Quando rodar o Playwright

Após mudanças substanciais que afetem cadastro, atendimento, JavaScript, templates ou integração entre etapas, execute a validação do servidor e o Playwright separadamente. Antes de publicar mudanças amplas, confira ambos. Para alterações apenas em documentação, revise os documentos e os links; não é necessário iniciar o navegador. Informe qualquer validação não executada.

O Playwright permanece exatamente como está. Ele não cria uma instalação isolada: usa o servidor configurado e pode apontar para uma URL remota. Por isso, não é executado pelo comando único nem pelo CI. Use uma instalação descartável local e defina a URL explicitamente.

### Preparar um servidor descartável

No primeiro PowerShell, na raiz do repositório, execute os comandos abaixo. As variáveis valem para esse terminal; feche-o depois para voltar ao seu ambiente normal. A senha abaixo é fictícia e exclusiva deste teste.

```powershell
$e2eRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("formiguinhas-e2e-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $e2eRoot | Out-Null
$e2eSqliteRoot = $e2eRoot.Replace('\', '/')
$env:DATABASE_URL = "sqlite:///$e2eSqliteRoot/main.db"
$env:PRE_CADASTRO_DATABASE_URL = "sqlite:///$e2eSqliteRoot/pre.db"
$env:SESSION_FILE_DIR = Join-Path $e2eRoot 'sessions'
$env:APP_ENV = 'development'
$env:FLASK_ENV = 'development'
$env:SECRET_KEY = 'e2e-only-secret-never-use-in-production'
$env:SENHA_ADMIN = 'SenhaApenasParaTeste123!'
$env:OPENAI_API_KEY = ''
$env:SENDGRID_API_KEY = ''
.venv\Scripts\python.exe manage.py
.venv\Scripts\python.exe -m flask --app main run --port 5001
```

Confira se a inicialização terminou com sucesso antes de iniciar o Flask. Acesse `http://127.0.0.1:5001/login` para confirmar o servidor. Não reutilize uma porta que já esteja atendendo uma instalação com dados reais. Esses arquivos ficam no diretório temporário criado, não no banco normal do projeto.

### Executar o navegador

No segundo PowerShell, na raiz:

```powershell
.venv\Scripts\python.exe -m playwright install chromium
$env:ATENDIMENTO_BASE_URL = 'http://127.0.0.1:5001'
$env:USUARIO_ADMIN = 'admin'
$env:SENHA_ADMIN = 'SenhaApenasParaTeste123!'
$env:ATENDIMENTO_RUNS = '1'
.venv\Scripts\python.exe -m pytest tests/test_playwright_atendimento.py -q
```

A instalação do Chromium é necessária apenas quando ele não estiver disponível para a versão instalada do Playwright. Para observar o navegador, defina `$env:PLAYWRIGHT_HEADLESS = '0'` antes de executar o teste. Um resultado `skipped` por ausência de senha não significa que o fluxo foi validado.

Depois, interrompa o Flask com Ctrl+C e feche os dois terminais. O teste cria dados fictícios na instalação descartável; não os importe para a instalação real. Não execute esse fluxo contra produção.

## Teste antigo de cadastro por API

Não execute o teste antigo de cadastro completo contra os bancos de desenvolvimento ou de produção: ele grava registros e não oferece o mesmo isolamento. Alterar apenas o `.env` não resolve suas dependências de ordem, dados iniciais e autenticação.

Antes de incluir esse arquivo na validação obrigatória, é necessário:

1. Criar bancos e sessões temporários, com limpeza dos recursos ao final.
2. Preparar tabelas, categorias e um usuário de teste autenticado.
3. Remover a dependência de IDs globais e da ordem de execução.
4. Confirmar que cada cenário passa isoladamente e que a execução conjunta não usa os bancos locais.

Depois desses ajustes, revise a inclusão desse arquivo em `scripts/validate.py`. Até lá, ele fica fora da seleção automática. Não execute indiscriminadamente toda a pasta `tests`, pois outros testes antigos podem usar a configuração normal da aplicação.

## O que fazer quando um teste falhar

Leia o nome do cenário e a comparação que falhou. Verifique se a mudança quebrou um comportamento esperado ou se houve uma mudança intencional de requisito. Não remova verificações, não troque valores esperados e não marque o cenário para ser ignorado apenas para obter um resultado verde.

Ao corrigir um defeito, acrescente um cenário que reproduza o problema. Se o comportamento esperado mudou intencionalmente, atualize o teste e explique o motivo junto da alteração. Execute novamente a suíte após a última mudança.

Ao pedir uma manutenção a uma ferramenta de IA, inclua uma instrução como:

> Leia `docs/testes-e-manutencao.md`. Após implementar a alteração, execute a validação recomendada no documento e os testes específicos afetados. Informe o comando, o resultado e qualquer limitação. Não enfraqueça testes para esconder regressões. Para corrigir um defeito, acrescente um cenário que o reproduza.

## O que ainda precisa de conferência

Uma suíte aprovada reduz o risco de regressão; não garante que toda a aplicação esteja correta. Para mudanças na interface, confira também o fluxo afetado no navegador, incluindo navegação, mensagens de erro e gravação dos dados. Para alterações em relatórios, confira os cálculos e campos afetados: a suíte atual valida famílias e quantidade de registros, sem conferir cada célula de cada planilha.

Mudanças nos modelos também exigem planejar a atualização dos bancos existentes. Os testes criam tabelas novas, e o `manage.py` não migra automaticamente a estrutura das tabelas já instaladas.
