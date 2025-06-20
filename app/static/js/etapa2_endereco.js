// JS para etapa 2 - endereço da família

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

    const cepInput = document.getElementById('cep');
    const manualCheckbox = document.getElementById('preenchimento_manual');
    const cepFeedback = document.getElementById('cep-feedback');
    const addressFields = ['logradouro', 'bairro', 'cidade', 'estado'];

    function setAddressFieldsEnabled(enabled) {
        addressFields.forEach(id => {
            const field = document.getElementById(id);
            if (field) {
                field.disabled = !enabled;
            }
        });
        if (enabled) {
            const cidade = document.getElementById('cidade');
            const estado = document.getElementById('estado');
            if (cidade && !cidade.value) cidade.value = 'Campinas';
            if (estado && !estado.value) estado.value = 'SP';
        }
    }

    function clearAddressFields() {
        addressFields.forEach(id => {
            const field = document.getElementById(id);
            if (field) field.value = '';
        });
    }

    function showCepError() {
        if (cepFeedback) {
            cepFeedback.classList.remove('d-none');
        }
        clearAddressFields();
    }

    if (manualCheckbox) {
        manualCheckbox.addEventListener('change', function() {
            setAddressFieldsEnabled(this.checked);
            if (!this.checked) {
                cepFeedback.classList.add('d-none');
            }
        });
        // inicial
        setAddressFieldsEnabled(manualCheckbox.checked);
    }

    if (cepInput) {
        Inputmask('99999-999').mask(cepInput);

        cepInput.addEventListener('blur', function() {
            const cep = cepInput.value.replace(/\D/g, '');
            if (cep.length === 8 && !manualCheckbox.checked) {
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(resp => resp.json())
                    .then(data => {
                        if (!data.erro) {
                            document.getElementById('logradouro').value = data.logradouro || '';
                            document.getElementById('bairro').value = data.bairro || '';
                            document.getElementById('cidade').value = data.localidade || '';
                            document.getElementById('estado').value = data.uf || '';
                            cepFeedback.classList.add('d-none');
                            document.getElementById('numero').focus();
                        } else {
                            showCepError();
                        }
                    })
                    .catch(() => {
                        showCepError();
                    });
            } else if (cep.length > 0 && !manualCheckbox.checked) {
                showCepError();
            }
        });
    }

    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa2');
    if (btnProxima && form) {
        btnProxima.addEventListener('click', async function (e) {
            e.preventDefault();

            const nextUrl = btnProxima.getAttribute('data-next-url');
            const dadosFormulario = Object.fromEntries(new FormData(form).entries());

            if (dadosFormulario.preenchimento_manual !== undefined) {
                dadosFormulario.preenchimento_manual =
                    dadosFormulario.preenchimento_manual === 'on' || dadosFormulario.preenchimento_manual === true;
            }

            const storedFamiliaId = sessionStorage.getItem('familia_id');
            const familiaId = storedFamiliaId !== null ? storedFamiliaId : window.sessionFamiliaId || '0';

            btnProxima.disabled = true;

            try {
                const resposta = await fetch(`/enderecos/upsert/familia/${familiaId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
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
