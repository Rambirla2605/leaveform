// Global Toast System
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Global Modal System
function showModal(message, onConfirm) {
    let overlay = document.getElementById('modal-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'modal-overlay';
        overlay.className = 'modal-overlay';
        
        const content = document.createElement('div');
        content.className = 'modal-content';
        
        const text = document.createElement('p');
        text.id = 'modal-text';
        
        const buttons = document.createElement('div');
        buttons.className = 'modal-buttons';
        
        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'btn-secondary';
        cancelBtn.textContent = 'Cancel';
        cancelBtn.onclick = closeModal;
        
        const confirmBtn = document.createElement('button');
        confirmBtn.className = 'btn-primary';
        confirmBtn.textContent = 'Confirm';
        confirmBtn.id = 'modal-confirm-btn';
        
        buttons.appendChild(cancelBtn);
        buttons.appendChild(confirmBtn);
        
        content.appendChild(text);
        content.appendChild(buttons);
        overlay.appendChild(content);
        document.body.appendChild(overlay);
    }
    
    document.getElementById('modal-text').textContent = message;
    
    const confirmBtn = document.getElementById('modal-confirm-btn');
    confirmBtn.onclick = () => {
        closeModal();
        if(onConfirm) onConfirm();
    };
    
    overlay.classList.add('active');
}

function closeModal() {
    const overlay = document.getElementById('modal-overlay');
    if (overlay) overlay.classList.remove('active');
}

// Global Auth Fetch
const authFetch = (url, opts = {}) => {
    return fetch(url, {
        ...opts,
        headers: {
            'Authorization': 'Bearer ' + sessionStorage.getItem('token'),
            'Content-Type': 'application/json',
            ...(opts.headers || {})
        }
    });
};

function logout() {
    showModal('Are you sure you want to log out?', () => {
        sessionStorage.clear();
        window.location.href = '/';
    });
}

function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = '🙈';
    } else {
        input.type = 'password';
        icon.textContent = '👁️';
    }
}
