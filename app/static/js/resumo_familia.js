document.addEventListener('DOMContentLoaded', function() {
    const familySummary = document.getElementById('familySummary');
    const toggleButton = document.getElementById('familySummaryToggle');
    const summaryContent = document.getElementById('familySummaryContent');
    const summaryArrow = document.querySelector('.family-summary-arrow');
    
    // Só executa se os elementos existirem (família foi selecionada)
    if (!familySummary || !toggleButton || !summaryContent) {
        return; // Elementos não encontrados, não fazer nada
    }
    
    // Recuperar estado do localStorage
    const isCollapsed = localStorage.getItem('familySummaryCollapsed') === 'true';
    
    // Aplicar estado inicial SEM animação para evitar efeito visual
    if (isCollapsed) {
        // Adicionar classe para desabilitar transições
        familySummary.classList.add('no-transition');
        
        familySummary.classList.add('collapsed');
        toggleButton.classList.add('collapsed');
        summaryContent.classList.add('collapsed');
        if (summaryArrow) {
            summaryArrow.classList.add('collapsed');
        }
        
        // Remover classe de transição após aplicar o estado
        setTimeout(() => {
            familySummary.classList.remove('no-transition');
        }, 50);
    }
    
    // Função para alternar o estado
    function toggleSummary() {
        const isCurrentlyCollapsed = familySummary.classList.contains('collapsed');
        
        if (isCurrentlyCollapsed) {
            // Expandir
            familySummary.classList.remove('collapsed');
            toggleButton.classList.remove('collapsed');
            summaryContent.classList.remove('collapsed');
            if (summaryArrow) {
                summaryArrow.classList.remove('collapsed');
            }
            localStorage.setItem('familySummaryCollapsed', 'false');
        } else {
            // Recolher
            familySummary.classList.add('collapsed');
            toggleButton.classList.add('collapsed');
            summaryContent.classList.add('collapsed');
            if (summaryArrow) {
                summaryArrow.classList.add('collapsed');
            }
            localStorage.setItem('familySummaryCollapsed', 'true');
        }
    }
    
    // Adicionar event listener para o botão
    toggleButton.addEventListener('click', toggleSummary);
    
    // Também permitir clicar no cabeçalho inteiro
    const summaryHeader = document.querySelector('.family-summary-header');
    if (summaryHeader) {
        summaryHeader.addEventListener('click', toggleSummary);
    }
});
