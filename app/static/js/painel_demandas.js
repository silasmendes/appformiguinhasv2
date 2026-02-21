document.addEventListener('DOMContentLoaded', function () {
    const dados = window.painelDemandas || [];
    const container = document.getElementById('familiasContainer');
    const paginacao = document.getElementById('paginacaoPainel');
    const semResultados = document.getElementById('semResultados');
    const familiasPorPagina = 10;
    let paginaAtual = 1;

    // --- Classificação de status ---
    const STATUS_CONCLUIDA = ['concluída', 'concluida'];
    const STATUS_CANCELADA = ['cancelada'];

    function isPendente(status) {
        if (!status) return true;
        const s = status.toLowerCase();
        return !STATUS_CONCLUIDA.includes(s) && !STATUS_CANCELADA.includes(s);
    }
    function isConcluida(status) {
        return STATUS_CONCLUIDA.includes((status || '').toLowerCase());
    }
    function isCancelada(status) {
        return STATUS_CANCELADA.includes((status || '').toLowerCase());
    }

    // --- Agrupar por família ---
    function agruparPorFamilia(lista) {
        const mapa = {};
        lista.forEach(d => {
            const fid = d.familia_id;
            if (!mapa[fid]) {
                mapa[fid] = {
                    familia_id: fid,
                    nome_responsavel: d.nome_responsavel,
                    cpf: d.cpf,
                    bairro: d.bairro,
                    demandas: []
                };
            }
            mapa[fid].demandas.push(d);
        });
        return Object.values(mapa);
    }

    // --- Contadores ---
    function contarStatus(demandas) {
        let pendentes = 0, concluidas = 0, canceladas = 0;
        demandas.forEach(d => {
            if (isConcluida(d.status_atual)) concluidas++;
            else if (isCancelada(d.status_atual)) canceladas++;
            else pendentes++;
        });
        return { pendentes, concluidas, canceladas, total: demandas.length };
    }

    // --- Filtros ---
    const filtroFamilia = document.getElementById('filtroFamilia');
    const filtroBairro = document.getElementById('filtroBairro');
    const filtroStatus = document.getElementById('filtroStatus');
    const filtroPrioridade = document.getElementById('filtroPrioridade');
    const filtroTipo = document.getElementById('filtroTipo');
    const limparFiltrosBtn = document.getElementById('limparFiltros');

    [filtroFamilia, filtroBairro, filtroTipo].forEach(el => {
        if (el) el.addEventListener('input', () => { paginaAtual = 1; render(); });
    });
    [filtroStatus, filtroPrioridade].forEach(el => {
        if (el) el.addEventListener('change', () => { paginaAtual = 1; render(); });
    });
    if (limparFiltrosBtn) {
        limparFiltrosBtn.addEventListener('click', () => {
            filtroFamilia.value = '';
            filtroBairro.value = '';
            filtroStatus.value = '';
            filtroPrioridade.value = '';
            filtroTipo.value = '';
            paginaAtual = 1;
            render();
        });
    }

    function aplicarFiltros(familias) {
        const busca = (filtroFamilia.value || '').toLowerCase();
        const bairro = (filtroBairro.value || '').toLowerCase();
        const statusFiltro = (filtroStatus.value || '').toLowerCase();
        const prioridade = (filtroPrioridade.value || '');
        const tipo = (filtroTipo.value || '').toLowerCase();

        return familias.map(fam => {
            // Filtrar família por nome/cpf e bairro
            if (busca && !fam.nome_responsavel.toLowerCase().includes(busca) && !(fam.cpf || '').toLowerCase().includes(busca)) {
                return null;
            }
            if (bairro && !(fam.bairro || '').toLowerCase().includes(bairro)) {
                return null;
            }

            // Filtrar demandas por status/prioridade/tipo
            let demFiltradas = fam.demandas;
            if (statusFiltro === 'pendente') {
                demFiltradas = demFiltradas.filter(d => isPendente(d.status_atual));
            } else if (statusFiltro === 'concluida') {
                demFiltradas = demFiltradas.filter(d => isConcluida(d.status_atual));
            } else if (statusFiltro === 'cancelada') {
                demFiltradas = demFiltradas.filter(d => isCancelada(d.status_atual));
            }
            if (prioridade) {
                demFiltradas = demFiltradas.filter(d => (d.prioridade || '') === prioridade);
            }
            if (tipo) {
                demFiltradas = demFiltradas.filter(d => (d.demanda_tipo_nome || '').toLowerCase().includes(tipo));
            }

            if (demFiltradas.length === 0) return null;

            return { ...fam, demandas: demFiltradas };
        }).filter(Boolean);
    }

    // --- KPIs ---
    function atualizarKPIs(familiasFiltradas) {
        let total = 0, pendentes = 0, concluidas = 0, canceladas = 0;
        familiasFiltradas.forEach(fam => {
            const c = contarStatus(fam.demandas);
            total += c.total;
            pendentes += c.pendentes;
            concluidas += c.concluidas;
            canceladas += c.canceladas;
        });
        document.getElementById('kpiTotal').textContent = total;
        document.getElementById('kpiPendentes').textContent = pendentes;
        document.getElementById('kpiConcluidas').textContent = concluidas;
        document.getElementById('kpiCanceladas').textContent = canceladas;
        document.getElementById('kpiFamilias').textContent = familiasFiltradas.length;
    }

    // --- Formatação ---
    function formatarData(data) {
        if (!data) return '';
        const d = new Date(data);
        if (isNaN(d)) return data;
        return d.toLocaleDateString('pt-BR');
    }

    function formatarDataHora(data) {
        if (!data) return '';
        const d = new Date(data);
        if (isNaN(d)) return data;
        return d.toLocaleDateString('pt-BR') + ' ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }

    function getStatusClass(status) {
        if (!status) return 'em-analise';
        const s = status.toLowerCase();
        if (s === 'em análise') return 'em-analise';
        if (s === 'em andamento') return 'em-andamento';
        if (s === 'encaminhada') return 'encaminhada';
        if (s.includes('aguardando')) return 'aguardando';
        if (s === 'suspensa') return 'suspensa';
        if (s === 'cancelada') return 'cancelada';
        if (s === 'concluída' || s === 'concluida') return 'concluida';
        return 'em-analise';
    }

    function formatarStatus(status) {
        if (!status) return '<span class="status-badge em-analise">Em análise</span>';
        return `<span class="status-badge ${getStatusClass(status)}">${status}</span>`;
    }

    function formatarPrioridade(prioridade) {
        if (!prioridade) return '';
        const p = prioridade.toLowerCase();
        let classe = 'media';
        if (p.includes('alta')) classe = 'alta';
        else if (p.includes('baixa')) classe = 'baixa';
        return `<span class="prioridade-badge ${classe}">${prioridade}</span>`;
    }

    function getIniciais(nome) {
        if (!nome) return '?';
        const partes = nome.trim().split(' ');
        if (partes.length === 1) return partes[0][0].toUpperCase();
        return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
    }

    // --- Render da família ---
    function renderFamilia(fam, index) {
        const counts = contarStatus(fam.demandas);
        const total = counts.total || 1;
        const pctConcluida = (counts.concluidas / total * 100).toFixed(1);
        const pctPendente = (counts.pendentes / total * 100).toFixed(1);
        const pctCancelada = (counts.canceladas / total * 100).toFixed(1);

        const card = document.createElement('div');
        card.className = 'familia-card';
        card.innerHTML = `
            <div class="familia-header" data-index="${index}">
                <div class="familia-info">
                    <div class="familia-avatar">${getIniciais(fam.nome_responsavel)}</div>
                    <div>
                        <div class="familia-nome">${fam.nome_responsavel}</div>
                        <div class="familia-meta">
                            ${fam.cpf ? `CPF: ${fam.cpf}` : ''}
                            ${fam.bairro ? ` | ${fam.bairro}` : ''}
                            | ${counts.total} demanda${counts.total > 1 ? 's' : ''}
                        </div>
                    </div>
                </div>
                <div class="familia-badges">
                    ${counts.pendentes > 0 ? `<span class="badge-count pendente"><i class="fas fa-hourglass-half"></i> ${counts.pendentes} pendente${counts.pendentes > 1 ? 's' : ''}</span>` : ''}
                    ${counts.concluidas > 0 ? `<span class="badge-count concluida"><i class="fas fa-check"></i> ${counts.concluidas} concluída${counts.concluidas > 1 ? 's' : ''}</span>` : ''}
                    ${counts.canceladas > 0 ? `<span class="badge-count cancelada"><i class="fas fa-times"></i> ${counts.canceladas}</span>` : ''}
                    <i class="fas fa-chevron-down familia-toggle"></i>
                </div>
            </div>
            <div class="familia-progress">
                <div class="progress-segment concluida" style="width:${pctConcluida}%"></div>
                <div class="progress-segment pendente" style="width:${pctPendente}%"></div>
                <div class="progress-segment cancelada" style="width:${pctCancelada}%"></div>
            </div>
            <div class="familia-demandas" id="demandas-${index}">
                <table class="demandas-table">
                    <thead>
                        <tr>
                            <th>Descrição</th>
                            <th>Tipo</th>
                            <th>Prioridade</th>
                            <th>Status</th>
                            <th>Identificação</th>
                            <th>Atualização</th>
                            <th>Observação</th>
                            <th class="text-center">Ciclo</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${fam.demandas.map(d => `
                            <tr>
                                <td>${d.descricao || ''}</td>
                                <td>${d.demanda_tipo_nome || ''}</td>
                                <td>${formatarPrioridade(d.prioridade)}</td>
                                <td>${formatarStatus(d.status_atual)}</td>
                                <td>${formatarData(d.data_identificacao)}</td>
                                <td>${formatarData(d.data_atualizacao)}</td>
                                <td>${d.observacao || ''}</td>
                                <td class="text-center">
                                    <button class="btn-timeline" 
                                            data-demanda='${JSON.stringify(d).replace(/'/g, "&#39;")}'
                                            title="Ver ciclo completo">
                                        <i class="fas fa-history"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        // Toggle expand/collapse
        const header = card.querySelector('.familia-header');
        header.addEventListener('click', () => {
            const body = card.querySelector('.familia-demandas');
            const toggle = card.querySelector('.familia-toggle');
            body.classList.toggle('show');
            toggle.classList.toggle('expanded');
        });

        // Timeline buttons
        card.querySelectorAll('.btn-timeline').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const demanda = JSON.parse(btn.dataset.demanda);
                abrirModalHistorico(demanda, fam);
            });
        });

        return card;
    }

    // --- Modal de histórico ---
    function abrirModalHistorico(demanda, familia) {
        const infoDiv = document.getElementById('modalDemandaInfo');
        const timelineDiv = document.getElementById('modalTimeline');

        infoDiv.innerHTML = `
            <div class="demanda-info-card">
                <div class="info-row"><span class="info-label">Família:</span> ${familia.nome_responsavel}</div>
                <div class="info-row"><span class="info-label">Demanda:</span> ${demanda.descricao || 'Sem descrição'}</div>
                <div class="info-row"><span class="info-label">Tipo:</span> ${demanda.demanda_tipo_nome || ''}</div>
                <div class="info-row"><span class="info-label">Prioridade:</span> ${formatarPrioridade(demanda.prioridade)}</div>
                <div class="info-row"><span class="info-label">Status atual:</span> ${formatarStatus(demanda.status_atual)}</div>
                <div class="info-row"><span class="info-label">Identificação:</span> ${formatarData(demanda.data_identificacao)}</div>
            </div>
        `;

        const historico = demanda.historico || [];
        if (historico.length === 0) {
            timelineDiv.innerHTML = '<p class="text-muted">Nenhuma transição registrada.</p>';
        } else {
            timelineDiv.innerHTML = historico.map((h, i) => {
                let dotClass = 'middle';
                if (i === 0) dotClass = 'first';
                if (i === historico.length - 1) {
                    if (isCancelada(h.status_atual)) dotClass = 'cancelada';
                    else if (isConcluida(h.status_atual)) dotClass = 'last';
                }
                return `
                    <div class="timeline-item">
                        <div class="timeline-dot ${dotClass}"></div>
                        <div class="timeline-content">
                            <div class="timeline-status">${formatarStatus(h.status_atual)}</div>
                            <div class="timeline-meta">
                                <span><i class="fas fa-calendar-alt me-1"></i>${formatarDataHora(h.data_atualizacao)}</span>
                                ${h.atendente ? `<span><i class="fas fa-user me-1"></i>${h.atendente}</span>` : ''}
                            </div>
                            ${h.observacao ? `<div class="timeline-obs">"${h.observacao}"</div>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }

        const btnGerenciar = document.getElementById('btnGerenciarDemandas');
        if (btnGerenciar) {
            btnGerenciar.href = `/gerenciar_demandas/${familia.familia_id}`;
        }

        const modal = new bootstrap.Modal(document.getElementById('modalHistorico'));
        modal.show();
    }

    // --- Paginação ---
    function renderPaginacao(total) {
        paginacao.innerHTML = '';
        if (total <= 1) return;

        // Prev
        const prevLi = document.createElement('li');
        prevLi.className = 'page-item' + (paginaAtual === 1 ? ' disabled' : '');
        prevLi.innerHTML = '<a class="page-link" href="#">&laquo;</a>';
        prevLi.querySelector('a').addEventListener('click', e => {
            e.preventDefault();
            if (paginaAtual > 1) { paginaAtual--; render(); }
        });
        paginacao.appendChild(prevLi);

        for (let i = 1; i <= total; i++) {
            const li = document.createElement('li');
            li.className = 'page-item' + (i === paginaAtual ? ' active' : '');
            const a = document.createElement('a');
            a.href = '#';
            a.className = 'page-link';
            a.textContent = i;
            a.addEventListener('click', e => {
                e.preventDefault();
                paginaAtual = i;
                render();
            });
            li.appendChild(a);
            paginacao.appendChild(li);
        }

        // Next
        const nextLi = document.createElement('li');
        nextLi.className = 'page-item' + (paginaAtual === total ? ' disabled' : '');
        nextLi.innerHTML = '<a class="page-link" href="#">&raquo;</a>';
        nextLi.querySelector('a').addEventListener('click', e => {
            e.preventDefault();
            if (paginaAtual < total) { paginaAtual++; render(); }
        });
        paginacao.appendChild(nextLi);
    }

    // --- Download ---
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        const downloadUrl = downloadBtn.dataset.url;
        downloadBtn.addEventListener('click', () => {
            fetch(downloadUrl, {
                method: 'GET',
                headers: { 'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
            })
            .then(resp => {
                if (!resp.ok) throw new Error('Erro ao gerar arquivo');
                return resp.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                const now = new Date();
                const dateStr = now.getFullYear() + '_' + String(now.getMonth() + 1).padStart(2, '0') + '_' + String(now.getDate()).padStart(2, '0');
                link.href = url;
                link.download = `painel_demandas_${dateStr}.xlsx`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            })
            .catch(err => console.error('Erro no download:', err));
        });
    }

    // --- Render principal ---
    function render() {
        const familias = agruparPorFamilia(dados);
        const filtradas = aplicarFiltros(familias);
        atualizarKPIs(filtradas);

        const totalPaginas = Math.ceil(filtradas.length / familiasPorPagina) || 1;
        paginaAtual = Math.min(paginaAtual, totalPaginas);
        const inicio = (paginaAtual - 1) * familiasPorPagina;
        const paginaDados = filtradas.slice(inicio, inicio + familiasPorPagina);

        container.innerHTML = '';
        if (filtradas.length === 0) {
            semResultados.classList.remove('d-none');
        } else {
            semResultados.classList.add('d-none');
            paginaDados.forEach((fam, i) => {
                container.appendChild(renderFamilia(fam, inicio + i));
            });
        }

        renderPaginacao(totalPaginas);
    }

    render();
});
