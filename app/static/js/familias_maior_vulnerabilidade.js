document.addEventListener('DOMContentLoaded', function () {
    const dados = window.familiasMaiorVulnerabilidadeData || [];
    const tbody = document.querySelector('#tabelaFamiliasMaiorVulnerabilidade tbody');
    const paginacao = document.getElementById('paginacaoFamiliasMaiorVulnerabilidade');
    const registrosPorPagina = 15;
    let paginaAtual = 1;

    const filtros = {
        nome: document.getElementById('filter-nome'),
        cpf: document.getElementById('filter-cpf'),
        bairro: document.getElementById('filter-bairro'),
        telefone: document.getElementById('filter-telefone'),
        email: document.getElementById('filter-email'),
        percepcao: document.getElementById('filter-percepcao'),
        cesta: document.getElementById('filter-cesta'),
        data: document.getElementById('filter-data'),
        motivo: document.getElementById('filter-motivo')
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
                   (!filtros.telefone.value || (item.telefone_principal || '').toLowerCase().includes(filtros.telefone.value.toLowerCase())) &&
                   (!filtros.email.value || (item.email_responsavel || '').toLowerCase().includes(filtros.email.value.toLowerCase())) &&
                   (!filtros.percepcao.value || formatarPercepcao(item.percepcao_necessidade).toLowerCase().includes(filtros.percepcao.value.toLowerCase())) &&
                   (!filtros.cesta.value || formatarCesta(item.cesta_entregue).toLowerCase().includes(filtros.cesta.value.toLowerCase())) &&
                   (!filtros.data.value || formatarData(item.data_hora_atendimento).toLowerCase().includes(filtros.data.value.toLowerCase())) &&
                   (!filtros.motivo.value || (item.motivo_duracao || '').toLowerCase().includes(filtros.motivo.value.toLowerCase()));
        });
    }

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
                    <td colspan="9" class="text-center text-muted py-4">
                        <i class="fas fa-search mb-3" style="font-size: 2rem; opacity: 0.5;"></i>
                        <p class="mb-0">Nenhuma família encontrada</p>
                    </td>
                </tr>
            `;
        } else {
            paginaDados.forEach(item => {
                const tr = document.createElement('tr');
                tr.className = 'familia-critica';
                
                tr.innerHTML = `
                    <td><a href="/familia/${item.familia_id}" class="text-decoration-none fw-semibold prioridade-critica">${item.nome_responsavel || 'N/A'}</a></td>
                    <td>${formatarCPF(item.cpf)}</td>
                    <td>${item.bairro || 'N/A'}</td>
                    <td>${formatarTelefone(item.telefone_principal)}</td>
                    <td>${item.email_responsavel || 'N/A'}</td>
                    <td>${formatarPercepcao(item.percepcao_necessidade)}</td>
                    <td>${formatarCesta(item.cesta_entregue)}</td>
                    <td>${formatarData(item.data_hora_atendimento)}</td>
                    <td class="motivo-col" title="${item.motivo_duracao || 'N/A'}">${item.motivo_duracao || 'N/A'}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        renderPagination(filtrados.length);
    }

    function renderPagination(totalRegistros) {
        const totalPaginas = Math.ceil(totalRegistros / registrosPorPagina) || 1;
        let html = '';

        // Previous button
        if (paginaAtual > 1) {
            html += `<li class="page-item">
                        <a class="page-link" href="#" data-page="${paginaAtual - 1}">Anterior</a>
                     </li>`;
        }

        // Page numbers
        for (let i = 1; i <= totalPaginas; i++) {
            if (i === paginaAtual) {
                html += `<li class="page-item active">
                            <span class="page-link">${i}</span>
                         </li>`;
            } else if (i === 1 || i === totalPaginas || (i >= paginaAtual - 2 && i <= paginaAtual + 2)) {
                html += `<li class="page-item">
                            <a class="page-link" href="#" data-page="${i}">${i}</a>
                         </li>`;
            } else if (i === paginaAtual - 3 || i === paginaAtual + 3) {
                html += `<li class="page-item disabled">
                            <span class="page-link">...</span>
                         </li>`;
            }
        }

        // Next button
        if (paginaAtual < totalPaginas) {
            html += `<li class="page-item">
                        <a class="page-link" href="#" data-page="${paginaAtual + 1}">Próximo</a>
                     </li>`;
        }

        paginacao.innerHTML = html;

        // Add event listeners to pagination links
        paginacao.querySelectorAll('a[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                paginaAtual = parseInt(e.target.getAttribute('data-page'));
                renderTable();
            });
        });
    }

    function formatarCPF(cpf) {
        if (!cpf) return 'N/A';
        // Remove caracteres não numéricos
        const apenasNumeros = cpf.replace(/\D/g, '');
        if (apenasNumeros.length === 11) {
            return apenasNumeros.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        }
        return cpf;
    }

    function formatarTelefone(telefone) {
        if (!telefone) return 'N/A';
        // Remove caracteres não numéricos
        const apenasNumeros = telefone.replace(/\D/g, '');
        if (apenasNumeros.length === 11) {
            return apenasNumeros.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (apenasNumeros.length === 10) {
            return apenasNumeros.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        }
        return telefone;
    }

    function formatarData(data) {
        if (!data) return 'N/A';
        try {
            return new Date(data).toLocaleDateString('pt-BR');
        } catch {
            return 'N/A';
        }
    }

    function formatarPercepcao(percepcao) {
        if (!percepcao) return 'N/A';
        const classes = {
            'Alta': 'badge-percepcao-alta',
            'Média': 'badge badge-warning',
            'Baixa': 'badge badge-success'
        };
        const className = classes[percepcao] || 'badge badge-secondary';
        return `<span class="badge ${className}">${percepcao}</span>`;
    }

    function formatarCesta(cesta) {
        if (cesta === null || cesta === undefined) return '<span class="badge badge-secondary">N/A</span>';
        
        if (cesta === 1 || cesta === true || cesta === 'Sim' || cesta === 'sim') {
            return '<span class="badge badge-cesta-sim">Sim</span>';
        } else {
            return '<span class="badge badge-cesta-nao">Não</span>';
        }
    }

    // Initial render
    renderTable();
});