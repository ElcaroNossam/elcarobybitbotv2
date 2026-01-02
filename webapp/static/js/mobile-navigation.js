/**
 * ElCaro Trading Platform - Mobile Navigation & Utilities
 * Version 2.0
 * 
 * Handles mobile menu toggles, touch interactions, and responsive behaviors
 */

(function() {
    'use strict';

    // ============================================
    // MOBILE MENU TOGGLE
    // ============================================
    
    /**
     * Initialize mobile hamburger menu
     */
    function initMobileMenu() {
        const mobileToggle = document.getElementById('mobile-toggle');
        const navLinks = document.querySelector('.nav-links');
        
        if (mobileToggle && navLinks) {
            mobileToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                navLinks.classList.toggle('active');
                
                // Update icon
                const icon = mobileToggle.querySelector('i');
                if (icon) {
                    if (navLinks.classList.contains('active')) {
                        icon.className = 'fas fa-times';
                    } else {
                        icon.className = 'fas fa-bars';
                    }
                }
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!e.target.closest('.navbar') && navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                    const icon = mobileToggle.querySelector('i');
                    if (icon) {
                        icon.className = 'fas fa-bars';
                    }
                }
            });
            
            // Close menu when clicking on a link
            const links = navLinks.querySelectorAll('a');
            links.forEach(link => {
                link.addEventListener('click', function() {
                    if (window.innerWidth <= 768) {
                        navLinks.classList.remove('active');
                        const icon = mobileToggle.querySelector('i');
                        if (icon) {
                            icon.className = 'fas fa-bars';
                        }
                    }
                });
            });
        }
    }
    
    // ============================================
    // TERMINAL SIDEBAR TOGGLE
    // ============================================
    
    /**
     * Initialize terminal sidebar toggle for mobile
     */
    function initTerminalSidebar() {
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        const sidebar = document.querySelector('.terminal-sidebar, .left-panel');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', function(e) {
                e.preventDefault();
                sidebar.classList.toggle('active');
                
                // Update icon
                const icon = sidebarToggle.querySelector('i');
                if (icon) {
                    if (sidebar.classList.contains('active')) {
                        icon.className = 'fas fa-times';
                    } else {
                        icon.className = 'fas fa-bars';
                    }
                }
            });
            
            // Close sidebar when clicking outside on mobile
            if (window.innerWidth <= 768) {
                document.addEventListener('click', function(e) {
                    if (!e.target.closest('.terminal-sidebar') && 
                        !e.target.closest('.left-panel') && 
                        !e.target.closest('.sidebar-toggle') && 
                        sidebar.classList.contains('active')) {
                        sidebar.classList.remove('active');
                        const icon = sidebarToggle.querySelector('i');
                        if (icon) {
                            icon.className = 'fas fa-bars';
                        }
                    }
                });
            }
        }
    }
    
    // ============================================
    // ADMIN SIDEBAR TOGGLE
    // ============================================
    
    /**
     * Initialize admin sidebar toggle for mobile
     */
    function initAdminSidebar() {
        const adminToggle = document.querySelector('.admin-menu-toggle');
        const adminSidebar = document.querySelector('.admin-sidebar');
        
        if (adminToggle && adminSidebar) {
            adminToggle.addEventListener('click', function(e) {
                e.preventDefault();
                adminSidebar.classList.toggle('active');
            });
            
            // Close sidebar when clicking outside
            document.addEventListener('click', function(e) {
                if (!e.target.closest('.admin-sidebar') && 
                    !e.target.closest('.admin-menu-toggle') && 
                    adminSidebar.classList.contains('active')) {
                    adminSidebar.classList.remove('active');
                }
            });
        }
    }
    
    // ============================================
    // SETTINGS MOBILE NAVIGATION
    // ============================================
    
    /**
     * Initialize settings mobile dropdown navigation
     */
    function initSettingsNav() {
        const settingsNavMobile = document.querySelector('.settings-nav-mobile select');
        
        if (settingsNavMobile) {
            settingsNavMobile.addEventListener('change', function() {
                const sectionId = this.value;
                const section = document.getElementById(sectionId);
                
                if (section) {
                    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        }
    }
    
    // ============================================
    // TOUCH SWIPE GESTURES
    // ============================================
    
    /**
     * Add swipe gestures for sidebars on mobile
     */
    function initSwipeGestures() {
        if (window.innerWidth > 768) return;
        
        let touchStartX = 0;
        let touchEndX = 0;
        
        const sidebar = document.querySelector('.terminal-sidebar, .left-panel, .admin-sidebar');
        
        if (sidebar) {
            document.addEventListener('touchstart', function(e) {
                touchStartX = e.changedTouches[0].screenX;
            }, { passive: true });
            
            document.addEventListener('touchend', function(e) {
                touchEndX = e.changedTouches[0].screenX;
                handleSwipe();
            }, { passive: true });
            
            function handleSwipe() {
                const swipeThreshold = 100;
                
                // Swipe right to open (from left edge)
                if (touchStartX < 50 && touchEndX - touchStartX > swipeThreshold) {
                    sidebar.classList.add('active');
                }
                
                // Swipe left to close
                if (touchEndX - touchStartX < -swipeThreshold && sidebar.classList.contains('active')) {
                    sidebar.classList.remove('active');
                }
            }
        }
    }
    
    // ============================================
    // TABLE SCROLL HINT
    // ============================================
    
    /**
     * Show scroll hint on horizontally scrollable tables
     */
    function initTableScrollHint() {
        const tables = document.querySelectorAll('.positions-table-container, .screener-table-container, .trades-list, .users-table-container');
        
        tables.forEach(container => {
            if (container.scrollWidth > container.clientWidth) {
                container.classList.add('scrollable');
                
                // Add visual hint
                const hint = document.createElement('div');
                hint.className = 'scroll-hint';
                hint.innerHTML = '<i class="fas fa-arrows-alt-h"></i> Swipe to scroll';
                hint.style.cssText = `
                    position: absolute;
                    bottom: 10px;
                    right: 10px;
                    background: rgba(220, 38, 38, 0.9);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    pointer-events: none;
                    animation: fadeOut 3s forwards;
                    z-index: 10;
                `;
                
                container.style.position = 'relative';
                container.appendChild(hint);
                
                // Remove hint after first scroll
                container.addEventListener('scroll', function() {
                    hint.remove();
                }, { once: true });
            }
        });
    }
    
    // ============================================
    // ORIENTATION CHANGE HANDLER
    // ============================================
    
    /**
     * Handle orientation changes
     */
    function handleOrientationChange() {
        // Close all open menus/sidebars on orientation change
        const navLinks = document.querySelector('.nav-links');
        const sidebar = document.querySelector('.terminal-sidebar, .left-panel, .admin-sidebar');
        
        if (navLinks && navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
        }
        
        if (sidebar && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
        }
        
        // Trigger resize event for charts and responsive elements
        window.dispatchEvent(new Event('resize'));
    }
    
    // ============================================
    // VIEWPORT HEIGHT FIX (iOS Safari)
    // ============================================
    
    /**
     * Fix viewport height issues on mobile browsers (especially iOS)
     */
    function fixViewportHeight() {
        // Set CSS custom property for real viewport height
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setVH();
        window.addEventListener('resize', setVH);
        window.addEventListener('orientationchange', setVH);
    }
    
    // ============================================
    // PREVENT DOUBLE-TAP ZOOM
    // ============================================
    
    /**
     * Prevent accidental double-tap zoom on buttons
     */
    function preventDoubleTapZoom() {
        let lastTouchEnd = 0;
        
        document.addEventListener('touchend', function(e) {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, { passive: false });
    }
    
    // ============================================
    // MOBILE CARD-STYLE TABLES
    // ============================================
    
    /**
     * Convert tables to card style on mobile
     */
    function initMobileCardTables() {
        if (window.innerWidth <= 768) {
            const tables = document.querySelectorAll('table:not(.no-mobile-cards)');
            
            tables.forEach(table => {
                if (table.classList.contains('mobile-cards')) {
                    return; // Already converted
                }
                
                // Add data-label attributes for mobile view
                const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    cells.forEach((cell, index) => {
                        if (headers[index]) {
                            cell.setAttribute('data-label', headers[index]);
                        }
                    });
                });
                
                table.classList.add('mobile-cards');
            });
        }
    }
    
    // ============================================
    // ACCESSIBILITY ENHANCEMENTS
    // ============================================
    
    /**
     * Add accessibility improvements for mobile
     */
    function enhanceAccessibility() {
        // Add aria-labels to touch targets
        const buttons = document.querySelectorAll('button, a.btn, .clickable');
        
        buttons.forEach(btn => {
            if (!btn.getAttribute('aria-label') && !btn.textContent.trim()) {
                const icon = btn.querySelector('i');
                if (icon) {
                    const iconClass = icon.className;
                    let label = 'Button';
                    
                    if (iconClass.includes('fa-bars')) label = 'Open menu';
                    if (iconClass.includes('fa-times')) label = 'Close menu';
                    if (iconClass.includes('fa-search')) label = 'Search';
                    if (iconClass.includes('fa-filter')) label = 'Filter';
                    if (iconClass.includes('fa-sort')) label = 'Sort';
                    
                    btn.setAttribute('aria-label', label);
                }
            }
        });
        
        // Ensure all interactive elements are keyboard accessible
        const interactive = document.querySelectorAll('.clickable:not(button):not(a)');
        interactive.forEach(el => {
            if (!el.hasAttribute('tabindex')) {
                el.setAttribute('tabindex', '0');
            }
            
            if (!el.hasAttribute('role')) {
                el.setAttribute('role', 'button');
            }
        });
    }
    
    // ============================================
    // PERFORMANCE MONITORING
    // ============================================
    
    /**
     * Monitor and optimize performance on mobile
     */
    function initPerformanceMonitoring() {
        if (window.innerWidth > 1024) return;
        
        // Lazy load images
        if ('IntersectionObserver' in window) {
            const images = document.querySelectorAll('img[data-src]');
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        }
        
        // Reduce animation on low-end devices
        if (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4) {
            document.documentElement.classList.add('reduce-motion');
        }
    }
    
    // ============================================
    // INITIALIZATION
    // ============================================
    
    /**
     * Initialize all mobile features
     */
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        // Initialize features
        fixViewportHeight();
        initMobileMenu();
        initTerminalSidebar();
        initAdminSidebar();
        initSettingsNav();
        initSwipeGestures();
        initTableScrollHint();
        initMobileCardTables();
        enhanceAccessibility();
        initPerformanceMonitoring();
        preventDoubleTapZoom();
        
        // Handle orientation changes
        window.addEventListener('orientationchange', handleOrientationChange);
        
        // Re-initialize on window resize (debounced)
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                initTableScrollHint();
                initMobileCardTables();
            }, 250);
        });
        
        // Add mobile class to body
        if (window.innerWidth <= 768) {
            document.body.classList.add('mobile');
        }
        
        console.log('ElCaro Mobile Navigation initialized ✓');
    }
    
    // Auto-initialize
    init();
    
    // Export for manual initialization if needed
    window.ElCaroMobile = {
        init,
        initMobileMenu,
        initTerminalSidebar,
        initAdminSidebar,
        initSwipeGestures
    };
    
})();

// ============================================
// CSS ANIMATION FOR SCROLL HINT
// ============================================
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        0% { opacity: 1; }
        70% { opacity: 1; }
        100% { opacity: 0; }
    }
    
    .scrollable {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
`;
document.head.appendChild(style);
