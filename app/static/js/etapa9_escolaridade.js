// JS para etapa 9 - escolaridade do entrevistado

document.addEventListener('DOMContentLoaded', function() {
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
        btnProxima.addEventListener('click', function() {
            console.log('Dados do formulário etapa 9:', Object.fromEntries(new FormData(form).entries()));
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
