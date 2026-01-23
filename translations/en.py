# translations/en.py
TEXTS = {
    # Main menu - Professional trading interface
    'welcome':                     '''🔥 <b>Lyxen Trading Terminal</b>

⚡ <b>&lt; 100ms</b> execution
🛡️ <b>Risk management</b> built-in
💎 <b>24/7</b> automated trading

Bybit • HyperLiquid • Multi-strategy''',
    'no_strategies':               '❌ No active strategies',
    'guide_caption':               '📚 <b>User Guide</b>\n\nAPI setup, strategies, risk management.',
    'privacy_caption':             '📜 <b>Privacy Policy</b>\n\n🔐 Encrypted storage\n✅ No data sharing',
    
    # ═══════════════════════════════════════════════════════════════════
    # MODERN MENU BUTTONS - Stylish & Persuasive
    # ═══════════════════════════════════════════════════════════════════
    'button_api':                  '🔐 Connect API',
    'button_secret':               '🔑 Secret Key',
    'button_api_settings':         '⚙️ API Setup',
    'button_subscribe':            '👑 PREMIUM',
    'button_licenses':             '🎫 Licenses',
    'button_admin':                '🛡️ Admin',
    'button_balance':              '💎 Portfolio',
    'button_orders':               '📊 Orders',
    'button_positions':            '🎯 Positions',
    'button_history':              '📜 History',
    'button_strategies':           '🤖 AI Bots',
    'button_api_keys':             '🔗 Exchange',
    'button_terminal':             '💻 Terminal',
    'button_bybit':                '🟠 Bybit',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_switch_bybit':         '🔄 Bybit',
    'button_switch_hl':            '🔄 HL',
    'button_percent':              '⚡ Risk %',
    'button_coins':                '🪙 Coins',
    'button_market':               '📈 Market',
    'button_manual_order':         '🎯 Sniper',
    'button_update_tpsl':          '🛡️ TP/SL',
    'button_cancel_order':         '✖️ Cancel',
    'button_limit_only':           '📍 Limit',
    'button_toggle_oi':            '🐋 OI Tracker',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_scalper':              '⚡ Scalper',
    'button_elcaro':               '🔥 Lyxen',
    'button_fibonacci':            '📐 Fibonacci',
    'button_settings':             '⚙️ Config',
    'button_indicators':           '📡 Signals',
    'button_support':              '💬 Support',
    'button_back':                 '← Back',
    'button_close':                '✖️ Close',
    'button_refresh':              '🔄 Refresh',
    'button_confirm':              '✅ Confirm',
    'button_cancel':               '❌ Cancel',
    
    # Menu section headers (for API settings, etc.)
    'menu_section_demo':           '══ 🧪 DEMO ══',
    'menu_section_real':           '══ 💼 REAL ══',
    'menu_test_connection':        '🔄 Test',
    'menu_delete':                 '🗑️ Delete',
    
    # Exchange indicators
    'exchange_bybit_demo':         '🟠 Bybit 🎮',
    'exchange_bybit_real':         '🟠 Bybit 💵',
    'exchange_bybit_both':         '🟠 Bybit 🔀',
    'exchange_hl_testnet':         '🔷 HL 🧪',
    'exchange_hl_mainnet':         '🔷 HL 🌐',
    
    # Strategy toggles
    'toggle_oi_status':            '🐋 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',
    'config_trade_scalper':        '⚡ Scalper: {state}',
    'config_trade_elcaro':         '🔥 Lyxen: {state}',
    'config_trade_fibonacci':      '📐 Fibonacci: {state}',

    # API Settings
    'api_settings_title':          '🔐 <b>Exchange Connection</b>',
    'api_demo_title':              '🧪 Demo Account',
    'api_real_title':              '💼 Real Account',
    'api_key_set':                 '✅ Set',
    'api_key_not_set':             '❌ Not set',
    'not_set':                     '—',
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

    # Exchange Mode & Multi-Exchange UI
    'exch_mode_bybit_only':        '🟠 Bybit Only',
    'exch_mode_hl_only':           '🟢 HyperLiquid Only',
    'exch_mode_both':              '🔄 Both Exchanges',
    'btn_connect_hl':              '➕ Connect HyperLiquid',
    'exch_not_configured':         '❌ Not configured',
    'exch_not_connected':          '❌ Not connected',
    'exch_trading_mode':           'Trading Mode',
    'exch_active':                 '🟢 Active',
    'exch_inactive':               '⚪ Inactive',
    'exch_switch_success':         '✅ Switched to {exchange}',
    'exch_select_mode':            'Select exchange mode:',

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
    'spot_freq_biweekly':          'Bi-Weekly',
    'spot_trailing_enabled':       '✅ Trailing TP enabled',
    'spot_trailing_disabled':      '❌ Trailing TP disabled',
    'spot_grid_started':           '✅ Grid bot started for {coin}',
    'spot_grid_stopped':           '🛑 Grid bot stopped for {coin}',
    'spot_limit_placed':           '✅ Limit order placed',
    'spot_limit_cancelled':        '❌ Order cancelled',

    # Strategy trading mode
    'strat_mode_global':           '🌐 Global',
    'strat_mode_demo':             '🧪 Demo',
    'strat_mode_real':             '💰 Real',
    'strat_mode_both':             '🔄 Both',
    'strat_mode_changed':          '✅ {strategy} trading mode: {mode}',
    
    # Toggle & Mode labels
    'toggle_on':                   '✅ Enabled',
    'toggle_off':                  '❌ Disabled',
    'mode_demo':                   '🧪 Demo',
    'mode_real':                   '💰 Real',
    'mode_testnet':                '🧪 Testnet',
    'mode_mainnet':                '🌐 Mainnet',

    # ─────────────────────────────────────────────────────────────────────────
    # Common Buttons (keyboard_helpers.py)
    # ─────────────────────────────────────────────────────────────────────────
    'btn_back':                    '⬅️ Back',
    'btn_close':                   '❌ Close',
    'btn_cancel':                  '❌ Cancel',
    'btn_confirm':                 '✅ Confirm',
    'btn_refresh':                 '🔄 Refresh',
    'btn_settings':                '⚙️ Settings',
    'btn_delete':                  '🗑️ Delete',
    'btn_yes':                     '✅ Yes',
    'btn_no':                      '❌ No',
    'btn_prev':                    '◀️ Prev',
    'btn_next':                    'Next ▶️',

    # ─────────────────────────────────────────────────────────────────────────
    # ELC Token Commands
    # ─────────────────────────────────────────────────────────────────────────
    'elc_balance_title':           '💰 <b>LYXEN Balance</b>',
    'elc_available':               'Available',
    'elc_staked':                  'Staked',
    'elc_locked':                  'Locked',
    'elc_total':                   'Total',
    'elc_value_usd':               '💵 Value: ~${value:.2f} USD',
    'btn_buy_elc':                 '🛒 Buy ELC',
    'btn_elc_history':             '📊 History',
    'btn_connect_wallet':          '🔗 Connect Wallet',
    'btn_disconnect_wallet':       '🔓 Disconnect',
    'elc_buy_title':               '🛒 <b>Buy LYXEN (ELC)</b>',
    'elc_current_price':           '💵 Current Price: <b>$1.00 USD / ELC</b>',
    'elc_platform_fee':            '🔥 Platform Fee: <b>0.5%</b>',
    'elc_purchase_hint':           '<i>Purchase ELC with USDT on TON Network</i>',
    'elc_choose_amount':           'Choose amount to buy:',
    'elc_custom_amount':           '✏️ Custom Amount',
    'elc_custom_amount_title':     '✏️ <b>Custom Amount</b>',
    'elc_custom_prompt':           'Reply with the amount of ELC you want to buy\nExample: <code>2500</code>\n\nMin: 100 ELC\nMax: 100,000 ELC',
    'elc_purchase_summary':        '🛒 <b>Purchase {amount:.2f} ELC</b>',
    'elc_cost':                    'Cost: <b>{cost:.2f} USDT</b>',
    'elc_fee_amount':              'Platform Fee: <b>{fee:.2f} USDT</b>',
    'elc_payment_link':            'Payment Link:',
    'elc_payment_hint':            '<i>Send USDT to this address on TON Network</i>',
    'btn_open_payment':            '🔗 Open Payment',
    'elc_payment_error':           '❌ Failed to create payment. Please try again.',
    'elc_balance_error':           '❌ Failed to get ELC balance. Please try again.',
    'elc_history_title':           '📊 <b>Transaction History</b>',
    'elc_no_transactions':         'No transactions yet.',
    'elc_history_error':           '❌ Failed to get transaction history. Please try again.',
    'elc_wallet_connected_title':  '🔗 <b>Connected Wallet</b>',
    'elc_wallet_address':          'Address',
    'elc_wallet_type':             'Type',
    'elc_wallet_chain':            'Chain',
    'elc_wallet_connected_at':     'Connected',
    'elc_wallet_hint':             '<i>Use this wallet to trade on HyperLiquid without exposing private keys</i>',
    'elc_connect_title':           '🔗 <b>Connect Cold Wallet</b>',
    'elc_connect_desc':            'Trade on HyperLiquid without exposing your private keys!',
    'elc_supported_wallets':       'Supported wallets:',
    'elc_wallet_metamask':         '• MetaMask (Ethereum, Polygon, BSC)',
    'elc_wallet_wc':               '• WalletConnect (Multi-chain)',
    'elc_wallet_tonkeeper':        '• Tonkeeper (TON Network)',
    'elc_keys_local':              '<i>Your keys never leave your device - all orders are signed locally</i>',
    'btn_metamask':                '🦊 MetaMask',
    'btn_walletconnect':           '🔗 WalletConnect',
    'btn_tonkeeper':               '💎 Tonkeeper',
    'elc_connect_steps_title':     '🔗 <b>Connect {wallet}</b>',
    'elc_connect_step1':           '1. Open our WebApp',
    'elc_connect_step2':           '2. Click \'Connect Wallet\'',
    'elc_connect_step3':           '3. Select {wallet}',
    'elc_connect_step4':           '4. Approve connection in wallet',
    'elc_connect_keys_hint':       '<i>Your private keys stay in your wallet - we only get your public address</i>',
    'btn_open_webapp':             '🌐 Open WebApp',
    'elc_disconnected_title':      '🔓 <b>Wallet Disconnected</b>',
    'elc_disconnected_msg':        'Your wallet has been successfully disconnected.',
    'elc_disconnected_hint':       '<i>You can reconnect anytime to resume cold wallet trading</i>',
    'elc_error_generic':           '❌ An error occurred. Please try again.',

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
    'position_item_v2':            (
        "— #{idx}: {symbol} | {side} (x{leverage}) [{strategy}]\n"
        "  • Size           : {size}\n"
        "  • Entry Price    : {avg:.8f}\n"
        "  • Mark Price     : {mark:.8f}\n"
        "  • Liquidation    : {liq}\n"
        "  • Initial Margin : {im:.2f}\n"
        "  • Maint Margin   : {mm:.2f}\n"
        "  • Take Profit    : {tp}\n"
        "  • Stop Loss      : {sl}\n"
        "  {pnl_emoji} Unreal PnL   : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'pnl_by_strategy':             '📊 *PnL by Strategy:*',
    'pnl_by_exchange':             '🏦 *PnL by Exchange:*',
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
    'indicators_header':           '📈 *Lyxen Indicators*',
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

    # Auto notifications - BLACK RHETORIC: Excitement + Authority
    'new_position': (
        '💎 *TRADE EXECUTED!*\n\n'
        '🎯 {symbol} @ {entry:.6f}\n'
        '📊 Size: {size}\n'
        '📍 {exchange} • {market_type}'
    ),
    'sl_auto_set':                 '🛡️ SL set @ {price:.6f}',
    'auto_close_position':         '⚡ Auto-close: {symbol} (TF={tf})',
    'position_closed': (
        '📊 *CLOSED* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🎯 Strategy: `{strategy}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 *Net: `{net_pnl:+.2f} USDT`*\n'
        '📍 {exchange} • {market_type}'
    ),

    # ==================== UNIFIED ENTRY TEMPLATES ====================
    # Strategy-specific entry notifications
    
    # OI - Open Interest signal
    'oi_entry': (
        '🐋 *OI* {side_emoji} *{side}*\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Entry: `{price:.6f}`\n'
        '🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)\n'
        '🎯 TP: `{tp_price:.6f}` ({tp_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '{atr_info}'
    ),
    
    # Scryptomera - Algorithm signal
    'scryptomera_entry': (
        '🔮 *SCRYPTOMERA* {side_emoji} *{side}*\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Entry: `{price:.6f}`\n'
        '🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)\n'
        '🎯 TP: `{tp_price:.6f}` ({tp_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '{atr_info}'
    ),
    
    # Scalper - Quick trade signal
    'scalper_entry': (
        '⚡ *SCALPER* {side_emoji} *{side}*\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Entry: `{price:.6f}`\n'
        '🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)\n'
        '🎯 TP: `{tp_price:.6f}` ({tp_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '{atr_info}'
    ),
    
    # Lyxen - Heatmap signal
    'elcaro_entry': (
        '🔥 *LYXEN* {side_emoji} *{side}*\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Entry: `{price:.6f}`\n'
        '🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)\n'
        '🎯 TP: `{tp_price:.6f}` ({tp_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '{atr_info}'
    ),
    
    # Fibonacci - Retracement signal
    'fibonacci_entry': (
        '📐 *FIBONACCI* {side_emoji} *{side}*\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Entry: `{price:.6f}`\n'
        '🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)\n'
        '🎯 TP: `{tp_price:.6f}` ({tp_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '{atr_info}'
    ),
    
    # RSI+BB - Technical signal
    'rsi_bb_entry': (
        '📊 *RSI+BB* {side_emoji} *{side}*\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Entry: `{price:.6f}`\n'
        '📈 RSI: `{rsi}` ({rsi_zone})\n'
        '🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}'
    ),

    # ==================== UNIFIED CLOSE TEMPLATES ====================
    # Strategy-specific close notifications
    
    'oi_closed': (
        '🐋 *OI CLOSED* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 *Net: `{net_pnl:+.2f} USDT`*\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'scryptomera_closed': (
        '🔮 *SCRYPTOMERA CLOSED* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 *Net: `{net_pnl:+.2f} USDT`*\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'scalper_closed': (
        '⚡ *SCALPER CLOSED* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 *Net: `{net_pnl:+.2f} USDT`*\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'elcaro_closed': (
        '🔥 *LYXEN CLOSED* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 *Net: `{net_pnl:+.2f} USDT`*\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'fibonacci_closed': (
        '📐 *FIBONACCI CLOSED* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 *Net: `{net_pnl:+.2f} USDT`*\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'rsi_bb_closed': (
        '📊 *RSI+BB CLOSED* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 *Net: `{net_pnl:+.2f} USDT`*\n'
        '📍 {exchange} • {market_type}'
    ),

    # Entry & error messages - technical format
    'oi_limit_entry':              '🐋 OI Limit: {symbol} {side} @ {price:.6f} qty={qty}',
    'oi_limit_error':              '❌ OI Limit failed: {msg}',
    'oi_market_entry':             '🐋 OI Market: {symbol} {side} @ {price:.6f} qty={qty}',
    'oi_market_error':             '❌ OI failed: {symbol} {side} - {msg}',
    'oi_market_ok':                '🐋 OI: {symbol} {side} @ {price:.6f} qty={qty}',

    'rsi_bb_limit_entry':          '📊 RSI+BB Limit: {symbol} {side} @ {price:.6f} qty={qty}',
    'rsi_bb_market_entry':         '📊 RSI+BB Market: {symbol} {side} @ {price:.6f} qty={qty}',
    'rsi_bb_market_ok':            '📊 RSI+BB: {symbol} {side} @ {price:.6f} RSI={rsi}',
    'rsi_bb_market_error':         '❌ RSI+BB failed: {symbol} {side} - {msg}',

    'oi_analysis':                 '🐋 OI Analysis: {symbol} {side}',

    # Scryptomera - Mystic Style
    'bitk_limit_entry':            '🔮 *Scryptomera Limit*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%\n_🌙 Spell cast. Destiny unfolds._',
    'bitk_limit_error':            '❌ Scryptomera error: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Market*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%\n_🌙 The oracle spoke. We obeyed._',
    'bitk_market_error':           '❌ Scryptomera error\n🪙 {symbol} {side}\n\n{msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}\n_🌙 Ancient signals detected._',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error - BLACK RHETORIC: Problem + Solution + Urgency
    'insufficient_balance_error':  '''🚨 <b>CAPITAL LOCKED!</b>

💰 Your {account_type} margin is tied up in positions.

<b>🧠 Smart Money Move:</b>
• Close losing positions — _cut losses fast_
• Reduce entry % — _risk management is key_
• Lower leverage — _pros use 5-10x max_

<i>The market waits for no one. Free your capital NOW.</i>

👉 /positions — <b>Take control</b>''',
    'insufficient_balance_error_extended': '''🚨 <b>ENTRY BLOCKED!</b>

📊 Strategy: <b>{strategy}</b> tried to enter
🪙 {symbol} {side}

💰 Not enough FREE margin on {account_type}.

<b>🧠 What top traders do:</b>
• Close underwater positions immediately
• Reduce position size for new entries
• Use DCA ladder for better entries

<i>Capital is your ammunition. Don't waste it.</i>''',

    # Leverage too high error
    'leverage_too_high_error':     '''⚠️ <b>LEVERAGE REJECTED!</b>

⚙️ {symbol} only allows <b>{max_leverage}x</b> maximum.

<b>💡 Pro tip:</b> Lower leverage = longer survival.
_Top traders rarely exceed 10x._

<b>Solution:</b> Adjust leverage in strategy settings.''',

    # ═══════════════════════════════════════════════════════════
    # DAILY ERROR NOTIFICATIONS (once per day per error type)
    # ═══════════════════════════════════════════════════════════
    
    # Zero balance notification (once per day)
    'daily_zero_balance':          '''⚠️ <b>BALANCE ALERT</b>

💰 Your <b>{account_type}</b> account has <b>$0</b> available.

📊 <b>Today's missed signals:</b> {missed_count}

<b>🧠 To resume trading:</b>
• Deposit funds to your {account_type} account
• Or switch to another account with balance

<i>This is a daily summary. Signals are waiting.</i>

👉 /balance — <b>Check your balance</b>''',

    # API keys invalid (once per day)
    'daily_api_keys_invalid':      '''🔑 <b>API KEYS ISSUE</b>

⚠️ Your <b>{account_type}</b> API keys are invalid or expired.

📊 <b>Missed signals today:</b> {missed_count}

<b>🔧 To fix:</b>
1. Go to Bybit → API Management
2. Create new API keys
3. Update in /api_settings

<i>Without valid keys, bot cannot trade for you.</i>''',

    # Account connection error (once per day)
    'daily_connection_error':      '''🌐 <b>CONNECTION ISSUE</b>

⚠️ Cannot connect to <b>{exchange}</b> for {account_type}.

📊 <b>Missed signals today:</b> {missed_count}

<b>Possible causes:</b>
• Exchange maintenance
• API rate limits
• Network issues

<i>Bot will retry automatically. Check exchange status.</i>''',

    # No positions possible (margin/limits)
    'daily_margin_exhausted':      '''📊 <b>MARGIN ALERT</b>

💰 Your <b>{account_type}</b> margin is fully allocated.

📊 <b>Open positions:</b> {open_count}
📊 <b>Missed signals today:</b> {missed_count}

<b>🧠 Options:</b>
• Close losing positions to free margin
• Reduce position sizes
• Increase deposit

<i>Capital efficiency is key to profits.</i>

👉 /positions — <b>Manage positions</b>''',
    
    # Position limit exceeded error (110090)
    'position_limit_error':        '''🛑 <b>POSITION LIMIT HIT!</b>

📊 <b>{strategy}</b> on {symbol}

⚠️ You've reached maximum position size.

<b>🧠 Options:</b>
• Lower leverage (recommended)
• Reduce entry % per trade
• Close other positions first

<i>Discipline is what separates winners from gamblers.</i>''',

    # Scalper - Lightning Style
    'scalper_limit_entry':         '⚡ *Scalper Limit*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%\n_⚡ Trap set. Lightning waits._',
    'scalper_limit_error':         '❌ Scalper error: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Market*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%\n_⚡ Instant strike. Maximum impact._',
    'scalper_market_error':        '❌ Scalper error\n🪙 {symbol} {side}\n\n{msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}\n_⚡ Speed is profit._',
    'feature_scalper':             'Scalper',

    # Lyxen (Heatmap) - Fire Style
    'elcaro_limit_entry':          '🔥 *Lyxen Limit*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%\n_🔥 Liquidity zone locked. Burn incoming._',
    'elcaro_limit_error':          '❌ Lyxen error: {msg}',
    'elcaro_market_entry':         '🔥 *Lyxen Market*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Lyxen: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%\n_🔥 Heatmap confirmed. We burn with precision._',
    'elcaro_market_error':         '❌ Lyxen error\n🪙 {symbol} {side}\n\n{msg}',
    'elcaro_analysis':             '🔥 Lyxen Heatmap: {side} @ {price}\n_🔥 Liquidity concentration detected._',
    'feature_elcaro':              'Lyxen',

    # Fibonacci - Mathematics Style
    'fibonacci_limit_entry':       '📐 *Fibonacci Limit*\n• {symbol} {side}\n• Price: {price:.6f}\n• Entry Zone: {entry_zone}\n• Qty: {qty}\n• SL: {sl_pct}%\n_📐 Golden level engaged. Mathematics never fails._',
    'fibonacci_limit_error':       '❌ Fibonacci error: {msg}',
    'fibonacci_market_entry':      '📐 *Fibonacci Market*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':         '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%\n_📐 Phi ratio confirmed. Perfect entry._',
    'fibonacci_market_error':      '❌ Fibonacci error\n🪙 {symbol} {side}\n\n{msg}',
    'fibonacci_analysis':          '📐 Fibonacci: {side} @ {price}\n_📐 Golden ratio aligned._',
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
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
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
    'button_toggle_atr':           '📊 ATR',
    'button_lang':                 '🌍 Lang',
    'button_set_tp':               '📈 TP %',
    'button_set_sl':               '📉 SL %',
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
    'strat_elcaro':                  '🔥 Lyxen',
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
    'stats_elcaro':                  '🔥 Lyxen',
    'stats_spot':                    '💹 Spot',
    'stats_spot_title':              'Spot DCA Statistics',
    'stats_spot_config':             'Configuration',
    'stats_spot_holdings':           'Holdings',
    'stats_spot_summary':            'Summary',
    'stats_spot_current_value':      'Current Value',
    'stats_period_all':              'All time',
    'stats_period_today':            '24h',
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

    # Lyxen AI
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
    
    # License status messages - BLACK RHETORIC: Loss Aversion + FOMO
    'no_license': '''🚨 *ACCESS DENIED*

While you're hesitating, *847 traders* are already profiting.

💸 Every minute without Lyxen = missed opportunities
⏰ Markets don't wait. Neither should you.

👉 /subscribe — _Unlock your unfair advantage NOW_''',
    'no_license_trading': '''🚨 *TRADING LOCKED*

Your competitors are making money RIGHT NOW with Lyxen.

❌ Manual trading = emotional mistakes
✅ Lyxen = cold AI precision

_Stop watching. Start earning._

👉 /subscribe — *Join 847+ smart traders*''',
    'license_required': '''🔒 *PREMIUM FEATURE*

This requires {required} subscription — _used by top 3% of traders_.

🎯 Success leaves clues. Follow the winners.

👉 /subscribe — *Upgrade now*''',
    'trial_demo_only': '''⚠️ *Demo mode is for learning, not earning.*

Real profits require real access.

🎁 You've tasted the power. Now *own* it.

👉 /subscribe — *Unlock Real Trading*''',
    'basic_strategy_limit': '''⚠️ *Basic = Basic Results*

You're limited to: {strategies}

The pros use *ALL* strategies. That's why they're pros.

👉 /subscribe — *Go Premium. Go Pro.*''',
    
    # Subscribe menu - BLACK RHETORIC: Urgency + Authority + Exclusivity  
    'subscribe_menu_header': '''💎 *UNLOCK YOUR TRADING EMPIRE*

⚡ 847+ traders already profiting
🏆 97% user satisfaction
📈 $2.4M+ generated this month''',
    'subscribe_menu_info': '''_"The best investment I ever made"_ — Premium User

Choose your level of dominance:''',
    'btn_premium': '💎 PREMIUM — Full Power ⚡',
    'btn_basic': '🥈 Basic — Starter',
    'btn_trial': '🎁 Free Trial — 7 Days',
    'btn_enter_promo': '🎟 Secret Promo Code',
    'btn_my_subscription': '📋 My Status',
    
    # Premium plan - BLACK RHETORIC: Authority + Scarcity + Social Proof
    'premium_title': '''💎 *PREMIUM — FULL DOMINATION*

_"This bot literally prints money"_ — @CryptoKing''',
    'premium_desc': '''🔥 *EVERYTHING UNLOCKED:*

✅ All 5 AI Strategies — _$100K+ trades executed daily_
✅ Real + Demo — _No limitations_
✅ Priority VIP Support — _Response < 1 hour_
✅ Dynamic ATR SL/TP — _AI-optimized entries_
✅ DCA Limit Ladder — _Institutional-grade scaling_
✅ Lifetime Updates — _Always ahead of the market_

⚡ *PREMIUM STATS:*
• Average ROI: +47%/month
• Win Rate: 78%
• Active Users: 312

_The question isn't "Can I afford Premium?"
The question is "Can I afford NOT to?"_''',
    'premium_1m': '💎 1 Month — {price} ELC ⚡',
    'premium_3m': '💎 3 Months — {price} ELC 🔥 SAVE 10%',
    'premium_6m': '💎 6 Months — {price} ELC 🎯 SAVE 20%',
    'premium_12m': '💎 12 Months — {price} ELC 🏆 BEST VALUE -30%',
    
    # Basic plan - BLACK RHETORIC: Stepping stone narrative
    'basic_title': '''🥈 *BASIC — SMART START*

_Perfect for testing the waters_''',
    'basic_desc': '''✅ Full Demo Access — _Risk-free learning_
✅ Real Account: OI, RSI+BB, Scryptomera, Scalper
⛔ Lyxen, Fibonacci, Spot — _Premium exclusive_
✅ Standard Support
✅ ATR Dynamic SL/TP

💡 *87% of Basic users upgrade to Premium within 2 weeks*
_They see the results. You will too._''',
    'basic_1m': '🥈 1 Month — {price} ELC',
    
    # Trial plan - BLACK RHETORIC: Zero risk + Taste of power
    'trial_title': '''🎁 *FREE TRIAL — ZERO RISK*

_Seeing is believing_''',
    'trial_desc': '''✅ Full Demo Access — *All 5 AI Strategies*
✅ 7 Days of Pure Power
✅ No Credit Card Required
⚡ One-Click Activation

⚠️ *WARNING:* After experiencing Lyxen AI,
manual trading will feel... primitive.

_91% of trial users become paying customers._
_Now you'll understand why._''',
    'trial_activate': '🎁 ACTIVATE FREE TRIAL ⚡',
    'trial_already_used': '''⚠️ Trial already used.

You've seen the power. Now *own* it.

👉 Choose a plan and join the elite.''',
    'trial_activated': '''🎉 *WELCOME TO THE FUTURE OF TRADING!*

⏰ You have 7 days to experience:
• AI-powered entries
• Automatic risk management
• 24/7 market monitoring

_Your journey to financial freedom starts NOW._

💡 Pro tip: Enable all strategies to maximize results!''',
    
    # Payment
    'payment_select_method': '💳 *Select Payment Method*',
    'btn_pay_elc': '◈ Pay with ELC',
    'btn_pay_ton': '💎 TON (deprecated)',
    'payment_elc_title': '◈ Payment via Lyxen Coin (ELC)',
    'payment_elc_desc': 'You will be charged {amount} ELC for {plan} ({period}).',
    'payment_ton_title': '💎 Payment via TON (Deprecated)',
    'payment_ton_desc': '''TON payments are no longer supported.
Please use ELC tokens instead.''',
    'btn_verify_ton': '✅ I Paid — Verify',
    'btn_check_again': '🔄 Check Again',
    'payment_processing': '⏳ Processing payment...',
    'payment_verifying': '⏳ Verifying payment...',
    'payment_success': '🎉 Payment successful!\n\n{plan} activated until {expires}.',
    'payment_failed': '❌ Payment failed: {error}',
    'payment_ton_not_configured': '❌ TON payments are deprecated. Use ELC tokens.',
    'payment_session_expired': '❌ Payment session expired. Please start again.',
    'payment_elc_insufficient': '''❌ Insufficient ELC balance.

Your balance: {balance} ELC
Required: {required} ELC

Top up your wallet to continue.''',
    
    # Wallet
    'wallet_title': '◈ *ELC Wallet*',
    'wallet_balance': '''💰 *Your ELC Wallet*

◈ Balance: *{balance} ELC*
📈 Staked: *{staked} ELC*
🎁 Pending Rewards: *{rewards} ELC*

💵 Total Value: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_address': '📍 Address: `{address}`',
    'wallet_btn_deposit': '📥 Deposit',
    'wallet_btn_withdraw': '📤 Withdraw',
    'wallet_btn_stake': '📈 Stake',
    'wallet_btn_unstake': '📤 Unstake',
    'wallet_btn_history': '📋 History',
    'wallet_btn_back': '« Back',
    'wallet_deposit_title': '📥 *Deposit ELC*',
    'wallet_deposit_desc': '''Send ELC tokens to your wallet address:

`{address}`

💡 *Demo mode:* Click below for free test tokens.''',
    'wallet_deposit_demo': '🎁 Get 100 ELC (Demo)',
    'wallet_deposit_success': '✅ Deposited {amount} ELC successfully!',
    'wallet_withdraw_title': '📤 *Withdraw ELC*',
    'wallet_withdraw_desc': 'Enter destination address and amount:',
    'wallet_withdraw_success': '✅ Withdrawn {amount} ELC to {address}',
    'wallet_withdraw_failed': '❌ Withdrawal failed: {error}',
    'wallet_stake_title': '📈 *Stake ELC*',
    'wallet_stake_desc': '''Stake your ELC tokens to earn *12% APY*!

💰 Available: {available} ELC
📈 Currently Staked: {staked} ELC
🎁 Pending Rewards: {rewards} ELC

Daily rewards • Instant unstaking''',
    'wallet_stake_success': '✅ Staked {amount} ELC successfully!',
    'wallet_unstake_success': '✅ Unstaked {amount} ELC + {rewards} ELC rewards!',
    'wallet_history_title': '📋 *Transaction History*',
    'wallet_history_empty': 'No transactions yet.',
    'wallet_history_item': '{type_emoji} {type}: {amount:+.2f} ELC\n   {date}',
    
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
  ELC: {total_elc} ◈

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
    'spot_freq_hourly': '⏰ Hourly',
}
