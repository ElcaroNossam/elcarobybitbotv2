//
//  SuperFeatures.swift
//  EnlikoTrading
//
//  🚀 SUPER FEATURES - Premium UX for Enliko Trading
//  =================================================
//  
//  ✨ What's included:
//  1. ConfettiView - Celebration animation for profitable trades
//  2. SoundManager - Trade sounds with haptic feedback
//  3. LivePriceFlash - Real-time price change animations
//  4. QuickTradeGestures - Swipe to Long/Short
//  5. ParticleExplosion - Visual feedback for actions
//  6. FloatingMenu - Quick action radial menu
//  7. CryptoMoodRing - Market sentiment indicator
//  8. TradingMascot - Animated helper character
//  9. AchievementToast - Gamification elements
//  10. VoiceControl - Hands-free trading commands
//

import SwiftUI
import AVFoundation
import CoreHaptics
import Combine

// MARK: - 1. CONFETTI CELEBRATION 🎉

/// Confetti particle
struct ConfettiParticle: Identifiable {
    let id = UUID()
    var position: CGPoint
    var color: Color
    var rotation: Double
    var scale: CGFloat
    var velocity: CGVector
    var angularVelocity: Double
    var lifetime: Double
    var shape: ConfettiShape
    
    enum ConfettiShape: CaseIterable {
        case circle, square, triangle, star
    }
}

/// Confetti View for celebrations
struct ConfettiView: View {
    @State private var particles: [ConfettiParticle] = []
    @State private var timer: Timer?
    let duration: Double
    let particleCount: Int
    
    init(duration: Double = 3.0, particleCount: Int = 150) {
        self.duration = duration
        self.particleCount = particleCount
    }
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                ForEach(particles) { particle in
                    confettiShape(for: particle)
                        .fill(particle.color)
                        .frame(width: 10 * particle.scale, height: 10 * particle.scale)
                        .rotationEffect(.degrees(particle.rotation))
                        .position(particle.position)
                        .opacity(max(0, particle.lifetime))
                }
            }
            .onAppear {
                spawnConfetti(in: geometry.size)
                startAnimation()
            }
            .onDisappear {
                timer?.invalidate()
            }
        }
        .allowsHitTesting(false)
    }
    
    private func confettiShape(for particle: ConfettiParticle) -> AnyShape {
        switch particle.shape {
        case .circle:
            AnyShape(Circle())
        case .square:
            AnyShape(Rectangle())
        case .triangle:
            AnyShape(Triangle())
        case .star:
            AnyShape(Star(corners: 5, smoothness: 0.5))
        }
    }
    
    private func spawnConfetti(in size: CGSize) {
        let colors: [Color] = [.enlikoPrimary, .enlikoGreen, .enlikoYellow, .enlikoAccent, .purple, .orange, .pink, .cyan]
        
        for _ in 0..<particleCount {
            let particle = ConfettiParticle(
                position: CGPoint(x: CGFloat.random(in: 0...size.width), y: -20),
                color: colors.randomElement() ?? .enlikoPrimary,
                rotation: Double.random(in: 0...360),
                scale: CGFloat.random(in: 0.5...1.5),
                velocity: CGVector(
                    dx: Double.random(in: -100...100),
                    dy: Double.random(in: 200...500)
                ),
                angularVelocity: Double.random(in: -360...360),
                lifetime: 1.0,
                shape: ConfettiParticle.ConfettiShape.allCases.randomElement() ?? .circle
            )
            particles.append(particle)
        }
    }
    
    private func startAnimation() {
        timer = Timer.scheduledTimer(withTimeInterval: 1/60, repeats: true) { _ in
            updateParticles()
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + duration) {
            timer?.invalidate()
        }
    }
    
    private func updateParticles() {
        let dt = 1.0 / 60.0
        
        for i in particles.indices.reversed() {
            var particle = particles[i]
            
            // Physics
            particle.velocity.dy += 500 * dt // gravity
            particle.position.x += particle.velocity.dx * dt
            particle.position.y += particle.velocity.dy * dt
            particle.rotation += particle.angularVelocity * dt
            particle.lifetime -= dt / duration
            
            if particle.lifetime <= 0 {
                particles.remove(at: i)
            } else {
                particles[i] = particle
            }
        }
    }
}

