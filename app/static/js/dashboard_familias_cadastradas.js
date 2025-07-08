// Dashboard Famílias Cadastradas JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const downloadBtn = document.getElementById('downloadBtn');
    const confirmModal = document.getElementById('confirmModal');
    const confirmCheckbox = document.getElementById('confirmCheckbox');
    const confirmDownloadBtn = document.getElementById('confirmDownloadBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const currentDateElement = document.getElementById('current-date');
    
    // Definir data atual
    const today = new Date();
    const formattedDate = today.toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    currentDateElement.textContent = formattedDate;
    
    // Event Listeners
    downloadBtn.addEventListener('click', showConfirmationModal);
    cancelBtn.addEventListener('click', hideConfirmationModal);
    confirmCheckbox.addEventListener('change', toggleConfirmButton);
    confirmDownloadBtn.addEventListener('click', initiateDownload);
    
    // Fechar modal ao clicar no overlay
    confirmModal.addEventListener('click', function(e) {
        if (e.target === confirmModal) {
            hideConfirmationModal();
        }
    });
    
    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && confirmModal.classList.contains('active')) {
            hideConfirmationModal();
        }
    });
    
    /**
     * Exibe o modal de confirmação
     */
    function showConfirmationModal() {
        confirmModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Reset do checkbox e botão
        confirmCheckbox.checked = false;
        confirmDownloadBtn.disabled = true;
        
        // Foco no checkbox para acessibilidade
        setTimeout(() => {
            confirmCheckbox.focus();
        }, 300);
    }
    
    /**
     * Oculta o modal de confirmação
     */
    function hideConfirmationModal() {
        confirmModal.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    /**
     * Alterna o estado do botão de confirmação baseado no checkbox
     */
    function toggleConfirmButton() {
        confirmDownloadBtn.disabled = !confirmCheckbox.checked;
        
        if (confirmCheckbox.checked) {
            confirmDownloadBtn.classList.remove('btn-secondary');
            confirmDownloadBtn.classList.add('btn-danger');
        } else {
            confirmDownloadBtn.classList.remove('btn-danger');
            confirmDownloadBtn.classList.add('btn-secondary');
        }
    }
    
    /**
     * Inicia o processo de download
     */
    function initiateDownload() {
        // Ocultar modal
        hideConfirmationModal();
        
        // Mostrar loading
        showLoading();
        
        // Fazer download
        performDownload();
    }
    
    /**
     * Mostra o overlay de loading
     */
    function showLoading() {
        loadingOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    /**
     * Oculta o overlay de loading
     */
    function hideLoading() {
        loadingOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    /**
     * Executa o download do arquivo
     */
    function performDownload() {
        // Criar elemento de link temporário para download
        const downloadUrl = '/dashboard/familias-cadastradas/download';
        
        // Usar fetch para fazer a requisição
        fetch(downloadUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição: ' + response.status);
            }
            return response.blob();
        })
        .then(blob => {
            // Criar URL temporária para o blob
            const url = window.URL.createObjectURL(blob);
            
            // Criar elemento de link temporário
            const link = document.createElement('a');
            link.href = url;
            
            // Gerar nome do arquivo com data atual
            const now = new Date();
            const dateStr = now.getFullYear() + '_' + 
                          String(now.getMonth() + 1).padStart(2, '0') + '_' + 
                          String(now.getDate()).padStart(2, '0');
            link.download = `migracao_familias_${dateStr}.xlsx`;
            
            // Adicionar ao DOM, clicar e remover
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Limpar URL temporária
            window.URL.revokeObjectURL(url);
            
            // Ocultar loading
            hideLoading();
            
            // Mostrar mensagem de sucesso
            showSuccessMessage();
        })
        .catch(error => {
            console.error('Erro no download:', error);
            hideLoading();
            showErrorMessage(error.message);
        });
    }
    
    /**
     * Mostra mensagem de sucesso
     */
    function showSuccessMessage() {
        // Criar toast de sucesso
        const toast = createToast('success', 'Download realizado com sucesso!', 
            'O arquivo foi gerado e salvo em seus downloads.');
        showToast(toast);
    }
    
    /**
     * Mostra mensagem de erro
     */
    function showErrorMessage(message) {
        const toast = createToast('error', 'Erro no download', 
            `Ocorreu um erro ao gerar o arquivo: ${message}`);
        showToast(toast);
    }
    
    /**
     * Cria um elemento de toast
     */
    function createToast(type, title, message) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
        const bgColor = type === 'success' ? '#28a745' : '#dc3545';
        
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon" style="background-color: ${bgColor}">
                    <i class="${icon}"></i>
                </div>
                <div class="toast-text">
                    <div class="toast-title">${title}</div>
                    <div class="toast-message">${message}</div>
                </div>
                <button class="toast-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Event listener para fechar
        toast.querySelector('.toast-close').addEventListener('click', () => {
            hideToast(toast);
        });
        
        return toast;
    }
    
    /**
     * Mostra o toast
     */
    function showToast(toast) {
        // Adicionar estilos CSS se não existirem
        if (!document.getElementById('toast-styles')) {
            const styles = document.createElement('style');
            styles.id = 'toast-styles';
            styles.textContent = `
                .toast {
                    position: fixed;
                    top: 2rem;
                    right: 2rem;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    z-index: 1002;
                    transform: translateX(400px);
                    transition: all 0.3s ease;
                    max-width: 400px;
                    border-left: 4px solid #28a745;
                }
                .toast.toast-error {
                    border-left-color: #dc3545;
                }
                .toast.show {
                    transform: translateX(0);
                }
                .toast-content {
                    display: flex;
                    align-items: flex-start;
                    padding: 1rem;
                    gap: 1rem;
                }
                .toast-icon {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    flex-shrink: 0;
                }
                .toast-text {
                    flex: 1;
                }
                .toast-title {
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 0.25rem;
                }
                .toast-message {
                    color: #666;
                    font-size: 0.9rem;
                    line-height: 1.4;
                }
                .toast-close {
                    background: none;
                    border: none;
                    color: #999;
                    cursor: pointer;
                    padding: 0.25rem;
                    border-radius: 4px;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }
                .toast-close:hover {
                    background: #f0f0f0;
                    color: #333;
                }
                @media (max-width: 768px) {
                    .toast {
                        left: 1rem;
                        right: 1rem;
                        max-width: none;
                        transform: translateY(-100px);
                    }
                    .toast.show {
                        transform: translateY(0);
                    }
                }
            `;
            document.head.appendChild(styles);
        }
        
        // Adicionar ao DOM
        document.body.appendChild(toast);
        
        // Mostrar com animação
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Auto hide após 5 segundos
        setTimeout(() => {
            hideToast(toast);
        }, 5000);
    }
    
    /**
     * Oculta o toast
     */
    function hideToast(toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
    
    // Animações de entrada para os elementos da página
    function initPageAnimations() {
        const elements = document.querySelectorAll('.download-card, .warning-card');
        
        elements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                element.style.transition = 'all 0.6s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * 200);
        });
    }
    
    // Inicializar animações
    initPageAnimations();
});
