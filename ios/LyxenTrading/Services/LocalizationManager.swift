//
//  LocalizationManager.swift
//  LyxenTrading
//
//  Manages app localization with 15 supported languages
//  Syncs language preference with server
//

import SwiftUI
import Combine

// MARK: - Supported Languages
enum AppLanguage: String, CaseIterable, Identifiable {
    case en = "en"
    case ru = "ru"
    case uk = "uk"
    case de = "de"
    case es = "es"
    case fr = "fr"
    case it = "it"
    case ja = "ja"
    case zh = "zh"
    case ar = "ar"
    case he = "he"
    case pl = "pl"
    case cs = "cs"
    case lt = "lt"
    case sq = "sq"
    
    var id: String { rawValue }
    
    var displayName: String {
        switch self {
        case .en: return "English"
        case .ru: return "Русский"
        case .uk: return "Українська"
        case .de: return "Deutsch"
        case .es: return "Español"
        case .fr: return "Français"
        case .it: return "Italiano"
        case .ja: return "日本語"
        case .zh: return "中文"
        case .ar: return "العربية"
        case .he: return "עברית"
        case .pl: return "Polski"
        case .cs: return "Čeština"
        case .lt: return "Lietuvių"
        case .sq: return "Shqip"
        }
    }
    
    var flag: String {
        switch self {
        case .en: return "🇺🇸"
        case .ru: return "🇷🇺"
        case .uk: return "🇺🇦"
        case .de: return "🇩🇪"
        case .es: return "🇪🇸"
        case .fr: return "🇫🇷"
        case .it: return "🇮🇹"
        case .ja: return "🇯🇵"
        case .zh: return "🇨🇳"
        case .ar: return "🇸🇦"
        case .he: return "🇮🇱"
        case .pl: return "🇵🇱"
        case .cs: return "🇨🇿"
        case .lt: return "🇱🇹"
        case .sq: return "🇦🇱"
        }
    }
    
    var isRTL: Bool {
        self == .ar || self == .he
    }
}

// MARK: - Localization Manager
class LocalizationManager: ObservableObject {
    static let shared = LocalizationManager()
    
    /// Flag to skip server sync (used when loading from server)
    private var skipNextSync = false
    
    @Published var currentLanguage: AppLanguage {
        didSet {
            saveLanguage()
            loadTranslations()
            
            // Sync with server unless skipped
            if skipNextSync {
                skipNextSync = false
            } else {
                Task {
                    await syncLanguageWithServer()
                }
            }
        }
    }
    
    @Published private(set) var translations: [String: String] = [:]
    @Published private(set) var isLoading = false
    
    private let userDefaultsKey = "appLanguage"
    
    private init() {
        // Load saved language or detect from system
        if let savedLang = UserDefaults.standard.string(forKey: userDefaultsKey),
           let lang = AppLanguage(rawValue: savedLang) {
            currentLanguage = lang
        } else {
            // Detect from system locale
            let systemLang = Locale.current.language.languageCode?.identifier ?? "en"
            currentLanguage = AppLanguage(rawValue: systemLang) ?? .en
        }
        
        loadTranslations()
    }
    
    // MARK: - Public Methods
    
    /// Get localized string for key
    func localized(_ key: String) -> String {
        translations[key] ?? key
    }
    
    /// Get localized string with format arguments
    func localized(_ key: String, _ args: CVarArg...) -> String {
        let format = translations[key] ?? key
        return String(format: format, arguments: args)
    }
    
    /// Set language and trigger updates
    func setLanguage(_ language: AppLanguage) {
        currentLanguage = language
    }
    
    /// Set language without syncing to server (used when loading from server)
    func setLanguageWithoutSync(_ language: AppLanguage) {
        guard language != currentLanguage else { return }
        skipNextSync = true
        currentLanguage = language
    }
    
    // MARK: - Private Methods
    
    private func saveLanguage() {
        UserDefaults.standard.set(currentLanguage.rawValue, forKey: userDefaultsKey)
    }
    
    private func loadTranslations() {
        // Load from bundled translations
        translations = Self.bundledTranslations[currentLanguage] ?? Self.bundledTranslations[.en]!
    }
    
