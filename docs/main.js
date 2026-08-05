// ===== NAVBAR SCROLL EFFECT =====
const navbar = document.querySelector('.site-header');
window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.pageYOffset > 40);
}, { passive: true });

// ===== INTERSECTION OBSERVER FOR FADE-INS =====
const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            fadeObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.08 });

document.querySelectorAll('.skill-group, .project-item, .service-card').forEach((el, i) => {
    el.style.animationDelay = `${i * 0.06}s`;
    fadeObserver.observe(el);
});

// ===== NUMBER COUNTER ANIMATION =====
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const el = entry.target;
            const target = parseInt(el.dataset.count);
            const suffix = el.dataset.suffix || '';
            const duration = 2000;
            const steps = duration / 30;
            const increment = target / steps;
            let current = 0;

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    el.textContent = target.toLocaleString() + suffix;
                    clearInterval(timer);
                } else {
                    el.textContent = Math.floor(current).toLocaleString() + suffix;
                }
            }, 30);

            counterObserver.unobserve(el);
        }
    });
}, { threshold: 0.6 });

document.querySelectorAll('.hero-stat-num').forEach(counter => counterObserver.observe(counter));

// ===== SMOOTH SCROLL =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        const target = document.querySelector(href);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

console.log('Portfolio loaded');