#!/usr/bin/env python3
"""
Add missing localization keys to Ukrainian and Russian sections in LocalizationManager.swift.
Inserts keys just before the closing '] }' of each language section.
"""

SWIFT_FILE = "ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift"

# Ukrainian translations for ALL 269 missing keys
UKRAINIAN_KEYS = {
    # Account / Auth
    "account_type": "Тип акаунту",
    "auth_add_email_prompt": "Додайте email для захисту акаунту",
    "auth_already_use_bot": "Вже використовуєте бот?",
    "auth_code_sent_to": "Код відправлено на %@",
    "auth_email_option": "Увійти через email",
    "auth_link_email_button": "Прив'язати email",
    "auth_logged_in_success": "Успішний вхід!",
    "auth_new_user": "Новий користувач?",
    "auth_open_telegram": "Відкрити Telegram",
    "auth_skip_for_now": "Пропустити",
    "auth_telegram_description": "Зв'яжіть Telegram для швидкого входу",
    "auth_telegram_optional_hint": "Опціонально — для сповіщень через бот",
    "auth_telegram_step1": "1. Відкрийте @enliko_bot в Telegram",
    "auth_telegram_step2": "2. Натисніть /app_login",
    "auth_telegram_step3": "3. Натисніть посилання для входу",
    "auth_telegram_title": "Зв'язати Telegram",
    "auth_verify_email_title": "Підтвердіть email",

    # Activity / Sync
    "activity_sync": "Синхронізація",

    # AI
    "ai_copilot": "AI Помічник",
    "ai_trading_copilot": "Торговий AI копілот",
    "ask_about_this": "Запитати про це",
    "smart_trading_assistant": "Розумний торговий асистент",

    # Trading Parameters
    "additional_investment": "Додаткова інвестиція",
    "amount_usdt": "Сума (USDT)",
    "atr_hint": "ATR автоматично підлаштовує стоп-лос",
    "atr_periods": "Періоди ATR",
    "atr_step": "Крок ATR",
    "atr_trailing": "ATR Трейлінг",
    "atr_trigger": "Тригер ATR",
    "be_info": "Переміщує SL на рівень входу при досягненні прибутку",
    "be_trigger": "Тригер BE (%)",
    "break_even": "Беззбитковість (BE)",
    "coins_group": "Група монет",
    "dca_enabled": "DCA увімкнено",
    "dca_hint": "Докупка при просадці",
    "dca_level_1": "Рівень DCA 1 (%)",
    "dca_level_2": "Рівень DCA 2 (%)",
    "dca_settings": "Налаштування DCA",
    "direction": "Напрямок",
    "enable_long": "Увімкнути Long",
    "enable_short": "Увімкнути Short",
    "entry_percent": "Вхід (%)",
    "filter_signal_direction": "Фільтр напрямку сигналу",
    "leverage": "Кредитне плече",
    "limit": "Лімітний",
    "limit_offset": "Зміщення ліміту",
    "main_parameters": "Основні параметри",
    "max_positions": "Макс. позицій",
    "order_settings": "Налаштування ордерів",
    "order_type": "Тип ордеру",
    "order_type_hint": "Market або Limit",
    "partial_tp": "Частковий TP",
    "partial_tp_info": "Закриття частини позиції при досягненні прибутку",
    "stop_loss": "Стоп-лос",
    "take_profit": "Тейк-профіт",
    "use_atr": "Використовувати ATR",

    # Trading View
    "buy": "Купити",
    "futures": "Ф'ючерси",
    "spot": "Спот",
    "trading_24h_change": "Зміна за 24г",
    "trading_24h_volume": "Об'єм за 24г",
    "trading_cancel_order": "Скасувати ордер",
    "trading_close_position": "Закрити позицію",
    "trading_current_price": "Поточна ціна",
    "trading_entry_price": "Ціна входу",
    "trading_leverage": "Плече",
    "trading_liq_price": "Ціна ліквідації",
    "trading_margin_required": "Необхідна маржа",
    "trading_mark_price": "Ціна маркування",
    "trading_open_interest": "Відкритий інтерес",
    "trading_order_failed": "Ордер не виконано",
    "trading_order_placed": "Ордер розміщено",
    "trading_order_value": "Вартість ордеру",
    "trading_place_long": "Відкрити Long",
    "trading_place_short": "Відкрити Short",
    "trading_preferences": "Торгові параметри",
    "trading_quantity": "Кількість",
    "trading_settings": "Налаштування торгівлі",
    "trading_tab_history": "Історія",
    "trading_tab_order": "Ордер",
    "trading_tab_orders": "Ордери",
    "trading_tab_positions": "Позиції",
    "trading_tools": "Торгові інструменти",
    "trading_tp_sl_section": "TP / SL",

    # Portfolio
    "portfolio_available": "Доступно",
    "portfolio_balance": "Баланс",
    "portfolio_candles": "Свічки",
    "portfolio_equity": "Капітал",
    "portfolio_futures": "Ф'ючерси",
    "portfolio_futures_equity": "Капітал ф'ючерсів",
    "portfolio_in_positions": "У позиціях",
    "portfolio_margin": "Маржа",
    "portfolio_no_chart_data": "Немає даних для графіку",
    "portfolio_no_data": "Немає даних",
    "portfolio_no_recent_trades": "Немає останніх угод",
    "portfolio_no_spot_assets": "Немає спот активів",
    "portfolio_open_positions": "Відкриті позиції",
    "portfolio_overview": "Огляд портфеля",
    "portfolio_pnl_chart": "Графік PnL",
    "portfolio_pnl_month": "PnL за місяць",
    "portfolio_pnl_today": "PnL сьогодні",
    "portfolio_pnl_week": "PnL за тиждень",
    "portfolio_positions": "Позиції",
    "portfolio_recent_trades": "Останні угоди",
    "portfolio_spot": "Спот",
    "portfolio_spot_balance": "Спот баланс",
    "portfolio_tap_candle_hint": "Натисніть на свічку для деталей",
    "portfolio_total_balance": "Загальний баланс",
    "portfolio_unrealized": "Нереалізований",
    "portfolio_unrealized_pnl": "Нереалізований PnL",

    # Positions / Orders
    "positions_no_orders": "Немає ордерів",
    "positions_no_orders_subtitle": "У вас немає активних ордерів",

    # Spot Trading
    "spot_advanced": "Розширені",
    "spot_auto_dca": "Авто DCA",
    "spot_balance": "Спот баланс",
    "spot_buy_sell": "Купити / Продати",
    "spot_dca_enabled": "DCA увімкнено",
    "spot_dca_pct": "DCA відсоток",
    "spot_dca_strategy": "Стратегія DCA",
    "spot_enabled": "Спот увімкнено",
    "spot_holdings": "Спот портфель",
    "spot_performance": "Продуктивність",
    "spot_portfolio": "Спот портфель",
    "spot_rebalance": "Ребалансування",
    "spot_sell": "Продати",
    "spot_start_dca": "Почати DCA",
    "spot_take_profit": "Тейк-профіт",
    "spot_trading": "Спот торгівля",
    "spot_trading_subtitle": "Купівля та продаж криптовалют",
    "futures_balance": "Баланс ф'ючерсів",

    # Strategies
    "strategies_subtitle": "Управління торговими стратегіями",
    "strategies_title": "Стратегії",
    "strategy_settings": "Налаштування стратегій",
    "strategy_settings_saved_message": "Налаштування збережено",

    # Settings
    "app_settings": "Налаштування додатку",
    "biometric_auth": "Біометричний вхід",
    "color_scheme": "Кольорова схема",
    "debug_demo_login": "Демо вхід (Debug)",
    "debug_dev_mode": "Режим розробника",
    "documentation": "Документація",
    "email": "Email",
    "email_linked": "Email прив'язано",
    "email_placeholder": "Введіть email",
    "email_support": "Підтримка по email",
    "enable_2fa": "Увімкнути 2FA",
    "enable_ip_whitelist": "IP білий список",
    "enable_notifications": "Увімкнути сповіщення",
    "enable_notifications_desc": "Отримуйте сповіщення про угоди",
    "exchange_connection": "Підключення біржі",
    "exchange_toggle_hint": "Натисніть для переключення біржі",
    "exchanges": "Біржі",
    "faq_title": "FAQ",
    "full_screener": "Повний скринер",
    "help_support": "Допомога та підтримка",
    "link_email": "Прив'язати email",
    "link_email_button": "Прив'язати",
    "link_email_description": "Прив'яжіть email для додаткового захисту",
    "link_email_error": "Помилка прив'язки email",
    "link_email_success": "Email успішно прив'язано",
    "link_email_title": "Прив'язати email",
    "link_telegram": "Зв'язати Telegram",
    "linked_accounts": "Зв'язані акаунти",
    "logout": "Вийти",
    "logout_confirm": "Підтвердити вихід",
    "logout_message": "Ви впевнені що хочете вийти?",
    "manage_api_keys": "Управління API ключами",
    "margin_warning": "Попередження про маржу",
    "need_more": "Потрібно більше?",
    "not_linked": "Не прив'язано",
    "not_verified": "Не підтверджено",
    "only_trading_permissions": "Тільки торгові дозволи",
    "no_withdrawal_permissions": "Без дозволу на виведення",
    "push_notifications": "Push-сповіщення",
    "rate_support": "Оцініть підтримку",
    "rate_support_message": "Як ви оцінюєте нашу підтримку?",
    "require_on_launch": "Вимагати при запуску",
    "save_settings": "Зберегти",
    "security_tips": "Поради безпеки",
    "security_warning": "Попередження безпеки",
    "settings_about": "Про додаток",
    "settings_account": "Акаунт",
    "settings_api_keys": "API ключі",
    "settings_app": "Додаток",
    "settings_appearance": "Оформлення",
    "settings_exchange": "Біржа",
    "settings_leverage": "Кредитне плече",
    "settings_logout_confirm": "Підтвердити вихід",
    "settings_notifications": "Сповіщення",
    "settings_privacy": "Конфіденційність",
    "settings_risk": "Ризик",
    "settings_saved": "Налаштування збережено",
    "settings_terms": "Умови використання",
    "settings_trading": "Торгівля",
    "sound_vibration": "Звук і вібрація",
    "specific_notifications": "Окремі сповіщення",
    "telegram_linked": "Telegram прив'язано",
    "telegram_support": "Підтримка через Telegram",
    "test_connection": "Тестувати з'єднання",
    "use_face_id": "Використовувати Face ID",
    "verified": "Підтверджено",

    # Chat
    "chat_status_closed": "Закрито",
    "chat_status_open": "Відкрито",
    "chat_status_resolved": "Вирішено",
    "chat_status_waiting": "Очікування",
    "close_chat": "Закрити чат",
    "start_chat": "Почати чат",
    "type_message": "Введіть повідомлення",

    # Cluster / Analytics
    "cluster_all_trades": "Всі угоди",
    "cluster_analysis": "Кластерний аналіз",
    "cluster_direction": "Напрямок",
    "cluster_pnl": "PnL",
    "cluster_strategies": "Стратегії",
    "cluster_summary": "Підсумок",
    "cluster_symbols": "Символи",
    "cluster_trades": "Угоди",
    "cluster_volume": "Об'єм",
    "cluster_win_rate": "Відсоток перемог",

    # Payment
    "buy_elc_to_pay": "Купити ELC для оплати",
    "confirm_password": "Підтвердіть пароль",
    "confirm_password_placeholder": "Повторіть пароль",
    "confirm_payment": "Підтвердити оплату",
    "elc_balance": "Баланс ELC",
    "pay": "Оплатити",
    "pay_elc_confirm": "Підтвердити оплату ELC",
    "pay_with_elc": "Оплатити ELC",
    "payment_failed": "Помилка оплати",
    "payment_no_refund_warning": "Після оплати повернення неможливе",
    "select_amount": "Виберіть суму",
    "select_coin": "Виберіть монету",
    "select_portfolio": "Виберіть портфель",
    "sell_coin": "Продати монету",
    "subscription_activated": "Підписку активовано!",

    # History
    "custom_end_date": "Кінцева дата",
    "custom_period": "Довільний період",
    "custom_start_date": "Початкова дата",
    "trade_closed": "Угоду закрито",
    "trade_history": "Історія угод",
    "trade_opened": "Угоду відкрито",

    # Sections
    "section_analytics": "Аналітика",
    "section_premium_features": "Преміум функції",
    "section_quick_access": "Швидкий доступ",
    "section_sync_notifications": "Синхронізація та сповіщення",
    "section_trading": "Торгівля",

    # HyperLiquid
    "hl_api_wallet_description": "API гаманець для торгівлі",
    "hl_api_wallet_info": "Інформація про API гаманець",
    "hl_security_warning": "Ніколи не діліться приватним ключем!",

    # Misc UI
    "copy_top_traders": "Копіювати топ трейдерів",
    "error_decoding": "Помилка декодування даних",
    "error_email_not_found": "Email не знайдено",
    "error_server": "Помилка сервера",
    "market_heatmap": "Теплова карта ринку",
    "market_overview": "Огляд ринку",
    "mark_all_read": "Позначити все як прочитане",
    "no_notifications": "Немає сповіщень",
    "no_notifications_desc": "У вас немає нових сповіщень",
    "notifications_subtitle": "Сповіщення та налаштування",
    "password": "Пароль",
    "password_placeholder": "Введіть пароль",
    "quick_dca": "Швидкий DCA",
    "siri_shortcuts": "Швидкі команди Siri",
    "social_trading": "Соціальний трейдинг",
    "support_title": "Підтримка",
    "support_welcome_subtitle": "Ми тут щоб допомогти",
    "support_welcome_title": "Ласкаво просимо до підтримки",
    "tokens": "Токени",
    "users_management": "Управління користувачами",
    "visual_market_overview": "Візуальний огляд ринку",
    "voice_commands_setup": "Налаштування голосових команд",
    "your_balance": "Ваш баланс",
}

