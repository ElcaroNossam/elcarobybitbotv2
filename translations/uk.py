# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu
    'welcome':                     '👋 Привіт! Оберіть дію:',
    'no_strategies':               '❌ Немає',
    'guide_caption':               '📚 Посібник користувача\n\nПрочитайте цей посібник, щоб дізнатися як налаштувати стратегії та ефективно використовувати бота.',
    'privacy_caption':             '📜 Політика конфіденційності та Умови використання\n\nБудь ласка, уважно прочитайте цей документ.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 Секрет',
    'button_api_settings':         '🔑 API',
    'button_balance':              '💰 Баланс USDT',
    'button_orders':               '📜 Мої ордери',
    'button_positions':            '📊 Позиції',
    'button_percent':              '🎚 % на угоду',
    'button_coins':                '💠 Група монет',
    'button_market':               '📈 Ринок',
    'button_manual_order':         '✋ Ручний ордер',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ Скасувати ордер',
    'button_limit_only':           '🎯 Лише Limit',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_settings':             '📋 Мій конфіг',
    'button_indicators':           '💡 Індикатори',
    'button_support':              '🆘 Підтримка',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 Режим TP/SL: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Фіксований %',

    # Limits
    'limit_positions_exceeded':    '🚫 Перевищено ліміт відкритих позицій ({max})',
    'limit_limit_orders_exceeded': '🚫 Перевищено ліміт ордерів Limit ({max})',

    # Languages
    'select_language':             'Оберіть мову:',
    'language_set':                'Мову встановлено:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'Оберіть тип ордера:',
    'limit_order_format': (
        "Введіть параметри ордера Limit у форматі:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "де SIDE = LONG або SHORT\n"
        "Приклад: `BTCUSDT LONG 20000 0.1`\n\n"
        "Щоб скасувати, надішліть ❌ Скасувати ордер"
    ),
    'market_order_format': (
        "Введіть параметри ордера Market у форматі:\n"
        "`SYMBOL SIDE QTY`\n"
        "де SIDE = LONG або SHORT\n"
        "Приклад: `BTCUSDT SHORT 0.1`\n\n"
        "Щоб скасувати, надішліть ❌ Скасувати ордер"
    ),
    'order_success':               '✅ Ордер успішно створено!',
    'order_create_error':          '❌ Не вдалося створити ордер: {msg}',
    'order_fail_leverage':         (
        "❌ Ордер не створено: надто велике плече на акаунті Bybit для цього розміру.\n"
        "Зменшіть плече в налаштуваннях Bybit."
    ),
    'order_parse_error':           '❌ Помилка розбору: {error}',
    'price_error_min':             '❌ Помилка ціни: має бути ≥{min}',
    'price_error_step':            '❌ Помилка ціни: має бути кратною {step}',
    'qty_error_min':               '❌ Помилка кількості: має бути ≥{min}',
    'qty_error_step':              '❌ Помилка кількості: має бути кратною {step}',

    # Loading…
    'loader':                      '⏳ Збираємо дані…',

    # Market command
    'market_status_heading':       '*Стан ринку:*',
    'market_dominance_header':    'Топ монет за домінацією',
    'market_total_header':        'Загальна капіталізація',
    'market_indices_header':      'Індекси ринку',
    'usdt_dominance':              'Домінування USDT',
    'btc_dominance':               'Домінування BTC',
    'dominance_rising':            '↑ зростає',
    'dominance_falling':           '↓ падає',
    'dominance_stable':            '↔️ стабільно',
    'dominance_unknown':           '❔ немає даних',
    'btc_price':                   'Ціна BTC',
    'last_24h':                    'за 24 години',
    'alt_signal_label':            'Сигнал альткоїнів',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Останні новини (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'Не знайдено ціну виконання для закриття',

    # /account
    'account_balance':             '💰 Баланс USDT: `{balance:.2f}`',
    'account_realized_header':     '📈 *Реалізований PnL:*',
    'account_realized_day':        '  • Сьогодні : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 днів   : `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *Нереалізований PnL:*',
    'account_unreal_total':        '  • Разом    : `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % від IM : `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Ваші налаштування:*',
    'config_percent':              '• 🎚 % на угоду      : `{percent}%`',
    'config_coins':                '• 💠 Монети          : `{coins}`',
    'config_limit_only':           '• 🎯 Ордери Limit    : {state}',
    'config_atr_mode':             '• 🏧 SL за ATR       : {atr}',
    'config_trade_oi':             '• 📊 Торгівля OI     : {oi}',
    'config_trade_rsi_bb':         '• 📈 Торгівля RSI+BB : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%             : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%             : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 Немає відкритих ордерів',
    'open_orders_header':          '*📒 Відкриті ордери:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Сторона: `{side}`\n"
        "   • Кількість: `{qty}`\n"
        "   • Ціна    : `{price}`\n"
        "   • ID      : `{id}`"
    ),
    'open_orders_error':           '❌ Помилка отримання ордерів: {error}',

    # Manual coin selection
    'enter_coins':                 "Введіть символи через кому, напр.:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Обрані монети: {coins}',

    # Positions
    'no_positions':                '🚫 Немає відкритих позицій',
    'positions_header':            '📊 Ваші відкриті позиції:',
    'position_item':               (
        "— Позиція #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • Розмір           : {size}\n"
        "  • Ціна входу       : {avg:.8f}\n"
        "  • Марк-ціна        : {mark:.8f}\n"
        "  • Ліквідація       : {liq}\n"
        "  • Початкова маржа  : {im:.2f}\n"
        "  • Маржа утримання  : {mm:.2f}\n"
        "  • Баланс позиції   : {pm:.2f}\n"
        "  • Take Profit      : {tp}\n"
        "  • Stop Loss        : {sl}\n"
        "  • Нереал. PnL      : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'positions_overall':           'Загальний нереал. PnL: {pnl:+.2f} ({pct:+.2f}%)',

    # Position management (inline)
    'open_positions_header':       '📊 *Відкриті позиції*',
    'positions_count':             'позицій',
    'positions_count_total':       'Всього позицій',
    'total_unrealized_pnl':        'Загальний нереал. PnL',
    'total_pnl':                   'Загальний PnL',
    'btn_close_short':             'Закрити',
    'btn_close_all':               'Закрити всі позиції',
    'btn_close_position':          'Закрити позицію',
    'btn_confirm_close':           'Підтвердити закриття',
    'btn_confirm_close_all':       'Так, закрити всі',
    'btn_cancel':                  '❌ Скасувати',
    'btn_back':                    '🔙 Назад',
    'confirm_close_position':      'Закрити позицію',
    'confirm_close_all':           'Закрити ВСІ позиції',
    'position_not_found':          'Позицію не знайдено або вже закрито',
    'position_already_closed':     'Позицію вже закрито',
    'position_closed_success':     'Позицію закрито',
    'position_close_error':        'Помилка закриття позиції',
    'positions_closed':            'Позиції закрито',
    'errors':                      'Помилки',

    # % per trade
    'set_percent_prompt':          'Введіть відсоток балансу на одну угоду (напр. 2.5):',
    'percent_set_success':         '✅ % на угоду встановлено: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Лише ордери Limit: {state}',
    'feature_limit_only':          'Лише Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Індикатори Elcaro*',
    'indicator_1':                 '1. RSI + BB (Індекс відносної сили + Смуги Боллінджера)',
    'indicator_2':                 '2. Торговий хаос (Trading Chaos)',
    'indicator_3':                 '3. Адаптивний тренд',
    'indicator_4':                 '4. Динамічна регресія',

    # Support
    'support_prompt':              '✉️ Потрібна допомога? Натисніть нижче:',
    'support_button':              'Зв’язатися з підтримкою',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 Немає відкритих позицій',
    'update_tpsl_prompt':          'Введіть SYMBOL TP SL, напр.:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Невірний формат. Використовуйте: SYMBOL TP SL\nНапр.: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Введіть ваш Bybit API Key:',
    'api_saved':                   '✅ Ключ API збережено',
    'enter_secret':                'Введіть Bybit API Secret:',
    'secret_saved':                '✅ Секрет API збережено',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ Введіть значення TP%',
    'tp_set_success':              '✅ TP% встановлено: {pct}%',
    'enter_sl':                    '❌ Введіть значення SL%',
    'sl_set_success':              '✅ SL% встановлено: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: потрібно 4 аргументи (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: потрібно 3 аргументи (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE має бути LONG або SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ Ключ/секрет API не задані',
    'api_missing_notice':          '⚠️ У вас не налаштовані API ключі біржі. Додайте API Key та Secret в налаштуваннях (кнопки 🔑 API та 🔒 Secret), інакше бот не зможе торгувати за вас.',
    'bybit_invalid_response':      '❌ Невірна відповідь Bybit',
    'bybit_error':                 '❌ Помилка Bybit {path}: {data}',

    # Auto notifications
    'new_position': (
        '🚀 Нова позиція {symbol} @ {entry:.6f}, розмір={size}\n'
        '📍 {exchange} • {market_type}'
    ),
    'sl_auto_set':                 '🛑 SL виставлено автоматично: {price:.6f}',
    'auto_close_position':         '⏱ Позицію {symbol} (TF={tf}) відкрито > {tf} та вона збиткова — закрито автоматично.',
    'position_closed': (
        '🔔 Позицію {symbol} закрито через *{reason}*:\n'
        '• Strategy: `{strategy}`\n'
        '• Вхід : `{entry:.8f}`\n'
        '• Вихід: `{exit:.8f}`\n'
        '• PnL  : `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '📍 {exchange} • {market_type}'
    ),

    # Entries & errors - уніфікований формат з повною інформацією
    'oi_limit_entry':              '📉 *OI Лiміт Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit помилка: {msg}',
    'oi_market_entry':             '📉 *OI Маркет Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Кіл-ть: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI Market помилка: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Кіл-ть: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Ліміт Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Кіл-ть: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Маркет Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Кіл-ть: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Кіл-ть: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB Market помилка: {msg}',

    'oi_analysis':                 '📊 *Аналіз OI {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Ліміт Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Кіл-ть: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit помилка: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Маркет Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Кіл-ть: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Кіл-ть: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market помилка: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>Недостатньо коштів!</b>\n\n💰 На вашому {account_type} акаунті недостатньо коштів для відкриття позиції.\n\n<b>Рішення:</b>\n• Поповніть баланс\n• Зменшіть розмір позиції (% від депозиту)\n• Зменшіть плече\n• Закрийте частину відкритих позицій',
    'insufficient_balance_error_extended': '❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Занадто високе плече!</b>\n\n⚙️ Встановлене плече перевищує максимум для цього символу.\n\n<b>Максимально дозволено:</b> {max_leverage}x\n\n<b>Рішення:</b> Перейдіть до налаштувань стратегії та зменшіть плече.',
    


    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Ліміт Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit помилка: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Маркет Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market помилка: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *Elcaro Ліміт Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Elcaro Limit помилка: {msg}',
    'elcaro_market_entry':         '🔥 *Elcaro Маркет Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Elcaro Market помилка: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci Ліміт Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci Limit помилка: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci Маркет Вхід*\n• {symbol} {side}\n• Ціна: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci Market помилка: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 Адмін-панель:',
    'admin_pause':                 '⏸️ Торгівлю та сповіщення призупинено для всіх.',
    'admin_resume':                '▶️ Торгівлю та сповіщення відновлено для всіх.',
    'admin_closed':                '✅ Закрито всього {count} {type}.',
    'admin_canceled_limits':       '✅ Скасовано {count} ордерів Limit.',

    # Coin groups
    'select_coin_group':           'Оберіть групу монет:',
    'group_all':                   'ALL',
    'group_top100':                'TOP100',
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ Групу монет встановлено: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *Аналіз RSI+BB*\n'
        '• Ціна : `{price:.6f}`\n'
        '• RSI  : `{rsi:.1f}` ({zone})\n'
        '• BB верхня: `{bb_hi:.4f}`\n'
        '• BB нижня : `{bb_lo:.4f}`\n\n'
        '*Вхід MARKET {side} за RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'Перепроданість (<30)',
    'rsi_zone_overbought':         'Перекупленість (>70)',
    'rsi_zone_neutral':            'Нейтральна (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ Некоректні TP/SL для LONG.\n'
        'Поточна ціна: {current:.2f}\n'
        'Очікувано: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ Некоректні TP/SL для SHORT.\n'
        'Поточна ціна: {current:.2f}\n'
        'Очікувано: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 У вас немає відкритої позиції по {symbol}',
    'tpsl_set_success':            '✅ Для {symbol} виставлено TP={tp:.2f} та SL={sl:.2f}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Мова',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Режим стоп: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ Лімітний ордер для {symbol} виконано @ {price}',
    'limit_order_cancelled':       '⚠️ Лімітний ордер для {symbol} (ID: {order_id}) скасовано.',
    'fixed_sl_tp':                 '✅ {symbol}: SL {sl}, TP {tp} встановлено',
    'tp_part':                     ', TP встановлено на {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL на {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL на {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP ініціалізовано на {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL перенесено в б/з при {entry}',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP оновлено до {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Позицію {symbol} закрито, але запис не виконано: {error}\n'
        'Зверніться до підтримки.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Фіксований %',

    # System notices
    'db_quarantine_notice':        '⚠️ Логи тимчасово призупинено. Тихий режим на 1 годину.',

    # Fallback
    'fallback':                    '❓ Скористайтесь кнопками меню.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 Вас заблоковано.',
    'invite_only': '🔒 Доступ лише за запрошенням. Зачекайте на рішення адміна.',
    'need_terms': '⚠️ Спершу прийміть правила: /terms',
    'please_confirm': 'Будь ласка, підтвердіть:',
    'terms_ok': '✅ Дякуємо! Правила прийнято.',
    'terms_declined': '❌ Ви відхилили правила. Доступ закрито. Повернутися: /terms.',
    'usage_approve': 'Використання: /approve <user_id>',
    'usage_ban': 'Використання: /ban <user_id>',
    'not_allowed': 'Заборонено',
    'bad_payload': 'Невірні дані',
    'unknown_action': 'Невідома дія',

    'title': 'Новий користувач',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Ім’я: {name}\n'
        '• Юзернейм: {uname}\n'
        '• Lang: {lang}\n'
        '• Allowed: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve': '✅ Схвалити',
    'btn_ban': '⛔️ Бан',
    'admin_notify_fail': 'Не вдалося повідомити адміна: {e}',
    'moderation_approved': '✅ Схвалено: {target}',
    'moderation_banned': '⛔️ Заблоковано: {target}',
    'approved_user_dm': '✅ Доступ схвалено. Натисніть /start.',
    'banned_user_dm': '🚫 Вас заблоковано.',

    'users_not_found': '😕 Користувачів не знайдено.',
    'users_page_info': '📄 Сторінка {page}/{pages} — всього: {total}',
    'user_card_html': (
        '<b>👤 Користувач</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Ім’я: {full_name}\n'
        '• Юзернейм: {uname}\n'
        '• Lang: <code>{lang}</code>\n'
        '• Allowed: {allowed}\n'
        '• Banned: {banned}\n'
        '• Terms: {terms}\n'
        '• % на угоду: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 Чорний список',
    'btn_delete_user': '🗑 Видалити з БД',
    'btn_prev': '⬅️ Назад',
    'btn_next': '➡️ Далі',
    'nav_caption': '🧭 Навігація:',
    'bad_page': 'Невірна сторінка.',
    'admin_user_delete_fail': '❌ Не вдалося видалити {target}: {error}',
    'admin_user_deleted': '🗑 Користувача {target} видалено з БД.',
    'user_access_approved': '✅ Доступ схвалено. Натисніть /start.',

    'admin_pause_all': '⏸️ Паузa для всіх',
    'admin_resume_all': '▶️ Відновити',
    'admin_close_longs': '🔒 Закр. всі лонги',
    'admin_close_shorts': '🔓 Закр. всі шорти',
    'admin_cancel_limits': '❌ Видалити ліміткu',
    'admin_users': '👥 Юзери',
    'admin_pause_notice': '⏸️ Торгівля та розсилки призупинені для всіх.',
    'admin_resume_notice': '▶️ Торгівля та розсилки відновлені для всіх.',
    'type_longs': 'лонги',
    'type_shorts': 'шорти',
    'admin_closed_total': '✅ Закрито всього {count} {type}.',
    'admin_canceled_limits_total': '✅ Скасовано {count} лімітних ордерів.',

    'terms_btn_accept': '✅ Приймаю',
    'terms_btn_decline': '❌ Відхиляю',

    'emoji_long': '🟢',
    'emoji_short': '🔴',
    'emoji_neutral': '⚪️',

    # Scalper Strategy
    'button_scalper':                '🎯 Scalper',
    'button_elcaro':                 '🔥 Elcaro',
    'button_fibonacci':                '📐 Вайкоф',
    'config_trade_scalper':          '🎯 Scalper: {state}',
    'config_trade_elcaro':           '🔥 Elcaro: {state}',
    'config_trade_fibonacci':          '📐 Вайкоф: {state}',

    # API Settings
    'api_settings_title':          '🔑 <b>Налаштування API</b>',
    'api_demo_title':              '🧪 Демо акаунт',
    'api_real_title':              '💼 Реальний акаунт',
    'api_key_set':                 '✅ Встановлено',
    'api_key_not_set':             '❌ Не встановлено',
    'api_trading_mode':            '📍 <b>Режим торгівлі:</b>',
    'api_mode_demo':               '🧪 Демо',
    'api_mode_real':               '💼 Реальний',
    'api_mode_both':               '🔄 Обидва',
    'api_btn_demo_key':            '🧪 Демо API Key',
    'api_btn_demo_secret':         '🧪 Демо Secret',
    'api_btn_real_key':            '💼 Реал API Key',
    'api_btn_real_secret':         '💼 Реал Secret',
    'api_btn_delete_demo':         '🗑 Видалити демо',
    'api_btn_delete_real':         '🗑 Видалити реал',
    'api_btn_mode_demo':           '🧪 Торгувати демо',
    'api_btn_mode_real':           '💼 Торгувати реал',
    'api_btn_mode_both':           '🔄 Торгувати обидва',
    'api_btn_back':                '⬅️ Назад',
    'api_enter_demo_key':          '🧪 Введіть ваш <b>Демо API Key</b>:',
    'api_enter_demo_secret':       '🧪 Введіть ваш <b>Демо API Secret</b>:',
    'api_enter_real_key':          '💼 Введіть ваш <b>Реальний API Key</b>:\n\n⚠️ <b>Увага:</b> Це для торгівлі реальними грошима!',
    'api_enter_real_secret':       '💼 Введіть ваш <b>Реальний API Secret</b>:\n\n⚠️ <b>Увага:</b> Це для торгівлі реальними грошима!',
    'api_key_saved':               '✅ API Key успішно збережено!',
    'api_secret_saved':            '✅ API Secret успішно збережено!',
    'api_deleted':                 '🗑 API дані видалено для {account}',
    'api_mode_changed':            '✅ Режим торгівлі змінено на: <b>{mode}</b>',
    'api_mode_both_warning':       '⚠️ <b>Режим "Обидва":</b> Сигнали виконуватимуться на ОБОХ демо та реальному акаунтах!',
    'api_key_hidden':              '••••••••{suffix}',
    'api_test_connection':         '🔄 Тест з\'єднання',
    'api_connection_ok':           '✅ З\'єднання OK! Баланс: {balance} USDT',
    'api_connection_fail':         '❌ Помилка з\'єднання: {error}',
    'api_test_success':            'Підключення успішне!',
    'api_test_no_keys':            'API ключі не встановлені',
    'api_test_set_keys':           'Спочатку встановіть API Key і Secret.',
    'api_test_failed':             'Помилка підключення',
    'api_test_error':              'Помилка',
    'api_test_check_keys':         'Перевірте ваші API ключі.',
    'api_test_status':             'Статус',
    'api_test_connected':          'Підключено',
    'balance_wallet':              'Баланс гаманця',
    'balance_equity':              'Еквіті',
    'balance_available':           'Доступно',

    # Spot Trading
    'api_spot_trading':            '💹 Спот торгівля',
    'api_spot_enabled':            '💹 <b>Спот торгівля:</b> ✅ УВІМК',
    'api_spot_disabled':           '💹 <b>Спот торгівля:</b> ❌ ВИМК',
    'api_spot_toggled':            'Спот торгівля: {status}',
    'spot_settings_title':         '💹 <b>Налаштування Спот DCA</b>',
    'spot_coins':                  '🪙 Монети: {coins}',
    'spot_coins_label':            'Coins',
    'spot_dca_amount':             '💵 Сума DCA: {amount} USDT',
    'spot_dca_amount_label':       'DCA Amount',
    'spot_dca_frequency':          '⏰ Частота: {freq}',
    'spot_freq_daily':             'Щодня',
    'spot_freq_weekly':            'Щотижня',
    'spot_freq_monthly':           'Щомісяця',
    'spot_buy_now':                '💰 Купити зараз',
    'spot_auto_dca':               '🔄 Авто DCA: {status}',
    'spot_auto_dca_label':         'Auto DCA',
    'spot_next_buy':               '⏳ Наст. покупка: {time}',
    'spot_total_invested':         '📊 Всього вкладено: {amount} USDT',
    'spot_holdings':               '💎 Активи: {holdings}',
    'spot_buy_success':            '✅ Куплено {qty} {coin} за {amount} USDT',
    'spot_buy_failed':             '❌ Покупка не вдалася: {error}',
    'spot_balance':                '💰 Спот баланс: {balance}',
    'spot_no_balance':             '❌ Спот баланс не знайдено',
    'spot_order_placed':           '✅ Спот ордер розміщено: {side} {qty} {coin}',
    'button_spot_settings':        '💹 Налаштування спот',
    'spot_btn_coins':              '🪙 Монети',
    'spot_btn_amount':             '💵 Сума',
    'spot_btn_frequency':          '⏰ Частота',
    'spot_btn_auto_toggle':        '🔄 Авто DCA',
    'spot_btn_buy_now':            '💰 Купити',
    'spot_btn_back':               '⬅️ Назад',
    'spot_enter_amount':           'Введіть суму DCA в USDT:',
    'spot_amount_saved':           '✅ Сума DCA: {amount} USDT',
    'spot_select_coins':           'Оберіть монети для Спот DCA:',
    'spot_coins_saved':            '✅ Монети спот: {coins}',
    'spot_select_frequency':       'Оберіть частоту DCA:',
    'spot_frequency_saved':        '✅ Частота: {freq}',
    'spot_auto_enabled':           '✅ Авто DCA увімкнено',
    'spot_auto_disabled':          '❌ Авто DCA вимкнено',
    'spot_not_enabled':            '❌ Спот торгівля не увімкнена. Увімкніть у налаштуваннях API.',

    # Strategy trading mode
    'strat_mode_global':           '🌐 Глобальний',
    'strat_mode_demo':             '🧪 Демо',
    'strat_mode_real':             '💰 Реальний',
    'strat_mode_both':             '🔄 Обидва',
    'strat_mode_changed':          '✅ Режим торгівлі {strategy}: {mode}',

    'feature_scalper':               'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':            '🔥 Elcaro limit-entry {symbol} @ {price:.6f}',
    'elcaro_limit_error':            '❌ Elcaro limit-entry error: {msg}',
    'elcaro_market_entry':           '🚀 Elcaro market {symbol} @ {price:.6f}',
    'elcaro_market_error':           '❌ Elcaro market error: {msg}',
    'elcaro_market_ok':              '🔥 Elcaro: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'elcaro_analysis':               'Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':                'Elcaro',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 Fibonacci лімітний вхід {symbol} @ {price:.6f}',
    'fibonacci_limit_error':         '❌ Fibonacci помилка лімітного входу: {msg}',
    'fibonacci_market_entry':        '🚀 Fibonacci ринковий {symbol} @ {price:.6f}',
    'fibonacci_market_error':        '❌ Fibonacci помилка ринкового входу: {msg}',
    'fibonacci_market_ok':           '📐 Fibonacci: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'fibonacci_analysis':            'Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    'scalper_limit_entry':           'Scalper: ліміт {symbol} @ {price}',
    'scalper_limit_error':           'Scalper ліміт помилка: {msg}',
    'scalper_market_entry':          '🚀 Scalper маркет {symbol} @ {price:.6f}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper помилка: {msg}',
    'scalper_analysis':              'Scalper: {side} @ {price}',
    'feature_scryptomera':           'Scryptomera',
    


    # Strategy Settings
    'button_strategy_settings':      '🎯 Стратегії',
    'strategy_settings_header':      '⚙️ *Налаштування стратегій*',
    'strategy_param_header':         '⚙️ *Налаштування {name}*',
    'using_global':                  'Глобальні налаштування',
    'global_default':                'Глоб.',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ Налаштування DCA',
    'dca_settings_header':           '⚙️ *Налаштування DCA (Фʼючерси)*\n\n',
    'dca_toggle':                    'DCA увімкнено',
    'dca_status':                    'Статус',
    'dca_description':               '_DCA додасть до позиції, коли ціна рухається проти вас._',
    'dca_leg1':                      '📉 DCA Нога 1 %',
    'dca_leg2':                      '📉 DCA Нога 2 %',
    'param_percent':                 '📊 Вхід %',
    'param_sl':                      '🔻 Стоп-Лосс %',
    'param_tp':                      '🔺 Тейк-Профіт %',
    'param_reset':                   '🔄 Скинути до глобальних',
    'btn_close':                     '❌ Закрити',
    'prompt_entry_pct':              'Введіть % входу (ризик на угоду):',
    'prompt_sl_pct':                 'Введіть % Стоп-Лосса:',
    'prompt_tp_pct':                 'Введіть % Тейк-Профіту:',
    'prompt_atr_periods':            'Введіть періоди ATR (напр., 7):',
    'prompt_atr_mult':               'Введіть множник ATR для trailing SL (напр., 1.0):',
    'prompt_atr_trigger':            'Введіть % активації ATR (напр., 2.0):',
    'prompt_dca_leg1':               'Введіть % для DCA Ноги 1 (напр., 10):',
    'prompt_dca_leg2':               'Введіть % для DCA Ноги 2 (напр., 25):',
    'settings_reset':                'Налаштування скинуто до глобальних',
    'strat_setting_saved':           '✅ {name} {param} встановлено на {value}',
    'dca_setting_saved':             '✅ DCA {leg} встановлено на {value}%',
    'invalid_number':                '❌ Некоректне число. Введіть значення від 0 до 100.',
    'dca_10pct':                     'DCA −{pct}%: докуп {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: докуп {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: Нога1=-{dca1}%, Нога2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 Періоди ATR',
    'param_atr_mult':                '📉 Множник ATR (крок SL)',
    'param_atr_trigger':             '🎯 Активація ATR %',

    # Hardcoded strings fix
    'terms_unavailable':             'Умови використання недоступні. Зверніться до адміністратора.',
    'terms_confirm_prompt':          'Підтвердіть:',
    'your_id':                       'Ваш ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Помилка: {msg}',
    'error_fetch_balance':           '❌ Помилка отримання балансу: {error}',
    'error_fetch_orders':            '❌ Помилка отримання ордерів: {error}',
    'error_occurred':                '❌ Помилка: {error}',

    # Trading Statistics
    'button_stats':                  '📊 Статистика',
    'stats_title':                   'Статистика торгівлі',
    'stats_strategy':                'Стратегія',
    'stats_period':                  'Період',
    'stats_overview':                'Огляд',
    'stats_total_trades':            'Всього угод',
    'stats_closed':                  'Закрито',
    'stats_open':                    'Відкрито',
    'stats_results':                 'Результати',
    'stats_winrate':                 'Вінрейт',
    'stats_total_r':                 'Сумарний R',
    'stats_avg_r':                   'Середній R',
    'stats_by_direction':            'За напрямком',
    'stats_long':                    'Лонг',
    'stats_short':                   'Шорт',
    'stats_pnl':                     'Прибуток/Збиток',
    'stats_gross_profit':            'Прибуток',
    'stats_gross_loss':              'Збиток',
    'stats_total_pnl':               'Загальний P/L',
    'stats_profit_factor':           'PF',
    'stats_strategy_settings':       'Налаштування стратегії',
    'settings_entry_pct':            'Вхід',
    'settings_leverage':             'Плече',
    'settings_trading_mode':         'Режим',
    'settings_direction':            'Напрямок',
    'stats_all':                     '📈 Всі',
    'stats_oi':                      '📉 OI',
    'stats_rsi_bb':                  '📊 RSI+BB',
    'stats_scryptomera':             '🐱 Scryptomera',
    'stats_scalper':                 '⚡ Scalper',
    'stats_elcaro':                  '🔥 Elcaro',
    'stats_period_all':              'Весь час',
    'stats_period_today':            'Сьогодні',
    'stats_period_week':             'Тиждень',
    'stats_period_month':            'Місяць',
    'stats_demo':                    '🔵 Demo',
    'stats_real':                    '🟢 Real',

    # Scryptomera direction settings
    'param_direction': '🎯 Напрямок',
    'param_long_settings': '📈 Налаштування LONG',
    'param_short_settings': '📉 Налаштування SHORT',
    'dir_all': '🔄 ВСІ (LONG + SHORT)',
    'dir_long_only': '📈 Тільки LONG',
    'dir_short_only': '📉 Тільки SHORT',
    'scrypto_side_header': '{emoji} *Scryptomera {side} налаштування*',
    'scalper_side_header': '{emoji} *Scalper {side} налаштування*',
    'global_settings': '🌐 Глобальні налаштування',
    'global_settings_header': '🌐 *Глобальні торгові налаштування*',
    'global_settings_info': 'Ці налаштування використовуються за замовчуванням, коли не задані налаштування конкретної стратегії.',
    'prompt_long_entry_pct': '📈 LONG Entry % (ризик на угоду):',
    'prompt_long_sl_pct': '📈 LONG Stop-Loss %:',
    'prompt_long_tp_pct': '📈 LONG Take-Profit %:',
    'prompt_short_entry_pct': '📉 SHORT Entry % (ризик на угоду):',
    'prompt_short_sl_pct': '📉 SHORT Stop-Loss %:',
    'prompt_short_tp_pct': '📉 SHORT Take-Profit %:',

    # Order type settings
    'param_order_type': '📤 Тип ордера',
    'order_type_market': '⚡ Market ордери',
    'order_type_limit': '🎯 Limit ордери',

    # Leverage settings
    'param_leverage': '⚡ Плече',
    'prompt_leverage': 'Введіть плече (1-100):',
    'auto_default': 'Авто',

    # Coins group per strategy
    'param_coins_group': '🪙 Монети',
    'select_coins_for_strategy': '🪙 *Виберіть групу монет для {name}*',
    'group_global': '📊 Глобальна (загальне налаштування)',

    # Elcaro AI
    'elcaro_ai_info': '🤖 *AI-трейдинг*',
    'elcaro_ai_desc': '_Всі параметри парсяться з AI-сигналів автоматично:_',

    # Limit Ladder
    'limit_ladder': '📉 Лімітна драбина',
    'limit_ladder_header': '📉 *Налаштування лімітної драбини*',
    'limit_ladder_settings': '⚙️ Налаштування драбини',
    'ladder_count': 'Кількість ордерів',
    'ladder_info': 'Лімітні ордери нижче входу для DCA. Кожен ордер має % відступ від входу і % від депозиту.',
    'prompt_ladder_pct_entry': '📉 Введіть % нижче ціни входу для ордера {idx}:',
    'prompt_ladder_pct_deposit': '💰 Введіть % від депозиту для ордера {idx}:',
    'ladder_order_saved': '✅ Ордер {idx} збережено: -{pct_entry}% @ {pct_deposit}% депозиту',
    'ladder_orders_placed': '📉 Розміщено {count} лімітних ордерів для {symbol}',
    
    # Spot Trading Mode
    'spot_trading_mode': 'Режим торгівлі',
    'spot_btn_mode': 'Режим',
    
    # Stats PnL
    'stats_realized_pnl': 'Реалізований',
    'stats_unrealized_pnl': 'Нереалізований',
    'stats_combined_pnl': 'Загальний',
    'stats_spot': '💹 Спот',
    'stats_spot_title': 'Статистика Spot DCA',
    'stats_spot_config': 'Конфігурація',
    'stats_spot_holdings': 'Позиції',
    'stats_spot_summary': 'Підсумок',
    'stats_spot_current_value': 'Поточна вартість',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    # License status messages
    'no_license': '⚠️ Для використання цієї функції потрібна активна підписка.\n\nВикористайте /subscribe для придбання ліцензії.',
    'no_license_trading': '⚠️ Для торгівлі потрібна активна підписка.\n\nВикористайте /subscribe для придбання ліцензії.',
    'license_required': '⚠️ Ця функція потребує підписки {required}.\n\nВикористайте /subscribe для оновлення.',
    'trial_demo_only': '⚠️ Пробна ліцензія дозволяє лише демо-торгівлю.\n\nОновіться до Premium або Basic для реальної торгівлі: /subscribe',
    'basic_strategy_limit': '⚠️ Basic ліцензія на реальному акаунті дозволяє лише: {strategies}\n\nОновіться до Premium для всіх стратегій: /subscribe',
    
    # Subscribe menu
    'subscribe_menu_header': '💎 *Плани підписки*',
    'subscribe_menu_info': 'Оберіть план для розблокування торгових функцій:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Пробний (Безкоштовно)',
    'btn_enter_promo': '🎟 Промокод',
    'btn_my_subscription': '📋 Моя підписка',
    
    # Premium plan
    'premium_title': '💎 *ПРЕМІУМ ПЛАН*',
    'premium_desc': '''✅ Повний доступ до всіх функцій
✅ Всі 5 стратегій: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ Реальна + Демо торгівля
✅ Пріоритетна підтримка
✅ Динамічний SL/TP на основі ATR
✅ Лімітна драбина DCA
✅ Всі майбутні оновлення''',
    'premium_1m': '💎 1 Місяць — {price} TRC',
    'premium_3m': '💎 3 Місяці — {price} TRC (-10%)',
    'premium_6m': '💎 6 Місяців — {price} TRC (-20%)',
    'premium_12m': '💎 12 Місяців — {price} TRC (-30%)',
    
    # Basic plan
    'basic_title': '🥈 *БАЗОВИЙ ПЛАН*',
    'basic_desc': '''✅ Повний доступ до демо-акаунту
✅ Реальний акаунт: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Fibonacci, Spot — лише Premium
✅ Стандартна підтримка
✅ Динамічний SL/TP на основі ATR''',
    'basic_1m': '🥈 1 Місяць — {price} TRC',
    
    # Trial plan
    'trial_title': '🎁 *ПРОБНИЙ ПЛАН (БЕЗКОШТОВНО)*',
    'trial_desc': '''✅ Повний доступ до демо-акаунту
✅ Всі 5 стратегій на демо
❌ Реальна торгівля недоступна
⏰ Тривалість: 7 днів
🎁 Лише один раз''',
    'trial_activate': '🎁 Активувати пробний період',
    'trial_already_used': '⚠️ Ви вже використали безкоштовний пробний період.',
    'trial_activated': '🎉 Пробний період активовано! Ви маєте 7 днів повного демо-доступу.',
    
    # Payment
    'payment_select_method': '💳 *Оберіть спосіб оплати*',
    'btn_pay_trc': '◈ Triacelo Coin (TRC)',
    'btn_pay_ton': '💎 TON',
    'payment_trc_title': ' Оплата через TRC',
    'payment_trc_desc': 'З вас буде списано {amount} TRC за {plan} ({period}).',
    'payment_ton_title': '💎 Оплата через TON',
    'payment_ton_desc': '''Надішліть рівно *{amount} TON* на:

`{wallet}`

Після оплати натисніть кнопку нижче для перевірки.''',
    'btn_verify_ton': '✅ Я оплатив — Перевірити',
    'payment_processing': '⏳ Обробка платежу...',
    'payment_success': '🎉 Оплата успішна!\n\n{plan} активовано до {expires}.',
    'payment_failed': '❌ Помилка оплати: {error}',
    
    # My subscription
    'my_subscription_header': '📋 *Моя підписка*',
    'my_subscription_active': '''📋 *Поточний план:* {plan}
⏰ *Закінчується:* {expires}
📅 *Залишилось днів:* {days}''',
    'my_subscription_none': '❌ Немає активної підписки.\n\nВикористайте /subscribe для придбання плану.',
    'my_subscription_history': '📜 *Історія платежів:*',
    'subscription_expiring_soon': '⚠️ Ваша підписка {plan} закінчується через {days} днів!\n\nПоновіть зараз: /subscribe',
    
    # Promo codes
    'promo_enter': '🎟 Введіть ваш промокод:',
    'promo_success': '🎉 Промокод застосовано!\n\n{plan} активовано на {days} днів.',
    'promo_invalid': '❌ Недійсний промокод.',
    'promo_expired': '❌ Цей промокод прострочений.',
    'promo_used': '❌ Цей промокод вже використаний.',
    'promo_already_used': '❌ Ви вже використали цей промокод.',
    
    # Admin license management
    'admin_license_menu': '🔑 *Управління ліцензіями*',
    'admin_btn_grant_license': '🎁 Видати ліцензію',
    'admin_btn_view_licenses': '📋 Переглянути ліцензії',
    'admin_btn_create_promo': '🎟 Створити промокод',
    'admin_btn_view_promos': '📋 Переглянути промокоди',
    'admin_btn_expiring_soon': '⚠️ Скоро закінчуються',
    'admin_grant_select_type': 'Оберіть тип ліцензії:',
    'admin_grant_select_period': 'Оберіть період:',
    'admin_grant_enter_user': 'Введіть ID користувача:',
    'admin_license_granted': '✅ {plan} видано користувачу {uid} на {days} днів.',
    'admin_license_extended': '✅ Ліцензію продовжено на {days} днів для користувача {uid}.',
    'admin_license_revoked': '✅ Ліцензію скасовано для користувача {uid}.',
    'admin_promo_created': '✅ Промокод створено: {code}\nТип: {type}\nДнів: {days}\nМакс. використань: {max}',

    # =====================================================
    # ADMIN USER MANAGEMENT
    # =====================================================
    'admin_users_management': '👥 Користувачі',
    'admin_licenses': '🔑 Ліцензії',
    'admin_search_user': '🔍 Знайти користувача',
    'admin_users_menu': '👥 *Управління користувачами*\n\nОберіть фільтр або пошук:',
    'admin_all_users': '👥 Всі користувачі',
    'admin_active_users': '✅ Активні',
    'admin_banned_users': '🚫 Заблоковані',
    'admin_no_license': '❌ Без ліцензії',
    'admin_no_users_found': 'Користувачів не знайдено.',
    'admin_enter_user_id': '🔍 Введіть ID користувача для пошуку:',
    'admin_user_found': '✅ Користувача {uid} знайдено!',
    'admin_user_not_found': '❌ Користувача {uid} не знайдено.',
    'admin_invalid_user_id': '❌ Невірний ID користувача. Введіть число.',
    'admin_view_card': '👤 Переглянути картку',
    
    # User card
    'admin_user_card': '''👤 *Картка користувача*

📋 *ID:* `{uid}`
{status_emoji} *Статус:* {status}
📝 *Умови:* {terms}

{license_emoji} *Ліцензія:* {license_type}
📅 *Закінчується:* {license_expires}
⏳ *Залишилось днів:* {days_left}

🌐 *Мова:* {lang}
📊 *Режим торгівлі:* {trading_mode}
💰 *% на угоду:* {percent}%
🪙 *Монети:* {coins}

🔌 *API ключі:*
  Демо: {demo_api}
  Реальний: {real_api}

📈 *Стратегії:* {strategies}

📊 *Статистика:*
  Позиції: {positions}
  Угоди: {trades}
  PnL: {pnl}
  Winrate: {winrate}%

💳 *Платежі:*
  Всього: {payments_count}
  TRC: {total_trc}

📅 *Перший візит:* {first_seen}
🕐 *Останній візит:* {last_seen}
''',
    
    # User actions
    'admin_btn_grant_lic': '🎁 Видати',
    'admin_btn_extend': '⏳ Продовжити',
    'admin_btn_revoke': '🚫 Скасувати',
    'admin_btn_ban': '🚫 Заблокувати',
    'admin_btn_unban': '✅ Розблокувати',
    'admin_btn_approve': '✅ Схвалити',
    'admin_btn_message': '✉️ Повідомлення',
    'admin_btn_delete': '🗑 Видалити',
    
    'admin_user_banned': 'Користувача заблоковано!',
    'admin_user_unbanned': 'Користувача розблоковано!',
    'admin_user_approved': 'Користувача схвалено!',
    'admin_confirm_delete': '⚠️ *Підтвердіть видалення*\n\nКористувача {uid} буде остаточно видалено!',
    'admin_confirm_yes': '✅ Так, видалити',
    'admin_confirm_no': '❌ Скасувати',
    
    'admin_select_license_type': 'Оберіть тип ліцензії для користувача {uid}:',
    'admin_select_period': 'Оберіть період:',
    'admin_select_extend_days': 'Оберіть кількість днів для продовження користувачу {uid}:',
    'admin_license_granted_short': 'Ліцензію видано!',
    'admin_license_extended_short': 'Продовжено на {days} днів!',
    'admin_license_revoked_short': 'Ліцензію скасовано!',
    
    'admin_enter_message': '✉️ Введіть повідомлення для користувача {uid}:',
    'admin_message_sent': '✅ Повідомлення надіслано користувачу {uid}!',
    'admin_message_failed': '❌ Не вдалося надіслати повідомлення: {error}',

    # =====================================================
    # ADMIN PAYMENTS & REPORTS
    # =====================================================
    'admin_payments': '💳 Платежі',
    'admin_reports': '📊 Звіти',
    'admin_payments_menu': '💳 *Керування платежами*',
    'admin_all_payments': '📜 Всі платежі',
    'admin_no_payments_found': 'Платежів не знайдено.',
    
    'admin_reports_menu': '📊 *Звіти та аналітика*\n\nОберіть тип звіту:',
    'admin_global_stats': '📊 Глобальна статистика',
    'admin_demo_stats': '🎮 Демо статистика',
    'admin_real_stats': '💰 Реальна статистика',
    'admin_strategy_breakdown': '🎯 По стратегіях',
    'admin_top_traders': '🏆 Топ трейдери',
    'admin_user_report': '👤 Звіт користувача',
    'admin_enter_user_for_report': '👤 Введіть ID користувача для детального звіту:',
    'admin_generating_report': '📊 Генерую звіт для користувача {uid}...',
    'admin_view_report': '📊 Переглянути звіт',
    'admin_view_user': '👤 Картка користувача',

    # Missing keys
    'all_positions_closed': 'Всі позиції закриті',
    'btn_check_again': '🔄 Перевірити знову',
    'button_admin': '👑 Адмін',
    'button_licenses': '🔑 Ліцензії',
    'button_subscribe': '💎 Підписка',
    'current': 'Поточний',
    'entry': 'Вхід',
    'max_positions_reached': '⚠️ Досягнуто максимум позицій.',
    'payment_session_expired': '❌ Сесія оплати закінчилася.',
    'payment_ton_not_configured': '❌ TON платежі не налаштовані.',
    'payment_ton_not_found': '❌ Платіж не знайдено.',
    'payment_verifying': '⏳ Перевіряємо платіж...',
    'position': 'Позиція',
    'size': 'Розмір',
    'stats_fibonacci': '📐 Fibonacci',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 Веб-панель",
    "button_switch_exchange": "🔄 Змінити біржу",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "Налаштування HyperLiquid",
    "hl_trading_enabled": "Торгівля на HyperLiquid",
    "hl_reset_settings": "🔄 Скинути на налаштування Bybit",



    # === HyperLiquid та інші додаткові рядки ===
    'cancelled': '❌ Скасовано.',
    'entry_pct_range_error': '❌ % входу має бути від 0.1 до 100.',
    'hl_no_history': '📭 Немає історії торгів на HyperLiquid.',
    'hl_no_orders': '📭 Немає відкритих ордерів на HyperLiquid.',
    'hl_no_positions': '📭 Немає відкритих позицій на HyperLiquid.',
    'hl_setup_cancelled': '❌ Налаштування HyperLiquid скасовано.',
    'invalid_amount': '❌ Невірне число. Введіть коректну суму.',
    'leverage_range_error': '❌ Плече має бути від 1 до 100.',
    'max_amount_error': '❌ Максимальна сума 100,000 USDT',
    'min_amount_error': '❌ Мінімальна сума 1 USDT',
    'sl_tp_range_error': '❌ SL/TP % має бути від 0.1 до 500.',
    
    # =====================================================
    # DEEP LOSS - ПОЗИЦІЯ В ГЛИБОКОМУ МІНУСІ
    # =====================================================
    'btn_close_position': '❌ Закрити позицію',
    'btn_enable_dca': '📈 Увімкнути DCA добір',
    'btn_ignore': '🔇 Ігнорувати',
    'deep_loss_alert': '⚠️ <b>Позиція в глибокому мінусі!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Збиток: <code>{loss_pct:.2f}%</code>\n💰 Вхід: <code>{entry}</code>\n📍 Поточна: <code>{mark}</code>\n\n❌ Стоп-лосс неможливо встановити вище ціни входу.\n\n<b>Що робити?</b>\n• <b>Закрити</b> - зафіксувати збиток\n• <b>DCA добір</b> - усереднити позицію доборами\n• <b>Ігнорувати</b> - залишити як є',
    'position_already_closed': '❌ Позиція {symbol} вже закрита.',
    'deep_loss_closed': '✅ Позиція {symbol} закрита.\n\nЗбиток зафіксовано. Іноді краще прийняти невеликий збиток, ніж сподіватися на розворот.',
    'deep_loss_close_error': '❌ Помилка при закритті позиції: {error}',
    'dca_already_enabled': '✅ DCA добір вже увімкнено!\n\n📊 <b>{symbol}</b>\nБот буде автоматично додавати до позиції при просадці:\n• -10% → добір\n• -25% → добір\n\nЦе допоможе усереднити ціну входу.',
    'dca_enabled_for_symbol': '✅ DCA добір увімкнено!\n\n📊 <b>{symbol}</b>\nБот буде автоматично додавати до позиції при просадці:\n• -10% → добір (усереднення)\n• -25% → добір (усереднення)\n\n⚠️ DCA потребує достатній баланс для доборів.\nНалаштувати параметри: /strategy_settings',
    'dca_enable_error': '❌ Помилка: {error}',
    'deep_loss_ignored': '🔇 Зрозумів, позиція {symbol} залишена без змін.\n\n⚠️ Памʼятайте: без стоп-лосса ризик втрат необмежений.\nВи можете закрити позицію вручну через /positions',


    # DCA and Deep Loss notifications
    'fibonacci_desc': '_Вхід, SL, TP — за рівнями Фібоначчі з сигналу._',
    'fibonacci_info': '📐 *Стратегія Fibonacci Extension*',
    'prompt_min_quality': 'Введіть мінімальну якість % (0-100):',


    # Hardcore trading phrase
    'hardcore_mode': '💀 *ХАРДКОР РЕЖИМ*: Без пощади, без жалю. Тільки профіт або смерть! 🔥',
}
