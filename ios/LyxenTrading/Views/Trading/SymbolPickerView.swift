//
//  SymbolPickerView.swift
//  LyxenTrading
//
//  Symbol selection sheet
//

import SwiftUI

struct SymbolPickerView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var tradingService: TradingService
    @Binding var selectedSymbol: String
    @State private var searchText = ""
    
    var filteredSymbols: [String] {
        if searchText.isEmpty {
            return tradingService.symbols
        }
        return tradingService.symbols.filter {
            $0.localizedCaseInsensitiveContains(searchText)
        }
    }
    
    // Popular symbols to show at top
    let popularSymbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT"]
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.lyxenBackground.ignoresSafeArea()
                
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
                        .foregroundColor(.lyxenPrimary)
                }
            }
        }
    }
    
    // MARK: - Popular Section
    private var popularSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Popular")
                .font(.subheadline.weight(.medium))
                .foregroundColor(.lyxenTextSecondary)
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
                                        ? Color.lyxenPrimary 
                                        : Color.lyxenCard
                                )
                                .foregroundColor(
                                    selectedSymbol == symbol 
                                        ? .white 
                                        : .lyxenText
                                )
                                .cornerRadius(20)
                        }
                    }
                }
                .padding(.horizontal)
            }
            
            Divider()
                .background(Color.lyxenCardHover)
                .padding(.top, 8)
        }
        .padding(.vertical, 12)
    }
    
    // MARK: - Symbols List
    private var symbolsList: some View {
        List {
            ForEach(filteredSymbols, id: \.self) { symbol in
                Button(action: { selectSymbol(symbol) }) {
                    HStack {
                        // Symbol Icon
                        ZStack {
                            Circle()
                                .fill(Color.lyxenCard)
                                .frame(width: 40, height: 40)
                            
                            Text(String(symbol.prefix(1)))
                                .font(.headline.weight(.bold))
                                .foregroundColor(.lyxenPrimary)
                        }
                        
                        // Symbol Name
                        VStack(alignment: .leading, spacing: 2) {
                            Text(symbol.replacingOccurrences(of: "USDT", with: ""))
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            Text("/ USDT Perpetual")
                                .font(.caption)
                                .foregroundColor(.lyxenTextSecondary)
                        }
                        
                        Spacer()
                        
                        // Checkmark
                        if selectedSymbol == symbol {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.lyxenPrimary)
                        }
                    }
                    .padding(.vertical, 4)
                }
                .listRowBackground(Color.lyxenBackground)
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
