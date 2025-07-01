// JS para etapa 9 - escolaridade do entrevistado

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

    const estudaSim = document.getElementById('estuda_sim');
    const estudaNao = document.getElementById('estuda_nao');
    const cursoContainer = document.getElementById('curso_ou_serie_atual_container');
    const cursoInput = document.getElementById('curso_ou_serie_atual');
    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa9');

    function toggleCurso() {
        if (estudaSim && estudaSim.checked) {
            cursoContainer.classList.remove('d-none');
        } else {
            cursoContainer.classList.add('d-none');
            if (cursoInput) cursoInput.value = '';
        }
    }

    document.querySelectorAll('input[name="estuda_atualmente"]').forEach(el => {
        el.addEventListener('change', toggleCurso);
    });

    toggleCurso();

    if (btnProxima && form) {
        btnProxima.addEventListener('click', async function(e) {
            e.preventDefault();

            const nextUrl = btnProxima.getAttribute('data-next-url');
            const dadosFormulario = Object.fromEntries(new FormData(form).entries());

            const storedFamiliaId = sessionStorage.getItem('familia_id');
            const familiaId = storedFamiliaId !== null ? storedFamiliaId : window.sessionFamiliaId || '0';

            btnProxima.disabled = true;

            try {
                const resposta = await fetch(`/educacao_entrevistado/upsert/familia/${familiaId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + sessionStorage.getItem('access_token')
                    },
                    body: JSON.stringify(dadosFormulario)
                });

                if (resposta.ok) {
                    const respFamilia = await fetch(`/familias/upsert/familia/${familiaId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + sessionStorage.getItem('access_token')
                        },
                        body: JSON.stringify({ status_cadastro: 'finalizado' })
                    });

                    if (respFamilia.ok) {
                        if (nextUrl) {
                            form.action = nextUrl;
                            form.method = 'post';
                            form.submit();
                        }
                    } else {
                        const erro = await respFamilia.json().catch(() => ({ mensagem: 'Erro desconhecido' }));
                        alert(JSON.stringify(erro));
                        btnProxima.disabled = false;
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
