// ElCaro WebApp Translations - 15 languages
const translations = {
    en: {
        // Navigation
        nav_home: "Home",
        nav_terminal: "Terminal", 
        nav_marketplace: "Marketplace",
        nav_strategies: "Strategies",
        nav_leaderboard: "Leaderboard",
        nav_screener: "Screener",
        nav_login: "Login",
        nav_dashboard: "Dashboard",
        
        // Common
        loading: "Loading...",
        search: "Search",
        filter: "Filter",
        all: "All",
        buy: "Buy",
        sell: "Sell",
        long: "Long",
        short: "Short",
        price: "Price",
        volume: "Volume",
        change_24h: "24h Change",
        high_24h: "24h High",
        low_24h: "24h Low",
        open_interest: "Open Interest",
        funding_rate: "Funding Rate",
        trade: "Trade",
        save: "Save",
        cancel: "Cancel",
        confirm: "Confirm",
        success: "Success",
        error: "Error",
        
        // Marketplace
        marketplace_title: "Strategy Marketplace",
        marketplace_subtitle: "Discover and purchase profitable trading strategies",
        strategy_builder: "Strategy Builder",
        create_strategy: "Create Strategy",
        my_strategies: "My Strategies",
        purchased: "Purchased",
        top_rated: "Top Rated",
        most_popular: "Most Popular",
        newest: "Newest",
        free: "Free",
        premium: "Premium",
        purchase: "Purchase",
        already_owned: "Already Owned",
        
        // Strategy Builder
        builder_title: "Strategy Builder",
        builder_subtitle: "Create your custom trading strategy",
        indicators: "Indicators",
        conditions: "Conditions",
        entry_rules: "Entry Rules",
        exit_rules: "Exit Rules",
        risk_management: "Risk Management",
        backtest: "Backtest",
        publish: "Publish to Marketplace",
        
        // Leaderboard
        leaderboard_title: "Strategy Leaderboard",
        leaderboard_subtitle: "Top performing strategies",
        rank: "Rank",
        strategy_name: "Strategy Name",
        author: "Author",
        win_rate: "Win Rate",
        total_pnl: "Total PnL",
        trades: "Trades",
        period_24h: "24 Hours",
        period_7d: "7 Days",
        period_30d: "30 Days",
        period_all: "All Time",
        
        // Screener
        screener_title: "Crypto Screener",
        screener_subtitle: "Real-time market overview",
        gainers: "Gainers",
        losers: "Losers",
        high_volume: "High Volume",
        top_gainers: "Top Gainers",
        top_losers: "Top Losers",
        recent_liquidations: "Recent Liquidations",
        connected: "Live",
        disconnected: "Disconnected",
        connecting: "Connecting...",
        
        // Terminal
        terminal_title: "Trading Terminal",
        positions: "Positions",
        orders: "Orders",
        history: "History",
        balance: "Balance",
        equity: "Equity",
        margin: "Margin",
        leverage: "Leverage",
        take_profit: "Take Profit",
        stop_loss: "Stop Loss",
        market_order: "Market",
        limit_order: "Limit",
        
        // Auth
        login_title: "Login",
        login_telegram: "Login with Telegram",
        logout: "Logout",
        
        // Footer
        footer_rights: "All rights reserved",
        footer_terms: "Terms of Service",
        footer_privacy: "Privacy Policy"
    },
    
    ru: {
        nav_home: "Главная",
        nav_terminal: "Терминал",
        nav_marketplace: "Маркетплейс",
        nav_strategies: "Стратегии",
        nav_leaderboard: "Рейтинг",
        nav_screener: "Скринер",
        nav_login: "Вход",
        nav_dashboard: "Панель",
        loading: "Загрузка...",
        search: "Поиск",
        filter: "Фильтр",
        all: "Все",
        buy: "Купить",
        sell: "Продать",
        long: "Лонг",
        short: "Шорт",
        price: "Цена",
        volume: "Объём",
        change_24h: "Изменение 24ч",
        high_24h: "Макс 24ч",
        low_24h: "Мин 24ч",
        open_interest: "Открытый интерес",
        funding_rate: "Ставка финансирования",
        trade: "Торговать",
        save: "Сохранить",
        cancel: "Отмена",
        confirm: "Подтвердить",
        success: "Успешно",
        error: "Ошибка",
        marketplace_title: "Маркетплейс стратегий",
        marketplace_subtitle: "Найдите и купите прибыльные торговые стратегии",
        strategy_builder: "Конструктор стратегий",
        create_strategy: "Создать стратегию",
        my_strategies: "Мои стратегии",
        purchased: "Купленные",
        top_rated: "Лучший рейтинг",
        most_popular: "Популярные",
        newest: "Новые",
        free: "Бесплатно",
        premium: "Премиум",
        purchase: "Купить",
        already_owned: "Уже куплено",
        builder_title: "Конструктор стратегий",
        builder_subtitle: "Создайте свою торговую стратегию",
        indicators: "Индикаторы",
        conditions: "Условия",
        entry_rules: "Правила входа",
        exit_rules: "Правила выхода",
        risk_management: "Управление рисками",
        backtest: "Бэктест",
        publish: "Опубликовать",
        leaderboard_title: "Рейтинг стратегий",
        leaderboard_subtitle: "Лучшие стратегии",
        rank: "Место",
        strategy_name: "Название",
        author: "Автор",
        win_rate: "Винрейт",
        total_pnl: "Общий PnL",
        trades: "Сделки",
        period_24h: "24 часа",
        period_7d: "7 дней",
        period_30d: "30 дней",
        period_all: "Всё время",
        screener_title: "Крипто скринер",
        screener_subtitle: "Обзор рынка в реальном времени",
        gainers: "Растущие",
        losers: "Падающие",
        high_volume: "Высокий объём",
        top_gainers: "Топ растущих",
        top_losers: "Топ падающих",
        recent_liquidations: "Последние ликвидации",
        connected: "Онлайн",
        disconnected: "Отключено",
        connecting: "Подключение...",
        terminal_title: "Торговый терминал",
        positions: "Позиции",
        orders: "Ордера",
        history: "История",
        balance: "Баланс",
        equity: "Эквити",
        margin: "Маржа",
        leverage: "Плечо",
        take_profit: "Тейк профит",
        stop_loss: "Стоп лосс",
        market_order: "Рыночный",
        limit_order: "Лимитный",
        login_title: "Вход",
        login_telegram: "Войти через Telegram",
        logout: "Выход",
        footer_rights: "Все права защищены",
        footer_terms: "Условия использования",
        footer_privacy: "Политика конфиденциальности"
    },
    
    uk: {
        nav_home: "Головна",
        nav_terminal: "Термінал",
        nav_marketplace: "Маркетплейс",
        nav_strategies: "Стратегії",
        nav_leaderboard: "Рейтинг",
        nav_screener: "Скринер",
        nav_login: "Вхід",
        nav_dashboard: "Панель",
        loading: "Завантаження...",
        search: "Пошук",
        filter: "Фільтр",
        all: "Всі",
        buy: "Купити",
        sell: "Продати",
        long: "Лонг",
        short: "Шорт",
        price: "Ціна",
        volume: "Об'єм",
        change_24h: "Зміна 24г",
        marketplace_title: "Маркетплейс стратегій",
        marketplace_subtitle: "Знайдіть прибуткові торгові стратегії",
        screener_title: "Крипто скринер",
        connected: "Онлайн",
        disconnected: "Відключено"
    },
    
    de: {
        nav_home: "Startseite",
        nav_terminal: "Terminal",
        nav_marketplace: "Marktplatz",
        nav_strategies: "Strategien",
        nav_leaderboard: "Rangliste",
        nav_screener: "Screener",
        loading: "Laden...",
        search: "Suche",
        price: "Preis",
        volume: "Volumen",
        trade: "Handeln",
        marketplace_title: "Strategie-Marktplatz",
        screener_title: "Krypto Screener",
        connected: "Live",
        disconnected: "Getrennt"
    },
    
    es: {
        nav_home: "Inicio",
        nav_terminal: "Terminal",
        nav_marketplace: "Mercado",
        nav_strategies: "Estrategias",
        nav_leaderboard: "Clasificación",
        nav_screener: "Escáner",
        loading: "Cargando...",
        search: "Buscar",
        price: "Precio",
        volume: "Volumen",
        trade: "Operar",
        marketplace_title: "Mercado de Estrategias",
        screener_title: "Escáner Cripto",
        connected: "En vivo",
        disconnected: "Desconectado"
    },
    
    fr: {
        nav_home: "Accueil",
        nav_terminal: "Terminal",
        nav_marketplace: "Marché",
        nav_strategies: "Stratégies",
        nav_leaderboard: "Classement",
        nav_screener: "Scanner",
        loading: "Chargement...",
        search: "Recherche",
        price: "Prix",
        volume: "Volume",
        trade: "Trader",
        marketplace_title: "Marché des Stratégies",
        screener_title: "Scanner Crypto",
        connected: "En direct",
        disconnected: "Déconnecté"
    },
    
    it: {
        nav_home: "Home",
        nav_terminal: "Terminale",
        nav_marketplace: "Mercato",
        nav_strategies: "Strategie",
        nav_leaderboard: "Classifica",
        nav_screener: "Scanner",
        loading: "Caricamento...",
        marketplace_title: "Mercato delle Strategie",
        screener_title: "Scanner Cripto"
    },
    
    pl: {
        nav_home: "Strona główna",
        nav_terminal: "Terminal",
        nav_marketplace: "Rynek",
        nav_strategies: "Strategie",
        nav_leaderboard: "Ranking",
        nav_screener: "Skaner",
        loading: "Ładowanie...",
        marketplace_title: "Rynek Strategii",
        screener_title: "Skaner Krypto"
    },
    
    ja: {
        nav_home: "ホーム",
        nav_terminal: "ターミナル",
        nav_marketplace: "マーケット",
        nav_strategies: "戦略",
        nav_leaderboard: "ランキング",
        nav_screener: "スクリーナー",
        loading: "読み込み中...",
        marketplace_title: "戦略マーケット",
        screener_title: "クリプトスクリーナー"
    },
    
    zh: {
        nav_home: "首页",
        nav_terminal: "终端",
        nav_marketplace: "市场",
        nav_strategies: "策略",
        nav_leaderboard: "排行榜",
        nav_screener: "筛选器",
        loading: "加载中...",
        marketplace_title: "策略市场",
        screener_title: "加密货币筛选器"
    },
    
    ar: {
        nav_home: "الرئيسية",
        nav_terminal: "المحطة",
        nav_marketplace: "السوق",
        nav_strategies: "الاستراتيجيات",
        nav_leaderboard: "الترتيب",
        nav_screener: "الماسح",
        loading: "جاري التحميل...",
        marketplace_title: "سوق الاستراتيجيات",
        screener_title: "ماسح العملات"
    },
    
    he: {
        nav_home: "בית",
        nav_terminal: "טרמינל",
        nav_marketplace: "שוק",
        nav_strategies: "אסטרטגיות",
        nav_leaderboard: "דירוג",
        nav_screener: "סורק",
        loading: "טוען...",
        marketplace_title: "שוק אסטרטגיות",
        screener_title: "סורק קריפטו"
    },
    
    cs: {
        nav_home: "Domů",
        nav_terminal: "Terminál",
        nav_marketplace: "Tržiště",
        nav_strategies: "Strategie",
        nav_leaderboard: "Žebříček",
        nav_screener: "Skener",
        loading: "Načítání...",
        marketplace_title: "Tržiště strategií",
        screener_title: "Krypto skener"
    },
    
    lt: {
        nav_home: "Pradžia",
        nav_terminal: "Terminalas",
        nav_marketplace: "Turgus",
        nav_strategies: "Strategijos",
        nav_leaderboard: "Reitingas",
        nav_screener: "Skeneris",
        loading: "Kraunama...",
        marketplace_title: "Strategijų turgus",
        screener_title: "Kripto skeneris"
    },
    
    sq: {
        nav_home: "Ballina",
        nav_terminal: "Terminali",
        nav_marketplace: "Tregu",
        nav_strategies: "Strategjitë",
        nav_leaderboard: "Renditja",
        nav_screener: "Skaneri",
        loading: "Duke ngarkuar...",
        marketplace_title: "Tregu i Strategjive",
        screener_title: "Skaneri Kripto"
    }
};

// i18n helper
class I18n {
    constructor() {
        this.currentLang = localStorage.getItem('lang') || 'en';
        this.fallback = 'en';
    }
    
    t(key) {
        const langData = translations[this.currentLang] || translations[this.fallback];
        return langData[key] || translations[this.fallback][key] || key;
    }
    
    setLang(lang) {
        if (translations[lang]) {
            this.currentLang = lang;
            localStorage.setItem('lang', lang);
            this.updatePage();
            return true;
        }
        return false;
    }
    
    getLang() {
        return this.currentLang;
    }
    
    getLanguages() {
        return Object.keys(translations);
    }
    
    updatePage() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            el.textContent = this.t(key);
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            el.placeholder = this.t(key);
        });
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            el.title = this.t(key);
        });
    }
}

const i18n = new I18n();

// Auto-update on load
document.addEventListener('DOMContentLoaded', () => {
    i18n.updatePage();
});
