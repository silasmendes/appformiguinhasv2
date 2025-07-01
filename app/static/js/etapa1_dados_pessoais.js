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

function converterDataParaISO(dataBR) {
    if (!dataBR || dataBR.length !== 10) return null;
    const [dia, mes, ano] = dataBR.split('/');
    if (!dia || !mes || !ano) return null;
    return `${ano}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`;
}

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
    const dataInput = document.getElementById('data_nascimento');
    if (dataInput) {
        dataInput.setAttribute('autocomplete', 'off');
        Inputmask({ alias: 'datetime', inputFormat: 'dd/mm/yyyy' }).mask(dataInput);
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
    const radiosImagem = form.querySelectorAll('input[name="autoriza_uso_imagem"]');

    function exibirValidacaoCPF() {
        const valor = cpfInput.value;
        if (valor.trim() === '') {
            cpfInput.classList.remove('is-invalid');
            return true;
        }

        const valido = validarCPF(valor);
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

    radiosImagem.forEach(function(el) {
        el.addEventListener('change', atualizarEstadoBotao);
    });

    atualizarEstadoBotao();

    btnProxima.addEventListener('click', async function (e) {
        e.preventDefault();
        if (btnProxima.disabled) {
            return;
        }

        const nextUrl = btnProxima.getAttribute('data-next-url');
        const dadosFormulario = Object.fromEntries(new FormData(form).entries());
        if (!dadosFormulario.familia_id) {
            delete dadosFormulario.familia_id;
        }
        
        // Converter data de nascimento do formato brasileiro para ISO
        if (dadosFormulario.data_nascimento) {
            const dataISO = converterDataParaISO(dadosFormulario.data_nascimento);
            if (dataISO) {
                dadosFormulario.data_nascimento = dataISO;
            }
        }
        
        // Converter valor para booleano esperado pela API
        if (dadosFormulario.autoriza_uso_imagem) {
            dadosFormulario.autoriza_uso_imagem = dadosFormulario.autoriza_uso_imagem === 'Sim';
        }

        // Obtém o familia_id salvo na sessão. Para uma nova família usamos 0,
        // indicando que o backend deve gerar um novo registro.
        const storedFamiliaId = sessionStorage.getItem('familia_id');
        const familiaId = storedFamiliaId !== null ? storedFamiliaId : '0';

        btnProxima.disabled = true;

        try {
            const resposta = await fetch(`/familias/upsert/familia/${familiaId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + sessionStorage.getItem('access_token')
                },
                body: JSON.stringify(dadosFormulario)
            });

            if (resposta.ok) {
                const dados = await resposta.json();
                if (dados.familia_id !== undefined) {
                    sessionStorage.setItem('familia_id', dados.familia_id);
                    if (hiddenIdInput) hiddenIdInput.value = dados.familia_id;
                }

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
});
