// ========================================
// WELLBEING RESULTS - IMPROVED DISPLAY
// ========================================

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
    
    const categoryMessages = {
        'Excellent': 'You\'re thriving! Keep up your great habits.',
        'Good': 'You\'re doing well. Small improvements can make a difference.',
        'Moderate': 'You\'re managing. Focus on small, positive steps.',
        'Concerning': 'Your wellbeing matters. Consider reaching out for support.',
        'Critical': 'Please reach out for support. You deserve help and care.'
    };
    
    const color = categoryColors[result.category] || '#9CAF88';
    const message = categoryMessages[result.category] || 'Keep taking care of yourself.';
    
    const tips = result.tips || [];
    
    container.innerHTML = `
        <div style="text-align: center;">
            <h2>🌿 Your Wellbeing Results</h2>
            <div class="score-circle" style="border: 4px solid ${color}">
                <div class="score-number">${result.total_score}</div>
                <div style="font-size: 14px;">/ 5.0</div>
            </div>
            <div class="category-badge" style="background: ${color}; color: white;">${result.category}</div>
            <p style="margin-top: 16px; color: var(--text-light);">${message}</p>
            <p style="font-size: 12px; color: var(--text-light);">Assessment completed: ${new Date(result.date).toLocaleDateString()}</p>
        </div>
        
        <h3 style="margin-top: 30px;">💡 Personalised Tips</h3>
        ${tips.length > 0 ? 
            `<ul class="tips-list">
                ${tips.map(tip => `<li>${escapeHtml(tip)}</li>`).join('')}
            </ul>` : 
            `<p style="color: var(--text-light); text-align: center; padding: 20px;">Complete the assessment to receive personalised wellbeing tips.</p>`
        }
        
        <div class="action-buttons">
            <button onclick="location.href='wellbeing-history.html'">View History</button>
            <button onclick="location.href='wellbeing.html'">Take Again</button>
            <button onclick="location.href='dashboard.html'">Go to Dashboard</button>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

if (!localStorage.getItem('user')) {
    window.location.href = 'index.html';
}

displayResults();