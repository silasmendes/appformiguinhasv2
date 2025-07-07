// JS para etapa 4 - contato

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

    // Funcionalidade das tags de contato
    const telefonePrincipalNomeInput = document.getElementById('telefone_principal_nome_contato');
    const telefoneAlternativoNomeInput = document.getElementById('telefone_alternativo_nome_contato');
    
    // Tags para telefone principal
    const contatoTagsPrincipal = document.querySelectorAll('.contato-tags')[0];
    if (contatoTagsPrincipal && telefonePrincipalNomeInput) {
        contatoTagsPrincipal.querySelectorAll('.contato-tag').forEach(tag => {
            tag.addEventListener('click', function() {
                const contato = this.getAttribute('data-contato');
                let current = telefonePrincipalNomeInput.value.trim();
                if (current) {
                    const list = current.split(',').map(c => c.trim());
                    if (!list.includes(contato)) {
                        telefonePrincipalNomeInput.value = current + ', ' + contato;
                    }
                } else {
                    telefonePrincipalNomeInput.value = contato;
                }
            });
        });
    }
    
    // Tags para telefone alternativo
    const contatoTagsAlternativo = document.querySelectorAll('.contato-tags')[1];
    if (contatoTagsAlternativo && telefoneAlternativoNomeInput) {
        contatoTagsAlternativo.querySelectorAll('.contato-tag').forEach(tag => {
            tag.addEventListener('click', function() {
                const contato = this.getAttribute('data-contato');
                let current = telefoneAlternativoNomeInput.value.trim();
                if (current) {
                    const list = current.split(',').map(c => c.trim());
                    if (!list.includes(contato)) {
                        telefoneAlternativoNomeInput.value = current + ', ' + contato;
                    }
                } else {
                    telefoneAlternativoNomeInput.value = contato;
                }
            });
        });
    }

    const telefonePrincipal = document.getElementById('telefone_principal');
    const telefoneAlternativo = document.getElementById('telefone_alternativo');
    const emailInput = document.getElementById('email_responsavel');
    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa4');

    if (telefonePrincipal) {
        Inputmask('(99) 99999-9999').mask(telefonePrincipal);
    }
    if (telefoneAlternativo) {
        Inputmask('(99) 999999999').mask(telefoneAlternativo);
    }

    function validarEmail() {
        if (!emailInput) return true;
        const valor = emailInput.value.trim();
        if (valor === '') {
            emailInput.classList.remove('is-invalid');
            return true;
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(valor)) {
            emailInput.classList.add('is-invalid');
            return false;
        } else {
            emailInput.classList.remove('is-invalid');
            return true;
        }
    }

    if (emailInput) {
        emailInput.addEventListener('blur', validarEmail);
        emailInput.addEventListener('input', validarEmail);
    }

    if (btnProxima && form) {
        btnProxima.addEventListener('click', async function(e) {
            e.preventDefault();
            if (!validarEmail()) {
                return;
            }

            const nextUrl = btnProxima.getAttribute('data-next-url');
            const dadosFormulario = Object.fromEntries(new FormData(form).entries());

            if (dadosFormulario.telefone_principal_whatsapp !== undefined) {
                dadosFormulario.telefone_principal_whatsapp =
                    dadosFormulario.telefone_principal_whatsapp === 'on' || dadosFormulario.telefone_principal_whatsapp === true;
            }
            if (dadosFormulario.telefone_alternativo_whatsapp !== undefined) {
                dadosFormulario.telefone_alternativo_whatsapp =
                    dadosFormulario.telefone_alternativo_whatsapp === 'on' || dadosFormulario.telefone_alternativo_whatsapp === true;
            }

            const storedFamiliaId = sessionStorage.getItem('familia_id');
            const familiaId = storedFamiliaId !== null ? storedFamiliaId : window.sessionFamiliaId || '0';

            btnProxima.disabled = true;

            try {
                const resposta = await fetch(`/contatos/upsert/familia/${familiaId}`, {
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
