//
//  NotificationSettingsView.swift
//  EnlikoTrading
//
//  Notification settings - synced with server via PushNotificationService
//

import SwiftUI

struct NotificationSettingsView: View {
    @ObservedObject private var pushService = PushNotificationService.shared
    @State private var isLoading = true
    @State private var permissionGranted = false
    
    var body: some View {
        List {
            // MARK: - Push Permission Status
            if !permissionGranted {
                Section {
                    Button {
                        Task {
                            await pushService.requestPermission()
                            await checkPermission()
                        }
                    } label: {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.orange)
                            VStack(alignment: .leading) {
                                Text("notification_enable_push".localized)
                                    .foregroundColor(.enlikoText)
                                Text("notification_enable_push_desc".localized)
                                    .font(.caption)
                                    .foregroundColor(.enlikoTextSecondary)
                            }
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundColor(.enlikoTextSecondary)
                        }
                    }
                }
                .listRowBackground(Color.enlikoCard)
            }
            
            // MARK: - Trading Notifications
            Section {
                Toggle(isOn: $pushService.preferences.tradesEnabled) {
                    HStack {
                        Image(systemName: "arrow.left.arrow.right.circle.fill")
                            .foregroundColor(.enlikoPrimary)
                        VStack(alignment: .leading) {
                            Text("notification_trades".localized)
                                .foregroundColor(.enlikoText)
                            Text("notification_trades_desc".localized)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                        }
                    }
                }
                .tint(.enlikoPrimary)
                
                if pushService.preferences.tradesEnabled {
                    Toggle(isOn: $pushService.preferences.tradeClosed) {
                        HStack(spacing: 12) {
                            Rectangle().fill(Color.clear).frame(width: 20)
                            VStack(alignment: .leading) {
                                Text("notification_tp_sl".localized)
                                    .foregroundColor(.enlikoText)
                                Text("notification_tp_sl_desc".localized)
                                    .font(.caption)
                                    .foregroundColor(.enlikoTextSecondary)
                            }
                        }
                    }
                    .tint(.enlikoPrimary)
                    
                    Toggle(isOn: $pushService.preferences.tradeOpened) {
                        HStack(spacing: 12) {
                            Rectangle().fill(Color.clear).frame(width: 20)
                            VStack(alignment: .leading) {
                                Text("notification_trade_opened".localized)
                                    .foregroundColor(.enlikoText)
                                Text("notification_trade_opened_desc".localized)
                                    .font(.caption)
                                    .foregroundColor(.enlikoTextSecondary)
                            }
                        }
                    }
                    .tint(.enlikoPrimary)
                    
                    Toggle(isOn: $pushService.preferences.breakEven) {
                        HStack(spacing: 12) {
                            Rectangle().fill(Color.clear).frame(width: 20)
                            VStack(alignment: .leading) {
                                Text("notification_break_even".localized)
                                    .foregroundColor(.enlikoText)
                                Text("notification_break_even_desc".localized)
                                    .font(.caption)
                                    .foregroundColor(.enlikoTextSecondary)
                            }
                        }
                    }
                    .tint(.enlikoPrimary)
                    
                    Toggle(isOn: $pushService.preferences.partialTp) {
                        HStack(spacing: 12) {
                            Rectangle().fill(Color.clear).frame(width: 20)
                            VStack(alignment: .leading) {
                                Text("notification_partial_tp".localized)
                                    .foregroundColor(.enlikoText)
                                Text("notification_partial_tp_desc".localized)
                                    .font(.caption)
                                    .foregroundColor(.enlikoTextSecondary)
                            }
                        }
                    }
                    .tint(.enlikoPrimary)
                }
                
                Toggle(isOn: $pushService.preferences.signalsEnabled) {
                    HStack {
                        Image(systemName: "bell.badge.fill")
                            .foregroundColor(.enlikoSecondary)
                        VStack(alignment: .leading) {
                            Text("notification_signals".localized)
                                .foregroundColor(.enlikoText)
                            Text("notification_signals_desc".localized)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                        }
                    }
                }
                .tint(.enlikoPrimary)
                
                Toggle(isOn: $pushService.preferences.priceAlertsEnabled) {
                    HStack {
                        Image(systemName: "chart.line.uptrend.xyaxis")
                            .foregroundColor(.enlikoAccent)
                        VStack(alignment: .leading) {
                            Text("notification_price_alerts".localized)
                                .foregroundColor(.enlikoText)
                            Text("notification_price_alerts_desc".localized)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                        }
                    }
                }
                .tint(.enlikoPrimary)
                
                Toggle(isOn: $pushService.preferences.dailyReportEnabled) {
                    HStack {
                        Image(systemName: "calendar")
                            .foregroundColor(.enlikoGreen)
                        VStack(alignment: .leading) {
                            Text("notification_daily_summary".localized)
                                .foregroundColor(.enlikoText)
                            Text("notification_daily_summary_desc".localized)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                        }
                    }
                }
                .tint(.enlikoPrimary)
                
                Toggle(isOn: $pushService.preferences.marginWarning) {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.enlikoRed)
                        VStack(alignment: .leading) {
                            Text("notification_margin_warning".localized)
                                .foregroundColor(.enlikoText)
                            Text("notification_margin_warning_desc".localized)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                        }
                    }
                }
                .tint(.enlikoPrimary)
            } header: {
                Text("notification_categories".localized)
                    .foregroundColor(.enlikoTextSecondary)
            }
            .listRowBackground(Color.enlikoCard)
            
            // MARK: - Notification Preferences
            Section {
                Toggle(isOn: $pushService.preferences.soundEnabled) {
                    HStack {
                        Image(systemName: "speaker.wave.2.fill")
                            .foregroundColor(.enlikoText)
                        Text("notification_sound".localized)
                            .foregroundColor(.enlikoText)
                    }
                }
                .tint(.enlikoPrimary)
                
                Toggle(isOn: $pushService.preferences.vibrationEnabled) {
                    HStack {
                        Image(systemName: "iphone.radiowaves.left.and.right")
                            .foregroundColor(.enlikoText)
                        Text("notification_vibration".localized)
                            .foregroundColor(.enlikoText)
                    }
                }
                .tint(.enlikoPrimary)
            } header: {
                Text("notification_preferences".localized)
                    .foregroundColor(.enlikoTextSecondary)
            }
            .listRowBackground(Color.enlikoCard)
        }
        .listStyle(.insetGrouped)
        .scrollContentBackground(.hidden)
        .background(Color.enlikoBackground)
        .navigationTitle("settings_notifications".localized)
        .navigationBarTitleDisplayMode(.inline)
        .overlay {
            if isLoading {
                ProgressView()
            }
        }
        .task {
            await checkPermission()
            await pushService.loadPreferences()
            isLoading = false
        }
        .onChange(of: pushService.preferences) { _, _ in
            Task {
                await pushService.savePreferences()
            }
        }
    }
    
    private func checkPermission() async {
        let center = UNUserNotificationCenter.current()
        let settings = await center.notificationSettings()
        await MainActor.run {
            permissionGranted = settings.authorizationStatus == .authorized
        }
    }
}

#Preview {
    NavigationStack {
        NotificationSettingsView()
    }
}
