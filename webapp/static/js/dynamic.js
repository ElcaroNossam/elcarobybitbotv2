/**
 * Enliko Platform - Dynamic Effects Library
 * Version 4.0.0
 * 
 * Modern JavaScript effects, animations, and interactions
 * Import on every page after main scripts
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    EnlikoDynamic.init();
});

const EnlikoDynamic = {
    
    // Initialize all effects
    init() {
        this.initScrollReveal();
        this.initParticles();
        this.initHeaderScroll();
        this.initCounterAnimation();
        this.initRippleEffect();
        this.initCursorGlow();
        this.initSmoothScroll();
        this.initLazyLoad();
        this.initTypewriter();
        this.initNumberCountUp();
        this.initMagneticButtons();
        this.initParallax();
        console.log('[Enliko] Dynamic effects initialized');
    },
    
    // ===== SCROLL REVEAL =====
    initScrollReveal() {
        const reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
        
        if (reveals.length === 0) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        reveals.forEach(el => observer.observe(el));
    },
    
    // ===== PARTICLE BACKGROUND =====
    initParticles() {
        const container = document.querySelector('.particles-container');
        if (!container) return;
        
        const particleCount = window.innerWidth < 768 ? 15 : 30;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.animationDelay = `${Math.random() * 15}s`;
            particle.style.animationDuration = `${15 + Math.random() * 10}s`;
            container.appendChild(particle);
        }
    },
    
    // ===== HEADER SCROLL EFFECT =====
    initHeaderScroll() {
        const header = document.querySelector('.header');
        if (!header) return;
        
        let lastScroll = 0;
        
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            // Add scrolled class for background change
            if (currentScroll > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
            
            // Hide/show header on scroll (optional)
            // if (currentScroll > lastScroll && currentScroll > 300) {
            //     header.style.transform = 'translateY(-100%)';
            // } else {
            //     header.style.transform = 'translateY(0)';
            // }
            
            lastScroll = currentScroll;
        }, { passive: true });
    },
    
    // ===== COUNTER ANIMATION =====
    initCounterAnimation() {
        const counters = document.querySelectorAll('[data-counter]');
        if (counters.length === 0) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                    this.animateCounter(entry.target);
                    entry.target.classList.add('counted');
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => observer.observe(counter));
    },
    
    animateCounter(element) {
        const target = parseFloat(element.dataset.counter);
        const duration = parseInt(element.dataset.duration) || 2000;
        const decimals = (target.toString().split('.')[1] || '').length;
        const prefix = element.dataset.prefix || '';
        const suffix = element.dataset.suffix || '';
        
        const startTime = performance.now();
        
        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = target * easeOut;
            
            element.textContent = prefix + current.toFixed(decimals) + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        };
        
        requestAnimationFrame(updateCounter);
    },
    
    // ===== RIPPLE EFFECT =====
    initRippleEffect() {
        document.querySelectorAll('.btn, .ripple').forEach(button => {
            button.addEventListener('click', (e) => {
                const rect = button.getBoundingClientRect();
                const ripple = document.createElement('span');
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: rippleAnim 0.6s ease-out;
                    pointer-events: none;
                `;
                
                button.style.position = 'relative';
                button.style.overflow = 'hidden';
                button.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });
        
        // Add ripple animation keyframes
        if (!document.querySelector('#ripple-styles')) {
            const style = document.createElement('style');
            style.id = 'ripple-styles';
            style.textContent = `
                @keyframes rippleAnim {
                    to { transform: scale(4); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    },
    
    // ===== CURSOR GLOW EFFECT =====
    initCursorGlow() {
        const glowElements = document.querySelectorAll('.cursor-glow');
        if (glowElements.length === 0) return;
        
        glowElements.forEach(el => {
            el.addEventListener('mousemove', (e) => {
                const rect = el.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                el.style.setProperty('--cursor-x', `${x}px`);
                el.style.setProperty('--cursor-y', `${y}px`);
            });
        });
    },
    
    // ===== SMOOTH SCROLL =====
    initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    },
    
    // ===== LAZY LOADING =====
    initLazyLoad() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        if (lazyImages.length === 0) return;
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    },
    
    // ===== TYPEWRITER EFFECT =====
    initTypewriter() {
        const typewriters = document.querySelectorAll('[data-typewriter]');
        if (typewriters.length === 0) return;
        
        typewriters.forEach(el => {
            const text = el.dataset.typewriter;
            const speed = parseInt(el.dataset.speed) || 50;
            let index = 0;
            el.textContent = '';
            
            const type = () => {
                if (index < text.length) {
                    el.textContent += text.charAt(index);
                    index++;
                    setTimeout(type, speed);
                }
            };
            
            // Start when visible
            const observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    type();
                    observer.disconnect();
                }
            });
            
            observer.observe(el);
        });
    },
    
    // ===== NUMBER COUNT UP (for PnL, stats etc) =====
    initNumberCountUp() {
        // Auto-animate numbers that change in real-time
        document.querySelectorAll('[data-live-number]').forEach(el => {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach(mutation => {
                    if (mutation.type === 'characterData' || mutation.type === 'childList') {
                        el.classList.add('number-flash');
                        setTimeout(() => el.classList.remove('number-flash'), 300);
                    }
                });
            });
            
            observer.observe(el, { characterData: true, childList: true, subtree: true });
        });
        
        // Add flash animation
        if (!document.querySelector('#number-flash-styles')) {
            const style = document.createElement('style');
            style.id = 'number-flash-styles';
            style.textContent = `
                .number-flash {
                    animation: numberFlash 0.3s ease;
                }
                @keyframes numberFlash {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); color: var(--accent); }
                    100% { transform: scale(1); }
                }
            `;
            document.head.appendChild(style);
        }
    },
    
    // ===== MAGNETIC BUTTONS =====
    initMagneticButtons() {
        const magneticBtns = document.querySelectorAll('.btn-magnetic');
        if (magneticBtns.length === 0) return;
        
        magneticBtns.forEach(btn => {
            btn.addEventListener('mousemove', (e) => {
                const rect = btn.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                
                btn.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translate(0, 0)';
            });
        });
    },
    
    // ===== PARALLAX EFFECT =====
    initParallax() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        if (parallaxElements.length === 0) return;
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(el => {
                const speed = parseFloat(el.dataset.parallax) || 0.5;
                const offset = scrolled * speed;
                el.style.transform = `translateY(${offset}px)`;
            });
        }, { passive: true });
    },
    
    // ===== TOAST NOTIFICATIONS =====
    showToast(message, type = 'info', duration = 3000) {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: '<i class="fas fa-check-circle"></i>',
            error: '<i class="fas fa-exclamation-circle"></i>',
            warning: '<i class="fas fa-exclamation-triangle"></i>',
            info: '<i class="fas fa-info-circle"></i>'
        };
        
        toast.innerHTML = `
            ${icons[type] || icons.info}
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, duration);
        
        // Add slideOut animation
        if (!document.querySelector('#toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                @keyframes slideOutRight {
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    },
    
    // ===== MODAL HELPERS =====
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        const backdrop = document.querySelector('.modal-backdrop');
        
        if (modal && backdrop) {
            backdrop.classList.add('active');
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    },
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        const backdrop = document.querySelector('.modal-backdrop');
        
        if (modal && backdrop) {
            backdrop.classList.remove('active');
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    },
    
    closeAllModals() {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
        document.querySelectorAll('.modal-backdrop.active').forEach(backdrop => {
            backdrop.classList.remove('active');
        });
        document.body.style.overflow = '';
    },
    
    // ===== LOADING STATE =====
    showLoader(element) {
        element.classList.add('loading');
        element.dataset.originalContent = element.innerHTML;
        element.innerHTML = '<span class="loader"></span>';
        element.disabled = true;
    },
    
    hideLoader(element) {
        element.classList.remove('loading');
        element.innerHTML = element.dataset.originalContent;
        element.disabled = false;
    },
    
    // ===== SKELETON LOADING =====
    showSkeleton(container, count = 3) {
        container.innerHTML = '';
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-item';
            skeleton.innerHTML = `
                <div class="skeleton" style="width: 40px; height: 40px; border-radius: 8px;"></div>
                <div style="flex: 1;">
                    <div class="skeleton" style="width: 60%; height: 16px; margin-bottom: 8px;"></div>
                    <div class="skeleton" style="width: 40%; height: 14px;"></div>
                </div>
            `;
            skeleton.style.cssText = 'display: flex; gap: 16px; padding: 16px; margin-bottom: 12px;';
            container.appendChild(skeleton);
        }
    },
    
    // ===== COPY TO CLIPBOARD =====
    copyToClipboard(text, successMessage = 'Copied!') {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast(successMessage, 'success');
        }).catch(() => {
            this.showToast('Failed to copy', 'error');
        });
    },
    
    // ===== FORMAT HELPERS =====
    formatNumber(num, decimals = 2) {
        if (num >= 1e9) return (num / 1e9).toFixed(decimals) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(decimals) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(decimals) + 'K';
        return num.toFixed(decimals);
    },
    
    formatCurrency(num, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(num);
    },
    
    formatPercent(num) {
        const sign = num >= 0 ? '+' : '';
        return sign + num.toFixed(2) + '%';
    }
};

// Expose globally
window.EnlikoDynamic = EnlikoDynamic;
