// JS para etapa 2 - endereço da família

document.addEventListener('DOMContentLoaded', function() {
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
        btnProxima.addEventListener('click', function() {
            console.log('Dados do formulário etapa 2:', Object.fromEntries(new FormData(form).entries()));
            const nextUrl = btnProxima.getAttribute('data-next-url');
            if (nextUrl) {
                form.action = nextUrl;
                form.method = 'post';
                form.submit();
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
