
document.addEventListener('DOMContentLoaded', function() {
    const doencaRadios = document.querySelectorAll('input[name="tem_doenca_cronica"]');
    const doencaContainer = document.getElementById('descricao_doenca_cronica_container');

    const medicacaoRadios = document.querySelectorAll('input[name="usa_medicacao_continua"]');
    const medicacaoContainer = document.getElementById('descricao_medicacao_container');

    const deficienciaRadios = document.querySelectorAll('input[name="tem_deficiencia"]');
    const deficienciaContainer = document.getElementById('descricao_deficiencia_container');
    const bpcContainer = document.getElementById('recebe_bpc_container');

    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa6');

    function toggleContainer(radios, container) {
        const selecionado = Array.from(radios).find(r => r.checked);
        if (selecionado && selecionado.value === 'Sim') {
            container.classList.remove('d-none');
        } else {
            container.classList.add('d-none');
            const input = container.querySelector('input, textarea');
            if (input) input.value = '';
        }
    }

    function atualizarDeficiencia() {
        toggleContainer(deficienciaRadios, deficienciaContainer);
        const selecionado = Array.from(deficienciaRadios).find(r => r.checked);
        if (selecionado && selecionado.value === 'Sim') {
            bpcContainer.classList.remove('d-none');
        } else {
            bpcContainer.classList.add('d-none');
            document.querySelectorAll('input[name="recebe_bpc"]').forEach(r => r.checked = false);
        }
    }

    doencaRadios.forEach(r => r.addEventListener('change', () => toggleContainer(doencaRadios, doencaContainer)));
    medicacaoRadios.forEach(r => r.addEventListener('change', () => toggleContainer(medicacaoRadios, medicacaoContainer)));
    deficienciaRadios.forEach(r => r.addEventListener('change', atualizarDeficiencia));

    // initialize state
    toggleContainer(doencaRadios, doencaContainer);
    toggleContainer(medicacaoRadios, medicacaoContainer);
    atualizarDeficiencia();

    if (btnProxima && form) {
        btnProxima.addEventListener('click', function() {
            console.log('Dados do formulário etapa 6:', Object.fromEntries(new FormData(form).entries()));
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
