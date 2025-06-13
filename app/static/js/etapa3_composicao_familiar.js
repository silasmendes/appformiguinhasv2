// JS para etapa 3 - composicao familiar

document.addEventListener('DOMContentLoaded', function() {
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

    if (btnProxima && form) {
        btnProxima.addEventListener('click', function() {
            console.log('Dados do formulário etapa 3:', Object.fromEntries(new FormData(form).entries()));
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
