

function getAuth() {
    const auth = localStorage.getItem('auth');
    return auth ? { 'Authorization': 'Basic ' + auth } : {};
}

function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Display user info with formatted date
async function loadUserInfo() {
    const usernameSpan = document.getElementById('username');
    const memberSinceSpan = document.getElementById('memberSince');
    
    // Get username from localStorage
    const localUser = getCurrentUser();
    if (localUser && localUser.username) {
        usernameSpan.textContent = localUser.username;
    }
    
    // Just show a friendly message instead of trying to fetch date
    memberSinceSpan.textContent = 'Member';
    
    // Optional: Try to fetch from backend but don't worry if it fails
    try {
        const response = await fetch(`${API_URL}/user/me`, {
            headers: getAuth()
        });
        
        if (response.ok) {
            const user = await response.json();
            usernameSpan.textContent = user.username;
            if (user.created_at) {
                const date = new Date(user.created_at);
                if (!isNaN(date.getTime())) {
                    const day = date.getDate().toString().padStart(2, '0');
                    const month = (date.getMonth() + 1).toString().padStart(2, '0');
                    const year = date.getFullYear();
                    memberSinceSpan.textContent = `${day}/${month}/${year}`;
                }
            }
        }
    } catch (error) {
        console.log('Using local data only');
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

if (deleteBtn) {
    deleteBtn.addEventListener('click', () => {
        modal.classList.add('active');
    });
}

if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });
}

if (confirmBtn) {
    confirmBtn.addEventListener('click', () => {
        modal.classList.remove('active');
        deleteAccount();
    });
}

// Close modal if clicking outside
window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.remove('active');
    }
});

// Manage Chats button
const manageChatsBtn = document.getElementById('manageChatsBtn');
if (manageChatsBtn) {
    manageChatsBtn.addEventListener('click', () => {
        window.location.href = 'chat-history.html';
    });
}

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

// Check if user is logged in
if (!localStorage.getItem('user')) {
    window.location.href = 'index.html';
}

// Load user info on page load
loadUserInfo();