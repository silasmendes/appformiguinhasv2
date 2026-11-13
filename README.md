# Formiguinhas - Desenvolvimento local

Aplicação Flask que utiliza SQLite por padrão. Recomendamos Python 3.12 para compatibilidade com as versões das dependências definidas no projeto.

## Instalação e execução

Com o `uv` instalado, abra o PowerShell na pasta do repositório e execute:

```powershell
uv venv --python 3.12
uv pip install -r requirements.txt
```

Se você ainda não tiver um `.env`, copie o arquivo de exemplo:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` e ajuste os valores para seu ambiente. Depois, inicialize os bancos e execute a aplicação:

```powershell
.venv\Scripts\python.exe manage.py --with-demo-data
.venv\Scripts\python.exe -m flask --app main run --debug
```

Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000) e entre com o usuário **admin** e a senha definida em `SENHA_ADMIN` no `.env`. 

Você pode repetir a inicialização sem excluir os dados ou alterar a senha de um administrador existente. A variável `SENHA_ADMIN` também pode ser definida diretamente no ambiente.

## Dados de demonstração

A opção `--with-demo-data` inclui quatro famílias fictícias:

- **525.067.333-37**
- **928.105.770-05**
- **955.314.618-01**
- **742.691.086-57**

Os nomes dessas famílias contêm `(Teste)`. Para adicionar os exemplos ausentes em um banco já existente, execute novamente `manage.py --with-demo-data`.

Para criar apenas as tabelas, as categorias e o administrador, execute sem a opção de demonstração:

```powershell
.venv\Scripts\python.exe manage.py
```

Executar sem essa opção não remove famílias fictícias criadas anteriormente.

## Banco de dados e configuração

Os bancos ficam em `instance/formiguinhas.db` e `instance/precadastro.db`. Ambos são ignorados pelo Git.

O banco de pré-cadastro começa vazio e utiliza a mesma estrutura de tabelas SQLAlchemy do banco principal. Ele é independente: a busca de pré-cadastros só retorna resultados depois que você o preencher. 

## Resumos por inteligência artificial

Os resumos utilizam a API direta da OpenAI. Para habilitá-los, configure no `.env`:

```dotenv
OPENAI_API_KEY=sua-chave-de-api-do-projeto
OPENAI_MODEL=gpt-6-luna
```

Reinicie o Flask após alterar a configuração. A aplicação utiliza apenas `POST https://api.openai.com/v1/chat/completions`, com esforço de raciocínio baixo e limite de 2.000 tokens de conclusão, incluindo os tokens de raciocínio.

Escolha um modelo compatível com esses parâmetros e confirme que seu projeto tem acesso a ele.

Credenciais, nomes de implantação, endpoints e versões de API do Azure não são mais utilizados.

Sem uma chave, ou se a chamada falhar, a aplicação gera um resumo local. Esses resumos locais não são armazenados em cache nem salvos como resumos de IA.

Resumos gerados pela API são reaproveitados por até 12 horas.

O consumo de tokens é registrado no SQLite, sem consultar os endpoints de uso ou faturamento da OpenAI. 

Crie uma chave de projeto com permissões **Restricted** e permita somente **Model capabilities → Chat Completions → Request/Write**. Deixe os demais endpoints como **None**.

Não é necessário liberar Models Read, Responses, Files, Assistants, Threads, Batch, Fine-tuning, Images, Audio, Embeddings, Usage ou permissões administrativas.

Em **Limits → Model usage** do projeto, permita apenas o modelo configurado.

## E-mails e ambiente de produção

O envio de e-mails de redefinição de senha depende da configuração do SendGrid.

OpenAI e SendGrid são opcionais para login local e cadastro, consulta, atualização e exclusão de registros.

O servidor Flask com debug e os segredos de exemplo são destinados somente ao desenvolvimento local.

Para executar em uma VPS Linux com Docker Compose, siga o [guia de deploy na VPS](docs/deploy-vps.md).

## Testes

Execute os testes de regressão do SQLite com:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_sqlite_local.py -q
```

Esses testes utilizam bancos temporários e não alteram os dados do seu banco de desenvolvimento local.

O `manage.py` cria tabelas ausentes, mas não migra a estrutura de tabelas existentes após alterações nos modelos.