    private func syncLanguageWithServer() async {
        do {
            struct LangResponse: Codable {}
            let _: LangResponse = try await NetworkService.shared.post(
                "/users/language",
                body: ["lang": currentLanguage.rawValue]
            )
            print("✅ Language synced with server: \(currentLanguage.rawValue)")
        } catch {
            print("⚠️ Failed to sync language: \(error.localizedDescription)")
        }
    }
    
    // MARK: - Bundled Translations
    static let bundledTranslations: [AppLanguage: [String: String]] = [
        .en: englishTranslations,
        .ru: russianTranslations,
        .uk: ukrainianTranslations,
        .de: germanTranslations,
        .es: spanishTranslations,
        .fr: frenchTranslations,
        .it: italianTranslations,
        .ja: japaneseTranslations,
        .zh: chineseTranslations,
        .ar: arabicTranslations,
        .he: hebrewTranslations,
        .pl: polishTranslations,
        .cs: czechTranslations,
        .lt: lithuanianTranslations,
        .sq: albanianTranslations,
    ]
    
    // MARK: - English (Reference)
    static let englishTranslations: [String: String] = [
        // Navigation
        "nav_portfolio": "Portfolio",
        "nav_positions": "Positions",
        "nav_trading": "Trading",
        "nav_market": "Market",
        "nav_more": "More",
        "nav_settings": "Settings",
        
        // Settings
        "settings_title": "Settings",
        "settings_account": "Account",
        "settings_trading": "Trading",
        "settings_notifications": "Notifications",
        "settings_app": "App",
        "settings_language": "Language",
        "settings_appearance": "Appearance",
        "settings_about": "About",
        "settings_privacy": "Privacy Policy",
        "settings_terms": "Terms of Service",
        "settings_logout": "Log Out",
        "settings_logout_confirm": "Are you sure you want to log out?",
        "settings_exchange": "Default Exchange",
        "settings_api_keys": "API Keys",
        "settings_leverage": "Default Leverage",
        "settings_risk": "Risk Management",
        
        // Auth
        "auth_login": "Log In",
        "auth_logout": "Log Out",
        "auth_email": "Email",
        "auth_password": "Password",
        "auth_forgot": "Forgot Password?",
        "auth_register": "Create Account",
        "auth_telegram": "Login with Telegram",
        "auth_welcome": "Welcome to Lyxen",
        
        // Portfolio
        "portfolio_title": "Portfolio",
        "portfolio_balance": "Total Balance",
        "portfolio_equity": "Equity",
        "portfolio_available": "Available",
        "portfolio_pnl_today": "Today P&L",
        "portfolio_pnl_week": "Weekly P&L",
        "portfolio_pnl_month": "Monthly P&L",
        "portfolio_no_data": "No portfolio data",
        
        // Positions
        "positions_title": "Positions",
        "positions_open": "Open Positions",
        "positions_closed": "Closed",
        "positions_no_open": "No open positions",
        "positions_close": "Close",
        "positions_close_all": "Close All",
        "positions_entry": "Entry",
        "positions_mark": "Mark",
        "positions_size": "Size",
        "positions_leverage": "Leverage",
        "positions_pnl": "P&L",
        "positions_tp": "Take Profit",
        "positions_sl": "Stop Loss",
        "positions_long": "LONG",
        "positions_short": "SHORT",
        
        // Trading
        "trading_title": "Trading",
        "trading_buy": "Buy / Long",
        "trading_sell": "Sell / Short",
        "trading_market": "Market",
        "trading_limit": "Limit",
        "trading_amount": "Amount",
        "trading_price": "Price",
        "trading_tp": "Take Profit",
        "trading_sl": "Stop Loss",
        "trading_place_order": "Place Order",
        "trading_confirm": "Confirm Order",
        
        // Orders
        "orders_title": "Orders",
        "orders_open": "Open Orders",
        "orders_history": "Order History",
        "orders_no_open": "No open orders",
        "orders_cancel": "Cancel",
        "orders_cancel_all": "Cancel All",
        
        // Market
        "market_title": "Market",
        "market_search": "Search coins...",
        "market_gainers": "Top Gainers",
        "market_losers": "Top Losers",
        "market_volume": "Volume",
        "market_24h": "24h Change",
        
        // Screener
        "screener_title": "Screener",
        "screener_all": "All",
        "screener_gainers": "Gainers",
        "screener_losers": "Losers",
        "screener_filter": "Filter",
        
        // Stats
        "stats_title": "Statistics",
        "stats_total_trades": "Total Trades",
        "stats_win_rate": "Win Rate",
        "stats_total_pnl": "Total P&L",
        "stats_avg_trade": "Avg Trade",
        "stats_best_trade": "Best Trade",
        "stats_worst_trade": "Worst Trade",
        "stats_by_strategy": "By Strategy",
        
        // AI
        "ai_title": "AI Analysis",
        "ai_analyze": "Analyze",
        "ai_sentiment": "Market Sentiment",
        "ai_bullish": "Bullish",
        "ai_bearish": "Bearish",
        "ai_neutral": "Neutral",
        
        // Signals
        "signals_title": "Signals",
        "signals_active": "Active",
        "signals_all": "All Signals",
        "signals_no_active": "No active signals",
        
        // Activity
        "activity_title": "Activity",
        "activity_recent": "Recent Activity",
        "activity_no_recent": "No recent activity",
        
        // Common
        "common_loading": "Loading...",
        "common_error": "Error",
        "common_retry": "Retry",
        "common_cancel": "Cancel",
        "common_confirm": "Confirm",
        "common_save": "Save",
        "common_delete": "Delete",
        "common_edit": "Edit",
        "common_done": "Done",
        "common_back": "Back",
        "common_close": "Close",
        "common_refresh": "Refresh",
        "common_search": "Search",
        "common_filter": "Filter",
        "common_sort": "Sort",
        "common_all": "All",
        "common_none": "None",
        "common_yes": "Yes",
        "common_no": "No",
        "common_ok": "OK",
        
        // Exchanges
        "exchange_bybit": "Bybit",
        "exchange_hyperliquid": "HyperLiquid",
        "exchange_demo": "Demo",
        "exchange_real": "Real",
        "exchange_testnet": "Testnet",
        "exchange_mainnet": "Mainnet",
        
        // Errors
        "error_network": "Network error. Please try again.",
        "error_auth": "Authentication failed.",
        "error_api": "API error. Please check your keys.",
        "error_unknown": "Something went wrong.",
        
        // Premium
        "premium_title": "Premium",
        "premium_upgrade": "Upgrade to Premium",
        "premium_features": "Premium Features",
        "premium_active": "Premium Active",
        
        // Trading Settings
        "trading_settings": "Trading Settings",
        "order_settings": "Order Settings",
        "order_type": "Order Type",
        "market": "Market",
        "limit": "Limit",
        "limit_offset": "Limit Offset",
        "order_type_hint": "Market orders execute immediately. Limit orders can get better prices.",
        "dca_settings": "DCA Settings",
        "dca_enabled": "Enable DCA",
        "dca_level_1": "Level 1 (Add at drawdown %)",
        "dca_level_2": "Level 2 (Add at drawdown %)",
        "dca_hint": "Dollar Cost Averaging adds to position on drawdowns to lower average entry.",
        "spot_trading": "Spot Trading",
        "spot_enabled": "Enable Spot Trading",
        "spot_dca_enabled": "Enable Spot DCA",
        "spot_dca_pct": "DCA Amount %",
        "atr_trailing": "ATR Trailing Stop",
        "use_atr": "Enable ATR Trailing",
        "atr_periods": "ATR Periods",
        "atr_trigger": "Trigger Profit %",
        "atr_step": "Trail Step %",
        "atr_hint": "ATR trailing dynamically adjusts stop-loss as position moves in profit.",
        "exchanges": "Exchanges",
        "not_configured": "Not Configured",
        "exchange_toggle_hint": "Toggle trading on configured exchanges.",
        "save_settings": "Save Settings",
        "settings_saved": "Settings Saved",
        
        // Strategy Settings
        "strategy_settings": "Strategy Settings",
        "enable_long": "Enable Long",
        "enable_short": "Enable Short",
        "entry_percent": "Entry Size %",
        "take_profit": "Take Profit %",
        "stop_loss": "Stop Loss %",
        "leverage": "Leverage",
    ]
    
