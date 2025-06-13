// JS para etapa 4 - contato

document.addEventListener('DOMContentLoaded', function() {
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
        btnProxima.addEventListener('click', function() {
            validarEmail();
            console.log('Dados do formulário etapa 4:', Object.fromEntries(new FormData(form).entries()));
            const nextUrl = btnProxima.getAttribute('data-next-url');
            if (nextUrl) {
                window.location.href = nextUrl;
            }
        });
    }

    document.getElementById("btnVoltar")?.addEventListener("click", function () {
        window.location.href = this.dataset.prevUrl;
    });
});
