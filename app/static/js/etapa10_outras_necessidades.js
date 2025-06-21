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
    const btnFinalizar = document.getElementById('btnFinalizar');
    const nenhuma = document.getElementById('nenhumaNecessidade');
    const form = document.getElementById('formEtapa10');

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

    if (Array.isArray(window.sessionCadastro.demandas)) {
        window.sessionCadastro.demandas.forEach(d => adicionarNecessidade(d));
    }

    btnFinalizar.addEventListener('click', async function (e) {
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

            btnFinalizar.disabled = true;
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
                    const nextUrl = btnFinalizar.getAttribute('data-next-url');
                    if (nextUrl) {
                        form.action = nextUrl;
                        form.method = 'post';
                        form.submit();
                    }
                } else {
                    const erro = await resp.json().catch(() => ({ mensagem: 'Erro desconhecido' }));
                    alert(JSON.stringify(erro));
                    btnFinalizar.disabled = false;
                }
            } catch (err) {
                alert('Erro ao enviar os dados. Tente novamente.');
                btnFinalizar.disabled = false;
            }
        }
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
