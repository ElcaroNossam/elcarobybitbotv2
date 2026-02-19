import Foundation
import LocalAuthentication
import SwiftUI
import Combine

/**
 * Modern Features Module for Enliko iOS App
 * =================================================
 * 
 * Топовые фичи современной мобильной разработки 2024-2026:
 * 
 * 1. Biometric Authentication - Face ID / Touch ID
 * 2. Haptic Feedback - тактильная обратная связь
 * 3. Advanced Animations - продвинутые анимации
 * 4. Skeleton Loading - скелетонная загрузка
 * 5. Pull-to-Refresh - обновление свайпом
 * 6. Offline-First - работа без интернета
 * 7. Adaptive Layout - адаптивная верстка
 * 8. Widget Support - виджеты для Home Screen
 * 9. App Shortcuts - быстрые действия
 * 10. Live Activities - динамические уведомления
 */

// MARK: - 1. BIOMETRIC AUTHENTICATION

/// Результат биометрической аутентификации
enum BiometricResult {
    case success
    case cancelled
    case failed(Error)
    case notAvailable
    case notEnrolled
}

/// Типы биометрии
enum BiometricType {
    case none
    case touchID
    case faceID
    case opticID // visionOS
    
    var displayName: String {
        switch self {
        case .none: return "Not Available"
        case .touchID: return "Touch ID"
        case .faceID: return "Face ID"
        case .opticID: return "Optic ID"
        }
    }
    
    var systemImageName: String {
        switch self {
        case .none: return "xmark.circle"
        case .touchID: return "touchid"
        case .faceID: return "faceid"
        case .opticID: return "opticid"
        }
    }
}

/// Менеджер биометрической аутентификации
@MainActor
class BiometricAuthManager: ObservableObject {
    static let shared = BiometricAuthManager()
    
    @Published var isAvailable: Bool = false
    @Published var isEnabled: Bool = false
    @Published var biometricType: BiometricType = .none
    @Published var lastAuthTime: Date? = nil
    
    private let context = LAContext()
    private let authTimeout: TimeInterval = 5 * 60 // 5 минут
    
    init() {
        checkAvailability()
        loadSettings()
    }
    
    /// Проверить доступность биометрии
    func checkAvailability() {
        var error: NSError?
        isAvailable = context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
        
        switch context.biometryType {
        case .none:
            biometricType = .none
        case .touchID:
            biometricType = .touchID
        case .faceID:
            biometricType = .faceID
        case .opticID:
            biometricType = .opticID
        @unknown default:
            biometricType = .none
        }
    }
    
    /// Аутентификация
    func authenticate(reason: String = "Authenticate to access Enliko") async -> BiometricResult {
        guard isAvailable else {
            return .notAvailable
        }
        
        do {
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
            
            if success {
                await MainActor.run {
                    self.lastAuthTime = Date()
                }
                return .success
            } else {
                return .failed(NSError(domain: "BiometricAuth", code: -1, userInfo: nil))
            }
        } catch let error as LAError {
            switch error.code {
            case .userCancel, .appCancel, .systemCancel:
                return .cancelled
            case .biometryNotEnrolled:
                return .notEnrolled
            case .biometryNotAvailable:
                return .notAvailable
            default:
                return .failed(error)
            }
        } catch {
            return .failed(error)
        }
    }
    
    /// Проверить нужна ли повторная аутентификация
    func needsReauthentication() -> Bool {
        guard let lastAuth = lastAuthTime else { return true }
        return Date().timeIntervalSince(lastAuth) > authTimeout
    }
    
    /// Включить/выключить биометрию
    func setBiometricEnabled(_ enabled: Bool) {
        isEnabled = enabled
        UserDefaults.standard.set(enabled, forKey: "biometric_enabled")
    }
    
    private func loadSettings() {
        isEnabled = UserDefaults.standard.bool(forKey: "biometric_enabled")
    }
}

// MARK: - 2. HAPTIC FEEDBACK

/// Типы тактильной обратной связи
enum HapticType {
    case light
    case medium
    case heavy
    case success
    case error
    case warning
    case selection
    case impact(UIImpactFeedbackGenerator.FeedbackStyle)
}

