// JS para etapa 3 - composicao familiar

document.addEventListener('DOMContentLoaded', function() {
    console.log('Estado atual da sessão:', window.sessionCadastro);
    const hiddenIdInput = document.getElementById('familia_id_hidden');
    if (window.sessionFamiliaId === null) {
        sessionStorage.removeItem('familia_id');
        if (hiddenIdInput) hiddenIdInput.value = '';
    } else if (window.sessionFamiliaId) {
        sessionStorage.setItem('familia_id', window.sessionFamiliaId);
        if (hiddenIdInput) hiddenIdInput.value = window.sessionFamiliaId;
    }

    const bebes = document.getElementById('quantidade_bebes');
    const criancas = document.getElementById('quantidade_criancas');
    const adolescentes = document.getElementById('quantidade_adolescentes');
    const menoresContainer = document.getElementById('menores_na_escola_container');
    const motivoContainer = document.getElementById('motivo_ausencia_escola_container');
    const motivoInput = document.getElementById('motivo_ausencia_escola');
    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa3');

    function atualizarCampoEscola() {
        const totalMenores = (parseInt(bebes.value) || 0) +
                             (parseInt(criancas.value) || 0) +
                             (parseInt(adolescentes.value) || 0);
        if (totalMenores >= 1) {
            menoresContainer.classList.remove('d-none');
        } else {
            menoresContainer.classList.add('d-none');
            motivoContainer.classList.add('d-none');
            form.querySelectorAll('input[name="menores_na_escola"]').forEach(r => r.checked = false);
            motivoInput.value = '';
        }
    }

    [bebes, criancas, adolescentes].forEach(el => {
        if (el) el.addEventListener('input', atualizarCampoEscola);
    });

    function atualizarMotivo() {
        const selecionado = document.querySelector('input[name="menores_na_escola"]:checked');
        if (selecionado && selecionado.value.toLowerCase() === 'não') {
            motivoContainer.classList.remove('d-none');
        } else {
            motivoContainer.classList.add('d-none');
            motivoInput.value = '';
        }
    }

    document.querySelectorAll('input[name="menores_na_escola"]').forEach(el => {
        el.addEventListener('change', atualizarMotivo);
    });

    // adjust visibility based on loaded values
    atualizarCampoEscola();
    atualizarMotivo();

    if (btnProxima && form) {
        btnProxima.addEventListener('click', async function (e) {
            e.preventDefault();

            const nextUrl = btnProxima.getAttribute('data-next-url');
            const dadosFormulario = Object.fromEntries(new FormData(form).entries());

            if (dadosFormulario.menores_na_escola !== undefined) {
                dadosFormulario.tem_menores_na_escola =
                    dadosFormulario.menores_na_escola === 'Sim' || dadosFormulario.menores_na_escola === true;
                delete dadosFormulario.menores_na_escola;
            }

            const storedFamiliaId = sessionStorage.getItem('familia_id');
            const familiaId = storedFamiliaId !== null ? storedFamiliaId : window.sessionFamiliaId || '0';

            btnProxima.disabled = true;

            try {
                const resposta = await fetch(`/composicao_familiar/upsert/familia/${familiaId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + sessionStorage.getItem('access_token')
                    },
                    body: JSON.stringify(dadosFormulario)
                });

                if (resposta.ok) {
                    if (nextUrl) {
                        form.action = nextUrl;
                        form.method = 'post';
                        form.submit();
                    }
                } else {
                    const erro = await resposta.json().catch(() => ({ mensagem: 'Erro desconhecido' }));
                    alert(JSON.stringify(erro));
                    btnProxima.disabled = false;
                }
            } catch (err) {
                alert('Erro ao enviar os dados. Tente novamente.');
                btnProxima.disabled = false;
            }
        });
    }

    document.getElementById("btnVoltar")?.addEventListener("click", function (e) {
        const url = this.dataset.prevUrl;
        if (url) {
            e.preventDefault();
            window.location.href = url;
        }
    });
});
