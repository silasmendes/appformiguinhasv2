// JS para etapa 7 - emprego e habilidades do provedor

document.addEventListener('DOMContentLoaded', function() {
    const relacaoSelect = document.getElementById('relacao_provedor_familia');
    const provedorExternoContainer = document.getElementById('descricao_provedor_externo_container');
    const provedorExternoInput = document.getElementById('descricao_provedor_externo');

    const situacaoSelect = document.getElementById('situacao_emprego');
    const situacaoOutroContainer = document.getElementById('descricao_situacao_emprego_outro_container');
    const situacaoOutroInput = document.getElementById('descricao_situacao_emprego_outro');

    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa7');

    function atualizarProvedorExterno() {
        if (!relacaoSelect) return;
        if (relacaoSelect.value === 'Provedor não familiar') {
            provedorExternoContainer.classList.remove('d-none');
        } else {
            provedorExternoContainer.classList.add('d-none');
            if (provedorExternoInput) provedorExternoInput.value = '';
        }
    }

    function atualizarSituacaoOutro() {
        if (!situacaoSelect) return;
        if (situacaoSelect.value === 'Outro') {
            situacaoOutroContainer.classList.remove('d-none');
        } else {
            situacaoOutroContainer.classList.add('d-none');
            if (situacaoOutroInput) situacaoOutroInput.value = '';
        }
    }

    if (relacaoSelect) {
        relacaoSelect.addEventListener('change', atualizarProvedorExterno);
        atualizarProvedorExterno();
    }

    if (situacaoSelect) {
        situacaoSelect.addEventListener('change', atualizarSituacaoOutro);
        atualizarSituacaoOutro();
    }

    if (btnProxima && form) {
        btnProxima.addEventListener('click', function() {
            console.log('Dados do formulário etapa 7:', Object.fromEntries(new FormData(form).entries()));
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
