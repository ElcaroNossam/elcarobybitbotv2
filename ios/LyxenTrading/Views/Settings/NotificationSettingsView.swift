//
//  NotificationSettingsView.swift
//  LyxenTrading
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
                            .foregroundColor(.lyxenPrimary)
                        VStack(alignment: .leading) {
                            Text("notification_trades".localized)
                                .foregroundColor(.lyxenText)
                            Text("notification_trades_desc".localized)
                                .font(.caption)
                                .foregroundColor(.lyxenTextSecondary)
                        }
                    }
                }
                .tint(.lyxenPrimary)
                
                Toggle(isOn: $signalsEnabled) {
                    HStack {
                        Image(systemName: "bell.badge.fill")
                            .foregroundColor(.lyxenSecondary)
                        VStack(alignment: .leading) {
                            Text("notification_signals".localized)
                                .foregroundColor(.lyxenText)
                            Text("notification_signals_desc".localized)
                                .font(.caption)
                                .foregroundColor(.lyxenTextSecondary)
                        }
                    }
                }
                .tint(.lyxenPrimary)
                
                Toggle(isOn: $priceAlertsEnabled) {
                    HStack {
                        Image(systemName: "chart.line.uptrend.xyaxis")
                            .foregroundColor(.lyxenAccent)
                        VStack(alignment: .leading) {
                            Text("notification_price_alerts".localized)
                                .foregroundColor(.lyxenText)
                            Text("notification_price_alerts_desc".localized)
                                .font(.caption)
                                .foregroundColor(.lyxenTextSecondary)
                        }
                    }
                }
                .tint(.lyxenPrimary)
                
                Toggle(isOn: $dailySummaryEnabled) {
                    HStack {
                        Image(systemName: "calendar")
                            .foregroundColor(.lyxenGreen)
                        VStack(alignment: .leading) {
                            Text("notification_daily_summary".localized)
                                .foregroundColor(.lyxenText)
                            Text("notification_daily_summary_desc".localized)
                                .font(.caption)
                                .foregroundColor(.lyxenTextSecondary)
                        }
                    }
                }
                .tint(.lyxenPrimary)
            } header: {
                Text("notification_categories".localized)
                    .foregroundColor(.lyxenTextSecondary)
            }
            .listRowBackground(Color.lyxenCard)
            
            // MARK: - Notification Preferences
            Section {
                Toggle(isOn: $soundEnabled) {
                    HStack {
                        Image(systemName: "speaker.wave.2.fill")
                            .foregroundColor(.lyxenText)
                        Text("notification_sound".localized)
                            .foregroundColor(.lyxenText)
                    }
                }
                .tint(.lyxenPrimary)
                
                Toggle(isOn: $vibrationEnabled) {
                    HStack {
                        Image(systemName: "iphone.radiowaves.left.and.right")
                            .foregroundColor(.lyxenText)
                        Text("notification_vibration".localized)
                            .foregroundColor(.lyxenText)
                    }
                }
                .tint(.lyxenPrimary)
            } header: {
                Text("notification_preferences".localized)
                    .foregroundColor(.lyxenTextSecondary)
            }
            .listRowBackground(Color.lyxenCard)
        }
        .listStyle(.insetGrouped)
        .scrollContentBackground(.hidden)
        .background(Color.lyxenBackground)
        .navigationTitle("settings_notifications".localized)
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    NavigationStack {
        NotificationSettingsView()
    }
}
