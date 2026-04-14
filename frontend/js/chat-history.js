
let currentSessionToDelete = null;

function getAuth() {
    const auth = localStorage.getItem('auth');
    return auth ? { 'Authorization': `Basic ${auth}` } : {};
}

// Load all chat sessions
async function loadSessions() {
    const container = document.getElementById('sessionsList');
    container.innerHTML = 'Loading...';
    
    try {
        const response = await fetch(`${API_URL}/chat/history`, {
            headers: getAuth()
        });
        
        if (response.ok) {
            const data = await response.json();
            const sessions = data.sessions || [];
            
            if (sessions.length === 0) {
                container.innerHTML = '<div class="empty-state">No chat history yet. Start a conversation!</div>';
                return;
            }
            
            container.innerHTML = sessions.map(session => `
                <div class="session-card" data-session-id="${session.session_id}">
                    <div class="session-header">
                        <div>
                            <span class="session-date">${new Date(session.started_at).toLocaleString()}</span>
                            ${session.crisis_detected ? '<span class="crisis-badge">⚠️ Crisis Support Given</span>' : ''}
                        </div>
                        <span>${session.messages?.length || 0} messages</span>
                    </div>
                    <div class="session-preview">
                        ${session.messages && session.messages.length > 0 ? 
                            session.messages.slice(0, 2).map(m => 
                                `<strong>${m.sender}:</strong> ${m.content.substring(0, 50)}...`
                            ).join('<br>') : 
                            'No messages'}
                    </div>
                    <div class="session-actions">
                        <button class="btn-export" onclick="exportSession('${session.session_id}')">📄 Export</button>
                        <button class="btn-delete-session" onclick="confirmDeleteSession('${session.session_id}')">🗑️ Delete</button>
                    </div>
                </div>
            `).join('');
        } else if (response.status === 401) {
            window.location.href = 'index.html';
        } else {
            container.innerHTML = 'Failed to load chat history';
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = 'Cannot connect to server';
    }
}

// Export single session
async function exportSession(sessionId) {
    const format = document.getElementById('exportFormat').value;
    
    try {
        const response = await fetch(`${API_URL}/chat/export/${sessionId}`, {
            headers: getAuth()
        });
        
        if (response.ok) {
            const data = await response.json();
            downloadFile(data, format, sessionId);
        } else {
            alert('Failed to export session');
        }
    } catch (error) {
        alert('Cannot connect to server');
    }
}

// Export all sessions
async function exportAll() {
    const format = document.getElementById('exportFormat').value;
    
    try {
        const response = await fetch(`${API_URL}/chat/export/all`, {
            headers: getAuth()
        });
        
        if (response.ok) {
            const data = await response.json();
            downloadFile(data, format, 'all-chats');
        } else {
            alert('Failed to export chats');
        }
    } catch (error) {
        alert('Cannot connect to server');
    }
}

// Download file helper
function downloadFile(data, format, filename) {
    let content, extension, mimeType;
    
    if (format === 'json') {
        content = JSON.stringify(data, null, 2);
        extension = 'json';
        mimeType = 'application/json';
    } else {
        // TXT format - human readable
        let text = `MuseChum Chat Export\n`;
        text += `Generated: ${new Date().toLocaleString()}\n`;
        text += `${'='.repeat(50)}\n\n`;
        
        if (data.sessions) {
            for (const session of data.sessions) {
                text += `Session: ${new Date(session.started_at).toLocaleString()}\n`;
                text += `${'-'.repeat(30)}\n`;
                for (const msg of session.messages) {
                    text += `[${new Date(msg.timestamp).toLocaleTimeString()}] ${msg.sender.toUpperCase()}: ${msg.content}\n`;
                }
                text += `\n${'='.repeat(50)}\n\n`;
            }
        } else if (data.messages) {
            text += `Session: ${new Date(data.started_at).toLocaleString()}\n`;
            text += `${'-'.repeat(30)}\n`;
            for (const msg of data.messages) {
                text += `[${new Date(msg.timestamp).toLocaleTimeString()}] ${msg.sender.toUpperCase()}: ${msg.content}\n`;
            }
        }
        
        content = text;
        extension = 'txt';
        mimeType = 'text/plain';
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `musechum-${filename}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Confirm delete session
function confirmDeleteSession(sessionId) {
    currentSessionToDelete = sessionId;
    document.getElementById('deleteSessionModal').classList.add('active');
}

// Delete single session
async function deleteSession() {
    if (!currentSessionToDelete) return;
    
    try {
        const response = await fetch(`${API_URL}/chat/session/${currentSessionToDelete}`, {
            method: 'DELETE',
            headers: getAuth()
        });
        
        if (response.ok) {
            document.getElementById('deleteSessionModal').classList.remove('active');
            loadSessions();
        } else {
            alert('Failed to delete session');
        }
    } catch (error) {
        alert('Cannot connect to server');
    }
    currentSessionToDelete = null;
}

// Delete all sessions
async function deleteAllSessions() {
    try {
        const response = await fetch(`${API_URL}/chat/all`, {
            method: 'DELETE',
            headers: getAuth()
        });
        
        if (response.ok) {
            document.getElementById('deleteAllModal').classList.remove('active');
            loadSessions();
        } else {
            alert('Failed to delete all chats');
        }
    } catch (error) {
        alert('Cannot connect to server');
    }
}

// Modal handlers
document.getElementById('exportAllBtn')?.addEventListener('click', exportAll);
document.getElementById('deleteAllBtn')?.addEventListener('click', () => {
    document.getElementById('deleteAllModal').classList.add('active');
});

document.getElementById('cancelSessionDelete')?.addEventListener('click', () => {
    document.getElementById('deleteSessionModal').classList.remove('active');
    currentSessionToDelete = null;
});

document.getElementById('confirmSessionDelete')?.addEventListener('click', deleteSession);

document.getElementById('cancelAllDelete')?.addEventListener('click', () => {
    document.getElementById('deleteAllModal').classList.remove('active');
});

document.getElementById('confirmAllDelete')?.addEventListener('click', deleteAllSessions);

// Load sessions on page load
if (!isLoggedIn()) {
    window.location.href = 'index.html';
}
loadSessions();