/*
 * Voltage Platform - JavaScript
 */

// Quiz Timer
class QuizTimer {
    constructor(duration, display, onComplete) {
        this.duration = duration * 60; // Convert to seconds
        this.display = display;
        this.onComplete = onComplete;
        this.remaining = this.duration;
        this.interval = null;
    }

    start() {
        this.interval = setInterval(() => {
            const minutes = Math.floor(this.remaining / 60);
            const seconds = this.remaining % 60;

            this.display.textContent =
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

            // Warning when less than 2 minutes
            if (this.remaining <= 120) {
                this.display.parentElement.classList.add('warning');
            }

            if (this.remaining <= 0) {
                this.stop();
                this.onComplete();
            }

            this.remaining--;
        }, 1000);
    }

    stop() {
        clearInterval(this.interval);
    }
}

// Video Progress Tracker
function trackVideoProgress(lectureId, playerElement) {
    let lastUpdate = 0;

    const updateProgress = (progress) => {
        // Only update every 10%
        if (progress - lastUpdate >= 10) {
            lastUpdate = progress;

            fetch(`/courses/lecture/${lectureId}/progress/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: `progress=${progress}`
            });
        }
    };

    // For Vimeo
    if (window.Vimeo) {
        const player = new Vimeo.Player(playerElement);
        player.on('timeupdate', (data) => {
            const progress = Math.floor(data.percent * 100);
            updateProgress(progress);
        });
    }
}

// Get CSRF Token
function getCsrfToken() {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

// Option Selection for Quiz
document.querySelectorAll('.option').forEach(option => {
    option.addEventListener('click', function () {
        const questionCard = this.closest('.question-card');
        questionCard.querySelectorAll('.option').forEach(opt => {
            opt.classList.remove('selected');
        });
        this.classList.add('selected');
        this.querySelector('input[type="radio"]').checked = true;
    });
});

// Watermark Movement
function initWatermark() {
    const watermark = document.querySelector('.watermark');
    if (watermark) {
        setInterval(() => {
            watermark.style.top = Math.random() * 70 + 10 + '%';
            watermark.style.right = Math.random() * 70 + 10 + '%';
        }, 5000);
    }
}

// Battery Animation
function animateBattery(level) {
    const batteryLevel = document.querySelector('.battery-level');
    if (batteryLevel) {
        batteryLevel.style.width = level + '%';

        // Change color based on level
        if (level < 30) {
            batteryLevel.style.background = 'var(--danger)';
        } else if (level < 60) {
            batteryLevel.style.background = 'var(--warning)';
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function () {
    // Mobile Menu Toggle
    const menuToggle = document.getElementById('mobile-menu');
    const navLinks = document.querySelector('.nav-links');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function () {
            // Toggle active class on both elements
            menuToggle.classList.toggle('is-active');
            navLinks.classList.toggle('active');
        });

        // Close menu when clicking on a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function () {
                menuToggle.classList.remove('is-active');
                navLinks.classList.remove('active');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', function (e) {
            if (!menuToggle.contains(e.target) && !navLinks.contains(e.target)) {
                menuToggle.classList.remove('is-active');
                navLinks.classList.remove('active');
            }
        });
    }

    initWatermark();

    // Initialize battery if on dashboard
    const batteryEl = document.querySelector('.battery-level');
    if (batteryEl) {
        const level = parseInt(batteryEl.dataset.level || 0);
        animateBattery(level);
    }
});

// Celebration Animation for passing quiz
function celebrate() {
    // Simple confetti effect
    const colors = ['#00d4ff', '#00b4d8', '#ffffff', '#00c853'];
    for (let i = 0; i < 50; i++) {
        createConfetti(colors[Math.floor(Math.random() * colors.length)]);
    }
}

function createConfetti(color) {
    const confetti = document.createElement('div');
    confetti.style.cssText = `
        position: fixed;
        width: 10px;
        height: 10px;
        background: ${color};
        left: ${Math.random() * 100}vw;
        top: -10px;
        border-radius: 50%;
        pointer-events: none;
        animation: fall ${2 + Math.random() * 2}s linear forwards;
    `;
    document.body.appendChild(confetti);

    setTimeout(() => confetti.remove(), 4000);
}

// Add confetti animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fall {
        to {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
