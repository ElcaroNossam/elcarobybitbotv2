//
//  AlertsView.swift
//  EnlikoTrading
//
//  Price Alerts Management View like Binance/Bybit
//  Features: Create, Edit, Delete price alerts with notifications
//

import SwiftUI

// MARK: - Alert Models
struct PriceAlert: Identifiable {
    let id = UUID()
    var symbol: String
    var condition: AlertCondition
    var targetPrice: Double
    var currentPrice: Double
    var isActive: Bool
    var isTriggered: Bool
    var createdAt: Date
    var triggeredAt: Date?
    var note: String
    
    enum AlertCondition: String, CaseIterable {
        case above = "Price Above"
        case below = "Price Below"
        case crossUp = "Cross Up"
        case crossDown = "Cross Down"
        case percentUp = "% Change Up"
        case percentDown = "% Change Down"
        
        var icon: String {
            switch self {
            case .above, .crossUp, .percentUp: return "arrow.up"
            case .below, .crossDown, .percentDown: return "arrow.down"
            }
        }
    }
}

struct AlertsView: View {
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var alerts: [PriceAlert] = []
    @State private var selectedTab: AlertTab = .active
    @State private var showCreateAlert = false
    @State private var alertToEdit: PriceAlert?
    @State private var showDeleteConfirm = false
    @State private var alertToDelete: PriceAlert?
    
    enum AlertTab: String, CaseIterable {
        case active = "Active"
        case triggered = "Triggered"
        case all = "All"
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Tab Selector
            tabSelector
            
