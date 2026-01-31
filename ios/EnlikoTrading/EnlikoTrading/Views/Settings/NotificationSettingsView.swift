//
//  NotificationSettingsView.swift
//  EnlikoTrading
//
//  Notification settings - synced with Android and WebApp
//

import SwiftUI

struct NotificationSettingsView: View {
    @AppStorage("notifications_trades") private var tradesEnabled = true
    @AppStorage("notifications_signals") private var signalsEnabled = true
    @AppStorage("notifications_price_alerts") private var priceAlertsEnabled = true
    @AppStorage("notifications_daily_summary") private var dailySummaryEnabled = false
    @AppStorage("notifications_sound") private var soundEnabled = true
    @AppStorage("notifications_vibration") private var vibrationEnabled = true
    
    var body: some View {
        List {
            // MARK: - Trading Notifications
            Section {
                Toggle(isOn: $tradesEnabled) {
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
                
                Toggle(isOn: $signalsEnabled) {
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
                
                Toggle(isOn: $priceAlertsEnabled) {
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
                
                Toggle(isOn: $dailySummaryEnabled) {
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
            } header: {
                Text("notification_categories".localized)
                    .foregroundColor(.enlikoTextSecondary)
            }
            .listRowBackground(Color.enlikoCard)
            
            // MARK: - Notification Preferences
            Section {
                Toggle(isOn: $soundEnabled) {
                    HStack {
                        Image(systemName: "speaker.wave.2.fill")
                            .foregroundColor(.enlikoText)
                        Text("notification_sound".localized)
                            .foregroundColor(.enlikoText)
                    }
                }
                .tint(.enlikoPrimary)
                
                Toggle(isOn: $vibrationEnabled) {
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
    }
}

#Preview {
    NavigationStack {
        NotificationSettingsView()
    }
}
