// ===== DARK MODE TOGGLE =====
const themeToggle = document.getElementById('theme-toggle');
const root = document.documentElement;

function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    themeToggle.textContent = theme === 'dark' ? '◐' : '◑';
}

function initTheme() {
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initial = saved || (prefersDark ? 'dark' : 'light');
    setTheme(initial);
}

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = root.getAttribute('data-theme');
        setTheme(current === 'dark' ? 'light' : 'dark');
    });
    initTheme();
}

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

// ===== LIVE GITHUB STATS =====
async function fetchGithubStats() {
    const stats = await Promise.allSettled([
        fetch('https://api.github.com/users/IVFSS').then(r => r.json()),
        fetch('https://api.github.com/repos/IVFSS/data-analyst-portfolio').then(r => r.json())
    ]);

    stats.forEach((res, i) => {
        if (res.status !== 'fulfilled') return;
        const data = res.value;

        if (i === 0 && data.public_repos !== undefined) {
            const num = document.createElement('span');
            num.className = 'hero-stat-num';
            num.textContent = data.public_repos;
            const lbl = document.createElement('span');
            lbl.className = 'hero-stat-label';
            lbl.textContent = 'GitHub Repos';
            const stat = document.querySelector('.hero-stat')?.parentElement;
            if (stat) {
                const existing = stat.querySelector('[data-label="repos"]');
                if (existing) return;
                const newStat = document.createElement('div');
                newStat.className = 'hero-stat';
                newStat.setAttribute('data-label', 'repos');
                newStat.innerHTML = `<span class="hero-stat-num">${data.public_repos}</span><span class="hero-stat-label">GitHub Repos</span>`;
                stat.appendChild(newStat);
            }
        }
        if (i === 1 && data.stargazers_count !== undefined) {
            const statRow = document.querySelector('.hero-stats');
            if (statRow) {
                const newStat = document.createElement('div');
                newStat.className = 'hero-stat';
                newStat.setAttribute('data-label', 'stars');
                newStat.innerHTML = `<span class="hero-stat-num">${data.stargazers_count}</span><span class="hero-stat-label">Repo Stars</span>`;
                statRow.appendChild(newStat);
            }
        }
    });
}

fetchGithubStats();

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