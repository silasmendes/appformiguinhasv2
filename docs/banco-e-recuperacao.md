# Banco, atualização e recuperação

`manage.py` cria tabelas ausentes; não altera a estrutura de tabelas existentes. Uma suíte aprovada contra bancos novos não comprova que uma instalação antiga pode ser atualizada.

## Antes de alterar modelos

Descreva a mudança de estrutura, quais registros antigos são afetados, como preencher campos novos e se o código anterior ainda funcionará. Prepare um procedimento de migração versionado e teste-o em uma cópia fictícia representativa da estrutura anterior, preservando registros e relações. Este projeto ainda não tem um mecanismo formal de migrações.

Não use exclusão e recriação do banco como atualização de uma instalação com dados. Não execute scripts de migração apenas porque eles foram produzidos por uma IA: revise as operações, valide o resultado na cópia e planeje a recuperação.

## Backup dos dois bancos

Confira os caminhos efetivos da instalação: no ambiente local, são configurados por `DATABASE_URL` e `PRE_CADASTRO_DATABASE_URL`; no Compose, ficam no volume `sqlite_data`. Não publique valores de configuração nem dados pessoais em um chamado ou pull request.

Faça o backup antes da mudança. Para obter um par consistente de bancos durante uma atualização, interrompa a aplicação e qualquer outro processo de escrita. Na VPS, use `docker compose stop app`; veja os volumes e caminhos no [guia de deploy](deploy-vps.md). Mantenha a cópia em local protegido fora do repositório e preserve o original.

SQLite usa WAL. Não copie somente o `.db` de um banco ativo e não exclua arquivos `-wal` ou `-shm` para “desbloquear” o banco. Use a API de backup do SQLite para obter uma cópia completa. O exemplo abaixo copia **um banco**; repita para o principal e o pré-cadastro, ajustando caminhos para a instalação e escolhendo destinos novos:

```python
from pathlib import Path
from contextlib import closing
import sqlite3

source = Path("instance/formiguinhas.db").resolve(strict=True)
destination = Path("../backups/antes-da-atualizacao/formiguinhas.db").resolve()
destination.parent.mkdir(parents=True, exist_ok=True)
# A abertura exclusiva impede sobrescrever um backup anterior por engano.
with destination.open("xb"):
    pass
with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as original:
    with closing(sqlite3.connect(destination)) as backup:
        original.backup(backup)
        result = backup.execute("PRAGMA integrity_check").fetchall()
        if result != [("ok",)]:
            raise RuntimeError("Falha na verificacao de integridade do backup")
```

Execute com o Python do ambiente virtual que possui acesso aos arquivos. Se ocorrer um erro, não use o destino como backup validado. Dentro de containers, os caminhos são diferentes: não execute o exemplo local sem adaptar origem e destino. `integrity_check` verifica a integridade estrutural, mas não substitui conferir famílias, relações e dados relevantes em uma restauração de teste.

Documente a data, a versão do código e quais bancos foram copiados. Proteja também a configuração necessária à recuperação, sem versionar segredos. Os backups contêm dados pessoais e precisam de acesso restrito. A API está documentada em [sqlite3.Connection.backup](https://docs.python.org/3.12/library/sqlite3.html#sqlite3.Connection.backup).

## Publicar uma mudança com banco

1. Execute `scripts/validate.py` e valide o procedimento de migração em uma cópia da estrutura antiga.
2. Combine uma janela sem atendimentos e interrompa as escritas.
3. Gere e verifique os backups dos dois bancos.
4. Execute apenas o procedimento de atualização revisado e registre a versão aplicada.
5. Inicie a aplicação e confira login, consulta de família, carregamento do atendimento e relatórios afetados.

Não use `docker compose down -v`: esse comando remove volumes com dados. Não rode inicialização ou migrações enquanto pessoas estão atendendo famílias.

## Se for necessário recuperar

Pare a aplicação e as demais escritas. Preserve os arquivos do estado com falha para investigação; restaure uma cópia do backup em um diretório ou volume separado e valide-a antes de substituir os arquivos da instalação. Não misture arquivos `.db`, `-wal` e `-shm` de momentos diferentes.

Restaure também uma versão de código compatível com a estrutura recuperada. Reinicie as sessões para que dados de trabalho antigos não sobrescrevam dados restaurados; essa etapa encerra atendimentos em andamento e deve ser coordenada com os usuários. Confirme o resultado antes de liberar o serviço.

Restaurar um backup pode perder tudo que foi gravado depois dele. Reverter apenas o commit não desfaz migrações nem recupera registros apagados. A operação deve ser autorizada pelo responsável pela instalação e ter seu impacto explicado.
