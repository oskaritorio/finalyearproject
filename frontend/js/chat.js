// ========================================
// CHAT FUNCTIONS
// ========================================

let currentCrisis = false;

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Display user message
    addMessage(message, 'user');
    input.value = '';
    
    // Send to backend
    try {
        const response = await fetch(`${API_URL}/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeader()
            },
            body: JSON.stringify({ message: message })
        });
        
        if (response.ok) {
            const data = await response.json();
            addMessage(data.reply, 'bot');
            
            // Check for crisis
            if (data.category === 'CRISIS') {
                currentCrisis = true;
                document.getElementById('crisisAlert').classList.remove('hidden');
            } else {
                document.getElementById('crisisAlert').classList.add('hidden');
            }
        } else if (response.status === 401) {
            alert('Session expired. Please login again.');
            window.location.href = 'index.html';
        } else {
            addMessage("Sorry, I'm having trouble responding right now.", 'bot');
        }
    } catch (error) {
        console.error('Chat error:', error);
        addMessage("Cannot connect to the server. Is the backend running?", 'bot');
    }
}

function addMessage(text, sender) {
    const container = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = `<div class="message-content">${escapeHtml(text)}</div>`;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function initChat() {
    if (!isLoggedIn()) {
        window.location.href = 'index.html';
    }
}