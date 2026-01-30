/**
 * Enliko Push Notifications WebSocket Client
 * ==========================================
 * Connects to /api/notifications/ws/{token} for real-time notifications
 * Uses ToastNotifications for display
 */

class PushNotificationClient {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.isConnected = false;
        this.unreadCount = 0;
        this.onNotification = null; // Callback for notification received
        this.onUnreadCountChange = null; // Callback for unread count change
    }

    /**
     * Connect to WebSocket for push notifications
     */
    connect() {
        const token = Enliko?.getAuthToken?.() || localStorage.getItem('auth_token');
        if (!token) {
            console.log('No auth token, skipping push notification WebSocket');
            return;
        }

        // Determine WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/notifications/ws/${token}`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('🔔 Push notification WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                
                // Update UI to show connected state
                this.updateConnectionIndicator(true);
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (e) {
                    console.error('Failed to parse notification message:', e);
                }
            };

            this.ws.onclose = (event) => {
                console.log('Push notification WebSocket closed:', event.code);
                this.isConnected = false;
                this.updateConnectionIndicator(false);
                
                // Attempt reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    setTimeout(() => {
                        this.reconnectAttempts++;
                        console.log(`Reconnecting... attempt ${this.reconnectAttempts}`);
                        this.connect();
                    }, this.reconnectDelay * this.reconnectAttempts);
                }
            };

            this.ws.onerror = (error) => {
                console.error('Push notification WebSocket error:', error);
            };

        } catch (e) {
            console.error('Failed to create WebSocket:', e);
        }
    }

    /**
     * Handle incoming message
     */
    handleMessage(data) {
        if (data.type === 'ping') {
            // Respond to ping with pong
            this.send({ type: 'pong' });
            return;
        }

        if (data.type === 'notification') {
            const notification = data.payload;
            this.showNotification(notification);
            
            // Call callback if set
            if (this.onNotification) {
                this.onNotification(notification);
            }
            
            // Update unread count
            this.unreadCount++;
            this.updateUnreadBadge();
            
            if (this.onUnreadCountChange) {
                this.onUnreadCountChange(this.unreadCount);
            }
        }
    }

    /**
     * Show notification as toast
     */
    showNotification(notification) {
        const { type, title, message, data } = notification;

        // Determine toast type based on notification type
        let toastType = 'info';
        if (type === 'trade_closed') {
            toastType = data?.pnl >= 0 ? 'success' : 'error';
        } else if (type === 'trade_opened') {
            toastType = 'success';
        } else if (type === 'break_even_triggered') {
            toastType = 'info';
        } else if (type === 'partial_tp_triggered') {
            toastType = 'success';
        } else if (type === 'signal_new') {
            toastType = data?.side?.toUpperCase() === 'LONG' ? 'success' : 'error';
        } else if (type === 'margin_warning') {
            toastType = 'warning';
        }

        // Use Enliko toast system if available
        if (window.Enliko?.showToast) {
            window.Enliko.showToast(message, toastType, 5000);
        } else if (window.toast) {
            window.toast[toastType]?.(title, message, 5000);
        } else {
            // Fallback to console
            console.log(`📢 ${title}: ${message}`);
        }

        // Play sound if enabled
        this.playNotificationSound(type);

        // Show browser notification if page is not visible
        if (document.hidden && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.svg',
                tag: notification.id
            });
        }
    }

    /**
     * Play notification sound
     */
    playNotificationSound(type) {
        // Only play if user has enabled sounds (check localStorage)
        const soundEnabled = localStorage.getItem('notification_sound') !== 'false';
        if (!soundEnabled) return;

        try {
            // Use Web Audio API for reliable sound
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            // Different sounds for different types
            if (type === 'trade_closed' || type === 'partial_tp_triggered') {
                oscillator.frequency.value = 880; // A5
            } else if (type === 'trade_opened') {
                oscillator.frequency.value = 660; // E5
            } else {
                oscillator.frequency.value = 440; // A4
            }

            oscillator.type = 'sine';
            gainNode.gain.value = 0.1;

            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.15);
        } catch (e) {
            // Audio not supported or blocked
        }
    }

    /**
     * Send message to WebSocket
     */
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    /**
     * Disconnect WebSocket
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
    }

    /**
     * Update connection indicator in UI
     */
    updateConnectionIndicator(connected) {
        const indicator = document.getElementById('notification-connection-indicator');
        if (indicator) {
            indicator.classList.toggle('connected', connected);
            indicator.title = connected ? 'Notifications connected' : 'Notifications disconnected';
        }
    }

    /**
     * Update unread badge in UI
     */
    updateUnreadBadge() {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            badge.style.display = this.unreadCount > 0 ? 'flex' : 'none';
        }
    }

    /**
     * Reset unread count
     */
    resetUnreadCount() {
        this.unreadCount = 0;
        this.updateUnreadBadge();
        if (this.onUnreadCountChange) {
            this.onUnreadCountChange(0);
        }
    }

    /**
     * Request browser notification permission
     */
    async requestPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }
        return Notification.permission === 'granted';
    }
}

// Create global instance
window.pushNotifications = new PushNotificationClient();

// Auto-connect when page loads and user is authenticated
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('auth_token');
    if (token) {
        // Request permission first
        window.pushNotifications.requestPermission();
        // Connect to WebSocket
        window.pushNotifications.connect();
    }
});

// Disconnect on page unload
window.addEventListener('beforeunload', () => {
    window.pushNotifications.disconnect();
});
