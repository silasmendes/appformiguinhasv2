# Mapa do projeto

Este documento descreve a organização atual. Consulte o código e os testes antes de assumir que dois fluxos com nomes semelhantes têm a mesma implementação.

## Entrada e configuração

| Local | Responsabilidade |
| --- | --- |
| `main.py` | Cria a aplicação e registra páginas, ficha da família, busca, pré-cadastro, dashboards e exportações Excel. |
| `app/__init__.py` | Factory `create_app(test_config=None)`, extensões, configuração dos bancos, autenticação, sessões, blueprints e helpers de template. |
| `config.py` | Lê configuração do ambiente e `.env`, incluindo caminhos dos bancos e serviços opcionais. |
| `manage.py` | Cria tabelas ausentes, categorias e administrador. Dados fictícios só são incluídos com `--with-demo-data`. Não é um sistema de migrações. |
| `compose.yaml`, `Dockerfile` | Execução em container; consulte o [guia da VPS](deploy-vps.md). |

Importar `main` ou `manage` cria uma aplicação. Nos testes, prepare a configuração antes dessas importações e evite reutilizar uma instância com caminhos de outro cenário.

## Caminho dos dados

As páginas usam templates em `app/templates/` e JavaScript em `app/static/js/`. A navegação das onze etapas de atendimento à familias está em `app/routes/fluxo_atendimento.py`. O JavaScript também chama APIs para persistir registros; uma resposta de navegação bem-sucedida não comprova que os dados foram gravados.

As APIs estão em `app/routes/`, registradas por `app/routes/__init__.py`. Elas recebem dados JSON, usam os schemas Marshmallow em `app/schemas/` e persistem modelos SQLAlchemy de `app/models/`. As consultas SQL dos relatórios estão principalmente em `main.py`; mudanças nos modelos podem exigir atualizar essas consultas.

`app/utils/fluxo_atendimento.py` carrega os dados da família e normaliza campos para os formulários. Dados de trabalho são mantidos na sessão e também há uso de `sessionStorage` no navegador. Ao adicionar ou renomear um campo, confira gravação, recarregamento, navegação e exportação.

Exemplos de nomes diferentes entre formulário e API: `renda_familiar_total`/`renda_total_familiar`, `total_gastos`/`gastos_totais` e `saldo`/`saldo_mensal`. Alguns valores monetários são serializados como strings decimais; booleanos podem aparecer como `Sim`/`Não` no formulário. Preserve os contratos de cada camada.

## Bancos e sessões

- O banco principal padrão é `instance/formiguinhas.db`, configurável por `DATABASE_URL`.
- O banco de pré-cadastro padrão é `instance/precadastro.db`, configurável por `PRE_CADASTRO_DATABASE_URL`. Usa a mesma estrutura de tabelas, mas um engine separado em `app.extensions['pre_cadastro_engine']`.
- `app/utils/pre_cadastro.py` consulta e converte dados do pré-cadastro; esse banco começa vazio.
- `app/sqlite.py` configura WAL e tempo de espera por bloqueios nas conexões SQLite.
- As sessões do servidor ficam em arquivos, com diretório configurável por `SESSION_FILE_DIR`.

Não versione esses arquivos nem use bancos com dados reais em testes. Veja [banco e recuperação](banco-e-recuperacao.md).

## Autenticação e serviços

`app/auth/__init__.py` trata login, logout e redefinição de senha. `app/routes/usuarios.py` inclui gerenciamento de usuários e a verificação de administrador. Confira os decorators em cada rota: a proteção não é uniforme em todas as APIs antigas.

`app/utils/resumo_familia.py` integra a geração de resumos com OpenAI, com fallback local e cache. `app/utils/openai_usage_tracker.py` registra consumo. `app/utils/email_reset.py` envia redefinições via SendGrid. Essas integrações não devem receber chamadas reais na validação automática do servidor.

## Onde validar

Execute `scripts/validate.py` para a seleção revisada de testes de servidor. O teste `tests/test_playwright_atendimento.py` exercita o navegador contra um servidor já iniciado e permanece separado. A [documentação de testes](testes-e-manutencao.md) descreve cobertura, comandos e riscos dos testes antigos.
