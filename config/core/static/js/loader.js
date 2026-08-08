// loader.js

class AILoader {
    constructor() {
        this.messageInterval = null;
        this.checklistInterval = null;
    }

    startQuestionLoader() {
        const messages = [
            "Connecting to Gemini AI...",
            "Understanding selected skill...",
            "Selecting difficulty...",
            "Creating practical questions...",
            "Optimizing assessment...",
            "Preparing workspace...",
            "Almost ready..."
        ];
        
        let currentIndex = 0;
        const msgElements = document.querySelectorAll('.status-message');
        
        if (msgElements.length === 0) return;

        // Initialize first message
        msgElements[0].textContent = messages[0];
        msgElements[0].classList.add('active');

        this.messageInterval = setInterval(() => {
            const currentEl = document.querySelector('.status-message.active');
            
            if (currentEl) {
                currentEl.classList.remove('active');
                currentEl.classList.add('exit');
                
                setTimeout(() => {
                    currentEl.classList.remove('exit');
                    currentIndex = (currentIndex + 1) % messages.length;
                    
                    // Stop at the last message and keep it
                    if (currentIndex === messages.length - 1) {
                        clearInterval(this.messageInterval);
                    }
                    
                    currentEl.textContent = messages[currentIndex];
                    currentEl.classList.add('active');
                }, 500);
            }
        }, 2200);
    }

    startEvaluationLoader() {
        const items = document.querySelectorAll('.check-item');
        if (items.length === 0) return;

        let currentIndex = 0;
        
        // Start first item
        items[0].classList.add('active');
        items[0].querySelector('.check-icon').innerHTML = '<i class="bi bi-arrow-repeat"></i>';

        this.checklistInterval = setInterval(() => {
            if (currentIndex < items.length - 1) {
                // Complete current
                const currentIcon = items[currentIndex].querySelector('.check-icon');
                currentIcon.innerHTML = '<i class="bi bi-check-lg"></i>';
                items[currentIndex].classList.remove('active');
                items[currentIndex].classList.add('done');
                
                // Move to next
                currentIndex++;
                items[currentIndex].classList.add('active');
                items[currentIndex].querySelector('.check-icon').innerHTML = '<i class="bi bi-arrow-repeat"></i>';
            } else {
                // Complete last
                const currentIcon = items[currentIndex].querySelector('.check-icon');
                currentIcon.innerHTML = '<i class="bi bi-check-lg"></i>';
                items[currentIndex].classList.remove('active');
                items[currentIndex].classList.add('done');
                clearInterval(this.checklistInterval);
            }
        }, 1500);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const loader = new AILoader();
    
    // Auto-initialize based on DOM elements
    if (document.getElementById('question-loader-active')) {
        loader.startQuestionLoader();
        // Redirect after animation start
        const targetUrl = document.getElementById('question-loader-active').dataset.url;
        if(targetUrl) {
            window.location.href = targetUrl;
        }
    }
    
    if (document.getElementById('eval-loader-active')) {
        loader.startEvaluationLoader();
        const targetUrl = document.getElementById('eval-loader-active').dataset.url;
        if(targetUrl) {
            window.location.href = targetUrl;
        }
    }
});
