document.addEventListener('DOMContentLoaded', function () {
    // Funcionalidade do botão de download
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        const downloadUrl = downloadBtn.dataset.url;
        downloadBtn.addEventListener('click', () => {
            fetch(downloadUrl, {
                method: 'GET',
                headers: {
                    'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao gerar arquivo');
                }
                return response.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                const now = new Date();
                const dateStr = now.getFullYear() + '_' + String(now.getMonth() + 1).padStart(2, '0') + '_' + String(now.getDate()).padStart(2, '0');
                link.href = url;
                link.download = `familias_sem_atendimento_recente_${dateStr}.xlsx`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Erro no download:', error);
            });
        });
    }

    const dados = window.familiasSemAtendimentoData || [];
    const tbody = document.querySelector('#tabelaFamiliasSemAtendimento tbody');
    const paginacao = document.getElementById('paginacaoFamiliasSemAtendimento');
    const registrosPorPagina = 15;
    let paginaAtual = 1;

    const filtros = {
        nome: document.getElementById('filter-nome'),
        cpf: document.getElementById('filter-cpf'),
        bairro: document.getElementById('filter-bairro'),
        telefone: document.getElementById('filter-telefone'),
        email: document.getElementById('filter-email'),
        cadastro: document.getElementById('filter-cadastro'),
        atendimento: document.getElementById('filter-atendimento')
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
                   (!filtros.cadastro.value || formatarData(item.data_cadastro).toLowerCase().includes(filtros.cadastro.value.toLowerCase())) &&
                   (!filtros.atendimento.value || formatarUltimoAtendimento(item.ultima_data_atendimento).toLowerCase().includes(filtros.atendimento.value.toLowerCase()));
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
                    <td colspan="7" class="text-center text-muted py-4">
                        <i class="fas fa-search mb-3" style="font-size: 2rem; opacity: 0.5;"></i>
                        <p class="mb-0">Nenhuma família encontrada</p>
                    </td>
                </tr>
            `;
        } else {
            paginaDados.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><a href="/familia/${item.familia_id}" class="text-decoration-none fw-semibold">${item.nome_responsavel || 'N/A'}</a></td>
                    <td>${item.cpf || 'N/A'}</td>
                    <td>${item.bairro || 'N/A'}</td>
                    <td>${item.telefone_principal || 'N/A'}</td>
                    <td>${item.email_responsavel || 'N/A'}</td>
                    <td>${formatarData(item.data_cadastro)}</td>
                    <td>${formatarUltimoAtendimento(item.ultima_data_atendimento)}</td>
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

    function formatarData(data) {
        if (!data) return 'N/A';
        try {
            return new Date(data).toLocaleDateString('pt-BR');
        } catch {
            return 'N/A';
        }
    }

    function formatarUltimoAtendimento(data) {
        if (!data) return 'Nunca atendido';
        try {
            return new Date(data).toLocaleDateString('pt-BR');
        } catch {
            return 'N/A';
        }
    }

    // Initial render
    renderTable();
});