            // Alerts List
            if filteredAlerts.isEmpty {
                emptyState
            } else {
                alertsList
            }
        }
        .background(Color.enlikoBackground)
        .navigationTitle("Price Alerts")
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    showCreateAlert = true
                } label: {
                    Image(systemName: "plus.circle.fill")
                        .font(.title3)
                        .foregroundColor(.enlikoPrimary)
                }
            }
        }
        .sheet(isPresented: $showCreateAlert) {
            CreateAlertSheet()
        }
        .sheet(item: $alertToEdit) { alert in
            CreateAlertSheet(editingAlert: alert)
        }
        .confirmationDialog("Delete Alert?", isPresented: $showDeleteConfirm, presenting: alertToDelete) { alert in
            Button("Delete", role: .destructive) {
                if let index = alerts.firstIndex(where: { $0.id == alert.id }) {
                    alerts.remove(at: index)
                }
            }
            Button("Cancel", role: .cancel) {}
        }
        .onAppear {
            loadMockAlerts()
        }
    }
    
    // MARK: - Tab Selector
    private var tabSelector: some View {
        HStack(spacing: 0) {
            ForEach(AlertTab.allCases, id: \.self) { tab in
                Button {
                    withAnimation { selectedTab = tab }
                } label: {
                    VStack(spacing: 6) {
                        HStack(spacing: 4) {
                            Text(tab.rawValue)
                                .font(.subheadline.bold())
                            
                            // Count badge
                            let count = countForTab(tab)
                            if count > 0 {
                                Text("\(count)")
                                    .font(.caption2.bold())
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(selectedTab == tab ? Color.enlikoPrimary : Color.secondary.opacity(0.3))
                                    .foregroundColor(.white)
                                    .cornerRadius(8)
                            }
                        }
                        .foregroundColor(selectedTab == tab ? .white : .secondary)
                        
                        Rectangle()
                            .fill(selectedTab == tab ? Color.enlikoPrimary : Color.clear)
                            .frame(height: 2)
                    }
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(.horizontal)
        .background(Color.enlikoSurface)
    }
    
    private func countForTab(_ tab: AlertTab) -> Int {
        switch tab {
        case .active: return alerts.filter { $0.isActive && !$0.isTriggered }.count
        case .triggered: return alerts.filter { $0.isTriggered }.count
        case .all: return alerts.count
        }
    }
    
    private var filteredAlerts: [PriceAlert] {
        switch selectedTab {
        case .active: return alerts.filter { $0.isActive && !$0.isTriggered }
        case .triggered: return alerts.filter { $0.isTriggered }
        case .all: return alerts
        }
    }
    
    // MARK: - Empty State
    private var emptyState: some View {
        VStack(spacing: 20) {
            Spacer()
            
            Image(systemName: "bell.slash")
                .font(.system(size: 60))
                .foregroundColor(.secondary.opacity(0.5))
            
            Text("No Price Alerts")
                .font(.title2.bold())
                .foregroundColor(.white)
            
            Text("Create alerts to get notified when\nprices reach your targets")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            
            Button {
                showCreateAlert = true
            } label: {
                Label("Create Alert", systemImage: "plus")
                    .font(.headline)
                    .padding()
                    .background(Color.enlikoPrimary)
                    .foregroundColor(.white)
                    .cornerRadius(12)
            }
            
            Spacer()
        }
    }
    
    // MARK: - Alerts List
    private var alertsList: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(filteredAlerts) { alert in
                    AlertRow(
                        alert: alert,
                        onToggle: { toggleAlert(alert) },
                        onEdit: { alertToEdit = alert },
                        onDelete: {
                            alertToDelete = alert
                            showDeleteConfirm = true
                        }
                    )
                }
            }
            .padding()
        }
    }
    
    // MARK: - Actions
    private func toggleAlert(_ alert: PriceAlert) {
        if let index = alerts.firstIndex(where: { $0.id == alert.id }) {
            alerts[index].isActive.toggle()
        }
    }
    
    private func loadMockAlerts() {
        alerts = [
            PriceAlert(
                symbol: "BTCUSDT",
                condition: .above,
                targetPrice: 100000,
                currentPrice: 98500,
                isActive: true,
                isTriggered: false,
                createdAt: Date().addingTimeInterval(-86400),
                note: "ATH breakout"
            ),
            PriceAlert(
                symbol: "ETHUSDT",
                condition: .below,
                targetPrice: 3000,
                currentPrice: 3200,
                isActive: true,
                isTriggered: false,
                createdAt: Date().addingTimeInterval(-172800),
                note: "Buy dip"
            ),
            PriceAlert(
                symbol: "SOLUSDT",
                condition: .above,
                targetPrice: 150,
                currentPrice: 180,
                isActive: false,
                isTriggered: true,
                createdAt: Date().addingTimeInterval(-604800),
                triggeredAt: Date().addingTimeInterval(-86400),
                note: "Target hit"
            ),
        ]
    }
}

// MARK: - Alert Row
struct AlertRow: View {
    let alert: PriceAlert
    let onToggle: () -> Void
    let onEdit: () -> Void
    let onDelete: () -> Void
    
