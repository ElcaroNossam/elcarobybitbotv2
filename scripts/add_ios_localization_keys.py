#!/usr/bin/env python3
"""
Add localization keys to iOS LocalizationManager.swift for hardcoded strings.
Adds keys to English dict and stubs for all other languages.
"""
import re

# Keys to add with English values and Russian translations
NEW_KEYS = {
    # PositionDetailView
    "pos_modify_tpsl": ("Modify TP/SL", "Изменить TP/SL"),
    "pos_add_to_position": ("Add to Position", "Добавить к позиции"),
    "pos_close_position": ("Close Position", "Закрыть позицию"),
    "pos_close_100": ("Close 100%", "Закрыть 100%"),
    "pos_close_confirm_msg": ("Are you sure you want to close this position?", "Вы уверены, что хотите закрыть позицию?"),
    "pos_unrealized_pnl": ("Unrealized PnL", "Нереализованный PnL"),
    "pos_roe": ("ROE", "ROE"),
    "pos_size": ("Size", "Размер"),
    "pos_value": ("Value", "Стоимость"),
    "pos_details": ("Position Details", "Детали позиции"),
    "pos_entry_price": ("Entry Price", "Цена входа"),
    "pos_mark_price": ("Mark Price", "Марк цена"),
    "pos_liq_price": ("Liq. Price", "Цена ликв."),
    "pos_margin": ("Margin", "Маржа"),
    "pos_maintenance_margin": ("Maintenance Margin", "Поддерж. маржа"),
    "pos_opened": ("Opened", "Открыто"),
    "pos_tpsl": ("TP/SL", "TP/SL"),
    "btn_modify": ("Modify", "Изменить"),
    "pos_take_profit": ("Take Profit", "Тейк-профит"),
    "pos_not_set": ("Not Set", "Не задан"),
    "pos_stop_loss": ("Stop Loss", "Стоп-лосс"),
    "pos_quick_actions": ("Quick Actions", "Быстрые действия"),
    "pos_partial_close": ("Partial Close", "Частичное закрытие"),
    "pos_add_position": ("Add Position", "Добавить"),
    "pos_flip": ("Flip", "Развернуть"),
    "pos_close_full": ("Close Position (100%)", "Закрыть (100%)"),
    "pos_close_partial_title": ("Close Partial Position", "Частичное закрытие"),
    "pos_closing_size": ("Closing Size", "Размер закрытия"),
    "pos_estimated_pnl": ("Estimated PnL", "Ожидаемый PnL"),
    "pos_remaining_size": ("Remaining Size", "Остаток"),
    "pos_current_price": ("Current Price", "Текущая цена"),
    "pos_tp_price": ("TP Price", "Цена TP"),
    "pos_sl_price": ("SL Price", "Цена SL"),
    "btn_save_changes": ("Save Changes", "Сохранить"),
    "pos_current_position": ("Current Position", "Текущая позиция"),
    "pos_amount_to_add": ("Amount to Add (USDT)", "Сумма (USDT)"),
    "pos_enter_amount": ("Enter amount", "Введите сумму"),

    # HyperLiquidView
    "hl_tab_overview": ("Overview", "Обзор"),
    "hl_tab_vaults": ("Vaults", "Хранилища"),
    "hl_tab_transfers": ("Transfers", "Переводы"),
    "hl_tab_points": ("Points", "Баллы"),
    "hl_title": ("HyperLiquid", "HyperLiquid"),
    "hl_testnet": ("Testnet", "Тестнет"),
    "hl_mainnet": ("Mainnet", "Основная"),
    "hl_switch": ("Switch", "Сменить"),
    "hl_total_balance": ("Total Balance", "Общий баланс"),
    "hl_perp": ("Perp", "Фьючерсы"),
    "hl_spot": ("Spot", "Спот"),
    "hl_deposit": ("Deposit", "Депозит"),
    "hl_withdraw": ("Withdraw", "Вывод"),
    "hl_transfer": ("Transfer", "Перевод"),
    "hl_24h_volume": ("24h Volume", "Объём 24ч"),
    "hl_open_interest": ("Open Interest", "Открытый интерес"),
    "hl_funding_rate": ("Funding Rate", "Ставка финанс."),
    "hl_positions": ("Positions", "Позиции"),
    "hl_margin_details": ("Margin Details", "Детали маржи"),
    "hl_account_margin": ("Account Margin", "Маржа аккаунта"),
    "hl_margin_ratio": ("Margin Ratio", "Маржа %"),
    "hl_recent_activity": ("Recent Activity", "Последняя активность"),
    "hl_see_all": ("See All", "Всё"),
    "hl_no_transfers": ("No transfers yet", "Нет переводов"),
    "hl_points_title": ("HyperLiquid Points", "Баллы HyperLiquid"),
    "hl_how_to_earn": ("How to Earn", "Как заработать"),
    "hl_earn_trading": ("Trading Volume", "Объём торговли"),
    "hl_earn_trading_desc": ("Earn 1 point per $1,000 traded", "1 балл за $1,000 торговли"),
    "hl_earn_referrals": ("Referrals", "Рефералы"),
    "hl_earn_referrals_desc": ("Invite friends to join", "Пригласите друзей"),
    "hl_earn_daily": ("Daily Login", "Ежедневный вход"),
    "hl_earn_daily_desc": ("Check in every day", "Заходите каждый день"),
    "hl_earn_vault": ("Vault Deposits", "Вклады"),
    "hl_earn_vault_desc": ("Deposit to earn extra", "Вносите для бонусов"),
    "hl_deposit_usdc": ("Deposit USDC", "Внести USDC"),
    "hl_withdraw_usdc": ("Withdraw USDC", "Вывести USDC"),
    "hl_dest_address": ("Destination Address", "Адрес получателя"),
    "hl_internal_transfer": ("Internal Transfer", "Внутренний перевод"),
    "hl_from": ("From", "Откуда"),
    "hl_to": ("To", "Куда"),
    "hl_deposit_to_vault": ("Deposit to Vault", "Внести в хранилище"),
    "hl_vault_details": ("Vault Details", "Детали хранилища"),
    "hl_tvl": ("TVL", "TVL"),
    "hl_your_deposit": ("Your Deposit", "Ваш вклад"),
    "hl_your_pnl": ("Your PnL", "Ваш PnL"),
    "hl_30d_return": ("30d Return", "Доход 30д"),
    "hl_pnl_label": ("PnL:", "PnL:"),

    # SpotTradingView
    "spot_buy": ("Buy", "Купить"),
    "spot_dca_fixed": ("Fixed", "Фиксированный"),
    "spot_dca_fixed_desc": ("Same amount", "Одинаковая сумма"),
    "spot_dca_value_avg": ("Value Avg", "Усредн. стоимости"),
    "spot_dca_value_avg_desc": ("Buy dips more", "Больше на просадке"),
    "spot_dca_fear_greed": ("Fear/Greed", "Страх/Жадность"),
    "spot_dca_fear_greed_desc": ("Fear = Buy more", "Страх = Больше покупать"),
    "spot_dca_crash_boost": ("Crash Boost", "Бустер обвала"),
    "spot_dca_crash_boost_desc": ("3x on -15%", "3x при -15%"),
    "spot_dca_momentum": ("Momentum", "Моментум"),
    "spot_dca_momentum_desc": ("Follow trend", "По тренду"),
    "spot_dca_rsi": ("RSI Smart", "RSI Умный"),
    "spot_dca_rsi_desc": ("RSI < 30 buy", "RSI < 30 купить"),
    "spot_coin": ("Coin", "Монета"),
    "spot_amount": ("Amount", "Сумма"),
    "spot_execute_dca": ("Execute DCA", "Выполнить DCA"),
    "spot_current_fear_greed": ("Current Fear & Greed:", "Индекс страха:"),
    "spot_portfolio_picker": ("Portfolio", "Портфель"),
    "spot_port_blue_chip": ("💎 Blue Chips", "💎 Голубые фишки"),
    "spot_port_defi": ("🏦 DeFi", "🏦 DeFi"),
    "spot_port_layer2": ("⚡ Layer 2", "⚡ Уровень 2"),
    "spot_port_ai": ("🤖 AI & Data", "🤖 ИИ и данные"),
    "spot_port_gaming": ("🎮 Gaming", "🎮 Игры"),
    "spot_port_meme": ("🐕 Memecoins", "🐕 Мемкоины"),
    "spot_port_l1_killers": ("⚔️ L1 Killers", "⚔️ L1 Килеры"),
    "spot_port_rwa": ("🏛️ RWA", "🏛️ RWA"),
    "spot_port_infra": ("🔧 Infrastructure", "🔧 Инфраструктура"),
    "spot_port_btc_only": ("₿ BTC Only", "₿ Только BTC"),
    "spot_port_eth_btc": ("💰 ETH+BTC", "💰 ETH+BTC"),
    "spot_port_custom": ("⚙️ Custom", "⚙️ Свой"),
    "spot_rebalance_now": ("Rebalance Now", "Ребаланс"),
    "spot_enable_auto_dca": ("Enable Auto DCA", "Вкл. авто DCA"),
    "spot_strat_fixed": ("📊 Fixed", "📊 Фиксированный"),
    "spot_strat_value_avg": ("📈 Value Averaging", "📈 Усреднение"),
    "spot_strat_fear_greed": ("😱 Fear & Greed", "😱 Страх и жадность"),
    "spot_strat_crash_boost": ("🚨 Crash Boost", "🚨 Бустер обвала"),
    "spot_freq_hourly": ("⏰ Hourly", "⏰ Каждый час"),
    "spot_freq_daily": ("📅 Daily", "📅 Ежедневно"),
    "spot_freq_weekly": ("📆 Weekly", "📆 Еженедельно"),
    "spot_enable_tp_levels": ("Enable TP Levels", "Вкл. уровни TP"),
    "spot_tp_conservative": ("🐢 Conservative", "🐢 Консервативный"),
    "spot_tp_balanced": ("⚖️ Balanced", "⚖️ Сбалансированный"),
    "spot_tp_aggressive": ("🦁 Aggressive", "🦁 Агрессивный"),
    "spot_tp_moonbag": ("🌙 Moonbag", "🌙 Moonbag"),
    "spot_trailing_tp": ("Trailing TP", "Скользящий TP"),
    "spot_profit_lock": ("🔒 Profit Lock", "🔒 Фиксация прибыли"),
    "spot_profit_lock_desc": ("Sell 50% when +30% profit", "Продать 50% при +30%"),
    "spot_auto_rebalance": ("⚖️ Auto Rebalance", "⚖️ Авто ребаланс"),
    "spot_rebalance_desc": ("Rebalance when >10% drift", "Ребаланс при >10%"),
    "spot_invested": ("Invested", "Вложено"),
    "spot_current_value": ("Current Value", "Текущая стоимость"),
    "spot_unrealized_pnl": ("Unrealized PnL", "Нереализованный PnL"),
    "spot_fear_greed_index": ("Fear & Greed Index", "Индекс страха и жадности"),
    "spot_no_holdings": ("No Spot Holdings", "Нет спот-активов"),
    "spot_no_holdings_desc": ("Start building your portfolio with DCA", "Начните портфель с DCA"),
    "spot_buy_crypto": ("Buy Crypto", "Купить крипто"),
    "spot_select_coin": ("Select Coin", "Выбрать монету"),
    "spot_amount_usdt": ("Amount (USDT)", "Сумма (USDT)"),
    "spot_enter_amount": ("Enter amount", "Введите сумму"),
    "spot_select_portfolio": ("Select Portfolio", "Выбрать портфель"),
    "spot_additional_investment": ("Additional Investment (optional)", "Доп. инвестиция (опц.)"),
    "spot_rebalance_portfolio": ("Rebalance Portfolio", "Ребаланс портфеля"),

    # AlertsView
    "alert_cond_above": ("Price Above", "Цена выше"),
    "alert_cond_below": ("Price Below", "Цена ниже"),
    "alert_cond_cross_up": ("Cross Up", "Пересечение вверх"),
    "alert_cond_cross_down": ("Cross Down", "Пересечение вниз"),
    "alert_cond_pct_up": ("% Change Up", "% Рост"),
    "alert_cond_pct_down": ("% Change Down", "% Падение"),
    "alert_tab_active": ("Active", "Активные"),
    "alert_tab_triggered": ("Triggered", "Сработавшие"),
    "alert_tab_all": ("All", "Все"),
    "alert_title": ("Price Alerts", "Уведомления о ценах"),
    "alert_delete_confirm": ("Delete Alert?", "Удалить оповещение?"),
    "btn_delete": ("Delete", "Удалить"),
    "alert_empty_title": ("No Price Alerts", "Нет оповещений"),
    "alert_empty_desc": ("Create alerts to get notified when\\nprices reach your targets", "Создайте оповещения о ценах"),
    "alert_create": ("Create Alert", "Создать"),
    "alert_target": ("Target", "Цель"),
    "alert_current": ("Current", "Текущая"),
    "alert_distance": ("Distance", "Расстояние"),
    "btn_edit": ("Edit", "Изменить"),
    "alert_symbol": ("Symbol", "Символ"),
    "alert_condition": ("Condition", "Условие"),
    "alert_target_price": ("Target Price", "Целевая цена"),
    "alert_note": ("Note (optional)", "Заметка (опц.)"),
    "alert_add_note": ("Add a note...", "Заметка..."),
    "alert_push_notif": ("Push Notification", "Push уведомление"),
    "alert_sound": ("Sound", "Звук"),
    "alert_repeat": ("Repeat Alert", "Повторять"),
    "alert_edit_title": ("Edit Alert", "Изменить оповещение"),
    "alert_new_title": ("New Alert", "Новое оповещение"),
    "btn_save": ("Save", "Сохранить"),
    "alert_search_symbol": ("Search symbol", "Поиск символа"),
    "alert_select_symbol": ("Select Symbol", "Выбрать символ"),

    # SubSettingsViews
    "exchange_bybit_desc": ("Demo & Real accounts", "Демо и реальные акк."),
    "exchange_hl_desc": ("Testnet & Mainnet", "Тестнет и основная"),
    "exchange_select": ("Select Exchange", "Выбрать биржу"),
    "exchange_title": ("Exchange", "Биржа"),
    "leverage_default": ("Default Leverage", "Плечо по умолчанию"),
    "leverage_warning": ("Higher leverage increases risk of liquidation", "Высокое плечо увеличивает риск ликвидации"),
    "leverage_title": ("Leverage", "Плечо"),
    "risk_entry_pct": ("Entry %", "Вход %"),
    "risk_tp_pct": ("Take Profit %", "Тейк-профит %"),
    "risk_sl_pct": ("Stop Loss %", "Стоп-лосс %"),
    "risk_position_sizing": ("Position Sizing", "Размер позиции"),
    "risk_use_atr": ("Use ATR for SL/TP", "ATR для SL/TP"),
    "risk_enable_dca": ("Enable DCA", "Включить DCA"),
    "risk_advanced": ("Advanced", "Расширенные"),
    "risk_advanced_footer": ("ATR adjusts SL/TP based on market volatility. DCA adds to positions at drawdown levels.", "ATR настраивает SL/TP по волатильности. DCA усредняет позицию при просадках."),
    "btn_save_settings": ("Save Settings", "Сохранить настройки"),
    "risk_title": ("Risk Management", "Управление рисками"),
    "about_subtitle": ("Professional Trading Platform", "Профессиональная торговая платформа"),
    "about_version": ("Version", "Версия"),
    "about_website": ("Website", "Веб-сайт"),
    "about_support": ("Support", "Поддержка"),
    "about_telegram": ("Telegram", "Telegram"),
    "about_copyright": ("© 2026 Enliko. All rights reserved.", "© 2026 Enliko. Все права защищены."),
    "about_title": ("About", "О приложении"),
    "apikey_demo_account": ("Demo Account", "Демо-аккаунт"),
    "apikey_demo_subtitle": ("Practice trading with testnet", "Тренировка на тестнете"),
    "apikey_real_account": ("Real Account", "Реальный аккаунт"),
    "apikey_real_subtitle": ("Live trading with real funds", "Торговля реальными средствами"),
    "apikey_testnet": ("Testnet", "Тестнет"),
    "apikey_testnet_subtitle": ("Practice with test funds", "Тренировка с тестовыми средствами"),
    "apikey_mainnet": ("Mainnet", "Основная сеть"),
    "apikey_mainnet_subtitle": ("Real funds trading", "Торговля реальными средствами"),
    "apikey_key_placeholder": ("API Key", "API ключ"),
    "apikey_secret_placeholder": ("API Secret", "API секрет"),
    "apikey_private_key_placeholder": ("Private Key (0x...)", "Приватный ключ (0x...)"),
    "apikey_api_wallet": ("API Wallet:", "API кошелёк:"),
    "apikey_main_wallet": ("Main Wallet:", "Основной кошелёк:"),
    "apikey_balance": ("Balance:", "Баланс:"),

    # Common
    "btn_cancel": ("Cancel", "Отмена"),
}

