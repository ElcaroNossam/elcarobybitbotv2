/**
 * Enliko — Mobile Bottom Navigation
 * Auto-highlights active page, handles auth-aware nav
 */
(function() {
    'use strict';

    function initBottomNav() {
        const nav = document.getElementById('bottomNav');
        if (!nav) return;

        // Detect current page
        const path = window.location.pathname;
        const items = nav.querySelectorAll('.bottom-nav-item');
        
        items.forEach(item => {
            item.classList.remove('active');
            const href = item.getAttribute('href');
            if (!href) return;
            
            // Exact or prefix match
            if (path === href || (href !== '/' && path.startsWith(href))) {
                item.classList.add('active');
            }
        });

        // Special: /dashboard is "home"
        if (path === '/' || path === '/dashboard' || path === '/home') {
            const homeItem = nav.querySelector('[data-nav="home"]');
            if (homeItem) {
                items.forEach(i => i.classList.remove('active'));
                homeItem.classList.add('active');
            }
        }
    }

    /**
     * Auth-aware navigation — hide login/show logout based on token
     */
    function updateAuthNav() {
        const token = localStorage.getItem('enliko_token');
        const isAuth = !!token;

        // Show/hide auth buttons in navbar
        document.querySelectorAll('.auth-login-btn').forEach(el => {
            el.style.display = isAuth ? 'none' : '';
        });
        document.querySelectorAll('.auth-logout-btn').forEach(el => {
            el.style.display = isAuth ? '' : 'none';
        });
        document.querySelectorAll('.auth-only').forEach(el => {
            el.style.display = isAuth ? '' : 'none';
        });
        document.querySelectorAll('.no-auth-only').forEach(el => {
            el.style.display = isAuth ? 'none' : '';
        });
    }

    /**
     * Logout handler
     */
    window.logout = function() {
        localStorage.removeItem('enliko_token');
        localStorage.removeItem('enliko_user');
        localStorage.removeItem('enliko_user_id');
        window.location.href = '/';
    };

    // Init on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initBottomNav();
            updateAuthNav();
        });
    } else {
        initBottomNav();
        updateAuthNav();
    }
})();
