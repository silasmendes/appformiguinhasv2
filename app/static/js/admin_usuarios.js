// JavaScript para página de gestão de usuários

document.addEventListener('DOMContentLoaded', function() {

    // Adicionar indicadores de status
    addStatusIndicators();

    // Configurar modais de ação
    setupResetSenhaModal();
    setupDeleteUsuarioModal();
    
    // Validação do formulário
    setupFormValidation();
    
    // Adicionar animações
    addAnimations();
    
    // Tooltip para botões
    initializeTooltips();

    // Desabilitar campo de expiração para administradores
    toggleExpiresField();
    
    // Event listener para quando o modal for aberto
    const modalNovo = document.getElementById('modalNovo');
    if (modalNovo) {
        modalNovo.addEventListener('shown.bs.modal', function() {
            toggleExpiresField();
        });
        
        // Resetar formulário quando modal for fechado
        modalNovo.addEventListener('hidden.bs.modal', function() {
            const form = modalNovo.querySelector('form');
            if (form) {
                form.reset();
                toggleExpiresField(); // Reaplica o estado inicial
            }
        });
    }
});

function addStatusIndicators() {
    const tbody = document.querySelector('table tbody');
    if (!tbody) return;
    
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 5) {
            const tipoCell = cells[2];
            const expiracaoCell = cells[3];
            const ultimoLoginCell = cells[4];
            
            // Badge para tipo de usuário
            const tipo = tipoCell.textContent.trim();
            const badgeClass = tipo === 'admin' ? 'badge-admin' : 'badge-temporario';
            tipoCell.innerHTML = `<span class="badge-tipo ${badgeClass}">${tipo}</span>`;
            
            // Indicador de status baseado na expiração e último login
            const expiracao = expiracaoCell.textContent.trim();
            const ultimoLogin = ultimoLoginCell.textContent.trim();
            
            let statusClass = 'status-ativo';
            if (expiracao && new Date(expiracao) < new Date()) {
                statusClass = 'status-expirado';
            } else if (!ultimoLogin) {
                statusClass = 'status-nunca-logou';
            }
            
            // Adicionar indicador visual no início da linha
            const loginCell = cells[0];
            loginCell.innerHTML = `<span class="status-indicator ${statusClass}"></span>${loginCell.textContent}`;
        }
    });
}


function setupFormValidation() {
    const form = document.querySelector('#modalNovo form');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearError);
    });
    
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        inputs.forEach(input => {
            if (!validateField({ target: input })) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
        }
    });
}

function validateField(e) {
    const input = e.target;
    const value = input.value.trim();
    
    // Remover erro anterior
    clearError({ target: input });
    
    if (input.hasAttribute('required') && !value) {
        showFieldError(input, 'Este campo é obrigatório');
        return false;
    }
    
    // Validações específicas
    if (input.name === 'login' && value) {
        if (value.length < 3) {
            showFieldError(input, 'Login deve ter pelo menos 3 caracteres');
            return false;
        }
        if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            showFieldError(input, 'Login deve conter apenas letras, números e underscore');
            return false;
        }
    }
    
    if (input.name === 'senha' && value) {
        if (value.length < 6) {
            showFieldError(input, 'Senha deve ter pelo menos 6 caracteres');
            return false;
        }
    }
    
    return true;
}

function showFieldError(input, message) {
    input.classList.add('is-invalid');
    
    let feedback = input.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        input.parentNode.appendChild(feedback);
    }
    
    feedback.textContent = message;
}

function clearError(e) {
    const input = e.target;
    input.classList.remove('is-invalid');
    
    const feedback = input.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

function addAnimations() {
    // Adicionar animação de entrada para linhas da tabela
    const rows = document.querySelectorAll('table tbody tr');
    
    rows.forEach((row, index) => {
        row.style.animationDelay = `${index * 0.1}s`;
        row.classList.add('fade-in-up');
    });
    
    // Animação para botões
    const actionButtons = document.querySelectorAll('.btn-action');
    actionButtons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

function toggleExpiresField() {
    // Função simplificada - a lógica principal está no script inline do HTML
    console.log('toggleExpiresField chamada do arquivo JS');
}

function setupResetSenhaModal() {
    const buttons = document.querySelectorAll('.btn-reset-senha');
    const modalEl = document.getElementById('modalResetSenha');
    if (!modalEl) return;

    const modal = new bootstrap.Modal(modalEl);
    const form = document.getElementById('formResetSenha');
    const senha = document.getElementById('novaSenha');
    const confirma = document.getElementById('confirmaSenha');
    const erro = document.getElementById('resetSenhaErro');
    const titulo = document.getElementById('modalResetTitulo');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            form.action = btn.dataset.action;
            if (titulo) {
                titulo.textContent = `Resetar senha de ${btn.dataset.userName}`;
            }
            senha.value = '';
            confirma.value = '';
            erro.classList.add('d-none');
            modal.show();
        });
    });

    form.addEventListener('submit', function(e) {
        if (senha.value !== confirma.value) {
            e.preventDefault();
            erro.textContent = 'As senhas não coincidem';
            erro.classList.remove('d-none');
        }
    });
}

function setupDeleteUsuarioModal() {
    const buttons = document.querySelectorAll('.btn-delete-usuario');
    const modalEl = document.getElementById('modalDeleteUsuario');
    if (!modalEl) return;

    const modal = new bootstrap.Modal(modalEl);
    const form = document.getElementById('formDeleteUsuario');
    const info = document.getElementById('deleteUsuarioInfo');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            form.action = btn.dataset.action;
            if (info) {
                info.textContent = `${btn.dataset.userName} (${btn.dataset.userLogin})`;
            }
            modal.show();
        });
    });
}

function initializeTooltips() {
    // Inicializar tooltips do Bootstrap se disponível
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Adicionar títulos informativos
    document.querySelectorAll('.btn-reset-senha').forEach(btn => {
        btn.setAttribute('title', 'Gerar nova senha para este usuário');
    });
    document.querySelectorAll('.btn-delete-usuario').forEach(btn => {
        btn.setAttribute('title', 'Excluir este usuário');
    });
}

// Utilitário para selecionar elementos por texto
function findByText(selector, text) {
    return Array.from(document.querySelectorAll(selector)).filter(el => 
        el.textContent.includes(text)
    );
}

// Busca em tempo real (se necessário no futuro)
function initializeSearch() {
    const searchInput = document.getElementById('searchUsers');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = document.querySelectorAll('table tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}
