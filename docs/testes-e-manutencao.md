# Testes após alterações no sistema

Uma alteração pode funcionar na tela modificada e causar problemas em outro lugar: mudar um campo do cadastro, por exemplo, pode afetar a gravação no banco, o carregamento do atendimento e uma exportação Excel. Isso vale para alterações feitas manualmente, com Codex, com Claude Code ou com outra ferramenta.

Execute a suíte de regressão antes de aceitar mudanças substanciais e antes de publicar uma versão. Considere substanciais as mudanças em modelos ou estrutura do banco, rotas, autenticação, cadastro, atendimento, demandas, relatórios, configuração, dependências e inicialização. Execute também os testes específicos da funcionalidade alterada.

## Os dois arquivos discutidos

Os arquivos abaixo têm coberturas diferentes e também estados de preparação diferentes. **Atualmente, somente `test_sqlite_local.py` está preparado para a rotina de validação com bancos temporários e cenários independentes.** O teste antigo de cadastro completo precisa de ajustes antes de ser obrigatório nessa rotina.

| Arquivo | O que verifica | Limites e segurança |
| --- | --- | --- |
| `tests/test_sqlite_local.py` | Login, senha incorreta, logout, acesso às páginas protegidas selecionadas; criação, leitura, atualização e exclusão de família; persistência em uma nova instância da aplicação; valores e vínculo das oito seções complementares; carregamento de campos no formulário; atendimento com identificação do usuário autenticado; demanda com histórico inicial; rejeição dos dados inválidos selecionados; filtros dos relatórios; registros e quantidade de linhas dos sete arquivos Excel; separação do pré-cadastro; preservação da senha do administrador; campos sem o texto indevido `None`. | Usa uma aplicação e dois bancos SQLite temporários por cenário, bloqueia conexões de rede e substitui a geração de resumos. Não testa navegador, JavaScript, cliques ou todos os campos e regras de negócio. |
| `tests/test_integracao_cadastro_completo.py` | Envia os dados pessoais e as oito seções complementares pelas APIs, consulta os registros criados, cria duas demandas para a mesma família, registra uma etapa, atualiza explicitamente o status da demanda e rejeita uma categoria inválida. | Na versão atual, usa a configuração normal da aplicação, sem criar bancos temporários nem preparar tabelas e categorias. Os cenários compartilham IDs globais e dependem da ordem. Não prepara login, embora a criação de demandas e etapas exija autenticação. A maioria das verificações confere apenas códigos HTTP. |

## Como executar a validação disponível

No PowerShell, na raiz do repositório, com as dependências instaladas conforme o README:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_sqlite_local.py -q
```

Não é necessário iniciar o Flask, preparar dados de demonstração ou fornecer credenciais de OpenAI/SendGrid. O teste prepara seus próprios dados.

O resultado esperado é uma linha final com `passed`, sem `failed` nem `ERROR`. A quantidade pode aumentar conforme novos cenários forem adicionados. Avisos (`warnings`) não são falhas, mas devem ser avaliados quando relacionados à mudança ou a uma atualização de dependências.

Para ver mais detalhes de uma falha:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_sqlite_local.py -v --tb=short
```

## Quando executar os dois juntos

Não execute o teste antigo de cadastro completo contra os bancos de desenvolvimento ou de produção: ele grava registros e não oferece o mesmo isolamento. Alterar apenas o `.env` não resolve suas dependências de ordem, dados iniciais e autenticação.

Antes de incluir esse arquivo na validação obrigatória, é necessário:

1. Criar bancos e sessões temporários, com limpeza dos recursos ao final.
2. Preparar tabelas, categorias e um usuário de teste autenticado.
3. Remover a dependência de IDs globais e da ordem de execução.
4. Confirmar que cada cenário passa isoladamente e que a execução conjunta não usa os bancos locais.

Depois desses ajustes e da validação dos dois arquivos, o comando conjunto será:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_sqlite_local.py tests/test_integracao_cadastro_completo.py -q
```

Esse é um comando para a etapa futura descrita acima; não é a recomendação de execução para o estado atual. Também não execute indiscriminadamente toda a pasta `tests`, pois outros testes antigos podem usar a configuração normal da aplicação.

## O que fazer quando um teste falhar

Leia o nome do cenário e a comparação que falhou. Verifique se a mudança quebrou um comportamento esperado ou se houve uma mudança intencional de requisito. Não remova verificações, não troque valores esperados e não marque o cenário para ser ignorado apenas para obter um resultado verde.

Ao corrigir um defeito, acrescente um cenário que reproduza o problema. Se o comportamento esperado mudou intencionalmente, atualize o teste e explique o motivo junto da alteração. Execute novamente a suíte após a última mudança.

Ao pedir uma manutenção a uma ferramenta de IA, inclua uma instrução como:

> Leia `docs/testes-e-manutencao.md`. Após implementar a alteração, execute a validação recomendada no documento e os testes específicos afetados. Informe o comando, o resultado e qualquer limitação. Não enfraqueça testes para esconder regressões. Para corrigir um defeito, acrescente um cenário que o reproduza.

## O que ainda precisa de conferência

Uma suíte aprovada reduz o risco de regressão; não garante que toda a aplicação esteja correta. Para mudanças na interface, confira também o fluxo afetado no navegador, incluindo navegação, mensagens de erro e gravação dos dados. Para alterações em relatórios, confira os cálculos e campos afetados: a suíte atual valida famílias e quantidade de registros, sem conferir cada célula de cada planilha.

Mudanças nos modelos também exigem planejar a atualização dos bancos existentes. Os testes criam tabelas novas, e o `manage.py` não migra automaticamente a estrutura das tabelas já instaladas.
