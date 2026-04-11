
// Backend URL (where your FastAPI is running)
const API_URL = 'http://localhost:8000';

// Helper function to get auth header for protected requests
function getAuthHeader() {
    const auth = localStorage.getItem('auth');
    if (!auth) return {};
    return { 'Authorization': `Basic ${auth}` };
}

// Helper function to handle API responses
async function handleResponse(response) {
    if (response.ok) {
        return await response.json();
    }
    
    if (response.status === 401) {
        // Unauthorized - redirect to login
        localStorage.clear();
        window.location.href = '/';
        throw new Error('Session expired');
    }
    
    const error = await response.text();
    throw new Error(error || 'Something went wrong');
}