// ========================================
// WELLBEING HISTORY
// Shows all past assessments
// ========================================

function getAuth() {
    const auth = localStorage.getItem('auth');
    return auth ? { 'Authorization': 'Basic ' + auth } : {};
}

function isLoggedIn() {
    return localStorage.getItem('user') !== null;
}

async function loadHistory() {
    const container = document.getElementById('historyContainer');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Loading history...</div>';
    
    try {
        const response = await fetch('http://localhost:8000/wellbeing/history', {
            headers: getAuth()
        });
        
        if (response.ok) {
            const history = await response.json();
            
            if (history.length === 0) {
                container.innerHTML = '<div class="empty-state">No wellbeing assessments yet. Take your first one!</div>';
                return;
            }
            
            const categoryClass = {
                'Excellent': 'category-excellent',
                'Good': 'category-good',
                'Moderate': 'category-moderate',
                'Concerning': 'category-concerning',
                'Critical': 'category-critical'
            };
            
            let html = '';
            for (let i = 0; i < history.length; i++) {
                const item = history[i];
                html += `
                    <div class="history-item">
                        <div>
                            <strong>${new Date(item.date).toLocaleDateString()}</strong>
                            <br>
                            <small>Score: ${item.total_score}/5</small>
                        </div>
                        <div>
                            <span class="history-category ${categoryClass[item.category] || 'category-moderate'}">${item.category}</span>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
            
        } else if (response.status === 401) {
            window.location.href = 'index.html';
        } else {
            container.innerHTML = '<div class="empty-state">Failed to load history</div>';
        }
    } catch (error) {
        console.error('Error loading history:', error);
        container.innerHTML = '<div class="empty-state">Cannot connect to server</div>';
    }
}

// Check login
if (!localStorage.getItem('user')) {
    window.location.href = 'index.html';
}

loadHistory();