// Custom shapes for confetti
struct Triangle: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        path.move(to: CGPoint(x: rect.midX, y: rect.minY))
        path.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
        path.addLine(to: CGPoint(x: rect.minX, y: rect.maxY))
        path.closeSubpath()
        return path
    }
}

struct Star: Shape {
    let corners: Int
    let smoothness: CGFloat
    
    func path(in rect: CGRect) -> Path {
        guard corners >= 2 else { return Path() }
        
        let center = CGPoint(x: rect.width / 2, y: rect.height / 2)
        var currentAngle = -CGFloat.pi / 2
        let angleAdjustment = .pi * 2 / CGFloat(corners * 2)
        let innerX = center.x * smoothness
        let innerY = center.y * smoothness
        
        var path = Path()
        path.move(to: CGPoint(x: center.x * cos(currentAngle), y: center.y * sin(currentAngle)))
        
        var bottomEdge: CGFloat = 0
        for corner in 0..<corners * 2 {
            let sinAngle = sin(currentAngle)
            let cosAngle = cos(currentAngle)
            let bottom: CGFloat
            
            if corner.isMultiple(of: 2) {
                bottom = center.y * sinAngle
                path.addLine(to: CGPoint(x: center.x * cosAngle + center.x, y: bottom + center.y))
            } else {
                bottom = innerY * sinAngle
                path.addLine(to: CGPoint(x: innerX * cosAngle + center.x, y: bottom + center.y))
            }
            
            bottomEdge = max(bottomEdge, bottom)
            currentAngle += angleAdjustment
        }
        
        return path
    }
}

// MARK: - 2. SOUND MANAGER 🔔

/// Trade sound types
enum TradeSound: String {
    case orderPlaced = "order_placed"
    case orderFilled = "order_filled"
    case profitClose = "profit_close"
    case lossClose = "loss_close"
    case alert = "alert"
    case newSignal = "new_signal"
    case priceAlert = "price_alert"
    case connected = "connected"
    case error = "error"
    
    var systemSound: SystemSoundID {
        switch self {
        case .orderPlaced: return 1004
        case .orderFilled: return 1057
        case .profitClose: return 1025
        case .lossClose: return 1073
        case .alert: return 1005
        case .newSignal: return 1007
        case .priceAlert: return 1013
        case .connected: return 1054
        case .error: return 1006
        }
    }
}

/// Sound Manager with haptic feedback
@MainActor
class SoundManager: ObservableObject {
    static let shared = SoundManager()
    
    @Published var isSoundEnabled: Bool = true
    @Published var isHapticEnabled: Bool = true
    @Published var volume: Float = 0.8
    
    private var hapticEngine: CHHapticEngine?
    
    init() {
        loadSettings()
        setupHapticEngine()
    }
    
    private func setupHapticEngine() {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else { return }
        
        do {
            hapticEngine = try CHHapticEngine()
            try hapticEngine?.start()
        } catch {
            print("Haptic engine error: \(error)")
        }
    }
    
    /// Play sound with optional haptic
    func play(_ sound: TradeSound, withHaptic: Bool = true) {
        if isSoundEnabled {
            AudioServicesPlaySystemSound(sound.systemSound)
        }
        
        if withHaptic && isHapticEnabled {
            playHaptic(for: sound)
        }
    }
    
    /// Play custom haptic pattern
    func playHaptic(for sound: TradeSound) {
        let hapticType: HapticType
        
        switch sound {
        case .orderPlaced, .orderFilled:
            hapticType = .medium
        case .profitClose:
            hapticType = .success
        case .lossClose:
            hapticType = .error
        case .alert, .priceAlert:
            hapticType = .warning
        case .newSignal:
            hapticType = .heavy
        case .connected:
            hapticType = .light
        case .error:
            hapticType = .error
        }
        
        HapticManager.shared.perform(hapticType)
    }
    
