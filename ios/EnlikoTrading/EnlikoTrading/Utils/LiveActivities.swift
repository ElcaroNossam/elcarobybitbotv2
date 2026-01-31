//
//  LiveActivities.swift
//  EnlikoTrading
//
//  🏝️ Dynamic Island + Lock Screen Live Activities
//  ================================================
//
//  Features:
//  1. Position tracking in Dynamic Island
//  2. Lock screen price updates
//  3. Order status tracking
//  4. Signal notifications
//

import SwiftUI
import ActivityKit
import WidgetKit

// MARK: - Position Tracking Activity

struct PositionActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var currentPrice: Double
        var pnl: Double
        var pnlPercent: Double
        var priceChange: Double
        var lastUpdate: Date
    }
    
    var symbol: String
    var side: String // "Long" or "Short"
    var entryPrice: Double
    var size: Double
    var leverage: Int
    var slPrice: Double?
    var tpPrice: Double?
}

// MARK: - Order Tracking Activity

struct OrderActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var status: OrderStatus
        var filledPercent: Double
        var message: String
        var lastUpdate: Date
        
        enum OrderStatus: String, Codable, Hashable {
            case pending
            case partiallyFilled
            case filled
            case cancelled
            case failed
        }
    }
    
    var symbol: String
    var side: String
    var orderType: String // "Limit" or "Market"
    var price: Double
    var qty: Double
}

// MARK: - Live Activity Manager

@available(iOS 16.2, *)
class LiveActivityManager {
    static let shared = LiveActivityManager()
    
    private var positionActivities: [String: Activity<PositionActivityAttributes>] = [:]
    private var orderActivities: [String: Activity<OrderActivityAttributes>] = [:]
    
    // MARK: - Position Activities
    
    func startPositionTracking(
        symbol: String,
        side: String,
        entryPrice: Double,
        currentPrice: Double,
        size: Double,
        leverage: Int,
        slPrice: Double? = nil,
        tpPrice: Double? = nil
    ) {
        guard ActivityAuthorizationInfo().areActivitiesEnabled else { return }
        
        let pnl = calculatePnL(side: side, entryPrice: entryPrice, currentPrice: currentPrice, size: size)
        let pnlPercent = calculatePnLPercent(side: side, entryPrice: entryPrice, currentPrice: currentPrice, leverage: leverage)
        
        let attributes = PositionActivityAttributes(
            symbol: symbol,
            side: side,
            entryPrice: entryPrice,
            size: size,
            leverage: leverage,
            slPrice: slPrice,
            tpPrice: tpPrice
        )
        
        let state = PositionActivityAttributes.ContentState(
            currentPrice: currentPrice,
            pnl: pnl,
            pnlPercent: pnlPercent,
            priceChange: currentPrice - entryPrice,
            lastUpdate: Date()
        )
        
        do {
            let activity = try Activity.request(
                attributes: attributes,
                content: .init(state: state, staleDate: Date().addingTimeInterval(300))
            )
            positionActivities[symbol] = activity
            print("Started position activity for \(symbol)")
        } catch {
            print("Error starting position activity: \(error)")
        }
    }
    
    func updatePositionActivity(symbol: String, currentPrice: Double) {
        guard let activity = positionActivities[symbol] else { return }
        
        let attributes = activity.attributes
        let pnl = calculatePnL(side: attributes.side, entryPrice: attributes.entryPrice, currentPrice: currentPrice, size: attributes.size)
        let pnlPercent = calculatePnLPercent(side: attributes.side, entryPrice: attributes.entryPrice, currentPrice: currentPrice, leverage: attributes.leverage)
        
        let state = PositionActivityAttributes.ContentState(
            currentPrice: currentPrice,
            pnl: pnl,
            pnlPercent: pnlPercent,
            priceChange: currentPrice - attributes.entryPrice,
            lastUpdate: Date()
        )
        
        Task {
            await activity.update(.init(state: state, staleDate: Date().addingTimeInterval(300)))
        }
    }
    
