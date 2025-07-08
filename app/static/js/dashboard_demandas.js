document.addEventListener('DOMContentLoaded', function () {
    const dados = window.demandasAtivas || [];
    const tbody = document.querySelector('#tabelaDemandasAtivas tbody');
    const paginacao = document.getElementById('paginacaoDemandas');
    const registrosPorPagina = 15;
    let paginaAtual = 1;

    const filtros = {
        nome: document.getElementById('filter-nome'),
        cpf: document.getElementById('filter-cpf'),
        bairro: document.getElementById('filter-bairro'),
        descricao: document.getElementById('filter-descricao'),
        tipo: document.getElementById('filter-tipo'),
        status: document.getElementById('filter-status'),
        prioridade: document.getElementById('filter-prioridade')
    };

    Object.values(filtros).forEach(input => {
        if (input) {
            input.addEventListener('input', () => {
                paginaAtual = 1;
                renderTable();
            });
        }
    });

    function aplicaFiltros(lista) {
        return lista.filter(item => {
            return (!filtros.nome.value || item.nome_responsavel.toLowerCase().includes(filtros.nome.value.toLowerCase())) &&
                   (!filtros.cpf.value || (item.cpf || '').toLowerCase().includes(filtros.cpf.value.toLowerCase())) &&
                   (!filtros.bairro.value || (item.bairro || '').toLowerCase().includes(filtros.bairro.value.toLowerCase())) &&
                   (!filtros.descricao.value || (item.descricao || '').toLowerCase().includes(filtros.descricao.value.toLowerCase())) &&
                   (!filtros.tipo.value || (item.demanda_tipo_nome || '').toLowerCase().includes(filtros.tipo.value.toLowerCase())) &&
                   (!filtros.status.value || (item.status_atual || '').toLowerCase().includes(filtros.status.value.toLowerCase())) &&
                   (!filtros.prioridade.value || (item.prioridade || '').toLowerCase().includes(filtros.prioridade.value.toLowerCase()));
        });
    }

    function renderTable() {
        const filtrados = aplicaFiltros(dados);
        const totalPaginas = Math.ceil(filtrados.length / registrosPorPagina) || 1;
        paginaAtual = Math.min(paginaAtual, totalPaginas);
        const inicio = (paginaAtual - 1) * registrosPorPagina;
        const paginaDados = filtrados.slice(inicio, inicio + registrosPorPagina);

        tbody.innerHTML = '';
        paginaDados.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><a href="/gerenciar_demandas/${item.familia_id}">${item.nome_responsavel}</a></td>
                <td>${item.cpf || ''}</td>
                <td>${item.bairro || ''}</td>
                <td>${item.descricao || ''}</td>
                <td>${formatarData(item.data_identificacao)}</td>
                <td>${item.demanda_tipo_nome || ''}</td>
                <td>${item.status_atual || ''}</td>
                <td>${item.prioridade || ''}</td>
                <td>${formatarData(item.data_atualizacao)}</td>
                <td>${item.observacao || ''}</td>`;
            tbody.appendChild(tr);
        });

        renderPaginacao(totalPaginas);
    }

    function renderPaginacao(total) {
        paginacao.innerHTML = '';
        for (let i = 1; i <= total; i++) {
            const li = document.createElement('li');
            li.className = 'page-item' + (i === paginaAtual ? ' active' : '');
            const a = document.createElement('a');
            a.href = '#';
            a.className = 'page-link';
            a.textContent = i;
            a.addEventListener('click', (e) => {
                e.preventDefault();
                paginaAtual = i;
                renderTable();
            });
            li.appendChild(a);
            paginacao.appendChild(li);
        }
    }

    function formatarData(data) {
        if (!data) return '';
        const d = new Date(data);
        if (isNaN(d)) return data;
        return d.toLocaleDateString('pt-BR');
    }

    renderTable();
});