# Russian translations for ALL 52 missing keys
RUSSIAN_KEYS = {
    "active": "Активный",
    "activity": "Активность",
    "ai": "ИИ",
    "configure_all_strategies": "Настроить все стратегии",
    "connected": "Подключено",
    "disconnected": "Отключено",
    "exchange": "Биржа",
    "full_screener": "Полный скринер",
    "futures_balance": "Баланс фьючерсов",
    "history": "История",
    "history_empty": "История пуста",
    "history_no_trades": "Нет сделок",
    "history_title": "История",
    "language": "Язык",
    "manage_alerts": "Управление оповещениями",
    "market_overview": "Обзор рынка",
    "more": "Ещё",
    "no_orders_subtitle": "У вас нет активных ордеров",
    "no_positions_subtitle": "У вас нет открытых позиций",
    "premium": "Премиум",
    "quick_tools": "Быстрые инструменты",
    "screener": "Скринер",
    "settings": "Настройки",
    "signals": "Сигналы",
    "stats": "Статистика",
    "synced_at": "Синхронизировано",
    "tap_to_configure": "Нажмите для настройки",
    "tokens": "Токены",
    "trading_24h_change": "Изменение за 24ч",
    "trading_24h_volume": "Объём за 24ч",
    "trading_cancel_order": "Отменить ордер",
    "trading_close_position": "Закрыть позицию",
    "trading_current_price": "Текущая цена",
    "trading_entry_price": "Цена входа",
    "trading_leverage": "Плечо",
    "trading_liq_price": "Цена ликвидации",
    "trading_long": "Лонг",
    "trading_margin_required": "Необходимая маржа",
    "trading_mark_price": "Цена маркировки",
    "trading_open_interest": "Открытый интерес",
    "trading_order_failed": "Ордер не выполнен",
    "trading_order_placed": "Ордер размещён",
    "trading_order_value": "Стоимость ордера",
    "trading_place_long": "Открыть Long",
    "trading_place_short": "Открыть Short",
    "trading_quantity": "Количество",
    "trading_short": "Шорт",
    "trading_tab_history": "История",
    "trading_tab_order": "Ордер",
    "trading_tab_orders": "Ордера",
    "trading_tab_positions": "Позиции",
    "trading_tp_sl_section": "TP / SL",
}


