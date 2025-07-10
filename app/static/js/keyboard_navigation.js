// Navegação por teclado para etapas - feedback visual
document.addEventListener('DOMContentLoaded', function() {
    console.log('Keyboard navigation loaded');
    
    // Criar tooltip para mostrar as teclas de atalho
    function createKeyboardTooltip() {
        const tooltip = document.createElement('div');
        tooltip.id = 'keyboard-tooltip';
        tooltip.className = 'keyboard-tooltip';
        tooltip.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 13px;
            z-index: 1000;
            display: none;
            max-width: 280px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.2);
        `;
        
        tooltip.innerHTML = `
            <div style="margin-bottom: 8px;"><strong>🎯 Navegação Rápida</strong></div>
            <div style="margin-bottom: 4px;">ALT + 1-9: Etapas 1-9</div>
            <div style="margin-bottom: 4px;">ALT + Q: Etapa 10</div>
            <div>ALT + W: Etapa 11</div>
        `;
        
        document.body.appendChild(tooltip);
        return tooltip;
    }
    
    // Mostrar tooltip quando ALT for pressionado
    let altPressed = false;
    let tooltipTimeout;
    const tooltip = createKeyboardTooltip();
    
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Alt' && !altPressed) {
            altPressed = true;
            
            // Verificar se navegação está disponível
            if (window.sessionCadastro && window.sessionCadastro.novo_cadastro === 0) {
                console.log('Mostrando tooltip de navegação');
                tooltip.style.display = 'block';
                
                // Auto-hide após 4 segundos
                tooltipTimeout = setTimeout(() => {
                    tooltip.style.display = 'none';
                }, 4000);
            }
        }
    });
    
    document.addEventListener('keyup', function(event) {
        if (event.key === 'Alt') {
            altPressed = false;
            tooltip.style.display = 'none';
            
            if (tooltipTimeout) {
                clearTimeout(tooltipTimeout);
            }
        }
    });
    
    // Esconder tooltip quando perder foco
    window.addEventListener('blur', function() {
        altPressed = false;
        tooltip.style.display = 'none';
        if (tooltipTimeout) {
            clearTimeout(tooltipTimeout);
        }
    });
    
    // Adicionar indicador visual na timeline quando ALT estiver pressionado
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Alt' && window.sessionCadastro && window.sessionCadastro.novo_cadastro === 0) {
            const circles = document.querySelectorAll('.timeline .circle');
            circles.forEach((circle, index) => {
                circle.style.boxShadow = '0 0 15px rgba(0, 123, 255, 0.6)';
                circle.style.transform = 'scale(1.1)';
                circle.style.transition = 'all 0.2s ease';
            });
        }
    });
    
    document.addEventListener('keyup', function(event) {
        if (event.key === 'Alt') {
            const circles = document.querySelectorAll('.timeline .circle');
            circles.forEach(circle => {
                circle.style.boxShadow = '';
                circle.style.transform = '';
            });
        }
    });
    
    // Log para debug
    console.log('Keyboard navigation initialized. Session state:', window.sessionCadastro);
});
