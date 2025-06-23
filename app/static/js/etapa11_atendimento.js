// JS para etapa 11 - conclusão do atendimento

document.addEventListener('DOMContentLoaded', function () {
    console.log('Estado atual da sessão:', window.sessionCadastro);
    const hiddenIdInput = document.getElementById('familia_id_hidden');
    if (window.sessionFamiliaId === null) {
        sessionStorage.removeItem('familia_id');
        if (hiddenIdInput) hiddenIdInput.value = '';
    } else if (window.sessionFamiliaId) {
        sessionStorage.setItem('familia_id', window.sessionFamiliaId);
        if (hiddenIdInput) hiddenIdInput.value = window.sessionFamiliaId;
    }

    const form = document.getElementById('formEtapa11');
    const btnFinalizar = document.getElementById('btnFinalizar');
    const percepcaoSelect = document.getElementById('percepcao_necessidade');
    const radiosDuracao = document.querySelectorAll('input[name="duracao_necessidade"]');
    const cestaCheckbox = document.getElementById('cesta_entregue');
    const avisoCesta = document.getElementById('avisoCesta');

    function toggleAviso() {
        if (!avisoCesta) return;
        if (cestaCheckbox.checked) {
            avisoCesta.classList.add('d-none');
        } else {
            avisoCesta.classList.remove('d-none');
        }
    }

    if (cestaCheckbox) {
        cestaCheckbox.addEventListener('change', toggleAviso);
        toggleAviso();
    }

    if (btnFinalizar && form) {
        btnFinalizar.addEventListener('click', async function (e) {
            e.preventDefault();
            let valido = true;
            if (!percepcaoSelect.value) {
                percepcaoSelect.classList.add('is-invalid');
                valido = false;
            } else {
                percepcaoSelect.classList.remove('is-invalid');
            }
            const duracaoSelecionada = Array.from(radiosDuracao).some(r => r.checked);
            if (!duracaoSelecionada) {
                radiosDuracao.forEach(r => r.classList.add('is-invalid'));
                valido = false;
            } else {
                radiosDuracao.forEach(r => r.classList.remove('is-invalid'));
            }
            if (!valido) return;

            const nextUrl = btnFinalizar.getAttribute('data-next-url');
            const dadosFormulario = Object.fromEntries(new FormData(form).entries());

            const storedFamiliaId = sessionStorage.getItem('familia_id');
            dadosFormulario.familia_id = storedFamiliaId !== null ? parseInt(storedFamiliaId) : parseInt(window.sessionFamiliaId || '0');
            dadosFormulario.usuario_atendente_id = 1; // TODO: substituir pelo ID do usuário logado
            dadosFormulario.cesta_entregue = cestaCheckbox.checked;
            if (dadosFormulario.motivo_duracao === '') delete dadosFormulario.motivo_duracao;

            btnFinalizar.disabled = true;
            try {
                const resp = await fetch('/atendimentos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dadosFormulario)
                });
                if (resp.ok) {
                    if (nextUrl) {
                        form.action = nextUrl;
                        form.method = 'post';
                        form.submit();
                    }
                } else {
                    const erro = await resp.json().catch(() => ({ mensagem: 'Erro desconhecido' }));
                    alert(JSON.stringify(erro));
                    btnFinalizar.disabled = false;
                }
            } catch (err) {
                alert('Erro ao enviar os dados. Tente novamente.');
                btnFinalizar.disabled = false;
            }
        });
    }
});