    /// Play profit celebration with custom pattern
    func playProfitCelebration(pnl: Double) {
        guard let engine = hapticEngine else { return }
        
        do {
            let intensity = CHHapticEventParameter(parameterID: .hapticIntensity, value: min(1.0, Float(abs(pnl) / 100)))
            let sharpness = CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.5)
            
            var events: [CHHapticEvent] = []
            
            // Create celebration pattern
            for i in 0..<3 {
                let event = CHHapticEvent(
                    eventType: .hapticTransient,
                    parameters: [intensity, sharpness],
                    relativeTime: TimeInterval(i) * 0.2
                )
                events.append(event)
            }
            
            let pattern = try CHHapticPattern(events: events, parameters: [])
            let player = try engine.makePlayer(with: pattern)
            try player.start(atTime: 0)
        } catch {
            print("Haptic celebration error: \(error)")
        }
        
        if isSoundEnabled {
            AudioServicesPlaySystemSound(pnl >= 0 ? TradeSound.profitClose.systemSound : TradeSound.lossClose.systemSound)
        }
    }
    
    func saveSettings() {
        UserDefaults.standard.set(isSoundEnabled, forKey: "sound_enabled")
        UserDefaults.standard.set(isHapticEnabled, forKey: "haptic_enabled")
        UserDefaults.standard.set(volume, forKey: "sound_volume")
    }
    
    private func loadSettings() {
        isSoundEnabled = UserDefaults.standard.object(forKey: "sound_enabled") as? Bool ?? true
        isHapticEnabled = UserDefaults.standard.object(forKey: "haptic_enabled") as? Bool ?? true
        volume = UserDefaults.standard.object(forKey: "sound_volume") as? Float ?? 0.8
    }
}

// MARK: - 3. LIVE PRICE FLASH ⚡

/// Animated price display with flash effect
struct LivePriceFlashView: View {
    let price: Double
    let previousPrice: Double
    let format: String
    let font: Font
    
    @State private var flashOpacity: Double = 0
    @State private var displayPrice: Double
    
    init(price: Double, previousPrice: Double, format: String = "%.2f", font: Font = .title2.bold()) {
        self.price = price
        self.previousPrice = previousPrice
        self.format = format
        self.font = font
        self._displayPrice = State(initialValue: previousPrice)
    }
    
    var priceColor: Color {
        if price > previousPrice { return .enlikoGreen }
        if price < previousPrice { return .enlikoRed }
        return .primary
    }
    
    var flashColor: Color {
        if price > previousPrice { return .green }
        if price < previousPrice { return .red }
        return .clear
    }
    
    var body: some View {
        Text("$\(String(format: format, displayPrice))")
            .font(font)
            .foregroundColor(priceColor)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(
                RoundedRectangle(cornerRadius: 6)
                    .fill(flashColor.opacity(flashOpacity))
            )
            .onChange(of: price) { _, newPrice in
                // Flash animation
                withAnimation(.easeIn(duration: 0.1)) {
                    flashOpacity = 0.4
                }
                
                // Count up/down animation
                withAnimation(.easeOut(duration: 0.3)) {
                    displayPrice = newPrice
                }
                
                // Fade flash
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                    withAnimation(.easeOut(duration: 0.3)) {
                        flashOpacity = 0
                    }
                }
                
                // Haptic
                HapticManager.shared.priceChange()
            }
    }
}

// MARK: - 4. QUICK TRADE GESTURES 👆

/// Swipe gesture detector for trading
struct QuickTradeGestureView: View {
    let onLongSwipe: () -> Void
    let onShortSwipe: () -> Void
    
    @State private var offset: CGFloat = 0
    @State private var showingLongHint = false
    @State private var showingShortHint = false
    
