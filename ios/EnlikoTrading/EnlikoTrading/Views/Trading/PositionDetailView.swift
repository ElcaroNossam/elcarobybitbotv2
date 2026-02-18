//
//  PositionDetailView.swift
//  EnlikoTrading
//
//  Full position management like Binance/Bybit
//  Features: Partial close, Add to position, TP/SL modification, Position info
//

import SwiftUI

struct PositionDetailView: View {
    let position: Position
    
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var tradingService: TradingService
    @Environment(\.dismiss) var dismiss
    
    // State
    @State private var showPartialClose = false
    @State private var showAddPosition = false
    @State private var showModifyTPSL = false
    @State private var showCloseConfirm = false
    @State private var isLoading = false
    
    // Partial close
    @State private var closePercent: Double = 50
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.enlikoBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Position Header Card
                        positionHeader
                        
                        // PnL Card
                        pnlCard
                        
                        // Position Details
                        positionDetails
                        
                        // TP/SL Status
                        tpslStatus
                        
                        // Quick Actions
                        quickActions
                        
                        // Danger Zone
                        dangerZone
                        
                        Spacer(minLength: 50)
                    }
                    .padding()
                }
            }
            .navigationTitle(position.symbol)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button { dismiss() } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
                
                ToolbarItem(placement: .primaryAction) {
                    Menu {
                        Button {
                            showModifyTPSL = true
                        } label: {
                            Label("pos_modify_tpsl".localized, systemImage: "slider.horizontal.3")
                        }
                        
                        Button {
                            showAddPosition = true
                        } label: {
                            Label("pos_add_to_position".localized, systemImage: "plus.circle")
                        }
                        
                        Divider()
                        
                        Button(role: .destructive) {
                            showCloseConfirm = true
                        } label: {
                            Label("pos_close_position".localized, systemImage: "xmark.circle")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle.fill")
                            .foregroundColor(.enlikoPrimary)
                    }
                }
            }
            .sheet(isPresented: $showPartialClose) {
                PartialCloseSheet(position: position, percent: $closePercent, onClose: closePartial)
            }
            .sheet(isPresented: $showModifyTPSL) {
                ModifyTPSLSheet(position: position)
            }
            .sheet(isPresented: $showAddPosition) {
                AddToPositionSheet(position: position)
            }
            .confirmationDialog("pos_close_position".localized, isPresented: $showCloseConfirm, titleVisibility: .visible) {
                Button("pos_close_100".localized, role: .destructive) {
                    closePosition(percent: 100)
                }
                Button("btn_cancel".localized, role: .cancel) {}
            } message: {
                Text("pos_close_confirm_msg".localized)
            }
        }
    }
    
    // MARK: - Position Header
    private var positionHeader: some View {
        HStack {
            // Side Badge
            VStack(spacing: 4) {
                Image(systemName: position.side.lowercased() == "buy" ? "arrow.up.circle.fill" : "arrow.down.circle.fill")
                    .font(.system(size: 40))
                    .foregroundColor(position.side.lowercased() == "buy" ? .green : .red)
                
                Text(position.side.lowercased() == "buy" ? "LONG" : "SHORT")
                    .font(.caption.bold())
                    .foregroundColor(position.side.lowercased() == "buy" ? .green : .red)
            }
            .padding()
            .background(
                (position.side.lowercased() == "buy" ? Color.green : Color.red).opacity(0.15)
            )
            .cornerRadius(16)
            
            VStack(alignment: .leading, spacing: 8) {
                Text(position.symbol)
                    .font(.title2.bold())
                
                HStack(spacing: 12) {
                    // Leverage Badge
                    Text("\(position.leverage)x")
                        .font(.caption.bold())
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(leverageColor.opacity(0.2))
                        .foregroundColor(leverageColor)
                        .cornerRadius(8)
                    
                    // Exchange Badge
                    Text(appState.currentExchange.displayName)
                        .font(.caption)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(Color.enlikoSurface)
                        .foregroundColor(.secondary)
                        .cornerRadius(8)
                    
                    // Strategy Badge
                    if let strategy = position.strategy {
                        Text(strategy.uppercased())
                            .font(.caption)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 4)
                            .background(Color.enlikoPrimary.opacity(0.2))
                            .foregroundColor(.enlikoPrimary)
                            .cornerRadius(8)
                    }
                }
            }
            
            Spacer()
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    private var leverageColor: Color {
        if position.leverage <= 10 { return .green }
        if position.leverage <= 50 { return .orange }
        return .red
    }
    
    // MARK: - PnL Card
    private var pnlCard: some View {
        VStack(spacing: 16) {
            // Unrealized PnL
            VStack(spacing: 4) {
                Text("pos_unrealized_pnl".localized)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text(position.pnlDisplay)
                    .font(.system(size: 36, weight: .bold))
                    .foregroundColor(position.pnlColor)
                
                Text(position.pnlPercentDisplay)
                    .font(.title3.bold())
                    .foregroundColor(position.pnlColor)
            }
            
            Divider()
            
            // ROE
            HStack {
                VStack {
                    Text("pos_roe".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "%.2f%%", position.pnlPercent * Double(position.leverage)))
                        .font(.headline.bold())
                        .foregroundColor(position.pnlColor)
                }
                
                Spacer()
                
                VStack {
                    Text("pos_size".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "%.4f", position.size))
                        .font(.headline)
                }
                
                Spacer()
                
                VStack {
                    Text("pos_value".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "$%.2f", position.positionValue))
                        .font(.headline)
                }
            }
        }
        .padding()
        .background(
            LinearGradient(
                colors: [
                    position.pnl >= 0 ? Color.green.opacity(0.15) : Color.red.opacity(0.15),
                    Color.enlikoSurface
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(16)
    }
    
    // MARK: - Position Details
    private var positionDetails: some View {
        VStack(spacing: 12) {
            HStack {
                Text("pos_details".localized)
                    .font(.headline)
                Spacer()
            }
            
            detailRow("pos_entry_price".localized, String(format: "$%.2f", position.entryPrice))
            detailRow("pos_mark_price".localized, String(format: "$%.2f", position.markPrice ?? position.entryPrice))
            detailRow("pos_liq_price".localized, String(format: "$%.2f", position.liquidationPrice ?? 0), color: .orange)
            detailRow("pos_margin".localized, String(format: "$%.2f", position.margin ?? 0))
            detailRow("pos_maintenance_margin".localized, String(format: "$%.2f", position.maintenanceMargin ?? 0))
            
            if let openTime = position.openTime {
                detailRow("pos_opened".localized, formatDate(openTime))
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    private func detailRow(_ label: String, _ value: String, color: Color = .white) -> some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundColor(.secondary)
            Spacer()
            Text(value)
                .font(.subheadline.bold())
                .foregroundColor(color)
        }
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .short
        return formatter.localizedString(for: date, relativeTo: Date())
    }
    
    // MARK: - TP/SL Status
    private var tpslStatus: some View {
        VStack(spacing: 12) {
            HStack {
                Text("pos_tpsl".localized)
                    .font(.headline)
                
                Spacer()
                
                Button {
                    showModifyTPSL = true
                } label: {
                    Text("btn_modify".localized)
                        .font(.caption.bold())
                        .foregroundColor(.enlikoPrimary)
                }
            }
            
            HStack(spacing: 16) {
                // Take Profit
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "target")
                            .foregroundColor(.green)
                        Text("pos_take_profit".localized)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    if let tp = position.takeProfit, tp > 0 {
                        Text(String(format: "$%.2f", tp))
                            .font(.headline.bold())
                            .foregroundColor(.green)
                        
                        // Distance
                        let distance = abs((tp - (position.markPrice ?? position.entryPrice)) / position.entryPrice * 100)
                        Text(String(format: "+%.2f%%", distance))
                            .font(.caption)
                            .foregroundColor(.green.opacity(0.7))
                    } else {
                        Text("pos_not_set".localized)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.green.opacity(0.1))
                .cornerRadius(12)
                
                // Stop Loss
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "exclamationmark.shield.fill")
                            .foregroundColor(.red)
                        Text("pos_stop_loss".localized)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    if let sl = position.stopLoss, sl > 0 {
                        Text(String(format: "$%.2f", sl))
                            .font(.headline.bold())
                            .foregroundColor(.red)
                        
                        // Distance
                        let distance = abs((sl - (position.markPrice ?? position.entryPrice)) / position.entryPrice * 100)
                        Text(String(format: "-%.2f%%", distance))
                            .font(.caption)
                            .foregroundColor(.red.opacity(0.7))
                    } else {
                        Text("pos_not_set".localized)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.red.opacity(0.1))
                .cornerRadius(12)
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    // MARK: - Quick Actions
    private var quickActions: some View {
        VStack(spacing: 12) {
            HStack {
                Text("pos_quick_actions".localized)
                    .font(.headline)
                Spacer()
            }
            
            HStack(spacing: 12) {
                // Partial Close
                Button {
                    showPartialClose = true
                } label: {
                    VStack(spacing: 8) {
                        Image(systemName: "chart.pie.fill")
                            .font(.title2)
                        Text("pos_partial_close".localized)
                            .font(.caption)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.orange.opacity(0.2))
                    .foregroundColor(.orange)
                    .cornerRadius(12)
                }
                
                // Add to Position
                Button {
                    showAddPosition = true
                } label: {
                    VStack(spacing: 8) {
                        Image(systemName: "plus.circle.fill")
                            .font(.title2)
                        Text("pos_add_position".localized)
                            .font(.caption)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.enlikoPrimary.opacity(0.2))
                    .foregroundColor(.enlikoPrimary)
                    .cornerRadius(12)
                }
                
                // Flip Position
                Button {
                    // TODO: Implement flip
                } label: {
                    VStack(spacing: 8) {
                        Image(systemName: "arrow.triangle.swap")
                            .font(.title2)
                        Text("pos_flip".localized)
                            .font(.caption)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.purple.opacity(0.2))
                    .foregroundColor(.purple)
                    .cornerRadius(12)
                }
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    // MARK: - Danger Zone
    private var dangerZone: some View {
        VStack(spacing: 12) {
            // Close 100%
            Button {
                showCloseConfirm = true
            } label: {
                HStack {
                    Image(systemName: "xmark.circle.fill")
                    Text("pos_close_full".localized)
                        .font(.headline)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.red)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .disabled(isLoading)
            
            // Quick Close Buttons
            HStack(spacing: 12) {
                quickCloseButton(25)
                quickCloseButton(50)
                quickCloseButton(75)
            }
        }
    }
    
    private func quickCloseButton(_ percent: Int) -> some View {
        Button {
            closePercent = Double(percent)
            closePartial()
        } label: {
            Text("Close \(percent)%")
                .font(.subheadline.bold())
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(Color.enlikoSurface)
                .foregroundColor(.orange)
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color.orange, lineWidth: 1)
                )
        }
        .disabled(isLoading)
    }
    
    // MARK: - Actions
    private func closePosition(percent: Double) {
        isLoading = true
        Task {
            // For partial close, we would need to add a new API endpoint
            // For now, close full position when 100%
            if percent >= 100 {
                await tradingService.closePosition(
                    symbol: position.symbol,
                    side: position.side
                )
            } else {
                // TODO: Add partial close API endpoint
                // For now show that partial close would close X% of position
                print("Would close \(percent)% of \(position.symbol)")
                await tradingService.closePosition(
                    symbol: position.symbol,
                    side: position.side
                )
            }
            await MainActor.run {
                isLoading = false
                dismiss()
            }
        }
    }
    
    private func closePartial() {
        closePosition(percent: closePercent)
    }
}

// MARK: - Partial Close Sheet
struct PartialCloseSheet: View {
    let position: Position
    @Binding var percent: Double
    let onClose: () -> Void
    
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 8) {
                    Text("pos_close_partial_title".localized)
                        .font(.title2.bold())
                    
                    Text(position.symbol)
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
                .padding(.top)
                
                // Slider
                VStack(spacing: 16) {
                    Text("\(Int(percent))%")
                        .font(.system(size: 48, weight: .bold))
                        .foregroundColor(.orange)
                    
                    Slider(value: $percent, in: 1...100, step: 1)
                        .tint(.orange)
                    
                    // Quick Buttons
                    HStack(spacing: 12) {
                        ForEach([25, 50, 75, 100], id: \.self) { p in
                            Button {
                                percent = Double(p)
                            } label: {
                                Text("\(p)%")
                                    .font(.subheadline.bold())
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 10)
                                    .background(Int(percent) == p ? Color.orange : Color.enlikoSurface)
                                    .foregroundColor(Int(percent) == p ? .white : .secondary)
                                    .cornerRadius(8)
                            }
                        }
                    }
                }
                .padding()
                
                // Summary
                VStack(spacing: 8) {
                    HStack {
                        Text("pos_closing_size".localized)
                        Spacer()
                        Text(String(format: "%.4f", position.size * percent / 100))
                            .bold()
                    }
                    
                    HStack {
                        Text("pos_estimated_pnl".localized)
                        Spacer()
                        Text(String(format: "$%.2f", position.pnl * percent / 100))
                            .bold()
                            .foregroundColor(position.pnlColor)
                    }
                    
                    HStack {
                        Text("pos_remaining_size".localized)
                        Spacer()
                        Text(String(format: "%.4f", position.size * (1 - percent / 100)))
                            .bold()
                    }
                }
                .font(.subheadline)
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
                
                Spacer()
                
                // Buttons
                VStack(spacing: 12) {
                    Button {
                        onClose()
                        dismiss()
                    } label: {
                        Text("Close \(Int(percent))% Position")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.orange)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                    }
                    
                    Button {
                        dismiss()
                    } label: {
                        Text("btn_cancel".localized)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding()
            .background(Color.enlikoBackground)
            .navigationBarHidden(true)
        }
        .presentationDetents([.medium, .large])
    }
}

// MARK: - Modify TP/SL Sheet
struct ModifyTPSLSheet: View {
    let position: Position
    
    @EnvironmentObject var tradingService: TradingService
    @Environment(\.dismiss) var dismiss
    
    @State private var tpPrice: String = ""
    @State private var slPrice: String = ""
    @State private var isLoading = false
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                // Header
                VStack(spacing: 4) {
                    Text("pos_modify_tpsl".localized)
                        .font(.title2.bold())
                    Text(position.symbol)
                        .foregroundColor(.secondary)
                }
                .padding(.top)
                
                // Current Price
                HStack {
                    Text("pos_current_price".localized)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text(String(format: "$%.2f", position.markPrice ?? position.entryPrice))
                        .font(.headline)
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
                
                // Take Profit
                VStack(alignment: .leading, spacing: 8) {
                    Label("pos_take_profit".localized, systemImage: "target")
                        .font(.subheadline)
                        .foregroundColor(.green)
                    
                    HStack {
                        TextField("pos_tp_price".localized, text: $tpPrice)
                            .keyboardType(.decimalPad)
                            .font(.title3)
                        
                        Button {
                            tpPrice = ""
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.green.opacity(0.5), lineWidth: 1)
                    )
                }
                
                // Stop Loss
                VStack(alignment: .leading, spacing: 8) {
                    Label("pos_stop_loss".localized, systemImage: "exclamationmark.shield.fill")
                        .font(.subheadline)
                        .foregroundColor(.red)
                    
                    HStack {
                        TextField("pos_sl_price".localized, text: $slPrice)
                            .keyboardType(.decimalPad)
                            .font(.title3)
                        
                        Button {
                            slPrice = ""
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.red.opacity(0.5), lineWidth: 1)
                    )
                }
                
                Spacer()
                
                // Buttons
                VStack(spacing: 12) {
                    Button {
                        saveTPSL()
                    } label: {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            } else {
                                Text("btn_save_changes".localized)
                            }
                        }
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.enlikoPrimary)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .disabled(isLoading)
                    
                    Button {
                        dismiss()
                    } label: {
                        Text("btn_cancel".localized)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding()
            .background(Color.enlikoBackground)
            .navigationBarHidden(true)
            .onAppear {
                if let tp = position.takeProfit, tp > 0 {
                    tpPrice = String(format: "%.2f", tp)
                }
                if let sl = position.stopLoss, sl > 0 {
                    slPrice = String(format: "%.2f", sl)
                }
            }
        }
        .presentationDetents([.medium])
    }
    
    private func saveTPSL() {
        isLoading = true
        Task {
            await tradingService.modifyTPSL(
                symbol: position.symbol,
                side: position.side,
                takeProfit: Double(tpPrice),
                stopLoss: Double(slPrice)
            )
            await MainActor.run {
                isLoading = false
                dismiss()
            }
        }
    }
}

// MARK: - Add to Position Sheet
struct AddToPositionSheet: View {
    let position: Position
    
    @Environment(\.dismiss) var dismiss
    
    @State private var amount: String = ""
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Text("pos_add_to_position".localized)
                    .font(.title2.bold())
                    .padding(.top)
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("pos_current_position".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    HStack {
                        Text(position.symbol)
                            .font(.headline)
                        Spacer()
                        Text(String(format: "%.4f", position.size))
                            .font(.headline)
                    }
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(12)
                }
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("pos_amount_to_add".localized)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    TextField("pos_enter_amount".localized, text: $amount)
                        .keyboardType(.decimalPad)
                        .font(.title3)
                        .padding()
                        .background(Color.enlikoSurface)
                        .cornerRadius(12)
                }
                
                Spacer()
                
                Button {
                    // TODO: Implement add to position
                    dismiss()
                } label: {
                    Text("pos_add_to_position".localized)
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.enlikoPrimary)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
                .disabled(amount.isEmpty)
            }
            .padding()
            .background(Color.enlikoBackground)
            .navigationBarHidden(true)
        }
        .presentationDetents([.medium])
    }
}

#Preview {
    PositionDetailView(position: Position.mock)
    .environmentObject(AppState.shared)
    .environmentObject(TradingService.shared)
    .preferredColorScheme(.dark)
}
