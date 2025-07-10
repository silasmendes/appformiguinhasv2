document.addEventListener('DOMContentLoaded', function() {
    const familySummary = document.getElementById('familySummary');
    const toggleButton = document.getElementById('familySummaryToggle');
    const summaryContent = document.getElementById('familySummaryContent');
    const summaryArrow = document.querySelector('.family-summary-arrow');
    
    // Só executa se os elementos existirem (família foi selecionada)
    if (!familySummary || !toggleButton || !summaryContent) {
        return; // Elementos não encontrados, não fazer nada
    }
    
    // Função para alternar o estado via Flask
    function toggleSummary() {
        // Fazer requisição POST para a rota Flask
        fetch('/toggle_resumo_familia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || ''
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Atualizar o estado visual baseado na resposta do servidor
                const isExpanded = data.resumo_expandido === 1;
                
                if (isExpanded) {
                    // Expandir
                    familySummary.classList.remove('collapsed');
                    toggleButton.classList.remove('collapsed');
                    summaryContent.classList.remove('collapsed');
                    if (summaryArrow) {
                        summaryArrow.classList.remove('collapsed');
                    }
                } else {
                    // Recolher
                    familySummary.classList.add('collapsed');
                    toggleButton.classList.add('collapsed');
                    summaryContent.classList.add('collapsed');
                    if (summaryArrow) {
                        summaryArrow.classList.add('collapsed');
                    }
                }
            }
        })
        .catch(error => {
            console.error('Erro ao alternar resumo da família:', error);
        });
    }
    
    // Adicionar event listener para o botão
    toggleButton.addEventListener('click', toggleSummary);
    
    // Também permitir clicar no cabeçalho inteiro
    const summaryHeader = document.querySelector('.family-summary-header');
    if (summaryHeader) {
        summaryHeader.addEventListener('click', toggleSummary);
    }
});
