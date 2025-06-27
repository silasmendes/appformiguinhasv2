// JS para buscar famílias existentes

document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('btnAtenderFamilia');
    const container = document.getElementById('buscaFamiliaContainer');
    const input = document.getElementById('buscaFamiliaInput');
    const lista = document.getElementById('buscaFamiliaResultados');
    let timer = null;

    if (!btn) return;

    btn.addEventListener('click', function (e) {
        e.preventDefault();
        if (container.classList.contains('d-none')) {
            container.classList.remove('d-none');
            input.focus();
        } else {
            container.classList.add('d-none');
            lista.innerHTML = '';
            input.value = '';
        }
    });

    input.addEventListener('input', function () {
        if (timer) clearTimeout(timer);
        timer = setTimeout(async () => {
            const termo = input.value.trim();
            if (termo.length < 2) {
                lista.innerHTML = '';
                return;
            }
            try {
                const resp = await fetch(`/familias/busca?q=${encodeURIComponent(termo)}`);
                if (resp.ok) {
                    const dados = await resp.json();
                    lista.innerHTML = '';
                    if (dados.length === 0) {
                        const li = document.createElement('li');
                        li.className = 'list-group-item';
                        li.textContent = 'Nenhuma família encontrada';
                        lista.appendChild(li);
                    } else {
                        dados.forEach(f => {
                            const li = document.createElement('li');
                            li.className = 'list-group-item';
                            const ultima = f.ultimo_atendimento ? ` - Último atendimento em ${f.ultimo_atendimento}` : '';
                            li.innerHTML = `<a href="/atendimento_familia/${f.familia_id}" class="text-decoration-none">${f.nome_responsavel} - ${f.cpf || ''} - ${f.data_nascimento || ''}${ultima}</a>`;
                            lista.appendChild(li);
                        });
                    }
                }
            } catch (err) {
                console.error(err);
            }
        }, 300);
    });
});
