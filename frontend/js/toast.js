
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</div>
        <div class="toast-message">${message}</div>
        <div class="toast-close">&times;</div>
    `;
    document.body.appendChild(toast);
    
    //Auto-remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
    
    //Close button
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
}