    let threshold: CGFloat = 100
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                // Background hints
                HStack {
                    // Long hint (left side when swiping right)
                    Image(systemName: "arrow.up.right.circle.fill")
                        .font(.system(size: 40))
                        .foregroundColor(.enlikoGreen)
                        .opacity(showingLongHint ? 1 : 0)
                        .scaleEffect(showingLongHint ? 1.2 : 0.8)
                    
                    Spacer()
                    
                    // Short hint (right side when swiping left)
                    Image(systemName: "arrow.down.right.circle.fill")
                        .font(.system(size: 40))
                        .foregroundColor(.enlikoRed)
                        .opacity(showingShortHint ? 1 : 0)
                        .scaleEffect(showingShortHint ? 1.2 : 0.8)
                }
                .padding(.horizontal, 40)
                
                // Gesture area indicator
                RoundedRectangle(cornerRadius: 20)
                    .stroke(
                        LinearGradient(
                            colors: swipeColor,
                            startPoint: .leading,
                            endPoint: .trailing
                        ),
                        lineWidth: 2
                    )
                    .background(
                        RoundedRectangle(cornerRadius: 20)
                            .fill(swipeBackground)
                    )
                    .offset(x: offset)
                    .gesture(
                        DragGesture()
                            .onChanged { value in
                                offset = value.translation.width
                                
                                withAnimation(.spring(response: 0.3)) {
                                    showingLongHint = offset > threshold * 0.5
                                    showingShortHint = offset < -threshold * 0.5
                                }
                                
                                if abs(offset) > threshold * 0.5 {
                                    HapticManager.shared.perform(.light)
                                }
                            }
                            .onEnded { value in
                                if value.translation.width > threshold {
                                    // Long triggered
                                    HapticManager.shared.perform(.success)
                                    onLongSwipe()
                                } else if value.translation.width < -threshold {
                                    // Short triggered
                                    HapticManager.shared.perform(.success)
                                    onShortSwipe()
                                }
                                
                                withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
                                    offset = 0
                                    showingLongHint = false
                                    showingShortHint = false
                                }
                            }
                    )
            }
        }
    }
    
    var swipeColor: [Color] {
        if offset > threshold * 0.3 {
            return [.enlikoGreen, .enlikoGreen.opacity(0.5)]
        } else if offset < -threshold * 0.3 {
            return [.enlikoRed.opacity(0.5), .enlikoRed]
        }
        return [.enlikoBorder, .enlikoBorder]
    }
    
    var swipeBackground: Color {
        if offset > threshold * 0.5 {
            return .enlikoGreen.opacity(0.1)
        } else if offset < -threshold * 0.5 {
            return .enlikoRed.opacity(0.1)
        }
        return .clear
    }
}

// MARK: - 5. PARTICLE EXPLOSION 💥

struct ParticleExplosionView: View {
    @Binding var isActive: Bool
    let color: Color
    let particleCount: Int
    
    @State private var particles: [(offset: CGSize, opacity: Double)] = []
    
    init(isActive: Binding<Bool>, color: Color = .enlikoPrimary, particleCount: Int = 20) {
        self._isActive = isActive
        self.color = color
        self.particleCount = particleCount
    }
    
    var body: some View {
        ZStack {
            ForEach(0..<particles.count, id: \.self) { index in
                Circle()
                    .fill(color)
                    .frame(width: 8, height: 8)
                    .offset(particles[index].offset)
                    .opacity(particles[index].opacity)
            }
        }
        .onChange(of: isActive) { _, newValue in
            if newValue {
                explode()
            }
        }
    }
    
    private func explode() {
        particles = (0..<particleCount).map { _ in
            (offset: .zero, opacity: 1.0)
        }
        
        for i in 0..<particleCount {
            let angle = Double(i) / Double(particleCount) * 2 * .pi
            let distance = CGFloat.random(in: 50...120)
            
            withAnimation(.easeOut(duration: 0.8)) {
                particles[i].offset = CGSize(
                    width: cos(angle) * distance,
                    height: sin(angle) * distance
                )
                particles[i].opacity = 0
            }
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
            particles = []
            isActive = false
        }
    }
}

