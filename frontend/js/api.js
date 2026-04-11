
const API_URL = 'http://localhost:8000';

function getAuthHeader() {
    const auth = localStorage.getItem('auth');
    if (!auth) return {};
    return { 'Authorization': `Basic ${auth}` };
}

function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

function isLoggedIn() {
    return localStorage.getItem('user') !== null;
}