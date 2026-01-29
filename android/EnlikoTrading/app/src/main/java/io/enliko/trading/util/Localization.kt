package io.enliko.trading.util

import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.remember
import androidx.compose.ui.text.intl.Locale
import io.enliko.trading.BuildConfig

// App name from BuildConfig (set via environment variable)
private val APP_NAME = BuildConfig.APP_NAME

enum class AppLanguage(
    val code: String,
    val displayName: String,
    val flag: String,
    val isRtl: Boolean = false
) {
    ENGLISH("en", "English", "🇬🇧"),
    RUSSIAN("ru", "Русский", "🇷🇺"),
    UKRAINIAN("uk", "Українська", "🇺🇦"),
    GERMAN("de", "Deutsch", "🇩🇪"),
    SPANISH("es", "Español", "🇪🇸"),
    FRENCH("fr", "Français", "🇫🇷"),
    ITALIAN("it", "Italiano", "🇮🇹"),
    JAPANESE("ja", "日本語", "🇯🇵"),
    CHINESE("zh", "中文", "🇨🇳"),
    ARABIC("ar", "العربية", "🇸🇦", isRtl = true),
    HEBREW("he", "עברית", "🇮🇱", isRtl = true),
    POLISH("pl", "Polski", "🇵🇱"),
    CZECH("cs", "Čeština", "🇨🇿"),
    LITHUANIAN("lt", "Lietuvių", "🇱🇹"),
    ALBANIAN("sq", "Shqip", "🇦🇱");

    companion object {
        fun fromCode(code: String): AppLanguage {
            return entries.find { it.code == code } ?: ENGLISH
        }
    }
}

val LocalStrings = compositionLocalOf<Strings> { Strings.English }

@Composable
fun ProvideStrings(
    language: AppLanguage,
    content: @Composable () -> Unit
) {
    val strings: Strings = remember(language) {
        when (language) {
            AppLanguage.ENGLISH -> Strings.English
            AppLanguage.RUSSIAN -> Strings.Russian
            AppLanguage.UKRAINIAN -> Strings.Ukrainian
            AppLanguage.GERMAN -> Strings.German
            AppLanguage.SPANISH -> Strings.Spanish
            AppLanguage.FRENCH -> Strings.French
            AppLanguage.ITALIAN -> Strings.Italian
            AppLanguage.JAPANESE -> Strings.Japanese
            AppLanguage.CHINESE -> Strings.Chinese
            AppLanguage.ARABIC -> Strings.Arabic
            AppLanguage.HEBREW -> Strings.Hebrew
            AppLanguage.POLISH -> Strings.Polish
            AppLanguage.CZECH -> Strings.Czech
            AppLanguage.LITHUANIAN -> Strings.Lithuanian
            AppLanguage.ALBANIAN -> Strings.Albanian
        }
    }
    CompositionLocalProvider(LocalStrings provides strings) {
        content()
    }
}

interface Strings {
    // App
    val appName: String
    
    // Navigation
    val portfolio: String
    val trading: String
    val market: String
    val settings: String
    val signals: String
    val screener: String
    val ai: String
    val activity: String
    
    // Auth
    val login: String
    val register: String
    val email: String
    val password: String
    val forgotPassword: String
    val dontHaveAccount: String
    val alreadyHaveAccount: String
    val logout: String
    
    // Portfolio
    val balance: String
    val positions: String
    val openPositions: String
    val noPositions: String
    val unrealizedPnl: String
    val availableBalance: String
    val totalEquity: String
    val marginUsed: String
    val todayPnl: String
    val weekPnl: String
    
    // Positions
    val entry: String
    val size: String
    val leverage: String
    val pnl: String
    val close: String
    val closeAll: String
    val confirmClose: String
    
    // Trading
    val buy: String
    val sell: String
    val long: String
    val short: String
    val marketOrder: String
    val limit: String
    val stopLoss: String
    val takeProfit: String
    val quantity: String
    val price: String
    val placeOrder: String
    
