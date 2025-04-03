// Navigation scroll effect
window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    header.classList.toggle('scrolled', window.scrollY > 50);
});

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

hamburger.addEventListener('click', function() {
    navLinks.classList.toggle('active');
    
    // Animate hamburger to X
    const lines = document.querySelectorAll('.hamburger div');
    lines.forEach(line => line.classList.toggle('active'));
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        if (navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
        }
        
        const target = document.querySelector(this.getAttribute('href'));
        
        window.scrollTo({
            top: target.offsetTop - 70,
            behavior: 'smooth'
        });
    });
});

// Skill progress animation with Intersection Observer
const skillSection = document.querySelector('#skills');
const skillProgresses = document.querySelectorAll('.skill-progress');

const skillObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            skillProgresses.forEach(progress => {
                const width = progress.getAttribute('data-width') + '%';
                progress.style.width = width;
                progress.style.transition = 'width 1.5s ease-in-out';
            });
            skillObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

if (skillSection) {
    skillObserver.observe(skillSection);
}

// Timeline animation with Intersection Observer
const timelineSection = document.querySelector('#experience');
const timelineItems = document.querySelectorAll('.timeline-item');

const timelineObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            timelineObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.2 });

timelineItems.forEach(item => {
    timelineObserver.observe(item);
});

// Form validation with real-time feedback
const form = document.querySelector('.contact-form');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const subjectInput = document.getElementById('subject');
const messageInput = document.getElementById('message');

// Real-time validation for name
nameInput.addEventListener('input', function() {
    if (this.value.trim() === '') {
        this.parentElement.classList.add('error');
        this.parentElement.querySelector('.error-message').style.display = 'block';
    } else {
        this.parentElement.classList.remove('error');
        this.parentElement.querySelector('.error-message').style.display = 'none';
    }
});

// Real-time validation for email
emailInput.addEventListener('input', function() {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.value)) {
        this.parentElement.classList.add('error');
        this.parentElement.querySelector('.error-message').style.display = 'block';
    } else {
        this.parentElement.classList.remove('error');
        this.parentElement.querySelector('.error-message').style.display = 'none';
    }
});

// Real-time validation for subject
subjectInput.addEventListener('input', function() {
    if (this.value.trim() === '') {
        this.parentElement.classList.add('error');
        this.parentElement.querySelector('.error-message').style.display = 'block';
    } else {
        this.parentElement.classList.remove('error');
        this.parentElement.querySelector('.error-message').style.display = 'none';
    }
});

// Real-time validation for message
messageInput.addEventListener('input', function() {
    if (this.value.trim() === '') {
        this.parentElement.classList.add('error');
        this.parentElement.querySelector('.error-message').style.display = 'block';
    } else {
        this.parentElement.classList.remove('error');
        this.parentElement.querySelector('.error-message').style.display = 'none';
    }
});

// Form submission with animation
form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    let isValid = true;
    
    // Validate name
    if (nameInput.value.trim() === '') {
        nameInput.parentElement.classList.add('error');
        nameInput.parentElement.querySelector('.error-message').style.display = 'block';
        isValid = false;
    }
    
    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailInput.value)) {
        emailInput.parentElement.classList.add('error');
        emailInput.parentElement.querySelector('.error-message').style.display = 'block';
        isValid = false;
    }
    
    // Validate subject
    if (subjectInput.value.trim() === '') {
        subjectInput.parentElement.classList.add('error');
        subjectInput.parentElement.querySelector('.error-message').style.display = 'block';
        isValid = false;
    }
    
    // Validate message
    if (messageInput.value.trim() === '') {
        messageInput.parentElement.classList.add('error');
        messageInput.parentElement.querySelector('.error-message').style.display = 'block';
        isValid = false;
    }
    
    if (isValid) {
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Sending...';
        submitBtn.disabled = true;
        
        // Simulate form submission (replace with actual API call)
        setTimeout(() => {
            // Success animation
            submitBtn.textContent = 'Sent!';
            submitBtn.classList.add('success');
            
            // Reset form after delay
            setTimeout(() => {
                form.reset();
                submitBtn.textContent = originalText;
                submitBtn.classList.remove('success');
                submitBtn.disabled = false;
            }, 2000);
        }, 1500);
    }
});

// Dark mode toggle with local storage
const themeToggle = document.querySelector('.theme-toggle');
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

// Check for saved theme preference or use system preference
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark' || (!savedTheme && prefersDarkScheme.matches)) {
    document.body.classList.add('dark-mode');
    themeToggle.textContent = '☀️';
}

themeToggle.addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
    
    if (document.body.classList.contains('dark-mode')) {
        themeToggle.textContent = '☀️';
        localStorage.setItem('theme', 'dark');
    } else {
        themeToggle.textContent = '🌙';
        localStorage.setItem('theme', 'light');
    }
});

// Typing effect for hero section with cursor
const typingElement = document.querySelector('.hero-content h1');
const originalText = typingElement.innerHTML;
typingElement.innerHTML = '';

let i = 0;
const typeWriter = function() {
    if (i < originalText.length) {
        typingElement.innerHTML += originalText.charAt(i);
        i++;
        setTimeout(typeWriter, 50);
    } else {
        // Add blinking cursor after typing is complete
        typingElement.innerHTML += '<span class="cursor">|</span>';
    }
};

setTimeout(typeWriter, 500);

// Interactive project cards with hover effects and click animations
const projectCards = document.querySelectorAll('.project-card');

projectCards.forEach(card => {
    // Add hover effect
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.03) translateY(-10px)';
        this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.2)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = '';
        this.style.boxShadow = '';
    });
    
    // Add click animation
    card.addEventListener('click', function() {
        this.classList.add('clicked');
        setTimeout(() => {
            this.classList.remove('clicked');
        }, 300);
        
        const title = this.querySelector('h3').textContent;
        // Create a modal instead of using alert
        const modal = document.createElement('div');
        modal.className = 'project-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-modal">&times;</span>
                <h2>${title}</h2>
                <p>This is a detailed view of the ${title} project. In a real portfolio, this would show more information about the project, technologies used, and possibly a live demo.</p>
                <div class="modal-buttons">
                    <a href="#" class="btn">View Demo</a>
                    <a href="#" class="btn btn-outline">GitHub</a>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close modal when clicking the close button or outside the modal
        const closeBtn = modal.querySelector('.close-modal');
        closeBtn.addEventListener('click', () => {
            modal.remove();
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    });
});

// Add scroll reveal animations for sections
const sections = document.querySelectorAll('section');
const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            sectionObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

sections.forEach(section => {
    sectionObserver.observe(section);
});

// Add parallax effect to hero section
const heroSection = document.querySelector('#hero');
window.addEventListener('scroll', () => {
    if (heroSection) {
        const scrollPosition = window.scrollY;
        heroSection.style.backgroundPositionY = `${scrollPosition * 0.5}px`;
    }
});

// Add skill hover effect to show more details
const skillCards = document.querySelectorAll('.skill-card');
skillCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.classList.add('expanded');
    });
    
    card.addEventListener('mouseleave', function() {
        this.classList.remove('expanded');
    });
}); 