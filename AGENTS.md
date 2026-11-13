# Orientações para agentes

## Projeto e contexto

Aplicação Flask, SQLAlchemy e SQLite para cadastro e atendimento de famílias. Use Python 3.12 e as versões de `requirements.txt`. A interface e a documentação são em português.

Antes de alterar um fluxo, leia os arquivos envolvidos e consulte:

- `docs/arquitetura.md`: mapa do código e persistência.
- `docs/regras-de-negocio.md`: comportamentos atuais e limitações conhecidas.
- `docs/testes-e-manutencao.md`: cobertura, comandos e cuidados dos testes.
- `docs/banco-e-recuperacao.md`: mudanças no banco, backup e recuperação.

## Como trabalhar

- Examine `git status` e preserve alterações locais. Não faça reset, limpeza de arquivos ou sobrescrita de trabalho alheio.
- Implemente o pedido com o menor conjunto coerente de mudanças. Evite refatorações ou atualizações de dependências sem relação com o problema.
- Confira o percurso completo dos campos: HTML/JavaScript, rotas, schemas, modelos, carregamento da sessão e relatórios. Eles podem usar nomes e formatos diferentes.
- Ao corrigir um defeito, acrescente um teste que reproduza o comportamento esperado. Não remova verificações, não ignore cenários e não reduza a seleção de testes para esconder falhas.
- Atualize os documentos afetados. Distinga comportamento existente de requisito novo; não invente regras de negócio.

## Dados e credenciais

- Não publique nem imprima valores de `.env`, credenciais, bancos, sessões ou dados reais das famílias em logs, commits, exemplos ou respostas. Use `.env.example` para documentar configuração.
- Testes automatizados devem usar dados fictícios, bancos temporários e serviços externos substituídos ou bloqueados. Não use o banco local ou produção para validar mudanças.
- Não apague bancos, volumes ou sessões reais e não execute migrações/deploy sem autorização correspondente. `manage.py` cria tabelas; não migra tabelas existentes.
- Para alterar modelos, documente a compatibilidade com bancos existentes, o procedimento de atualização e a recuperação antes de publicar.

## Validação obrigatória

Após alterações substanciais e antes de entregar mudanças de código, execute na raiz:

```powershell
.venv\Scripts\python.exe scripts/validate.py
```

Em Linux/macOS, com o ambiente virtual ativado: `python scripts/validate.py`.

O script seleciona os testes de servidor preparados para execução isolada. Não execute indiscriminadamente `pytest tests`: há testes antigos que usam a configuração normal da aplicação.

O teste `tests/test_playwright_atendimento.py` deve permanecer como está, salvo pedido explícito para alterá-lo. Ele é executado separadamente, contra um servidor escolhido pelo usuário, e grava dados. Não o inclua no comando automático nem o aponte para produção.

Para mudanças de interface, registre a conferência do fluxo no navegador e qualquer cobertura que não foi executada. Para falhas, investigue o motivo e execute novamente a validação após a correção. Se não puder executar, informe a limitação; não declare testes aprovados.

## Entrega

Informe o que mudou, o motivo, o comando executado e o resultado real. Explique impactos em dados, configuração, dependências e limitações relevantes. Não faça commit, push, merge ou deploy apenas para concluir uma tarefa local sem que isso tenha sido solicitado.