    // Signals
    val allSignals: String
    val longSignals: String
    val shortSignals: String
    val noSignals: String
    val all: String
    val long_text: String
    val short_text: String
    
    // Screener
    val cryptoScreener: String
    val searchCoins: String
    val volume: String
    val change24h: String
    val oiChange: String
    
    // Settings
    val language: String
    val exchange: String
    val accountType: String
    val demo: String
    val real: String
    val testnet: String
    val mainnet: String
    val apiKeys: String
    val notifications: String
    val theme: String
    val darkTheme: String
    val lightTheme: String
    val systemTheme: String
    val strategies: String
    val premium: String
    
    // Linked Accounts (Unified Auth)
    val linkedAccounts: String
    val linkTelegram: String
    val linkEmail: String
    val telegramLinked: String
    val emailLinked: String
    val notLinked: String
    val notVerified: String
    val verified: String
    
    // AI
    val aiAssistant: String
    val askAnything: String
    val typeMessage: String
    
    // Activity
    val recentActivity: String
    val settingsChanges: String
    val noActivity: String
    
    // Common
    val loading: String
    val error: String
    val retry: String
    val cancel: String
    val confirm: String
    val save: String
    val delete: String
    val refresh: String
    val back: String
    val next: String
    val done: String
    val success: String
    val failed: String
    val enabled: String
    val disabled: String
    val on: String
    val off: String
    
    // Stats
    val tradingStats: String
    val totalTrades: String
    val winRate: String
    val wins: String
    val losses: String
    val avgPnl: String
    val bestTrade: String
    val worstTrade: String
    
    // Disclaimer - Legal Compliance
    val disclaimerTitle: String
    val disclaimerIntro: String
    val disclaimerNotFinancialAdvice: String
    val disclaimerRiskOfLoss: String
    val disclaimerPastPerformance: String
    val disclaimerUserResponsibility: String
    val disclaimerEducationalOnly: String
    val disclaimerRiskWarningTitle: String
    val disclaimerRiskWarningText: String
    val disclaimerAcceptBtn: String
    val disclaimerDeclineBtn: String
    val disclaimerTermsAgreement: String
    val disclaimerAcceptedMsg: String
    val disclaimerDeclinedMsg: String
    
    /**
     * Operator to access strings by key for dynamic lookup
     * Falls back to key if not found
     */
    operator fun get(key: String): String? {
        return when (key) {
            "disclaimer_title" -> disclaimerTitle
            "disclaimer_intro" -> disclaimerIntro
            "disclaimer_not_financial_advice" -> disclaimerNotFinancialAdvice
            "disclaimer_risk_of_loss" -> disclaimerRiskOfLoss
            "disclaimer_past_performance" -> disclaimerPastPerformance
            "disclaimer_user_responsibility" -> disclaimerUserResponsibility
            "disclaimer_educational_only" -> disclaimerEducationalOnly
            "disclaimer_risk_warning_title" -> disclaimerRiskWarningTitle
            "disclaimer_risk_warning_text" -> disclaimerRiskWarningText
            "disclaimer_accept_btn" -> disclaimerAcceptBtn
            "disclaimer_decline_btn" -> disclaimerDeclineBtn
            "disclaimer_terms_agreement" -> disclaimerTermsAgreement
            "disclaimer_accepted_msg" -> disclaimerAcceptedMsg
            "disclaimer_declined_msg" -> disclaimerDeclinedMsg
            else -> null
        }
    }
    
