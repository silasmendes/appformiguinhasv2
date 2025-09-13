# Guia de Implementação de Relatórios no Dashboard

## Visão Geral

Este documento serve como referência para implementação de novos relatórios no sistema Formiguinhas Solidárias. Baseado na implementação bem-sucedida do relatório "Famílias Atendidas nos Últimos 30 Dias", este guia apresenta o padrão estabelecido e as melhores práticas para manter consistência no projeto.

## Estrutura do Projeto

### Organização de Arquivos

```
app/
├── templates/
│   └── dashboards/
│       ├── dashboard.html                    # Dashboard principal
│       ├── demandas_ativas.html             # Relatório de demandas (referência)
│       └── [novo_relatorio].html            # Novo relatório
├── static/
│   ├── css/
│   │   ├── dashboard.css                    # CSS base do dashboard
│   │   ├── dashboard_demandas.css           # CSS específico de demandas
│   │   └── [novo_relatorio].css             # CSS específico do novo relatório
│   └── js/
│       ├── dashboard_demandas.js            # JS específico de demandas
│       └── [novo_relatorio].js              # JS específico do novo relatório
main.py                                      # Rotas do back-end
```

## Padrão de Implementação

### 1. Rota no Back-end (main.py)

#### Padrão de Nomenclatura
- URL: `/dashboard/[nome-relatorio-kebab-case]`
- Função: `dashboard_[nome_relatorio_snake_case]()`

#### Template de Rota
```python
@app.route("/dashboard/[nome-relatorio]")
@login_required
@admin_required
def dashboard_[nome_relatorio]():
    """Descrição do relatório."""
    sql = text(
        """
        SELECT [colunas necessárias]
        FROM [tabelas principais] f
        JOIN [tabelas relacionadas] ON [condições de join]
        WHERE [filtros específicos do relatório]
        ORDER BY [ordenação apropriada]
        """
    )

    resultados = db.session.execute(sql).mappings().all()
    dados = [dict(r) for r in resultados]
    return render_template("dashboards/[nome_relatorio].html", [nome_variavel]=dados)
@@ -120,75 +120,75 @@ def dashboard_familias_atendidas_30_dias():
            <tr class="filtros">
                <!-- Inputs de filtro para cada coluna -->
            </tr>
        </thead>
        <tbody></tbody>
    </table>
</div>
<nav>
    <ul class="pagination" id="paginacao[NomeRelatorio]"></ul>
</nav>
{% endblock %}

{% block extra_js %}
<script>
    window.[nomeVariavelDados] = {{ [variavel_backend] | tojson }};
</script>
<script src="{{ url_for('static', filename='js/[nome_relatorio].js') }}"></script>
{% endblock %}
```

### 3. CSS Específico

#### Padrões de Estilo

```css
/* Estilos de cabeçalho - padrão para todos os relatórios */
.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
}

.header-text h1 {
    color: white;
    font-weight: 700;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 2rem;
}

.header-text p {
    margin: 0;
    opacity: 0.9;
    font-size: 1.1rem;
}

/* Cabeçalho responsivo */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        align-items: flex-start;
    }
}

/* Estilo da tabela - Adaptar ID da tabela */
#tabela[NomeRelatorio] {
    font-size: 0.875rem;
    border: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border-radius: 12px;
    overflow: hidden;
    background: white;
}

/* Hover personalizado por tipo de relatório */
#tabela[NomeRelatorio] tbody tr:hover {
    background-color: rgba([cor-tema], 0.02);
    transform: scale(1.001);
}

/* Badges específicos do relatório */
.badge-[tipo] {
@@ -431,222 +431,267 @@ function formatarData(data) {
.badge-nao { background-color: #6c757d; color: white; }
```

## Integração com Dashboard Principal

### Atualização do Link no Dashboard

No arquivo `dashboard.html`, localizar o script de clique dos cards e atualizar:

```javascript
// De:
} else if (title === '[Título do Card]') {
    window.location.href = "{{ url_for('dashboard_em_desenvolvimento') }}";

// Para:
} else if (title === '[Título do Card]') {
    window.location.href = "{{ url_for('[nome_funcao_rota]') }}";
```

### Atualização Dinâmica dos Cards do Dashboard

**IMPORTANTE**: Após implementar um novo relatório, é necessário atualizar o respectivo card no dashboard principal para mostrar dados reais em vez de valores mock.

#### Padrão de Implementação

No arquivo `main.py`, na função `dashboard()`, adicionar uma consulta SQL para calcular dinamicamente o valor do card:

