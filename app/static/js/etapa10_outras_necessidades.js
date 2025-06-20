// JS para etapa 10 - outras necessidades informadas

document.addEventListener('DOMContentLoaded', function() {
    const lista = document.getElementById('necessidadesLista');
    const btnAdicionar = document.getElementById('adicionarNecessidade');
    const btnFinalizar = document.getElementById('btnFinalizar');
    const nenhuma = document.getElementById('nenhumaNecessidade');
    const form = document.getElementById('formEtapa10');

    function atualizarNumeracao() {
        const itens = lista.querySelectorAll('.necessidade-item');
        itens.forEach((item, index) => {
            const titulo = item.querySelector('.necessidade-titulo');
            if (titulo) {
                titulo.textContent = `Necessidade ${index + 1}`;
            }
        });
        nenhuma.style.display = itens.length ? 'none' : 'block';
    }

    function criarSelectCategorias() {
        const select = document.createElement('select');
        select.className = 'form-select categoria';
        select.name = 'categoria[]';
        select.required = true;
        select.innerHTML = `
            <option value="" selected disabled>Selecione</option>
            <option value="Cursos profissionalizantes">Cursos profissionalizantes</option>
            <option value="Equipamentos para casa">Equipamentos para casa (fogão, colchão, televisão, etc.)</option>
            <option value="Medicamentos">Medicamentos</option>
            <option value="Necessidades jurídicas">Necessidades jurídicas</option>
            <option value="Serviços domésticos">Serviços domésticos (elétrica, montagem, etc.)</option>
            <option value="Vaga em escola">Vaga em escola</option>
            <option value="Outras">Outras</option>
        `;
        return select;
    }

    function adicionarNecessidade() {
        const item = document.createElement('div');
        item.className = 'necessidade-item border rounded p-3 mb-3';

        const titulo = document.createElement('h5');
        titulo.className = 'necessidade-titulo mb-3';
        item.appendChild(titulo);

        const row = document.createElement('div');
        row.className = 'row g-2 align-items-end';

        const colDesc = document.createElement('div');
        colDesc.className = 'col-md-6';
        const labelDesc = document.createElement('label');
        labelDesc.className = 'form-label';
        labelDesc.textContent = 'Descrição da necessidade';
        const inputDesc = document.createElement('input');
        inputDesc.type = 'text';
        inputDesc.className = 'form-control descricao';
        inputDesc.name = 'descricao[]';
        inputDesc.setAttribute('autocomplete', 'off');
        colDesc.appendChild(labelDesc);
        colDesc.appendChild(inputDesc);

        const colCat = document.createElement('div');
        colCat.className = 'col-md-5';
        const labelCat = document.createElement('label');
        labelCat.className = 'form-label';
        labelCat.textContent = 'Categoria';
        const selectCat = criarSelectCategorias();
        colCat.appendChild(labelCat);
        colCat.appendChild(selectCat);

        const colRemover = document.createElement('div');
        colRemover.className = 'col-md-1 text-end';
        const btnRemover = document.createElement('button');
        btnRemover.type = 'button';
        btnRemover.className = 'btn btn-link text-danger p-0 btn-remover';
        btnRemover.innerHTML = '<i class="fa fa-trash"></i>';
        btnRemover.addEventListener('click', function() {
            item.remove();
            atualizarNumeracao();
        });
        colRemover.appendChild(btnRemover);

        row.appendChild(colDesc);
        row.appendChild(colCat);
        row.appendChild(colRemover);

        item.appendChild(row);
        lista.appendChild(item);
        atualizarNumeracao();
    }

    btnAdicionar.addEventListener('click', adicionarNecessidade);

    btnFinalizar.addEventListener('click', function() {
        let valido = true;
        lista.querySelectorAll('.necessidade-item').forEach(item => {
            const select = item.querySelector('.categoria');
            if (select && !select.value) {
                select.classList.add('is-invalid');
                valido = false;
            } else if (select) {
                select.classList.remove('is-invalid');
            }
        });
        if (valido) {
            console.log('Dados do formulário etapa 10:', Object.fromEntries(new FormData(form).entries()));
            console.log('Cadastro completo:', window.sessionCadastro);
            const nextUrl = btnFinalizar.getAttribute('data-next-url');
            if (nextUrl) {
                form.action = nextUrl;
                form.method = 'post';
                form.submit();
            }
        }
    });

    document.getElementById("btnVoltar")?.addEventListener("click", function (e) {
        const url = this.dataset.prevUrl;
        if (url) {
            e.preventDefault();
            window.location.href = url;
        }
    });

    atualizarNumeracao();
});
