/**
 * ElCaro Beautiful Modal Dialogs
 * Replace ugly browser alert/confirm with styled modals
 */

class ModalDialogs {
    constructor() {
        this.activeModal = null;
        this.injectStyles();
    }
    
    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .modal-overlay {
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.75);
                backdrop-filter: blur(8px);
                z-index: 100000;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: modalFadeIn 0.2s ease;
                padding: 20px;
            }
            
            @keyframes modalFadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            .modal-dialog {
                background: var(--bg-secondary, #111111);
                border: 1px solid var(--border, rgba(255, 255, 255, 0.1));
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
                max-width: 440px;
                width: 100%;
                animation: modalSlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                overflow: hidden;
            }
            
            @keyframes modalSlideUp {
                from { 
                    transform: translateY(20px) scale(0.95);
                    opacity: 0;
                }
                to { 
                    transform: translateY(0) scale(1);
                    opacity: 1;
                }
            }
            
            .modal-header {
                padding: 24px;
                border-bottom: 1px solid var(--border, rgba(255, 255, 255, 0.06));
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .modal-icon {
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                flex-shrink: 0;
            }
            
            .modal-icon.warning {
                background: linear-gradient(135deg, rgba(234, 179, 8, 0.15) 0%, rgba(234, 179, 8, 0.05) 100%);
                color: var(--yellow, #eab308);
            }
            
            .modal-icon.danger {
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%);
                color: var(--red, #ef4444);
            }
            
            .modal-icon.info {
                background: linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(37, 99, 235, 0.05) 100%);
                color: var(--accent, #2563eb);
            }
            
            .modal-icon.success {
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(34, 197, 94, 0.05) 100%);
                color: var(--green, #22c55e);
            }
            
            .modal-title-group {
                flex: 1;
            }
            
            .modal-title {
                font-size: 18px;
                font-weight: 600;
                color: var(--text-primary, #f8fafc);
                margin-bottom: 4px;
            }
            
            .modal-subtitle {
                font-size: 13px;
                color: var(--text-muted, #64748b);
            }
            
            .modal-body {
                padding: 24px;
                font-size: 14px;
                line-height: 1.6;
                color: var(--text-secondary, #94a3b8);
            }
            
            .modal-footer {
                padding: 20px 24px;
                border-top: 1px solid var(--border, rgba(255, 255, 255, 0.06));
                display: flex;
                gap: 12px;
                justify-content: flex-end;
            }
            
            .modal-btn {
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                font-family: inherit;
            }
            
            .modal-btn-cancel {
                background: var(--bg-tertiary, #1a1a1a);
                color: var(--text-secondary, #94a3b8);
                border: 1px solid var(--border, rgba(255, 255, 255, 0.06));
            }
            
            .modal-btn-cancel:hover {
                background: var(--bg-hover, #1f1f1f);
                color: var(--text-primary, #f8fafc);
            }
            
            .modal-btn-primary {
                background: var(--gradient-purple, linear-gradient(135deg, #1e40af 0%, #2563eb 100%));
                color: white;
            }
            
            .modal-btn-primary:hover {
                transform: translateY(-1px);
                box-shadow: 0 8px 16px rgba(37, 99, 235, 0.3);
            }
            
            .modal-btn-danger {
                background: var(--gradient-red, linear-gradient(135deg, #ef4444 0%, #dc2626 100%));
                color: white;
            }
            
            .modal-btn-danger:hover {
                transform: translateY(-1px);
                box-shadow: 0 8px 16px rgba(239, 68, 68, 0.3);
            }
            
            .modal-btn:active {
                transform: translateY(0);
            }
            
            /* Input field for prompt */
            .modal-input {
                width: 100%;
                padding: 12px;
                background: var(--bg-tertiary, #1a1a1a);
                border: 1px solid var(--border, rgba(255, 255, 255, 0.1));
                border-radius: 8px;
                color: var(--text-primary, #f8fafc);
                font-size: 14px;
                font-family: inherit;
                margin-top: 12px;
            }
            
            .modal-input:focus {
                outline: none;
                border-color: var(--accent, #2563eb);
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            }
            
            /* Mobile */
            @media (max-width: 768px) {
                .modal-dialog {
                    max-width: 100%;
                    margin: 20px;
                }
                
                .modal-footer {
                    flex-direction: column;
                }
                
                .modal-btn {
                    width: 100%;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    createModal({ type = 'info', title, message, buttons = [] }) {
        // Remove existing modal
        this.close();
        
        // Icon mapping
        const icons = {
            info: 'ℹ️',
            success: '✓',
            warning: '⚠️',
            danger: '✕',
            question: '?'
        };
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        
        // Create dialog
        const dialog = document.createElement('div');
        dialog.className = 'modal-dialog';
        
        // Header
        const header = document.createElement('div');
        header.className = 'modal-header';
        header.innerHTML = `
            <div class="modal-icon ${type}">
                ${icons[type] || icons.info}
            </div>
            <div class="modal-title-group">
                <div class="modal-title">${title}</div>
            </div>
        `;
        
        // Body
        const body = document.createElement('div');
        body.className = 'modal-body';
        body.innerHTML = message;
        
        // Footer
        const footer = document.createElement('div');
        footer.className = 'modal-footer';
        
        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.className = `modal-btn ${btn.className || ''}`;
            button.textContent = btn.text;
            button.onclick = () => {
                this.close();
                if (btn.onClick) btn.onClick();
            };
            footer.appendChild(button);
        });
        
        dialog.appendChild(header);
        dialog.appendChild(body);
        dialog.appendChild(footer);
        overlay.appendChild(dialog);
        
        // Close on overlay click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.close();
                // Call cancel callback if exists
                const cancelBtn = buttons.find(b => b.isCancel);
                if (cancelBtn?.onClick) cancelBtn.onClick();
            }
        });
        
        document.body.appendChild(overlay);
        this.activeModal = overlay;
        
        return overlay;
    }
    
    close() {
        if (this.activeModal) {
            this.activeModal.style.animation = 'modalFadeIn 0.15s ease reverse';
            setTimeout(() => {
                if (this.activeModal && this.activeModal.parentNode) {
                    this.activeModal.parentNode.removeChild(this.activeModal);
                }
                this.activeModal = null;
            }, 150);
        }
    }
    
    alert(message, title = 'Уведомление') {
        return new Promise((resolve) => {
            this.createModal({
                type: 'info',
                title,
                message,
                buttons: [
                    {
                        text: 'OK',
                        className: 'modal-btn-primary',
                        onClick: resolve
                    }
                ]
            });
        });
    }
    
    confirm(message, title = 'Подтверждение', options = {}) {
        return new Promise((resolve) => {
            this.createModal({
                type: options.type || 'warning',
                title,
                message,
                buttons: [
                    {
                        text: options.cancelText || 'Отмена',
                        className: 'modal-btn-cancel',
                        isCancel: true,
                        onClick: () => resolve(false)
                    },
                    {
                        text: options.confirmText || 'Подтвердить',
                        className: options.danger ? 'modal-btn-danger' : 'modal-btn-primary',
                        onClick: () => resolve(true)
                    }
                ]
            });
        });
    }
    
    prompt(message, title = 'Введите значение', defaultValue = '') {
        return new Promise((resolve) => {
            const modal = this.createModal({
                type: 'info',
                title,
                message: message + '<input type="text" class="modal-input" value="' + defaultValue + '" autofocus>',
                buttons: [
                    {
                        text: 'Отмена',
                        className: 'modal-btn-cancel',
                        onClick: () => resolve(null)
                    },
                    {
                        text: 'OK',
                        className: 'modal-btn-primary',
                        onClick: () => {
                            const input = modal.querySelector('.modal-input');
                            resolve(input ? input.value : null);
                        }
                    }
                ]
            });
            
            // Focus input and submit on Enter
            setTimeout(() => {
                const input = modal.querySelector('.modal-input');
                if (input) {
                    input.focus();
                    input.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            resolve(input.value);
                            this.close();
                        }
                    });
                }
            }, 100);
        });
    }
}

// Create global instance
window.modalDialogs = new ModalDialogs();

// Override native functions
window.customAlert = window.alert;
window.customConfirm = window.confirm;
window.customPrompt = window.prompt;

// Provide beautiful alternatives
window.showAlert = (message, title) => window.modalDialogs.alert(message, title);
window.showConfirm = (message, title, options) => window.modalDialogs.confirm(message, title, options);
window.showPrompt = (message, title, defaultValue) => window.modalDialogs.prompt(message, title, defaultValue);

// Optional: Override native functions globally (uncomment if needed)
// window.alert = window.showAlert;
// window.confirm = window.showConfirm;
// window.prompt = window.showPrompt;
