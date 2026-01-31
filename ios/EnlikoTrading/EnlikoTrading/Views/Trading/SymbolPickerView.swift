//
//  SymbolPickerView.swift
//  EnlikoTrading
//
//  Symbol selection sheet
//

import SwiftUI

struct SymbolPickerView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var tradingService: TradingService
    @Binding var selectedSymbol: String
    @State private var searchText = ""
    
    var filteredSymbols: [SymbolInfo] {
        if searchText.isEmpty {
            return tradingService.symbols
        }
        return tradingService.symbols.filter {
            $0.symbol.localizedCaseInsensitiveContains(searchText)
        }
    }
    
    // Convenience for symbol names
    var filteredSymbolNames: [String] {
        filteredSymbols.map { $0.symbol }
    }
    
    // Popular symbols to show at top
    let popularSymbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT"]
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Popular Section
                    if searchText.isEmpty {
                        popularSection
                    }
                    
                    // All Symbols
                    symbolsList
                }
            }
            .navigationTitle("Select Symbol")
            .navigationBarTitleDisplayMode(.inline)
            .searchable(text: $searchText, prompt: "Search symbols...")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { dismiss() }
                        .foregroundColor(.enlikoPrimary)
                }
            }
        }
    }
    
    // MARK: - Popular Section
    private var popularSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Popular")
                .font(.subheadline.weight(.medium))
                .foregroundColor(.enlikoTextSecondary)
                .padding(.horizontal)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(popularSymbols, id: \.self) { symbol in
                        Button(action: { selectSymbol(symbol) }) {
                            Text(symbol.replacingOccurrences(of: "USDT", with: ""))
                                .font(.subheadline.weight(.medium))
                                .padding(.horizontal, 16)
                                .padding(.vertical, 8)
                                .background(
                                    selectedSymbol == symbol 
                                        ? Color.enlikoPrimary 
                                        : Color.enlikoCard
                                )
                                .foregroundColor(
                                    selectedSymbol == symbol 
                                        ? .white 
                                        : .enlikoText
                                )
                                .cornerRadius(20)
                        }
                    }
                }
                .padding(.horizontal)
            }
            
            Divider()
                .background(Color.enlikoCardHover)
                .padding(.top, 8)
        }
        .padding(.vertical, 12)
    }
    
    // MARK: - Symbols List
    private var symbolsList: some View {
        List {
            ForEach(filteredSymbols) { symbolInfo in
                Button(action: { selectSymbol(symbolInfo.symbol) }) {
                    HStack {
                        // Symbol Icon
                        ZStack {
                            Circle()
                                .fill(Color.enlikoCard)
                                .frame(width: 40, height: 40)
                            
                            Text(String(symbolInfo.symbol.prefix(1)))
                                .font(.headline.weight(.bold))
                                .foregroundColor(.enlikoPrimary)
                        }
                        
                        // Symbol Name
                        VStack(alignment: .leading, spacing: 2) {
                            Text(symbolInfo.base)
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            HStack(spacing: 4) {
                                Text("/ USDT")
                                    .font(.caption)
                                    .foregroundColor(.enlikoTextSecondary)
                                
                                if symbolInfo.price > 0 {
                                    Text("$\(symbolInfo.price, specifier: "%.2f")")
                                        .font(.caption)
                                        .foregroundColor(.enlikoTextSecondary)
                                }
                            }
                        }
                        
                        Spacer()
                        
                        // Price change + Checkmark
                        VStack(alignment: .trailing, spacing: 2) {
                            if symbolInfo.change24h != 0 {
                                Text("\(symbolInfo.change24h >= 0 ? "+" : "")\(symbolInfo.change24h, specifier: "%.2f")%")
                                    .font(.caption.weight(.medium))
                                    .foregroundColor(symbolInfo.change24h >= 0 ? .green : .red)
                            }
                            
                            if selectedSymbol == symbolInfo.symbol {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.enlikoPrimary)
                            }
                        }
                    }
                    .padding(.vertical, 4)
                }
                .listRowBackground(Color.enlikoBackground)
            }
        }
        .listStyle(.plain)
        .scrollContentBackground(.hidden)
    }
    
    private func selectSymbol(_ symbol: String) {
        selectedSymbol = symbol
        dismiss()
    }
}

#Preview {
    SymbolPickerView(selectedSymbol: .constant("BTCUSDT"))
        .environmentObject(TradingService.shared)
        .preferredColorScheme(.dark)
}
