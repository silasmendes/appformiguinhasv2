document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('btnAtenderFamilia');
    const modal = document.getElementById('buscaFamiliaModal');
    const closeBtn = document.getElementById('fecharBuscaFamilia');
    const input = document.getElementById('buscaFamiliaInput');
    const form = document.getElementById('formBuscaFamilia');
    const status = document.getElementById('buscaFamiliaStatus');

    function destacarResultados() {
        const results = document.getElementById('resultadosContainer');
        if (!results) return;
        results.classList.remove('busca-resultados-entrada');
        void results.offsetWidth;
        results.classList.add('busca-resultados-entrada');
        results.focus({ preventScroll: true });
        results.scrollIntoView({
            behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',
            block: 'nearest'
        });
    }

    if (form) {
        form.addEventListener('submit', async function (event) {
            event.preventDefault();
            const term = input.value.trim();
            if (!term) {
                status.textContent = 'Digite um nome ou CPF para buscar.';
                input.focus();
                return;
            }
            const submit = form.querySelector('[type="submit"]');
            const original = submit.innerHTML;
            submit.disabled = true;
            input.readOnly = true;
            submit.innerHTML = '<i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i> Buscando…';
            status.textContent = 'Buscando famílias…';
            modal.setAttribute('aria-busy', 'true');
            const previous = document.getElementById('resultadosContainer');
            if (previous) previous.hidden = true;
            try {
                const url = new URL(form.action || window.location.href);
                url.searchParams.set('q', term);
                const response = await fetch(url, { credentials: 'same-origin' });
                if (!response.ok) throw new Error('Falha na busca');
                const page = new DOMParser().parseFromString(await response.text(), 'text/html');
                const results = page.getElementById('resultadosContainer');
                if (!results) throw new Error('Resposta inesperada ou sessão expirada');
                if (previous) previous.replaceWith(results);
                else status.after(results);
                window.history.replaceState(null, '', url);
                status.textContent = results.querySelector('h6').textContent.trim();
                destacarResultados();
            } catch (error) {
                status.textContent = 'Não foi possível concluir a busca. Tente novamente. Se o problema continuar, atualize a página para verificar seu acesso.';
            } finally {
                modal.removeAttribute('aria-busy');
                submit.disabled = false;
                input.readOnly = false;
                submit.innerHTML = original;
            }
        });
    }

    function abrirModal() {
        if (modal) {
            modal.classList.remove('d-none');
            if (input) input.focus();
        }
    }

    function fecharModal() {
        if (modal) {
            modal.classList.add('d-none');
        }
    }

    if (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            abrirModal();
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', fecharModal);
    }

    if (window.autoOpenBuscaFamilia) {
        abrirModal();
        destacarResultados();
    }

    // Funcionalidade para o modal de pré-cadastro
    const btnPreCadastro = document.getElementById('btnAtenderPreCadastro');
    const modalPreCadastro = document.getElementById('buscaPreCadastroModal');
    const closeBtnPreCadastro = document.getElementById('fecharBuscaPreCadastro');
    const inputPreCadastro = document.getElementById('buscaPreCadastroInput');
    const formPreCadastro = document.getElementById('formBuscaPreCadastro');

    function abrirModalPreCadastro() {
        if (modalPreCadastro) {
            modalPreCadastro.classList.remove('d-none');
            if (inputPreCadastro) inputPreCadastro.focus();
        }
    }

    function fecharModalPreCadastro() {
        if (modalPreCadastro) {
            modalPreCadastro.classList.add('d-none');
            // Limpar resultados
            const container = document.getElementById('resultadosPreCadastroContainer');
            if (container) container.style.display = 'none';
        }
    }

    if (btnPreCadastro) {
        btnPreCadastro.addEventListener('click', function (e) {
            e.preventDefault();
            abrirModalPreCadastro();
        });
    }

    if (closeBtnPreCadastro) {
        closeBtnPreCadastro.addEventListener('click', fecharModalPreCadastro);
    }

    // Interceptar submit do formulário de pré-cadastro para fazer busca via AJAX
    if (formPreCadastro) {
        formPreCadastro.addEventListener('submit', function(e) {
            e.preventDefault();
            const termo = inputPreCadastro.value.trim();
            if (termo) {
                buscarPreCadastros(termo);
            }
        });
    }

    function buscarPreCadastros(termo) {
        fetch(`/buscar_pre_cadastro?q=${encodeURIComponent(termo)}`)
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('resultadosPreCadastroContainer');
                const lista = document.getElementById('listaPreCadastros');
                
                if (lista) {
                    lista.innerHTML = '';
                    
                    if (data.resultados && data.resultados.length > 0) {
                        data.resultados.forEach(familia => {
                            const li = document.createElement('li');
                            li.className = 'list-group-item familia-resultado';
                            li.innerHTML = `
                                <a href="#" class="text-decoration-none familia-link" data-familia='${JSON.stringify(familia)}'>
                                    <div class="familia-nome">Nome: ${familia.nome_responsavel}</div>
                                    <div class="familia-cpf">CPF: ${familia.cpf || 'Não informado'}</div>
                                    <div class="familia-data">Data pré-cadastro: ${familia.data_pre_cadastro}</div>
                                </a>
                            `;
                            
                            // Adicionar evento de clique
                            li.querySelector('.familia-link').addEventListener('click', function(e) {
                                e.preventDefault();
                                const familiaData = JSON.parse(this.dataset.familia);
                                selecionarPreCadastro(familiaData);
                            });
                            
                            lista.appendChild(li);
                        });
                    } else {
                        lista.innerHTML = '<li class="list-group-item">Nenhum pré-cadastro encontrado</li>';
                    }
                    
                    container.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Erro ao buscar pré-cadastros:', error);
                alert('Erro ao buscar pré-cadastros. Tente novamente.');
            });
    }

    function selecionarPreCadastro(familiaData) {
        // Enviar dados para o servidor para carregar na sessão
        fetch('/carregar_pre_cadastro', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(familiaData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirecionar para primeira etapa do atendimento
                window.location.href = '/atendimento/etapa1';
            } else {
                alert('Erro ao carregar pré-cadastro: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar pré-cadastro:', error);
            alert('Erro ao carregar pré-cadastro. Tente novamente.');
        });
    }
});