    // MARK: - Russian
    static let russianTranslations: [String: String] = [
        // Navigation
        "nav_portfolio": "Портфель",
        "nav_positions": "Позиции",
        "nav_trading": "Торговля",
        "nav_market": "Рынок",
        "nav_more": "Ещё",
        "nav_settings": "Настройки",
        
        // Settings
        "settings_title": "Настройки",
        "settings_account": "Аккаунт",
        "settings_trading": "Торговля",
        "settings_notifications": "Уведомления",
        "settings_app": "Приложение",
        "settings_language": "Язык",
        "settings_appearance": "Оформление",
        "settings_about": "О приложении",
        "settings_privacy": "Политика конфиденциальности",
        "settings_terms": "Условия использования",
        "settings_logout": "Выйти",
        "settings_logout_confirm": "Вы уверены, что хотите выйти?",
        "settings_exchange": "Биржа по умолчанию",
        "settings_api_keys": "API ключи",
        "settings_leverage": "Плечо по умолчанию",
        "settings_risk": "Управление рисками",
        
        // Auth
        "auth_login": "Войти",
        "auth_logout": "Выйти",
        "auth_email": "Email",
        "auth_password": "Пароль",
        "auth_forgot": "Забыли пароль?",
        "auth_register": "Создать аккаунт",
        "auth_telegram": "Войти через Telegram",
        "auth_welcome": "Добро пожаловать в Lyxen",
        
        // Portfolio
        "portfolio_title": "Портфель",
        "portfolio_balance": "Общий баланс",
        "portfolio_equity": "Эквити",
        "portfolio_available": "Доступно",
        "portfolio_pnl_today": "PnL за сегодня",
        "portfolio_pnl_week": "PnL за неделю",
        "portfolio_pnl_month": "PnL за месяц",
        "portfolio_no_data": "Нет данных",
        
        // Positions
        "positions_title": "Позиции",
        "positions_open": "Открытые позиции",
        "positions_closed": "Закрытые",
        "positions_no_open": "Нет открытых позиций",
        "positions_close": "Закрыть",
        "positions_close_all": "Закрыть все",
        "positions_entry": "Вход",
        "positions_mark": "Маркировка",
        "positions_size": "Размер",
        "positions_leverage": "Плечо",
        "positions_pnl": "PnL",
        "positions_tp": "Тейк профит",
        "positions_sl": "Стоп лосс",
        "positions_long": "ЛОНГ",
        "positions_short": "ШОРТ",
        
        // Trading
        "trading_title": "Торговля",
        "trading_buy": "Купить / Лонг",
        "trading_sell": "Продать / Шорт",
        "trading_market": "Рынок",
        "trading_limit": "Лимит",
        "trading_amount": "Количество",
        "trading_price": "Цена",
        "trading_tp": "Тейк профит",
        "trading_sl": "Стоп лосс",
        "trading_place_order": "Разместить ордер",
        "trading_confirm": "Подтвердить ордер",
        
        // Orders
        "orders_title": "Ордера",
        "orders_open": "Открытые ордера",
        "orders_history": "История ордеров",
        "orders_no_open": "Нет открытых ордеров",
        "orders_cancel": "Отменить",
        "orders_cancel_all": "Отменить все",
        
        // Market
        "market_title": "Рынок",
        "market_search": "Поиск монет...",
        "market_gainers": "Лидеры роста",
        "market_losers": "Лидеры падения",
        "market_volume": "Объём",
        "market_24h": "Изменение 24ч",
        
        // Screener
        "screener_title": "Скринер",
        "screener_all": "Все",
        "screener_gainers": "Рост",
        "screener_losers": "Падение",
        "screener_filter": "Фильтр",
        
        // Stats
        "stats_title": "Статистика",
        "stats_total_trades": "Всего сделок",
        "stats_win_rate": "Винрейт",
        "stats_total_pnl": "Общий PnL",
        "stats_avg_trade": "Средняя сделка",
        "stats_best_trade": "Лучшая сделка",
        "stats_worst_trade": "Худшая сделка",
        "stats_by_strategy": "По стратегиям",
        
        // AI
        "ai_title": "AI Анализ",
        "ai_analyze": "Анализировать",
        "ai_sentiment": "Настроение рынка",
        "ai_bullish": "Бычий",
        "ai_bearish": "Медвежий",
        "ai_neutral": "Нейтральный",
        
        // Signals
        "signals_title": "Сигналы",
        "signals_active": "Активные",
        "signals_all": "Все сигналы",
        "signals_no_active": "Нет активных сигналов",
        
        // Activity
        "activity_title": "Активность",
        "activity_recent": "Недавняя активность",
        "activity_no_recent": "Нет недавней активности",
        
        // Common
        "common_loading": "Загрузка...",
        "common_error": "Ошибка",
        "common_retry": "Повторить",
        "common_cancel": "Отмена",
        "common_confirm": "Подтвердить",
        "common_save": "Сохранить",
        "common_delete": "Удалить",
        "common_edit": "Редактировать",
        "common_done": "Готово",
        "common_back": "Назад",
        "common_close": "Закрыть",
        "common_refresh": "Обновить",
        "common_search": "Поиск",
        "common_filter": "Фильтр",
        "common_sort": "Сортировка",
        "common_all": "Все",
        "common_none": "Нет",
        "common_yes": "Да",
        "common_no": "Нет",
        "common_ok": "ОК",
        
        // Exchanges
        "exchange_bybit": "Bybit",
        "exchange_hyperliquid": "HyperLiquid",
        "exchange_demo": "Демо",
        "exchange_real": "Реал",
        "exchange_testnet": "Тестнет",
        "exchange_mainnet": "Мейннет",
        
        // Errors
        "error_network": "Ошибка сети. Попробуйте снова.",
        "error_auth": "Ошибка авторизации.",
        "error_api": "Ошибка API. Проверьте ключи.",
        "error_unknown": "Что-то пошло не так.",
        
        // Premium
        "premium_title": "Премиум",
        "premium_upgrade": "Перейти на Премиум",
        "premium_features": "Премиум функции",
        "premium_active": "Премиум активен",
        
        // Trading Settings
        "trading_settings": "Торговые настройки",
        "order_settings": "Настройки ордеров",
        "order_type": "Тип ордера",
        "market": "Маркет",
        "limit": "Лимит",
        "limit_offset": "Отступ лимита",
        "order_type_hint": "Маркет ордера исполняются мгновенно. Лимитные могут получить лучшую цену.",
        "dca_settings": "Настройки DCA",
        "dca_enabled": "Включить DCA",
        "dca_level_1": "Уровень 1 (добор при просадке %)",
        "dca_level_2": "Уровень 2 (добор при просадке %)",
        "dca_hint": "DCA добавляет к позиции при просадках для усреднения входа.",
        "spot_trading": "Спот торговля",
        "spot_enabled": "Включить спот",
        "spot_dca_enabled": "Включить спот DCA",
        "spot_dca_pct": "Объём DCA %",
        "atr_trailing": "ATR трейлинг стоп",
        "use_atr": "Включить ATR трейлинг",
        "atr_periods": "Период ATR",
        "atr_trigger": "Триггер прибыли %",
        "atr_step": "Шаг трейла %",
        "atr_hint": "ATR трейлинг динамически двигает стоп-лосс за ценой в прибыли.",
        "exchanges": "Биржи",
        "not_configured": "Не настроено",
        "exchange_toggle_hint": "Включение/выключение торговли на бирже.",
        "save_settings": "Сохранить",
        "settings_saved": "Настройки сохранены",
        
        // Strategy Settings
        "strategy_settings": "Настройки стратегий",
        "enable_long": "Включить Long",
        "enable_short": "Включить Short",
        "entry_percent": "Размер входа %",
        "take_profit": "Тейк профит %",
        "stop_loss": "Стоп лосс %",
        "leverage": "Плечо",
    ]
    
