document.addEventListener('DOMContentLoaded', function() {
    console.log('Estado atual da sessão:', window.sessionCadastro);
    const tipoMoradiaSelect = document.getElementById('tipo_moradia');
    const valorAluguelContainer = document.getElementById('valor_aluguel_container');
    const valorAluguelInput = document.getElementById('valor_aluguel');
    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa5');

    function saveValorAluguel() {
        if (!tipoMoradiaSelect) return;
        if (tipoMoradiaSelect.value === 'Alugada' && valorAluguelInput) {
            sessionStorage.setItem('valor_aluguel', valorAluguelInput.value || '0');
        } else {
            sessionStorage.removeItem('valor_aluguel');
        }
    }

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
        tipoMoradiaSelect.addEventListener('change', function() {
            atualizarValorAluguel();
            saveValorAluguel();
        });
        atualizarValorAluguel();
    }

    if (valorAluguelInput) {
        valorAluguelInput.addEventListener('input', saveValorAluguel);
    }

    if (btnProxima && form) {
        btnProxima.addEventListener('click', function() {
            console.log('Dados do formulário etapa 5:', Object.fromEntries(new FormData(form).entries()));
            console.log('Estado atual da sessão:', window.sessionCadastro);
            saveValorAluguel();
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