// MARK: - 6. FLOATING RADIAL MENU 🎯

struct FloatingRadialMenu: View {
    @Binding var isOpen: Bool
    let items: [RadialMenuItem]
    
    @State private var rotation: Double = 0
    
    struct RadialMenuItem {
        let icon: String
        let color: Color
        let action: () -> Void
    }
    
    var body: some View {
        ZStack {
            // Background overlay
            if isOpen {
                Color.black.opacity(0.5)
                    .ignoresSafeArea()
                    .onTapGesture {
                        withAnimation(.spring(response: 0.4)) {
                            isOpen = false
                        }
                    }
            }
            
            // Menu items
            ForEach(0..<items.count, id: \.self) { index in
                let angle = angleFor(index: index)
                let offset = offsetFor(angle: angle)
                
                Button(action: {
                    items[index].action()
                    HapticManager.shared.perform(.medium)
                    withAnimation(.spring(response: 0.4)) {
                        isOpen = false
                    }
                }) {
                    ZStack {
                        Circle()
                            .fill(items[index].color.gradient)
                            .frame(width: 50, height: 50)
                            .shadow(color: items[index].color.opacity(0.5), radius: 10, y: 5)
                        
                        Image(systemName: items[index].icon)
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.white)
                    }
                }
                .offset(isOpen ? offset : .zero)
                .opacity(isOpen ? 1 : 0)
                .scaleEffect(isOpen ? 1 : 0.5)
                .rotationEffect(.degrees(isOpen ? 0 : 180))
            }
            
            // Center button
            Button(action: {
                withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
                    isOpen.toggle()
                }
                HapticManager.shared.perform(.selection)
            }) {
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [.enlikoPrimary, .enlikoAccent],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 60, height: 60)
                        .shadow(color: .enlikoPrimary.opacity(0.5), radius: 15, y: 5)
                    
                    Image(systemName: "plus")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                        .rotationEffect(.degrees(isOpen ? 45 : 0))
                }
            }
        }
        .animation(.spring(response: 0.4, dampingFraction: 0.6), value: isOpen)
    }
    
    private func angleFor(index: Int) -> Double {
        let count = Double(items.count)
        let spread = 180.0 // degrees
        let startAngle = 270.0 - spread / 2
        return startAngle + (spread / (count - 1)) * Double(index)
    }
    
    private func offsetFor(angle: Double) -> CGSize {
        let radius: CGFloat = 100
        let radians = angle * .pi / 180
        return CGSize(
            width: cos(radians) * radius,
            height: sin(radians) * radius
        )
    }
}

// MARK: - 7. CRYPTO MOOD RING 🔮

struct CryptoMoodRing: View {
    let fearGreedIndex: Int // 0-100
    
    var moodColor: Color {
        switch fearGreedIndex {
        case 0..<25: return .red
        case 25..<45: return .orange
        case 45..<55: return .yellow
        case 55..<75: return .lime
        default: return .green
        }
    }
    
    var moodText: String {
        switch fearGreedIndex {
        case 0..<25: return "Extreme Fear"
        case 25..<45: return "Fear"
        case 45..<55: return "Neutral"
        case 55..<75: return "Greed"
        default: return "Extreme Greed"
        }
    }
    
    var body: some View {
        VStack(spacing: 8) {
            ZStack {
                // Background ring
                Circle()
                    .stroke(Color.enlikoCard, lineWidth: 12)
                    .frame(width: 80, height: 80)
                
                // Mood ring
                Circle()
                    .trim(from: 0, to: CGFloat(fearGreedIndex) / 100)
                    .stroke(
                        AngularGradient(
                            colors: [.red, .orange, .yellow, .green],
                            center: .center
                        ),
                        style: StrokeStyle(lineWidth: 12, lineCap: .round)
                    )
                    .frame(width: 80, height: 80)
                    .rotationEffect(.degrees(-90))
                
                // Value
                Text("\(fearGreedIndex)")
                    .font(.system(size: 24, weight: .bold, design: .rounded))
                    .foregroundColor(moodColor)
            }
            
            Text(moodText)
                .font(.caption.bold())
                .foregroundColor(moodColor)
        }
    }
}

