// JS para etapa 11 - conclusão do atendimento

function converterDataParaISO(dataBR) {
    if (!dataBR || dataBR.trim() === '' || dataBR.length !== 10) return null;
    const [dia, mes, ano] = dataBR.split('/');
    if (!dia || !mes || !ano || dia.length !== 2 || mes.length !== 2 || ano.length !== 4) return null;
    return `${ano}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`;
}

function obterDataHojeBR() {
    const hoje = new Date();
    const dia = String(hoje.getDate()).padStart(2, '0');
    const mes = String(hoje.getMonth() + 1).padStart(2, '0');
    const ano = hoje.getFullYear();
    return `${dia}/${mes}/${ano}`;
}

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
    const dataEntregaCestaContainer = document.getElementById('dataEntregaCestaContainer');
    const dataEntregaCestaInput = document.getElementById('data_entrega_cesta');

    // Aplicar máscara de data no campo de data de entrega da cesta
    if (dataEntregaCestaInput) {
        dataEntregaCestaInput.setAttribute('autocomplete', 'off');
        Inputmask({ alias: 'datetime', inputFormat: 'dd/mm/yyyy' }).mask(dataEntregaCestaInput);
    }

    function toggleAviso() {
        if (!avisoCesta) return;
        if (cestaCheckbox.checked) {
            avisoCesta.classList.add('d-none');
            // Mostrar campo de data e preencher com data atual se vazio
            if (dataEntregaCestaContainer) {
                dataEntregaCestaContainer.style.display = '';
            }
            if (dataEntregaCestaInput && !dataEntregaCestaInput.value) {
                dataEntregaCestaInput.value = obterDataHojeBR();
            }
        } else {
            avisoCesta.classList.remove('d-none');
            // Ocultar campo de data
            if (dataEntregaCestaContainer) {
                dataEntregaCestaContainer.style.display = 'none';
            }
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
            // usuario_atendente_id é definido automaticamente pelo backend com base no usuário logado
            dadosFormulario.cesta_entregue = cestaCheckbox.checked;
            if (dadosFormulario.motivo_duracao === '') delete dadosFormulario.motivo_duracao;

            // Converter data de entrega da cesta do formato brasileiro para ISO
            if (dadosFormulario.cesta_entregue && dadosFormulario.data_entrega_cesta && dadosFormulario.data_entrega_cesta.trim() !== '') {
                const dataISO = converterDataParaISO(dadosFormulario.data_entrega_cesta);
                if (dataISO) {
                    dadosFormulario.data_entrega_cesta = dataISO;
                } else {
                    delete dadosFormulario.data_entrega_cesta;
                }
            } else {
                delete dadosFormulario.data_entrega_cesta;
            }

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