    // MARK: - Ukrainian
    static let ukrainianTranslations: [String: String] = [
        "nav_portfolio": "Портфель",
        "nav_positions": "Позиції",
        "nav_trading": "Торгівля",
        "nav_market": "Ринок",
        "nav_more": "Ще",
        "nav_settings": "Налаштування",
        "settings_title": "Налаштування",
        "settings_language": "Мова",
        "settings_logout": "Вийти",
        "common_loading": "Завантаження...",
        "common_error": "Помилка",
        "common_cancel": "Скасувати",
        "common_confirm": "Підтвердити",
        "portfolio_title": "Портфель",
        "positions_title": "Позиції",
        "trading_title": "Торгівля",
    ]
    
    // MARK: - German
    static let germanTranslations: [String: String] = [
        "nav_portfolio": "Portfolio",
        "nav_positions": "Positionen",
        "nav_trading": "Handel",
        "nav_market": "Markt",
        "nav_more": "Mehr",
        "nav_settings": "Einstellungen",
        "settings_title": "Einstellungen",
        "settings_language": "Sprache",
        "settings_logout": "Abmelden",
        "common_loading": "Laden...",
        "common_error": "Fehler",
        "common_cancel": "Abbrechen",
        "common_confirm": "Bestätigen",
        "portfolio_title": "Portfolio",
        "positions_title": "Positionen",
        "trading_title": "Handel",
    ]
    
