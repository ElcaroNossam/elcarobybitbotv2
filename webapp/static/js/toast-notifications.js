/**
 * ElCaro Toast Notifications System
 * Beautiful toast notifications matching ElCaro design
 */

class ToastNotifications {
    constructor() {
        this.container = null;
        this.init();
    }
    
    init() {
        // Create container if not exists
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
            
            // Add styles
            this.injectStyles();
        } else {
            this.container = document.getElementById('toast-container');
        }
    }
    
    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .toast-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 12px;
                pointer-events: none;
            }
            
            .toast {
                background: var(--bg-secondary, #111111);
                border: 1px solid var(--border, rgba(255, 255, 255, 0.06));
                border-radius: 12px;
                padding: 16px 20px;
                min-width: 320px;
                max-width: 420px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                display: flex;
                align-items: flex-start;
                gap: 12px;
                pointer-events: auto;
                animation: toastSlideIn 0.3s ease;
                backdrop-filter: blur(10px);
                position: relative;
                overflow: hidden;
            }
            
            .toast::before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 4px;
                background: currentColor;
            }
            
            @keyframes toastSlideIn {
                from {
                    transform: translateX(120%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes toastSlideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(120%);
                    opacity: 0;
                }
            }
            
            .toast.hiding {
                animation: toastSlideOut 0.3s ease forwards;
            }
            
            .toast-icon {
                font-size: 20px;
                flex-shrink: 0;
                margin-top: 2px;
            }
            
            .toast-content {
                flex: 1;
            }
            
            .toast-title {
                font-weight: 600;
                font-size: 14px;
                color: var(--text-primary, #f8fafc);
                margin-bottom: 4px;
            }
            
            .toast-message {
                font-size: 13px;
                color: var(--text-secondary, #94a3b8);
                line-height: 1.4;
            }
            
            .toast-close {
                background: none;
                border: none;
                color: var(--text-muted, #64748b);
                cursor: pointer;
                padding: 4px;
                font-size: 16px;
                opacity: 0.6;
                transition: opacity 0.2s;
                flex-shrink: 0;
            }
            
            .toast-close:hover {
                opacity: 1;
            }
            
            .toast-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 2px;
                background: currentColor;
                width: 100%;
                transform-origin: left;
                animation: toastProgress linear;
            }
            
            @keyframes toastProgress {
                from { transform: scaleX(1); }
                to { transform: scaleX(0); }
            }
            
            /* Toast Types */
            .toast.success {
                color: var(--green, #22c55e);
                border-color: rgba(34, 197, 94, 0.2);
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.05) 0%, var(--bg-secondary, #111111) 100%);
            }
            
            .toast.error {
                color: var(--red, #ef4444);
                border-color: rgba(239, 68, 68, 0.2);
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, var(--bg-secondary, #111111) 100%);
            }
            
            .toast.warning {
                color: var(--yellow, #eab308);
                border-color: rgba(234, 179, 8, 0.2);
                background: linear-gradient(135deg, rgba(234, 179, 8, 0.05) 0%, var(--bg-secondary, #111111) 100%);
            }
            
            .toast.info {
                color: var(--accent, #7C3AED);
                border-color: rgba(124, 58, 237, 0.2);
                background: linear-gradient(135deg, rgba(124, 58, 237, 0.05) 0%, var(--bg-secondary, #111111) 100%);
            }
            
            /* Mobile */
            @media (max-width: 768px) {
                .toast-container {
                    left: 20px;
                    right: 20px;
                    top: 20px;
                }
                
                .toast {
                    min-width: unset;
                    max-width: unset;
                    width: 100%;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    show(options) {
        const {
            type = 'info',
            title = '',
            message = '',
            duration = 4000,
            icon = null
        } = options;
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Icon
        const iconMap = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        const toastIcon = icon || iconMap[type];
        
        toast.innerHTML = `
            <div class="toast-icon">${toastIcon}</div>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">×</button>
            ${duration > 0 ? `<div class="toast-progress" style="animation-duration: ${duration}ms;"></div>` : ''}
        `;
        
        // Add to container
        this.container.appendChild(toast);
        
        // Close button
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.hide(toast));
        
        // Auto hide
        if (duration > 0) {
            setTimeout(() => this.hide(toast), duration);
        }
        
        return toast;
    }
    
    hide(toast) {
        toast.classList.add('hiding');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
    
    success(message, title = 'Success') {
        return this.show({ type: 'success', title, message });
    }
    
    error(message, title = 'Error') {
        return this.show({ type: 'error', title, message });
    }
    
    warning(message, title = 'Warning') {
        return this.show({ type: 'warning', title, message });
    }
    
    info(message, title = 'Info') {
        return this.show({ type: 'info', title, message });
    }
}

// Create global instance
window.toast = new ToastNotifications();

// Convenience methods
window.showToast = (message, type = 'info', title = '') => {
    return window.toast.show({ type, message, title });
};

window.showSuccess = (message, title) => window.toast.success(message, title);
window.showError = (message, title) => window.toast.error(message, title);
window.showWarning = (message, title) => window.toast.warning(message, title);
window.showInfo = (message, title) => window.toast.info(message, title);