extension Color {
    static let lime = Color(red: 0.5, green: 1, blue: 0)
}

// MARK: - 8. ACHIEVEMENT TOAST 🏆

struct AchievementToast: View {
    let title: String
    let subtitle: String
    let icon: String
    let color: Color
    @Binding var isShowing: Bool
    
    @State private var offset: CGFloat = -200
    @State private var opacity: Double = 0
    
    var body: some View {
        HStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(color.gradient)
                    .frame(width: 50, height: 50)
                
                Image(systemName: icon)
                    .font(.system(size: 22, weight: .bold))
                    .foregroundColor(.white)
            }
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.headline)
                    .foregroundColor(.white)
                
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundColor(.enlikoTextSecondary)
            }
            
            Spacer()
            
            // Stars animation
            HStack(spacing: 4) {
                ForEach(0..<3) { i in
                    Image(systemName: "star.fill")
                        .foregroundColor(.yellow)
                        .font(.system(size: 12))
                        .scaleEffect(isShowing ? 1 : 0)
                        .animation(.spring(response: 0.4).delay(Double(i) * 0.1), value: isShowing)
                }
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.enlikoCard)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(color.opacity(0.5), lineWidth: 2)
                )
                .shadow(color: color.opacity(0.3), radius: 20, y: 10)
        )
        .padding(.horizontal)
        .offset(y: offset)
        .opacity(opacity)
        .onChange(of: isShowing) { _, newValue in
            if newValue {
                show()
            }
        }
        .onAppear {
            if isShowing {
                show()
            }
        }
    }
    
    private func show() {
        HapticManager.shared.perform(.success)
        SoundManager.shared.play(.profitClose)
        
        withAnimation(.spring(response: 0.6, dampingFraction: 0.7)) {
            offset = 0
            opacity = 1
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            withAnimation(.easeIn(duration: 0.3)) {
                offset = -200
                opacity = 0
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                isShowing = false
            }
        }
    }
}

// MARK: - 9. PULL TO REFRESH CUSTOM

struct PullToRefreshView<Content: View>: View {
    let content: Content
    let onRefresh: () async -> Void
    
    @State private var isRefreshing = false
    @State private var pullProgress: CGFloat = 0
    
    init(@ViewBuilder content: () -> Content, onRefresh: @escaping () async -> Void) {
        self.content = content()
        self.onRefresh = onRefresh
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                // Refresh indicator
                ZStack {
                    Circle()
                        .stroke(Color.enlikoCard, lineWidth: 3)
                        .frame(width: 30, height: 30)
                    
                    if isRefreshing {
                        ProgressView()
                            .tint(.enlikoPrimary)
                    } else {
                        Circle()
                            .trim(from: 0, to: pullProgress)
                            .stroke(Color.enlikoPrimary, style: StrokeStyle(lineWidth: 3, lineCap: .round))
                            .frame(width: 30, height: 30)
                            .rotationEffect(.degrees(-90))
                    }
                }
                .frame(height: pullProgress > 0 || isRefreshing ? 50 : 0)
                .opacity(pullProgress > 0 || isRefreshing ? 1 : 0)
                
                content
            }
        }
        .refreshable {
            isRefreshing = true
            HapticManager.shared.perform(.light)
            await onRefresh()
            isRefreshing = false
        }
    }
}

// MARK: - 10. TRADING MASCOT 🤖

struct TradingMascotView: View {
    @State private var eyePosition: CGPoint = .zero
    @State private var isBlinking = false
    @State private var expression: MascotExpression = .neutral
    
    enum MascotExpression {
        case neutral, happy, worried, excited
    }
    
