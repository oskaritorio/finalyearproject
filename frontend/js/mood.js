// ========================================
// MOOD FUNCTIONS
// ========================================

async function quickMood(score) {
    try {
        const response = await fetch(`${API_URL}/mood/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeader()
            },
            body: JSON.stringify({ mood_score: score })
        });
        
        if (response.ok) {
            alert(`✅ Mood ${score} logged!`);
            loadMoodHistory();
        } else if (response.status === 400) {
            alert('Already logged mood today!');
        } else if (response.status === 401) {
            window.location.href = 'index.html';
        } else {
            alert('Failed to log mood');
        }
    } catch (error) {
        console.error('Mood error:', error);
        alert('Cannot connect to server');
    }
}

async function loadMoodHistory() {
    const container = document.getElementById('moodHistoryContainer');
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_URL}/mood/`, {
            method: 'GET',
            headers: getAuthHeader()
        });
        
        if (response.ok) {
            const data = await response.json();
            
            document.getElementById('averageMood').innerHTML = `${data.average_mood || 0} / 5`;
            document.getElementById('moodCount').textContent = `${data.total_entries || 0} entries`;
            
            if (data.history && data.history.length > 0) {
                container.innerHTML = data.history.map(item => `
                    <div class="mood-item">
                        <span class="mood-emoji-large">${getMoodEmoji(item.mood)}</span>
                        <span>${item.date}</span>
                        <span>${item.note || ''}</span>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<div class="empty-state">No mood entries yet. Click an emoji above!</div>';
            }
        } else if (response.status === 401) {
            window.location.href = 'index.html';
        } else {
            container.innerHTML = '<div class="empty-state">Failed to load mood history</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="empty-state">Cannot connect to server</div>';
    }
}

function getMoodEmoji(score) {
    const emojis = {1: '😢', 2: '😐', 3: '🙂', 4: '😊', 5: '🤗'};
    return emojis[score] || '🙂';
}

function initMood() {
    if (!isLoggedIn()) {
        window.location.href = 'index.html';
    }
    loadMoodHistory();
}