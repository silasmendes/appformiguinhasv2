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
                link.download = `demandas_ativas_${dateStr}.xlsx`;
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
                <td><a href="/gerenciar_demandas/${item.familia_id}" style="color: #007bff; text-decoration: none; font-weight: 500;">${item.nome_responsavel}</a></td>
                <td>${item.cpf || ''}</td>
                <td>${item.bairro || ''}</td>
                <td>${item.descricao || ''}</td>
                <td>${formatarData(item.data_identificacao)}</td>
                <td>${item.demanda_tipo_nome || ''}</td>
                <td>${formatarStatus(item.status_atual)}</td>
                <td>${formatarPrioridade(item.prioridade)}</td>
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

    function formatarStatus(status) {
        if (!status) return '';
        const statusLower = status.toLowerCase();
        let classe = 'status-badge';
        
        if (statusLower.includes('ativo') || statusLower.includes('em andamento')) {
            classe += ' ativo';
        } else if (statusLower.includes('pendente') || statusLower.includes('aguardando')) {
            classe += ' pendente';
        } else if (statusLower.includes('concluído') || statusLower.includes('finalizado')) {
            classe += ' concluido';
        }
        
        return `<span class="${classe}">${status}</span>`;
    }

    function formatarPrioridade(prioridade) {
        if (!prioridade) return '';
        const prioridadeLower = prioridade.toLowerCase();
        let classe = 'prioridade-badge';
        
        if (prioridadeLower.includes('alta') || prioridadeLower.includes('urgente')) {
            classe += ' alta';
        } else if (prioridadeLower.includes('média') || prioridadeLower.includes('media') || prioridadeLower.includes('normal')) {
            classe += ' media';
        } else if (prioridadeLower.includes('baixa') || prioridadeLower.includes('baixo')) {
            classe += ' baixa';
        }
        
        return `<span class="${classe}">${prioridade}</span>`;
    }

    renderTable();
});