    // MARK: - Spanish
    static let spanishTranslations: [String: String] = [
        "nav_portfolio": "Cartera",
        "nav_positions": "Posiciones",
        "nav_trading": "Trading",
        "nav_market": "Mercado",
        "nav_more": "Más",
        "nav_settings": "Ajustes",
        "settings_title": "Ajustes",
        "settings_language": "Idioma",
        "settings_logout": "Cerrar sesión",
        "common_loading": "Cargando...",
        "common_error": "Error",
        "common_cancel": "Cancelar",
        "common_confirm": "Confirmar",
        "portfolio_title": "Cartera",
        "positions_title": "Posiciones",
        "trading_title": "Trading",
    ]
    
    // MARK: - French
    static let frenchTranslations: [String: String] = [
        "nav_portfolio": "Portefeuille",
        "nav_positions": "Positions",
        "nav_trading": "Trading",
        "nav_market": "Marché",
        "nav_more": "Plus",
        "nav_settings": "Paramètres",
        "settings_title": "Paramètres",
        "settings_language": "Langue",
        "settings_logout": "Déconnexion",
        "common_loading": "Chargement...",
        "common_error": "Erreur",
        "common_cancel": "Annuler",
        "common_confirm": "Confirmer",
        "portfolio_title": "Portefeuille",
        "positions_title": "Positions",
        "trading_title": "Trading",
    ]
    