    func endPositionActivity(symbol: String, finalPrice: Double, reason: String) {
        guard let activity = positionActivities[symbol] else { return }
        
        let attributes = activity.attributes
        let pnl = calculatePnL(side: attributes.side, entryPrice: attributes.entryPrice, currentPrice: finalPrice, size: attributes.size)
        let pnlPercent = calculatePnLPercent(side: attributes.side, entryPrice: attributes.entryPrice, currentPrice: finalPrice, leverage: attributes.leverage)
        
        let finalState = PositionActivityAttributes.ContentState(
            currentPrice: finalPrice,
            pnl: pnl,
            pnlPercent: pnlPercent,
            priceChange: finalPrice - attributes.entryPrice,
            lastUpdate: Date()
        )
        
        Task {
            await activity.end(.init(state: finalState, staleDate: nil), dismissalPolicy: .default)
            positionActivities.removeValue(forKey: symbol)
        }
    }
    
    // MARK: - Order Activities
    
    func startOrderTracking(
        orderId: String,
        symbol: String,
        side: String,
        orderType: String,
        price: Double,
        qty: Double
    ) {
        guard ActivityAuthorizationInfo().areActivitiesEnabled else { return }
        
        let attributes = OrderActivityAttributes(
            symbol: symbol,
            side: side,
            orderType: orderType,
            price: price,
            qty: qty
        )
        
        let state = OrderActivityAttributes.ContentState(
            status: .pending,
            filledPercent: 0,
            message: "Order placed",
            lastUpdate: Date()
        )
        
        do {
            let activity = try Activity.request(
                attributes: attributes,
                content: .init(state: state, staleDate: Date().addingTimeInterval(300))
            )
            orderActivities[orderId] = activity
        } catch {
            print("Error starting order activity: \(error)")
        }
    }
    
    func updateOrderActivity(orderId: String, status: OrderActivityAttributes.ContentState.OrderStatus, filledPercent: Double, message: String) {
        guard let activity = orderActivities[orderId] else { return }
        
        let state = OrderActivityAttributes.ContentState(
            status: status,
            filledPercent: filledPercent,
            message: message,
            lastUpdate: Date()
        )
        
        Task {
            if status == .filled || status == .cancelled || status == .failed {
                await activity.end(.init(state: state, staleDate: nil), dismissalPolicy: .after(.init(timeIntervalSinceNow: 10)))
                orderActivities.removeValue(forKey: orderId)
            } else {
                await activity.update(.init(state: state, staleDate: Date().addingTimeInterval(300)))
            }
        }
    }
    
    // MARK: - Helper Functions
    
    private func calculatePnL(side: String, entryPrice: Double, currentPrice: Double, size: Double) -> Double {
        if side == "Long" {
            return (currentPrice - entryPrice) * size
        } else {
            return (entryPrice - currentPrice) * size
        }
    }
    
    private func calculatePnLPercent(side: String, entryPrice: Double, currentPrice: Double, leverage: Int) -> Double {
        let priceChange: Double
        if side == "Long" {
            priceChange = (currentPrice - entryPrice) / entryPrice
        } else {
            priceChange = (entryPrice - currentPrice) / entryPrice
        }
        return priceChange * 100 * Double(leverage)
    }
    
    func endAllActivities() {
        for (symbol, activity) in positionActivities {
            Task {
                let finalContent = activity.content
                await activity.end(finalContent, dismissalPolicy: .immediate)
            }
            positionActivities.removeValue(forKey: symbol)
        }
        
        for (orderId, activity) in orderActivities {
            Task {
                let finalContent = activity.content
                await activity.end(finalContent, dismissalPolicy: .immediate)
            }
            orderActivities.removeValue(forKey: orderId)
        }
    }
}

// MARK: - Position Activity Widget Views

struct PositionActivityWidgetView: View {
    let context: ActivityViewContext<PositionActivityAttributes>
    
