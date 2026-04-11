
let currentEditId = null;
let selectedMood = 3;
let editSelectedMood = 3;

// Create a new journal entry
async function createEntry() {
    const content = document.getElementById('newEntryContent').value;
    if (!content.trim()) {
        alert('Please write something in your journal');
        return;
    }

    const saveBtn = document.getElementById('saveBtn');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    try {
        const response = await fetch(`${API_URL}/journal/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeader()
            },
            body: JSON.stringify({
                encrypted_content: content,
                mood_score: selectedMood
            })
        });

        if (response.ok) {
            document.getElementById('newEntryContent').value = '';
            selectedMood = 3;
            updateMoodSelector('moodSelector', 3);
            loadEntries();
        } else if (response.status === 401) {
            alert('Session expired. Please login again.');
            window.location.href = 'index.html';
        } else {
            alert('Failed to save entry');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Cannot connect to server');
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save Entry';
    }
}

// Load all journal entries
async function loadEntries() {
    const container = document.getElementById('entriesContainer');
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_URL}/journal/`, {
            method: 'GET',
            headers: getAuthHeader()
        });

        if (response.ok) {
            const data = await response.json();
            const entries = data.entries || [];
            
            document.getElementById('entryCount').textContent = `${entries.length} entries`;
            
            if (entries.length === 0) {
                container.innerHTML = '<div class="empty-state">✨ No entries yet. Write your first journal entry above!</div>';
                return;
            }
            
            container.innerHTML = entries.map(entry => `
                <div class="entry-card">
                    <div class="entry-header">
                        <span class="entry-mood">${getMoodEmoji(entry.mood_score)}</span>
                        <span class="entry-date">${formatDate(entry.created_at)}</span>
                    </div>
                    <div class="entry-preview">${escapeHtml(entry.encrypted_content.substring(0, 150))}${entry.encrypted_content.length > 150 ? '...' : ''}</div>
                    <div class="entry-actions">
                        <span class="edit-btn" onclick="openEditModal('${entry.id}', ${entry.mood_score}, \`${escapeHtml(entry.encrypted_content)}\`)">✏️ Edit</span>
                        <span class="delete-btn" onclick="deleteEntry('${entry.id}')">🗑️ Delete</span>
                    </div>
                </div>
            `).join('');
        } else if (response.status === 401) {
            window.location.href = 'index.html';
        } else {
            container.innerHTML = '<div class="empty-state">Failed to load entries</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="empty-state">Cannot connect to server</div>';
    }
}

// Delete an entry
async function deleteEntry(entryId) {
    if (!confirm('Are you sure you want to delete this entry?')) return;
    
    try {
        const response = await fetch(`${API_URL}/journal/${entryId}`, {
            method: 'DELETE',
            headers: getAuthHeader()
        });

        if (response.ok) {
            loadEntries();
        } else {
            alert('Failed to delete entry');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Cannot connect to server');
    }
}

// Open edit modal
function openEditModal(id, mood, content) {
    currentEditId = id;
    editSelectedMood = mood;
    
    document.getElementById('editContent').value = content;
    updateMoodSelector('editMoodSelector', mood);
    document.getElementById('editModal').style.display = 'flex';
}

// Close modal
function closeModal() {
    document.getElementById('editModal').style.display = 'none';
    currentEditId = null;
}

// Update entry
async function updateEntry() {
    const content = document.getElementById('editContent').value;
    if (!content.trim()) {
        alert('Please write something');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/journal/${currentEditId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeader()
            },
            body: JSON.stringify({
                encrypted_content: content,
                mood_score: editSelectedMood
            })
        });

        if (response.ok) {
            closeModal();
            loadEntries();
        } else {
            alert('Failed to update entry');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Cannot connect to server');
    }
}

// Update mood selector UI
function updateMoodSelector(selectorId, moodValue) {
    const container = document.getElementById(selectorId);
    if (!container) return;
    
    container.querySelectorAll('.mood-option').forEach(el => {
        el.classList.remove('selected');
        if (parseInt(el.getAttribute('data-mood')) === moodValue) {
            el.classList.add('selected');
        }
    });
}

// Setup mood selector event listeners
function setupMoodSelector(selectorId, callback) {
    const container = document.getElementById(selectorId);
    if (!container) return;
    
    container.querySelectorAll('.mood-option').forEach(emoji => {
        emoji.addEventListener('click', () => {
            const mood = parseInt(emoji.getAttribute('data-mood'));
            updateMoodSelector(selectorId, mood);
            callback(mood);
        });
    });
}

// Helper functions
function getMoodEmoji(score) {
    const emojis = {1: '😢', 2: '😐', 3: '🙂', 4: '😊', 5: '🤗'};
    return emojis[score] || '🙂';
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown date';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize journal page
function initJournal() {
    if (!isLoggedIn()) {
        window.location.href = 'index.html';
        return;
    }
    
    setupMoodSelector('moodSelector', (mood) => { selectedMood = mood; });
    setupMoodSelector('editMoodSelector', (mood) => { editSelectedMood = mood; });
    
    updateMoodSelector('moodSelector', 3);
    updateMoodSelector('editMoodSelector', 3);
    
    loadEntries();
}