    var body: some View {
        HStack(spacing: 12) {
            // Status Indicator
            Circle()
                .fill(statusColor)
                .frame(width: 10, height: 10)
            
            // Main Info
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(alert.symbol)
                        .font(.headline.bold())
                        .foregroundColor(.white)
                    
                    Image(systemName: alert.condition.icon)
                        .font(.caption)
                        .foregroundColor(conditionColor)
                    
                    Text(alert.condition.rawValue)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                HStack(spacing: 16) {
                    // Target Price
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Target")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text("$\(alert.targetPrice, specifier: "%.2f")")
                            .font(.subheadline.bold())
                            .foregroundColor(conditionColor)
                    }
                    
                    // Current Price
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Current")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text("$\(alert.currentPrice, specifier: "%.2f")")
                            .font(.subheadline)
                            .foregroundColor(.white)
                    }
                    
                    // Distance
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Distance")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Text(distanceText)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                
                if !alert.note.isEmpty {
                    Text(alert.note)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
            }
            
            Spacer()
            
            // Actions
            VStack(spacing: 8) {
                if alert.isTriggered {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(.green)
                } else {
                    Toggle("", isOn: Binding(
                        get: { alert.isActive },
                        set: { _ in onToggle() }
                    ))
                    .toggleStyle(SwitchToggleStyle(tint: .enlikoPrimary))
                    .labelsHidden()
                }
                
                Menu {
                    Button { onEdit() } label: {
                        Label("Edit", systemImage: "pencil")
                    }
                    Button(role: .destructive) { onDelete() } label: {
                        Label("Delete", systemImage: "trash")
                    }
                } label: {
                    Image(systemName: "ellipsis")
                        .font(.title3)
                        .foregroundColor(.secondary)
                        .padding(8)
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(12)
    }
    
    private var statusColor: Color {
        if alert.isTriggered { return .green }
        if alert.isActive { return .enlikoPrimary }
        return .gray
    }
    
    private var conditionColor: Color {
        switch alert.condition {
        case .above, .crossUp, .percentUp: return .green
        case .below, .crossDown, .percentDown: return .red
        }
    }
    
    private var distanceText: String {
        let diff = alert.targetPrice - alert.currentPrice
        let percent = (diff / alert.currentPrice) * 100
        let prefix = percent >= 0 ? "+" : ""
        return "\(prefix)\(String(format: "%.2f", percent))%"
    }
}

// MARK: - Create Alert Sheet
struct CreateAlertSheet: View {
    @Environment(\.dismiss) var dismiss
    
    var editingAlert: PriceAlert?
    
    @State private var symbol = "BTCUSDT"
    @State private var condition: PriceAlert.AlertCondition = .above
    @State private var targetPrice = ""
    @State private var note = ""
    @State private var enablePush = true
    @State private var enableSound = true
    @State private var repeatAlert = false
    
    @State private var showSymbolPicker = false
    
    let popularSymbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT"]
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Symbol Selector
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Symbol")
                            .font(.subheadline.bold())
                            .foregroundColor(.secondary)
                        
                        Button {
                            showSymbolPicker = true
                        } label: {
                            HStack {
                                Text(symbol)
                                    .font(.headline)
                                    .foregroundColor(.white)
                                
                                Spacer()
                                
                                Image(systemName: "chevron.right")
                                    .foregroundColor(.secondary)
                            }
                            .padding()
                            .background(Color.enlikoSurface)
                            .cornerRadius(12)
                        }
                        
                        // Quick symbols
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 8) {
                                ForEach(popularSymbols, id: \.self) { sym in
                                    Button {
                                        symbol = sym
                                    } label: {
                                        Text(sym.replacingOccurrences(of: "USDT", with: ""))
                                            .font(.caption.bold())
                                            .padding(.horizontal, 12)
                                            .padding(.vertical, 6)
                                            .background(symbol == sym ? Color.enlikoPrimary : Color.enlikoSurface)
                                            .foregroundColor(symbol == sym ? .white : .secondary)
                                            .cornerRadius(8)
                                    }
                                }
                            }
                        }
                    }
                    
                    // Condition Selector
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Condition")
                            .font(.subheadline.bold())
                            .foregroundColor(.secondary)
                        
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 8) {
                            ForEach(PriceAlert.AlertCondition.allCases, id: \.self) { cond in
                                Button {
                                    condition = cond
                                } label: {
                                    HStack {
                                        Image(systemName: cond.icon)
                                        Text(cond.rawValue)
                                            .font(.caption)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 10)
                                    .background(condition == cond ? Color.enlikoPrimary : Color.enlikoSurface)
                                    .foregroundColor(condition == cond ? .white : .secondary)
                                    .cornerRadius(8)
                                }
                            }
                        }
                    }
                    
                    // Target Price
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Target Price")
                            .font(.subheadline.bold())
                            .foregroundColor(.secondary)
                        
                        HStack {
                            Text("$")
                                .foregroundColor(.secondary)
                            
                            TextField("0.00", text: $targetPrice)
                                .keyboardType(.decimalPad)
                                .font(.title2)
                        }
                        .padding()
                        .background(Color.enlikoSurface)
                        .cornerRadius(12)
                        
                        Text("Current: $98,500.00")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    // Note
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Note (optional)")
                            .font(.subheadline.bold())
                            .foregroundColor(.secondary)
                        
                        TextField("Add a note...", text: $note)
                            .padding()
                            .background(Color.enlikoSurface)
                            .cornerRadius(12)
                    }
                    
                    // Notification Settings
                    VStack(spacing: 12) {
                        Toggle(isOn: $enablePush) {
                            HStack {
                                Image(systemName: "bell.fill")
                                    .foregroundColor(.enlikoPrimary)
                                Text("Push Notification")
                            }
                        }
                        .toggleStyle(SwitchToggleStyle(tint: .enlikoPrimary))
                        
                        Toggle(isOn: $enableSound) {
                            HStack {
                                Image(systemName: "speaker.wave.2.fill")
                                    .foregroundColor(.enlikoPrimary)
                                Text("Sound")
                            }
                        }
                        .toggleStyle(SwitchToggleStyle(tint: .enlikoPrimary))
                        
                        Toggle(isOn: $repeatAlert) {
                            HStack {
                                Image(systemName: "repeat")
                                    .foregroundColor(.enlikoPrimary)
                                Text("Repeat Alert")
                            }
                        }
                        .toggleStyle(SwitchToggleStyle(tint: .enlikoPrimary))
                    }
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                }
                .padding()
            }
            .background(Color.enlikoBackground)
            .navigationTitle(editingAlert != nil ? "Edit Alert" : "New Alert")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        // Save alert
                        dismiss()
                    }
                    .fontWeight(.bold)
                    .disabled(targetPrice.isEmpty)
                }
            }
            .sheet(isPresented: $showSymbolPicker) {
                SymbolPickerSheet(selectedSymbol: $symbol)
            }
        }
        .onAppear {
            if let alert = editingAlert {
                symbol = alert.symbol
                condition = alert.condition
                targetPrice = String(format: "%.2f", alert.targetPrice)
                note = alert.note
            }
        }
    }
}

