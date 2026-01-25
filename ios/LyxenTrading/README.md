# Lyxen Trading iOS App

Профессиональное iOS приложение для торговой платформы Lyxen. Полная интеграция с бекендом, поддержка Bybit и HyperLiquid бирж.

## 📱 Возможности

### Торговля
- ✅ Открытие Long/Short позиций
- ✅ Market и Limit ордера
- ✅ Настройка Take Profit / Stop Loss
- ✅ Управление левериджем (1x - 100x)
- ✅ Просмотр и закрытие позиций
- ✅ Отмена ордеров

### Портфолио
- ✅ Баланс в реальном времени
- ✅ Нереализованный PnL
- ✅ Торговая статистика (Win Rate, Total PnL)
- ✅ История сделок с фильтрацией

### Стратегии
- ✅ Управление AI стратегиями (OI, Scryptomera, Scalper, Elcaro)
- ✅ Маркетплейс стратегий
- ✅ Бэктестинг с визуализацией результатов

### Настройки
- ✅ API ключи Bybit (Demo/Real)
- ✅ API ключи HyperLiquid (Testnet/Mainnet)
- ✅ Риск-менеджмент (Max positions, Default TP/SL)
- ✅ Уведомления

## 🛠 Технологии

- **SwiftUI** - Декларативный UI
- **Combine** - Реактивное программирование
- **URLSession** - Сетевые запросы
- **Keychain** - Безопасное хранение токенов
- **WebSocket** - Реальтайм данные

## 📋 Требования

- iOS 16.0+
- Xcode 15.0+
- Swift 5.9+

## 🚀 Установка

### Вариант 1: Xcode Project

1. Откройте Xcode
2. File → New → Project
3. Выберите "App" под iOS
4. Настройки проекта:
   - Product Name: `LyxenTrading`
   - Bundle Identifier: `io.lyxen.trading`
   - Interface: SwiftUI
   - Language: Swift
5. Скопируйте все файлы из этой папки в проект

### Вариант 2: Xcode Gen (Рекомендуется)

```bash
# Установите XcodeGen
brew install xcodegen

# Создайте project.yml в папке ios/LyxenTrading
cd ios/LyxenTrading

# Создайте Xcode проект
xcodegen generate
```

**project.yml:**
```yaml
name: LyxenTrading
options:
  bundleIdPrefix: io.lyxen
  deploymentTarget:
    iOS: "16.0"
  xcodeVersion: "15.0"
  generateEmptyDirectories: true

targets:
  LyxenTrading:
    type: application
    platform: iOS
    sources:
      - path: .
        excludes:
          - "*.md"
          - Package.swift
          - project.yml
    settings:
      base:
        INFOPLIST_FILE: Info.plist
        PRODUCT_BUNDLE_IDENTIFIER: io.lyxen.trading
        MARKETING_VERSION: "1.0.0"
        CURRENT_PROJECT_VERSION: 1
        DEVELOPMENT_TEAM: YOUR_TEAM_ID
        CODE_SIGN_STYLE: Automatic
```

### Вариант 3: Swift Package

```bash
cd ios/LyxenTrading
swift build
```

## 📁 Структура проекта

```
LyxenTrading/
├── App/
│   ├── LyxenTradingApp.swift    # Entry point
│   ├── AppState.swift            # Global state
│   └── Config.swift              # API configuration
├── Models/
│   ├── Models.swift              # Data models
│   └── AuthModels.swift          # Auth models
├── Services/
│   ├── NetworkService.swift      # HTTP client
│   ├── AuthManager.swift         # Authentication
│   ├── TradingService.swift      # Trading operations
│   ├── WebSocketService.swift    # Real-time data
│   └── StrategyService.swift     # Strategies
├── ViewModels/
│   └── ViewModels.swift          # Observable ViewModels
├── Views/
│   ├── MainTabView.swift         # Tab navigation
│   ├── Auth/
│   │   └── LoginView.swift       # Login screen
│   ├── Portfolio/
│   │   ├── PortfolioView.swift   # Main portfolio
│   │   ├── PositionsView.swift   # Positions list
│   │   └── TradeHistoryView.swift
│   ├── Trading/
│   │   ├── TradingView.swift     # Order placement
│   │   ├── SymbolPickerView.swift
│   │   └── MarketView.swift      # Market screener
│   ├── Strategies/
│   │   └── StrategiesView.swift  # Strategy management
│   ├── Settings/
│   │   └── SettingsView.swift    # Settings screens
│   └── Components/
│       └── LoadingView.swift     # Reusable components
├── Extensions/
│   └── Color+Extensions.swift    # Theme colors
├── Resources/
│   └── Assets.xcassets/          # App icons, colors
├── Info.plist                    # App configuration
└── Package.swift                 # SPM manifest
```

## ⚙️ Конфигурация

### API URL

Измените URL в `App/Config.swift`:

```swift
struct Config {
    // Production
    static let apiBaseURL = "https://your-cloudflare-url.trycloudflare.com/api/v1"
    static let wsBaseURL = "wss://your-cloudflare-url.trycloudflare.com/ws"
    
    // Development
    #if DEBUG
    static let apiBaseURL = "http://localhost:8765/api/v1"
    #endif
}
```

### Кастомизация темы

Цвета в `Extensions/Color+Extensions.swift`:

```swift
extension Color {
    static let lyxenPrimary = Color(hex: "#6C5CE7")
    static let lyxenGreen = Color(hex: "#00C853")
    static let lyxenRed = Color(hex: "#FF5252")
    // ...
}
```

## 🔐 Безопасность

- JWT токены хранятся в iOS Keychain
- Никаких API ключей в коде
- HTTPS обязателен для production
- Биометрическая авторизация (планируется)

## 📝 TODO

- [ ] Face ID / Touch ID авторизация
- [ ] Push уведомления (APNS)
- [ ] Виджеты для Home Screen
- [ ] Apple Watch app
- [ ] Charts с TradingView
- [ ] Локализация (RU, EN, ES, ZH)

## 🤝 Разработка

```bash
# Clone репозитория
git clone https://github.com/your-repo/lyxen-trading.git

# Откройте в Xcode
open LyxenTrading.xcodeproj

# Выберите симулятор или устройство
# Cmd + R для запуска
```

## 📄 Лицензия

Proprietary - Lyxen Trading Platform © 2026
