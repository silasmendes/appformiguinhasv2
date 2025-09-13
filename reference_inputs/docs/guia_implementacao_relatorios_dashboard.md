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
main.py                                      # Rotas do backend
```

## Padrão de Implementação

### 1. Rota no Backend (main.py)

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
```

#### Exemplo Implementado
```python
@app.route("/dashboard/familias-atendidas-30-dias")
@login_required
@admin_required
def dashboard_familias_atendidas_30_dias():
    """Lista de famílias atendidas nos últimos 30 dias."""
    sql = text(
        """
        SELECT f.familia_id, f.nome_responsavel, f.cpf, e.bairro,
               c.telefone_principal, c.email_responsavel,
               a.percepcao_necessidade, a.cesta_entregue, a.data_hora_atendimento
        FROM familias f
        JOIN enderecos e ON f.familia_id = e.familia_id
        JOIN contatos c ON f.familia_id = c.familia_id
        JOIN atendimentos a ON f.familia_id = a.familia_id
        WHERE a.data_hora_atendimento >= NOW() - INTERVAL 30 DAY
        ORDER BY a.data_hora_atendimento DESC
        """
    )

    resultados = db.session.execute(sql).mappings().all()
    familias = [dict(r) for r in resultados]
    return render_template("dashboards/familias_atendidas_30_dias.html", familias=familias)
```

### 2. Template HTML

#### Estrutura Base
```html
{% extends "base.html" %}

{% block title %}[Título do Relatório]{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/[nome_relatorio].css') }}">
{% endblock %}

{% block content %}
<div class="dashboard-header">
    <div class="header-content">
        <div class="header-text">
            <h1>
                <i class="fas fa-[icone-appropriado]"></i>
                [Título do Relatório]
            </h1>
            <p>[Descrição do relatório]</p>
        </div>
        <a href="{{ url_for('dashboard') }}" class="btn btn-secondary">
            <i class="fas fa-arrow-left"></i>
            Voltar ao Dashboard
        </a>
    </div>
</div>
<div class="table-responsive">
    <table id="tabela[NomeRelatorio]" class="table table-hover align-middle">
        <thead>
            <tr>
                <!-- Cabeçalhos das colunas -->
            </tr>
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
/* Header Styles - Padrão para todos os relatórios */
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

/* Responsive Header */
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
    font-size: 0.75rem;
    padding: 0.375rem 0.75rem;
    border-radius: 0.5rem;
    font-weight: 600;
}
```

#### Cores por Tipo de Relatório
- **Demandas Ativas**: Azul (`#007bff`)
- **Famílias Atendidas**: Verde (`#28a745`)
- **Cestas Entregues**: Laranja (`#fd7e14`)
- **Vulnerabilidade**: Vermelho (`#dc3545`)

### 4. JavaScript Específico

#### Estrutura Base

