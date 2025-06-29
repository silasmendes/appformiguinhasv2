// JS para etapa 10 - outras necessidades informadas

document.addEventListener('DOMContentLoaded', function () {
    console.log('Estado atual da sessão:', window.sessionCadastro);
    const hiddenIdInput = document.getElementById('familia_id_hidden');
    if (window.sessionFamiliaId === null) {
        sessionStorage.removeItem('familia_id');
        if (hiddenIdInput) hiddenIdInput.value = '';
    } else if (window.sessionFamiliaId) {
        sessionStorage.setItem('familia_id', window.sessionFamiliaId);
        if (hiddenIdInput) hiddenIdInput.value = window.sessionFamiliaId;
    }

    const lista = document.getElementById('necessidadesLista');
    const btnAdicionar = document.getElementById('adicionarNecessidade');
    const btnProxima = document.getElementById('btnProxima');
    const nenhuma = document.getElementById('nenhumaNecessidade');
    const form = document.getElementById('formEtapa10');

    const secDemandas = document.getElementById('demandasAtivasSection');
    const tabelaBody = document.querySelector('#tabelaDemandasAtivas tbody');
    const modal = document.getElementById('modalAtualizarDemanda');
    const fecharModalBtn = document.getElementById('fecharModalDemanda');
    const salvarModalBtn = document.getElementById('salvarAtualizacaoDemanda');
    const modalStatus = document.getElementById('modal_status');
    const modalObs = document.getElementById('modal_observacao');
    const modalDesc = document.getElementById('modal_demanda_descricao');
    const modalId = document.getElementById('modal_demanda_id');

    function atualizarNumeracao() {
        const itens = lista.querySelectorAll('.necessidade-item');
        itens.forEach((item, index) => {
            const labelDesc = item.querySelector('label.form-label');
            if (labelDesc) {
                labelDesc.innerHTML = `Descrição da necessidade #${index + 1} <span class="text-danger">*</span>`;
            }
        });
        nenhuma.style.display = itens.length ? 'none' : 'block';
    } 

    function criarSelectCategorias() {
        const select = document.createElement('select');
        select.className = 'form-select categoria';
        select.name = 'categoria[]';
        select.required = true;
        select.innerHTML = `
            <option value="" selected disabled>Selecione</option>
            <option value="Cursos profissionalizantes">Cursos profissionalizantes</option>
            <option value="Equipamentos para casa">Equipamentos para casa (fogão, colchão, televisão, etc.)</option>
            <option value="Medicamentos">Medicamentos</option>
            <option value="Necessidades jurídicas">Necessidades jurídicas</option>
            <option value="Serviços domésticos">Serviços domésticos (elétrica, montagem, etc.)</option>
            <option value="Vaga em escola">Vaga em escola</option>
            <option value="Outras">Outras</option>
        `;
        return select;
    }

    function criarSelectPrioridade() {
        const select = document.createElement('select');
        select.className = 'form-select prioridade';
        select.name = 'prioridade[]';
        select.innerHTML = `
            <option value="" selected disabled>Selecione</option>
            <option value="Alta">🔴 Alta (urgente)</option>
            <option value="Média">🟠 Média (importante)</option>
            <option value="Baixa">🟢 Baixa (pode esperar)</option>
        `;
        return select;
    }

    const MAP_CATEGORIA_TIPO = {
        'Cursos profissionalizantes': 1,
        'Equipamentos para casa': 2,
        'Serviços domésticos': 3,
        'Medicamentos': 4,
        'Vaga em escola': 5,
        'Necessidades jurídicas': 6,
        'Outras': 7
    };

    function prioridadeClasse(p) {
        if (p === 'Alta') return 'prioridade-alta';
        if (p === 'Média') return 'prioridade-media';
        if (p === 'Baixa') return 'prioridade-baixa';
        return '';
    }

    function formatarPrioridade(p) {
        if (!p) return '<span class="text-muted">—</span>';
        const classe = prioridadeClasse(p);
        let emoji = '';
        if (p === 'Alta') emoji = '🔴';
        if (p === 'Média') emoji = '🟠';
        if (p === 'Baixa') emoji = '🟢';
        return `<span class="prioridade-badge ${classe}">${emoji} ${p}</span>`;
    }

    function formatarStatus(status) {
        if (!status) return '<span class="status-badge">—</span>';
        
        let classe = '';
        if (status.toLowerCase().includes('análise')) classe = 'em-analise';
        else if (status.toLowerCase().includes('andamento')) classe = 'em-andamento';
        else if (status.toLowerCase().includes('concluí')) classe = 'concluida';
        else if (status.toLowerCase().includes('cancelad')) classe = 'cancelada';
        
        return `<span class="status-badge ${classe}">${status}</span>`;
    }

    function formatarCategoria(categoria) {
        if (!categoria) return '<span class="text-muted">—</span>';
        return `<span class="categoria-cell">${categoria}</span>`;
    }

    function formatarObservacao(obs) {
        if (!obs) return '<span class="observacao-cell"></span>';
        return `<div class="observacao-cell">${obs}</div>`;
    }

    function formatarDescricao(desc) {
        if (!desc) return '<div class="descricao-cell text-muted">Sem descrição</div>';
        return `<div class="descricao-cell">${desc}</div>`;
    }

    function renderizarDemandasAtivas() {
        if (!tabelaBody || !secDemandas) return;
        const demandas = Array.isArray(window.sessionCadastro.demandas) ? window.sessionCadastro.demandas : [];
        tabelaBody.innerHTML = '';
        
        // Atualiza contador
        const contador = document.getElementById('contadorDemandas');
        if (contador) {
            contador.textContent = demandas.length;
            contador.style.animation = 'none';
            // Força reflow para reiniciar animação
            contador.offsetHeight;
            contador.style.animation = 'countUpdate 0.3s ease-out';
        }
        
        if (!demandas.length) {
            secDemandas.classList.add('d-none');
            return;
        }
        
        // Adiciona row de "carregando" temporário para suavizar transição
        if (demandas.length > 0) {
            tabelaBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4"><i class="fas fa-spinner fa-spin me-2"></i>Carregando demandas...</td></tr>';
            
            setTimeout(() => {
                tabelaBody.innerHTML = '';
                secDemandas.classList.remove('d-none');
                
                demandas.forEach((d, index) => {
                    const tr = document.createElement('tr');
                    tr.style.animationDelay = `${index * 0.1}s`;
                    tr.innerHTML = `
                        <td>${formatarDescricao(d.descricao)}</td>
                        <td>${formatarCategoria(d.categoria)}</td>
                        <td>${formatarPrioridade(d.prioridade)}</td>
                        <td>${formatarStatus(d.status_atual || d.status)}</td>
                        <td>${formatarObservacao(d.observacao)}</td>
                        <td class="text-center">
                            <button type="button" class="btn-editar-demanda" data-id="${d.demanda_id}" title="Editar demanda">
                                <i class="fas fa-edit"></i>
                            </button>
                        </td>`;
                    tabelaBody.appendChild(tr);
                });
            }, 300);
        }
    }

    function adicionarNecessidade(dados = null) {
        const item = document.createElement('div');
        item.className = 'necessidade-item border rounded p-3 mb-3';

        const titulo = document.createElement('h5');
        titulo.className = 'necessidade-titulo mb-3';
        item.appendChild(titulo);

        const row = document.createElement('div');
        row.className = 'row g-2 align-items-end';

        const colDesc = document.createElement('div');
        colDesc.className = 'col-md-4';
        const labelDesc = document.createElement('label');
        labelDesc.className = 'form-label';
        labelDesc.innerHTML = 'Descrição da necessidade <span class="text-danger">*</span>';
        const inputDesc = document.createElement('input');
        inputDesc.type = 'text';
        inputDesc.className = 'form-control descricao';
        inputDesc.name = 'descricao[]';
        inputDesc.required = true;
        inputDesc.setAttribute('autocomplete', 'off');
        colDesc.appendChild(labelDesc);
        colDesc.appendChild(inputDesc);

        const colCat = document.createElement('div');
        colCat.className = 'col-md-4';
        const labelCat = document.createElement('label');
        labelCat.className = 'form-label';
        labelCat.innerHTML = 'Categoria <span class="text-danger">*</span>';
        const selectCat = criarSelectCategorias();
        colCat.appendChild(labelCat);
        colCat.appendChild(selectCat);

        const colPri = document.createElement('div');
        colPri.className = 'col-md-3';
        const labelPri = document.createElement('label');
        labelPri.className = 'form-label';
        labelPri.textContent = 'Prioridade';
        const selectPri = criarSelectPrioridade();
        colPri.appendChild(labelPri);
        colPri.appendChild(selectPri);

        const colRemover = document.createElement('div');
        colRemover.className = 'col-md-1 text-end';
        const btnRemover = document.createElement('button');
        btnRemover.type = 'button';
        btnRemover.className = 'btn btn-link text-danger p-0 btn-remover';
        btnRemover.innerHTML = '<i class="fa fa-trash"></i>';
        btnRemover.addEventListener('click', function () {
            item.remove();
            atualizarNumeracao();
        });
        colRemover.appendChild(btnRemover);

        row.appendChild(colDesc);
        row.appendChild(colCat);
        row.appendChild(colPri);
        row.appendChild(colRemover);

        item.appendChild(row);

        if (dados) {
            if (dados.demanda_id) {
                const hiddenId = document.createElement('input');
                hiddenId.type = 'hidden';
                hiddenId.className = 'demanda-id';
                hiddenId.value = dados.demanda_id;
                item.appendChild(hiddenId);
            }
            inputDesc.value = dados.descricao || '';
            selectCat.value = dados.categoria || '';
            if (dados.prioridade) selectPri.value = dados.prioridade;
        }

        lista.appendChild(item);
        atualizarNumeracao();
    }

    btnAdicionar.addEventListener('click', () => adicionarNecessidade());

    renderizarDemandasAtivas();

    btnProxima.addEventListener('click', async function (e) {
        e.preventDefault();
        let valido = true;
        lista.querySelectorAll('.necessidade-item').forEach(item => {
            const inputDesc = item.querySelector('.descricao');
            const selectCat = item.querySelector('.categoria');

            if (inputDesc && !inputDesc.value.trim()) {
                inputDesc.classList.add('is-invalid');
                valido = false;
            } else if (inputDesc) {
                inputDesc.classList.remove('is-invalid');
            }

            if (selectCat && !selectCat.value) {
                selectCat.classList.add('is-invalid');
                valido = false;
            } else if (selectCat) {
                selectCat.classList.remove('is-invalid');
            }
        });

        if (valido) {
            const storedFamiliaId = sessionStorage.getItem('familia_id');
            const familiaId = storedFamiliaId !== null ? storedFamiliaId : window.sessionFamiliaId || '0';

            const demandas = [];
            lista.querySelectorAll('.necessidade-item').forEach(item => {
                const desc = item.querySelector('.descricao').value.trim();
                const cat = item.querySelector('.categoria').value;
                const priEl = item.querySelector('.prioridade');
                const prioridade = priEl && priEl.value ? priEl.value : null;
                const idEl = item.querySelector('.demanda-id');
                const demanda = {
                    familia_id: parseInt(familiaId),
                    descricao: desc,                    
                    demanda_tipo_id: MAP_CATEGORIA_TIPO[cat],
                    data_identificacao: new Date().toISOString().split('T')[0],
                    status: 'Em análise'
                };
                if (prioridade) demanda.prioridade = prioridade;
                if (idEl && idEl.value) demanda.demanda_id = parseInt(idEl.value);
                demandas.push(demanda);
            });

            btnProxima.disabled = true;
            try {
                const resp = await fetch(`/demandas/upsert/lote/familia/${familiaId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(demandas)
                });

                if (resp.ok) {
                    const salvas = await resp.json().catch(() => []);
                    window.sessionCadastro.demandas = salvas;
                    const hidden = document.getElementById('demandas_json');
                    if (hidden) hidden.value = JSON.stringify(salvas);
                    const nextUrl = btnProxima.getAttribute('data-next-url');
                    if (nextUrl) {
                        form.action = nextUrl;
                        form.method = 'post';
                        form.submit();
                    }
                } else {
                    const erro = await resp.json().catch(() => ({ mensagem: 'Erro desconhecido' }));
                    alert(JSON.stringify(erro));
                    btnProxima.disabled = false;
                }
            } catch (err) {
                alert('Erro ao enviar os dados. Tente novamente.');
                btnProxima.disabled = false;
            }
        }
    });

    tabelaBody?.addEventListener('click', function (e) {
        const btn = e.target.closest('.btn-editar-demanda');
        if (!btn) return;
        const id = btn.getAttribute('data-id');
        const demanda = (window.sessionCadastro.demandas || []).find(d => String(d.demanda_id) === String(id));
        if (!demanda) return;
        modalId.value = demanda.demanda_id;
        modalStatus.value = demanda.status_atual || 'Em análise';
        modalObs.value = demanda.observacao || '';
        modalDesc.textContent = demanda.descricao || '';
        modal.classList.remove('d-none');
    });

    function fecharModal() {
        modal.classList.add('d-none');
    }

    fecharModalBtn?.addEventListener('click', fecharModal);

    salvarModalBtn?.addEventListener('click', async function () {
        const demId = modalId.value;
        const status = modalStatus.value;
        const observacao = modalObs.value.trim();
        if (!demId || !status) return;
        salvarModalBtn.disabled = true;
        try {
            const etapaResp = await fetch('/demanda_etapas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ demanda_id: parseInt(demId), status_atual: status, observacao })
            });
            if (etapaResp.ok) {
                await fetch(`/demandas/${demId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status })
                });
                const demandas = window.sessionCadastro.demandas || [];
                const alvo = demandas.find(d => String(d.demanda_id) === String(demId));
                if (alvo) {
                    alvo.status_atual = status;
                    alvo.observacao = observacao;
                }
                renderizarDemandasAtivas();
                fecharModal();
            } else {
                alert('Erro ao salvar atualização da demanda.');
            }
        } catch (err) {
            alert('Erro ao salvar atualização da demanda.');
        }
        salvarModalBtn.disabled = false;
    });

    document.getElementById("btnVoltar")?.addEventListener("click", function (e) {
        const url = this.dataset.prevUrl;
        if (url) {
            e.preventDefault();
            window.location.href = url;
        }
    });

    atualizarNumeracao();
});