```python
# Exemplo para famílias atendidas nos últimos 30 dias
sql_familias_atendidas_30_dias = text(
    """
    SELECT COUNT(DISTINCT f.familia_id) as total_familias_atendidas_30_dias
    FROM familias f
    JOIN atendimentos a ON f.familia_id = a.familia_id
    WHERE a.data_hora_atendimento >= DATEADD(DAY, -30, GETDATE())
    """
)

resultado_atendidas = db.session.execute(sql_familias_atendidas_30_dias).mappings().first()
total_familias_atendidas_30_dias = resultado_atendidas['total_familias_atendidas_30_dias'] if resultado_atendidas else 0

# Atualizar o valor no dicionário dados_dashboard
dados_dashboard = {
    # ... outros valores
    'familias_atendidas_30_dias': total_familias_atendidas_30_dias,  # ← Substituir valor mock
    # ... outros valores
}
```

#### Template de consulta para cards dinâmicos

```python
# Template genérico para contagem de registros
sql_[nome_metrica] = text(
    """
    SELECT COUNT(DISTINCT [tabela_principal].[id_campo]) as total_[nome_metrica]
    FROM [tabela_principal] [alias]
    [JOINS necessários]
    WHERE [condições específicas da métrica]
    """
)

resultado_[nome_metrica] = db.session.execute(sql_[nome_metrica]).mappings().first()
total_[nome_metrica] = resultado_[nome_metrica]['total_[nome_metrica]'] if resultado_[nome_metrica] else 0
```

#### Exemplos de consultas por tipo de card

**Contagem de Famílias por Período:**
```sql
SELECT COUNT(DISTINCT f.familia_id) as total
FROM familias f
JOIN atendimentos a ON f.familia_id = a.familia_id
WHERE a.data_hora_atendimento >= DATEADD(DAY, -[DIAS], GETDATE())
```

**Contagem de Entregas de Cestas:**
```sql
SELECT COUNT(*) as total
FROM atendimentos a
WHERE a.cesta_entregue = 1 
AND a.data_hora_atendimento >= DATEADD(DAY, -30, GETDATE())
```

**Bairro com Mais Atendimentos:**
```sql
SELECT TOP 1 e.bairro
FROM enderecos e
JOIN familias f ON e.familia_id = f.familia_id
JOIN atendimentos a ON f.familia_id = a.familia_id
WHERE a.data_hora_atendimento >= DATEADD(DAY, -30, GETDATE())
GROUP BY e.bairro
ORDER BY COUNT(*) DESC
```

**Famílias por Nível de Vulnerabilidade:**
```sql
SELECT COUNT(DISTINCT f.familia_id) as total
FROM familias f
JOIN atendimentos a ON f.familia_id = a.familia_id
WHERE a.percepcao_necessidade = 'Alta'
AND a.data_hora_atendimento >= DATEADD(DAY, -30, GETDATE())
```

#### Lista de verificação para atualização de cards

- [ ] Implementar consulta SQL específica para a métrica do card
- [ ] Executar a consulta na função `dashboard()` em `main.py`
- [ ] Substituir o valor mock no dicionário `dados_dashboard`
- [ ] Testar se o card exibe o valor correto no dashboard
- [ ] Verificar se o valor é atualizado quando novos dados são inseridos

### Ícones Recomendados (Font Awesome)

- **Famílias**: `fas fa-users`
- **Atendimentos**: `fas fa-calendar-check`
- **Cestas**: `fas fa-box`
- **Demandas**: `fas fa-exclamation-triangle`
- **Vulnerabilidade**: `fas fa-heartbeat`
- **Localização**: `fas fa-map-marker-alt`
- **Download**: `fas fa-download`
- **Relatórios**: `fas fa-chart-line`

## Exportação de dados em Excel

### 1. Rota no back-end (`main.py`)
- **URL**: `/dashboard/[nome-relatorio-kebab-case]/download`
- **Função**: `download_[nome_relatorio_snake_case]()`
- **Requisitos**
  - Incluir `@login_required` e `@admin_required`.
  - Buscar **todas** as colunas relevantes (família, endereços, contatos etc.), mesmo as não exibidas na tabela do relatório.
  - Transformar o resultado em `pandas.DataFrame`, remover fuso horário (`tzinfo`) quando existir e renomear colunas para PT-BR.
  - Retornar o arquivo usando `send_file(..., as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')`.
- **Exemplo**
  `download_familias_atendidas_30_dias()` em `main.py`.

### 2. Template HTML (`app/templates/dashboards/[novo_relatorio].html`)
- Adicionar botão de download dentro de `.header-actions`:
  ```html
  <button id="downloadBtn" class="btn btn-primary"
          data-url="{{ url_for('download_[nome_relatorio]') }}">
      <i class="fas fa-file-excel"></i>
      Baixar Excel
  </button>
  ```
