// ========================================
// WELLBEING ASSESSMENT - WITH SCALE LABELS
// ========================================

let currentQuestions = [];
let userResponses = {};

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

async function loadQuestions() {
    const container = document.getElementById('questionsContainer');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Loading questions...</div>';
    
    try {
        const response = await fetch('http://localhost:8000/wellbeing/questions', {
            headers: getAuth()
        });
        
        if (response.ok) {
            const data = await response.json();
            currentQuestions = data.all || [];
            renderQuestions();
        } else if (response.status === 401) {
            window.location.href = 'index.html';
        } else {
            container.innerHTML = '<div class="empty-state">Failed to load questions. Please try again.</div>';
        }
    } catch (error) {
        console.error('Error loading questions:', error);
        container.innerHTML = '<div class="empty-state">Cannot connect to server. Is the backend running?</div>';
    }
}

function renderQuestions() {
    const container = document.getElementById('questionsContainer');
    if (!container) return;
    
    // Separate SWEMWBS (7 questions) and PHQ-2 (2 questions)
    const swemwbsQuestions = currentQuestions.filter(q => 
        q.id === 'q1_optimistic' || q.id === 'q2_useful' || q.id === 'q3_relaxed' ||
        q.id === 'q4_dealing' || q.id === 'q5_thinking' || q.id === 'q6_close' || q.id === 'q7_decisions'
    );
    
    const phq2Questions = currentQuestions.filter(q => 
        q.id === 'q8_interest' || q.id === 'q9_depressed'
    );
    
    let html = `
        <div class="card">
            <h3 class="section-title">How have you been feeling?</h3>
            <p>Rate each statement for the <strong>past two weeks</strong>.</p>
        </div>
    `;
    
    // SWEMWBS Questions
    if (swemwbsQuestions.length > 0) {
        html += `<div class="card"><h3>General Wellbeing</h3>`;
        for (const q of swemwbsQuestions) {
            html += renderQuestionCard(q);
        }
        html += `</div>`;
    }
    
    // PHQ-2 Questions
    if (phq2Questions.length > 0) {
        html += `<div class="card"><h3>How often have you been bothered by...</h3>`;
        for (const q of phq2Questions) {
            html += renderQuestionCard(q);
        }
        html += `</div>`;
    }
    
    container.innerHTML = html;
    
    // Show submit section
    const submitSection = document.getElementById('submitSection');
    if (submitSection) submitSection.style.display = 'block';
    
    // Attach event listeners
    attachScaleListeners();
}

function renderQuestionCard(q) {
    return `
        <div class="question-card" data-question-id="${q.id}">
            <div class="question-text">${escapeHtml(q.text)}</div>
            <div class="scale-container">
                <div class="scale">
                    <div class="scale-option" data-value="1">1</div>
                    <div class="scale-option" data-value="2">2</div>
                    <div class="scale-option" data-value="3">3</div>
                    <div class="scale-option" data-value="4">4</div>
                    <div class="scale-option" data-value="5">5</div>
                </div>
                <div class="scale-labels">
                    <span>Strongly<br>Disagree</span>
                    <span>Disagree</span>
                    <span>Neutral</span>
                    <span>Agree</span>
                    <span>Strongly<br>Agree</span>
                </div>
            </div>
        </div>
    `;
}

function attachScaleListeners() {
    const allScaleOptions = document.querySelectorAll('.scale-option');
    
    allScaleOptions.forEach(option => {
        option.removeEventListener('click', handleScaleClick);
        option.addEventListener('click', handleScaleClick);
    });
}

function handleScaleClick(event) {
    const option = event.currentTarget;
    const value = parseInt(option.getAttribute('data-value'));
    const questionCard = option.closest('.question-card');
    const questionId = questionCard.getAttribute('data-question-id');
    
    // Remove selected class from all options in this question
    const allOptionsInCard = questionCard.querySelectorAll('.scale-option');
    allOptionsInCard.forEach(opt => opt.classList.remove('selected'));
    
    // Add selected class to clicked option
    option.classList.add('selected');
    
    // Store the response
    userResponses[questionId] = value;
    
    console.log('Answered ' + questionId + ': ' + value);
}

async function submitAssessment() {
    const expectedIds = currentQuestions.map(q => q.id);
    const missingIds = expectedIds.filter(id => !userResponses[id]);
    
    if (missingIds.length > 0) {
        alert('Please answer all ' + expectedIds.length + ' questions. Missing: ' + missingIds.length + ' question(s).');
        return;
    }
    
    const submitBtn = document.getElementById('submitBtn');
    if (!submitBtn) return;
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    try {
        const response = await fetch('http://localhost:8000/wellbeing/assess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + localStorage.getItem('auth')
            },
            body: JSON.stringify({ responses: userResponses })
        });
        
        if (response.ok) {
            const result = await response.json();
            localStorage.setItem('lastWellbeingResult', JSON.stringify(result));
            window.location.href = 'wellbeing-results.html';
        } else if (response.status === 401) {
            alert('Session expired. Please login again.');
            window.location.href = 'index.html';
        } else {
            const error = await response.text();
            alert('Failed to submit assessment: ' + error);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Assessment';
        }
    } catch (error) {
        console.error('Submit error:', error);
        alert('Cannot connect to server. Is the backend running?');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Assessment';
    }
}

function initWellbeing() {
    if (!localStorage.getItem('user')) {
        window.location.href = 'index.html';
        return;
    }
    
    loadQuestions();
    
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitAssessment);
    }
}

// Auto-initialise
if (document.getElementById('questionsContainer')) {
    initWellbeing();
}