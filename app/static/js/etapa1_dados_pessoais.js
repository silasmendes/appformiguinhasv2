// JS para etapa 1 - dados pessoais
function validarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    if (cpf === '' || /^(\d)\1{10}$/.test(cpf)) return true;
    if (cpf.length !== 11) return false;
    let soma = 0;
    for (let i = 0; i < 9; i++) soma += parseInt(cpf.charAt(i)) * (10 - i);
    let digito1 = 11 - (soma % 11);
    if (digito1 > 9) digito1 = 0;
    if (digito1 !== parseInt(cpf.charAt(9))) return false;
    soma = 0;
    for (let i = 0; i < 10; i++) soma += parseInt(cpf.charAt(i)) * (11 - i);
    let digito2 = 11 - (soma % 11);
    if (digito2 > 9) digito2 = 0;
    if (digito2 !== parseInt(cpf.charAt(10))) return false;
    return true;
}

function aplicarMascaraCPF(valor) {
    let v = valor.replace(/\D/g, '').slice(0, 11);
    if (v.length > 9) v = v.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2}).*/, '$1.$2.$3-$4');
    else if (v.length > 6) v = v.replace(/(\d{3})(\d{3})(\d+)/, '$1.$2.$3');
    else if (v.length > 3) v = v.replace(/(\d{3})(\d+)/, '$1.$2');
    return v;
}

document.addEventListener('DOMContentLoaded', function() {
    const dataInput = document.getElementById('data_nascimento');
    if (dataInput) {
        const hoje = new Date();
        const ano = hoje.getFullYear() - 10;
        const dataPadrao = new Date(ano, hoje.getMonth(), hoje.getDate());
        dataInput.value = dataPadrao.toISOString().split('T')[0];
    }

    const generoSelect = document.getElementById('genero');
    const generoOutroContainer = document.getElementById('genero_autodeclarado_container');
    generoSelect.addEventListener('change', function() {
        if (this.value === 'Outro') {
            generoOutroContainer.classList.remove('d-none');
        } else {
            generoOutroContainer.classList.add('d-none');
            document.getElementById('genero_autodeclarado').value = '';
        }
    });

    const cpfInput = document.getElementById('cpf');
    const btnProxima = document.getElementById('btnProxima');
    const form = document.getElementById('formEtapa1');
    const requiredInputs = form.querySelectorAll('[required]');

    function exibirValidacaoCPF() {
        const valido = validarCPF(cpfInput.value);
        if (!valido) {
            cpfInput.classList.add('is-invalid');
        } else {
            cpfInput.classList.remove('is-invalid');
        }
        return valido;
    }

    function atualizarEstadoBotao() {
        const cpfOk = exibirValidacaoCPF();
        btnProxima.disabled = !(cpfOk && form.checkValidity());
    }

    cpfInput.addEventListener('input', function() {
        this.value = aplicarMascaraCPF(this.value);
        atualizarEstadoBotao();
    });

    cpfInput.addEventListener('blur', exibirValidacaoCPF);

    requiredInputs.forEach(function(el) {
        el.addEventListener('input', atualizarEstadoBotao);
        el.addEventListener('change', atualizarEstadoBotao);
    });

    atualizarEstadoBotao();

    btnProxima.addEventListener('click', function() {
        console.log('Dados do formulário etapa 1:', Object.fromEntries(new FormData(form).entries()));
    });
});
