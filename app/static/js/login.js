// Login Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.login-form');
    const submitBtn = document.querySelector('.btn-login');
    const inputs = document.querySelectorAll('.form-control');
    
    // Adiciona efeitos visuais aos inputs
    inputs.forEach(input => {
        // Efeito de foco nos labels
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Verifica se já tem valor ao carregar a página
        if (input.value) {
            input.parentElement.classList.add('focused');
        }
    });
    
    // Efeito de loading no botão de submit
    let isSubmitting = false;
    if (form && submitBtn) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            if (isSubmitting) return;
            const loginInput = document.getElementById('login');
            const senhaInput = document.getElementById('senha');
            if (!loginInput.value.trim() || !senhaInput.value.trim()) {
                return;
            }
            isSubmitting = true;
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
            const span = submitBtn.querySelector('span');
            if (span) span.textContent = 'Entrando...';

            try {
                const resp = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ login: loginInput.value, senha: senhaInput.value })
                });
                if (resp.ok) {
                    const data = await resp.json();
                    sessionStorage.setItem('access_token', data.access_token);
                    window.location.href = '/';
                } else {
                    const erro = await resp.json().catch(() => ({ mensagem: 'Erro' }));
                    alert(erro.mensagem || 'Falha no login');
                }
            } catch (err) {
                alert('Erro ao conectar ao servidor.');
            }
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
            if (span) span.textContent = 'Entrar';
            isSubmitting = false;
        });
    }
    
    // Auto-dismiss dos alertas após 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.btn-close');
        if (closeBtn) {
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.style.opacity = '0';
                    alert.style.transform = 'translateY(-20px)';
                    setTimeout(() => {
                        alert.remove();
                    }, 300);
                }
            }, 5000);
        }
    });
    
    // Adiciona animação suave ao fechar alertas manualmente
    const closeButtons = document.querySelectorAll('.btn-close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        });
    });
    
    // Validação visual dos campos
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
            }
        });
    });
    
    // Efeito de hover no logo
    const logo = document.querySelector('.login-logo img');
    if (logo) {
        let hoverCount = 0;
        logo.addEventListener('mouseenter', function() {
            hoverCount++;
            if (hoverCount === 5) { // Easter egg após 5 hovers
                this.style.animation = 'spin 1s ease-in-out';
                setTimeout(() => {
                    this.style.animation = '';
                }, 1000);
                hoverCount = 0;
            }
        });
    }
    
    
    // Adiciona efeito de ripple nos botões
    function createRipple(event) {
        const button = event.currentTarget;
        const circle = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;
        
        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
        circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
        circle.classList.add('ripple');
        
        const ripple = button.getElementsByClassName('ripple')[0];
        if (ripple) {
            ripple.remove();
        }
        
        button.appendChild(circle);
    }
    
    if (submitBtn) {
        submitBtn.addEventListener('click', createRipple);
    }
});

// CSS para o efeito ripple (será injetado via JavaScript)
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    .btn-login {
        position: relative;
        overflow: hidden;
    }
    
    .btn-login .ripple {
        position: absolute;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 600ms linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .form-group.focused .form-label {
        color: var(--primary-color);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    .form-control.is-valid {
        border-color: #198754;
        box-shadow: 0 0 0 3px rgba(25, 135, 84, 0.1);
    }
`;
document.head.appendChild(rippleStyle);