    // MARK: - Italian
    static let italianTranslations: [String: String] = [
        "nav_portfolio": "Portafoglio",
        "nav_positions": "Posizioni",
        "nav_trading": "Trading",
        "nav_market": "Mercato",
        "nav_more": "Altro",
        "nav_settings": "Impostazioni",
        "settings_title": "Impostazioni",
        "settings_language": "Lingua",
        "settings_logout": "Esci",
        "common_loading": "Caricamento...",
        "common_error": "Errore",
        "common_cancel": "Annulla",
        "common_confirm": "Conferma",
        "portfolio_title": "Portafoglio",
        "positions_title": "Posizioni",
        "trading_title": "Trading",
    ]
    
    // MARK: - Japanese
    static let japaneseTranslations: [String: String] = [
        "nav_portfolio": "ポートフォリオ",
        "nav_positions": "ポジション",
        "nav_trading": "取引",
        "nav_market": "マーケット",
        "nav_more": "その他",
        "nav_settings": "設定",
        "settings_title": "設定",
        "settings_language": "言語",
        "settings_logout": "ログアウト",
        "common_loading": "読み込み中...",
        "common_error": "エラー",
        "common_cancel": "キャンセル",
        "common_confirm": "確認",
        "portfolio_title": "ポートフォリオ",
        "positions_title": "ポジション",
        "trading_title": "取引",
    ]
    
    // MARK: - Chinese
    static let chineseTranslations: [String: String] = [
        "nav_portfolio": "投资组合",
        "nav_positions": "持仓",
        "nav_trading": "交易",
        "nav_market": "市场",
        "nav_more": "更多",
        "nav_settings": "设置",
        "settings_title": "设置",
        "settings_language": "语言",
        "settings_logout": "退出登录",
        "common_loading": "加载中...",
        "common_error": "错误",
        "common_cancel": "取消",
        "common_confirm": "确认",
        "portfolio_title": "投资组合",
        "positions_title": "持仓",
        "trading_title": "交易",
    ]
    
    // MARK: - Arabic
    static let arabicTranslations: [String: String] = [
        "nav_portfolio": "المحفظة",
        "nav_positions": "المراكز",
        "nav_trading": "التداول",
        "nav_market": "السوق",
        "nav_more": "المزيد",
        "nav_settings": "الإعدادات",
        "settings_title": "الإعدادات",
        "settings_language": "اللغة",
        "settings_logout": "تسجيل الخروج",
        "common_loading": "جاري التحميل...",
        "common_error": "خطأ",
        "common_cancel": "إلغاء",
        "common_confirm": "تأكيد",
        "portfolio_title": "المحفظة",
        "positions_title": "المراكز",
        "trading_title": "التداول",
    ]
    
