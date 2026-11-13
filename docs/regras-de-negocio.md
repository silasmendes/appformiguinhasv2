# Comportamentos a preservar

Este documento registra comportamentos atuais e pontos que exigem decisão antes de mudanças. Não substitui uma especificação completa. Ao mudar um requisito, atualize o documento e acrescente exemplos verificáveis com dados fictícios.

## Cadastro e atendimento

- A família é identificada por `familia_id`. Endereço, contato, composição, moradia, saúde, emprego, renda e educação devem continuar associados à família correta.
- Existem estados de cadastro `rascunho` e `finalizado`. Não trate automaticamente todo registro criado como cadastro concluído.
- O fluxo tem onze etapas: dados pessoais, endereço, composição, contato, moradia, saúde, emprego, renda, educação, demandas e encerramento. Preserve os dados ao avançar e ao carregar uma família existente.
- Valores ausentes devem aparecer vazios no formulário, sem texto literal `None`. A normalização deve preservar números, zero e booleanos.
- A API de família valida estados civis e a relação entre gênero `Outro` e gênero autodeclarado. O CPF pode estar vazio; o validador atual também aceita sequências repetidas de dígitos. Mudar essa exceção exige decisão explícita e avaliação de cadastros existentes.
- A criação e a atualização de atendimento usam o ID do usuário autenticado, mesmo que o cliente envie outro `usuario_atendente_id`.
- Renda e despesas têm nomes e formatos diferentes entre formulário, sessão e API. Cálculos no JavaScript não significam validação equivalente no servidor. Teste também os valores persistidos quando alterar cálculos.

## Demandas

- A criação via `POST /demandas` gera uma etapa inicial com o status da demanda e o usuário autenticado.
- Os status aceitos pelo schema são `Em análise`, `Em andamento`, `Encaminhada`, `Aguardando resposta`, `Suspensa`, `Cancelada` e `Concluída`.
- A categoria precisa estar entre os IDs aceitos pelo schema e existir na tabela de tipos. O inicializador prepara sete categorias.
- O histórico (`DemandaEtapa`) e o status de `DemandaFamilia` são armazenados separadamente. Criar uma etapa pela API não atualiza automaticamente o status na outra tabela. Ao mudar o fluxo, confira ambos e os relatórios.
- Não confunda a última etapa por maior `etapa_id` com a maior data informada. Algumas consultas usam o primeiro critério.

## Relatórios

| Relatório | Critério relevante na implementação atual |
| --- | --- |
| Famílias cadastradas | Exporta dados das famílias e seções relacionadas; a página é uma tela de download. |
| Famílias atendidas em 30 dias | Usa a data/hora de atendimento nos últimos 30 dias. A listagem pode ter mais de uma linha por família, enquanto o indicador conta famílias distintas. |
| Entregas de cestas em 30 dias | Filtra a data/hora do atendimento e `cesta_entregue`; não usa apenas a data de entrega informada. O indicador conta atendimentos com cesta. |
| Famílias sem atendimento recente | Cadastro no último ano e nenhum atendimento, ou último atendimento anterior a 90 dias. |
| Maior vulnerabilidade | Usa atendimentos com percepção `Alta`; a listagem seleciona o mais recente dentre os atendimentos de percepção alta, não necessariamente o último atendimento geral. |
| Demandas ativas e painel de demandas | Dependem das relações com categorias e histórico. Algumas consultas também exigem endereço. |

**Limitação conhecida:** o nome “demandas ativas” não garante um filtro de status em todas as consultas atuais. Não considere a suíte uma prova de que demandas concluídas são sempre excluídas. Qualquer correção deve definir o requisito e incluir casos de demandas abertas e encerradas, além de famílias com e sem endereço.

As consultas de indicadores, listagens e exportações não são necessariamente idênticas. Ao mudar filtros, datas ou agregações, confira as três saídas e a quantidade de linhas esperada.

## Inicialização, dados e acesso

- Reexecutar a inicialização preserva a senha de um administrador existente.
- Dados de demonstração só são incluídos mediante `--with-demo-data`; executar sem a opção não apaga exemplos existentes.
- O pré-cadastro é independente do banco principal. Uma família no banco principal não deve aparecer na busca de pré-cadastro por esse motivo apenas.
- Em produção, a factory rejeita segredos ausentes ou de exemplo e configura cookies seguros; o acesso pelo navegador depende de HTTPS.
- Há APIs antigas sem proteção de login uniforme. Isso é uma limitação a revisar, e não uma autorização para remover proteção de outras rotas. Mudanças de acesso precisam de testes de usuário anônimo, autenticado e perfis pertinentes.

## Alteração de uma regra

Registre o comportamento anterior, o novo comportamento e um exemplo fictício que diferencie os dois. Confira compatibilidade dos registros já existentes e atualize os testes. Se o requisito estiver ambíguo, peça uma decisão sobre o resultado esperado antes de modificar dados ou regras.