    var body: some View {
        HStack(spacing: 12) {
            // Left: Symbol & Side
            VStack(alignment: .leading, spacing: 2) {
                Text(context.attributes.symbol.replacingOccurrences(of: "USDT", with: ""))
                    .font(.headline.bold())
                
                HStack(spacing: 4) {
                    Circle()
                        .fill(context.attributes.side == "Long" ? Color.green : Color.red)
                        .frame(width: 6, height: 6)
                    Text(context.attributes.side)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("\(context.attributes.leverage)x")
                        .font(.caption.bold())
                        .foregroundColor(.purple)
                }
            }
            
            Spacer()
            
            // Right: Price & PnL
            VStack(alignment: .trailing, spacing: 2) {
                Text("$\(context.state.currentPrice, specifier: "%.2f")")
                    .font(.system(.headline, design: .monospaced))
                
                HStack(spacing: 4) {
                    Image(systemName: context.state.pnl >= 0 ? "arrow.up.right" : "arrow.down.right")
                        .font(.caption2)
                    Text(String(format: "%+.2f%%", context.state.pnlPercent))
                        .font(.caption.bold())
                }
                .foregroundColor(context.state.pnl >= 0 ? .green : .red)
            }
        }
        .padding()
    }
}

// Compact view for Dynamic Island
struct PositionCompactView: View {
    let context: ActivityViewContext<PositionActivityAttributes>
    
    var body: some View {
        HStack(spacing: 8) {
            // Symbol
            Text(context.attributes.symbol.replacingOccurrences(of: "USDT", with: ""))
                .font(.caption.bold())
            
            // PnL
            Text(String(format: "%+.1f%%", context.state.pnlPercent))
                .font(.caption.bold())
                .foregroundColor(context.state.pnl >= 0 ? .green : .red)
        }
    }
}

// Minimal view for Dynamic Island ends
struct PositionMinimalView: View {
    let context: ActivityViewContext<PositionActivityAttributes>
    let isLeading: Bool
    
    var body: some View {
        if isLeading {
            // Leading: Symbol
            Text(context.attributes.symbol.replacingOccurrences(of: "USDT", with: ""))
                .font(.caption2.bold())
        } else {
            // Trailing: PnL %
            Text(String(format: "%+.0f%%", context.state.pnlPercent))
                .font(.caption2.bold())
                .foregroundColor(context.state.pnl >= 0 ? .green : .red)
        }
    }
}

// MARK: - Order Activity Widget Views

struct OrderActivityWidgetView: View {
    let context: ActivityViewContext<OrderActivityAttributes>
    
