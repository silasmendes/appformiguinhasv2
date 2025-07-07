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

    // Formatação de campo monetário
    function formatCurrency(input) {
        if (!input) return;
        const cursorPos = input.selectionStart;
        const prevLength = input.value.length;
        let value = input.value.replace(/[^\d-]/g, '');
        let negative = value.startsWith('-');
        value = value.replace(/-/g, '');
        value = (parseInt(value || '0') / 100).toFixed(2);
        value = value.replace('.', ',');
        value = value.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
        input.value = `${negative ? '-' : ''}R$ ${value}`;
        input.dataset.rawValue = (negative ? '-' : '') + (parseInt(input.value.replace(/\D/g, '')) / 100).toFixed(2);
        if (document.activeElement === input) {
            const newLength = input.value.length;
            const diff = newLength - prevLength;
            const newPos = cursorPos + diff;
            input.setSelectionRange(newPos, newPos);
        }
    }

    // Configurar campos monetários
    const currencyInputs = document.querySelectorAll('.renda-decimal');
    currencyInputs.forEach(input => {
        input.addEventListener('input', function() {
            const numbers = this.value.replace(/[^\d-]/g, '');
            if (numbers.length > 15) {
                this.value = this.dataset.previousValue || '';
                return;
            }
            this.dataset.previousValue = this.value;
            formatCurrency(this);
        });
        input.addEventListener('focus', function() {
            if (!this.value) {
                this.value = 'R$ 0,00';
                this.dataset.rawValue = '0.00';
            }
        });
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.value = 'R$ 0,00';
                this.dataset.rawValue = '0.00';
            } else {
                formatCurrency(this);
            }
        });
        if (!input.value) {
            input.value = 'R$ 0,00';
            input.dataset.rawValue = '0.00';
        } else {
            formatCurrency(input);
        }
    });

    const tipoMoradiaSelect = document.getElementById('tipo_moradia');
    const valorAluguelContainer = document.getElementById('valor_aluguel_container');
    const valorAluguelInput = document.getElementById('valor_aluguel');
    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa5');

    function saveValorAluguel() {
        if (!tipoMoradiaSelect) return;
        if (tipoMoradiaSelect.value === 'Alugada' && valorAluguelInput) {
            // Salvar o valor raw para manter a compatibilidade
            const rawValue = valorAluguelInput.dataset.rawValue || '0';
            sessionStorage.setItem('valor_aluguel', rawValue);
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
                valorAluguelInput.value = 'R$ 0,00';
                valorAluguelInput.dataset.rawValue = '0.00';
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

            // Processar valor do aluguel usando rawValue se disponível
            if (dadosFormulario.valor_aluguel !== undefined && valorAluguelInput && valorAluguelInput.dataset.rawValue) {
                dadosFormulario.valor_aluguel = valorAluguelInput.dataset.rawValue;
            }

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
                        'Content-Type': 'application/json'
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
