/**
 * Enliko Cookie Consent Banner
 * ============================
 * GDPR-compliant cookie consent management
 * 
 * Usage: Include this script on all pages, it will auto-initialize
 * 
 * <script src="/static/js/cookie-consent.js"></script>
 */

(function() {
    'use strict';
    
    const COOKIE_NAME = 'enliko_cookie_consent';
    const COOKIE_EXPIRY_DAYS = 365;
    
    // Styles for the consent banner
    const STYLES = `
        .cookie-consent-banner {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--bg-secondary, #1a1a2e);
            border-top: 1px solid var(--border, #333);
            padding: 20px;
            z-index: 10000;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
            animation: slideUp 0.3s ease-out;
        }
        
        @keyframes slideUp {
            from {
                transform: translateY(100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        .cookie-consent-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .cookie-consent-text {
            flex: 1;
            min-width: 300px;
        }
        
        .cookie-consent-text h3 {
            margin: 0 0 8px 0;
            font-size: 1.1rem;
            color: var(--text-primary, #fff);
        }
        
        .cookie-consent-text p {
            margin: 0;
            font-size: 0.9rem;
            color: var(--text-secondary, #aaa);
            line-height: 1.5;
        }
        
        .cookie-consent-text a {
            color: var(--primary, #6366f1);
            text-decoration: none;
        }
        
        .cookie-consent-text a:hover {
            text-decoration: underline;
        }
        
        .cookie-consent-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .cookie-consent-btn {
            padding: 10px 24px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: all 0.2s ease;
        }
        
        .cookie-consent-btn-accept {
            background: var(--primary, #6366f1);
            color: white;
        }
        
        .cookie-consent-btn-accept:hover {
            background: var(--primary-hover, #5558e3);
            transform: translateY(-1px);
        }
        
        .cookie-consent-btn-settings {
            background: transparent;
            color: var(--text-secondary, #aaa);
            border: 1px solid var(--border, #333);
        }
        
        .cookie-consent-btn-settings:hover {
            background: var(--bg-tertiary, #252538);
            color: var(--text-primary, #fff);
        }
        
        /* Settings Modal */
        .cookie-settings-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10001;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.2s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .cookie-settings-content {
            background: var(--bg-secondary, #1a1a2e);
            border-radius: 16px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            padding: 24px;
        }
        
        .cookie-settings-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .cookie-settings-header h2 {
            margin: 0;
            font-size: 1.3rem;
            color: var(--text-primary, #fff);
        }
        
        .cookie-settings-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            color: var(--text-secondary, #aaa);
            cursor: pointer;
        }
        
        .cookie-category {
            background: var(--bg-tertiary, #252538);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }
        
        .cookie-category-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .cookie-category-name {
            font-weight: 500;
            color: var(--text-primary, #fff);
        }
        
        .cookie-category-desc {
            font-size: 0.85rem;
            color: var(--text-secondary, #aaa);
            margin-top: 8px;
            line-height: 1.4;
        }
        
        .cookie-toggle {
            position: relative;
            width: 48px;
            height: 26px;
        }
        
        .cookie-toggle input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .cookie-toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: var(--border, #333);
            transition: 0.3s;
            border-radius: 26px;
        }
        
        .cookie-toggle-slider:before {
            position: absolute;
            content: "";
            height: 20px;
            width: 20px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: 0.3s;
            border-radius: 50%;
        }
        
        .cookie-toggle input:checked + .cookie-toggle-slider {
            background-color: var(--primary, #6366f1);
        }
        
        .cookie-toggle input:checked + .cookie-toggle-slider:before {
            transform: translateX(22px);
        }
        
        .cookie-toggle input:disabled + .cookie-toggle-slider {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .cookie-settings-footer {
            margin-top: 20px;
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }
        
        @media (max-width: 600px) {
            .cookie-consent-content {
                flex-direction: column;
                text-align: center;
            }
            
            .cookie-consent-buttons {
                justify-content: center;
                width: 100%;
            }
            
            .cookie-consent-btn {
                flex: 1;
            }
        }
    `;
    
    // Cookie utility functions
    function setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
    }
    
    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i].trim();
            if (c.indexOf(nameEQ) === 0) {
                return c.substring(nameEQ.length, c.length);
            }
        }
        return null;
    }
    
    // Main consent manager
    const CookieConsent = {
        settings: {
            essential: true,    // Always required
            functional: true,   // Default on
            analytics: false    // Default off
        },
        
        init: function() {
            // Inject styles
            const styleSheet = document.createElement('style');
            styleSheet.textContent = STYLES;
            document.head.appendChild(styleSheet);
            
            // Check if consent already given
            const existingConsent = getCookie(COOKIE_NAME);
            if (existingConsent) {
                try {
                    this.settings = JSON.parse(existingConsent);
                } catch (e) {
                    // Invalid cookie, show banner
                    this.showBanner();
                }
            } else {
                // No consent yet, show banner
                this.showBanner();
            }
        },
        
        showBanner: function() {
            const banner = document.createElement('div');
            banner.className = 'cookie-consent-banner';
            banner.id = 'cookie-consent-banner';
            banner.innerHTML = `
                <div class="cookie-consent-content">
                    <div class="cookie-consent-text">
                        <h3>🍪 We use cookies</h3>
                        <p>
                            We use essential cookies to make our platform work. 
                            With your consent, we may also use functional cookies to improve your experience.
                            <a href="/cookies">Learn more</a>
                        </p>
                    </div>
                    <div class="cookie-consent-buttons">
                        <button class="cookie-consent-btn cookie-consent-btn-settings" onclick="CookieConsent.showSettings()">
                            ⚙️ Customize
                        </button>
                        <button class="cookie-consent-btn cookie-consent-btn-accept" onclick="CookieConsent.acceptAll()">
                            ✅ Accept All
                        </button>
                    </div>
                </div>
            `;
            document.body.appendChild(banner);
        },
        
        showSettings: function() {
            const modal = document.createElement('div');
            modal.className = 'cookie-settings-modal';
            modal.id = 'cookie-settings-modal';
            modal.innerHTML = `
                <div class="cookie-settings-content">
                    <div class="cookie-settings-header">
                        <h2>🍪 Cookie Settings</h2>
                        <button class="cookie-settings-close" onclick="CookieConsent.closeSettings()">×</button>
                    </div>
                    
                    <div class="cookie-category">
                        <div class="cookie-category-header">
                            <span class="cookie-category-name">🔒 Essential Cookies</span>
                            <label class="cookie-toggle">
                                <input type="checkbox" checked disabled>
                                <span class="cookie-toggle-slider"></span>
                            </label>
                        </div>
                        <p class="cookie-category-desc">
                            Required for the platform to function. Cannot be disabled.
                        </p>
                    </div>
                    
                    <div class="cookie-category">
                        <div class="cookie-category-header">
                            <span class="cookie-category-name">⚙️ Functional Cookies</span>
                            <label class="cookie-toggle">
                                <input type="checkbox" id="cookie-functional" ${this.settings.functional ? 'checked' : ''}>
                                <span class="cookie-toggle-slider"></span>
                            </label>
                        </div>
                        <p class="cookie-category-desc">
                            Remember your preferences like theme and language.
                        </p>
                    </div>
                    
                    <div class="cookie-category">
                        <div class="cookie-category-header">
                            <span class="cookie-category-name">📊 Analytics Cookies</span>
                            <label class="cookie-toggle">
                                <input type="checkbox" id="cookie-analytics" ${this.settings.analytics ? 'checked' : ''}>
                                <span class="cookie-toggle-slider"></span>
                            </label>
                        </div>
                        <p class="cookie-category-desc">
                            Help us understand how you use the platform (anonymous data only).
                        </p>
                    </div>
                    
                    <div class="cookie-settings-footer">
                        <button class="cookie-consent-btn cookie-consent-btn-settings" onclick="CookieConsent.rejectNonEssential()">
                            Essential Only
                        </button>
                        <button class="cookie-consent-btn cookie-consent-btn-accept" onclick="CookieConsent.saveSettings()">
                            Save Preferences
                        </button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Close on background click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeSettings();
                }
            });
        },
        
        closeSettings: function() {
            const modal = document.getElementById('cookie-settings-modal');
            if (modal) {
                modal.remove();
            }
        },
        
        saveSettings: function() {
            const functional = document.getElementById('cookie-functional');
            const analytics = document.getElementById('cookie-analytics');
            
            this.settings = {
                essential: true,
                functional: functional ? functional.checked : true,
                analytics: analytics ? analytics.checked : false
            };
            
            this.save();
        },
        
        acceptAll: function() {
            this.settings = {
                essential: true,
                functional: true,
                analytics: true
            };
            this.save();
        },
        
        rejectNonEssential: function() {
            this.settings = {
                essential: true,
                functional: false,
                analytics: false
            };
            this.save();
        },
        
        save: function() {
            setCookie(COOKIE_NAME, JSON.stringify(this.settings), COOKIE_EXPIRY_DAYS);
            
            // Remove banner and modal
            const banner = document.getElementById('cookie-consent-banner');
            if (banner) {
                banner.style.animation = 'slideUp 0.3s ease-out reverse';
                setTimeout(() => banner.remove(), 300);
            }
            
            const modal = document.getElementById('cookie-settings-modal');
            if (modal) {
                modal.remove();
            }
            
            // Dispatch event for other scripts to listen
            window.dispatchEvent(new CustomEvent('cookieConsentChanged', { 
                detail: this.settings 
            }));
        },
        
        // Public API
        hasConsent: function(category) {
            return this.settings[category] === true;
        },
        
        getSettings: function() {
            return { ...this.settings };
        }
    };
    
    // Export to window
    window.CookieConsent = CookieConsent;
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => CookieConsent.init());
    } else {
        CookieConsent.init();
    }
    
})();
