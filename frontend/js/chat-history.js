// ========================================
// CHAT HISTORY - EXPORT & DELETE
// ========================================

const API_URL = 'http://localhost:8000';
let currentSessionToDelete = null;

function getAuth() {
    const auth = localStorage.getItem('auth');
    return auth ? { 'Authorization': 'Basic ' + auth } : {};
}

function isLoggedIn() {
    return localStorage.getItem('user') !== null;
}

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

// Load all chat sessions
async function loadSessions() {
    const container = document.getElementById('sessionsList');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Loading...</div>';
    
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
            
            let html = '';
            for (let i = 0; i < sessions.length; i++) {
                const s = sessions[i];
                const date = new Date(s.started_at).toLocaleString();
                const msgCount = s.messages ? s.messages.length : 0;
                const crisisBadge = s.crisis_detected ? '<span class="crisis-badge">⚠️ Crisis Support Given</span>' : '';
                
                html += `
                    <div class="session-card" data-session-id="${s.session_id}">
                        <div class="session-header">
                            <div>
                                <span class="session-date">${date}</span>
                                ${crisisBadge}
                            </div>
                            <span>${msgCount} messages</span>
                        </div>
                        <div class="session-preview">
                            ${s.messages && s.messages.length > 0 ? 
                                s.messages.slice(0, 2).map(m => 
                                    `<strong>${m.sender}:</strong> ${(m.content || '').substring(0, 50)}...`
                                ).join('<br>') : 
                                'No messages'}
                        </div>
                        <div class="session-actions">
                            <button class="btn-export" onclick="exportSession('${s.session_id}')">📄 Export</button>
                            <button class="btn-delete" onclick="confirmDeleteSession('${s.session_id}')">🗑️ Delete</button>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        } else if (response.status === 401) {
            window.location.href = 'index.html';
        } else {
            container.innerHTML = '<div class="empty-state">Failed to load chat history</div>';
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
        container.innerHTML = '<div class="empty-state">Cannot connect to server</div>';
    }
}

//Export single session
async function exportSession(sessionId) {
    const format = document.getElementById('exportFormat').value;
    
    try {
        const response = await fetch(`${API_URL}/chat/export/${sessionId}`, {
            headers: getAuth()
        });
        
        if (response.ok) {
            const data = await response.json();
            downloadFile(data, format, `session-${sessionId.substring(0, 8)}`);
        } else {
            alert('Failed to export session');
        }
    } catch (error) {
        console.error('Export error:', error);
        alert('Cannot connect to server');
    }
}

//Export all sessions
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
        console.error('Export error:', error);
        alert('Cannot connect to server');
    }
}

//Download file helper
function downloadFile(data, format, filename) {
    let content, extension, mimeType;
    
    if (format === 'json') {
        content = JSON.stringify(data, null, 2);
        extension = 'json';
        mimeType = 'application/json';
    } else {
       
        let text = `MuseChum Chat Export\n`;
        text += `Generated: ${new Date().toLocaleString()}\n`;
        text += `${'='.repeat(50)}\n\n`;
        
       
        if (data.sessions && data.sessions.length > 0) {
            for (const session of data.sessions) {
                text += `Session: ${new Date(session.started_at).toLocaleString()}\n`;
                text += `Session ID: ${session.session_id}\n`;
                text += `Crisis Detected: ${session.crisis_detected ? 'Yes' : 'No'}\n`;
                text += `${'-'.repeat(30)}\n`;
                
                if (session.messages && session.messages.length > 0) {
                    for (const msg of session.messages) {
                        const time = new Date(msg.timestamp).toLocaleTimeString();
                        text += `[${time}] ${msg.sender.toUpperCase()}: ${msg.content}\n`;
                    }
                } else {
                    text += `No messages in this session\n`;
                }
                text += `\n${'='.repeat(50)}\n\n`;
            }
        }
        
        else if (data.messages && data.messages.length > 0) {
            text += `Session: ${new Date(data.started_at).toLocaleString()}\n`;
            text += `Session ID: ${data.session_id}\n`;
            text += `Crisis Detected: ${data.crisis_detected ? 'Yes' : 'No'}\n`;
            text += `${'-'.repeat(30)}\n`;
            
            for (const msg of data.messages) {
                const time = new Date(msg.timestamp).toLocaleTimeString();
                text += `[${time}] ${msg.sender.toUpperCase()}: ${msg.content}\n`;
            }
            text += `\n${'='.repeat(50)}\n`;
        }
       
        else {
            text += `No messages found in this export.\n`;
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

//Confirm delete session
function confirmDeleteSession(sessionId) {
    currentSessionToDelete = sessionId;
    document.getElementById('deleteSessionModal').classList.add('active');
}

//Delete single session
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
        console.error('Delete error:', error);
        alert('Cannot connect to server');
    }
    currentSessionToDelete = null;
}

//Delete all sessions
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
        console.error('Delete all error:', error);
        alert('Cannot connect to server');
    }
}

//Modal handlers
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

//Check login and load sessions
if (!isLoggedIn()) {
    window.location.href = 'index.html';
}

loadSessions();

//Make functions global for onclick handlers
window.exportSession = exportSession;
window.confirmDeleteSession = confirmDeleteSession;
window.deleteSession = deleteSession;
window.deleteAllSessions = deleteAllSessions;