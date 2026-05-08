const API_URL = 'http://localhost:8000';
let conversationContext = [];
let userName = null;

function getAuth() {
    const auth = localStorage.getItem('auth');
    return auth ? { 'Authorization': 'Basic ' + auth } : {};
}

function addMessage(text, sender) {
    const container = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    msgDiv.innerHTML = `<div class="message-content">${escapeHtml(text)}</div>`;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
    
    //Store in context
    conversationContext.push({ sender: sender, message: text });
    if (conversationContext.length > 10) conversationContext.shift();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessage(message, 'user');
    input.value = '';
    
    //Check if user mentions their name
    const nameMatch = message.match(/my name is (\w+)|i'm (\w+)|i am (\w+)/i);
    if (nameMatch) {
        userName = nameMatch[1] || nameMatch[2] || nameMatch[3];
    }
    
    try {
        const response = await fetch(`${API_URL}/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuth()
            },
            body: JSON.stringify({ message: message })
        });
        
        if (response.ok) {
            const data = await response.json();
            let reply = data.reply;
            
            //Inject user name if known and not already in reply
            if (userName && !reply.includes(userName) && Math.random() > 0.7) {
                reply = `${userName}, ${reply.toLowerCase()}`;
            }
            
            addMessage(reply, 'bot');
            
            if (data.category === 'CRISIS') {
                document.getElementById('crisisAlert').classList.remove('hidden');
            } else {
                document.getElementById('crisisAlert').classList.add('hidden');
            }
        } else if (response.status === 401) {
            addMessage('Session expired. Please login again.', 'bot');
            setTimeout(() => window.location.href = 'index.html', 2000);
        } else {
            addMessage('Sorry, I had trouble responding. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Chat error:', error);
        addMessage('Cannot connect to server. Is the backend running?', 'bot');
    }
}

function initChat() {
    if (!localStorage.getItem('user')) {
        window.location.href = 'index.html';
    }
    
    //Try to get user name from stored user data
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user.username) {
        userName = user.username;
    }
}

//Make functions global
window.sendMessage = sendMessage;