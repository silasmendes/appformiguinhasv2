// JavaScript para página de gestão de usuários

document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar estatísticas
    initializeStats();
    
    // Adicionar indicadores de status
    addStatusIndicators();
    
    // Melhorar confirmação de exclusão
    enhanceDeleteConfirmation();
    
    // Validação do formulário
    setupFormValidation();
    
    // Adicionar animações
    addAnimations();
    
    // Tooltip para botões
    initializeTooltips();
});

function initializeStats() {
    const tbody = document.querySelector('table tbody');
    if (!tbody) return;
    
    const rows = tbody.querySelectorAll('tr');
    const totalUsers = rows.length;
    let adminCount = 0;
    let tempCount = 0;
    let expiredCount = 0;
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 4) {
            const tipo = cells[2].textContent.trim();
            const expiracao = cells[3].textContent.trim();
            
            if (tipo === 'admin') adminCount++;
            if (tipo === 'temporario') tempCount++;
            
            // Verificar se expirou
            if (expiracao && new Date(expiracao) < new Date()) {
                expiredCount++;
            }
        }
    });
    
    // Criar cards de estatísticas
    createStatsCards(totalUsers, adminCount, tempCount, expiredCount);
}

function createStatsCards(total, admin, temp, expired) {
    const header = document.querySelector('h2');
    if (!header) return;
    
    const statsHTML = `
        <div class="stats-cards row g-3 mb-4 fade-in-up">
            <div class="col-md-3 col-sm-6">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <h3 class="stat-number">${total}</h3>
                    <p class="stat-label">Total de Usuários</p>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-user-shield"></i>
                    </div>
                    <h3 class="stat-number">${admin}</h3>
                    <p class="stat-label">Administradores</p>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-user-clock"></i>
                    </div>
                    <h3 class="stat-number">${temp}</h3>
                    <p class="stat-label">Temporários</p>
                </div>
            </div>
            <div class="col-md-3 col-sm-6">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-user-times"></i>
                    </div>
                    <h3 class="stat-number">${expired}</h3>
                    <p class="stat-label">Expirados</p>
                </div>
            </div>
        </div>
    `;
    
    header.insertAdjacentHTML('afterend', statsHTML);
}

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

function enhanceDeleteConfirmation() {
    const deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    
    deleteForms.forEach(form => {
        form.removeAttribute('onsubmit');
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const row = form.closest('tr');
            const userName = row.querySelector('td:nth-child(2)').textContent.trim();
            
            // Criar modal de confirmação personalizado
            showDeleteConfirmation(userName, () => {
                form.submit();
            });
        });
    });
}

function showDeleteConfirmation(userName, callback) {
    const modalHTML = `
        <div class="modal fade" id="confirmDeleteModal" tabindex="-1">
            <div class="modal-dialog modal-sm">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Confirmar Exclusão
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-3">
                            <i class="fas fa-user-times text-danger" style="font-size: 3rem;"></i>
                        </div>
                        <p class="mb-1">Tem certeza que deseja excluir o usuário:</p>
                        <strong>${userName}</strong>
                        <p class="text-muted mt-2 mb-0">Esta ação não pode ser desfeita.</p>
                    </div>
                    <div class="modal-footer justify-content-center">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-danger" id="confirmDeleteBtn">
                            <i class="fas fa-trash me-1"></i>
                            Excluir
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal anterior se existir
    const existingModal = document.getElementById('confirmDeleteModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    modal.show();
    
    document.getElementById('confirmDeleteBtn').addEventListener('click', () => {
        modal.hide();
        callback();
    });
    
    // Remover modal após fechar
    document.getElementById('confirmDeleteModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
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

function initializeTooltips() {
    // Inicializar tooltips do Bootstrap se disponível
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Adicionar títulos informativos
    const resetBtns = document.querySelectorAll('button[type="submit"]:contains("Resetar")');
    resetBtns.forEach(btn => {
        btn.setAttribute('title', 'Gerar nova senha para este usuário');
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