    object English : Strings {
        override val appName = "$APP_NAME Trading"
        override val portfolio = "Portfolio"
        override val trading = "Trading"
        override val market = "Market"
        override val settings = "Settings"
        override val signals = "Signals"
        override val screener = "Screener"
        override val ai = "AI"
        override val activity = "Activity"
        override val login = "Login"
        override val register = "Register"
        override val email = "Email"
        override val password = "Password"
        override val forgotPassword = "Forgot Password?"
        override val dontHaveAccount = "Don't have an account?"
        override val alreadyHaveAccount = "Already have an account?"
        override val logout = "Logout"
        override val balance = "Balance"
        override val positions = "Positions"
        override val openPositions = "Open Positions"
        override val noPositions = "No open positions"
        override val unrealizedPnl = "Unrealized PnL"
        override val availableBalance = "Available"
        override val totalEquity = "Total Equity"
        override val marginUsed = "Margin Used"
        override val todayPnl = "Today PnL"
        override val weekPnl = "Week PnL"
        override val entry = "Entry"
        override val size = "Size"
        override val leverage = "Leverage"
        override val pnl = "PnL"
        override val close = "Close"
        override val closeAll = "Close All"
        override val confirmClose = "Confirm close position?"
        override val buy = "Buy"
        override val sell = "Sell"
        override val long = "Long"
        override val short = "Short"
        override val marketOrder = "Market"
        override val limit = "Limit"
        override val stopLoss = "Stop Loss"
        override val takeProfit = "Take Profit"
        override val quantity = "Quantity"
        override val price = "Price"
        override val placeOrder = "Place Order"
        override val allSignals = "All"
        override val longSignals = "Long"
        override val shortSignals = "Short"
        override val noSignals = "No signals"
        override val all = "All"
        override val long_text = "Long"
        override val short_text = "Short"
        override val cryptoScreener = "Crypto Screener"
        override val searchCoins = "Search coins..."
        override val volume = "Volume"
        override val change24h = "24h Change"
        override val oiChange = "OI Change"
        override val language = "Language"
        override val exchange = "Exchange"
        override val accountType = "Account Type"
        override val demo = "Demo"
        override val real = "Real"
        override val testnet = "Testnet"
        override val mainnet = "Mainnet"
        override val apiKeys = "API Keys"
        override val notifications = "Notifications"
        override val theme = "Theme"
        override val darkTheme = "Dark"
        override val lightTheme = "Light"
        override val systemTheme = "System"
        override val strategies = "Strategies"
        override val premium = "Premium"
        
        // Linked Accounts (Unified Auth)
        override val linkedAccounts = "Linked Accounts"
        override val linkTelegram = "Link Telegram"
        override val linkEmail = "Link Email"
        override val telegramLinked = "Telegram Linked"
        override val emailLinked = "Email Linked"
        override val notLinked = "Not Linked"
        override val notVerified = "Not Verified"
        override val verified = "Verified"
        
        override val aiAssistant = "AI Assistant"
        override val askAnything = "Ask anything about trading..."
        override val typeMessage = "Type a message..."
        override val recentActivity = "Recent Activity"
        override val settingsChanges = "Settings Changes"
        override val noActivity = "No recent activity"
        override val loading = "Loading..."
        override val error = "Error"
        override val retry = "Retry"
        override val cancel = "Cancel"
        override val confirm = "Confirm"
        override val save = "Save"
        override val delete = "Delete"
        override val refresh = "Refresh"
        override val back = "Back"
        override val next = "Next"
        override val done = "Done"
        override val success = "Success"
        override val failed = "Failed"
        override val enabled = "Enabled"
        override val disabled = "Disabled"
        override val on = "ON"
        override val off = "OFF"
        override val tradingStats = "Trading Statistics"
        override val totalTrades = "Total Trades"
        override val winRate = "Win Rate"
        override val wins = "Wins"
        override val losses = "Losses"
        override val avgPnl = "Avg PnL"
        override val bestTrade = "Best Trade"
        override val worstTrade = "Worst Trade"
        // Disclaimer
        override val disclaimerTitle = "⚠️ Important Disclaimer"
        override val disclaimerIntro = "Enliko is an educational and analytical tool for cryptocurrency markets."
        override val disclaimerNotFinancialAdvice = "This is NOT financial advice"
        override val disclaimerRiskOfLoss = "Trading involves substantial risk of loss"
        override val disclaimerPastPerformance = "Past performance does not guarantee future results"
        override val disclaimerUserResponsibility = "You are solely responsible for your trading decisions"
        override val disclaimerEducationalOnly = "This tool is for educational purposes only"
        override val disclaimerRiskWarningTitle = "RISK WARNING"
        override val disclaimerRiskWarningText = "Trading cryptocurrencies is highly speculative. You may lose some or all of your investment. Only trade with funds you can afford to lose."
        override val disclaimerAcceptBtn = "✅ I Understand & Accept"
        override val disclaimerDeclineBtn = "❌ I Decline"
        override val disclaimerTermsAgreement = "By accepting, you agree to our Terms of Service and Privacy Policy."
        override val disclaimerAcceptedMsg = "Thank you for accepting the disclaimer."
        override val disclaimerDeclinedMsg = "You must accept the disclaimer to use Enliko."
    }
    
