//
//  NotificationsView.swift
//  EnlikoTrading
//
//  Notifications list and banner UI
//

import SwiftUI

// MARK: - Notification Banner (In-App)

struct NotificationBannerView: View {
    @ObservedObject var notificationService = PushNotificationService.shared
    
    var body: some View {
        VStack {
            if notificationService.showBanner, let notification = notificationService.currentBannerNotification {
                NotificationBannerCard(notification: notification) {
                    notificationService.dismissBanner()
                }
                .transition(.asymmetric(
                    insertion: .move(edge: .top).combined(with: .opacity),
                    removal: .move(edge: .top).combined(with: .opacity)
                ))
                .onTapGesture {
                    Task {
                        await notificationService.markAsRead(notification.id)
                    }
                    notificationService.dismissBanner()
                }
            }
            
            Spacer()
        }
        .animation(.spring(response: 0.3, dampingFraction: 0.8), value: notificationService.showBanner)
    }
}

struct NotificationBannerCard: View {
    let notification: AppNotification
    let onDismiss: () -> Void
    
    var body: some View {
        HStack(spacing: 12) {
            // Icon
            ZStack {
                Circle()
                    .fill(notification.color.opacity(0.2))
                    .frame(width: 44, height: 44)
                
                Image(systemName: notification.icon)
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(notification.color)
            }
            
            // Content
            VStack(alignment: .leading, spacing: 4) {
                Text(notification.title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white)
                    .lineLimit(1)
                
                Text(notification.message)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                    .lineLimit(2)
            }
            
            Spacer()
            
            // Dismiss button
            Button(action: onDismiss) {
                Image(systemName: "xmark")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.enlikoTextMuted)
                    .padding(8)
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.enlikoCard)
                .shadow(color: .black.opacity(0.3), radius: 20, y: 10)
        )
        .padding(.horizontal, 16)
        .padding(.top, 8)
    }
}

// MARK: - Notifications List View

struct NotificationsView: View {
    @ObservedObject var notificationService = PushNotificationService.shared
    @State private var isLoading = false
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            if isLoading {
                ProgressView()
                    .scaleEffect(1.5)
            } else if notificationService.notifications.isEmpty {
                emptyState
            } else {
                notificationList
            }
        }
        .navigationTitle("notifications".localized)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                if notificationService.unreadCount > 0 {
                    Button("mark_all_read".localized) {
                        Task {
                            await notificationService.markAllAsRead()
                        }
                    }
                    .font(.caption)
                }
            }
        }
        .task {
            isLoading = true
            await notificationService.loadNotifications()
            isLoading = false
        }
    }
    
    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "bell.slash.fill")
                .font(.system(size: 60))
                .foregroundColor(.enlikoTextMuted)
            
            Text("no_notifications".localized)
                .font(.headline)
                .foregroundColor(.enlikoTextSecondary)
            
            Text("no_notifications_desc".localized)
                .font(.caption)
                .foregroundColor(.enlikoTextMuted)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
    }
    
    private var notificationList: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(notificationService.notifications) { notification in
                    NotificationCard(notification: notification)
                        .onTapGesture {
                            if !notification.isRead {
                                Task {
                                    await notificationService.markAsRead(notification.id)
                                }
                            }
                        }
                }
            }
            .padding()
        }
        .refreshable {
            await notificationService.loadNotifications()
        }
    }
}

struct NotificationCard: View {
    let notification: AppNotification
    
    var body: some View {
        HStack(spacing: 12) {
            // Unread indicator
            Circle()
                .fill(notification.isRead ? Color.clear : Color.enlikoPrimary)
                .frame(width: 8, height: 8)
            
            // Icon
            ZStack {
                Circle()
                    .fill(notification.color.opacity(0.15))
                    .frame(width: 40, height: 40)
                
                Image(systemName: notification.icon)
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(notification.color)
            }
            
            // Content
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(notification.title)
                        .font(.subheadline.weight(.medium))
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    Text(timeAgo(notification.createdAt))
                        .font(.caption2)
                        .foregroundColor(.enlikoTextMuted)
                }
                
                Text(notification.message)
                    .font(.caption)
                    .foregroundColor(.enlikoTextSecondary)
                    .lineLimit(2)
                
                // Extra data if available
                if let symbol = notification.data?["symbol"]?.value as? String {
                    HStack(spacing: 4) {
                        Text(symbol)
                            .font(.caption2.weight(.medium))
                            .foregroundColor(.enlikoPrimary)
                        
                        if let pnl = notification.data?["pnl"]?.value as? Double {
                            Text(String(format: "%+.2f%%", pnl))
                                .font(.caption2.weight(.semibold))
                                .foregroundColor(pnl >= 0 ? .enlikoGreen : .enlikoRed)
                        }
                    }
                    .padding(.top, 2)
                }
            }
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(notification.isRead ? Color.enlikoCard : Color.enlikoCard.opacity(0.8))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(notification.isRead ? Color.clear : notification.color.opacity(0.3), lineWidth: 1)
                )
        )
    }
    
    private func timeAgo(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}