/// Менеджер хаптики
class HapticManager {
    static let shared = HapticManager()
    
    private init() {}
    
    /// Выполнить тактильную обратную связь
    func perform(_ type: HapticType) {
        switch type {
        case .light:
            let generator = UIImpactFeedbackGenerator(style: .light)
            generator.impactOccurred()
            
        case .medium:
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
            
        case .heavy:
            let generator = UIImpactFeedbackGenerator(style: .heavy)
            generator.impactOccurred()
            
        case .success:
            let generator = UINotificationFeedbackGenerator()
            generator.notificationOccurred(.success)
            
        case .error:
            let generator = UINotificationFeedbackGenerator()
            generator.notificationOccurred(.error)
            
        case .warning:
            let generator = UINotificationFeedbackGenerator()
            generator.notificationOccurred(.warning)
            
        case .selection:
            let generator = UISelectionFeedbackGenerator()
            generator.selectionChanged()
            
        case .impact(let style):
            let generator = UIImpactFeedbackGenerator(style: style)
            generator.impactOccurred()
        }
    }
    
    /// Хаптика для успешной сделки
    func tradeSuccess() {
        perform(.success)
    }
    
    /// Хаптика для ошибки
    func tradeError() {
        perform(.error)
    }
    
    /// Хаптика для нового сигнала
    func newSignal() {
        perform(.medium)
    }
    
    /// Хаптика для изменения цены
    func priceChange() {
        perform(.light)
    }
}

// MARK: - 3. ADVANCED ANIMATIONS

/// Пульсирующая анимация
struct PulsingView<Content: View>: View {
    let content: Content
    let pulseFraction: CGFloat
    
    @State private var isPulsing = false
    
    init(pulseFraction: CGFloat = 1.1, @ViewBuilder content: () -> Content) {
        self.pulseFraction = pulseFraction
        self.content = content()
    }
    
    var body: some View {
        content
            .scaleEffect(isPulsing ? pulseFraction : 1.0)
            .animation(
                Animation.easeInOut(duration: 1.0)
                    .repeatForever(autoreverses: true),
                value: isPulsing
            )
            .onAppear {
                isPulsing = true
            }
    }
}

/// Shake анимация для ошибок
struct ShakeEffect: GeometryEffect {
    var animatableData: CGFloat
    
    func effectValue(size: CGSize) -> ProjectionTransform {
        let translation = sin(animatableData * .pi * 10) * 10
        return ProjectionTransform(CGAffineTransform(translationX: translation, y: 0))
    }
}

extension View {
    func shake(trigger: Bool) -> some View {
        modifier(ShakeModifier(trigger: trigger))
    }
}

struct ShakeModifier: ViewModifier {
    let trigger: Bool
    @State private var shake: CGFloat = 0
    
    func body(content: Content) -> some View {
        content
            .modifier(ShakeEffect(animatableData: shake))
            .onChange(of: trigger) { _, newValue in
                if newValue {
                    withAnimation(.default) {
                        shake = 1
                    }
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                        shake = 0
                    }
                }
            }
    }
}

/// Анимация появления снизу
struct SlideInFromBottom: ViewModifier {
    let isVisible: Bool
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    
    func body(content: Content) -> some View {
        GeometryReader { geometry in
            content
                .offset(y: isVisible ? 0 : geometry.size.height)
                .opacity(isVisible ? 1 : 0)
                .animation(.spring(response: 0.5, dampingFraction: 0.7), value: isVisible)
        }
    }
}

/// Анимированный счётчик
struct AnimatedCounter: Animatable, View {
    var value: Double
    var animatableData: Double {
        get { value }
        set { value = newValue }
    }
    
    let prefix: String
    let suffix: String
    let format: String
    let font: Font
    let color: Color
    
    init(value: Double, prefix: String = "", suffix: String = "", format: String = "%.2f", font: Font = .body, color: Color = .primary) {
        self.value = value
        self.prefix = prefix
        self.suffix = suffix
        self.format = format
        self.font = font
        self.color = color
    }
    
