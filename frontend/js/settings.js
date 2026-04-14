
function getAuth() {
    const auth = localStorage.getItem('auth');
    return auth ? { 'Authorization': `Basic ${auth}` } : {};
}

// Display user info
async function loadUserInfo() {
    const user = getCurrentUser();
    if (user) {
        document.getElementById('username').textContent = user.username;
        document.getElementById('memberSince').textContent = user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown';
    }
}

// Delete account function
async function deleteAccount() {
    try {
        const response = await fetch(`${API_URL}/user/`, {
            method: 'DELETE',
            headers: getAuth()
        });
        
        if (response.ok) {
            // Clear local storage
            localStorage.clear();
            // Show message before redirect
            alert('Your account has been permanently deleted.');
            window.location.href = 'index.html';
        } else if (response.status === 401) {
            alert('Session expired. Please login again.');
            window.location.href = 'index.html';
        } else {
            const error = await response.text();
            alert('Failed to delete account: ' + error);
        }
    } catch (error) {
        console.error('Delete account error:', error);
        alert('Cannot connect to server. Is the backend running?');
    }
}

// Modal handling
const modal = document.getElementById('deleteModal');
const deleteBtn = document.getElementById('deleteAccountBtn');
const cancelBtn = document.getElementById('cancelDeleteBtn');
const confirmBtn = document.getElementById('confirmDeleteBtn');

deleteBtn.addEventListener('click', () => {
    modal.classList.add('active');
});

cancelBtn.addEventListener('click', () => {
    modal.classList.remove('active');
});

confirmBtn.addEventListener('click', () => {
    modal.classList.remove('active');
    deleteAccount();
});

// Close modal if clicking outside
window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.remove('active');
    }
});

// Manage Chats button
document.getElementById('manageChatsBtn').addEventListener('click', () => {
    window.location.href = 'chat-history.html';
});

// Load user info on page load
loadUserInfo();