// MARK: - Notification Preferences View

struct NotificationPreferencesView: View {
    @ObservedObject var notificationService = PushNotificationService.shared
    @State private var isLoading = false
    @State private var showPermissionAlert = false
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 20) {
                    // Permission status
                    permissionCard
                    
                    // Categories
                    categoriesCard
                    
                    // Specific notifications
                    specificNotificationsCard
                    
                    // Sound & Vibration
                    soundCard
                }
                .padding()
            }
        }
        .navigationTitle("notification_preferences".localized)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            isLoading = true
            await notificationService.loadPreferences()
            await notificationService.checkAuthorizationStatus()
            isLoading = false
        }
        .onChange(of: notificationService.preferences) { _, _ in
            Task {
                await notificationService.savePreferences()
            }
        }
        .alert("enable_notifications".localized, isPresented: $showPermissionAlert) {
            Button("settings".localized) {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            }
            Button("cancel".localized, role: .cancel) {}
        } message: {
            Text("enable_notifications_desc".localized)
        }
    }
    
    private var permissionCard: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("push_notifications".localized)
                    .font(.headline)
                
                Text(notificationService.isAuthorized ? "enabled".localized : "disabled".localized)
                    .font(.caption)
                    .foregroundColor(notificationService.isAuthorized ? .enlikoGreen : .enlikoRed)
            }
            
            Spacer()
            
            if !notificationService.isAuthorized {
                Button("enable".localized) {
                    Task {
                        let granted = await notificationService.requestPermission()
                        if !granted {
                            showPermissionAlert = true
                        }
                    }
                }
                .buttonStyle(.bordered)
                .tint(.enlikoPrimary)
            } else {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundColor(.enlikoGreen)
                    .font(.title2)
            }
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
    
    private var categoriesCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("notification_categories".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            Toggle("notification_trades".localized, isOn: $notificationService.preferences.tradesEnabled)
                .tint(.enlikoPrimary)
            
            Toggle("notification_signals".localized, isOn: $notificationService.preferences.signalsEnabled)
                .tint(.enlikoPrimary)
            
            Toggle("notification_price_alerts".localized, isOn: $notificationService.preferences.priceAlertsEnabled)
                .tint(.enlikoPrimary)
            
            Toggle("notification_daily_summary".localized, isOn: $notificationService.preferences.dailyReportEnabled)
                .tint(.enlikoPrimary)
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
    
    private var specificNotificationsCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("specific_notifications".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            Toggle("trade_opened".localized, isOn: $notificationService.preferences.tradeOpened)
                .tint(.enlikoPrimary)
            
            Toggle("trade_closed".localized, isOn: $notificationService.preferences.tradeClosed)
                .tint(.enlikoPrimary)
            
            Toggle("break_even".localized, isOn: $notificationService.preferences.breakEven)
                .tint(.enlikoPrimary)
            
            Toggle("partial_tp".localized, isOn: $notificationService.preferences.partialTp)
                .tint(.enlikoPrimary)
            
            Toggle("margin_warning".localized, isOn: $notificationService.preferences.marginWarning)
                .tint(.enlikoPrimary)
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
    
    private var soundCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("sound_vibration".localized)
                .font(.headline)
                .foregroundColor(.white)
            
            Toggle("notification_sound".localized, isOn: $notificationService.preferences.soundEnabled)
                .tint(.enlikoPrimary)
            
            Toggle("notification_vibration".localized, isOn: $notificationService.preferences.vibrationEnabled)
                .tint(.enlikoPrimary)
        }
        .padding()
        .background(Color.enlikoCard)
        .cornerRadius(16)
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        NotificationsView()
    }
}