    object Russian : Strings {
        override val appName = "$APP_NAME Trading"
        override val portfolio = "Портфель"
        override val trading = "Торговля"
        override val market = "Рынок"
        override val settings = "Настройки"
        override val signals = "Сигналы"
        override val screener = "Скринер"
        override val ai = "ИИ"
        override val activity = "Активность"
        override val login = "Войти"
        override val register = "Регистрация"
        override val email = "Email"
        override val password = "Пароль"
        override val forgotPassword = "Забыли пароль?"
        override val dontHaveAccount = "Нет аккаунта?"
        override val alreadyHaveAccount = "Уже есть аккаунт?"
        override val logout = "Выйти"
        override val balance = "Баланс"
        override val positions = "Позиции"
        override val openPositions = "Открытые позиции"
        override val noPositions = "Нет открытых позиций"
        override val unrealizedPnl = "Нереализованный PnL"
        override val availableBalance = "Доступно"
        override val totalEquity = "Общий капитал"
        override val marginUsed = "Маржа"
        override val todayPnl = "PnL за сегодня"
        override val weekPnl = "PnL за неделю"
        override val entry = "Вход"
        override val size = "Размер"
        override val leverage = "Плечо"
        override val pnl = "PnL"
        override val close = "Закрыть"
        override val closeAll = "Закрыть все"
        override val confirmClose = "Подтвердить закрытие позиции?"
        override val buy = "Купить"
        override val sell = "Продать"
        override val long = "Лонг"
        override val short = "Шорт"
        override val marketOrder = "Рыночный"
        override val limit = "Лимит"
        override val stopLoss = "Стоп-лосс"
        override val takeProfit = "Тейк-профит"
        override val quantity = "Количество"
        override val price = "Цена"
        override val placeOrder = "Разместить ордер"
        override val allSignals = "Все"
        override val longSignals = "Лонг"
        override val shortSignals = "Шорт"
        override val noSignals = "Нет сигналов"
        override val all = "Все"
        override val long_text = "Лонг"
        override val short_text = "Шорт"
        override val cryptoScreener = "Крипто скринер"
        override val searchCoins = "Поиск монет..."
        override val volume = "Объём"
        override val change24h = "Изменение 24ч"
        override val oiChange = "Изменение OI"
        override val language = "Язык"
        override val exchange = "Биржа"
        override val accountType = "Тип аккаунта"
        override val demo = "Демо"
        override val real = "Реальный"
        override val testnet = "Тестнет"
        override val mainnet = "Мейннет"
        override val apiKeys = "API ключи"
        override val notifications = "Уведомления"
        override val theme = "Тема"
        override val darkTheme = "Тёмная"
        override val lightTheme = "Светлая"
        override val systemTheme = "Системная"
        override val strategies = "Стратегии"
        override val premium = "Премиум"
        