    // MARK: - Hebrew
    static let hebrewTranslations: [String: String] = [
        "nav_portfolio": "תיק השקעות",
        "nav_positions": "פוזיציות",
        "nav_trading": "מסחר",
        "nav_market": "שוק",
        "nav_more": "עוד",
        "nav_settings": "הגדרות",
        "settings_title": "הגדרות",
        "settings_language": "שפה",
        "settings_logout": "התנתק",
        "common_loading": "טוען...",
        "common_error": "שגיאה",
        "common_cancel": "ביטול",
        "common_confirm": "אישור",
        "portfolio_title": "תיק השקעות",
        "positions_title": "פוזיציות",
        "trading_title": "מסחר",
    ]
    
    // MARK: - Polish
    static let polishTranslations: [String: String] = [
        "nav_portfolio": "Portfel",
        "nav_positions": "Pozycje",
        "nav_trading": "Trading",
        "nav_market": "Rynek",
        "nav_more": "Więcej",
        "nav_settings": "Ustawienia",
        "settings_title": "Ustawienia",
        "settings_language": "Język",
        "settings_logout": "Wyloguj",
        "common_loading": "Ładowanie...",
        "common_error": "Błąd",
        "common_cancel": "Anuluj",
        "common_confirm": "Potwierdź",
        "portfolio_title": "Portfel",
        "positions_title": "Pozycje",
        "trading_title": "Trading",
    ]
    
    // MARK: - Czech
    static let czechTranslations: [String: String] = [
        "nav_portfolio": "Portfolio",
        "nav_positions": "Pozice",
        "nav_trading": "Obchodování",
        "nav_market": "Trh",
        "nav_more": "Více",
        "nav_settings": "Nastavení",
        "settings_title": "Nastavení",
        "settings_language": "Jazyk",
        "settings_logout": "Odhlásit",
        "common_loading": "Načítání...",
        "common_error": "Chyba",
        "common_cancel": "Zrušit",
        "common_confirm": "Potvrdit",
        "portfolio_title": "Portfolio",
        "positions_title": "Pozice",
        "trading_title": "Obchodování",
    ]
    
    // MARK: - Lithuanian
    static let lithuanianTranslations: [String: String] = [
        "nav_portfolio": "Portfelis",
        "nav_positions": "Pozicijos",
        "nav_trading": "Prekyba",
        "nav_market": "Rinka",
        "nav_more": "Daugiau",
        "nav_settings": "Nustatymai",
        "settings_title": "Nustatymai",
        "settings_language": "Kalba",
        "settings_logout": "Atsijungti",
        "common_loading": "Kraunama...",
        "common_error": "Klaida",
        "common_cancel": "Atšaukti",
        "common_confirm": "Patvirtinti",
        "portfolio_title": "Portfelis",
        "positions_title": "Pozicijos",
        "trading_title": "Prekyba",
    ]
    
    // MARK: - Albanian
    static let albanianTranslations: [String: String] = [
        "nav_portfolio": "Portofol",
        "nav_positions": "Pozicionet",
        "nav_trading": "Tregtimi",
        "nav_market": "Tregu",
        "nav_more": "Më shumë",
        "nav_settings": "Cilësimet",
        "settings_title": "Cilësimet",
        "settings_language": "Gjuha",
        "settings_logout": "Dilni",
        "common_loading": "Duke u ngarkuar...",
        "common_error": "Gabim",
        "common_cancel": "Anulo",
        "common_confirm": "Konfirmo",
        "portfolio_title": "Portofol",
        "positions_title": "Pozicionet",
        "trading_title": "Tregtimi",
    ]
}

// MARK: - String Extension for Localization
extension String {
    /// Get localized version of this key
    var localized: String {
        LocalizationManager.shared.localized(self)
    }
    
    /// Get localized version with format arguments
    func localized(_ args: CVarArg...) -> String {
        let format = LocalizationManager.shared.translations[self] ?? self
        return String(format: format, arguments: args)
    }
}

// MARK: - View Modifier for RTL Support
struct RTLModifier: ViewModifier {
    @ObservedObject var localization = LocalizationManager.shared
    
    func body(content: Content) -> some View {
        content
            .environment(\.layoutDirection, localization.currentLanguage.isRTL ? .rightToLeft : .leftToRight)
    }
}

extension View {
    func withRTLSupport() -> some View {
        modifier(RTLModifier())
    }
}
