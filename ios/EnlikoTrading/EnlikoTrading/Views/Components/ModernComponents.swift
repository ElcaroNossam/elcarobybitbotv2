//
//  ModernComponents.swift
//  EnlikoTrading
//
//  Modern UI Components Library - 2026 Design System
//  Glass morphism, smooth animations, dynamic gradients
//

import SwiftUI

// MARK: - Glass Morphism Card
struct GlassCard<Content: View>: View {
    let content: Content
    var cornerRadius: CGFloat = 20
    var blur: CGFloat = 20
    
    init(cornerRadius: CGFloat = 20, blur: CGFloat = 20, @ViewBuilder content: () -> Content) {
        self.content = content()
        self.cornerRadius = cornerRadius
        self.blur = blur
    }
    
    var body: some View {
        content
            .background(
                ZStack {
                    // Glass effect
                    RoundedRectangle(cornerRadius: cornerRadius)
                        .fill(.ultraThinMaterial)
                    
                    // Subtle gradient overlay
                    RoundedRectangle(cornerRadius: cornerRadius)
                        .fill(
                            LinearGradient(
                                colors: [
                                    Color.white.opacity(0.1),
                                    Color.clear
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    
                    // Border glow
                    RoundedRectangle(cornerRadius: cornerRadius)
                        .stroke(
                            LinearGradient(
                                colors: [
                                    Color.white.opacity(0.3),
                                    Color.white.opacity(0.1),
                                    Color.clear
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ),
                            lineWidth: 1
                        )
                }
            )
    }
}

// MARK: - Animated Gradient Background
struct AnimatedGradientBackground: View {
    @State private var animateGradient = false
    let colors: [Color]
    
    init(colors: [Color] = [.enlikoPrimary, .enlikoAccent, .enlikoPrimary]) {
        self.colors = colors
    }
    
    var body: some View {
        LinearGradient(
            colors: colors,
            startPoint: animateGradient ? .topLeading : .bottomLeading,
            endPoint: animateGradient ? .bottomTrailing : .topTrailing
        )
        .ignoresSafeArea()
        .onAppear {
            withAnimation(.easeInOut(duration: 5.0).repeatForever(autoreverses: true)) {
                animateGradient.toggle()
            }
        }
    }
}

// MARK: - Neumorphic Button
struct NeuButton: View {
    let title: String
    let icon: String?
    let action: () -> Void
    var isLoading: Bool = false
    var style: ButtonStyle = .primary
    
    enum ButtonStyle {
        case primary, secondary, success, danger
        
        var gradient: LinearGradient {
            switch self {
            case .primary:
                return LinearGradient(colors: [.enlikoPrimary, .enlikoPrimary.opacity(0.8)], startPoint: .top, endPoint: .bottom)
            case .secondary:
                return LinearGradient(colors: [.enlikoCard, .enlikoSurface], startPoint: .top, endPoint: .bottom)
            case .success:
                return LinearGradient(colors: [.enlikoGreen, .enlikoGreen.opacity(0.8)], startPoint: .top, endPoint: .bottom)
            case .danger:
                return LinearGradient(colors: [.enlikoRed, .enlikoRed.opacity(0.8)], startPoint: .top, endPoint: .bottom)
            }
        }
    }
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                        .scaleEffect(0.9)
                } else {
                    if let icon = icon {
                        Image(systemName: icon)
                            .font(.system(size: 16, weight: .semibold))
                    }
                    Text(title)
                        .font(.system(size: 16, weight: .semibold))
                }
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(style.gradient)
            .clipShape(RoundedRectangle(cornerRadius: 14))
            .shadow(color: style == .primary ? .enlikoPrimary.opacity(0.4) : .clear, radius: 10, y: 5)
        }
        .disabled(isLoading)
        .opacity(isLoading ? 0.7 : 1)
    }
}

// MARK: - Shimmer Loading Effect
struct ShimmerEffect: ViewModifier {
    @State private var phase: CGFloat = 0
    
    func body(content: Content) -> some View {
        content
            .overlay(
                GeometryReader { geometry in
                    LinearGradient(
                        colors: [
                            .clear,
                            .white.opacity(0.3),
                            .clear
                        ],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                    .frame(width: geometry.size.width * 2)
                    .offset(x: phase * geometry.size.width * 2 - geometry.size.width)
                    .mask(content)
                }
            )
            .onAppear {
                withAnimation(.linear(duration: 1.5).repeatForever(autoreverses: false)) {
                    phase = 1
                }
            }
    }
}

extension View {
    func shimmer() -> some View {
        modifier(ShimmerEffect())
    }
}

// MARK: - Skeleton Loading View
struct SkeletonView: View {
    var width: CGFloat? = nil
    var height: CGFloat = 20
    var cornerRadius: CGFloat = 8
    
    var body: some View {
        RoundedRectangle(cornerRadius: cornerRadius)
            .fill(Color.enlikoCard)
            .frame(width: width, height: height)
            .shimmer()
    }
}

// MARK: - Modern Badge
struct ModernBadge: View {
    let text: String
    let color: Color
    var icon: String? = nil
    
