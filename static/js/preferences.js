// Preferences Page JavaScript

let currentQuestion = 1;
const totalQuestions = 13;

function updateQuestionCounter() {
    const counter = document.getElementById('questionCounter');
    counter.textContent = `Question ${currentQuestion} of ${totalQuestions}`;
}

function showQuestion(questionNumber) {
    // Hide all questions
    const questions = document.querySelectorAll('.question-section');
    questions.forEach(q => q.classList.remove('active'));
    
    // Show current question
    const currentQ = document.querySelector(`[data-question="${questionNumber}"]`);
    if (currentQ) {
        currentQ.classList.add('active');
    }
    
    // Update navigation buttons
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    prevBtn.disabled = questionNumber === 1;
    
    if (questionNumber === totalQuestions) {
        nextBtn.textContent = 'Lanjut ke Text Preferences';
        nextBtn.onclick = goToTextPreferences;
    } else {
        nextBtn.textContent = 'Selanjutnya';
        nextBtn.onclick = nextQuestion;
    }
    
    updateQuestionCounter();
}

function nextQuestion() {
    if (currentQuestion < totalQuestions) {
        currentQuestion++;
        showQuestion(currentQuestion);
    }
}

function previousQuestion() {
    if (currentQuestion > 1) {
        currentQuestion--;
        showQuestion(currentQuestion);
    }
}

function goToTextPreferences() {
    // Here you would navigate to text preferences page
    alert('Menuju ke halaman Text Preferences...');
    // window.location.href = 'text-preferences.html';
}

// Hobby selection limit
function limitHobbies() {
    const checkboxes = document.querySelectorAll('input[name="hobbies"]');
    const checkedBoxes = document.querySelectorAll('input[name="hobbies"]:checked');
    
    if (checkedBoxes.length >= 5) {
        checkboxes.forEach(cb => {
            if (!cb.checked) {
                cb.disabled = true;
                cb.parentElement.style.opacity = '0.5';
            }
        });
    } else {
        checkboxes.forEach(cb => {
            cb.disabled = false;
            cb.parentElement.style.opacity = '1';
        });
    }
}

// Smooth scroll to top when changing questions
function smoothScrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
    showQuestion(1);
    
    // Add hobby limit functionality
    const hobbyCheckboxes = document.querySelectorAll('input[name="hobbies"]');
    hobbyCheckboxes.forEach(cb => {
        cb.addEventListener('change', limitHobbies);
    });
    
    // Range input visual feedback
    const ranges = document.querySelectorAll('input[type="range"]');
    ranges.forEach(range => {
        range.addEventListener('input', function() {
            const value = (this.value - this.min) / (this.max - this.min) * 100;
            this.style.background = `linear-gradient(to right, #FF6B6B 0%, #4ECDC4 ${value}%, rgba(255,255,255,0.3) ${value}%, rgba(255,255,255,0.3) 100%)`;
        });
        
        // Initialize
        const value = (range.value - range.min) / (range.max - range.min) * 100;
        range.style.background = `linear-gradient(to right, #FF6B6B 0%, #4ECDC4 ${value}%, rgba(255,255,255,0.3) ${value}%, rgba(255,255,255,0.3) 100%)`;
    });
    
    // Override navigation functions to include smooth scroll
    const originalNext = nextQuestion;
    const originalPrev = previousQuestion;

    nextQuestion = function() {
        originalNext();
        smoothScrollToTop();
    }

    previousQuestion = function() {
        originalPrev();
        smoothScrollToTop();
    }
});