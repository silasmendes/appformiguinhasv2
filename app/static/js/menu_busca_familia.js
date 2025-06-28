document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('btnAtenderFamilia');
    const modal = document.getElementById('buscaFamiliaModal');
    const closeBtn = document.getElementById('fecharBuscaFamilia');
    const input = document.getElementById('buscaFamiliaInput');

    function abrirModal() {
        if (modal) {
            modal.classList.remove('d-none');
            if (input) input.focus();
        }
    }

    function fecharModal() {
        if (modal) {
            modal.classList.add('d-none');
        }
    }

    if (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            abrirModal();
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', fecharModal);
    }

    if (window.autoOpenBuscaFamilia) {
        abrirModal();
    }
});
