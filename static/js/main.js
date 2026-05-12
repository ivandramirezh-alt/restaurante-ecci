// main.js — El Buen Sabor

// Lógica de Toasts
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = { success: 'fa-check-circle', danger: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' }[type] || 'fa-info-circle';
    toast.innerHTML = `<i class="fas ${icon}"></i><div class="toast-content">${message}</div>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
    toast.onclick = () => toast.remove();
}

// Lógica de Confirmación Personalizada (Coqueta)
let pendingAction = null;

function customConfirm(message, callback) {
    const modal = document.getElementById('custom-confirm');
    const msgEl = document.getElementById('confirm-msg');
    const okBtn = document.getElementById('confirm-ok');
    const cancelBtn = document.getElementById('confirm-cancel');

    msgEl.textContent = message;
    modal.classList.add('active');
    pendingAction = callback;

    const close = () => modal.classList.remove('active');

    okBtn.onclick = () => { close(); if(pendingAction) pendingAction(); };
    cancelBtn.onclick = close;
    modal.onclick = (e) => { if(e.target === modal) close(); };
}

// Interceptar clicks con data-confirm
document.addEventListener('click', e => {
    const target = e.target.closest('[data-confirm]');
    if (target) {
        e.preventDefault();
        const msg = target.dataset.confirm;
        const url = target.getAttribute('href');
        
        customConfirm(msg, () => {
            if (url) window.location.href = url;
            else if (target.form) target.form.submit();
        });
    }
});

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.flash-message-data');
    flashMessages.forEach(msg => {
        showToast(msg.dataset.message, msg.dataset.category);
    });
});