        // Linked Accounts
        override val linkedAccounts = "Связанные аккаунты"
        override val linkTelegram = "Привязать Telegram"
        override val linkEmail = "Привязать Email"
        override val telegramLinked = "Telegram привязан"
        override val emailLinked = "Email привязан"
        override val notLinked = "Не привязан"
        override val notVerified = "Не подтверждён"
        override val verified = "Подтверждён"
        override val aiAssistant = "ИИ Ассистент"
        override val askAnything = "Спросите о трейдинге..."
        override val typeMessage = "Введите сообщение..."
        override val recentActivity = "Недавняя активность"
        override val settingsChanges = "Изменения настроек"
        override val noActivity = "Нет активности"
        override val loading = "Загрузка..."
        override val error = "Ошибка"
        override val retry = "Повторить"
        override val cancel = "Отмена"
        override val confirm = "Подтвердить"
        override val save = "Сохранить"
        override val delete = "Удалить"
        override val refresh = "Обновить"
        override val back = "Назад"
        override val next = "Далее"
        override val done = "Готово"
        override val success = "Успешно"
        override val failed = "Ошибка"
        override val enabled = "Включено"
        override val disabled = "Выключено"
        override val on = "ВКЛ"
        override val off = "ВЫКЛ"
        override val tradingStats = "Статистика торговли"
        override val totalTrades = "Всего сделок"
        override val winRate = "Винрейт"
        override val wins = "Прибыльных"
        override val losses = "Убыточных"
        override val avgPnl = "Средний PnL"
        override val bestTrade = "Лучшая сделка"
        override val worstTrade = "Худшая сделка"
        // Disclaimer
        override val disclaimerTitle = "⚠️ Важное предупреждение"
        override val disclaimerIntro = "Enliko — это образовательный и аналитический инструмент для криптовалютных рынков."
        override val disclaimerNotFinancialAdvice = "Это НЕ является финансовой консультацией"
        override val disclaimerRiskOfLoss = "Торговля связана со значительным риском потерь"
        override val disclaimerPastPerformance = "Прошлые результаты не гарантируют будущих"
        override val disclaimerUserResponsibility = "Вы несёте полную ответственность за свои решения"
        override val disclaimerEducationalOnly = "Только для образовательных целей"
        override val disclaimerRiskWarningTitle = "ПРЕДУПРЕЖДЕНИЕ О РИСКАХ"
        override val disclaimerRiskWarningText = "Торговля криптовалютами высоко спекулятивна. Вы можете потерять часть или все свои инвестиции. Торгуйте только теми средствами, которые готовы потерять."
        override val disclaimerAcceptBtn = "✅ Понимаю и принимаю"
        override val disclaimerDeclineBtn = "❌ Отклоняю"
        override val disclaimerTermsAgreement = "Принимая, вы соглашаетесь с Условиями использования и Политикой конфиденциальности."
        override val disclaimerAcceptedMsg = "Спасибо за принятие предупреждения."
        override val disclaimerDeclinedMsg = "Для использования Enliko необходимо принять предупреждение."
    }
    
