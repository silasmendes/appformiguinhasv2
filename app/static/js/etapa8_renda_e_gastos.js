// JS para etapa 8 - renda e gastos mensais

document.addEventListener('DOMContentLoaded', function() {
    const currencyInputs = document.querySelectorAll('.renda-decimal');

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
        const total = somar(gastosIds);
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
        btnProxima.addEventListener('click', function() {
            console.log('Dados do formulário etapa 8:', Object.fromEntries(new FormData(form).entries()));
        });
    }

    updateTotais();
    calcularGastosGas();
});
