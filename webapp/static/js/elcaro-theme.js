/**
 * ElCaro Theme & Language Manager
 * Unified system for theme and language switching across all pages
 */

(function() {
    'use strict';
    
    // Language definitions with flags
    const LANGUAGES = {
        'en': { flag: '🇺🇸', name: 'English' },
        'ru': { flag: '🇷🇺', name: 'Русский' },
        'uk': { flag: '🇺🇦', name: 'Українська' },
        'zh': { flag: '🇨🇳', name: '中文' },
        'es': { flag: '🇪🇸', name: 'Español' },
        'de': { flag: '🇩🇪', name: 'Deutsch' },
        'fr': { flag: '🇫🇷', name: 'Français' },
        'it': { flag: '🇮🇹', name: 'Italiano' },
        'ja': { flag: '🇯🇵', name: '日本語' },
        'ar': { flag: '🇸🇦', name: 'العربية' },
        'he': { flag: '🇮🇱', name: 'עברית' },
        'pl': { flag: '🇵🇱', name: 'Polski' }
    };
    
    const STORAGE_KEYS = {
        language: 'elcaro_language',
        theme: 'elcaro_theme'
    };
    
    // ===== Language Functions =====
    
    function toggleLangMenu() {
        const menu = document.getElementById('langMenu');
        const themeMenu = document.getElementById('themeMenu');
        
        if (themeMenu && themeMenu.classList.contains('show')) {
            themeMenu.classList.remove('show');
        }
        
        if (menu) {
            menu.classList.toggle('show');
        }
    }
    
    function setLanguage(lang) {
        const langData = LANGUAGES[lang];
        if (!langData) return;
        
        // Update flag icon
        const flag = document.getElementById('currentLangFlag');
        if (flag) {
            flag.textContent = langData.flag;
        }
        
        // Update active state in menu
        document.querySelectorAll('.lang-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.lang === lang) {
                item.classList.add('active');
            }
        });
        
        // Save to localStorage
        localStorage.setItem(STORAGE_KEYS.language, lang);
        
        // Close menu
        const menu = document.getElementById('langMenu');
        if (menu) menu.classList.remove('show');
        
        // Dispatch event for other components
        window.dispatchEvent(new CustomEvent('elcaro:languageChanged', { detail: { lang, langData } }));
        
        // Apply RTL for Arabic and Hebrew
        if (lang === 'ar' || lang === 'he') {
            document.documentElement.setAttribute('dir', 'rtl');
        } else {
            document.documentElement.removeAttribute('dir');
        }
    }
    
    function getLanguage() {
        return localStorage.getItem(STORAGE_KEYS.language) || 'en';
    }
    
    // ===== Theme Functions =====
    
    function toggleThemeMenu() {
        const menu = document.getElementById('themeMenu');
        const langMenu = document.getElementById('langMenu');
        
        if (langMenu && langMenu.classList.contains('show')) {
            langMenu.classList.remove('show');
        }
        
        if (menu) {
            menu.classList.toggle('show');
        }
    }
    
    function setTheme(theme) {
        const html = document.documentElement;
        const icon = document.getElementById('themeIcon');
        
        // Remove any existing theme
        html.removeAttribute('data-theme');
        
        if (theme === 'light') {
            html.setAttribute('data-theme', 'light');
            if (icon) icon.className = 'fas fa-sun';
        } else if (theme === 'system') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (!prefersDark) {
                html.setAttribute('data-theme', 'light');
            }
            if (icon) icon.className = 'fas fa-desktop';
        } else {
            // dark theme (default)
            if (icon) icon.className = 'fas fa-moon';
        }
        
        // Update active state in menu
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.theme === theme) {
                option.classList.add('active');
            }
        });
        
        // Save to localStorage
        localStorage.setItem(STORAGE_KEYS.theme, theme);
        
        // Close menu
        const menu = document.getElementById('themeMenu');
        if (menu) menu.classList.remove('show');
        
        // Dispatch event for other components
        window.dispatchEvent(new CustomEvent('elcaro:themeChanged', { detail: { theme } }));
    }
    
    function getTheme() {
        return localStorage.getItem(STORAGE_KEYS.theme) || 'dark';
    }
    
    // ===== Initialization =====
    
    function initLanguageAndTheme() {
        // Language
        const savedLang = getLanguage();
        const langData = LANGUAGES[savedLang];
        
        if (langData) {
            const flag = document.getElementById('currentLangFlag');
            if (flag) flag.textContent = langData.flag;
            
            document.querySelectorAll('.lang-item').forEach(item => {
                item.classList.remove('active');
                if (item.dataset.lang === savedLang) {
                    item.classList.add('active');
                }
            });
            
            // Apply RTL for Arabic
            if (savedLang === 'ar') {
                document.documentElement.setAttribute('dir', 'rtl');
            }
        }
        
        // Theme
        const savedTheme = getTheme();
        const html = document.documentElement;
        const icon = document.getElementById('themeIcon');
        
        if (savedTheme === 'light') {
            html.setAttribute('data-theme', 'light');
            if (icon) icon.className = 'fas fa-sun';
        } else if (savedTheme === 'system') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (!prefersDark) {
                html.setAttribute('data-theme', 'light');
            }
            if (icon) icon.className = 'fas fa-desktop';
        } else {
            if (icon) icon.className = 'fas fa-moon';
        }
        
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.theme === savedTheme) {
                option.classList.add('active');
            }
        });
    }
    
    // Close dropdowns when clicking outside
    function setupDropdownClose() {
        document.addEventListener('click', function(e) {
            const langSelector = document.getElementById('langSelector');
            const themeSwitcher = document.getElementById('themeSwitcher');
            
            if (langSelector && !langSelector.contains(e.target)) {
                const menu = document.getElementById('langMenu');
                if (menu) menu.classList.remove('show');
            }
            
            if (themeSwitcher && !themeSwitcher.contains(e.target)) {
                const menu = document.getElementById('themeMenu');
                if (menu) menu.classList.remove('show');
            }
        });
    }
    
    // Listen for system theme changes
    function setupSystemThemeListener() {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            const savedTheme = getTheme();
            if (savedTheme === 'system') {
                const html = document.documentElement;
                if (e.matches) {
                    html.removeAttribute('data-theme');
                } else {
                    html.setAttribute('data-theme', 'light');
                }
            }
        });
    }
    
    // Auto-initialize on DOM ready
    function init() {
        initLanguageAndTheme();
        setupDropdownClose();
        setupSystemThemeListener();
    }
    
    // Run init when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Export to global scope
    window.ElCaroTheme = {
        LANGUAGES,
        toggleLangMenu,
        setLanguage,
        getLanguage,
        toggleThemeMenu,
        setTheme,
        getTheme,
        init: initLanguageAndTheme
    };
    
    // Also expose individual functions for inline handlers
    window.toggleLangMenu = toggleLangMenu;
    window.toggleThemeMenu = toggleThemeMenu;
    window.setLanguage = setLanguage;
    window.setTheme = setTheme;
    window.initLanguageAndTheme = initLanguageAndTheme;
    
    // ===== Mobile Menu =====
    
    function setupMobileMenu() {
        const mobileToggle = document.getElementById('mobile-toggle');
        const navLinks = document.querySelector('.nav-links');
        const navbar = document.querySelector('.navbar');
        
        if (!mobileToggle) return;
        
        // Create mobile nav overlay
        let mobileNav = document.querySelector('.mobile-nav');
        if (!mobileNav && navLinks) {
            mobileNav = document.createElement('div');
            mobileNav.className = 'mobile-nav';
            mobileNav.innerHTML = `
                <button class="mobile-close" onclick="toggleMobileMenu()">
                    <i class="fas fa-times"></i>
                </button>
                <div class="mobile-nav-links">
                    ${navLinks.innerHTML}
                </div>
            `;
            document.body.appendChild(mobileNav);
        }
        
        mobileToggle.addEventListener('click', toggleMobileMenu);
        
        // Close on link click
        if (mobileNav) {
            mobileNav.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    mobileNav.classList.remove('open');
                    document.body.style.overflow = '';
                });
            });
        }
    }
    
    function toggleMobileMenu() {
        const mobileNav = document.querySelector('.mobile-nav');
        const mobileToggle = document.getElementById('mobile-toggle');
        
        if (mobileNav) {
            mobileNav.classList.toggle('open');
            document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
            
            // Update toggle icon
            if (mobileToggle) {
                const icon = mobileToggle.querySelector('i');
                if (icon) {
                    icon.className = mobileNav.classList.contains('open') ? 'fas fa-times' : 'fas fa-bars';
                }
            }
        }
    }
    
    // Expose mobile menu functions
    window.toggleMobileMenu = toggleMobileMenu;
    
    // Setup mobile menu on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupMobileMenu);
    } else {
        setupMobileMenu();
    }
    
})();
