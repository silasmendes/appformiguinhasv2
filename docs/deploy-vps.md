# Deploy na VPS: Flask + SQLite

Esta etapa prepara a imagem, o Compose, os dados persistentes e a configuração
de produção. Requer uma VPS Linux com Docker Engine e Docker Compose v2, acesso
ao repositório e acesso de rede para baixar a imagem e as dependências.
Não é necessário instalar Python ou uv no host.

O proxy reverso, domínio/HTTPS, ajustes de concorrência do SQLite, backups e
migrações de esquema ainda não são configurados por este procedimento.

## Primeira instalação

Na pasta clonada do projeto:

```bash
cp .env.example .env
chmod 600 .env
docker compose build
docker compose run --rm --no-deps app python -c 'import secrets; print(secrets.token_hex(32))'
```

Edite o `.env` da VPS: coloque o segredo gerado em `SECRET_KEY` e escolha uma
senha própria de pelo menos 12 caracteres em `SENHA_ADMIN`. Os valores fictícios
do exemplo são rejeitados em produção. A chave OpenAI é opcional.
Cada instalação tem seu próprio `.env`; não sobrescreva um arquivo já configurado.
O `.env` é ignorado pelo Git e pelo build. O Compose injeta seus valores no
ambiente do container sem copiar o arquivo para a imagem. Ele também força
`APP_ENV=production`, `FLASK_ENV=production`, debug desativado e os caminhos dos
bancos e das sessões nos volumes, mesmo que o exemplo tenha valores locais.

Depois de preencher os valores:

```bash
docker compose config --quiet
docker compose run --rm app python manage.py
docker compose up -d
docker compose ps
docker compose logs --tail=100 app
curl --fail http://127.0.0.1:5000/login
```

O `manage.py` deve terminar com sucesso antes de iniciar a aplicação. Ele cria
os dois bancos SQLite, as categorias e o administrador. Sem `SENHA_ADMIN`,
solicita a senha no terminal na primeira inicialização; atualizações de uma base
que já possui administrador não exigem nem alteram sua senha. Depois de criar o
administrador, você pode remover `SENHA_ADMIN` do arquivo.

Para uma instalação de demonstração, inclua explicitamente:

```bash
docker compose run --rm app python manage.py --with-demo-data
```

Esse comando cria as quatro famílias fictícias anunciadas na modal. Não é
executado automaticamente ao iniciar o serviço. Reexecutar sem essa opção não
remove famílias de demonstração já existentes.

## Produção e persistência

- Gunicorn executa a aplicação como usuário sem privilégios, com um processo e
  quatro threads. Não usa o servidor de desenvolvimento nem recarregamento.
- O volume `sqlite_data` contém `formiguinhas.db` e `precadastro.db` em
  `/app/instance`. O volume `session_data` contém as sessões em `/app/flask_session`.
- O Compose fixa esses caminhos Linux; caminhos Windows do ambiente local não
  interferem nos bancos do container. A base local do desenvolvedor não é copiada.
- Os volumes são preservados quando o container é recriado. `docker compose down`
  mantém os volumes; **não use `docker compose down -v`**, pois remove os dados.
- `restart: unless-stopped` reinicia o serviço após falhas/reinício do Docker,
  desde que o daemon Docker também esteja configurado para iniciar com a VPS.
- Logs vão para stdout/stderr e têm rotação configurada pelo Compose.
- `APP_ENV=production` força debug desativado, valida o segredo e ativa cookies
  `Secure`, `HttpOnly` e `SameSite=Lax` para sessão e login persistente.

A porta 5000 está publicada **somente em 127.0.0.1 da VPS**. O `curl` acima testa
o serviço internamente; não significa que o site esteja publicado na internet.
O login de produção exige HTTPS por causa dos cookies Secure. A publicação e o
login pelo navegador dependem da próxima etapa de proxy reverso/HTTPS. Não abra
a porta 5000 em todas as interfaces para contornar essa etapa.

Para aplicar mudanças no código e no `.env`, depois de atualizar o
checkout:

```bash
docker compose build
docker compose run --rm app python manage.py
docker compose up -d --force-recreate
```

Esses comandos preservam os volumes e criam tabelas ausentes; não constituem
um sistema de migrações ou rollback. Alterações em tabelas existentes precisam
de migração e backup antes da atualização.
