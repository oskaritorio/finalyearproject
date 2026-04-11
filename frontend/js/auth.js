
// Login function
async function login(username, password) {
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const user = await response.json();
            
            // Save user data to localStorage
            localStorage.setItem('user', JSON.stringify(user));
            localStorage.setItem('auth', btoa(`${username}:${password}`));
            
            return { success: true, user };
        } else {
            const error = await response.text();
            return { success: false, error: 'Invalid username or password' };
        }
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: 'Cannot connect to server. Is the backend running?' };
    }
}

// Logout function
function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

// Check if user is logged in
function isLoggedIn() {
    return localStorage.getItem('user') !== null;
}

// Get current user
function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Redirect to login if not authenticated
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/';
    }
}