    object Ukrainian : Strings {
        override val appName = "$APP_NAME Trading"
        override val portfolio = "Портфель"
        override val trading = "Торгівля"
        override val market = "Ринок"
        override val settings = "Налаштування"
        override val signals = "Сигнали"
        override val screener = "Скринер"
        override val ai = "ШІ"
        override val activity = "Активність"
        override val login = "Увійти"
        override val register = "Реєстрація"
        override val email = "Email"
        override val password = "Пароль"
        override val forgotPassword = "Забули пароль?"
        override val dontHaveAccount = "Немає акаунту?"
        override val alreadyHaveAccount = "Вже є акаунт?"
        override val logout = "Вийти"
        override val balance = "Баланс"
        override val positions = "Позиції"
        override val openPositions = "Відкриті позиції"
        override val noPositions = "Немає відкритих позицій"
        override val unrealizedPnl = "Нереалізований PnL"
        override val availableBalance = "Доступно"
        override val totalEquity = "Загальний капітал"
        override val marginUsed = "Маржа"
        override val todayPnl = "PnL за сьогодні"
        override val weekPnl = "PnL за тиждень"
        override val entry = "Вхід"
        override val size = "Розмір"
        override val leverage = "Плече"
        override val pnl = "PnL"
        override val close = "Закрити"
        override val closeAll = "Закрити все"
        override val confirmClose = "Підтвердити закриття позиції?"
        override val buy = "Купити"
        override val sell = "Продати"
        override val long = "Лонг"
        override val short = "Шорт"
        override val marketOrder = "Ринковий"
        override val limit = "Ліміт"
        override val stopLoss = "Стоп-лос"
        override val takeProfit = "Тейк-профіт"
        override val quantity = "Кількість"
        override val price = "Ціна"
        override val placeOrder = "Розмістити ордер"
        override val allSignals = "Всі"
        override val longSignals = "Лонг"
        override val shortSignals = "Шорт"
        override val noSignals = "Немає сигналів"
        override val all = "Всі"
        override val long_text = "Лонг"
        override val short_text = "Шорт"
        override val cryptoScreener = "Крипто скринер"
        override val searchCoins = "Пошук монет..."
        override val volume = "Об'єм"
        override val change24h = "Зміна 24г"
        override val oiChange = "Зміна OI"
        override val language = "Мова"
        override val exchange = "Біржа"
        override val accountType = "Тип акаунту"
        override val demo = "Демо"
        override val real = "Реальний"
        override val testnet = "Тестнет"
        override val mainnet = "Мейннет"
        override val apiKeys = "API ключі"
        override val notifications = "Сповіщення"
        override val theme = "Тема"
        override val darkTheme = "Темна"
        override val lightTheme = "Світла"
        override val systemTheme = "Системна"
        override val strategies = "Стратегії"
        override val premium = "Преміум"
        
        // Linked Accounts
        override val linkedAccounts = "Пов'язані акаунти"
        override val linkTelegram = "Прив'язати Telegram"
        override val linkEmail = "Прив'язати Email"
        override val telegramLinked = "Telegram прив'язано"
        override val emailLinked = "Email прив'язано"
        override val notLinked = "Не прив'язано"
        override val notVerified = "Не підтверджено"
        override val verified = "Підтверджено"
        override val aiAssistant = "ШІ Асистент"
        override val askAnything = "Запитайте про трейдинг..."
        override val typeMessage = "Введіть повідомлення..."
        override val recentActivity = "Нещодавня активність"
        override val settingsChanges = "Зміни налаштувань"
        override val noActivity = "Немає активності"
        override val loading = "Завантаження..."
        override val error = "Помилка"
        override val retry = "Повторити"
        override val cancel = "Скасувати"
        override val confirm = "Підтвердити"
        override val save = "Зберегти"
        override val delete = "Видалити"
        override val refresh = "Оновити"
        override val back = "Назад"
        override val next = "Далі"
        override val done = "Готово"
        override val success = "Успішно"
        override val failed = "Помилка"
        override val enabled = "Увімкнено"
        override val disabled = "Вимкнено"
        override val on = "УВІМК"
        override val off = "ВИМК"
        override val tradingStats = "Статистика торгівлі"
        override val totalTrades = "Всього угод"
        override val winRate = "Вінрейт"
        override val wins = "Прибуткових"
        override val losses = "Збиткових"
        override val avgPnl = "Середній PnL"
        override val bestTrade = "Найкраща угода"
        override val worstTrade = "Найгірша угода"
        // Disclaimer
        override val disclaimerTitle = "⚠️ Важливе попередження"
        override val disclaimerIntro = "Enliko — це освітній та аналітичний інструмент для криптовалютних ринків."
        override val disclaimerNotFinancialAdvice = "Це НЕ є фінансовою консультацією"
        override val disclaimerRiskOfLoss = "Торгівля пов'язана зі значним ризиком втрат"
        override val disclaimerPastPerformance = "Минулі результати не гарантують майбутніх"
        override val disclaimerUserResponsibility = "Ви несете повну відповідальність за свої рішення"
        override val disclaimerEducationalOnly = "Лише для освітніх цілей"
        override val disclaimerRiskWarningTitle = "ПОПЕРЕДЖЕННЯ ПРО РИЗИКИ"
        override val disclaimerRiskWarningText = "Торгівля криптовалютами є високо спекулятивною. Ви можете втратити частину або всі свої інвестиції. Торгуйте лише тими коштами, які готові втратити."
        override val disclaimerAcceptBtn = "✅ Розумію та приймаю"
        override val disclaimerDeclineBtn = "❌ Відхиляю"
        override val disclaimerTermsAgreement = "Приймаючи, ви погоджуєтесь з Умовами використання та Політикою конфіденційності."
        override val disclaimerAcceptedMsg = "Дякуємо за прийняття попередження."
        override val disclaimerDeclinedMsg = "Для використання Enliko необхідно прийняти попередження."
    }
    
