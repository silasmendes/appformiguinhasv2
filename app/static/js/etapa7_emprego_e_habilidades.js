// JS para etapa 7 - emprego e habilidades do provedor

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
    const relacaoSelect = document.getElementById('relacao_provedor_familia');
    const provedorExternoContainer = document.getElementById('descricao_provedor_externo_container');
    const provedorExternoInput = document.getElementById('descricao_provedor_externo');

    const situacaoSelect = document.getElementById('situacao_emprego');
    const situacaoOutroContainer = document.getElementById('descricao_situacao_emprego_outro_container');
    const situacaoOutroInput = document.getElementById('descricao_situacao_emprego_outro');

    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa7');

    function atualizarProvedorExterno() {
        if (!relacaoSelect) return;
        if (relacaoSelect.value === 'Provedor não familiar') {
            provedorExternoContainer.classList.remove('d-none');
        } else {
            provedorExternoContainer.classList.add('d-none');
            if (provedorExternoInput) provedorExternoInput.value = '';
        }
    }

    function atualizarSituacaoOutro() {
        if (!situacaoSelect) return;
        if (situacaoSelect.value === 'Outro') {
            situacaoOutroContainer.classList.remove('d-none');
        } else {
            situacaoOutroContainer.classList.add('d-none');
            if (situacaoOutroInput) situacaoOutroInput.value = '';
        }
    }

    if (relacaoSelect) {
        relacaoSelect.addEventListener('change', atualizarProvedorExterno);
        atualizarProvedorExterno();
    }

    if (situacaoSelect) {
        situacaoSelect.addEventListener('change', atualizarSituacaoOutro);
        atualizarSituacaoOutro();
    }

    if (btnProxima && form) {
        btnProxima.addEventListener('click', async function(e) {
            e.preventDefault();

            const nextUrl = btnProxima.getAttribute('data-next-url');
            const dadosFormulario = Object.fromEntries(new FormData(form).entries());

            const storedFamiliaId = sessionStorage.getItem('familia_id');
            const familiaId = storedFamiliaId !== null ? storedFamiliaId : window.sessionFamiliaId || '0';

            btnProxima.disabled = true;

            try {
                const resposta = await fetch(`/emprego_provedor/upsert/familia/${familiaId}`, {
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