    var body: some View {
        HStack(spacing: 12) {
            // Status icon
            ZStack {
                Circle()
                    .fill(statusColor.opacity(0.2))
                    .frame(width: 40, height: 40)
                
                Image(systemName: statusIcon)
                    .foregroundColor(statusColor)
            }
            
            // Info
            VStack(alignment: .leading, spacing: 2) {
                Text("\(context.attributes.side) \(context.attributes.symbol.replacingOccurrences(of: "USDT", with: ""))")
                    .font(.headline.bold())
                
                Text(context.state.message)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // Progress
            if context.state.status == .partiallyFilled {
                VStack(alignment: .trailing, spacing: 2) {
                    Text("\(Int(context.state.filledPercent))%")
                        .font(.headline.bold())
                    Text("Filled")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
    }
    
    var statusColor: Color {
        switch context.state.status {
        case .pending: return .orange
        case .partiallyFilled: return .blue
        case .filled: return .green
        case .cancelled: return .gray
        case .failed: return .red
        }
    }
    
    var statusIcon: String {
        switch context.state.status {
        case .pending: return "clock.fill"
        case .partiallyFilled: return "chart.pie.fill"
        case .filled: return "checkmark.circle.fill"
        case .cancelled: return "xmark.circle.fill"
        case .failed: return "exclamationmark.triangle.fill"
        }
    }
}

// MARK: - Lock Screen View

struct PositionLockScreenView: View {
    let context: ActivityViewContext<PositionActivityAttributes>
    
    var body: some View {
        VStack(spacing: 8) {
            // Top row: Symbol and Price
            HStack {
                // Side indicator + Symbol
                HStack(spacing: 6) {
                    RoundedRectangle(cornerRadius: 2)
                        .fill(context.attributes.side == "Long" ? Color.green : Color.red)
                        .frame(width: 4, height: 24)
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text(context.attributes.symbol.replacingOccurrences(of: "USDT", with: ""))
                            .font(.headline.bold())
                        Text("\(context.attributes.side) \(context.attributes.leverage)x")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                // Current price
                VStack(alignment: .trailing, spacing: 2) {
                    Text("$\(context.state.currentPrice, specifier: "%.2f")")
                        .font(.system(.title3, design: .monospaced).bold())
                    
                    HStack(spacing: 2) {
                        Image(systemName: context.state.priceChange >= 0 ? "arrow.up" : "arrow.down")
                            .font(.caption2)
                        Text(String(format: "%+.2f", context.state.priceChange))
                            .font(.caption2)
                    }
                    .foregroundColor(context.state.priceChange >= 0 ? .green : .red)
                }
            }
            
            // Bottom row: PnL and Levels
            HStack {
                // PnL
                VStack(alignment: .leading, spacing: 2) {
                    Text("PnL")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Text(String(format: "%+.2f USDT", context.state.pnl))
                        .font(.caption.bold())
                        .foregroundColor(context.state.pnl >= 0 ? .green : .red)
                }
                
                Spacer()
                
                // ROE
                VStack(alignment: .center, spacing: 2) {
                    Text("ROE")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Text(String(format: "%+.1f%%", context.state.pnlPercent))
                        .font(.caption.bold())
                        .foregroundColor(context.state.pnlPercent >= 0 ? .green : .red)
                }
                
                Spacer()
                
                // TP/SL Levels
                VStack(alignment: .trailing, spacing: 2) {
                    if let tpPrice = context.attributes.tpPrice {
                        HStack(spacing: 2) {
                            Text("TP")
                                .font(.caption2)
                                .foregroundColor(.green)
                            Text("$\(tpPrice, specifier: "%.2f")")
                                .font(.caption2)
                        }
                    }
                    if let slPrice = context.attributes.slPrice {
                        HStack(spacing: 2) {
                            Text("SL")
                                .font(.caption2)
                                .foregroundColor(.red)
                            Text("$\(slPrice, specifier: "%.2f")")
                                .font(.caption2)
                        }
                    }
                }
            }
        }
        .padding()
    }
}

// MARK: - Usage Example

/*
 
// Start tracking a position:
if #available(iOS 16.2, *) {
    LiveActivityManager.shared.startPositionTracking(
        symbol: "BTCUSDT",
        side: "Long",
        entryPrice: 42000,
        currentPrice: 42500,
        size: 0.1,
        leverage: 10,
        slPrice: 41000,
        tpPrice: 45000
    )
}

// Update price:
if #available(iOS 16.2, *) {
    LiveActivityManager.shared.updatePositionActivity(
        symbol: "BTCUSDT",
        currentPrice: 43000
    )
}

// End position:
if #available(iOS 16.2, *) {
    LiveActivityManager.shared.endPositionActivity(
        symbol: "BTCUSDT",
        finalPrice: 45000,
        reason: "TP Hit"
    )
}
 
*/

// MARK: - Preview

@available(iOS 16.2, *)
struct LiveActivitiesPreview: View {
    var body: some View {
        VStack(spacing: 20) {
            // Position Activity Preview
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.black.opacity(0.8))
                .frame(height: 100)
                .overlay(
                    HStack {
                        VStack(alignment: .leading) {
                            Text("BTC")
                                .font(.headline.bold())
                                .foregroundColor(.white)
                            HStack {
                                Circle()
                                    .fill(Color.green)
                                    .frame(width: 6, height: 6)
                                Text("Long 10x")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                        }
                        Spacer()
                        VStack(alignment: .trailing) {
                            Text("$43,250.00")
                                .font(.system(.headline, design: .monospaced))
                                .foregroundColor(.white)
                            Text("+12.5%")
                                .font(.caption.bold())
                                .foregroundColor(.green)
                        }
                    }
                    .padding()
                )
            
            Text("Dynamic Island Preview")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
    }
}

#Preview("Live Activities") {
    if #available(iOS 16.2, *) {
        LiveActivitiesPreview()
    } else {
        Text("iOS 16.2+ required")
    }
}