    object German : Strings {
        override val appName = "$APP_NAME Trading"
        override val portfolio = "Portfolio"
        override val trading = "Handel"
        override val market = "Markt"
        override val settings = "Einstellungen"
        override val signals = "Signale"
        override val screener = "Screener"
        override val ai = "KI"
        override val activity = "Aktivität"
        override val login = "Anmelden"
        override val register = "Registrieren"
        override val email = "E-Mail"
        override val password = "Passwort"
        override val forgotPassword = "Passwort vergessen?"
        override val dontHaveAccount = "Kein Konto?"
        override val alreadyHaveAccount = "Bereits ein Konto?"
        override val logout = "Abmelden"
        override val balance = "Guthaben"
        override val positions = "Positionen"
        override val openPositions = "Offene Positionen"
        override val noPositions = "Keine offenen Positionen"
        override val unrealizedPnl = "Unrealisierter PnL"
        override val availableBalance = "Verfügbar"
        override val totalEquity = "Gesamtkapital"
        override val marginUsed = "Verwendete Marge"
        override val todayPnl = "PnL heute"
        override val weekPnl = "PnL Woche"
        override val entry = "Einstieg"
        override val size = "Größe"
        override val leverage = "Hebel"
        override val pnl = "PnL"
        override val close = "Schließen"
        override val closeAll = "Alle schließen"
        override val confirmClose = "Position schließen bestätigen?"
        override val buy = "Kaufen"
        override val sell = "Verkaufen"
        override val long = "Long"
        override val short = "Short"
        override val marketOrder = "Markt"
        override val limit = "Limit"
        override val stopLoss = "Stop-Loss"
        override val takeProfit = "Take-Profit"
        override val quantity = "Menge"
        override val price = "Preis"
        override val placeOrder = "Order platzieren"
        override val allSignals = "Alle"
        override val longSignals = "Long"
        override val shortSignals = "Short"
        override val noSignals = "Keine Signale"
        override val all = "Alle"
        override val long_text = "Long"
        override val short_text = "Short"
        override val cryptoScreener = "Krypto Screener"
        override val searchCoins = "Coins suchen..."
        override val volume = "Volumen"
        override val change24h = "24h Änderung"
        override val oiChange = "OI Änderung"
        override val language = "Sprache"
        override val exchange = "Börse"
        override val accountType = "Kontotyp"
        override val demo = "Demo"
        override val real = "Real"
        override val testnet = "Testnet"
        override val mainnet = "Mainnet"
        override val apiKeys = "API-Schlüssel"
        override val notifications = "Benachrichtigungen"
        override val theme = "Theme"
        override val darkTheme = "Dunkel"
        override val lightTheme = "Hell"
        override val systemTheme = "System"
        override val strategies = "Strategien"
        override val premium = "Premium"
        