- Manter o link “Voltar ao Dashboard” ao lado do botão, conforme padrão das páginas existentes.

### 3. JavaScript (`app/static/js/[novo_relatorio].js`)
- No `DOMContentLoaded`, capturar clique em `#downloadBtn`.
- Efetuar `fetch` `GET` para `downloadBtn.dataset.url`.
- Converter a resposta para `blob`, criar `URL.createObjectURL`, definir o nome do arquivo `"[nome_relatorio]_AAAA_MM_DD.xlsx"` e disparar o download.
- Exemplo de uso: `familias_atendidas_30_dias.js`.

### 4. CSS (`app/static/css/[novo_relatorio].css`)
- Utilizar layout flexível do cabeçalho:
  ```css
  .header-content { display: flex; justify-content: space-between; align-items: center; gap: 2rem; }
  .header-actions { display: flex; align-items: center; gap: 1rem; }
  ```
  - Garantir responsividade via consultas de mídia (`media queries`) semelhantes às usadas em `familias_atendidas_30_dias.css`.

### 5. Lista de verificação adicional
- [ ] Rota de download criada com `@login_required` e `@admin_required`.
- [ ] Botão “Baixar Excel” adicionado ao template.
- [ ] Lógica de download implementada em JS.
- [ ] Arquivo CSS do relatório contém estilos do cabeçalho e botão.
- [ ] Planilha contém todas as colunas necessárias com nomenclatura em PT-BR.

## Responsividade

### Pontos de quebra padrão

```css
/* Tablet */
@media (max-width: 992px) {
    /* Reduzir font-size da tabela */
    #tabela[Nome] { font-size: 0.8rem; }
}

/* Mobile */
@media (max-width: 768px) {
    /* Ajustes para mobile */
    #tabela[Nome] { font-size: 0.75rem; }
    .badge-[tipo] { font-size: 0.65rem; padding: 0.25rem 0.5rem; }
}
```

## Lista de verificação de implementação

### ✅ Back-end
- [ ] Criar rota em `main.py` com decorators `@login_required` e `@admin_required`
- [ ] Implementar consulta SQL com JOINs apropriados
- [ ] Converter resultados para lista de dicionários
- [ ] Passar dados para template via `render_template`

### ✅ Front-end
- [ ] Criar template HTML seguindo estrutura padrão
- [ ] Implementar cabeçalhos e filtros de tabela
- [ ] Criar CSS específico com ID único da tabela
- [ ] Implementar JavaScript com filtros e paginação
- [ ] Adicionar formatações específicas do relatório

### ✅ Integração
- [ ] Atualizar link no dashboard principal
- [ ] **Implementar atualização dinâmica do card correspondente no dashboard**
- [ ] Testar navegação entre páginas
- [ ] Verificar responsividade em diferentes tamanhos de tela
- [ ] Validar formatação de dados e badges
- [ ] **Verificar se o card exibe dados reais (não mock) no dashboard principal**

## Exemplos de consultas por tipo de relatório

### Relatórios Temporais (30 dias, 90 dias, etc.)
```sql
WHERE a.data_hora_atendimento >= NOW() - INTERVAL [X] DAY
```

### Relatórios por Status
```sql
WHERE df.status = '[status_especifico]'
```

### Relatórios por Localização
```sql
WHERE e.bairro = '[bairro_especifico]'
OR e.cidade = '[cidade_especifica]'
```

### Relatórios Agregados
```sql
SELECT e.bairro, COUNT(*) as total_familias
FROM familias f
JOIN enderecos e ON f.familia_id = e.familia_id
GROUP BY e.bairro
ORDER BY total_familias DESC
```

## Considerações de desempenho

### Índices Recomendados
- `familia_id` em todas as tabelas relacionadas
- `data_hora_atendimento` para filtros temporais
- `status` e `prioridade` para filtros de demandas
- `bairro` e `cidade` para filtros geográficos

### Paginação
- Manter padrão de 15 registros por página
- Implementar paginação no front-end (não no back-end)
- Mostrar indicador de "Nenhum registro encontrado"

## Manutenção e Evolução

### Versionamento
- Manter comentários nas consultas SQL explicando a lógica
- Documentar formatações específicas em comentários no CSS
- Usar nomes descritivos para funções JavaScript

### Extensibilidade
- Criar funções de formatação reutilizáveis
- Modularizar CSS comum em classes base
- Manter padrão de nomenclatura consistente

---

**Última atualização**: Setembro 2025  
**Versão**: 1.0  
**Baseado na implementação**: Famílias Atendidas nos Últimos 30 Dias