def add_keys_to_section(content, section_marker, keys_dict):
    """Add missing keys to a language section, just before the closing '] }'."""
    idx = content.find(section_marker)
    if idx == -1:
        print(f"  WARNING: Section not found: {section_marker}")
        return content

    # Find 'return [' after marker
    ret_idx = content.find("return [", idx)
    if ret_idx == -1:
        print(f"  WARNING: 'return [' not found after {section_marker}")
        return content

    # Find the matching '] }'
    bracket_start = content.index("[", ret_idx)
    depth = 0
    close_bracket = bracket_start
    for i in range(bracket_start, len(content)):
        if content[i] == "[":
            depth += 1
        elif content[i] == "]":
            depth -= 1
            if depth == 0:
                close_bracket = i
                break

    # Build the new entries string
    entries = []
    for key, value in sorted(keys_dict.items()):
        escaped_value = value.replace('"', '\\"')
        entries.append(f'        "{key}": "{escaped_value}",')

    new_block = "\n        // NEW: Auto-added missing keys\n" + "\n".join(entries) + "\n    "

    # Insert before the closing ']'
    content = content[:close_bracket] + new_block + content[close_bracket:]

    return content


def main():
    with open(SWIFT_FILE, "r") as f:
        content = f.read()

    print(f"Adding {len(UKRAINIAN_KEYS)} keys to Ukrainian...")
    content = add_keys_to_section(content, "// MARK: - Ukrainian", UKRAINIAN_KEYS)

    print(f"Adding {len(RUSSIAN_KEYS)} keys to Russian...")
    content = add_keys_to_section(content, "// MARK: - Russian", RUSSIAN_KEYS)

    with open(SWIFT_FILE, "w") as f:
        f.write(content)

    print("Done! Keys added successfully.")


if __name__ == "__main__":
    main()