        // Linked Accounts
        override val linkedAccounts = "Verknüpfte Konten"
        override val linkTelegram = "Telegram verknüpfen"
        override val linkEmail = "E-Mail verknüpfen"
        override val telegramLinked = "Telegram verknüpft"
        override val emailLinked = "E-Mail verknüpft"
        override val notLinked = "Nicht verknüpft"
        override val notVerified = "Nicht verifiziert"
        override val verified = "Verifiziert"
        
        override val aiAssistant = "KI-Assistent"
        override val askAnything = "Fragen zum Trading..."
        override val typeMessage = "Nachricht eingeben..."
        override val recentActivity = "Letzte Aktivität"
        override val settingsChanges = "Einstellungsänderungen"
        override val noActivity = "Keine Aktivität"
        override val loading = "Laden..."
        override val error = "Fehler"
        override val retry = "Wiederholen"
        override val cancel = "Abbrechen"
        override val confirm = "Bestätigen"
        override val save = "Speichern"
        override val delete = "Löschen"
        override val refresh = "Aktualisieren"
        override val back = "Zurück"
        override val next = "Weiter"
        override val done = "Fertig"
        override val success = "Erfolg"
        override val failed = "Fehlgeschlagen"
        override val enabled = "Aktiviert"
        override val disabled = "Deaktiviert"
        override val on = "AN"
        override val off = "AUS"
        override val tradingStats = "Handelsstatistik"
        override val totalTrades = "Gesamte Trades"
        override val winRate = "Gewinnrate"
        override val wins = "Gewinne"
        override val losses = "Verluste"
        override val avgPnl = "Durchschn. PnL"
        override val bestTrade = "Bester Trade"
        override val worstTrade = "Schlechtester Trade"
        // Disclaimer
        override val disclaimerTitle = "⚠️ Wichtiger Hinweis"
        override val disclaimerIntro = "Enliko ist ein Bildungs- und Analysewerkzeug für Kryptowährungsmärkte."
        override val disclaimerNotFinancialAdvice = "Dies ist KEINE Finanzberatung"
        override val disclaimerRiskOfLoss = "Der Handel birgt erhebliche Verlustrisiken"
        override val disclaimerPastPerformance = "Vergangene Ergebnisse garantieren keine zukünftigen"
        override val disclaimerUserResponsibility = "Sie sind allein für Ihre Entscheidungen verantwortlich"
        override val disclaimerEducationalOnly = "Nur für Bildungszwecke"
        override val disclaimerRiskWarningTitle = "RISIKOWARNUNG"
        override val disclaimerRiskWarningText = "Der Handel mit Kryptowährungen ist hochspekulativ. Sie können einen Teil oder Ihre gesamte Investition verlieren. Handeln Sie nur mit Mitteln, deren Verlust Sie sich leisten können."
        override val disclaimerAcceptBtn = "✅ Ich verstehe und akzeptiere"
        override val disclaimerDeclineBtn = "❌ Ich lehne ab"
        override val disclaimerTermsAgreement = "Mit der Annahme stimmen Sie unseren Nutzungsbedingungen und Datenschutzrichtlinien zu."
        override val disclaimerAcceptedMsg = "Vielen Dank für die Annahme."
        override val disclaimerDeclinedMsg = "Sie müssen den Hinweis akzeptieren, um Enliko zu nutzen."
    }
    
    // Placeholder implementations for other languages
    object Spanish : Strings by English
    object French : Strings by English
    object Italian : Strings by English
    object Japanese : Strings by English
    object Chinese : Strings by English
    object Arabic : Strings by English
    object Hebrew : Strings by English
    object Polish : Strings by English
    object Czech : Strings by English
    object Lithuanian : Strings by English
    object Albanian : Strings by English
}