LOCALIZATION_FILE = "ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift"

def main():
    with open(LOCALIZATION_FILE, "r") as f:
        content = f.read()

    # Build the key-value block for English
    en_block = "\n        // Position Detail, HL, Spot, Alerts, Settings (auto-generated)\n"
    for key, (en_val, _) in NEW_KEYS.items():
        escaped = en_val.replace('"', '\\"')
        en_block += f'        "{key}": "{escaped}",\n'

    # Build for Russian
    ru_block = "\n        // Position Detail, HL, Spot, Alerts, Settings (auto-generated)\n"
    for key, (_, ru_val) in NEW_KEYS.items():
        escaped = ru_val.replace('"', '\\"')
        ru_block += f'        "{key}": "{escaped}",\n'

    # For other languages, use English as fallback
    other_block = "\n        // Position Detail, HL, Spot, Alerts, Settings (auto-generated)\n"
    for key, (en_val, _) in NEW_KEYS.items():
        escaped = en_val.replace('"', '\\"')
        other_block += f'        "{key}": "{escaped}",\n'

    # Find all language dicts and inject
    # Pattern: find "users_management": "..." line followed by '] }' 
    # and inject our keys before '] }'
    
    # Dict locations (line, name)
    dicts = {
        "englishTranslations": en_block,
        "russianTranslations": ru_block,
        "ukrainianTranslations": ru_block,  # UK uses same as RU for now
    }
    # All others get English
    for name in ["germanTranslations", "spanishTranslations", "frenchTranslations",
                 "italianTranslations", "japaneseTranslations", "chineseTranslations",
                 "arabicTranslations", "hebrewTranslations", "polishTranslations",
                 "czechTranslations", "lithuanianTranslations", "albanianTranslations"]:
        dicts[name] = other_block

    lines = content.split('\n')
    
    # For each dict, find its '] }' ending and inject keys before it
    for dict_name, block in dicts.items():
        # Find the start line
        start_idx = None
        for i, line in enumerate(lines):
            if f"static var {dict_name}" in line:
                start_idx = i
                break
        
        if start_idx is None:
            print(f"WARNING: Could not find {dict_name}")
            continue
            
        # Find the '] }' that closes this dict
        end_idx = None
        for i in range(start_idx + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped == '] }' or stripped == ']}':
                end_idx = i
                break
        
        if end_idx is None:
            print(f"WARNING: Could not find end of {dict_name}")
            continue
        
        # Check if keys already exist
        if "pos_modify_tpsl" in '\n'.join(lines[start_idx:end_idx]):
            print(f"SKIP: {dict_name} already has new keys")
            continue
            
        # Insert block before the closing '] }'
        block_lines = block.rstrip('\n').split('\n')
        for j, bl in enumerate(block_lines):
            lines.insert(end_idx + j, bl)
        
        # Rebuild to re-find subsequent dicts  
        content = '\n'.join(lines)
        lines = content.split('\n')
        print(f"OK: Added {len(NEW_KEYS)} keys to {dict_name}")

    with open(LOCALIZATION_FILE, "w") as f:
        f.write('\n'.join(lines))
    
    print(f"\nDone! Added {len(NEW_KEYS)} keys to 15 language dicts.")

if __name__ == "__main__":
    main()