    var body: some View {
        ZStack {
            // Body
            Capsule()
                .fill(
                    LinearGradient(
                        colors: [.enlikoPrimary, .enlikoAccent],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .frame(width: 80, height: 100)
            
            // Face
            VStack(spacing: 8) {
                // Eyes
                HStack(spacing: 20) {
                    Eye(isBlinking: isBlinking, lookAt: eyePosition)
                    Eye(isBlinking: isBlinking, lookAt: eyePosition)
                }
                
                // Mouth
                mouthView
            }
            .offset(y: -10)
        }
        .onAppear {
            startBlinking()
            startLooking()
        }
    }
    
    @ViewBuilder
    var mouthView: some View {
        switch expression {
        case .neutral:
            Capsule()
                .fill(.white)
                .frame(width: 20, height: 8)
        case .happy:
            HappyMouth()
                .stroke(.white, lineWidth: 3)
                .frame(width: 25, height: 12)
        case .worried:
            WorriedMouth()
                .stroke(.white, lineWidth: 3)
                .frame(width: 25, height: 12)
        case .excited:
            Circle()
                .fill(.white)
                .frame(width: 20, height: 20)
        }
    }
    
    private func startBlinking() {
        Timer.scheduledTimer(withTimeInterval: Double.random(in: 2...5), repeats: true) { _ in
            withAnimation(.easeInOut(duration: 0.1)) {
                isBlinking = true
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                withAnimation(.easeInOut(duration: 0.1)) {
                    isBlinking = false
                }
            }
        }
    }
    
    private func startLooking() {
        Timer.scheduledTimer(withTimeInterval: Double.random(in: 1...3), repeats: true) { _ in
            withAnimation(.easeInOut(duration: 0.3)) {
                eyePosition = CGPoint(
                    x: CGFloat.random(in: -5...5),
                    y: CGFloat.random(in: -3...3)
                )
            }
        }
    }
    
    func setExpression(_ expr: MascotExpression) {
        withAnimation(.spring(response: 0.3)) {
            expression = expr
        }
    }
}

struct Eye: View {
    let isBlinking: Bool
    let lookAt: CGPoint
    
    var body: some View {
        ZStack {
            // White
            Circle()
                .fill(.white)
                .frame(width: 18, height: isBlinking ? 2 : 18)
            
            // Pupil
            if !isBlinking {
                Circle()
                    .fill(.black)
                    .frame(width: 8, height: 8)
                    .offset(x: lookAt.x, y: lookAt.y)
            }
        }
    }
}

struct HappyMouth: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        path.move(to: CGPoint(x: 0, y: rect.midY))
        path.addQuadCurve(
            to: CGPoint(x: rect.maxX, y: rect.midY),
            control: CGPoint(x: rect.midX, y: rect.maxY)
        )
        return path
    }
}

struct WorriedMouth: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        path.move(to: CGPoint(x: 0, y: rect.maxY))
        path.addQuadCurve(
            to: CGPoint(x: rect.maxX, y: rect.maxY),
            control: CGPoint(x: rect.midX, y: rect.minY)
        )
        return path
    }
}

// MARK: - PREVIEW

#Preview("Super Features") {
    ZStack {
        Color.enlikoBackground.ignoresSafeArea()
        
        VStack(spacing: 30) {
            // Mood Ring
            CryptoMoodRing(fearGreedIndex: 65)
            
            // Live Price
            LivePriceFlashView(price: 45234.50, previousPrice: 45200.00)
            
            // Achievement (static preview)
            HStack(spacing: 16) {
                ZStack {
                    Circle()
                        .fill(Color.enlikoGreen.gradient)
                        .frame(width: 50, height: 50)
                    
                    Image(systemName: "star.fill")
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading) {
                    Text("First Trade!")
                        .font(.headline)
                    Text("+$50.00 profit")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
            }
            .padding()
            .background(Color.enlikoCard)
            .cornerRadius(16)
            
            // Mascot
            TradingMascotView()
        }
    }
}