    var body: some View {
        Text("\(prefix)\(String(format: format, value))\(suffix)")
            .font(font)
            .foregroundColor(color)
    }
}

// MARK: - 4. SHIMMER EFFECT

/// Shimmer эффект для загрузки
struct ShimmerView: View {
    @State private var phase: CGFloat = 0
    
    let width: CGFloat
    let height: CGFloat
    let cornerRadius: CGFloat
    
    init(width: CGFloat = .infinity, height: CGFloat = 20, cornerRadius: CGFloat = 4) {
        self.width = width
        self.height = height
        self.cornerRadius = cornerRadius
    }
    
    var body: some View {
        RoundedRectangle(cornerRadius: cornerRadius)
            .fill(
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color.gray.opacity(0.3),
                        Color.gray.opacity(0.5),
                        Color.gray.opacity(0.3)
                    ]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .frame(maxWidth: width == .infinity ? nil : width, minHeight: height, maxHeight: height)
            .mask(
                Rectangle()
                    .fill(
                        LinearGradient(
                            gradient: Gradient(colors: [.clear, .white, .clear]),
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .rotationEffect(.degrees(70))
                    .offset(x: phase)
            )
            .onAppear {
                withAnimation(Animation.linear(duration: 1.5).repeatForever(autoreverses: false)) {
                    phase = 350
                }
            }
    }
}

/// Skeleton карточка позиции
struct PositionSkeletonCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                ShimmerView(width: 80, height: 24, cornerRadius: 4)
                Spacer()
                ShimmerView(width: 60, height: 20, cornerRadius: 4)
            }
            
            HStack {
                ShimmerView(width: 100, height: 16, cornerRadius: 4)
                Spacer()
                ShimmerView(width: 80, height: 16, cornerRadius: 4)
            }
            
