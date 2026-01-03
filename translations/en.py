# translations/en.py
TEXTS = {
    # Main menu
    'welcome':                     '👋 Hello! Choose an action:',
    'no_strategies':               '❌ None',
    'guide_caption':               '📚 Trading Bot User Guide\n\nPlease read this guide to learn how to configure strategies and use the bot effectively.',
    'privacy_caption':             '📜 Privacy Policy & Terms of Use\n\nPlease read this document carefully.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 Secret',
    'button_api_settings':         '🔑 API',
    'button_subscribe':            '💎 Subscribe',
    'button_licenses':             '🔑 Licenses',
    'button_admin':                '👑 Admin',
    'button_balance':              '💰 USDT Balance',
    'button_orders':               '📜 My Orders',
    'button_positions':            '📊 Positions',
    'button_percent':              '🎚 % per Trade',
    'button_coins':                '💠 Coin Group',
    'button_market':               '📈 Market',
    'button_manual_order':         '✋ Manual Order',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ Cancel Order',
    'button_limit_only':           '🎯 Limit-Only',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_scalper':              '🎯 Scalper',
    'button_elcaro':               '🔥 Elcaro',
    'button_fibonacci':            '📐 Fibonacci',
    'button_settings':             '📋 My Config',
    'button_indicators':           '💡 Indicators',
    'button_support':              '🆘 Support',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',
    'config_trade_scalper':        '🎯 Scalper: {state}',
    'config_trade_elcaro':         '🔥 Elcaro: {state}',
    'config_trade_fibonacci':      '📐 Fibonacci: {state}',

    # API Settings
    'api_settings_title':          '🔑 <b>API Settings</b>',
    'api_demo_title':              '🧪 Demo Account',
    'api_real_title':              '💼 Real Account',
    'api_key_set':                 '✅ Set',
    'api_key_not_set':             '❌ Not set',
    'api_trading_mode':            '📍 <b>Trading Mode:</b>',
    'api_mode_demo':               '🧪 Demo',
    'api_mode_real':               '💼 Real',
    'api_mode_both':               '🔄 Both',
    'api_btn_demo_key':            '🧪 Demo API Key',
    'api_btn_demo_secret':         '🧪 Demo Secret',
    'api_btn_real_key':            '💼 Real API Key',
    'api_btn_real_secret':         '💼 Real Secret',
    'api_btn_delete_demo':         '🗑 Delete Demo',
    'api_btn_delete_real':         '🗑 Delete Real',
    'api_btn_mode_demo':           '🧪 Trade Demo',
    'api_btn_mode_real':           '💼 Trade Real',
    'api_btn_mode_both':           '🔄 Trade Both',
    'api_btn_back':                '⬅️ Back',
    'api_enter_demo_key':          '🧪 Enter your <b>Demo API Key</b>:',
    'api_enter_demo_secret':       '🧪 Enter your <b>Demo API Secret</b>:',
    'api_enter_real_key':          '💼 Enter your <b>Real API Key</b>:\n\n⚠️ <b>Warning:</b> This is for real money trading!',
    'api_enter_real_secret':       '💼 Enter your <b>Real API Secret</b>:\n\n⚠️ <b>Warning:</b> This is for real money trading!',
    'api_key_saved':               '✅ API Key saved successfully!',
    'api_secret_saved':            '✅ API Secret saved successfully!',
    'api_deleted':                 '🗑 API credentials deleted for {account}',
    'api_mode_changed':            '✅ Trading mode changed to: <b>{mode}</b>',
    'api_mode_both_warning':       '⚠️ <b>Both mode:</b> Signals will be executed on BOTH Demo and Real accounts!',
    'api_key_hidden':              '••••••••{suffix}',
    'api_test_connection':         '🔄 Test Connection',
    'api_connection_ok':           '✅ Connection OK! Balance: {balance} USDT',
    'api_connection_fail':         '❌ Connection failed: {error}',
    'api_test_success':            'Connection Successful!',
    'api_test_no_keys':            'API Keys Not Set',
    'api_test_set_keys':           'Please set API Key and Secret first.',
    'api_test_failed':             'Connection Failed',
    'api_test_error':              'Error',
    'api_test_check_keys':         'Please check your API credentials.',
    'api_test_status':             'Status',
    'api_test_connected':          'Connected',
    'balance_wallet':              'Wallet Balance',
    'balance_equity':              'Equity',
    'balance_available':           'Available',

    # Spot Trading
    'api_spot_trading':            '💹 Spot Trading',
    'api_spot_enabled':            '💹 <b>Spot Trading:</b> ✅ ON',
    'api_spot_disabled':           '💹 <b>Spot Trading:</b> ❌ OFF',
    'api_spot_toggled':            'Spot Trading: {status}',
    'spot_settings_title':         '💹 <b>Spot DCA Settings</b>',
    'spot_coins':                  '🪙 Coins: {coins}',
    'spot_coins_label':            'Coins',
    'spot_dca_amount':             '💵 DCA Amount: {amount} USDT',
    'spot_dca_amount_label':       'DCA Amount',
    'spot_dca_frequency':          '⏰ Frequency: {freq}',
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_freq_monthly':           'Monthly',
    'spot_buy_now':                '💰 Buy Now',
    'spot_auto_dca':               '🔄 Auto DCA: {status}',
    'spot_auto_dca_label':         'Auto DCA',
    'spot_next_buy':               '⏳ Next Buy: {time}',
    'spot_total_invested':         '📊 Total Invested: {amount} USDT',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_buy_success':            '✅ Bought {qty} {coin} for {amount} USDT',
    'spot_buy_failed':             '❌ Spot buy failed: {error}',
    'spot_balance':                '💰 Spot Balance: {balance}',
    'spot_no_balance':             '❌ No spot balance found',
    'spot_order_placed':           '✅ Spot order placed: {side} {qty} {coin}',
    'button_spot_settings':        '💹 Spot Settings',
    'spot_btn_coins':              '🪙 Coins',
    'spot_btn_amount':             '💵 Amount',
    'spot_btn_frequency':          '⏰ Frequency',
    'spot_btn_auto_toggle':        '🔄 Auto DCA',
    'spot_btn_buy_now':            '💰 Buy Now',
    'spot_btn_back':               '⬅️ Back',
    'spot_enter_amount':           'Enter DCA amount in USDT:',
    'spot_amount_saved':           '✅ DCA amount set to {amount} USDT',
    'spot_trading_mode':           'Trading Mode',
    'spot_btn_mode':               'Mode',
    'spot_select_coins':           'Select coins for Spot DCA:',
    'spot_coins_saved':            '✅ Spot coins set: {coins}',
    'spot_select_frequency':       'Select DCA frequency:',
    'spot_frequency_saved':        '✅ Frequency set to {freq}',
    'spot_auto_enabled':           '✅ Auto DCA enabled',
    'spot_auto_disabled':          '❌ Auto DCA disabled',
    'spot_not_enabled':            '❌ Spot trading is not enabled. Enable it in Strategy Settings first.',

    # Strategy trading mode
    'strat_mode_global':           '🌐 Global',
    'strat_mode_demo':             '🧪 Demo',
    'strat_mode_real':             '💰 Real',
    'strat_mode_both':             '🔄 Both',
    'strat_mode_changed':          '✅ {strategy} trading mode: {mode}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 TP/SL mode is now: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Fixed %',

    # Limits
    'limit_positions_exceeded':    '🚫 Open positions limit exceeded ({max})',
    'limit_limit_orders_exceeded': '🚫 Limit orders limit exceeded ({max})',
    'max_positions_reached':       '⚠️ Maximum positions reached. New signals will be skipped until a position closes.',

    # Languages
    'select_language':             'Select language:',
    'language_set':                'Language set to:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'Select order type:',
    'limit_order_format': (
        "Enter limit order parameters as:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "where SIDE = LONG or SHORT\n"
        "Example: `BTCUSDT LONG 20000 0.1`\n\n"
        "To cancel, send ❌ Cancel Order"
    ),
    'market_order_format': (
        "Enter market order parameters as:\n"
        "`SYMBOL SIDE QTY`\n"
        "where SIDE = LONG or SHORT\n"
        "Example: `BTCUSDT SHORT 0.1`\n\n"
        "To cancel, send ❌ Cancel Order"
    ),
    'order_success':               '✅ Order created successfully!',
    'order_create_error':          '❌ Failed to create order: {msg}',
    'order_fail_leverage':         (
        "❌ Order not created: your Bybit account has too high leverage for this size.\n"
        "Please reduce leverage in your Bybit settings."
    ),
    'order_parse_error':           '❌ Failed to parse: {error}',
    'price_error_min':             '❌ Price error: must be ≥{min}',
    'price_error_step':            '❌ Price error: must be a multiple of {step}',
    'qty_error_min':               '❌ Quantity error: must be ≥{min}',
    'qty_error_step':              '❌ Quantity error: must be a multiple of {step}',

    # Loading…
    'loader':                      '⏳ Gathering data…',

    # Market command
    'market_status_heading':       '*Market Status:*',
    'market_dominance_header':    'Top Coins by Dominance',
    'market_total_header':        'Total Market Cap',
    'market_indices_header':      'Market Indices',
    'usdt_dominance':              'USDT Dominance',
    'btc_dominance':               'BTC Dominance',
    'dominance_rising':            '↑ rising',
    'dominance_falling':           '↓ falling',
    'dominance_stable':            '↔️ stable',
    'dominance_unknown':           '❔ no data',
    'btc_price':                   'BTC Price',
    'last_24h':                    'in last 24h',
    'alt_signal_label':            'Altcoin Signal',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Latest News (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'Failed to find execution price for closing',

    # /account
    'account_balance':             '💰 USDT Balance: `{balance:.2f}`',
    'account_realized_header':     '📈 *Realized PnL:*',
    'account_realized_day':        '  • Today : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 days: `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *Unrealized PnL:*',
    'account_unreal_total':        '  • Total : `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % of IM: `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Your Settings:*',
    'config_percent':              '• 🎚 % per Trade       : `{percent}%`',
    'config_coins':                '• 💠 Coins            : `{coins}`',
    'config_limit_only':           '• 🎯 Limit orders     : {state}',
    'config_atr_mode':             '• 🏧 ATR-Trailing SL  : {atr}',
    'config_trade_oi':             '• 📊 Trade OI         : {oi}',
    'config_trade_rsi_bb':         '• 📈 Trade RSI+BB     : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%              : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%              : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 No open orders',
    'open_orders_header':          '*📒 Your Open Orders:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Side: `{side}`\n"
        "   • Qty : `{qty}`\n"
        "   • Price: `{price}`\n"
        "   • ID  : `{id}`"
    ),
    'open_orders_error':           '❌ Error fetching orders: {error}',

    # Manual coin selection
    'enter_coins':                 "Enter comma-separated symbols, e.g.:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Coins selected: {coins}',

    # Positions
    'no_positions':                '🚫 No open positions',
    'positions_header':            '📊 Your Open Positions:',
    'position_item':               (
        "— Position #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • Size           : {size}\n"
        "  • Entry Price    : {avg:.8f}\n"
        "  • Mark Price     : {mark:.8f}\n"
        "  • Liquidation    : {liq}\n"
        "  • Initial Margin : {im:.2f}\n"
        "  • Maint Margin   : {mm:.2f}\n"
        "  • Position Bal.  : {pm:.2f}\n"
        "  • Take Profit    : {tp}\n"
        "  • Stop Loss      : {sl}\n"
        "  • Unreal PnL     : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'positions_overall':           'Total Unreal PnL: {pnl:+.2f} ({pct:+.2f}%)',

    # Position management (inline)
    'open_positions_header':       '📊 *Open positions*',
    'positions_count':             'positions',
    'positions_count_total':       'Total positions',
    'total_unrealized_pnl':        'Total unrealized P/L',
    'total_pnl':                   'Total P/L',
    'btn_close_short':             'Close',
    'btn_close_all':               'Close all positions',
    'btn_close_position':          'Close position',
    'btn_confirm_close':           'Confirm close',
    'btn_confirm_close_all':       'Yes, close all',
    'btn_cancel':                  '❌ Cancel',
    'btn_back':                    '🔙 Back',
    'confirm_close_position':      'Close position',
    'confirm_close_all':           'Close ALL positions',
    'position_not_found':          'Position not found or already closed',
    'position_already_closed':     'Position already closed',
    'position_closed_success':     'Position closed',
    'position_close_error':        'Error closing position',
    'positions_closed':            'Positions closed',
    'all_positions_closed':        'All positions closed',
    'errors':                      'Errors',

    # Position view
    'position':                    'Position',
    'entry':                       'Entry',
    'current':                     'Current',
    'size':                        'Size',

    # % per trade
    'set_percent_prompt':          'Enter percentage of balance per trade (e.g. 2.5):',
    'percent_set_success':         '✅ % per trade set: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Limit-Only orders {state}',
    'feature_limit_only':          'Limit-Only',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Elcaro Indicators*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. Adaptive Trend',
    'indicator_4':                 '4. Dynamic Regression',

    # Support
    'support_prompt':              '✉️ Need help? Click below:',
    'support_button':              'Contact Support',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 No open positions',
    'update_tpsl_prompt':          'Enter SYMBOL TP SL, e.g.:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Invalid format. Use: SYMBOL TP SL\nE.g.: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Enter your Bybit API Key:',
    'api_saved':                   '✅ API Key saved',
    'enter_secret':                'Enter your Bybit API Secret:',
    'secret_saved':                '✅ API Secret saved',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ Enter TP% value',
    'tp_set_success':              '✅ TP% set: {pct}%',
    'enter_sl':                    '❌ Enter SL% value',
    'sl_set_success':              '✅ SL% set: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: requires 4 args (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: requires 3 args (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE must be LONG or SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ API Key/Secret not set',
    'api_missing_notice':          '⚠️ You do not have exchange API keys configured. Please add your API Key and Secret in the settings (🔑 API and 🔒 Secret buttons), otherwise the bot cannot trade for you.',
    'bybit_invalid_response':      '❌ Bybit returned invalid response',
    'bybit_error':                 '❌ Bybit error {path}: {data}',

    # Auto notifications
    'new_position': (
        '🚀 New position {symbol} @ {entry:.6f}, size={size}\n'
        '📍 {exchange} • {market_type}'
    ),
    'sl_auto_set':                 '🛑 SL set automatically: {price:.6f}',
    'auto_close_position':         '⏱ Position {symbol} (TF={tf}) open > {tf} and losing, closed automatically.',
    'position_closed': (
        '🔔 Position {symbol} closed by *{reason}*:\n'
        '• Strategy: `{strategy}`\n'
        '• Entry: `{entry:.8f}`\n'
        '• Exit: `{exit:.8f}`\n'
        '• PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '📍 {exchange} • {market_type}'
    ),

    # Entries & errors - unified format with full info
    'oi_limit_entry':              '📉 *OI Limit Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit error: {msg}',
    'oi_market_entry':             '📉 *OI Market Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI error\n🪙 {symbol} {side}\n\n{msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Limit Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Market Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB error\n🪙 {symbol} {side}\n\n{msg}',

    'oi_analysis':                 '📊 *OI {symbol} analysis* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Limit Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit error: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Market Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market error: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>Insufficient balance!</b>\n\n💰 Not enough FREE margin on your {account_type} account.\n\n<b>Why this happens:</b>\nAll your balance is locked in open positions.\n\n<b>Solutions:</b>\n• Close some open positions to free margin\n• Reduce position size (% per trade)\n• Lower leverage\n• Use /positions to view and close positions',
    'insufficient_balance_error_extended': '❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough FREE margin on your {account_type} account.\n\n<b>Why this happens:</b>\nAll your balance is locked in open positions.\n\n<b>Solutions:</b>\n• Close some open positions\n• Reduce position size (% per trade)\n• Lower leverage',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Leverage too high!</b>\n\n⚙️ Your configured leverage exceeds the maximum allowed for this symbol.\n\n<b>Maximum allowed:</b> {max_leverage}x\n\n<b>Solution:</b> Go to strategy settings and reduce leverage.',

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Limit Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit error: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Market Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market error: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *Elcaro Limit Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Elcaro Limit error: {msg}',
    'elcaro_market_entry':         '🔥 *Elcaro Market Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Elcaro Market error: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

    # Fibonacci Extension Strategy
    'fibonacci_limit_entry':       '📐 *Fibonacci Limit Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Entry Zone: {entry_zone}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':       '❌ Fibonacci Limit error: {msg}',
    'fibonacci_market_entry':      '📐 *Fibonacci Market Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':         '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':      '❌ Fibonacci error\n🪙 {symbol} {side}\n\n{msg}',
    'fibonacci_analysis':          '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':           'Fibonacci',
    'stats_fibonacci':             '📐 Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 Admin Panel:',
    'admin_pause':                 '⏸️ Trading & notifications paused for all.',
    'admin_resume':                '▶️ Trading & notifications resumed for all.',
    'admin_closed':                '✅ Closed total {count} {type}.',
    'admin_canceled_limits':       '✅ Canceled {count} limit orders.',

    # Coin groups
    'select_coin_group':           'Select coin group:',
    'group_all':                   'ALL',
    'group_top100':                'TOP100',
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ Coin group set: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *RSI+BB analysis*\n'
        '• Price: `{price:.6f}`\n'
        '• RSI: `{rsi:.1f}` ({zone})\n'
        '• BB upper: `{bb_hi:.4f}`\n'
        '• BB lower: `{bb_lo:.4f}`\n\n'
        '*Entering MARKET {side} by RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'Oversold (<30)',
    'rsi_zone_overbought':         'Overbought (>70)',
    'rsi_zone_neutral':            'Neutral (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ Invalid TP/SL for LONG.\n'
        'Current price: {current:.2f}\n'
        'Expected: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ Invalid TP/SL for SHORT.\n'
        'Current price: {current:.2f}\n'
        'Expected: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 You have no open position on {symbol}',
    'tpsl_set_success':            '✅ TP={tp:.2f} and SL={sl:.2f} set for {symbol}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Language',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Stop mode: *{mode}*',
    'config_dca':                  'DCA: Leg1=-{dca1}%, Leg2=-{dca2}%',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ Limit order for {symbol} filled @ {price}',
    'limit_order_cancelled':       '⚠️ Limit order for {symbol} (ID: {order_id}) cancelled.',
    'fixed_sl_tp':                 '✅ {symbol}: SL set at {sl}, TP set at {tp}',
    'tp_part':                     ', TP set at {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL set at {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL set at {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP initialized at {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL moved to breakeven at {entry}',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP updated to {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Position {symbol} closed but failed to log: {error}\n'
        'Please contact support.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Fixed %',

    # System notices
    'db_quarantine_notice':        '⚠️ Logs are temporarily paused. Quiet mode enabled for 1 hour.',

    # Fallback
    'fallback':                    '❓ Please use the menu buttons.',
    
    # Symbols / markers
    'dash':                      '—',
    'mark_yes':                  '✅',
    'mark_no':                   '—',
    'mark_ban':                  '⛔️',

    # Access / terms / moderation
    'banned':                    '🚫 You are blocked.',
    'invite_only':               '🔒 Invite-only access. Please wait for admin approval.',
    'need_terms':                '⚠️ Please accept the terms first: /terms',
    'please_confirm':            'Please confirm:',
    'terms_ok':                  '✅ Thank you! Terms accepted.',
    'terms_declined':            '❌ You declined the terms. Access is closed. You can return with /terms.',
    'usage_approve':             'Usage: /approve <user_id>',
    'usage_ban':                 'Usage: /ban <user_id>',
    'not_allowed':               'Not allowed',
    'bad_payload':               'Bad payload',
    'unknown_action':            'Unknown action',

    # Admin: new user notification
    'title':                     'New user',
    'wave':                      '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Name: {name}\n'
        '• Username: {uname}\n'
        '• Lang: {lang}\n'
        '• Allowed: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve':               '✅ Approve',
    'btn_ban':                   '⛔️ Ban',
    'admin_notify_fail':         'Failed to notify admin: {e}',
    'moderation_approved':       '✅ Approved: {target}',
    'moderation_banned':         '⛔️ Banned: {target}',
    'approved_user_dm':          '✅ Access approved. Press /start.',
    'banned_user_dm':            '🚫 You are blocked.',

    # Admin: users list / navigation
    'users_not_found':           '😕 No users found.',
    'users_page_info':           '📄 Page {page}/{pages} — total: {total}',
    'user_card_html': (
        '<b>👤 User</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Name: {full_name}\n'
        '• Username: {uname}\n'
        '• Lang: <code>{lang}</code>\n'
        '• Allowed: {allowed}\n'
        '• Banned: {banned}\n'
        '• Terms: {terms}\n'
        '• % per trade: <code>{percent}</code>'
    ),
    'btn_blacklist':             '🚫 Blacklist',
    'btn_delete_user':           '🗑 Delete from DB',
    'btn_prev':                  '⬅️ Back',
    'btn_next':                  '➡️ Next',
    'nav_caption':               '🧭 Navigation:',
    'bad_page':                  'Invalid page.',
    'admin_user_delete_fail':    '❌ Failed to delete {target}: {error}',
    'admin_user_deleted':        '🗑 User {target} deleted from DB.',
    'user_access_approved':      '✅ Access approved. Press /start.',

    # Admin panel & actions (buttons + notices)
    'admin_pause_all':           '⏸️ Pause for all',
    'admin_resume_all':          '▶️ Resume',
    'admin_close_longs':         '🔒 Close all LONGs',
    'admin_close_shorts':        '🔓 Close all SHORTs',
    'admin_cancel_limits':       '❌ Delete limit orders',
    'admin_users':               '👥 Users',
    'admin_pause_notice':        '⏸️ Trading & notifications paused for all.',
    'admin_resume_notice':       '▶️ Trading & notifications resumed for all.',
    'type_longs':                'longs',
    'type_shorts':               'shorts',
    'admin_closed_total':        '✅ Closed total {count} {type}.',
    'admin_canceled_limits_total':'✅ Canceled {count} limit orders.',

    # Terms buttons
    'terms_btn_accept':          '✅ Accept',
    'terms_btn_decline':         '❌ Decline',

    # Market emojis (signal colors)
    'emoji_long':                '🟢',
    'emoji_short':               '🔴',
    'emoji_neutral':             '⚪️',

    # Strategy Settings
    'button_strategy_settings':      '🎯 Strategies',
    'strategy_settings_header':      '⚙️ *Strategy Settings*',
    'strategy_param_header':         '⚙️ *{name} Settings*',
    'using_global':                  'Using global settings',
    'global_default':                'Global',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_fibonacci':               '📐 Fibonacci',
    'dca_settings':                  '⚙️ DCA Settings',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA Leg 1 %',
    'dca_leg2':                      '📉 DCA Leg 2 %',
    'param_percent':                 '📊 Entry %',
    'param_sl':                      '🔻 Stop-Loss %',
    'param_tp':                      '🔺 Take-Profit %',
    'param_reset':                   '🔄 Reset to Global',
    'btn_close':                     '❌ Close',
    'prompt_entry_pct':              'Enter Entry % (risk per trade):',
    'prompt_sl_pct':                 'Enter Stop-Loss %:',
    'prompt_tp_pct':                 'Enter Take-Profit %:',
    'prompt_dca_leg1':               'Enter DCA Leg 1 % (e.g., 10):',
    'prompt_dca_leg2':               'Enter DCA Leg 2 % (e.g., 25):',
    'prompt_atr_periods':            'Enter ATR Periods (e.g., 7):',
    'prompt_atr_mult':               'Enter ATR Multiplier for trailing SL step (e.g., 1.0):',
    'prompt_atr_trigger':            'Enter ATR Trigger % to activate trailing (e.g., 2.0):',
    'settings_reset':                'Settings reset to global',
    'strat_setting_saved':           '✅ {name} {param} set to {value}',
    'dca_setting_saved':             '✅ DCA {leg} set to {value}%',
    'invalid_number':                '❌ Invalid number. Enter a value between 0 and 100.',
    'dca_10pct':                     'DCA −{pct}%: avg down on {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: avg down on {symbol} qty={qty} @ {price}',

    # ATR settings UI
    'param_atr_periods':             '📈 ATR Periods',
    'param_atr_mult':                '📉 ATR Multiplier (SL step)',
    'param_atr_trigger':             '🎯 ATR Trigger %',

    # Hardcoded strings fix
    'terms_unavailable':             'Terms of Service are unavailable. Please contact the admin.',
    'terms_confirm_prompt':          'Please confirm:',
    'your_id':                       'Your ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Error: {msg}',
    'error_fetch_balance':           '❌ Error fetching balance: {error}',
    'error_fetch_orders':            '❌ Error fetching orders: {error}',
    'error_occurred':                '❌ Error: {error}',

    # Trading Statistics
    'button_stats':                  '📊 Statistics',
    'stats_title':                   'Trading Statistics',
    'stats_strategy':                'Strategy',
    'stats_period':                  'Period',
    'stats_overview':                'Overview',
    'stats_total_trades':            'Total trades',
    'stats_closed':                  'Closed',
    'stats_open':                    'Open',
    'stats_results':                 'Results',
    'stats_winrate':                 'Winrate',
    'stats_total_r':                 'Total R',
    'stats_avg_r':                   'Avg R',
    'stats_by_direction':            'By Direction',
    'stats_long':                    'Long',
    'stats_short':                   'Short',
    'stats_pnl':                     'Profit/Loss',
    'stats_gross_profit':            'Profit',
    'stats_gross_loss':              'Loss',
    'stats_total_pnl':               'Total P/L',
    'stats_realized_pnl':            'Realized',
    'stats_unrealized_pnl':          'Unrealized',
    'stats_combined_pnl':            'Combined',
    'stats_profit_factor':           'PF',
    'stats_strategy_settings':       'Strategy Settings',
    'settings_entry_pct':            'Entry',
    'settings_leverage':             'Leverage',
    'settings_trading_mode':         'Mode',
    'settings_direction':            'Direction',
    'stats_all':                     '📈 All',
    'stats_oi':                      '📉 OI',
    'stats_rsi_bb':                  '📊 RSI+BB',
    'stats_scryptomera':             '🐱 Scryptomera',
    'stats_scalper':                 '⚡ Scalper',
    'stats_elcaro':                  '🔥 Elcaro',
    'stats_fibonacci':               '📐 Fibonacci',
    'stats_spot':                    '💹 Spot',
    'stats_spot_title':              'Spot DCA Statistics',
    'stats_spot_config':             'Configuration',
    'stats_spot_holdings':           'Holdings',
    'stats_spot_summary':            'Summary',
    'stats_spot_current_value':      'Current Value',
    'stats_period_all':              'All time',
    'stats_period_today':            'Today',
    'stats_period_week':             'Week',
    'stats_period_month':            'Month',
    'stats_demo':                    '🔵 Demo',
    'stats_real':                    '🟢 Real',

    # Scryptomera direction settings
    'param_direction': '🎯 Direction',
    'param_long_settings': '📈 LONG Settings',
    'param_short_settings': '📉 SHORT Settings',
    'dir_all': '🔄 ALL (LONG + SHORT)',
    'dir_long_only': '📈 LONG only',
    'dir_short_only': '📉 SHORT only',
    'scrypto_side_header': '{emoji} *Scryptomera {side} Settings*',
    'scalper_side_header': '{emoji} *Scalper {side} Settings*',
    'global_settings': '🌐 Global Settings',
    'global_settings_header': '🌐 *Global Trading Settings*',
    'global_settings_info': 'These settings are used as defaults when strategy-specific settings are not configured.',
    'prompt_long_entry_pct': '📈 LONG Entry % (risk per trade):',
    'prompt_long_sl_pct': '📈 LONG Stop-Loss %:',
    'prompt_long_tp_pct': '📈 LONG Take-Profit %:',
    'prompt_short_entry_pct': '📉 SHORT Entry % (risk per trade):',
    'prompt_short_sl_pct': '📉 SHORT Stop-Loss %:',
    'prompt_short_tp_pct': '📉 SHORT Take-Profit %:',

    # Order type settings
    'param_order_type': '📤 Order Type',
    'order_type_market': '⚡ Market orders',
    'order_type_limit': '🎯 Limit orders',

    # Leverage settings
    'param_leverage': '⚡ Leverage',
    'prompt_leverage': 'Enter Leverage (1-100):',
    'auto_default': 'Auto',

    # Coins group per strategy
    'param_coins_group': '🪙 Coins',
    'select_coins_for_strategy': '🪙 *Select coins group for {name}*',
    'group_global': '📊 Global (use common setting)',

    # Elcaro AI
    'elcaro_ai_info': '🤖 *AI-Powered Trading*',
    'elcaro_ai_desc': '_All parameters are parsed from AI signals automatically:_',

    # Fibonacci
    'fibonacci_info': '📐 *Fibonacci Extension Strategy*',
    'fibonacci_desc': '_Entry, SL, TP - from Fibonacci levels in signal._',
    'prompt_min_quality': 'Enter Min Quality % (0-100):',

    # Limit Ladder
    'limit_ladder': '📉 Limit Ladder',
    'limit_ladder_header': '📉 *Limit Ladder Settings*',
    'limit_ladder_settings': '⚙️ Ladder Settings',
    'ladder_count': 'Number of orders',
    'ladder_info': 'Limit orders placed below entry for DCA. Each order has a % offset from entry and a % of deposit.',
    'prompt_ladder_pct_entry': '📉 Enter % below entry price for order {idx}:',
    'prompt_ladder_pct_deposit': '💰 Enter % of deposit for order {idx}:',
    'ladder_order_saved': '✅ Order {idx} saved: -{pct_entry}% @ {pct_deposit}% deposit',
    'ladder_orders_placed': '📉 Placed {count} ladder limit orders for {symbol}',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    # License status messages
    'no_license': '⚠️ You need an active subscription to use this feature.\n\nUse /subscribe to purchase a license.',
    'no_license_trading': '⚠️ You need an active subscription to trade.\n\nUse /subscribe to purchase a license.',
    'license_required': '⚠️ This feature requires a {required} subscription.\n\nUse /subscribe to upgrade.',
    'trial_demo_only': '⚠️ Trial license allows only demo trading.\n\nUpgrade to Premium or Basic for real trading: /subscribe',
    'basic_strategy_limit': '⚠️ Basic license on real account allows only: {strategies}\n\nUpgrade to Premium for all strategies: /subscribe',
    
    # Subscribe menu
    'subscribe_menu_header': '💎 *Subscription Plans*',
    'subscribe_menu_info': 'Choose your plan to unlock trading features:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Trial (Free)',
    'btn_enter_promo': '🎟 Promo Code',
    'btn_my_subscription': '📋 My Subscription',
    
    # Premium plan
    'premium_title': '💎 *PREMIUM PLAN*',
    'premium_desc': '''✅ Full access to all features
✅ All 5 strategies: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ Real + Demo trading
✅ Priority support
✅ ATR-based dynamic SL/TP
✅ Limit ladder DCA
✅ All future updates''',
    'premium_1m': '💎 1 Month — {price} TRC',
    'premium_3m': '💎 3 Months — {price} TRC (-10%)',
    'premium_6m': '💎 6 Months — {price} TRC (-20%)',
    'premium_12m': '💎 12 Months — {price} TRC (-30%)',
    
    # Basic plan
    'basic_title': '🥈 *BASIC PLAN*',
    'basic_desc': '''✅ Full demo account access
✅ Real account: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Fibonacci, Spot — Premium only
✅ Standard support
✅ ATR-based dynamic SL/TP''',
    'basic_1m': '🥈 1 Month — {price} TRC',
    
    # Trial plan
    'trial_title': '🎁 *TRIAL PLAN (FREE)*',
    'trial_desc': '''✅ Full demo account access
✅ All 5 strategies on demo
❌ Real trading not available
⏰ Duration: 7 days
🎁 One time only''',
    'trial_activate': '🎁 Activate Free Trial',
    'trial_already_used': '⚠️ You have already used your free trial.',
    'trial_activated': '🎉 Trial activated! You have 7 days of full demo access.',
    
    # Payment
    'payment_select_method': '💳 *Select Payment Method*',
    'btn_pay_trc': '◈ Pay with TRC',
    'btn_pay_ton': '💎 TON (deprecated)',
    'payment_trc_title': '◈ Payment via Triacelo Coin (TRC)',
    'payment_trc_desc': 'You will be charged {amount} TRC for {plan} ({period}).',
    'payment_ton_title': '💎 Payment via TON (Deprecated)',
    'payment_ton_desc': '''TON payments are no longer supported.
Please use TRC tokens instead.''',
    'btn_verify_ton': '✅ I Paid — Verify',
    'btn_check_again': '🔄 Check Again',
    'payment_processing': '⏳ Processing payment...',
    'payment_verifying': '⏳ Verifying payment...',
    'payment_success': '🎉 Payment successful!\n\n{plan} activated until {expires}.',
    'payment_failed': '❌ Payment failed: {error}',
    'payment_ton_not_configured': '❌ TON payments are deprecated. Use TRC tokens.',
    'payment_session_expired': '❌ Payment session expired. Please start again.',
    'payment_trc_insufficient': '''❌ Insufficient TRC balance.

Your balance: {balance} TRC
Required: {required} TRC

Top up your wallet to continue.''',
    
    # Wallet
    'wallet_title': '◈ *TRC Wallet*',
    'wallet_balance': '''💰 *Your TRC Wallet*

◈ Balance: *{balance} TRC*
📈 Staked: *{staked} TRC*
🎁 Pending Rewards: *{rewards} TRC*

💵 Total Value: *${total_usd}*
📍 1 TRC = 1 USDT''',
    'wallet_address': '📍 Address: `{address}`',
    'wallet_btn_deposit': '📥 Deposit',
    'wallet_btn_withdraw': '📤 Withdraw',
    'wallet_btn_stake': '📈 Stake',
    'wallet_btn_unstake': '📤 Unstake',
    'wallet_btn_history': '📋 History',
    'wallet_btn_back': '« Back',
    'wallet_deposit_title': '📥 *Deposit TRC*',
    'wallet_deposit_desc': '''Send TRC tokens to your wallet address:

`{address}`

💡 *Demo mode:* Click below for free test tokens.''',
    'wallet_deposit_demo': '🎁 Get 100 TRC (Demo)',
    'wallet_deposit_success': '✅ Deposited {amount} TRC successfully!',
    'wallet_withdraw_title': '📤 *Withdraw TRC*',
    'wallet_withdraw_desc': 'Enter destination address and amount:',
    'wallet_withdraw_success': '✅ Withdrawn {amount} TRC to {address}',
    'wallet_withdraw_failed': '❌ Withdrawal failed: {error}',
    'wallet_stake_title': '📈 *Stake TRC*',
    'wallet_stake_desc': '''Stake your TRC tokens to earn *12% APY*!

💰 Available: {available} TRC
📈 Currently Staked: {staked} TRC
🎁 Pending Rewards: {rewards} TRC

Daily rewards • Instant unstaking''',
    'wallet_stake_success': '✅ Staked {amount} TRC successfully!',
    'wallet_unstake_success': '✅ Unstaked {amount} TRC + {rewards} TRC rewards!',
    'wallet_history_title': '📋 *Transaction History*',
    'wallet_history_empty': 'No transactions yet.',
    'wallet_history_item': '{type_emoji} {type}: {amount:+.2f} TRC\n   {date}',
    
    # My subscription
    'my_subscription_header': '📋 *My Subscription*',
    'my_subscription_active': '''📋 *Current Plan:* {plan}
⏰ *Expires:* {expires}
📅 *Days Left:* {days}''',
    'my_subscription_none': '❌ No active subscription.\n\nUse /subscribe to purchase a plan.',
    'my_subscription_history': '📜 *Payment History:*',
    'subscription_expiring_soon': '⚠️ Your {plan} subscription expires in {days} days!\n\nRenew now: /subscribe',
    
    # Promo codes
    'promo_enter': '🎟 Enter your promo code:',
    'promo_success': '🎉 Promo code applied!\n\n{plan} activated for {days} days.',
    'promo_invalid': '❌ Invalid promo code.',
    'promo_expired': '❌ This promo code has expired.',
    'promo_used': '❌ This promo code has already been used.',
    'promo_already_used': '❌ You have already used this promo code.',
    
    # Admin license management
    'admin_license_menu': '🔑 *License Management*',
    'admin_btn_grant_license': '🎁 Grant License',
    'admin_btn_view_licenses': '📋 View Licenses',
    'admin_btn_create_promo': '🎟 Create Promo',
    'admin_btn_view_promos': '📋 View Promos',
    'admin_btn_expiring_soon': '⚠️ Expiring Soon',
    'admin_grant_select_type': 'Select license type:',
    'admin_grant_select_period': 'Select period:',
    'admin_grant_enter_user': 'Enter user ID:',
    'admin_license_granted': '✅ {plan} granted to user {uid} for {days} days.',
    'admin_license_extended': '✅ License extended by {days} days for user {uid}.',
    'admin_license_revoked': '✅ License revoked for user {uid}.',
    'admin_promo_created': '✅ Promo code created: {code}\nType: {type}\nDays: {days}\nMax uses: {max}',

    # =====================================================
    # ADMIN USER MANAGEMENT
    # =====================================================
    'admin_users_management': '👥 Users',
    'admin_licenses': '🔑 Licenses',
    'admin_search_user': '🔍 Find User',
    'admin_users_menu': '👥 *User Management*\n\nSelect filter or search:',
    'admin_all_users': '👥 All Users',
    'admin_active_users': '✅ Active',
    'admin_banned_users': '🚫 Banned',
    'admin_no_license': '❌ No License',
    'admin_no_users_found': 'No users found.',
    'admin_enter_user_id': '🔍 Enter user ID to search:',
    'admin_user_found': '✅ User {uid} found!',
    'admin_user_not_found': '❌ User {uid} not found.',
    'admin_invalid_user_id': '❌ Invalid user ID. Enter a number.',
    'admin_view_card': '👤 View Card',
    
    # User card
    'admin_user_card': '''👤 *User Card*

📋 *ID:* `{uid}`
{status_emoji} *Status:* {status}
📝 *Terms:* {terms}

{license_emoji} *License:* {license_type}
📅 *Expires:* {license_expires}
⏳ *Days Left:* {days_left}

🌐 *Language:* {lang}
📊 *Trading Mode:* {trading_mode}
💰 *% per Trade:* {percent}%
🪙 *Coins:* {coins}

🔌 *API Keys:*
  Demo: {demo_api}
  Real: {real_api}

📈 *Strategies:* {strategies}

📊 *Statistics:*
  Positions: {positions}
  Trades: {trades}
  PnL: {pnl}
  Winrate: {winrate}%

💳 *Payments:*
  Total: {payments_count}
  TRC: {total_trc} ◈

📅 *First Seen:* {first_seen}
🕐 *Last Seen:* {last_seen}
''',
    
    # User actions
    'admin_btn_grant_lic': '🎁 Grant',
    'admin_btn_extend': '⏳ Extend',
    'admin_btn_revoke': '🚫 Revoke',
    'admin_btn_ban': '🚫 Ban',
    'admin_btn_unban': '✅ Unban',
    'admin_btn_approve': '✅ Approve',
    'admin_btn_message': '✉️ Message',
    'admin_btn_delete': '🗑 Delete',
    
    'admin_user_banned': 'User banned!',
    'admin_user_unbanned': 'User unbanned!',
    'admin_user_approved': 'User approved!',
    'admin_confirm_delete': '⚠️ *Confirm deletion*\n\nUser {uid} will be permanently deleted!',
    'admin_confirm_yes': '✅ Yes, Delete',
    'admin_confirm_no': '❌ Cancel',
    
    'admin_select_license_type': 'Select license type for user {uid}:',
    'admin_select_period': 'Select period:',
    'admin_select_extend_days': 'Select days to extend for user {uid}:',
    'admin_license_granted_short': 'License granted!',
    'admin_license_extended_short': 'Extended by {days} days!',
    'admin_license_revoked_short': 'License revoked!',
    
    'admin_enter_message': '✉️ Enter message to send to user {uid}:',
    'admin_message_sent': '✅ Message sent to user {uid}!',
    'admin_message_failed': '❌ Failed to send message: {error}',

    # =====================================================
    # ADMIN PAYMENTS & REPORTS
    # =====================================================
    'admin_payments': '💳 Payments',
    'admin_reports': '📊 Reports',
    'admin_payments_menu': '💳 *Payments Management*',
    'admin_all_payments': '📜 All Payments',
    'admin_no_payments_found': 'No payments found.',
    
    'admin_reports_menu': '📊 *Reports & Analytics*\n\nSelect report type:',
    'admin_global_stats': '📊 Global Stats',
    'admin_demo_stats': '🎮 Demo Stats',
    'admin_real_stats': '💰 Real Stats',
    'admin_strategy_breakdown': '🎯 By Strategy',
    'admin_top_traders': '🏆 Top Traders',
    'admin_user_report': '👤 User Report',
    'admin_enter_user_for_report': '👤 Enter user ID for detailed report:',
    'admin_generating_report': '📊 Generating report for user {uid}...',
    'admin_view_report': '📊 View Report',
    'admin_view_user': '👤 User Card',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "HyperLiquid Trading",
    "hl_reset_settings": "🔄 Reset to Bybit Settings",

    # =====================================================
    # HARDCODED PHRASES FIX
    # =====================================================
    "min_amount_error": "❌ Minimum amount is 1 USDT",
    "max_amount_error": "❌ Maximum amount is 100,000 USDT",
    "invalid_amount": "❌ Invalid number. Please enter a valid amount.",
    "hl_no_positions": "📭 No open positions on HyperLiquid.",
    "hl_no_orders": "📭 No open orders on HyperLiquid.",
    "hl_no_history": "📭 No trade history on HyperLiquid.",
    "cancelled": "❌ Cancelled.",
    "invalid_number": "❌ Please enter a valid number.",
    "entry_pct_range_error": "❌ Entry % must be between 0.1 and 100.",
    "sl_tp_range_error": "❌ SL/TP % must be between 0.1 and 500.",
    "leverage_range_error": "❌ Leverage must be between 1 and 100.",
    "hl_setup_cancelled": "❌ HyperLiquid setup cancelled.",

    # =====================================================
    # DEEP LOSS POSITION ALERTS
    # =====================================================
    "btn_close_position": "❌ Close Position",
    "btn_enable_dca": "📈 Enable DCA Averaging",
    "btn_ignore": "🔇 Ignore",
    "deep_loss_alert": "⚠️ <b>Position in Deep Loss!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Loss: <code>{loss_pct:.2f}%</code>\n💰 Entry: <code>{entry}</code>\n📍 Current: <code>{mark}</code>\n\n❌ Stop-loss cannot be set above entry price.\n\n<b>What to do?</b>\n• <b>Close</b> - lock in the loss\n• <b>DCA Average</b> - add to position to average down\n• <b>Ignore</b> - leave as is",
    "position_already_closed": "❌ Position {symbol} is already closed.",
    "deep_loss_closed": "✅ Position {symbol} closed.\n\nLoss locked in. Sometimes it's better to take a small loss than hope for a reversal.",
    "deep_loss_close_error": "❌ Error closing position: {error}",
    "dca_already_enabled": "✅ DCA averaging is already enabled!\n\n📊 <b>{symbol}</b>\nBot will automatically add to position on drawdown:\n• -10% → add\n• -25% → add\n\nThis helps average the entry price.",
    "dca_enabled_for_symbol": "✅ DCA averaging enabled!\n\n📊 <b>{symbol}</b>\nBot will automatically add to position on drawdown:\n• -10% → add (average down)\n• -25% → add (average down)\n\n⚠️ DCA requires sufficient balance for adds.\nConfigure settings: /strategy_settings",
    "dca_enable_error": "❌ Error: {error}",
    "deep_loss_ignored": "🔇 Got it, position {symbol} left unchanged.\n\n⚠️ Remember: without stop-loss, risk of losses is unlimited.\nYou can close the position manually via /positions",



    # Hardcore trading phrase
    'hardcore_mode': '💀 *HARDCORE MODE*: No mercy, no regrets. Only profit or death! 🔥',
}
