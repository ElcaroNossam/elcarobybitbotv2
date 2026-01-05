# translations/ru.py
TEXTS = {
    # Главное меню
    'welcome':                     '👋 Привет! Выбери действие:',
    'no_strategies':               '❌ Нет',
    'guide_caption':               '📚 Руководство пользователя\n\nПрочитайте это руководство, чтобы узнать как настроить стратегии и эффективно использовать бота.',
    'privacy_caption':             '📜 Политика конфиденциальности и Условия использования\n\nПожалуйста, внимательно прочитайте этот документ.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 Secret',
    'button_api_settings':         '🔑 API',
    'button_subscribe':            '💎 Подписка',
    'button_balance':              '💰 Баланс USDT',
    'button_orders':               '📜 Мои ордера',
    'button_positions':            '📊 Позиции',
    'button_percent':              '🎚 % на сделку',
    'button_coins':                '💠 Группа монет',
    'button_market':               '📈 Рынок',
    'button_manual_order':         '✋ Ручной ордер',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ Отменить ордер',
    'button_limit_only':           '🎯 Только лимит',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_scalper':              '🎯 Scalper',
    'button_elcaro':               '🔥 Elcaro',
    'button_fibonacci':            '📐 Fibonacci',
    'button_settings':             '📋 Мой конфиг',
    'button_indicators':           '💡 Индикаторы',
    'button_support':              '🆘 Поддержка',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',
    'config_trade_scalper':        '🎯 Scalper: {state}',
    'config_trade_elcaro':         '🔥 Elcaro: {state}',
    'config_trade_fibonacci':      '📐 Fibonacci: {state}',

    # API настройки
    'api_settings_title':          '🔑 <b>Настройки API</b>',
    'api_demo_title':              '🧪 Демо аккаунт',
    'api_real_title':              '💼 Реальный аккаунт',
    'api_key_set':                 '✅ Установлен',
    'api_key_not_set':             '❌ Не установлен',
    'api_trading_mode':            '📍 <b>Режим торговли:</b>',
    'api_mode_demo':               '🧪 Демо',
    'api_mode_real':               '💼 Реал',
    'api_mode_both':               '🔄 Оба',
    'api_btn_demo_key':            '🧪 Демо API Key',
    'api_btn_demo_secret':         '🧪 Демо Secret',
    'api_btn_real_key':            '💼 Реал API Key',
    'api_btn_real_secret':         '💼 Реал Secret',
    'api_btn_delete_demo':         '🗑 Удалить Демо',
    'api_btn_delete_real':         '🗑 Удалить Реал',
    'api_btn_mode_demo':           '🧪 Торговать Демо',
    'api_btn_mode_real':           '💼 Торговать Реал',
    'api_btn_mode_both':           '🔄 Торговать Оба',
    'api_btn_back':                '⬅️ Назад',
    'api_enter_demo_key':          '🧪 Введите <b>Demo API Key</b>:',
    'api_enter_demo_secret':       '🧪 Введите <b>Demo API Secret</b>:',
    'api_enter_real_key':          '💼 Введите <b>Real API Key</b>:\n\n⚠️ <b>Внимание:</b> Это для торговли реальными деньгами!',
    'api_enter_real_secret':       '💼 Введите <b>Real API Secret</b>:\n\n⚠️ <b>Внимание:</b> Это для торговли реальными деньгами!',
    'api_key_saved':               '✅ API Key сохранён!',
    'api_secret_saved':            '✅ API Secret сохранён!',
    'api_deleted':                 '🗑 API ключи удалены для {account}',
    'api_mode_changed':            '✅ Режим торговли изменён на: <b>{mode}</b>',
    'api_mode_both_warning':       '⚠️ <b>Режим Оба:</b> Сигналы будут исполняться на ОБОИХ аккаунтах — Демо и Реал!',
    'api_key_hidden':              '••••••••{suffix}',
    'api_test_connection':         '🔄 Проверить подключение',
    'api_connection_ok':           '✅ Подключение OK! Баланс: {balance} USDT',
    'api_connection_fail':         '❌ Ошибка подключения: {error}',
    'api_test_success':            'Подключение успешно!',
    'api_test_no_keys':            'API ключи не установлены',
    'api_test_set_keys':           'Сначала установите API Key и Secret.',
    'api_test_failed':             'Ошибка подключения',
    'api_test_error':              'Ошибка',
    'api_test_check_keys':         'Проверьте ваши API ключи.',
    'api_test_status':             'Статус',
    'api_test_connected':          'Подключено',
    'balance_wallet':              'Баланс кошелька',
    'balance_equity':              'Эквити',
    'balance_available':           'Доступно',

    # Spot Trading
    'api_spot_trading':            '💹 Спот торговля',
    'api_spot_enabled':            '💹 <b>Спот торговля:</b> ✅ ВКЛ',
    'api_spot_disabled':           '💹 <b>Спот торговля:</b> ❌ ВЫКЛ',
    'api_spot_toggled':            'Спот торговля: {status}',
    'spot_settings_title':         '💹 <b>Настройки Спот DCA</b>',
    'spot_coins':                  '🪙 Монеты: {coins}',
    'spot_coins_label':            'Монеты',
    'spot_dca_amount':             '💵 Сумма DCA: {amount} USDT',
    'spot_dca_amount_label':       'Сумма DCA',
    'spot_dca_frequency':          '⏰ Частота: {freq}',
    'spot_freq_daily':             'Ежедневно',
    'spot_freq_weekly':            'Еженедельно',
    'spot_freq_monthly':           'Ежемесячно',
    'spot_buy_now':                '💰 Купить сейчас',
    'spot_auto_dca':               '🔄 Авто DCA: {status}',
    'spot_auto_dca_label':         'Авто DCA',
    'spot_next_buy':               '⏳ След. покупка: {time}',
    'spot_total_invested':         '📊 Всего вложено: {amount} USDT',
    'spot_holdings':               '💎 Активы: {holdings}',
    'spot_buy_success':            '✅ Куплено {qty} {coin} за {amount} USDT',
    'spot_buy_failed':             '❌ Покупка не удалась: {error}',
    'spot_balance':                '💰 Спот баланс: {balance}',
    'spot_no_balance':             '❌ Спот баланс не найден',
    'spot_order_placed':           '✅ Спот ордер размещён: {side} {qty} {coin}',
    'button_spot_settings':        '💹 Настройки спот',
    'spot_btn_coins':              '🪙 Монеты',
    'spot_btn_amount':             '💵 Сумма',
    'spot_btn_frequency':          '⏰ Частота',
    'spot_btn_auto_toggle':        '🔄 Авто DCA',
    'spot_btn_buy_now':            '💰 Купить',
    'spot_btn_back':               '⬅️ Назад',
    'spot_enter_amount':           'Введите сумму DCA в USDT:',
    'spot_amount_saved':           '✅ Сумма DCA: {amount} USDT',
    'spot_trading_mode':           'Режим торговли',
    'spot_btn_mode':               'Режим',
    'spot_select_coins':           'Выберите монеты для Спот DCA:',
    'spot_coins_saved':            '✅ Монеты спот: {coins}',
    'spot_select_frequency':       'Выберите частоту DCA:',
    'spot_frequency_saved':        '✅ Частота: {freq}',
    'spot_auto_enabled':           '✅ Авто DCA включён',
    'spot_auto_disabled':          '❌ Авто DCA выключен',
    'spot_not_enabled':            '❌ Спот торговля не включена. Включите в Настройках Стратегий.',

    # Режим торговли стратегии
    'strat_mode_global':           '🌐 Глобальный',
    'strat_mode_demo':             '🧪 Демо',
    'strat_mode_real':             '💰 Реал',
    'strat_mode_both':             '🔄 Оба',
    'strat_mode_changed':          '✅ Режим {strategy}: {mode}',

    # Инлайн-кнопки для ручного ордера
    'button_order_limit':          'Лимит',
    'button_order_market':         'Маркет',

    # Режим ATR / стоп-режим
    'atr_mode_changed':            '🔄 Режим TP/SL: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Фиксированный %',

    # Лимиты
    'limit_positions_exceeded':    '🚫 Превышен лимит открытых позиций ({max})',
    'limit_limit_orders_exceeded': '🚫 Превышен лимит лимит-ордеров ({max})',
    'max_positions_reached':       '⚠️ Достигнут максимум позиций. Новые сигналы будут пропускаться до закрытия позиции.',

    # Языки
    'select_language':             'Выберите язык:',
    'language_set':                'Язык установлен:',
    'lang_en':                     'English',

    # Ручной ордер
    'order_type_prompt':           'Выберите тип ордера:',
    'limit_order_format': (
        "Введите параметры лимит-ордера в формате:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "где SIDE = LONG или SHORT\n"
        "Пример: `BTCUSDT LONG 20000 0.1`\n\n"
        "Для отмены отправьте ❌ Отменить ордер"
    ),
    'market_order_format': (
        "Введите параметры маркет-ордера в формате:\n"
        "`SYMBOL SIDE QTY`\n"
        "где SIDE = LONG или SHORT\n"
        "Пример: `BTCUSDT SHORT 0.1`\n\n"
        "Для отмены отправьте ❌ Отменить ордер"
    ),
    'order_success':               '✅ Ордер успешно создан!',
    'order_create_error':          '❌ Не удалось создать ордер: {msg}',
    'order_fail_leverage':         (
        "❌ Ордер не создан: слишком высокое кредитное плечо для данного размера.\n"
        "Понизьте плечо в настройках Bybit."
    ),
    'order_parse_error':           '❌ Ошибка разбора: {error}',
    'price_error_min':             '❌ Ошибка цены: должно быть ≥{min}',
    'price_error_step':            '❌ Ошибка цены: шаг должен быть кратен {step}',
    'qty_error_min':               '❌ Ошибка количества: должно быть ≥{min}',
    'qty_error_step':              '❌ Ошибка количества: шаг должен быть кратен {step}',

    # Загрузка…
    'loader':                      '⏳ Собираю данные…',

    # Команда /market
    'market_status_heading':       '*Состояние рынка:*',
    'market_dominance_header':    'Топ монет по доминации',
    'market_total_header':        'Общая капитализация',
    'market_indices_header':      'Индексы рынка',
    'usdt_dominance':              'Доминация USDT',
    'btc_dominance':               'Доминация BTC',
    'dominance_rising':            '↑ растёт',
    'dominance_falling':           '↓ падает',
    'dominance_stable':            '↔️ стабильно',
    'dominance_unknown':           '❔ нет данных',
    'btc_price':                   'Цена BTC',
    'last_24h':                    'за 24ч',
    'alt_signal_label':            'Сигнал по альтам',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Последние новости (CoinDesk):*',

    # Ошибка цены исполнения
    'exec_price_not_found':        'Не удалось найти цену исполнения для закрытия',

    # /account
    'account_balance':             '💰 Баланс USDT: `{balance:.2f}`',
    'account_realized_header':     '📈 *Реализованный PnL:*',
    'account_realized_day':        '  • Сегодня: `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 дней: `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *Нереализованный PnL:*',
    'account_unreal_total':        '  • Итого: `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % от IM: `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Твои настройки:*',
    'config_percent':              '• 🎚 % на сделку      : `{percent}%`',
    'config_coins':                '• 💠 Монеты           : `{coins}`',
    'config_limit_only':           '• 🎯 Лимит-ордера     : {state}',
    'config_atr_mode':             '• 🏧 ATR-трейлинг SL  : {atr}',
    'config_trade_oi':             '• 📊 Торговля OI      : {oi}',
    'config_trade_rsi_bb':         '• 📈 Торговля RSI+BB  : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%              : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%              : `{sl}%`',

    # Открытые ордера
    'no_open_orders':              '🚫 Открытых ордеров нет',
    'open_orders_header':          '*📒 Твои открытые ордера:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Сторона: `{side}`\n"
        "   • Кол-во : `{qty}`\n"
        "   • Цена   : `{price}`\n"
        "   • ID     : `{id}`"
    ),
    'open_orders_error':           '❌ Ошибка получения ордеров: {error}',

    # Выбор монет
    'enter_coins':                 "Введи тикеры через запятую, напр.:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Монеты выбраны: {coins}',

    # Позиции
    'no_positions':                '🚫 Открытых позиций нет',
    'positions_header':            '📊 Твои открытые позиции:',
    'position_item':               (
        "— Позиция #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • Размер         : {size}\n"
        "  • Цена входа     : {avg:.8f}\n"
        "  • Марк-цена      : {mark:.8f}\n"
        "  • Ликвидация     : {liq}\n"
        "  • Initial Margin : {im:.2f}\n"
        "  • Maint Margin   : {mm:.2f}\n"
        "  • Баланс позиции : {pm:.2f}\n"
        "  • Take Profit    : {tp}\n"
        "  • Stop Loss      : {sl}\n"
        "  • Unreal PnL     : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'positions_overall':           'Итого Unreal PnL: {pnl:+.2f} ({pct:+.2f}%)',

    # Управление позициями (inline)
    'open_positions_header':       '📊 *Открытые позиции*',
    'positions_count':             'позиций',
    'positions_count_total':       'Всего позиций',
    'total_unrealized_pnl':        'Общий нереализ. P/L',
    'total_pnl':                   'Общий P/L',
    'btn_close_short':             'Закрыть',
    'btn_close_all':               'Закрыть все позиции',
    'btn_close_position':          'Закрыть позицию',
    'btn_confirm_close':           'Подтвердить закрытие',
    'btn_confirm_close_all':       'Да, закрыть все',
    'btn_cancel':                  '❌ Отмена',
    'btn_back':                    '🔙 Назад',
    'confirm_close_position':      'Закрыть позицию',
    'confirm_close_all':           'Закрыть ВСЕ позиции',
    'position_not_found':          'Позиция не найдена или уже закрыта',
    'position_already_closed':     'Позиция уже закрыта',
    'position_closed_success':     'Позиция закрыта',
    'position_close_error':        'Ошибка закрытия позиции',
    'positions_closed':            'Позиций закрыто',
    'all_positions_closed':        'Все позиции закрыты',
    'errors':                      'Ошибок',

    # Просмотр позиции
    'position':                    'Позиция',
    'entry':                       'Вход',
    'current':                     'Текущая',
    'size':                        'Размер',

    # % на сделку
    'set_percent_prompt':          'Введи процент баланса на сделку (например, 2.5):',
    'percent_set_success':         '✅ % на сделку установлен: {pct}%',

    # Переключатели
    'limit_only_toggled':          '🔄 Только-лимит {state}',
    'feature_limit_only':          'Только-лимит',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Индикаторы
    'indicators_header':           '📈 *Индикаторы Elcaro*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Торговый хаос',
    'indicator_3':                 '3. Адаптивный тренд',
    'indicator_4':                 '4. Динамическая регрессия',

    # Поддержка
    'support_prompt':              '✉️ Нужна помощь? Жми ниже:',
    'support_button':              'Связаться с поддержкой',

    # Обновление TP/SL
    'update_tpsl_no_positions':    '🚫 Нет открытых позиций',
    'update_tpsl_prompt':          'Введи SYMBOL TP SL, напр.:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Неверный формат. Используй: SYMBOL TP SL\nНапр.: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Введи свой Bybit API Key:',
    'api_saved':                   '✅ API Key сохранён',
    'enter_secret':                'Введи свой Bybit API Secret:',
    'secret_saved':                '✅ API Secret сохранён',

    # Ручная установка TP/SL (%)
    'enter_tp':                    '❌ Введи значение TP%',
    'tp_set_success':              '✅ TP% установлен: {pct}%',
    'enter_sl':                    '❌ Введи значение SL%',
    'sl_set_success':              '✅ SL% установлен: {pct}%',

    # Ошибки парсинга
    'parse_limit_error':           'Лимит: нужно 4 аргумента (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Маркет: нужно 3 аргумента (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE должен быть LONG или SHORT',

    # Помощник Bybit
    'api_missing_credentials':     '❌ Не заданы API Key/Secret',
    'api_missing_notice':          '⚠️ У вас не настроены API ключи биржи. Добавьте API Key и Secret в настройках (кнопки 🔑 API и 🔒 Secret), иначе бот не сможет торговать за вас.',
    'bybit_invalid_response':      '❌ Bybit вернул некорректный ответ',
    'bybit_error':                 '❌ Ошибка Bybit {path}: {data}',

    # Авто-уведомления
    'new_position': (
        '🚀 Новая позиция {symbol} @ {entry:.6f}, размер={size}\n'
        '📍 {exchange} • {market_type}'
    ),
    'sl_auto_set':                 '🛑 SL установлен автоматически: {price:.6f}',
    'auto_close_position':         '⏱ Позиция {symbol} (TF={tf}) открыта > {tf} и убыточна — закрыта автоматически.',
    'position_closed': (
        '🔔 Позиция {symbol} закрыта по *{reason}*:\n'
        '• Стратегия: `{strategy}`\n'
        '• Вход: `{entry:.8f}`\n'
        '• Выход: `{exit:.8f}`\n'
        '• PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '📍 {exchange} • {market_type}'
    ),

    # Входы/ошибки - унифицированный формат с полной информацией
    'oi_limit_entry':              '📉 *OI Лимит Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit ошибка: {msg}',
    'oi_market_entry':             '📉 *OI Маркет Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI ошибка\n🪙 {symbol} {side}\n\n{msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Лимит Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Маркет Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB ошибка\n🪙 {symbol} {side}\n\n{msg}',

    'oi_analysis':                 '📊 *Аналитика OI {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Лимит Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit ошибка: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Маркет Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market ошибка: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>Недостаточно средств!</b>\n\n💰 На вашем {account_type} аккаунте недостаточно средств для открытия позиции.\n\n<b>Решения:</b>\n• Пополните баланс\n• Уменьшите размер позиции (% от депозита)\n• Уменьшите плечо\n• Закройте часть открытых позиций',
    'insufficient_balance_error_extended': '❌ <b>Недостаточно средств!</b>\n\n📊 Стратегия: <b>{strategy}</b>\n🪙 Символ: <b>{symbol}</b> {side}\n\n💰 На вашем {account_type} аккаунте недостаточно средств.\n\n<b>Решения:</b>\n• Пополните баланс\n• Уменьшите размер позиции (% от депозита)\n• Уменьшите плечо\n• Закройте часть открытых позиций',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Слишком высокое плечо!</b>\n\n⚙️ Установленное плечо превышает максимум для этого символа.\n\n<b>Максимально допустимо:</b> {max_leverage}x\n\n<b>Решение:</b> Перейдите в настройки стратегии и уменьшите плечо.',
    
    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>Превышен лимит позиции!</b>\n\n📊 Стратегия: <b>{strategy}</b>\n🪙 Символ: <b>{symbol}</b>\n\n⚠️ Ваша позиция превысит максимально допустимый лимит.\n\n<b>Решения:</b>\n• Уменьшите плечо в настройках стратегии\n• Уменьшите размер позиции (% на сделку)\n• Закройте часть открытых позиций',

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Лимит Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit ошибка: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Маркет Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market ошибка: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *Elcaro Лимит Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Elcaro Limit ошибка: {msg}',
    'elcaro_market_entry':         '🔥 *Elcaro Маркет Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Elcaro Market ошибка: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

    # Fibonacci Extension Strategy
    'fibonacci_limit_entry':       '📐 *Fibonacci Лимит Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':       '❌ Fibonacci Limit ошибка: {msg}',
    'fibonacci_market_entry':      '📐 *Fibonacci Маркет Вход*\n• {symbol} {side}\n• Цена: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':         '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':      '❌ Fibonacci ошибка\n🪙 {symbol} {side}\n\n{msg}',
    'fibonacci_analysis':          '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':           'Fibonacci',

    # Админ-панель
    'admin_panel':                 '👑 Админ-панель:',
    'admin_pause':                 '⏸️ Торговля и уведомления приостановлены для всех.',
    'admin_resume':                '▶️ Торговля и уведомления возобновлены для всех.',
    'admin_closed':                '✅ Закрыто всего {count} {type}.',
    'admin_canceled_limits':       '✅ Отменено {count} лимитных ордеров.',

    # Группы монет
    'select_coin_group':           'Выбери группу монет:',
    'group_all':                   'ALL',
    'group_top100':                'TOP100',
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ Группа монет установлена: {group}',

    # RSI+BB анализ и помощь
    'rsi_bb_analysis':     (
        '📈 *RSI+BB анализ*\n'
        '• Цена: `{price:.6f}`\n'
        '• RSI: `{rsi:.1f}` ({zone})\n'
        '• BB верх: `{bb_hi:.4f}`\n'
        '• BB низ : `{bb_lo:.4f}`\n\n'
        '*Вход MARKET {side} по RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'Перепроданность (<30)',
    'rsi_zone_overbought':         'Перекупленность (>70)',
    'rsi_zone_neutral':            'Нейтральная зона (30–70)',

    # Проверки TP/SL
    'invalid_tpsl_long': (
        '❌ Неверные TP/SL для LONG.\n'
        'Текущая цена: {current:.2f}\n'
        'Ожидается: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ Неверные TP/SL для SHORT.\n'
        'Текущая цена: {current:.2f}\n'
        'Ожидается: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 У тебя нет открытой позиции по {symbol}',
    'tpsl_set_success':            '✅ TP={tp:.2f} и SL={sl:.2f} установлены для {symbol}',

    # Кнопки и режим стопа
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Язык',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Режим стопа: *{mode}*',
    'config_dca':                  'DCA: Нога1=-{dca1}%, Нога2=-{dca2}%',

    # Жизненный цикл ордеров
    'limit_order_filled':          '✅ Лимит-ордер по {symbol} исполнен @ {price}',
    'limit_order_cancelled':       '⚠️ Лимит-ордер по {symbol} (ID: {order_id}) отменён.',
    'fixed_sl_tp':                 '✅ {symbol}: SL установлен на {sl}, TP — на {tp}',
    'tp_part':                     ', TP установлен на {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL установлен на {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL установлен на {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP инициализированы на {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL сдвинут в безубыток @ {entry}',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP обновлены до {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Позиция {symbol} закрыта, но запись не сохранена: {error}\n'
        'Свяжитесь с поддержкой.'
    ),

    # возможные значения
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Фиксированный %',

    # Системные уведомления
    'db_quarantine_notice':        '⚠️ Логи временно не пишутся. Включён тихий режим на 1 ч.',

    # Fallback
    'fallback':                    '❓ Пожалуйста, используйте кнопки меню.',
    
    # Symbols / markers
    'dash':                      '—',
    'mark_yes':                  '✅',
    'mark_no':                   '—',
    'mark_ban':                  '⛔️',

    # Access / terms / moderation
    'banned':                    '🚫 Вы заблокированы.',
    'invite_only':               '🔒 Доступ по приглашению. Ждите решения админа.',
    'need_terms':                '⚠️ Сначала примите правила: /terms',
    'please_confirm':            'Пожалуйста подтвердите:',
    'terms_ok':                  '✅ Спасибо! Правила приняты.',
    'terms_declined':            '❌ Вы отклонили правила. Доступ к боту закрыт. Вы можете вернуться командой /terms.',
    'usage_approve':             'Использование: /approve <user_id>',
    'usage_ban':                 'Использование: /ban <user_id>',
    'not_allowed':               'Недостаточно прав',
    'bad_payload':               'Некорректный payload',
    'unknown_action':            'Неизвестное действие',

    # Admin: new user notification
    'title':                     'Новый пользователь',
    'wave':                      '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Имя: {name}\n'
        '• Юзернейм: {uname}\n'
        '• Lang: {lang}\n'
        '• Allowed: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve':               '✅ Одобрить',
    'btn_ban':                   '⛔️ Бан',
    'admin_notify_fail':         'Не удалось уведомить админа: {e}',
    'moderation_approved':       '✅ Одобрено: {target}',
    'moderation_banned':         '⛔️ Забанен: {target}',
    'approved_user_dm':          '✅ Доступ одобрен. Нажмите /start.',
    'banned_user_dm':            '🚫 Вы заблокированы.',

    # Admin: users list / navigation
    'users_not_found':           '😕 Пользователи не найдены.',
    'users_page_info':           '📄 Страница {page}/{pages} — всего: {total}',
    'user_card_html': (
        '<b>👤 Пользователь</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Имя: {full_name}\n'
        '• Юзернейм: {uname}\n'
        '• Lang: <code>{lang}</code>\n'
        '• Allowed: {allowed}\n'
        '• Banned: {banned}\n'
        '• Terms: {terms}\n'
        '• % на сделку: <code>{percent}</code>'
    ),
    'btn_blacklist':             '🚫 В ЧС',
    'btn_delete_user':           '🗑 Удалить из БД',
    'btn_prev':                  '⬅️ Назад',
    'btn_next':                  '➡️ Далее',
    'nav_caption':               '🧭 Навигация:',
    'bad_page':                  'Неверная страница.',
    'admin_user_delete_fail':    '❌ Не удалось удалить {target}: {error}',
    'admin_user_deleted':        '🗑 Пользователь {target} удалён из БД.',
    'user_access_approved':      '✅ Доступ одобрен. Нажмите /start.',

    # Admin panel & actions (buttons + notices)
    'admin_pause_all':           '⏸️ Пауза для всех',
    'admin_resume_all':          '▶️ Возобновить',
    'admin_close_longs':         '🔒 Закр. все лонги',
    'admin_close_shorts':        '🔓 Закр. все шорты',
    'admin_cancel_limits':       '❌ Удалить лимитки',
    'admin_users':               '👥 Юзеры',
    'admin_pause_notice':        '⏸️ Торговля и рассылка приостановлены для всех.',
    'admin_resume_notice':       '▶️ Торговля и рассылка возобновлены для всех.',
    'type_longs':                'лонги',
    'type_shorts':               'шорты',
    'admin_closed_total':        '✅ Закрыто всего {count} {type}.',
    'admin_canceled_limits_total':'✅ Отменено {count} лимитных ордеров.',

    # Terms buttons
    'terms_btn_accept':          '✅ Принимаю',
    'terms_btn_decline':         '❌ Отклоняю',

    # Market emojis (signal colors)
    'emoji_long':                '🟢',
    'emoji_short':               '🔴',
    'emoji_neutral':             '⚪️',

    # Strategy Settings
    'button_strategy_settings':      '🎯 Стратегии',
    'strategy_settings_header':      '⚙️ *Настройки стратегий*',
    'strategy_param_header':         '⚙️ *Настройки {name}*',
    'using_global':                  'Глобальные настройки',
    'global_default':                'Глоб.',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_fibonacci':               '📐 Fibonacci',
    'dca_settings':                  '⚙️ Настройки DCA',
    'dca_settings_header':           '⚙️ *Настройки DCA (Фьючерсы)*\n\n',
    'dca_toggle':                    'DCA включён',
    'dca_status':                    'Статус',
    'dca_description':               '_DCA добавит к позиции, когда цена движется против вас._',
    'dca_leg1':                      '📉 DCA Нога 1 %',
    'dca_leg2':                      '📉 DCA Нога 2 %',
    'param_percent':                 '📊 Вход %',
    'param_sl':                      '🔻 Стоп-Лосс %',
    'param_tp':                      '🔺 Тейк-Профит %',
    'param_reset':                   '🔄 Сбросить к глобальным',
    'btn_close':                     '❌ Закрыть',
    'prompt_entry_pct':              'Введите % входа (риск на сделку):',
    'prompt_sl_pct':                 'Введите % Стоп-Лосса:',
    'prompt_tp_pct':                 'Введите % Тейк-Профита:',
    'prompt_dca_leg1':               'Введите % для DCA Ноги 1 (напр., 10):',
    'prompt_dca_leg2':               'Введите % для DCA Ноги 2 (напр., 25):',
    'prompt_atr_periods':            'Введите количество периодов ATR (напр., 7):',
    'prompt_atr_mult':               'Введите множитель ATR для шага trailing SL (напр., 1.0):',
    'prompt_atr_trigger':            'Введите триггер ATR % для активации trailing (напр., 2.0):',
    'settings_reset':                'Настройки сброшены к глобальным',
    'strat_setting_saved':           '✅ {name} {param} установлен на {value}',
    'dca_setting_saved':             '✅ DCA {leg} установлен на {value}%',
    'invalid_number':                '❌ Некорректное число. Введите значение от 0 до 100.',
    'dca_10pct':                     'DCA −{pct}%: добор по {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: добор по {symbol} qty={qty} @ {price}',

    # ATR settings UI
    'param_atr_periods':             '📈 Периоды ATR',
    'param_atr_mult':                '📉 Множитель ATR (шаг SL)',
    'param_atr_trigger':             '🎯 Триггер ATR %',

    # Hardcoded strings fix
    'terms_unavailable':             'Условия использования недоступны. Обратитесь к администратору.',
    'terms_confirm_prompt':          'Подтвердите:',
    'your_id':                       'Ваш ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Ошибка: {msg}',
    'error_fetch_balance':           '❌ Ошибка получения баланса: {error}',
    'error_fetch_orders':            '❌ Ошибка получения ордеров: {error}',
    'error_occurred':                '❌ Ошибка: {error}',

    # Trading Statistics
    'button_stats':                  '📊 Статистика',
    'stats_title':                   'Статистика торговли',
    'stats_strategy':                'Стратегия',
    'stats_period':                  'Период',
    'stats_overview':                'Обзор',
    'stats_total_trades':            'Всего сделок',
    'stats_closed':                  'Закрыто',
    'stats_open':                    'Открыто',
    'stats_results':                 'Результаты',
    'stats_winrate':                 'Винрейт',
    'stats_total_r':                 'Суммарный R',
    'stats_avg_r':                   'Средний R',
    'stats_by_direction':            'По направлению',
    'stats_long':                    'Лонг',
    'stats_short':                   'Шорт',
    'stats_pnl':                     'Прибыль/Убыток',
    'stats_gross_profit':            'Прибыль',
    'stats_gross_loss':              'Убыток',
    'stats_total_pnl':               'Общий P/L',
    'stats_realized_pnl':            'Реализ.',
    'stats_unrealized_pnl':          'Нереализ.',
    'stats_combined_pnl':            'Итого',
    'stats_profit_factor':           'PF',
    'stats_strategy_settings':       'Настройки стратегии',
    'settings_entry_pct':            'Вход',
    'settings_leverage':             'Плечо',
    'settings_trading_mode':         'Режим',
    'settings_direction':            'Направление',
    'stats_all':                     '📈 Все',
    'stats_oi':                      '📉 OI',
    'stats_rsi_bb':                  '📊 RSI+BB',
    'stats_scryptomera':             '🐱 Scryptomera',
    'stats_scalper':                 '⚡ Scalper',
    'stats_elcaro':                  '🔥 Elcaro',
    'stats_fibonacci':               '📐 Fibonacci',
    'stats_spot':                    '💹 Спот',
    'stats_spot_title':              'Статистика Спот DCA',
    'stats_spot_config':             'Конфигурация',
    'stats_spot_holdings':           'Активы',
    'stats_spot_summary':            'Итого',
    'stats_spot_current_value':      'Текущая стоимость',
    'stats_period_all':              'Всё время',
    'stats_period_today':            '24 часа',
    'stats_period_week':             'Неделя',
    'stats_period_month':            'Месяц',
    'stats_demo':                    '🔵 Демо',
    'stats_real':                    '🟢 Реал',

    # Scryptomera direction settings
    'param_direction': '🎯 Направление',
    'param_long_settings': '📈 Настройки LONG',
    'param_short_settings': '📉 Настройки SHORT',
    'dir_all': '🔄 ВСЕ (LONG + SHORT)',
    'dir_long_only': '📈 Только LONG',
    'dir_short_only': '📉 Только SHORT',
    'scrypto_side_header': '{emoji} *Scryptomera {side} настройки*',
    'scalper_side_header': '{emoji} *Scalper {side} настройки*',
    'global_settings': '🌐 Глобальные настройки',
    'global_settings_header': '🌐 *Глобальные торговые настройки*',
    'global_settings_info': 'Эти настройки используются по умолчанию, когда не заданы настройки конкретной стратегии.',
    'prompt_long_entry_pct': '📈 LONG Entry % (риск на сделку):',
    'prompt_long_sl_pct': '�� LONG Stop-Loss %:',
    'prompt_long_tp_pct': '📈 LONG Take-Profit %:',
    'prompt_short_entry_pct': '📉 SHORT Entry % (риск на сделку):',
    'prompt_short_sl_pct': '📉 SHORT Stop-Loss %:',
    'prompt_short_tp_pct': '📉 SHORT Take-Profit %:',

    # Order type settings
    'param_order_type': '📤 Тип ордера',
    'order_type_market': '⚡ Market ордера',
    'order_type_limit': '🎯 Limit ордера',

    # Leverage settings
    'param_leverage': '⚡ Плечо',
    'prompt_leverage': 'Введите плечо (1-100):',
    'auto_default': 'Авто',

    # Coins group per strategy
    'param_coins_group': '🪙 Монеты',
    'select_coins_for_strategy': '🪙 *Выберите группу монет для {name}*',
    'group_global': '📊 Глобальная (общая настройка)',

    # Elcaro AI
    'elcaro_ai_info': '🤖 *AI-трейдинг*',
    'elcaro_ai_desc': '_Все параметры парсятся из AI-сигналов автоматически:_',

    # Limit Ladder
    'limit_ladder': '📉 Лесенка лимиток',
    'limit_ladder_header': '📉 *Настройки лесенки лимиток*',
    'limit_ladder_settings': '⚙️ Настройки лесенки',
    'ladder_count': 'Кол-во ордеров',
    'ladder_info': 'Лимитные ордера ниже входа для DCA. Каждый ордер имеет % отступ от входа и % от депозита.',
    'prompt_ladder_pct_entry': '📉 Введите % ниже цены входа для ордера {idx}:',
    'prompt_ladder_pct_deposit': '💰 Введите % от депозита для ордера {idx}:',
    'ladder_order_saved': '✅ Ордер {idx} сохранён: -{pct_entry}% @ {pct_deposit}% депозита',
    'ladder_orders_placed': '📉 Размещено {count} лесенка лимиток для {symbol}',
    
    # =====================================================
    # СИСТЕМА ЛИЦЕНЗИРОВАНИЯ
    # =====================================================
    
    # Сообщения о статусе лицензии
    'no_license': '⚠️ Для использования этой функции нужна активная подписка.\n\nИспользуйте /subscribe для покупки.',
    'no_license_trading': '⚠️ Для торговли нужна активная подписка.\n\nИспользуйте /subscribe для покупки.',
    'license_required': '⚠️ Эта функция требует подписку {required}.\n\nИспользуйте /subscribe для апгрейда.',
    'trial_demo_only': '⚠️ Пробная версия позволяет только демо-торговлю.\n\nОбновитесь до Premium или Basic для реальной торговли: /subscribe',
    'basic_strategy_limit': '⚠️ Basic лицензия на реальном аккаунте позволяет только: {strategies}\n\nОбновитесь до Premium для всех стратегий: /subscribe',
    
    # Меню подписки
    'subscribe_menu_header': '💎 *Тарифные планы*',
    'subscribe_menu_info': 'Выберите план для разблокировки торговых функций:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Пробный (Бесплатно)',
    'btn_enter_promo': '🎟 Промокод',
    'btn_my_subscription': '📋 Моя подписка',
    
    # Premium план
    'premium_title': '💎 *PREMIUM ПЛАН*',
    'premium_desc': '''✅ Полный доступ ко всем функциям
✅ Все 5 стратегий: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ Реальная + Демо торговля
✅ Приоритетная поддержка
✅ ATR динамический SL/TP
✅ Лесенка лимиток DCA
✅ Все будущие обновления''',
    'premium_1m': '💎 1 Месяц — {price} TRC',
    'premium_3m': '💎 3 Месяца — {price} TRC (-10%)',
    'premium_6m': '💎 6 Месяцев — {price} TRC (-20%)',
    'premium_12m': '💎 12 Месяцев — {price} TRC (-30%)',
    
    # Basic план
    'basic_title': '🥈 *BASIC ПЛАН*',
    'basic_desc': '''✅ Полный доступ к демо аккаунту
✅ Реальный аккаунт: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Wyckoff, Spot — только Premium
✅ Стандартная поддержка
✅ ATR динамический SL/TP''',
    'basic_1m': '🥈 1 Месяц — {price} TRC',
    
    # Пробный план
    'trial_title': '🎁 *ПРОБНЫЙ ПЛАН (БЕСПЛАТНО)*',
    'trial_desc': '''✅ Полный доступ к демо аккаунту
✅ Все 5 стратегий на демо
❌ Реальная торговля недоступна
⏰ Срок: 7 дней
🎁 Только один раз''',
    'trial_activate': '🎁 Активировать пробный',
    'trial_already_used': '⚠️ Вы уже использовали пробный период.',
    'trial_activated': '🎉 Пробный период активирован! У вас 7 дней полного демо-доступа.',
    
    # Оплата
    'payment_select_method': '💳 *Выберите способ оплаты*',
    'btn_pay_trc': '◈ Оплатить TRC',
    'btn_pay_ton': '💎 TON (устарело)',
    'payment_trc_title': '◈ Оплата через Triacelo Coin (TRC)',
    'payment_trc_desc': 'С вас будет списано {amount} TRC за {plan} ({period}).',
    'payment_ton_title': '💎 Оплата через TON (Устарело)',
    'payment_ton_desc': '''Оплата через TON больше не поддерживается.
Используйте TRC токены.''',
    'btn_verify_ton': '✅ Я оплатил — Проверить',
    'btn_check_again': '🔄 Проверить снова',
    'payment_processing': '⏳ Обработка платежа...',
    'payment_verifying': '⏳ Проверка платежа...',
    'payment_success': '🎉 Оплата успешна!\n\n{plan} активирован до {expires}.',
    'payment_failed': '❌ Ошибка оплаты: {error}',
    'payment_ton_not_configured': '❌ TON платежи устарели. Используйте TRC токены.',
    'payment_session_expired': '❌ Сессия оплаты истекла. Начните заново.',
    'payment_trc_insufficient': '''❌ Недостаточно TRC.

Ваш баланс: {balance} TRC
Требуется: {required} TRC

Пополните кошелёк для продолжения.''',
    
    # Кошелёк
    'wallet_title': '◈ *TRC Кошелёк*',
    'wallet_balance': '''💰 *Ваш TRC Кошелёк*

◈ Баланс: *{balance} TRC*
📈 В стейкинге: *{staked} TRC*
🎁 Ожидающие награды: *{rewards} TRC*

💵 Общая стоимость: *${total_usd}*
📍 1 TRC = 1 USDT''',
    'wallet_address': '📍 Адрес: `{address}`',
    'wallet_btn_deposit': '📥 Пополнить',
    'wallet_btn_withdraw': '📤 Вывести',
    'wallet_btn_stake': '📈 Стейкинг',
    'wallet_btn_unstake': '📤 Снять стейк',
    'wallet_btn_history': '📋 История',
    'wallet_btn_back': '« Назад',
    'wallet_deposit_title': '📥 *Пополнение TRC*',
    'wallet_deposit_desc': '''Отправьте TRC токены на адрес кошелька:

`{address}`

💡 *Демо режим:* Нажмите ниже для получения тестовых токенов.''',
    'wallet_deposit_demo': '🎁 Получить 100 TRC (Демо)',
    'wallet_deposit_success': '✅ Пополнено {amount} TRC успешно!',
    'wallet_withdraw_title': '📤 *Вывод TRC*',
    'wallet_withdraw_desc': 'Введите адрес назначения и сумму:',
    'wallet_withdraw_success': '✅ Выведено {amount} TRC на {address}',
    'wallet_withdraw_failed': '❌ Ошибка вывода: {error}',
    'wallet_stake_title': '📈 *Стейкинг TRC*',
    'wallet_stake_desc': '''Стейкайте TRC токены и получайте *12% годовых*!

💰 Доступно: {available} TRC
📈 В стейкинге: {staked} TRC
🎁 Ожидающие награды: {rewards} TRC

Ежедневные награды • Мгновенный вывод''',
    'wallet_stake_success': '✅ {amount} TRC успешно застейкано!',
    'wallet_unstake_success': '✅ Снято {amount} TRC + {rewards} TRC наград!',
    'wallet_history_title': '📋 *История транзакций*',
    'wallet_history_empty': 'Пока нет транзакций.',
    'wallet_history_item': '{type_emoji} {type}: {amount:+.2f} TRC\n   {date}',
    
    # Моя подписка
    'my_subscription_header': '📋 *Моя подписка*',
    'my_subscription_active': '''📋 *Текущий план:* {plan}
⏰ *Истекает:* {expires}
📅 *Осталось дней:* {days}''',
    'my_subscription_none': '❌ Нет активной подписки.\n\nИспользуйте /subscribe для покупки.',
    'my_subscription_history': '📜 *История платежей:*',
    'subscription_expiring_soon': '⚠️ Ваша подписка {plan} истекает через {days} дней!\n\nПродлите сейчас: /subscribe',
    
    # Промокоды
    'promo_enter': '🎟 Введите ваш промокод:',
    'promo_success': '🎉 Промокод применён!\n\n{plan} активирован на {days} дней.',
    'promo_invalid': '❌ Неверный промокод.',
    'promo_expired': '❌ Срок действия промокода истёк.',
    'promo_used': '❌ Промокод уже использован.',
    'promo_already_used': '❌ Вы уже использовали этот промокод.',
    
    # Админ управление лицензиями
    'admin_license_menu': '🔑 *Управление лицензиями*',
    'admin_btn_grant_license': '🎁 Выдать лицензию',
    'admin_btn_view_licenses': '📋 Просмотр лицензий',
    'admin_btn_create_promo': '🎟 Создать промо',
    'admin_btn_view_promos': '📋 Просмотр промо',
    'admin_btn_expiring_soon': '⚠️ Скоро истекут',
    'admin_grant_select_type': 'Выберите тип лицензии:',
    'admin_grant_select_period': 'Выберите период:',
    'admin_grant_enter_user': 'Введите ID пользователя:',
    'admin_license_granted': '✅ {plan} выдан пользователю {uid} на {days} дней.',
    'admin_license_extended': '✅ Лицензия продлена на {days} дней для пользователя {uid}.',
    'admin_license_revoked': '✅ Лицензия отозвана у пользователя {uid}.',
    'admin_promo_created': '✅ Промокод создан: {code}\nТип: {type}\nДней: {days}\nМакс. использований: {max}',

    # =====================================================
    # АДМИН УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
    # =====================================================
    'admin_users_management': '👥 Пользователи',
    'admin_licenses': '🔑 Лицензии',
    'admin_search_user': '🔍 Найти',
    'admin_users_menu': '👥 *Управление пользователями*\n\nВыберите фильтр или поиск:',
    'admin_all_users': '👥 Все',
    'admin_active_users': '✅ Активные',
    'admin_banned_users': '🚫 Заблокированные',
    'admin_no_license': '❌ Без лицензии',
    'admin_no_users_found': 'Пользователи не найдены.',
    'admin_enter_user_id': '🔍 Введите ID пользователя для поиска:',
    'admin_user_found': '✅ Пользователь {uid} найден!',
    'admin_user_not_found': '❌ Пользователь {uid} не найден.',
    'admin_invalid_user_id': '❌ Неверный ID. Введите число.',
    'admin_view_card': '👤 Карточка',
    
    # Карточка пользователя
    'admin_user_card': '''👤 *Карточка пользователя*

📋 *ID:* `{uid}`
{status_emoji} *Статус:* {status}
📝 *Правила:* {terms}

{license_emoji} *Лицензия:* {license_type}
📅 *Истекает:* {license_expires}
⏳ *Осталось дней:* {days_left}

🌐 *Язык:* {lang}
📊 *Режим:* {trading_mode}
💰 *% на сделку:* {percent}%
🪙 *Монеты:* {coins}

🔌 *API ключи:*
  Demo: {demo_api}
  Real: {real_api}

📈 *Стратегии:* {strategies}

📊 *Статистика:*
  Позиций: {positions}
  Сделок: {trades}
  PnL: {pnl}
  Винрейт: {winrate}%

💳 *Платежи:*
  Всего: {payments_count}
  TRC: {total_trc}

📅 *Первый визит:* {first_seen}
🕐 *Последний:* {last_seen}
''',
    
    # Действия с пользователем
    'admin_btn_grant_lic': '🎁 Выдать',
    'admin_btn_extend': '⏳ Продлить',
    'admin_btn_revoke': '🚫 Отозвать',
    'admin_btn_ban': '🚫 Бан',
    'admin_btn_unban': '✅ Разбан',
    'admin_btn_approve': '✅ Одобрить',
    'admin_btn_message': '✉️ Написать',
    'admin_btn_delete': '🗑 Удалить',
    
    'admin_user_banned': 'Пользователь заблокирован!',
    'admin_user_unbanned': 'Пользователь разблокирован!',
    'admin_user_approved': 'Пользователь одобрен!',
    'admin_confirm_delete': '⚠️ *Подтвердите удаление*\n\nПользователь {uid} будет удалён безвозвратно!',
    'admin_confirm_yes': '✅ Да, удалить',
    'admin_confirm_no': '❌ Отмена',
    
    'admin_select_license_type': 'Выберите тип лицензии для пользователя {uid}:',
    'admin_select_period': 'Выберите период:',
    'admin_select_extend_days': 'Выберите дни для продления для пользователя {uid}:',
    'admin_license_granted_short': 'Лицензия выдана!',
    'admin_license_extended_short': 'Продлено на {days} дней!',
    'admin_license_revoked_short': 'Лицензия отозвана!',
    
    'admin_enter_message': '✉️ Введите сообщение для пользователя {uid}:',
    'admin_message_sent': '✅ Сообщение отправлено пользователю {uid}!',
    'admin_message_failed': '❌ Не удалось отправить сообщение: {error}',

    # =====================================================
    # ADMIN PAYMENTS & REPORTS
    # =====================================================
    'admin_payments': '💳 Платежи',
    'admin_reports': '📊 Отчёты',
    'admin_payments_menu': '💳 *Управление платежами*',
    'admin_all_payments': '📜 Все платежи',
    'admin_no_payments_found': 'Платежей не найдено.',
    
    'admin_reports_menu': '📊 *Отчёты и аналитика*\n\nВыберите тип отчёта:',
    'admin_global_stats': '📊 Глобальная статистика',
    'admin_demo_stats': '🎮 Демо статистика',
    'admin_real_stats': '💰 Реальная статистика',
    'admin_strategy_breakdown': '🎯 По стратегиям',
    'admin_top_traders': '🏆 Топ трейдеры',
    'admin_user_report': '👤 Отчёт пользователя',
    'admin_enter_user_for_report': '👤 Введите ID пользователя для детального отчёта:',
    'admin_generating_report': '📊 Генерирую отчёт для пользователя {uid}...',
    'admin_view_report': '📊 Смотреть отчёт',
    'admin_view_user': '👤 Карточка пользователя',

    # Payment keys
    'btn_check_again': '🔄 Проверить снова',
    'button_admin': '👑 Админ',
    'button_licenses': '🔑 Лицензии',
    'payment_session_expired': '❌ Сессия оплаты истекла. Начните заново.',
    'payment_ton_not_configured': '❌ TON платежи не настроены.',
    'payment_verifying': '⏳ Проверяем платёж...',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "Торговля на HyperLiquid",
    "hl_reset_settings": "🔄 Сбросить на настройки Bybit",



    # === HyperLiquid и дополнительные строки ===
    'cancelled': '❌ Отменено.',
    'entry_pct_range_error': '❌ % входа должен быть от 0.1 до 100.',
    'hl_no_history': '📭 Нет истории торгов на HyperLiquid.',
    'hl_no_orders': '📭 Нет открытых ордеров на HyperLiquid.',
    'hl_no_positions': '📭 Нет открытых позиций на HyperLiquid.',
    'hl_setup_cancelled': '❌ Настройка HyperLiquid отменена.',
    'invalid_amount': '❌ Неверное число. Введите корректную сумму.',
    'leverage_range_error': '❌ Плечо должно быть от 1 до 100.',
    'max_amount_error': '❌ Максимальная сумма 100,000 USDT',
    'min_amount_error': '❌ Минимальная сумма 1 USDT',
    'sl_tp_range_error': '❌ SL/TP % должен быть от 0.1 до 500.',
    
    # =====================================================
    # DEEP LOSS - ПОЗИЦИЯ В ГЛУБОКОМ МИНУСЕ
    # =====================================================
    'btn_close_position': '❌ Закрыть позицию',
    'btn_enable_dca': '📈 Включить DCA добор',
    'btn_ignore': '🔇 Игнорировать',
    'deep_loss_alert': '⚠️ <b>Позиция в глубоком минусе!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Убыток: <code>{loss_pct:.2f}%</code>\n💰 Вход: <code>{entry}</code>\n📍 Текущая: <code>{mark}</code>\n\n❌ Стоп-лосс невозможно установить выше цены входа.\n\n<b>Что делать?</b>\n• <b>Закрыть</b> - зафиксировать убыток\n• <b>DCA добор</b> - усреднить позицию доборами\n• <b>Игнорировать</b> - оставить как есть',
    'position_already_closed': '❌ Позиция {symbol} уже закрыта.',
    'deep_loss_closed': '✅ Позиция {symbol} закрыта.\n\nУбыток зафиксирован. Иногда лучше принять небольшой убыток, чем надеяться на разворот.',
    'deep_loss_close_error': '❌ Ошибка при закрытии позиции: {error}',
    'dca_already_enabled': '✅ DCA добор уже включен!\n\n📊 <b>{symbol}</b>\nБот будет автоматически добавлять к позиции при просадке:\n• -10% → добор\n• -25% → добор\n\nЭто поможет усреднить цену входа.',
    'dca_enabled_for_symbol': '✅ DCA добор включен!\n\n📊 <b>{symbol}</b>\nБот будет автоматически добавлять к позиции при просадке:\n• -10% → добор (усреднение)\n• -25% → добор (усреднение)\n\n⚠️ DCA требует достаточный баланс для доборов.\nНастроить параметры: /strategy_settings',
    'dca_enable_error': '❌ Ошибка: {error}',
    'deep_loss_ignored': '🔇 Понял, позиция {symbol} оставлена без изменений.\n\n⚠️ Помните: без стоп-лосса риск потерь неограничен.\nВы можете закрыть позицию вручную через /positions',


    # DCA and Deep Loss notifications
    'fibonacci_desc': '_Вход, SL, TP — по уровням Фибоначчи из сигнала._',
    'fibonacci_info': '📐 *Стратегия Fibonacci Extension*',
    'prompt_min_quality': 'Введите минимальное качество % (0-100):',


    # Hardcore trading phrase
    'hardcore_mode': '💀 *ХАРДКОР РЕЖИМ*: Без пощады, без сожалений. Только профит или смерть! 🔥',
}
