document.addEventListener('DOMContentLoaded', function() {
    const tipoMoradiaSelect = document.getElementById('tipo_moradia');
    const valorAluguelContainer = document.getElementById('valor_aluguel_container');
    const valorAluguelInput = document.getElementById('valor_aluguel');
    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa5');

    function atualizarValorAluguel() {
        if (!tipoMoradiaSelect) return;
        if (tipoMoradiaSelect.value === 'Alugada') {
            valorAluguelContainer.classList.remove('d-none');
        } else {
            valorAluguelContainer.classList.add('d-none');
            if (valorAluguelInput) {
                valorAluguelInput.value = '';
            }
        }
    }

    if (tipoMoradiaSelect) {
        tipoMoradiaSelect.addEventListener('change', atualizarValorAluguel);
        atualizarValorAluguel();
    }

    if (btnProxima && form) {
        btnProxima.addEventListener('click', function() {
            console.log('Dados do formulário etapa 5:', Object.fromEntries(new FormData(form).entries()));
        });
    }
});
