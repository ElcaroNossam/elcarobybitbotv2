//
//  LoadingView.swift
//  LyxenTrading
//
//  Full screen loading indicator
//

import SwiftUI

struct LoadingView: View {
    var message: String = "Loading..."
    @State private var isAnimating = false
    
    var body: some View {
        ZStack {
            Color.lyxenBackground.ignoresSafeArea()
            
            VStack(spacing: 24) {
                // Animated Logo
                ZStack {
                    // Outer ring
                    Circle()
                        .stroke(Color.lyxenPrimary.opacity(0.3), lineWidth: 4)
                        .frame(width: 80, height: 80)
                    
                    // Spinning arc
                    Circle()
                        .trim(from: 0, to: 0.3)
                        .stroke(Color.lyxenPrimary, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                        .frame(width: 80, height: 80)
                        .rotationEffect(.degrees(isAnimating ? 360 : 0))
                        .animation(.linear(duration: 1).repeatForever(autoreverses: false), value: isAnimating)
                    
                    // Icon
                    Image(systemName: "chart.line.uptrend.xyaxis")
                        .font(.system(size: 30))
                        .foregroundColor(.lyxenPrimary)
                }
                
                Text(message)
                    .font(.subheadline)
                    .foregroundColor(.lyxenTextSecondary)
            }
        }
        .onAppear {
            isAnimating = true
        }
    }
}

// MARK: - Toast View
struct ToastView: View {
    let message: String
    let type: ToastType
    
    enum ToastType {
        case success, error, info
        
        var icon: String {
            switch self {
            case .success: return "checkmark.circle.fill"
            case .error: return "xmark.circle.fill"
            case .info: return "info.circle.fill"
            }
        }
        
        var color: Color {
            switch self {
            case .success: return .lyxenGreen
            case .error: return .lyxenRed
            case .info: return .lyxenBlue
            }
        }
    }
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: type.icon)
                .foregroundColor(type.color)
            
            Text(message)
                .font(.subheadline)
                .foregroundColor(.white)
        }
        .padding()
        .background(Color.lyxenCard)
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.3), radius: 10)
    }
}

// MARK: - Empty State View
struct EmptyStateView: View {
    let icon: String
    let title: String
    let message: String
    var actionTitle: String? = nil
    var action: (() -> Void)? = nil
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 60))
                .foregroundColor(.lyxenTextMuted)
            
            Text(title)
                .font(.title3.weight(.medium))
                .foregroundColor(.white)
            
            Text(message)
                .font(.subheadline)
                .foregroundColor(.lyxenTextSecondary)
                .multilineTextAlignment(.center)
            
            if let actionTitle = actionTitle, let action = action {
                Button(action: action) {
                    Text(actionTitle)
                        .font(.headline)
                        .padding(.horizontal, 24)
                        .padding(.vertical, 12)
                        .background(Color.lyxenPrimary)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .padding(.top, 8)
            }
        }
        .padding()
    }
}

// MARK: - Shimmer Effect
struct ShimmerView: View {
    @State private var isAnimating = false
    
    var body: some View {
        LinearGradient(
            colors: [
                Color.lyxenCard,
                Color.lyxenCardHover,
                Color.lyxenCard
            ],
            startPoint: .leading,
            endPoint: .trailing
        )
        .mask(
            Rectangle()
                .fill(Color.white)
        )
        .offset(x: isAnimating ? 200 : -200)
        .animation(.linear(duration: 1.5).repeatForever(autoreverses: false), value: isAnimating)
        .onAppear {
            isAnimating = true
        }
    }
}

// MARK: - Skeleton Loading
struct SkeletonCard: View {
    var height: CGFloat = 100
    
    var body: some View {
        RoundedRectangle(cornerRadius: 12)
            .fill(Color.lyxenCard)
            .frame(height: height)
            .overlay(ShimmerView())
            .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

// MARK: - Price Change Indicator
struct PriceChangeView: View {
    let change: Double
    let showArrow: Bool
    
    init(change: Double, showArrow: Bool = true) {
        self.change = change
        self.showArrow = showArrow
    }
    
    var body: some View {
        HStack(spacing: 4) {
            if showArrow {
                Image(systemName: change >= 0 ? "arrow.up" : "arrow.down")
                    .font(.caption2.weight(.bold))
            }
            Text(abs(change).formattedPercent)
                .font(.subheadline.weight(.medium))
        }
        .foregroundColor(change >= 0 ? .lyxenGreen : .lyxenRed)
    }
}

// MARK: - Gradient Button
struct GradientButton: View {
    let title: String
    let icon: String?
    let action: () -> Void
    var isLoading: Bool = false
    var isDisabled: Bool = false
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else {
                    if let icon = icon {
                        Image(systemName: icon)
                    }
                    Text(title)
                        .fontWeight(.semibold)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(
                Group {
                    if isDisabled {
                        Color.lyxenTextMuted
                    } else {
                        Color.lyxenGradient
                    }
                }
            )
            .foregroundColor(.white)
            .cornerRadius(12)
        }
        .disabled(isLoading || isDisabled)
    }
}

// MARK: - Safe Area Bottom Padding
extension View {
    func safeAreaBottomPadding(_ value: CGFloat = 20) -> some View {
        self.padding(.bottom, value)
            .padding(.bottom, UIApplication.shared.connectedScenes
                .compactMap { $0 as? UIWindowScene }
                .flatMap { $0.windows }
                .first { $0.isKeyWindow }?
                .safeAreaInsets.bottom ?? 0)
    }
}

#Preview {
    VStack(spacing: 20) {
        LoadingView()
        
        ToastView(message: "Order placed successfully", type: .success)
        
        EmptyStateView(
            icon: "chart.bar.xaxis",
            title: "No Data",
            message: "Start trading to see your stats",
            actionTitle: "Start Trading"
        ) {}
    }
    .preferredColorScheme(.dark)
}