    var body: some View {
        HStack(spacing: 4) {
            if let icon = icon {
                Image(systemName: icon)
                    .font(.system(size: 10, weight: .bold))
            }
            Text(text)
                .font(.system(size: 11, weight: .bold))
        }
        .foregroundColor(.white)
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(
            Capsule()
                .fill(color.gradient)
        )
    }
}

// MARK: - Stat Tile
struct StatTile: View {
    let title: String
    let value: String
    let icon: String
    let iconColor: Color
    var trend: Double? = nil
    
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                ZStack {
                    Circle()
                        .fill(iconColor.opacity(0.2))
                        .frame(width: 36, height: 36)
                    
                    Image(systemName: icon)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(iconColor)
                }
                
                Spacer()
                
                if let trend = trend {
                    HStack(spacing: 2) {
                        Image(systemName: trend >= 0 ? "arrow.up.right" : "arrow.down.right")
                            .font(.system(size: 10, weight: .bold))
                        Text("\(abs(trend), specifier: "%.1f")%")
                            .font(.system(size: 11, weight: .semibold))
                    }
                    .foregroundColor(trend >= 0 ? .enlikoGreen : .enlikoRed)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 3)
                    .background(
                        Capsule()
                            .fill((trend >= 0 ? Color.enlikoGreen : Color.enlikoRed).opacity(0.15))
                    )
                }
            }
            
            Text(value)
                .font(.system(size: 22, weight: .bold, design: .rounded))
                .foregroundColor(.white)
            
            Text(title)
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.enlikoTextSecondary)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.enlikoCard)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(Color.enlikoBorder, lineWidth: 1)
                )
        )
    }
}

// MARK: - Glowing Border
struct GlowBorder: ViewModifier {
    let color: Color
    var blur: CGFloat = 10
    
    func body(content: Content) -> some View {
        content
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(color, lineWidth: 2)
                    .blur(radius: blur / 2)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(color.opacity(0.5), lineWidth: 1)
            )
    }
}

extension View {
    func glowBorder(color: Color, blur: CGFloat = 10) -> some View {
        modifier(GlowBorder(color: color, blur: blur))
    }
}

// MARK: - Modern Toggle
struct ModernToggle: View {
    @Binding var isOn: Bool
    let label: String
    var icon: String? = nil
    
    var body: some View {
        HStack {
            if let icon = icon {
                Image(systemName: icon)
                    .font(.system(size: 18))
                    .foregroundColor(.enlikoTextSecondary)
                    .frame(width: 24)
            }
            
            Text(label)
                .font(.system(size: 15, weight: .medium))
                .foregroundColor(.white)
            
            Spacer()
            
            ZStack {
                Capsule()
                    .fill(isOn ? Color.enlikoGreen : Color.enlikoCard)
                    .frame(width: 50, height: 30)
                
                Circle()
                    .fill(.white)
                    .frame(width: 26, height: 26)
                    .offset(x: isOn ? 10 : -10)
                    .shadow(color: .black.opacity(0.2), radius: 2, y: 1)
            }
            .onTapGesture {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    isOn.toggle()
                }
            }
        }
        .padding(.vertical, 12)
        .padding(.horizontal, 16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.enlikoSurface)
        )
    }
}

// MARK: - Progress Ring
struct ProgressRing: View {
    let progress: Double
    let lineWidth: CGFloat
    let gradient: [Color]
    
    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.enlikoCard, lineWidth: lineWidth)
            
            Circle()
                .trim(from: 0, to: min(progress, 1.0))
                .stroke(
                    AngularGradient(colors: gradient, center: .center),
                    style: StrokeStyle(lineWidth: lineWidth, lineCap: .round)
                )
                .rotationEffect(.degrees(-90))
                .animation(.spring(response: 0.8), value: progress)
        }
    }
}

// MARK: - Floating Action Button
struct FloatingActionButton: View {
    let icon: String
    let action: () -> Void
    var color: Color = .enlikoPrimary
    
    var body: some View {
        Button(action: action) {
            ZStack {
                Circle()
                    .fill(color.gradient)
                    .frame(width: 56, height: 56)
                    .shadow(color: color.opacity(0.5), radius: 10, y: 5)
                
                Image(systemName: icon)
                    .font(.system(size: 24, weight: .semibold))
                    .foregroundColor(.white)
            }
        }
    }
}

// MARK: - Preview
#Preview {
    ZStack {
        Color.enlikoBackground.ignoresSafeArea()
        
        VStack(spacing: 20) {
            StatTile(
                title: "Total PnL",
                value: "$1,234.56",
                icon: "chart.line.uptrend.xyaxis",
                iconColor: .enlikoGreen,
                trend: 12.5
            )
            
            NeuButton(title: "Place Order", icon: "plus.circle.fill", action: {}, style: .primary)
            
            ModernBadge(text: "LONG", color: .enlikoGreen, icon: "arrow.up.right")
            
            ModernToggle(isOn: .constant(true), label: "ATR Trailing", icon: "waveform.path")
        }
        .padding()
    }
}
