document.addEventListener('DOMContentLoaded', function () {
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
                link.download = `familias_atendidas_30_dias_${dateStr}.xlsx`;
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

    const dados = window.familiasAtendidas || [];
    const tbody = document.querySelector('#tabelaFamiliasAtendidas tbody');
    const paginacao = document.getElementById('paginacaoFamiliasAtendidas');
    const registrosPorPagina = 15;
    let paginaAtual = 1;

    const filtros = {
        nome: document.getElementById('filter-nome'),
        cpf: document.getElementById('filter-cpf'),
        bairro: document.getElementById('filter-bairro'),
        telefone: document.getElementById('filter-telefone'),
        email: document.getElementById('filter-email'),
        percepcao: document.getElementById('filter-percepcao'),
        cesta: document.getElementById('filter-cesta')
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
                   (!filtros.percepcao.value || (item.percepcao_necessidade || '').toLowerCase().includes(filtros.percepcao.value.toLowerCase())) &&
                   (!filtros.cesta.value || formatarCesta(item.cesta_entregue).toLowerCase().includes(filtros.cesta.value.toLowerCase()));
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
                    <td colspan="7" class="text-center py-4">
                        <i class="fas fa-search text-muted"></i>
                        <p class="text-muted mb-0 mt-2">Nenhuma família encontrada com os filtros aplicados</p>
                    </td>
                </tr>
            `;
        } else {
            paginaDados.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><a href="/familia/${item.familia_id}" style="color: #28a745; text-decoration: none; font-weight: 500;">${item.nome_responsavel}</a></td>
                    <td>${formatarCPF(item.cpf)}</td>
                    <td>${item.bairro || ''}</td>
                    <td>${formatarTelefone(item.telefone_principal)}</td>
                    <td>${item.email_responsavel || ''}</td>
                    <td>${formatarPercepcao(item.percepcao_necessidade)}</td>
                    <td>${formatarCesta(item.cesta_entregue)}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        renderPaginacao(filtrados.length);
    }

    function renderPaginacao(totalItens) {
        const totalPaginas = Math.ceil(totalItens / registrosPorPagina) || 1;
        paginacao.innerHTML = '';

        if (totalPaginas <= 1) return;

        // Primeira página
        if (paginaAtual > 1) {
            const li = document.createElement('li');
            li.className = 'page-item';
            const a = document.createElement('a');
            a.className = 'page-link';
            a.href = '#';
            a.innerHTML = '&laquo;';
            a.onclick = (e) => { e.preventDefault(); paginaAtual = 1; renderTable(); };
            li.appendChild(a);
            paginacao.appendChild(li);
        }

        // Páginas visíveis
        const inicio = Math.max(1, paginaAtual - 2);
        const fim = Math.min(totalPaginas, paginaAtual + 2);

        for (let i = inicio; i <= fim; i++) {
            const li = document.createElement('li');
            li.className = i === paginaAtual ? 'page-item active' : 'page-item';
            const a = document.createElement('a');
            a.className = 'page-link';
            a.href = '#';
            a.textContent = i;
            a.onclick = (e) => { e.preventDefault(); paginaAtual = i; renderTable(); };
            li.appendChild(a);
            paginacao.appendChild(li);
        }

        // Última página
        if (paginaAtual < totalPaginas) {
            const li = document.createElement('li');
            li.className = 'page-item';
            const a = document.createElement('a');
            a.className = 'page-link';
            a.href = '#';
            a.innerHTML = '&raquo;';
            a.onclick = (e) => { e.preventDefault(); paginaAtual = totalPaginas; renderTable(); };
            li.appendChild(a);
            paginacao.appendChild(li);
        }
    }

    function formatarCPF(cpf) {
        if (!cpf) return '';
        // Remove caracteres não numéricos
        const cleaned = cpf.replace(/\D/g, '');
        // Aplica máscara XXX.XXX.XXX-XX
        if (cleaned.length === 11) {
            return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        }
        return cpf;
    }

    function formatarTelefone(telefone) {
        if (!telefone) return '';
        // Remove caracteres não numéricos
        const cleaned = telefone.replace(/\D/g, '');
        // Aplica máscara (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
        if (cleaned.length === 11) {
            return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (cleaned.length === 10) {
            return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        }
        return telefone;
    }

    function formatarPercepcao(percepcao) {
        if (!percepcao) return '';
        const percepcaoLower = percepcao.toLowerCase();
        let classe = 'badge-percepcao';
        
        if (percepcaoLower === 'alta') {
            classe += ' badge-alta';
        } else if (percepcaoLower === 'media' || percepcaoLower === 'média') {
            classe += ' badge-media';
        } else if (percepcaoLower === 'baixa') {
            classe += ' badge-baixa';
        }
        
        return `<span class="${classe}">${percepcao}</span>`;
    }

    function formatarCesta(cestaEntregue) {
        if (cestaEntregue === null || cestaEntregue === undefined) return '';
        
        const entregue = cestaEntregue === 1 || cestaEntregue === true;
        const texto = entregue ? 'Sim' : 'Não';
        const classe = entregue ? 'badge-cesta badge-sim' : 'badge-cesta badge-nao';
        
        return `<span class="${classe}">${texto}</span>`;
    }

    renderTable();
});