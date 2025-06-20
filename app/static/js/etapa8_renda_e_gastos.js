// JS para etapa 8 - renda e gastos mensais

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

    const currencyInputs = document.querySelectorAll('.renda-decimal');

    let valorAluguel = 0;
    function carregarValorAluguel() {
        const armazenado = sessionStorage.getItem('valor_aluguel');
        if (armazenado !== null) {
            valorAluguel = parseFloat(armazenado) || 0;
        } else {
            const hidden = document.getElementById('valor_aluguel_hidden');
            if (hidden) {
                valorAluguel = parseFloat(hidden.dataset.rawValue || hidden.value || '0') || 0;
            }
        }
        console.log('Valor aluguel recuperado:', valorAluguel);
    }

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

    const valorBotija = document.getElementById('valor_botija_gas');
    const duracaoBotija = document.getElementById('duracao_botija_gas');
    const gastosGas = document.getElementById('gastos_gas');

    function calcularGastosGas() {
        if (!valorBotija || !duracaoBotija || !gastosGas) return;
        const valor = parseFloat(valorBotija.dataset.rawValue || '0');
        const meses = parseFloat(duracaoBotija.value || '0');
        if (meses > 0) {
            const mensal = valor / meses;
            gastosGas.dataset.rawValue = mensal.toFixed(2);
            gastosGas.value = `R$ ${mensal.toFixed(2).replace('.', ',')}`;
        } else {
            gastosGas.dataset.rawValue = '0.00';
            gastosGas.value = 'R$ 0,00';
        }
        updateTotais();
    }

    if (valorBotija && duracaoBotija) {
        valorBotija.addEventListener('input', calcularGastosGas);
        duracaoBotija.addEventListener('input', calcularGastosGas);
    }

    const gastosIds = [
        'gastos_supermercado',
        'gastos_energia_eletrica',
        'gastos_agua',
        'gastos_gas',
        'gastos_transporte',
        'gastos_medicamentos',
        'gastos_conta_celular',
        'gastos_outros'
    ];
    const rendaIds = [
        'renda_arrimo',
        'renda_outros_familiares',
        'auxilio_parentes_amigos',
        'valor_total_beneficios'
    ];

    const totalGastosInput = document.getElementById('total_gastos');
    const rendaTotalInput = document.getElementById('renda_familiar_total');
    const saldoInput = document.getElementById('saldo');

    function somar(ids) {
        return ids.reduce((sum, id) => {
            const el = document.getElementById(id);
            if (el && el.dataset.rawValue) {
                sum += parseFloat(el.dataset.rawValue) || 0;
            }
            return sum;
        }, 0);
    }

    function atualizarTotaisRenda() {
        const total = somar(rendaIds);
        rendaTotalInput.dataset.rawValue = total.toFixed(2);
        rendaTotalInput.value = `R$ ${total.toFixed(2).replace('.', ',')}`;
        atualizarSaldo();
    }

    function atualizarTotaisGastos() {
        const total = somar(gastosIds) + valorAluguel;
        totalGastosInput.dataset.rawValue = total.toFixed(2);
        totalGastosInput.value = `R$ ${total.toFixed(2).replace('.', ',')}`;
        atualizarSaldo();
    }

    function atualizarSaldo() {
        const renda = parseFloat(rendaTotalInput.dataset.rawValue || '0');
        const gastos = parseFloat(totalGastosInput.dataset.rawValue || '0');
        const saldo = renda - gastos;
        saldoInput.dataset.rawValue = saldo.toFixed(2);
        saldoInput.value = `R$ ${saldo.toFixed(2).replace('.', ',')}`;
        if (saldo < 0) {
            saldoInput.classList.add('text-danger');
            saldoInput.classList.remove('text-success');
        } else {
            saldoInput.classList.add('text-success');
            saldoInput.classList.remove('text-danger');
        }
    }

    function updateTotais() {
        atualizarTotaisGastos();
        atualizarTotaisRenda();
    }

    gastosIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', atualizarTotaisGastos);
    });
    rendaIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', atualizarTotaisRenda);
    });

    // Programas sociais
    const beneficioSim = document.getElementById('beneficio_sim');
    const beneficioNao = document.getElementById('beneficio_nao');
    const beneficiosSection = document.getElementById('beneficios_section');
    const beneficiosTags = document.querySelector('.beneficios-tags');
    const descricaoBeneficios = document.getElementById('descricao_beneficios');
    const valorTotalBeneficios = document.getElementById('valor_total_beneficios');
    const valorTotalBeneficiosContainer = document.getElementById('valor_total_beneficios_container');

    function toggleBeneficios() {
        if (beneficioSim && beneficioSim.checked) {
            beneficiosSection.style.display = 'block';
            beneficiosTags.style.display = 'flex';
            if (valorTotalBeneficiosContainer) valorTotalBeneficiosContainer.style.display = 'block';
        } else {
            beneficiosSection.style.display = 'none';
            beneficiosTags.style.display = 'none';
            descricaoBeneficios.value = '';
            valorTotalBeneficios.value = 'R$ 0,00';
            valorTotalBeneficios.dataset.rawValue = '0.00';
            if (valorTotalBeneficiosContainer) valorTotalBeneficiosContainer.style.display = 'none';
            updateTotais();
        }
    }

    if (beneficioSim && beneficioNao) {
        beneficioSim.addEventListener('change', toggleBeneficios);
        beneficioNao.addEventListener('change', toggleBeneficios);
        toggleBeneficios();
    }

    if (beneficiosTags) {
        beneficiosTags.querySelectorAll('.beneficio-tag').forEach(tag => {
            tag.addEventListener('click', function() {
                const beneficio = this.getAttribute('data-beneficio');
                let current = descricaoBeneficios.value.trim();
                if (current) {
                    const list = current.split(',').map(b => b.trim());
                    if (!list.includes(beneficio)) {
                        descricaoBeneficios.value = current + ', ' + beneficio;
                    }
                } else {
                    descricaoBeneficios.value = beneficio;
                }
            });
        });
    }

    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa8');
    if (btnProxima && form) {
        btnProxima.addEventListener('click', async function(e) {
            e.preventDefault();

            const nextUrl = btnProxima.getAttribute('data-next-url');

            const dadosFormulario = {};
            const formData = new FormData(form);
            for (const [name, value] of formData.entries()) {
                const el = form.querySelector(`[name="${name}"]`);
                if (el && el.dataset.rawValue !== undefined) {
                    dadosFormulario[name] = el.dataset.rawValue;
                } else {
                    dadosFormulario[name] = value;
                }
            }

            if (dadosFormulario.cadastro_unico !== undefined) {
                dadosFormulario.possui_cadastro_unico =
                    dadosFormulario.cadastro_unico === 'Sim' || dadosFormulario.cadastro_unico === true;
                delete dadosFormulario.cadastro_unico;
            }
            if (dadosFormulario.recebe_beneficio !== undefined) {
                dadosFormulario.recebe_beneficios_governo =
                    dadosFormulario.recebe_beneficio === 'Sim' || dadosFormulario.recebe_beneficio === true;
                delete dadosFormulario.recebe_beneficio;
            }
            if (dadosFormulario.valor_botija_gas !== undefined) {
                dadosFormulario.valor_botijao_gas = dadosFormulario.valor_botija_gas;
                delete dadosFormulario.valor_botija_gas;
            }
            if (dadosFormulario.duracao_botija_gas !== undefined) {
                dadosFormulario.duracao_botijao_gas = dadosFormulario.duracao_botija_gas;
                delete dadosFormulario.duracao_botija_gas;
            }
            if (dadosFormulario.gastos_conta_celular !== undefined) {
                dadosFormulario.gastos_celular = dadosFormulario.gastos_conta_celular;
                delete dadosFormulario.gastos_conta_celular;
            }
            if (dadosFormulario.renda_arrimo !== undefined) {
                dadosFormulario.renda_provedor_principal = dadosFormulario.renda_arrimo;
                delete dadosFormulario.renda_arrimo;
            }
            if (dadosFormulario.renda_outros_familiares !== undefined) {
                dadosFormulario.renda_outros_moradores = dadosFormulario.renda_outros_familiares;
                delete dadosFormulario.renda_outros_familiares;
            }
            if (dadosFormulario.auxilio_parentes_amigos !== undefined) {
                dadosFormulario.ajuda_terceiros = dadosFormulario.auxilio_parentes_amigos;
                delete dadosFormulario.auxilio_parentes_amigos;
            }
            if (dadosFormulario.valor_total_beneficios !== undefined) {
                dadosFormulario.valor_beneficios = dadosFormulario.valor_total_beneficios;
                delete dadosFormulario.valor_total_beneficios;
            }
            if (dadosFormulario.renda_familiar_total !== undefined) {
                dadosFormulario.renda_total_familiar = dadosFormulario.renda_familiar_total;
                delete dadosFormulario.renda_familiar_total;
            }
            if (dadosFormulario.total_gastos !== undefined) {
                dadosFormulario.gastos_totais = dadosFormulario.total_gastos;
                delete dadosFormulario.total_gastos;
            }
            if (dadosFormulario.saldo !== undefined) {
                dadosFormulario.saldo_mensal = dadosFormulario.saldo;
                delete dadosFormulario.saldo;
            }

            const storedFamiliaId = sessionStorage.getItem('familia_id');
            const familiaId = storedFamiliaId !== null ? storedFamiliaId : window.sessionFamiliaId || '0';

            btnProxima.disabled = true;

            try {
                const resposta = await fetch(`/renda_familiar/upsert/familia/${familiaId}`, {
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

    carregarValorAluguel();
    updateTotais();
    calcularGastosGas();
});
