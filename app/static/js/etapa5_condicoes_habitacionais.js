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
        btnProxima.addEventListener('click', async function(e) {
            e.preventDefault();
            saveValorAluguel();

            const nextUrl = btnProxima.getAttribute('data-next-url');
            const dadosFormulario = Object.fromEntries(new FormData(form).entries());

            if (dadosFormulario.agua_encanada !== undefined) {
                dadosFormulario.tem_agua_encanada =
                    dadosFormulario.agua_encanada === 'Sim' || dadosFormulario.agua_encanada === true;
                delete dadosFormulario.agua_encanada;
            }
            if (dadosFormulario.rede_esgoto !== undefined) {
                dadosFormulario.tem_rede_esgoto =
                    dadosFormulario.rede_esgoto === 'Sim' || dadosFormulario.rede_esgoto === true;
                delete dadosFormulario.rede_esgoto;
            }
            if (dadosFormulario.energia_eletrica !== undefined) {
                dadosFormulario.tem_energia_eletrica =
                    dadosFormulario.energia_eletrica === 'Sim' || dadosFormulario.energia_eletrica === true;
                delete dadosFormulario.energia_eletrica;
            }
            if (dadosFormulario.tem_fogao !== undefined) {
                dadosFormulario.tem_fogao =
                    dadosFormulario.tem_fogao === 'Sim' || dadosFormulario.tem_fogao === true;
            }
            if (dadosFormulario.tem_geladeira !== undefined) {
                dadosFormulario.tem_geladeira =
                    dadosFormulario.tem_geladeira === 'Sim' || dadosFormulario.tem_geladeira === true;
            }
            if (dadosFormulario.num_camas !== undefined) {
                dadosFormulario.quantidade_camas = dadosFormulario.num_camas;
                delete dadosFormulario.num_camas;
            }
            if (dadosFormulario.num_tvs !== undefined) {
                dadosFormulario.quantidade_tvs = dadosFormulario.num_tvs;
                delete dadosFormulario.num_tvs;
            }
            if (dadosFormulario.num_ventiladores !== undefined) {
                dadosFormulario.quantidade_ventiladores = dadosFormulario.num_ventiladores;
                delete dadosFormulario.num_ventiladores;
            }

            const storedFamiliaId = sessionStorage.getItem('familia_id');
            const familiaId = storedFamiliaId !== null ? storedFamiliaId : window.sessionFamiliaId || '0';

            btnProxima.disabled = true;

            try {
                const resposta = await fetch(`/condicoes_moradia/upsert/familia/${familiaId}`, {
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