```javascript
document.addEventListener('DOMContentLoaded', function () {
    const dados = window.[nomeVariavelDados] || [];
    const tbody = document.querySelector('#tabela[NomeRelatorio] tbody');
    const paginacao = document.getElementById('paginacao[NomeRelatorio]');
    const registrosPorPagina = 15;
    let paginaAtual = 1;

    // Configuração dos filtros
    const filtros = {
        campo1: document.getElementById('filter-campo1'),
        campo2: document.getElementById('filter-campo2'),
        // ... outros campos
    };

    // Event listeners para filtros
    Object.values(filtros).forEach(input => {
        if (input) {
            input.addEventListener('input', () => {
                paginaAtual = 1;
                renderTable();
            });
        }
    });

    // Função de aplicação de filtros
    function aplicaFiltros(lista) {
        return lista.filter(item => {
            return (!filtros.campo1.value || item.campo1.toLowerCase().includes(filtros.campo1.value.toLowerCase())) &&
                   (!filtros.campo2.value || (item.campo2 || '').toLowerCase().includes(filtros.campo2.value.toLowerCase()));
                   // ... outros filtros
        });
    }

    // Renderização da tabela
    function renderTable() {
        const filtrados = aplicaFiltros(dados);
        const totalPaginas = Math.ceil(filtrados.length / registrosPorPagina) || 1;
        paginaAtual = Math.min(paginaAtual, totalPaginas);
        const inicio = (paginaAtual - 1) * registrosPorPagina;
        const paginaDados = filtrados.slice(inicio, inicio + registrosPorPagina);

        tbody.innerHTML = '';
        
        if (paginaDados.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="[numero_colunas]" class="text-center py-4">
                        <i class="fas fa-search text-muted"></i>
                        <p class="text-muted mb-0 mt-2">Nenhum registro encontrado</p>
                    </td>
                </tr>
            `;
        } else {
            paginaDados.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>[campo1 formatado]</td>
                    <td>[campo2 formatado]</td>
                    <!-- ... outras colunas -->
                `;
                tbody.appendChild(tr);
            });
        }

        renderPaginacao(filtrados.length);
    }

    // Funções de formatação específicas
    function formatarCPF(cpf) { /* implementação */ }
    function formatarTelefone(telefone) { /* implementação */ }
    function formatarData(data) { /* implementação */ }
    // ... outras funções de formatação

    renderTable();
});
```

## Modelos de Dados Principais

### Tabelas Frequentemente Utilizadas

#### familias
```sql
familia_id (PK)
nome_responsavel
cpf
data_nascimento
genero
estado_civil
rg
autoriza_uso_imagem
status_cadastro
data_hora_log_utc
```

#### enderecos
```sql
endereco_id (PK)
familia_id (FK)
cep
logradouro
numero
complemento
bairro
cidade
estado
ponto_referencia
```

#### contatos
```sql
contato_id (PK)
familia_id (FK)
telefone_principal
telefone_principal_whatsapp
telefone_principal_nome_contato
telefone_alternativo
email_responsavel
```

#### atendimentos
```sql
atendimento_id (PK)
familia_id (FK)
usuario_atendente_id
percepcao_necessidade
duracao_necessidade
motivo_duracao
cesta_entregue
data_hora_atendimento
```

### Padrões de JOIN Comuns

```sql
-- Join básico família + endereço + contato
FROM familias f
JOIN enderecos e ON f.familia_id = e.familia_id
JOIN contatos c ON f.familia_id = c.familia_id

-- Join com atendimentos (últimos 30 dias)
JOIN atendimentos a ON f.familia_id = a.familia_id
WHERE a.data_hora_atendimento >= NOW() - INTERVAL 30 DAY

-- Join com demandas ativas
JOIN demanda_familia df ON f.familia_id = df.familia_id
JOIN demanda_tipo dt ON df.demanda_tipo_id = dt.demanda_tipo_id
JOIN (
    SELECT de1.*
    FROM demanda_etapa de1
    INNER JOIN (
        SELECT demanda_id, MAX(etapa_id) AS max_etapa_id
        FROM demanda_etapa
        GROUP BY demanda_id
    ) m ON de1.demanda_id = m.demanda_id AND de1.etapa_id = m.max_etapa_id
) de ON df.demanda_id = de.demanda_id
```

## Formatações e Badges Comuns

### Formatação de Dados

#### CPF
```javascript
function formatarCPF(cpf) {
    if (!cpf) return '';
    const cleaned = cpf.replace(/\D/g, '');
    if (cleaned.length === 11) {
        return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }
    return cpf;
}
```

#### Telefone
```javascript
function formatarTelefone(telefone) {
    if (!telefone) return '';
    const cleaned = telefone.replace(/\D/g, '');
    if (cleaned.length === 11) {
        return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (cleaned.length === 10) {
        return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return telefone;
}
```

#### Data
```javascript
function formatarData(data) {
    if (!data) return '';
    const d = new Date(data);
    if (isNaN(d)) return data;
    return d.toLocaleDateString('pt-BR');
}
```

### Badges de Status

#### Percepção de Necessidade
- **Alta**: Fundo vermelho (`#dc3545`)
- **Média**: Fundo amarelo (`#ffc107`)
- **Baixa**: Fundo verde (`#28a745`)

#### Sim/Não (Cesta Entregue, etc.)
- **Sim**: Fundo verde (`#28a745`)
- **Não**: Fundo cinza (`#6c757d`)

```css
.badge-alta { background-color: #dc3545; color: white; }
.badge-media { background-color: #ffc107; color: #212529; }
.badge-baixa { background-color: #28a745; color: white; }
.badge-sim { background-color: #28a745; color: white; }
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

### Ícones Recomendados (Font Awesome)

- **Famílias**: `fas fa-users`
- **Atendimentos**: `fas fa-calendar-check`
- **Cestas**: `fas fa-box`
- **Demandas**: `fas fa-exclamation-triangle`
- **Vulnerabilidade**: `fas fa-heartbeat`
- **Localização**: `fas fa-map-marker-alt`
- **Download**: `fas fa-download`
- **Relatórios**: `fas fa-chart-line`

## Responsividade

### Breakpoints Padrão

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

## Checklist de Implementação

### ✅ Backend
- [ ] Criar rota em `main.py` com decorators `@login_required` e `@admin_required`
- [ ] Implementar query SQL com JOINs apropriados
- [ ] Converter resultados para lista de dicionários
- [ ] Passar dados para template via `render_template`

### ✅ Frontend
- [ ] Criar template HTML seguindo estrutura padrão
- [ ] Implementar cabeçalhos e filtros de tabela
- [ ] Criar CSS específico com ID único da tabela
- [ ] Implementar JavaScript com filtros e paginação
- [ ] Adicionar formatações específicas do relatório

### ✅ Integração
- [ ] Atualizar link no dashboard principal
- [ ] Testar navegação entre páginas
- [ ] Verificar responsividade em diferentes tamanhos de tela
- [ ] Validar formatação de dados e badges

## Exemplos de Queries por Tipo de Relatório

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

## Considerações de Performance

### Índices Recomendados
- `familia_id` em todas as tabelas relacionadas
- `data_hora_atendimento` para filtros temporais
- `status` e `prioridade` para filtros de demandas
- `bairro` e `cidade` para filtros geográficos

### Paginação
- Manter padrão de 15 registros por página
- Implementar paginação no frontend (não no backend)
- Mostrar indicador de "Nenhum registro encontrado"

## Manutenção e Evolução

### Versionamento
- Manter comentários nas queries SQL explicando a lógica
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