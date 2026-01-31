//
//  DebugView.swift
//  EnlikoTrading
//
//  Debug console to view logs in-app for troubleshooting
//

import SwiftUI
import Combine

struct DebugView: View {
    @State private var logs: [LogEntry] = []
    @State private var selectedLevel: LogLevel? = nil
    @State private var selectedCategory: LogCategory? = nil
    @State private var autoRefresh = true
    @State private var showingExport = false
    @State private var exportText = ""
    
    private let logger = AppLogger.shared
    private let timer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()
    
    var filteredLogs: [LogEntry] {
        var result = logs
        if let level = selectedLevel {
            result = result.filter { $0.level >= level }
        }
        if let category = selectedCategory {
            result = result.filter { $0.category == category }
        }
        return result
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Filters
                filterBar
                
                Divider()
                
                // Logs list
                if filteredLogs.isEmpty {
                    emptyState
                } else {
                    logsList
                }
            }
            .navigationTitle("Debug Console")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Clear") {
                        logger.clearHistory()
                        refreshLogs()
                    }
                    .foregroundColor(.red)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button("Export Logs") {
                            exportText = logger.exportLogs()
                            showingExport = true
                        }
                        Button("Send to Server") {
                            logger.sendLogsToServer()
                        }
                        Toggle("Auto Refresh", isOn: $autoRefresh)
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
            .onAppear { refreshLogs() }
            .onReceive(timer) { _ in
                if autoRefresh {
                    refreshLogs()
                }
            }
            .sheet(isPresented: $showingExport) {
                ExportLogsView(logs: exportText)
            }
        }
    }
    
    // MARK: - Filter Bar
    
    private var filterBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                // Level filter
                Menu {
                    Button("All Levels") { selectedLevel = nil }
                    ForEach([LogLevel.debug, .info, .warning, .error, .critical], id: \.self) { level in
                        Button(level.prefix) { selectedLevel = level }
                    }
                } label: {
                    Label(selectedLevel?.prefix ?? "All Levels", systemImage: "line.3.horizontal.decrease.circle")
                        .font(.caption)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.secondary.opacity(0.1))
                        .cornerRadius(8)
                }
                
                // Category filter
                Menu {
                    Button("All Categories") { selectedCategory = nil }
                    ForEach(LogCategory.allCases, id: \.self) { category in
                        Button("\(category.emoji) \(category.rawValue)") { selectedCategory = category }
                    }
                } label: {
                    Label(selectedCategory?.rawValue ?? "All Categories", systemImage: "folder")
                        .font(.caption)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.secondary.opacity(0.1))
                        .cornerRadius(8)
                }
                
                Spacer()
                
                Text("\(filteredLogs.count) logs")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
        }
    }
    
    // MARK: - Logs List
    
    private var logsList: some View {
        ScrollViewReader { proxy in
            List(filteredLogs.reversed()) { log in
                LogEntryRow(entry: log)
                    .listRowInsets(EdgeInsets(top: 4, leading: 8, bottom: 4, trailing: 8))
            }
            .listStyle(.plain)
        }
    }
    
    // MARK: - Empty State
    
    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 48))
                .foregroundColor(.secondary)
            Text("No logs found")
                .font(.headline)
            Text("Logs will appear here as they are generated")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    // MARK: - Helpers
    
    private func refreshLogs() {
        logs = logger.getRecentLogs(count: 500)
    }
}

// MARK: - Log Entry Row

struct LogEntryRow: View {
    let entry: LogEntry
    
    private var levelColor: Color {
        switch entry.level {
        case .debug: return .secondary
        case .info: return .blue
        case .warning: return .orange
        case .error: return .red
        case .critical: return .purple
        }
    }
    
    private var formattedTime: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss.SSS"
        return formatter.string(from: entry.timestamp)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            // Header row
            HStack {
                Text(entry.level.prefix)
                    .font(.caption2)
                    .fontWeight(.bold)
                    .foregroundColor(levelColor)
                
                Text("\(entry.category.emoji) \(entry.category.rawValue)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Text(formattedTime)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            // Message
            Text(entry.message)
                .font(.system(.caption, design: .monospaced))
                .foregroundColor(.primary)
            
            // Location
            Text("\(entry.file):\(entry.line)")
                .font(.caption2)
                .foregroundColor(.secondary.opacity(0.7))
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Export Logs View

struct ExportLogsView: View {
    let logs: String
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                Text(logs)
                    .font(.system(.caption, design: .monospaced))
                    .padding()
            }
            .navigationTitle("Exported Logs")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Close") { dismiss() }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: copyToClipboard) {
                        Image(systemName: "doc.on.doc")
                    }
                }
            }
        }
    }
    
    private func copyToClipboard() {
        UIPasteboard.general.string = logs
    }
}

#Preview {
    DebugView()
}
