
function getAuth() {
    const auth = localStorage.getItem('auth');
    return auth ? { 'Authorization': 'Basic ' + auth } : {};
}

function isLoggedIn() {
    return localStorage.getItem('user') !== null;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function displayResults() {
    const resultStr = localStorage.getItem('lastWellbeingResult');
    const container = document.getElementById('resultsContainer');
    
    if (!container) return;
    
    if (!resultStr) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No assessment results found.</p>
                <button onclick="location.href='wellbeing.html'">Take Assessment</button>
            </div>
        `;
        return;
    }
    
    const result = JSON.parse(resultStr);
    
    const categoryColors = {
        'Excellent': '#48BB78',
        'Good': '#9CAF88',
        'Moderate': '#ECC94B',
        'Concerning': '#ED8936',
        'Critical': '#E53E3E'
    };
    
    const color = categoryColors[result.category] || '#9CAF88';
    
    container.innerHTML = `
        <div style="text-align: center;">
            <h2>🌿 Your Wellbeing Results</h2>
            <div class="score-circle" style="border: 4px solid ${color}">
                <div class="score-number">${result.total_score}</div>
                <div>/ 5.0</div>
            </div>
            <h3 style="color: ${color}">${result.category}</h3>
            <p>Assessment completed: ${new Date(result.date).toLocaleDateString()}</p>
        </div>
        
        <h3>💡 Personalised Tips</h3>
        <ul class="tips-list">
            ${result.tips.map(tip => `<li>${escapeHtml(tip)}</li>`).join('')}
        </ul>
        
        <div class="action-buttons">
            <button onclick="location.href='wellbeing-history.html'">View History</button>
            <button onclick="location.href='wellbeing.html'">Take Again</button>
            <button onclick="location.href='dashboard.html'">Go to Dashboard</button>
        </div>
    `;
}

// Check login
if (!localStorage.getItem('user')) {
    window.location.href = 'index.html';
}

displayResults();