// MARK: - Symbol Picker Sheet
struct SymbolPickerSheet: View {
    @Environment(\.dismiss) var dismiss
    @Binding var selectedSymbol: String
    
    @State private var searchText = ""
    
    let symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT", "LINKUSDT", "UNIUSDT", "ATOMUSDT", "LTCUSDT", "ETCUSDT", "XLMUSDT", "APTUSDT", "ARBUSDT", "OPUSDT", "SUIUSDT"]
    
    var filteredSymbols: [String] {
        if searchText.isEmpty {
            return symbols
        }
        return symbols.filter { $0.lowercased().contains(searchText.lowercased()) }
    }
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Search
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.secondary)
                    
                    TextField("Search symbol", text: $searchText)
                }
                .padding()
                .background(Color.enlikoSurface)
                
                // Symbols List
                ScrollView {
                    LazyVStack(spacing: 1) {
                        ForEach(filteredSymbols, id: \.self) { symbol in
                            Button {
                                selectedSymbol = symbol
                                dismiss()
                            } label: {
                                HStack {
                                    Text(symbol)
                                        .foregroundColor(.white)
                                    
                                    Spacer()
                                    
                                    if symbol == selectedSymbol {
                                        Image(systemName: "checkmark")
                                            .foregroundColor(.enlikoPrimary)
                                    }
                                }
                                .padding()
                                .background(Color.enlikoSurface)
                            }
                        }
                    }
                }
            }
            .background(Color.enlikoBackground)
            .navigationTitle("Select Symbol")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }
}

#Preview {
    NavigationStack {
        AlertsView()
            .preferredColorScheme(.dark)
    }
}
