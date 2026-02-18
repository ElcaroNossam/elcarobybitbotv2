//
//  NotificationSettingsView.swift
//  EnlikoTrading
//
//  Push notification settings with glassmorphism design
//  Synced with server via PushNotificationService
//

import SwiftUI

struct NotificationSettingsView: View {
    @ObservedObject private var pushService = PushNotificationService.shared
    @State private var isLoading = true
    @State private var permissionGranted = false
    @State private var showPermissionDeniedAlert = false
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 16) {
                    // MARK: - Header
                    notificationHeader
                    
                    // MARK: - Permission Banner
                    if !permissionGranted && !isLoading {
                        permissionBanner
                            .transition(.move(edge: .top).combined(with: .opacity))
                    }
                    
                    // MARK: - Trade Notifications
                    tradeNotificationsCard
                    
                    // MARK: - Other Notifications
                    otherNotificationsCard
                    
                    // MARK: - Preferences
                    preferencesCard
                    
                    Spacer(minLength: 32)
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
            }
            
            if isLoading {
                ProgressView()
                    .tint(.enlikoPrimary)
                    .scaleEffect(1.2)
            }
        }
        .navigationTitle("settings_notifications".localized)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await checkPermission()
            await pushService.loadPreferences()
            withAnimation(.easeOut(duration: 0.3)) {
                isLoading = false
            }
        }
        .onChange(of: pushService.preferences) { _, _ in
            Task { await pushService.savePreferences() }
        }
        .alert("notification_enable_push".localized, isPresented: $showPermissionDeniedAlert) {
            Button("notification_open_settings".localized) {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            }
            Button("common_cancel".localized, role: .cancel) {}
        } message: {
            Text("notification_denied_desc".localized)
        }
    }
    
    // MARK: - Header
    private var notificationHeader: some View {
        VStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.enlikoPrimary.opacity(0.3), Color.enlikoAccent.opacity(0.15)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 72, height: 72)
                
                Image(systemName: "bell.badge.fill")
                    .font(.system(size: 30))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.enlikoPrimary, .enlikoAccent],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
            }
            
            Text("settings_notifications".localized)
                .font(.title3.bold())
                .foregroundColor(.enlikoText)
            
            Text("notification_header_desc".localized)
                .font(.subheadline)
                .foregroundColor(.enlikoTextSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 24)
        }
        .padding(.vertical, 8)
    }
    
    // MARK: - Permission Banner
    private var permissionBanner: some View {
        Button {
            Task {
                let center = UNUserNotificationCenter.current()
                let settings = await center.notificationSettings()
                if settings.authorizationStatus == .denied {
                    showPermissionDeniedAlert = true
                } else {
                    await pushService.requestPermission()
                    await checkPermission()
                }
            }
        } label: {
            HStack(spacing: 14) {
                ZStack {
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color.enlikoOrange.opacity(0.15))
                        .frame(width: 40, height: 40)
                    Image(systemName: "bell.slash.fill")
                        .font(.system(size: 18))
                        .foregroundColor(.enlikoOrange)
                }
                
                VStack(alignment: .leading, spacing: 3) {
                    Text("notification_enable_push".localized)
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.enlikoText)
                    Text("notification_enable_push_desc".localized)
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                }
                
                Spacer()
                
                Image(systemName: "arrow.right.circle.fill")
                    .font(.title3)
                    .foregroundColor(.enlikoOrange)
            }
            .padding(14)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.enlikoGlass)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.enlikoOrange.opacity(0.3), lineWidth: 1)
                    )
            )
        }
    }
    
    // MARK: - Trade Notifications Card
    private var tradeNotificationsCard: some View {
        VStack(spacing: 0) {
            // Section header
            sectionHeader(
                icon: "arrow.left.arrow.right.circle.fill",
                title: "notification_trades".localized,
                color: .enlikoPrimary
            )
            
            Divider().background(Color.enlikoBorder)
            
            // Master toggle
            notificationToggle(
                icon: "arrow.triangle.swap",
                iconColor: .enlikoPrimary,
                title: "notification_trades".localized,
                subtitle: "notification_trades_desc".localized,
                isOn: $pushService.preferences.tradesEnabled
            )
            
            // Sub-toggles (animated)
            if pushService.preferences.tradesEnabled {
                Group {
                    Divider().background(Color.enlikoBorder).padding(.leading, 56)
                    
                    subToggle(
                        icon: "target",
                        iconColor: .enlikoGreen,
                        title: "notification_tp_sl".localized,
                        subtitle: "notification_tp_sl_desc".localized,
                        isOn: $pushService.preferences.tradeClosed
                    )
                    
                    Divider().background(Color.enlikoBorder).padding(.leading, 56)
                    
                    subToggle(
                        icon: "plus.circle.fill",
                        iconColor: .enlikoBlue,
                        title: "notification_trade_opened".localized,
                        subtitle: "notification_trade_opened_desc".localized,
                        isOn: $pushService.preferences.tradeOpened
                    )
                    
                    Divider().background(Color.enlikoBorder).padding(.leading, 56)
                    
                    subToggle(
                        icon: "equal.circle.fill",
                        iconColor: .enlikoYellow,
                        title: "notification_break_even".localized,
                        subtitle: "notification_break_even_desc".localized,
                        isOn: $pushService.preferences.breakEven
                    )
                    
                    Divider().background(Color.enlikoBorder).padding(.leading, 56)
                    
                    subToggle(
                        icon: "chart.pie.fill",
                        iconColor: .enlikoAccent,
                        title: "notification_partial_tp".localized,
                        subtitle: "notification_partial_tp_desc".localized,
                        isOn: $pushService.preferences.partialTp
                    )
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
            
            Divider().background(Color.enlikoBorder)
            
            // Margin Warning (always visible, red accent)
            notificationToggle(
                icon: "exclamationmark.triangle.fill",
                iconColor: .enlikoRed,
                title: "notification_margin_warning".localized,
                subtitle: "notification_margin_warning_desc".localized,
                isOn: $pushService.preferences.marginWarning
            )
        }
        .glassCard()
    }
    
    // MARK: - Other Notifications Card
    private var otherNotificationsCard: some View {
        VStack(spacing: 0) {
            sectionHeader(
                icon: "sparkles",
                title: "notification_other".localized,
                color: .enlikoSecondary
            )
            
            Divider().background(Color.enlikoBorder)
            
            notificationToggle(
                icon: "bell.badge.fill",
                iconColor: .enlikoSecondary,
                title: "notification_signals".localized,
                subtitle: "notification_signals_desc".localized,
                isOn: $pushService.preferences.signalsEnabled
            )
            
            Divider().background(Color.enlikoBorder)
            
            notificationToggle(
                icon: "chart.line.uptrend.xyaxis",
                iconColor: .enlikoAccent,
                title: "notification_price_alerts".localized,
                subtitle: "notification_price_alerts_desc".localized,
                isOn: $pushService.preferences.priceAlertsEnabled
            )
            
            Divider().background(Color.enlikoBorder)
            
            notificationToggle(
                icon: "doc.text.fill",
                iconColor: .enlikoGreen,
                title: "notification_daily_summary".localized,
                subtitle: "notification_daily_summary_desc".localized,
                isOn: $pushService.preferences.dailyReportEnabled
            )
        }
        .glassCard()
    }
    
    // MARK: - Preferences Card
    private var preferencesCard: some View {
        VStack(spacing: 0) {
            sectionHeader(
                icon: "gearshape.fill",
                title: "notification_preferences".localized,
                color: .enlikoTextSecondary
            )
            
            Divider().background(Color.enlikoBorder)
            
            notificationToggle(
                icon: "speaker.wave.2.fill",
                iconColor: .enlikoBlue,
                title: "notification_sound".localized,
                subtitle: nil,
                isOn: $pushService.preferences.soundEnabled
            )
            
            Divider().background(Color.enlikoBorder)
            
            notificationToggle(
                icon: "iphone.radiowaves.left.and.right",
                iconColor: .enlikoPurple,
                title: "notification_vibration".localized,
                subtitle: nil,
                isOn: $pushService.preferences.vibrationEnabled
            )
        }
        .glassCard()
    }
    
    // MARK: - Reusable Components
    
    private func sectionHeader(icon: String, title: String, color: Color) -> some View {
        HStack(spacing: 10) {
            Image(systemName: icon)
                .font(.subheadline.weight(.semibold))
                .foregroundColor(color)
            Text(title)
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.enlikoTextSecondary)
            Spacer()
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
    }
    
    private func notificationToggle(
        icon: String,
        iconColor: Color,
        title: String,
        subtitle: String?,
        isOn: Binding<Bool>
    ) -> some View {
        Toggle(isOn: isOn) {
            HStack(spacing: 14) {
                ZStack {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(iconColor.opacity(0.15))
                        .frame(width: 36, height: 36)
                    Image(systemName: icon)
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(iconColor)
                }
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.subheadline.weight(.medium))
                        .foregroundColor(.enlikoText)
                    if let subtitle = subtitle {
                        Text(subtitle)
                            .font(.caption)
                            .foregroundColor(.enlikoTextSecondary)
                            .lineLimit(2)
                    }
                }
            }
        }
        .tint(.enlikoPrimary)
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
    }
    
    private func subToggle(
        icon: String,
        iconColor: Color,
        title: String,
        subtitle: String,
        isOn: Binding<Bool>
    ) -> some View {
        Toggle(isOn: isOn) {
            HStack(spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 7)
                        .fill(iconColor.opacity(0.1))
                        .frame(width: 30, height: 30)
                    Image(systemName: icon)
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(iconColor)
                }
                
                VStack(alignment: .leading, spacing: 1) {
                    Text(title)
                        .font(.subheadline)
                        .foregroundColor(.enlikoText)
                    Text(subtitle)
                        .font(.caption2)
                        .foregroundColor(.enlikoTextMuted)
                        .lineLimit(2)
                }
            }
        }
        .tint(.enlikoPrimary)
        .padding(.leading, 40)
        .padding(.trailing, 16)
        .padding(.vertical, 8)
    }
    
    // MARK: - Permission Check
    private func checkPermission() async {
        let center = UNUserNotificationCenter.current()
        let settings = await center.notificationSettings()
        await MainActor.run {
            withAnimation(.easeInOut(duration: 0.3)) {
                permissionGranted = settings.authorizationStatus == .authorized
            }
        }
    }
}

// MARK: - Glass Card Modifier
private extension View {
    func glassCard() -> some View {
        self
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.enlikoGlass)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Color.enlikoGlassBorder, lineWidth: 0.5)
            )
            .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

#Preview {
    NavigationStack {
        NotificationSettingsView()
    }
}
