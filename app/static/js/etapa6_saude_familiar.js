
document.addEventListener('DOMContentLoaded', function() {
    console.log('Estado atual da sessão:', window.sessionCadastro);
    const hiddenIdInput = document.getElementById('familia_id_hidden');
    if (window.sessionFamiliaId === null) {
        sessionStorage.removeItem('familia_id');
        if (hiddenIdInput) hiddenIdInput.value = '';
    } else if (window.sessionFamiliaId) {
        sessionStorage.setItem('familia_id', window.sessionFamiliaId);
        if (hiddenIdInput) hiddenIdInput.value = window.sessionFamiliaId;
    }
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
        btnProxima.addEventListener('click', async function(e) {
            e.preventDefault();

            const nextUrl = btnProxima.getAttribute('data-next-url');
            const dadosFormulario = Object.fromEntries(new FormData(form).entries());

            if (dadosFormulario.tem_doenca_cronica !== undefined) {
                dadosFormulario.tem_doenca_cronica = dadosFormulario.tem_doenca_cronica === 'Sim' || dadosFormulario.tem_doenca_cronica === true;
            }
            if (dadosFormulario.usa_medicacao_continua !== undefined) {
                dadosFormulario.usa_medicacao_continua = dadosFormulario.usa_medicacao_continua === 'Sim' || dadosFormulario.usa_medicacao_continua === true;
            }
            if (dadosFormulario.tem_deficiencia !== undefined) {
                dadosFormulario.tem_deficiencia = dadosFormulario.tem_deficiencia === 'Sim' || dadosFormulario.tem_deficiencia === true;
            }
            if (dadosFormulario.recebe_bpc !== undefined) {
                dadosFormulario.recebe_bpc = dadosFormulario.recebe_bpc === 'Sim' || dadosFormulario.recebe_bpc === true;
            }

            const storedFamiliaId = sessionStorage.getItem('familia_id');
            const familiaId = storedFamiliaId !== null ? storedFamiliaId : window.sessionFamiliaId || '0';

            btnProxima.disabled = true;

            try {
                const resposta = await fetch(`/saude_familiar/upsert/familia/${familiaId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + sessionStorage.getItem('access_token')
                    },
                    body: JSON.stringify(dadosFormulario)
                });

                if (resposta.ok) {
                    if (nextUrl) {
                        form.action = nextUrl;
                        form.method = 'post';
                        form.submit();
                    }
                } else {
                    const erro = await resposta.json().catch(() => ({ mensagem: 'Erro desconhecido' }));
                    alert(JSON.stringify(erro));
                    btnProxima.disabled = false;
                }
            } catch (err) {
                alert('Erro ao enviar os dados. Tente novamente.');
                btnProxima.disabled = false;
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
