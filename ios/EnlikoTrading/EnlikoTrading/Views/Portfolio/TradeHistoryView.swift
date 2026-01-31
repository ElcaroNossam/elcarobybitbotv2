//
//  TradeHistoryView.swift
//  EnlikoTrading
//
//  Full trade history list
//

import SwiftUI

struct TradeHistoryView: View {
    @EnvironmentObject var tradingService: TradingService
    @State private var searchText = ""
    @State private var selectedStrategy: String?
    @State private var showFilters = false
    
    var filteredTrades: [Trade] {
        var trades = tradingService.trades
        
        if !searchText.isEmpty {
            trades = trades.filter { $0.symbol.localizedCaseInsensitiveContains(searchText) }
        }
        
        if let strategy = selectedStrategy {
            trades = trades.filter { $0.strategy == strategy }
        }
        
        return trades
    }
    
    var strategies: [String] {
        Array(Set(tradingService.trades.compactMap { $0.strategy })).sorted()
    }
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Filters
                if showFilters {
                    filtersSection
                }
                
                // Trade List
                if filteredTrades.isEmpty {
                    emptyState
                } else {
                    tradesList
                }
            }
        }
        .navigationTitle("Trade History")
        .navigationBarTitleDisplayMode(.inline)
        .searchable(text: $searchText, prompt: "Search symbol...")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button(action: { showFilters.toggle() }) {
                    Image(systemName: "line.3.horizontal.decrease.circle")
                        .foregroundColor(showFilters ? .enlikoPrimary : .enlikoTextSecondary)
                }
            }
        }
        .refreshable {
            await tradingService.fetchTrades()
        }
    }
    
    // MARK: - Filters Section
    private var filtersSection: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                // All filter
                TradeFilterChip(
                    title: "All",
                    isSelected: selectedStrategy == nil,
                    action: { selectedStrategy = nil }
                )
                
                // Strategy filters
                ForEach(strategies, id: \.self) { strategy in
                    TradeFilterChip(
                        title: strategy.capitalized,
                        isSelected: selectedStrategy == strategy,
                        action: { selectedStrategy = strategy }
                    )
                }
            }
            .padding(.horizontal)
            .padding(.vertical, 12)
        }
        .background(Color.enlikoSurface)
    }
    
    // MARK: - Empty State
    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 60))
                .foregroundColor(.enlikoTextMuted)
            
            Text("No trades found")
                .font(.title3.weight(.medium))
                .foregroundColor(.white)
            
            Text("Your trading history will appear here")
                .font(.subheadline)
                .foregroundColor(.enlikoTextSecondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    // MARK: - Trades List
    private var tradesList: some View {
        List {
            ForEach(filteredTrades) { trade in
                TradeDetailRow(trade: trade)
                    .listRowBackground(Color.enlikoCard)
                    .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
            }
        }
        .listStyle(.plain)
        .scrollContentBackground(.hidden)
    }
}

// MARK: - Filter Chip
struct TradeFilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption.weight(.medium))
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? Color.enlikoPrimary : Color.enlikoCard)
                .foregroundColor(isSelected ? .white : .enlikoTextSecondary)
                .cornerRadius(16)
        }
    }
}

// MARK: - Trade Detail Row
struct TradeDetailRow: View {
    let trade: Trade
    @State private var isExpanded = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Main Row
            HStack {
                // Side & Symbol
                HStack(spacing: 8) {
                    Text(trade.side.uppercased())
                        .font(.caption.weight(.bold))
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(trade.side.lowercased() == "buy" ? Color.enlikoGreen : Color.enlikoRed)
                        .foregroundColor(.white)
                        .cornerRadius(4)
                    
                    Text(trade.symbol)
                        .font(.headline)
                        .foregroundColor(.white)
                }
                
                Spacer()
                
                // PnL
                VStack(alignment: .trailing, spacing: 2) {
                    Text(trade.pnl?.formattedCurrency ?? "--")
                        .font(.headline.weight(.semibold))
                        .foregroundColor((trade.pnl ?? 0) >= 0 ? .enlikoGreen : .enlikoRed)
                    
                    if let pnlPct = trade.pnlPct {
                        Text(pnlPct.formattedPercent)
                            .font(.caption)
                            .foregroundColor(.enlikoTextSecondary)
                    }
                }
            }
            .contentShape(Rectangle())
            .onTapGesture { isExpanded.toggle() }
            
            // Expanded Details
            if isExpanded {
                VStack(spacing: 8) {
                    Divider().background(Color.enlikoCardHover)
                    
                    HStack {
                        DetailItem(label: "Entry", value: "$\(trade.entryPrice.formattedPrice)")
                        Spacer()
                        if let exit = trade.exitPrice {
                            DetailItem(label: "Exit", value: "$\(exit.formattedPrice)")
                        }
                        Spacer()
                        if let strategy = trade.strategy {
                            DetailItem(label: "Strategy", value: strategy.capitalized)
                        }
                    }
                    
                    HStack {
                        if let reason = trade.exitReason {
                            DetailItem(label: "Exit Reason", value: reason)
                        }
                        Spacer()
                        DetailItem(label: "Date", value: trade.timestamp.formattedDate)
                    }
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .animation(.easeInOut(duration: 0.2), value: isExpanded)
    }
}

struct DetailItem: View {
    let label: String
    let value: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(.caption)
                .foregroundColor(.enlikoTextMuted)
            Text(value)
                .font(.subheadline)
                .foregroundColor(.enlikoTextSecondary)
        }
    }
}

#Preview {
    NavigationStack {
        TradeHistoryView()
            .environmentObject(TradingService.shared)
    }
    .preferredColorScheme(.dark)
}
