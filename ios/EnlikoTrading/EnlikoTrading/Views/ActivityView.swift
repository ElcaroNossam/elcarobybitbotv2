//
//  ActivityView.swift
//  EnlikoTrading
//
//  Cross-platform activity sync view with localization
//

import SwiftUI

struct ActivityView: View {
    @ObservedObject private var activity = ActivityService.shared
    @ObservedObject var localization = LocalizationManager.shared
    @State private var selectedSource: String?
    @State private var selectedCategory: String?
    
    let sources = ["ios", "webapp", "telegram", "api"]
    let categories = ["settings", "trading", "auth", "exchange"]
    
    var body: some View {
        VStack(spacing: 0) {
            // Filters
            VStack(spacing: 8) {
                // Source Filter
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        FilterPill(title: "All Sources", isSelected: selectedSource == nil) {
                            selectedSource = nil
                            Task { await activity.fetchHistory(source: nil, category: selectedCategory) }
                        }
                        ForEach(sources, id: \.self) { source in
                            FilterPill(
                                title: sourceLabel(source),
                                isSelected: selectedSource == source
                            ) {
                                selectedSource = source
                                Task { await activity.fetchHistory(source: source, category: selectedCategory) }
                            }
                        }
                    }
                    .padding(.horizontal)
                }
                
                // Category Filter
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        FilterPill(title: "All Types", isSelected: selectedCategory == nil) {
                            selectedCategory = nil
                            Task { await activity.fetchHistory(source: selectedSource, category: nil) }
                        }
                        ForEach(categories, id: \.self) { category in
                            FilterPill(
                                title: category.capitalized,
                                isSelected: selectedCategory == category
                            ) {
                                selectedCategory = category
                                Task { await activity.fetchHistory(source: selectedSource, category: category) }
                            }
                        }
                    }
                    .padding(.horizontal)
                }
            }
            .padding(.vertical, 8)
            .background(Color(.systemBackground))
            
            // Stats Summary
            if let stats = activity.stats {
                ActivityStatsBar(stats: stats)
            }
            
            // Activity List
            if activity.isLoading && activity.activities.isEmpty {
                Spacer()
                ProgressView()
                Spacer()
            } else if activity.activities.isEmpty {
                Spacer()
                VStack(spacing: 12) {
                    Image(systemName: "clock.arrow.circlepath")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)
                    Text("activity_title".localized)
                        .font(.headline)
                    Text("activity_no_recent".localized)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                Spacer()
            } else {
                List(activity.activities) { item in
                    ActivityRow(item: item)
                }
                .listStyle(PlainListStyle())
            }
        }
        .navigationTitle("activity_title".localized)
        .navigationBarTitleDisplayMode(.inline)
        .withRTLSupport()
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    Task { await activity.triggerSync() }
                } label: {
                    Image(systemName: "arrow.triangle.2.circlepath")
                }
            }
        }
        .refreshable {
            await activity.refreshAll()
            await activity.fetchHistory(source: selectedSource, category: selectedCategory)
        }
        .task {
            await activity.refreshAll()
        }
    }
    
    private func sourceLabel(_ source: String) -> String {
        switch source {
        case "ios": return "📱 iOS"
        case "webapp": return "🌐 Web"
        case "telegram": return "💬 Telegram"
        case "api": return "🔌 API"
        default: return source.capitalized
        }
    }
}

// MARK: - Filter Pill
struct FilterPill: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption)
                .fontWeight(isSelected ? .semibold : .regular)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? Color.accentColor : Color(.systemGray5))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(16)
        }
    }
}

// MARK: - Activity Stats Bar
struct ActivityStatsBar: View {
    let stats: ActivityStats
    
    var body: some View {
        HStack(spacing: 16) {
            VStack {
                Text("\(stats.totalActivities)")
                    .font(.headline)
                Text("common_total".localized)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            Divider()
                .frame(height: 30)
            
            VStack {
                Text("\(stats.last24hCount)")
                    .font(.headline)
                Text("24h")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            Divider()
                .frame(height: 30)
            
            // Source breakdown
            HStack(spacing: 8) {
                ForEach(Array(stats.bySource.keys.sorted()), id: \.self) { source in
                    if let count = stats.bySource[source], count > 0 {
                        VStack {
                            Text("\(count)")
                                .font(.caption)
                                .fontWeight(.medium)
                            Text(sourceIcon(source))
                                .font(.caption2)
                        }
                    }
                }
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color(.secondarySystemBackground))
    }
    
    private func sourceIcon(_ source: String) -> String {
        switch source {
        case "ios": return "📱"
        case "webapp": return "🌐"
        case "telegram": return "💬"
        case "api": return "🔌"
        default: return "❓"
        }
    }
}

// MARK: - Activity Row
struct ActivityRow: View {
    let item: ActivityItem
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(item.icon)
                Text(item.sourceIcon)
                
                Text(formatActionType(item.actionType))
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Spacer()
                
                Text(formatDate(item.createdAt))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            // Details
            HStack {
                if let entityType = item.entityType {
                    Text(entityType)
                        .font(.caption)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color(.systemGray5))
                        .cornerRadius(4)
                }
                
                Text(item.actionCategory)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            // Value Change
            if let oldValue = item.oldValue, let newValue = item.newValue {
                HStack(spacing: 4) {
                    Text(truncateValue(oldValue))
                        .font(.caption)
                        .foregroundColor(.red)
                        .strikethrough()
                    
                    Image(systemName: "arrow.right")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    
                    Text(truncateValue(newValue))
                        .font(.caption)
                        .foregroundColor(.green)
                }
            }
        }
        .padding(.vertical, 4)
    }
    
    private func formatActionType(_ type: String) -> String {
        type.replacingOccurrences(of: "_", with: " ").capitalized
    }
    
    private func formatDate(_ dateString: String) -> String {
        // Simple date formatting
        if dateString.contains("T") {
            let parts = dateString.components(separatedBy: "T")
            if parts.count > 1 {
                let timeParts = parts[1].components(separatedBy: ":")
                if timeParts.count >= 2 {
                    return "\(timeParts[0]):\(timeParts[1])"
                }
            }
        }
        return dateString
    }
    
    private func truncateValue(_ value: String) -> String {
        if value.count > 20 {
            return String(value.prefix(17)) + "..."
        }
        return value
    }
}

#Preview {
    NavigationView {
        ActivityView()
    }
}