            HStack {
                ShimmerView(width: 120, height: 16, cornerRadius: 4)
                Spacer()
                ShimmerView(width: 60, height: 16, cornerRadius: 4)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

// MARK: - 5. LOADING STATES

/// Состояние загрузки
enum LoadingState<T> {
    case idle
    case loading
    case success(T)
    case error(Error)
    case progress(Double) // 0.0 - 1.0
    
    var isLoading: Bool {
        switch self {
        case .loading, .progress: return true
        default: return false
        }
    }
    
    var isSuccess: Bool {
        if case .success = self { return true }
        return false
    }
    
    var isError: Bool {
        if case .error = self { return true }
        return false
    }
    
    var data: T? {
        if case .success(let data) = self { return data }
        return nil
    }
}

// MARK: - 6. OFFLINE-FIRST

/// Состояние подключения
enum ConnectionState {
    case connected
    case disconnected
    case reconnecting
}

/// Кеш данных для offline
struct OfflineCache<T: Codable>: Codable {
    let data: T
    let timestamp: Date
    
    var isValid: Bool {
        Date().timeIntervalSince(timestamp) < 5 * 60 // 5 минут
    }
}

/// Менеджер оффлайн данных
class OfflineDataManager {
    static let shared = OfflineDataManager()
    
    private let userDefaults = UserDefaults.standard
    
    func save<T: Codable>(_ data: T, forKey key: String) {
        let cache = OfflineCache(data: data, timestamp: Date())
        if let encoded = try? JSONEncoder().encode(cache) {
            userDefaults.set(encoded, forKey: "offline_\(key)")
        }
    }
    
    func load<T: Codable>(forKey key: String, type: T.Type) -> T? {
        guard let data = userDefaults.data(forKey: "offline_\(key)"),
              let cache = try? JSONDecoder().decode(OfflineCache<T>.self, from: data),
              cache.isValid else {
            return nil
        }
        return cache.data
    }
    
    func clear(forKey key: String) {
        userDefaults.removeObject(forKey: "offline_\(key)")
    }
}

// MARK: - 7. ADAPTIVE LAYOUT

/// Типы устройств
enum DeviceType {
    case phoneCompact  // iPhone SE
    case phoneMedium   // iPhone
    case phoneExpanded // iPhone Pro Max
    case tablet        // iPad
    
    static func current(for width: CGFloat) -> DeviceType {
        switch width {
        case ..<375: return .phoneCompact
        case 375..<430: return .phoneMedium
        case 430..<768: return .phoneExpanded
        default: return .tablet
        }
    }
    
    static var current: DeviceType {
        // Default to phoneMedium, use GeometryReader in views for accurate detection
        return .phoneMedium
    }
}

/// Адаптивные размеры
struct AdaptiveSizes {
    static var cardPadding: CGFloat {
        switch DeviceType.current {
        case .phoneCompact: return 12
        case .phoneMedium: return 16
        case .phoneExpanded: return 20
        case .tablet: return 24
        }
    }
    
    static var fontSize: CGFloat {
        switch DeviceType.current {
        case .phoneCompact: return 14
        case .phoneMedium: return 16
        case .phoneExpanded: return 17
        case .tablet: return 18
        }
    }
    
    static var gridColumns: Int {
        switch DeviceType.current {
        case .phoneCompact, .phoneMedium, .phoneExpanded: return 1
        case .tablet: return 2
        }
    }
}

// MARK: - 8. PRICE CHANGE ANIMATION

/// Цвет изменения цены
struct PriceChangeColor {
    static func forChange(_ current: Double, _ previous: Double) -> Color {
        if current > previous {
            return Color.green
        } else if current < previous {
            return Color.red
        }
        return Color.primary
    }
}

/// Анимированное отображение цены
struct AnimatedPriceView: View {
    let price: Double
    let previousPrice: Double
    
    @State private var displayedPrice: Double
    @State private var flashColor: Color = .clear
    
    init(price: Double, previousPrice: Double) {
        self.price = price
        self.previousPrice = previousPrice
        self._displayedPrice = State(initialValue: previousPrice)
    }
    
    var body: some View {
        Text(String(format: "%.2f", displayedPrice))
            .foregroundColor(PriceChangeColor.forChange(price, previousPrice))
            .background(flashColor)
            .onChange(of: price) { _, newValue in
                withAnimation(.easeInOut(duration: 0.3)) {
                    displayedPrice = newValue
                    flashColor = PriceChangeColor.forChange(newValue, previousPrice).opacity(0.3)
                }
                
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                    withAnimation {
                        flashColor = .clear
                    }
                }
            }
    }
}

// MARK: - 9. TRADING CELEBRATION

/// Эффект празднования успешной сделки
struct TradeCelebrationView: View {
    @Binding var isShowing: Bool
    let pnl: Double
    
    @State private var scale: CGFloat = 0
    @State private var opacity: Double = 0
    
    var body: some View {
        if isShowing {
            VStack(spacing: 20) {
                Image(systemName: "checkmark.circle.fill")
                    .font(.system(size: 80))
                    .foregroundColor(.green)
                
                Text("Trade Closed!")
                    .font(.title)
                    .fontWeight(.bold)
                
                Text(String(format: "%+.2f USDT", pnl))
                    .font(.title2)
                    .foregroundColor(pnl >= 0 ? .green : .red)
            }
            .scaleEffect(scale)
            .opacity(opacity)
            .onAppear {
                HapticManager.shared.tradeSuccess()
                
                withAnimation(.spring(response: 0.5, dampingFraction: 0.6)) {
                    scale = 1
                    opacity = 1
                }
                
                DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                    withAnimation {
                        scale = 0.5
                        opacity = 0
                    }
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        isShowing = false
                    }
                }
            }
        }
    }
}

// MARK: - 10. VIEW MODIFIERS

extension View {
    /// Добавить пульсирующую анимацию
    func pulsing(fraction: CGFloat = 1.1) -> some View {
        PulsingView(pulseFraction: fraction) { self }
    }
    
    /// Skeleton loading
    func skeleton(isLoading: Bool) -> some View {
        Group {
            if isLoading {
                self.redacted(reason: .placeholder)
            } else {
                self
            }
        }
    }
    
    /// Slide in from bottom
    func slideInFromBottom(isVisible: Bool) -> some View {
        modifier(SlideInFromBottom(isVisible: isVisible))
    }
}
