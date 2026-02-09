# -*- coding: utf-8 -*-
"""
Enliko Trading Tools — English Translations
============================================
Version: 4.0.0 | Updated: 28 January 2026

LEGAL POSITIONING:
This is an EDUCATIONAL trading toolkit providing:
- Market data visualization and analysis
- Strategy backtesting and simulation
- Portfolio tracking and performance metrics
- One-tap order execution (user-initiated)
- Risk management calculators

IMPORTANT DISCLAIMERS:
- Not financial advice
- Not automated trading (user initiates all actions)
- For educational purposes only
- Past performance does not guarantee future results
- Trading involves substantial risk of loss

All texts are written in technical, educational style
with appropriate disclaimers where needed.
"""

TEXTS = {
    # =====================================================
    # WELCOME & ONBOARDING
    # =====================================================
    
    'welcome': (
        '� <b>Enliko Trading Terminal</b>\n\n'
        '⚡ <b>&lt; 100ms</b> execution\n'
        '🛡️ <b>Risk management</b> built-in\n'
        '💎 <b>24/7</b> automated trading\n\n'
        'Bybit • HyperLiquid • Multi-Strategy'
    ),
    
    'welcome_back': (
        '🔥 <b>Enliko Trading Terminal</b>\n\n'
        '⚠️ <i>Educational platform. Not financial advice.</i>\n\n'
        '👇 Select an option:'
    ),
    
    # =====================================================
    # APP LOGIN (UNIFIED AUTH)
    # =====================================================
    
    'app_login_prompt': (
        '🔐 <b>Login to Enliko App</b>\n\n'
        'Click the button below to login to iOS or Android app.\n'
        'Link is valid for 5 minutes.\n\n'
        '⚠️ Do not share this link with anyone!'
    ),
    
    'app_login_approved': '✅ <b>Login confirmed!</b>\n\nYou can continue in the app.',
    'app_login_rejected': '❌ <b>Login rejected</b>\n\nIf this wasn\'t you, we recommend checking your security settings.',
    'app_login_expired': '⏰ Login request expired. Please try again.',
    'app_login_error': '⚠️ Processing error. Please try later.',
    
    # =====================================================
    # LEGAL DISCLAIMERS (REQUIRED)
    # =====================================================
    
    'disclaimer_trading': (
        '⚠️ *IMPORTANT DISCLAIMER*\n\n'
        'This platform provides educational tools for learning about '
        'cryptocurrency markets. It is NOT:\n'
        '• Financial advice\n'
        '• Investment recommendation\n'
        '• Guaranteed profit system\n\n'
        'Trading cryptocurrencies involves substantial risk of loss. '
        'You may lose some or all of your investment. '
        'Only trade with funds you can afford to lose.\n\n'
        'Past performance does not guarantee future results.'
    ),
    
    'disclaimer_short': '⚠️ _Educational tools only. Not financial advice. Trading involves risk._',
    
    'disclaimer_execution': (
        '⚠️ By proceeding, you acknowledge:\n'
        '• You are responsible for all trading decisions\n'
        '• This is an educational tool, not financial advice\n'
        '• You understand the risks of cryptocurrency trading\n'
        '• Past performance does not guarantee future results'
    ),
    
    # Disclaimer acceptance buttons and messages
    'disclaimer_accept_btn': '✅ I Understand & Accept',
    'disclaimer_decline_btn': '❌ I Decline',
    'disclaimer_accepted_msg': (
        '✅ *Disclaimer Accepted*\n\n'
        'You have acknowledged that:\n'
        '• This is an educational platform\n'
        '• You are responsible for all trading decisions\n'
        '• Past performance does not guarantee future results\n\n'
        'Welcome to Enliko Trading Tools!'
    ),
    'disclaimer_declined_msg': (
        '❌ *Disclaimer Declined*\n\n'
        'You must accept the disclaimer to use Enliko Trading Tools.\n\n'
        'If you change your mind, use /start to begin again.'
    ),
    
    # =====================================================
    # COMMON UI
    # =====================================================
    
    'loader': '⏳ Loading...',
    
    # =====================================================
    # MAIN MENU BUTTONS
    # =====================================================
    
    'button_portfolio': '💼 Portfolio',
    'button_balance': '💎 Portfolio',
    'button_positions': '📊 Positions',
    'button_orders': '📋 Orders',
    'button_ai_bots': '🎯 Strategies',
    'button_strategies': '🤖 AI Bots',
    'button_spot': '💹 Spot',
    'button_screener': '📈 Screener',
    'button_market': '📈 Market',
    'button_history': '📜 History',
    'button_premium': '💎 Premium',
    'button_subscribe': '👑 PREMIUM',
    'button_language': '🌍 Language',
    'button_lang': '🌍 Lang',
    'select_language': '🌍 Select your language:',
    'language_set': '✅ Language set to',
    'button_api_keys': '🔗 API Keys',
    'button_settings': '⚙️ Settings',
    'button_terminal': '💻 Terminal',
    'button_help': '❓ Help',
    'button_back': '« Back',
    'button_close': '✖️ Close',
    'button_refresh': '🔄 Refresh',
    'button_confirm': '✅ Confirm',
    'button_cancel': '❌ Cancel',
    'button_indicators': '📊 Indicators',
    'button_limit_only': '📝 Limit Only',
    'button_toggle_oi': '📊 OI',
    'button_scryptomera': '🔮 Scryptomera',
    'button_scalper': '⚡ Scalper',
    'button_elcaro': '🎯 Elcaro',
    'button_fibonacci': '📐 Fibonacci',
    'button_toggle_rsi_bb': '📈 RSI/BB',
    'button_toggle_atr': '📊 ATR',
    'button_support': '📞 Support',
    'button_coins': '🪙 Coins',
    'button_update_tpsl': '🎯 TP/SL',
    
    # Common buttons
    'btn_back': '« Back',
    'btn_close': '✖️ Close',
    'btn_cancel': '❌ Cancel',
    'btn_confirm': '✅ Confirm',
    'btn_refresh': '🔄 Refresh',
    'btn_settings': '⚙️ Settings',
    'btn_delete': '🗑 Delete',
    'btn_yes': '✅ Yes',
    'btn_no': '❌ No',
    'btn_prev': '« Prev',
    'btn_next': 'Next »',
    
    # =====================================================
    # PORTFOLIO & BALANCE
    # =====================================================
    
    'portfolio_header': '💼 *Portfolio Overview*',
    'balance_title': '💰 *Account Balance*',
    'balance_demo': '🎮 Demo Account',
    'balance_real': '💎 Live Account',
    'balance_testnet': '🧪 Testnet',
    'balance_mainnet': '🌐 Mainnet',
    'balance_equity': 'Equity',
    'balance_available': 'Available',
    'balance_margin_used': 'Used Margin',
    'balance_unrealized': 'Unrealized P/L',
    'balance_today_pnl': 'Today P/L',
    'balance_week_pnl': '7-Day P/L',
    
    'balance_empty': (
        '📊 *Account Balance*\n\n'
        '💰 No funds detected in this account.\n\n'
        '_Tip: Transfer funds to your exchange account to start tracking._'
    ),
    
    'balance_error': '❌ Unable to fetch balance. Check API configuration.',
    
    # Balance display format
    'balance_display': (
        '💰 *{account_type} Balance*\n\n'
        '💵 Equity: `{equity:.2f} USDT`\n'
        '🔓 Available: `{available:.2f} USDT`\n'
        '🔒 Margin: `{margin:.2f} USDT`\n\n'
        '📊 Unrealized: `{unrealized:+.2f} USDT`\n'
        '📈 Today: `{today_pnl:+.2f} USDT`\n'
        '📆 Week: `{week_pnl:+.2f} USDT`\n\n'
        '_{disclaimer}_'
    ),
    
    # =====================================================
    # POSITIONS
    # =====================================================
    
    'positions_header': '📊 *Open Positions*',
    'positions_empty': '📭 No open positions.',
    'positions_page': 'Page {current}/{total}',
    
    'position_card': (
        '{side_emoji} *{symbol}*\n'
        '├ Side: `{side}`\n'
        '├ Entry: `{entry:.6f}`\n'
        '├ Size: `{size}`\n'
        '├ Leverage: `{leverage}x`\n'
        '├ Mark: `{mark:.6f}`\n'
        '├ P/L: `{pnl:+.2f} USDT ({pnl_pct:+.2f}%)`\n'
        '└ Strategy: `{strategy}`'
    ),
    
    'position_long': '🟢 LONG',
    'position_short': '🔴 SHORT',
    
    'btn_close_pos': '❌ Close',
    'btn_modify_tpsl': '⚙️ TP/SL',
    
    'close_position_confirm': (
        '⚠️ *Close Position?*\n\n'
        '📊 {symbol} {side}\n'
        '💰 P/L: {pnl:+.2f} USDT ({pnl_pct:+.2f}%)\n\n'
        '_This action cannot be undone._'
    ),
    
    'position_closed_success': '✅ Position {symbol} closed.',
    'position_close_error': '❌ Error closing position: {error}',
    
    # =====================================================
    # ORDERS
    # =====================================================
    
    'orders_header': '📋 *Open Orders*',
    'orders_empty': '📭 No open orders.',
    'orders_pending': '⏳ Pending Limit Orders',
    
    'order_card': (
        '📋 *{symbol}*\n'
        '├ Type: `{order_type}`\n'
        '├ Side: `{side}`\n'
        '├ Price: `{price:.6f}`\n'
        '├ Qty: `{qty}`\n'
        '└ Status: `{status}`'
    ),
    
    'btn_cancel_order': '❌ Cancel Order',
    'btn_cancel_all': '❌ Cancel All',
    
    'order_cancelled': '✅ Order cancelled.',
    'orders_cancelled_all': '✅ All orders cancelled.',
    
    # =====================================================
    # API CONFIGURATION
    # =====================================================
    
    'api_settings_header': '🔗 *Exchange API Configuration*',
    'api_settings_info': (
        'Connect your exchange API keys to enable portfolio tracking.\n\n'
        '⚠️ _Only read & trade permissions needed. Withdrawal NOT required._'
    ),
    
    'api_bybit_demo': '🎮 Bybit Demo',
    'api_bybit_real': '💎 Bybit Live',
    'api_hl_testnet': '🧪 HyperLiquid Testnet',
    'api_hl_mainnet': '🌐 HyperLiquid Mainnet',
    
    'api_key_set': '✅ Configured',
    'api_key_missing': '❌ Not configured',
    
    'enter_api': 'Enter your API Key:',
    'api_saved': '✅ API Key saved.',
    'enter_secret': 'Enter your API Secret:',
    'secret_saved': '✅ API Secret saved.',
    
    'api_test_success': '✅ API connection successful!',
    'api_test_failed': '❌ API connection failed: {error}',
    
    'api_missing_credentials': '❌ API credentials not configured.',
    'api_missing_notice': (
        '⚠️ Exchange API keys are not configured.\n\n'
        'Add your API Key and Secret in settings to enable:\n'
        '• Portfolio tracking\n'
        '• Position monitoring\n'
        '• Order execution\n\n'
        '👉 Go to 🔗 API Keys'
    ),
    
    # =====================================================
    # STRATEGY TEMPLATES
    # =====================================================
    
    'button_strategy_settings': '🎯 Strategies',
    'strategy_settings_header': '⚙️ *Strategy Configuration*',
    'strategy_invalid': '❌ Invalid strategy',
    
    'strategy_info': (
        '📊 *Strategy Templates*\n\n'
        'Configure parameters for market analysis:\n'
        '• Entry % — Position size calculator\n'
        '• Stop-Loss % — Risk limit\n'
        '• Take-Profit % — Target level\n'
        '• ATR Settings — Volatility-based levels\n\n'
        '⚠️ _These are educational tools for strategy testing._\n'
        '_Not financial advice._'
    ),
    
    'strat_oi': '🔀 Open Interest',
    'strat_rsi_bb': '📊 RSI + Bollinger',
    'strat_scryptomera': '🔮 Scryptomera',
    'strat_scalper': '⚡ Scalper',
    'strat_elcaro': '🔥 Enliko',
    'strat_fibonacci': '📐 Fibonacci',
    
    'using_global': 'Using global settings',
    'global_default': 'Global',
    
    # Strategy parameters
    'param_percent': '📊 Entry %',
    'param_sl': '🔻 Stop-Loss %',
    'param_tp': '🔺 Take-Profit %',
    'param_leverage': '⚡ Leverage',
    'param_reset': '🔄 Reset to Global',
    'param_direction': '🎯 Direction',
    'param_long_settings': '📈 LONG Settings',
    'param_short_settings': '📉 SHORT Settings',
    
    'dir_all': '🔄 ALL (LONG + SHORT)',
    'dir_long_only': '📈 LONG only',
    'dir_short_only': '📉 SHORT only',
    
    'prompt_entry_pct': 'Enter Entry % (position size):',
    'prompt_sl_pct': 'Enter Stop-Loss %:',
    'prompt_tp_pct': 'Enter Take-Profit %:',
    'prompt_leverage': 'Enter Leverage (1-100):',
    
    'strat_setting_saved': '✅ {name} {param} set to {value}',
    'settings_reset': '✅ Settings reset to global defaults.',
    'invalid_number': '❌ Invalid number. Enter a value between 0 and 100.',
    
    # Global settings (DEPRECATED)
    'global_settings': '🌐 Global Settings',
    'global_settings_header': '🌐 *Global Configuration*',
    'global_settings_info': 'Default parameters used when strategy-specific settings are not configured.',
    'global_settings_removed': '⚠️ *Global Settings Removed*\n\nPlease use per-strategy Long/Short settings instead.\n\nEach strategy now has its own Entry%, SL%, TP%, ATR settings.',
    
    # ATR settings
    'param_atr_periods': '📈 ATR Periods',
    'param_atr_mult': '📉 ATR Multiplier',
    'param_atr_trigger': '🎯 ATR Trigger %',
    'prompt_atr_periods': 'Enter ATR Periods (e.g., 7):',
    'prompt_atr_mult': 'Enter ATR Multiplier (e.g., 1.0):',
    'prompt_atr_trigger': 'Enter ATR Trigger % (e.g., 2.0):',
    
    # Break-Even settings
    'be_settings_header': '🔒 *Break-Even Configuration*',
    'be_settings_desc': '_Move stop-loss to entry when profit reaches trigger %_',
    'be_enabled_label': '🔒 Break-Even',
    'be_trigger_label': '🎯 BE Trigger %',
    'prompt_be_trigger': 'Enter Break-Even Trigger % (e.g., 1.0):',
    'prompt_long_be_trigger': '📈 LONG BE Trigger %\n\nEnter profit % to move SL to entry:',
    'prompt_short_be_trigger': '📉 SHORT BE Trigger %\n\nEnter profit % to move SL to entry:',
    'param_be_trigger': '🎯 BE Trigger %',
    'be_moved_to_entry': '🔒 {symbol}: Stop-loss moved to entry @ {entry}',
    'be_status_enabled': '✅ BE: {trigger}%',
    'be_status_disabled': '❌ BE: Off',
    
    # ATR Disabled - Restore SL/TP
    'atr_disabled_restored': '🔄 <b>ATR Disabled</b>\n\n📊 {symbol}\n🛡️ SL restored: {sl_price:.4f}\n🎯 TP restored: {tp_price:.4f}',
    
    # Partial Take Profit
    'partial_tp_label': '✂️ Partial TP',
    'partial_tp_status_enabled': '✅ Partial TP enabled',
    'partial_tp_status_disabled': '❌ Partial TP disabled',
    'partial_tp_step1_menu': '✂️ *Partial TP - Step 1*\n\nClose {close}% of position at +{trigger}% profit\n\n_Select parameter:_',
    'partial_tp_step2_menu': '✂️ *Partial TP - Step 2*\n\nClose {close}% of position at +{trigger}% profit\n\n_Select parameter:_',
    'trigger_pct': 'Trigger',
    'close_pct': 'Close',
    'prompt_long_ptp_1_trigger': '📈 LONG Step 1: Trigger %\n\nEnter profit % to close first part:',
    'prompt_long_ptp_1_close': '📈 LONG Step 1: Close %\n\nEnter % of position to close:',
    'prompt_long_ptp_2_trigger': '📈 LONG Step 2: Trigger %\n\nEnter profit % to close second part:',
    'prompt_long_ptp_2_close': '📈 LONG Step 2: Close %\n\nEnter % of position to close:',
    'prompt_short_ptp_1_trigger': '📉 SHORT Step 1: Trigger %\n\nEnter profit % to close first part:',
    'prompt_short_ptp_1_close': '📉 SHORT Step 1: Close %\n\nEnter % of position to close:',
    'prompt_short_ptp_2_trigger': '📉 SHORT Step 2: Trigger %\n\nEnter profit % to close second part:',
    'prompt_short_ptp_2_close': '📉 SHORT Step 2: Close %\n\nEnter % of position to close:',
    'partial_tp_executed': '✂️ {symbol}: Closed {close}% at +{trigger}% profit',
    'partial_tp_notification': '✂️ <b>Partial TP Step {step}</b>\n\n📊 {symbol}\n📉 Closed: {close_pct:.0f}% ({close_qty})\n📈 Profit: +{profit_pct:.2f}%\n💰 PnL: ~${pnl:.2f}',
    
    # DCA settings
    'dca_settings': '⚙️ DCA Settings',
    'dca_settings_header': '⚙️ *DCA Configuration*\n\n',
    'dca_toggle': 'DCA Enabled',
    'dca_status': 'Status',
    'dca_description': '_Dollar Cost Averaging: Add to position on drawdown._',
    'dca_leg1': '📉 DCA Level 1 %',
    'dca_leg2': '📉 DCA Level 2 %',
    'prompt_dca_leg1': 'Enter DCA Level 1 % (e.g., 10):',
    'prompt_dca_leg2': 'Enter DCA Level 2 % (e.g., 25):',
    'dca_setting_saved': '✅ DCA {leg} set to {value}%',
    
    # Coin groups
    'param_coins_group': '🪙 Coins',
    'select_coin_group': 'Select coin group:',
    'select_coins_for_strategy': '🪙 *Select coins for {name}*',
    'group_all': 'ALL',
    'group_top': 'TOP',
    'group_top100': 'TOP',
    'group_volatile': 'VOLATILE',
    'group_global': '📊 Global',
    'group_set': '✅ Coin group set: {group}',
    
    # Order type
    'param_order_type': '📤 Order Type',
    'order_type_market': '⚡ Market',
    'order_type_limit': '🎯 Limit',
    
    # =====================================================
    # TRADING EXECUTION
    # =====================================================
    
    'execution_header': '📊 *Order Execution*',
    
    'execution_confirm': (
        '⚠️ *Confirm Execution*\n\n'
        '📊 {symbol} {side}\n'
        '💰 Size: {size} USDT\n'
        '⚡ Leverage: {leverage}x\n'
        '🔻 SL: {sl_pct}%\n'
        '🔺 TP: {tp_pct}%\n\n'
        '⚠️ _Trading involves risk of loss._\n'
        '_You are responsible for this decision._'
    ),
    
    'execution_success': (
        '✅ *Order Executed*\n\n'
        '📊 {symbol} {side}\n'
        '💰 Entry: {entry:.6f}\n'
        '📦 Size: {size}\n'
        '⚡ Leverage: {leverage}x\n\n'
        '🔻 SL: {sl_price:.6f}\n'
        '🔺 TP: {tp_price:.6f}'
    ),
    
    'execution_failed': '❌ Order failed: {error}',
    
    # Position notifications
    'new_position': (
        '📊 *Position Opened*\n\n'
        '🎯 {symbol} @ {entry:.6f}\n'
        '📦 Size: {size}\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'position_closed': (
        '📊 *Position Closed*\n\n'
        '📌 {symbol}\n'
        '🏷️ Strategy: `{strategy}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 P/L: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 Net: `{net_pnl:+.2f} USDT`\n'
        '📍 {exchange} • {market_type}\n\n'
        '_⚠️ Past performance ≠ future results_'
    ),
    
    # =====================================================
    # MARKET ANALYSIS SIGNALS
    # =====================================================
    
    # Signal templates - Educational format
    'signal_header': '📊 *Market Analysis*',
    
    # OI Analysis
    'oi_entry': (
        '🐋 *Open Interest Analysis* {side_emoji} {side}\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Level: `{price:.6f}`\n'
        '🛡️ Risk: `{sl_price:.6f}` ({sl_pct:.2f}%)\n'
        '🎯 Target: `{tp_price:.6f}` ({tp_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '{atr_info}\n'
        '_⚠️ Educational analysis only_'
    ),
    
    # Scryptomera Analysis
    'scryptomera_entry': (
        '🔮 *Scryptomera Analysis* {side_emoji} {side}\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Level: `{price:.6f}`\n'
        '🛡️ Risk: `{sl_price:.6f}` ({sl_pct:.2f}%)\n'
        '🎯 Target: `{tp_price:.6f}` ({tp_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '{atr_info}\n'
        '_⚠️ Educational analysis only_'
    ),
    
    # Scalper Analysis
    'scalper_entry': (
        '⚡ *Scalper Analysis* {side_emoji} {side}\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Level: `{price:.6f}`\n'
        '🛡️ Risk: `{sl_price:.6f}` ({sl_pct:.2f}%)\n'
        '🎯 Target: `{tp_price:.6f}` ({tp_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '{atr_info}\n'
        '_⚠️ Educational analysis only_'
    ),
    
    # Enliko Analysis
    'elcaro_entry': (
        '🔥 *Enliko Analysis* {side_emoji} {side}\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Level: `{price:.6f}`\n'
        '🛡️ Risk: `{sl_price:.6f}` ({sl_pct:.2f}%)\n'
        '🎯 Target: `{tp_price:.6f}` ({tp_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '{atr_info}\n'
        '_⚠️ Educational analysis only_'
    ),
    
    # Fibonacci Analysis
    'fibonacci_entry': (
        '📐 *Fibonacci Analysis* {side_emoji} {side}\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Level: `{price:.6f}`\n'
        '🛡️ Risk: `{sl_price:.6f}` ({sl_pct:.2f}%)\n'
        '🎯 Target: `{tp_price:.6f}` ({tp_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '{atr_info}\n'
        '_⚠️ Educational analysis only_'
    ),
    
    # RSI+BB Analysis
    'rsi_bb_entry': (
        '📊 *RSI + Bollinger Analysis* {side_emoji} {side}\n'
        '────────────────\n'
        '🪙 `{symbol}`\n'
        '💰 Level: `{price:.6f}`\n'
        '📈 RSI: `{rsi}` ({rsi_zone})\n'
        '🛡️ Risk: `{sl_price:.6f}` ({sl_pct:.2f}%)\n\n'
        '*Accounts:*\n{accounts}\n'
        '_⚠️ Educational analysis only_'
    ),
    
    # Closed positions by strategy
    'oi_closed': (
        '🐋 *OI Position Closed* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 P/L: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 Net: `{net_pnl:+.2f} USDT`\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'scryptomera_closed': (
        '🔮 *Scryptomera Closed* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 P/L: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 Net: `{net_pnl:+.2f} USDT`\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'scalper_closed': (
        '⚡ *Scalper Closed* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 P/L: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 Net: `{net_pnl:+.2f} USDT`\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'elcaro_closed': (
        '🔥 *Enliko Closed* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 P/L: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 Net: `{net_pnl:+.2f} USDT`\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'fibonacci_closed': (
        '📐 *Fibonacci Closed* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 P/L: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 Net: `{net_pnl:+.2f} USDT`\n'
        '📍 {exchange} • {market_type}'
    ),
    
    'rsi_bb_closed': (
        '📊 *RSI+BB Closed* `{symbol}`\n\n'
        '📌 Reason: `{reason}`\n'
        '🟢 Entry: `{entry:.8f}`\n'
        '🔴 Exit: `{exit:.8f}`\n'
        '💰 P/L: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '💸 Fee: `{fee:.4f} USDT`\n'
        '💵 Net: `{net_pnl:+.2f} USDT`\n'
        '📍 {exchange} • {market_type}'
    ),
    
    # Technical entry logs
    'oi_limit_entry': '🐋 OI Limit: {symbol} {side} @ {price:.6f} qty={qty}',
    'oi_limit_error': '❌ OI Limit failed: {msg}',
    'oi_market_entry': '🐋 OI Market: {symbol} {side} @ {price:.6f} qty={qty}',
    'oi_market_error': '❌ OI failed: {symbol} {side} - {msg}',
    'oi_market_ok': '🐋 OI: {symbol} {side} @ {price:.6f} qty={qty}',
    
    'rsi_bb_limit_entry': '📊 RSI+BB Limit: {symbol} {side} @ {price:.6f} qty={qty}',
    'rsi_bb_market_entry': '📊 RSI+BB Market: {symbol} {side} @ {price:.6f} qty={qty}',
    'rsi_bb_market_ok': '📊 RSI+BB: {symbol} {side} @ {price:.6f} RSI={rsi}',
    'rsi_bb_market_error': '❌ RSI+BB failed: {symbol} {side} - {msg}',
    
    'oi_analysis': '🐋 OI Analysis: {symbol} {side}',
    
    # Scryptomera
    'bitk_limit_entry': '🔮 *Scryptomera Limit*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error': '❌ Scryptomera error: {msg}',
    'bitk_market_entry': '🔮 *Scryptomera Market*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok': '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error': '❌ Scryptomera error\n🪙 {symbol} {side}\n\n{msg}',
    'bitk_analysis': '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera': 'Scryptomera',
    
    # Scalper
    'scalper_limit_entry': '⚡ *Scalper Limit*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error': '❌ Scalper error: {msg}',
    'scalper_market_entry': '⚡ *Scalper Market*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok': '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error': '❌ Scalper error\n🪙 {symbol} {side}\n\n{msg}',
    'scalper_analysis': '⚡ Scalper: {side} @ {price}',
    'feature_scalper': 'Scalper',
    
    # Enliko
    'elcaro_limit_entry': '🔥 *Enliko Limit*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error': '❌ Enliko error: {msg}',
    'elcaro_market_entry': '🔥 *Enliko Market*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok': '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error': '❌ Enliko error\n🪙 {symbol} {side}\n\n{msg}',
    'elcaro_analysis': '🔥 Enliko: {side} @ {price}',
    'feature_elcaro': 'Enliko',
    
    # Fibonacci
    'fibonacci_limit_entry': '📐 *Fibonacci Limit*\n• {symbol} {side}\n• Price: {price:.6f}\n• Entry Zone: {entry_zone}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error': '❌ Fibonacci error: {msg}',
    'fibonacci_market_entry': '📐 *Fibonacci Market*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok': '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error': '❌ Fibonacci error\n🪙 {symbol} {side}\n\n{msg}',
    'fibonacci_analysis': '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci': 'Fibonacci',
    'stats_fibonacci': '📐 Fibonacci',
    
    # =====================================================
    # ERRORS & NOTIFICATIONS
    # =====================================================
    
    # Balance errors - Educational tone
    'insufficient_balance_error': (
        '⚠️ <b>Insufficient Margin</b>\n\n'
        '💰 Your {account_type} account margin is fully allocated.\n\n'
        '<b>Options:</b>\n'
        '• Close existing positions to free margin\n'
        '• Reduce position size (Entry %)\n'
        '• Lower leverage setting\n\n'
        '<i>Risk management is essential in trading.</i>\n\n'
        '👉 /positions — Manage positions'
    ),
    
    'insufficient_balance_error_extended': (
        '⚠️ <b>Order Not Placed</b>\n\n'
        '📊 Strategy: <b>{strategy}</b>\n'
        '🪙 {symbol} {side}\n\n'
        '💰 Insufficient free margin on {account_type}.\n\n'
        '<b>Suggestions:</b>\n'
        '• Review open positions\n'
        '• Adjust position sizing\n'
        '• Consider risk-reward ratio\n\n'
        '<i>Proper capital allocation is key.</i>'
    ),
    
    'leverage_too_high_error': (
        '⚠️ <b>Leverage Limit</b>\n\n'
        '⚙️ {symbol} maximum leverage is <b>{max_leverage}x</b>.\n\n'
        '<b>Note:</b> Lower leverage reduces liquidation risk.\n'
        'Adjust leverage in strategy settings.'
    ),
    
    'position_limit_error': (
        '⚠️ <b>Position Limit Reached</b>\n\n'
        '📊 <b>{strategy}</b> on {symbol}\n\n'
        'Maximum position size limit reached.\n\n'
        '<b>Options:</b>\n'
        '• Lower leverage\n'
        '• Reduce entry %\n'
        '• Close other positions'
    ),
    
    # Daily notifications
    'daily_zero_balance': (
        '⚠️ <b>Balance Notice</b>\n\n'
        '💰 Your <b>{account_type}</b> account shows <b>$0</b> available.\n\n'
        '<b>To enable tracking:</b>\n'
        '• Deposit funds to your exchange account\n'
        '• Or switch to another configured account\n\n'
        '👉 /balance — Check your balance'
    ),
    
    'daily_api_keys_invalid': (
        '🔑 <b>API Configuration Issue</b>\n\n'
        '⚠️ Your <b>{account_type}</b> API keys appear invalid.\n\n'
        '<b>To resolve:</b>\n'
        '1. Check API key status on exchange\n'
        '2. Create new API keys if needed\n'
        '3. Update in /api_settings\n\n'
        '<i>Valid API keys are required for portfolio tracking.</i>'
    ),
    
    'daily_connection_error': (
        '🌐 <b>Connection Notice</b>\n\n'
        '⚠️ Unable to connect to <b>{exchange}</b> for {account_type}.\n\n'
        '<b>Possible causes:</b>\n'
        '• Exchange maintenance\n'
        '• API rate limits\n'
        '• Network issues\n\n'
        '<i>Connection will be retried automatically.</i>'
    ),
    
    'daily_margin_exhausted': (
        '📊 <b>Margin Notice</b>\n\n'
        '💰 Your <b>{account_type}</b> margin is fully allocated.\n\n'
        '📊 Open positions: {open_count}\n\n'
        '<b>Options:</b>\n'
        '• Close positions to free margin\n'
        '• Reduce position sizes\n'
        '• Increase account balance\n\n'
        '👉 /positions — Manage positions'
    ),
    
    # API errors
    'bybit_invalid_response': '❌ Exchange returned invalid response.',
    'bybit_error': '❌ Exchange error {path}: {data}',
    
    # SL/TP notifications
    'sl_auto_set': '🛡️ Stop-loss set @ {price:.6f}',
    'auto_close_position': '⚡ Auto-close: {symbol} (TF={tf})',
    'limit_order_filled': '✅ Limit order for {symbol} filled @ {price}',
    'limit_order_cancelled': '⚠️ Limit order for {symbol} cancelled.',
    'sl_tp_set': '✅ {symbol}: SL @ {sl_price}{tp_part}',
    'sl_set_only': '✅ {symbol}: SL @ {sl_price}',
    'sl_tp_initialized': '✅ {symbol}: SL/TP initialized @ {sl}/{tp}',
    'sl_breakeven': '🔄 {symbol}: SL moved to breakeven @ {entry}',
    'sl_tp_updated': '✏️ {symbol}: SL/TP updated to {sl}/{tp}',
    'fixed_sl_tp': '✅ {symbol}: SL @ {sl}, TP @ {tp}',
    'tp_part': ', TP @ {tp_price}',
    'sl_set': '🛑 SL={price:.6f}',
    
    # =====================================================
    # TRADING STATISTICS
    # =====================================================
    
    'button_stats': '📊 Statistics',
    'stats_title': 'Performance Metrics',
    'stats_strategy': 'Strategy',
    'stats_period': 'Period',
    'stats_overview': 'Overview',
    'stats_total_trades': 'Total Trades',
    'stats_closed': 'Closed',
    'stats_open': 'Open',
    'stats_results': 'Results',
    'stats_winrate': 'Win Rate',
    'stats_total_r': 'Total R',
    'stats_avg_r': 'Avg R',
    'stats_by_direction': 'By Direction',
    'stats_long': 'Long',
    'stats_short': 'Short',
    'stats_pnl': 'Profit/Loss',
    'stats_gross_profit': 'Gross Profit',
    'stats_gross_loss': 'Gross Loss',
    'stats_total_pnl': 'Total P/L',
    'stats_realized_pnl': 'Realized',
    'stats_unrealized_pnl': 'Unrealized',
    'stats_combined_pnl': 'Combined',
    'stats_profit_factor': 'Profit Factor',
    'stats_strategy_settings': 'Strategy Settings',
    'settings_entry_pct': 'Entry',
    'settings_leverage': 'Leverage',
    'settings_trading_mode': 'Mode',
    'settings_direction': 'Direction',
    
    'stats_all': '📈 All',
    'stats_oi': '📉 OI',
    'stats_rsi_bb': '📊 RSI+BB',
    'stats_scryptomera': '🔮 Scryptomera',
    'stats_scalper': '⚡ Scalper',
    'stats_elcaro': '🔥 Enliko',
    'stats_spot': '💹 Spot',
    'stats_spot_title': 'Spot Metrics',
    'stats_spot_config': 'Configuration',
    'stats_spot_holdings': 'Holdings',
    'stats_spot_summary': 'Summary',
    'stats_spot_current_value': 'Current Value',
    'stats_period_all': 'All time',
    'stats_period_today': '24h',
    'stats_period_week': 'Week',
    'stats_period_month': 'Month',
    'stats_demo': '🎮 Demo',
    'stats_real': '💎 Live',
    'stats_testnet': '🧪 Testnet',
    'stats_mainnet': '🌐 Mainnet',
    
    'stats_disclaimer': '⚠️ _Past performance does not guarantee future results._',
    
    # Trade list
    'trades_title': 'Trade History',
    'trades_list_btn': 'Trade List',
    'trades_page': 'Page',
    'trades_total': 'trades',
    'trades_empty': 'No trades found for this filter.',
    'trades_to_stats': 'Statistics',
    
    # =====================================================
    # SUBSCRIPTION & PREMIUM
    # =====================================================
    
    # No aggressive marketing - Educational framing
    'no_license': (
        '📊 *Premium Features*\n\n'
        'Unlock additional educational tools:\n'
        '• Advanced strategy templates\n'
        '• Extended analytics\n'
        '• Priority support\n\n'
        '👉 /subscribe — View plans'
    ),
    
    'no_license_trading': (
        '📊 *Feature Requires Premium*\n\n'
        'This educational tool requires a subscription.\n\n'
        '👉 /subscribe — View plans'
    ),
    
    'license_required': (
        '🔒 *Premium Feature*\n\n'
        'This requires {required} subscription.\n\n'
        '👉 /subscribe — Upgrade'
    ),
    
    'trial_demo_only': (
        '⚠️ *Trial Limitation*\n\n'
        'Trial access is limited to demo trading only.\n\n'
        '👉 /subscribe — Unlock real trading'
    ),
    
    'basic_strategy_limit': (
        '⚠️ *Basic Plan Limitation*\n\n'
        'Basic plan includes only: OI, RSI+BB\n\n'
        '👉 /subscribe — Upgrade to Premium'
    ),
    
    'basic_bybit_only': (
        '⚠️ *Basic Plan Limitation*\n\n'
        'Basic plan supports Bybit only.\n'
        'HyperLiquid is available on Premium.\n\n'
        '👉 /subscribe — Upgrade to Premium'
    ),
    
    # Subscribe menu - Professional, no hype
    'subscribe_menu_header': (
        '💎 *Enliko Premium*\n\n'
        'Choose your subscription level:'
    ),
    
    'subscribe_menu_info': '_Select a plan to continue:_',
    
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic',
    'btn_trial': '🎁 Free Trial',
    'btn_enter_promo': '🎟 Promo Code',
    'btn_my_subscription': '📋 My Subscription',
    
    # Premium plan - Professional description
    'premium_title': '💎 *Premium Plan*',
    'premium_desc': (
        '*Features included:*\n\n'
        '✅ All strategy templates\n'
        '✅ Demo & Live environments\n'
        '✅ Priority support\n'
        '✅ ATR-based risk management\n'
        '✅ DCA configuration\n'
        '✅ All platform updates\n\n'
        '⚠️ _Trading involves risk. Not financial advice._'
    ),
    
    'premium_1m': '💎 1 Month — {price} ELC',
    'premium_3m': '💎 3 Months — {price} ELC',
    'premium_6m': '💎 6 Months — {price} ELC',
    'premium_12m': '💎 12 Months — {price} ELC',
    
    # Basic plan
    'basic_title': '🥈 *Basic Plan*',
    'basic_desc': (
        '*Features included:*\n\n'
        '✅ Demo + Real trading\n'
        '✅ Strategies: OI, RSI+BB\n'
        '✅ Bybit only\n'
        '✅ ATR-based risk management\n\n'
        '⛔ Other strategies — Premium only\n'
        '⛔ HyperLiquid — Premium only\n\n'
        '⚠️ _Trading involves risk. Not financial advice._'
    ),
    
    'basic_1m': '🥈 1 Month — {price} ELC',
    
    # Trial plan
    'trial_title': '🎁 *Free Trial — 14 Days*',
    'trial_desc': (
        '*Try before you subscribe:*\n\n'
        '✅ Full Demo access\n'
        '✅ All strategy templates\n'
        '✅ 14 days duration\n'
        '✅ No payment required\n\n'
        '⛔ Real trading not available\n\n'
        '⚠️ _Educational tools only. Not financial advice._'
    ),
    
    'trial_activate': '🎁 Activate Trial',
    'trial_already_used': '⚠️ Trial already used. Choose a paid plan.',
    'trial_activated': (
        '🎉 *Trial Activated!*\n\n'
        '⏰ You have 14 days of access.\n\n'
        'Explore all educational features in demo mode.\n\n'
        '⚠️ _Remember: Trading involves risk._'
    ),
    
    # Payment
    'payment_select_method': '💳 *Select Payment Method*',
    'btn_pay_elc': '◈ Pay with ELC',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': '◈ Payment via ELC Token',
    'payment_elc_desc': 'Amount: {amount} ELC for {plan} ({period}).',
    'payment_ton_title': '💎 Payment via TON',
    'payment_ton_desc': 'TON payments are currently unavailable.',
    'btn_verify_ton': '✅ Verify Payment',
    'btn_check_again': '🔄 Check Again',
    'payment_processing': '⏳ Processing...',
    'payment_verifying': '⏳ Verifying...',
    'payment_success': '🎉 Payment successful!\n\n{plan} activated until {expires}.',
    'payment_failed': '❌ Payment failed: {error}',
    'payment_ton_not_configured': '❌ TON payments unavailable.',
    'payment_session_expired': '❌ Session expired. Please try again.',
    'payment_elc_insufficient': (
        '❌ Insufficient ELC balance.\n\n'
        'Your balance: {balance} ELC\n'
        'Required: {required} ELC'
    ),
    
    # Crypto Payments (OxaPay)
    'crypto_select_currency': (
        '💳 *Crypto Payment*\n\n'
        '📦 *Plan:* {plan}\n'
        '⏰ *Duration:* {duration}\n'
        '💰 *Price:* ${price:.2f} USD\n\n'
        'Select payment currency:'
    ),
    'crypto_payment_invoice': (
        '💳 *Crypto Payment Invoice*\n\n'
        '📦 *Plan:* {plan}\n'
        '⏰ *Duration:* {duration}\n'
        '💰 *Amount:* {amount}\n'
        '🔗 *Network:* {network}\n\n'
        '📋 *Payment Address:*\n'
        '`{address}`\n\n'
        '⏱ *Expires in:* 60 minutes\n\n'
        '⚠️ Send exact amount to this address.\n'
        'After payment, click Check to verify.\n\n'
        '🚫 *All cryptocurrency payments are final and non-refundable.*'
    ),
    'creating_payment': '⏳ Creating payment invoice...',
    'payment_creation_failed': '❌ Failed to create payment. Please try again.',
    'payment_error': '❌ Payment service error. Please try again later.\n\nError: {error}',
    'invalid_plan': 'Invalid plan or duration',
    'btn_check_payment': '✅ Check Payment',
    'btn_copy_address': '📋 Copy Address',
    'btn_new_currency': '🔄 Different Currency',
    'btn_retry': '🔄 Retry',
    'crypto_creating_invoice': '⏳ Creating payment invoice...',
    'crypto_payment_instructions': (
        '💳 *Crypto Payment*\n\n'
        '📦 *Plan:* {plan}\n'
        '⏰ *Period:* {period}\n'
        '💰 *Amount:* {amount_crypto:.6f} {currency}\n'
        '📍 *Network:* {network}\n\n'
        '📋 *Send exactly this amount to:*\n'
        '`{address}`\n\n'
        '⚠️ *Important:*\n'
        '• Send EXACTLY the amount shown\n'
        '• Use the correct network ({network})\n'
        '• Payment expires in 30 minutes\n\n'
        '🆔 Payment ID: `{payment_id}`'
    ),
    'crypto_payment_error': '❌ Failed to create payment: {error}',
    'checking_payment': 'Checking payment status...',
    'crypto_payment_confirmed': (
        '✅ *Payment Confirmed!*\n\n'
        'Your subscription has been activated.\n'
        'Thank you for using Enliko!'
    ),
    'crypto_payment_confirming': '⏳ Payment detected, waiting for confirmations...',
    'crypto_payment_expired': '❌ Payment expired. Please create a new payment.',
    'crypto_payment_pending': '⏳ Payment not yet received. Please complete the transfer.',
    
    # =====================================================
    # WALLET
    # =====================================================
    
    'wallet_title': '◈ *ELC Wallet*',
    'wallet_balance': (
        '💰 *Your ELC Balance*\n\n'
        '◈ Available: *{balance} ELC*\n'
        '📈 Staked: *{staked} ELC*\n'
        '🎁 Rewards: *{rewards} ELC*\n\n'
        '💵 Value: *${total_usd}*'
    ),
    
    'wallet_address': '📍 Address: `{address}`',
    'wallet_btn_deposit': '📥 Deposit',
    'wallet_btn_withdraw': '📤 Withdraw',
    'wallet_btn_stake': '📈 Stake',
    'wallet_btn_unstake': '📤 Unstake',
    'wallet_btn_history': '📋 History',
    'wallet_btn_back': '« Back',
    
    'wallet_deposit_title': '📥 *Deposit ELC*',
    'wallet_deposit_desc': 'Send ELC tokens to:\n\n`{address}`',
    'wallet_deposit_demo': '🎁 Get 100 ELC (Demo)',
    'wallet_deposit_success': '✅ Deposited {amount} ELC.',
    
    'wallet_withdraw_title': '📤 *Withdraw ELC*',
    'wallet_withdraw_desc': 'Enter destination address and amount:',
    'wallet_withdraw_success': '✅ Withdrawn {amount} ELC to {address}',
    'wallet_withdraw_failed': '❌ Withdrawal failed: {error}',
    
    'wallet_stake_title': '📈 *Stake ELC*',
    'wallet_stake_desc': (
        'Stake ELC tokens to earn rewards.\n\n'
        '💰 Available: {available} ELC\n'
        '📈 Staked: {staked} ELC\n'
        '🎁 Rewards: {rewards} ELC'
    ),
    
    'wallet_stake_success': '✅ Staked {amount} ELC.',
    'wallet_unstake_success': '✅ Unstaked {amount} ELC + {rewards} ELC rewards.',
    
    # ELC minimum requirements
    'elc_min_convert': '❌ Minimum 10 ELC required for conversion',
    'elc_min_stake': '❌ Minimum 1 ELC required for staking',
    
    'wallet_history_title': '📋 *Transaction History*',
    'wallet_history_empty': 'No transactions yet.',
    'wallet_history_item': '{type_emoji} {type}: {amount:+.2f} ELC\n   {date}',
    
    # My subscription
    'my_subscription_header': '📋 *My Subscription*',
    'my_subscription_active': (
        '📋 *Current Plan:* {plan}\n'
        '⏰ *Expires:* {expires}\n'
        '📅 *Days Left:* {days}'
    ),
    'my_subscription_none': '❌ No active subscription.\n\n👉 /subscribe',
    'my_subscription_history': '📜 *Payment History:*',
    'subscription_expiring_soon': '⚠️ Your {plan} expires in {days} days.\n\n👉 /subscribe',
    
    # Promo codes
    'promo_enter': '🎟 Enter promo code:',
    'promo_success': '🎉 Promo applied!\n\n{plan} activated for {days} days.',
    'promo_invalid': '❌ Invalid promo code.',
    'promo_expired': '❌ Promo code expired.',
    'promo_used': '❌ Promo code already used.',
    'promo_already_used': '❌ You already used this promo.',
    
    # =====================================================
    # ADMIN PANEL
    # =====================================================
    
    'admin_panel': '👑 Admin Panel:',
    'admin_pause': '⏸️ Notifications paused.',
    'admin_resume': '▶️ Notifications resumed.',
    'admin_closed': '✅ Closed {count} {type}.',
    'admin_canceled_limits': '✅ Cancelled {count} limit orders.',
    
    'admin_pause_all': '⏸️ Pause All',
    'admin_resume_all': '▶️ Resume',
    'admin_close_longs': '🔒 Close LONGs',
    'admin_close_shorts': '🔓 Close SHORTs',
    'admin_cancel_limits': '❌ Cancel Limits',
    'admin_users': '👥 Users',
    
    'admin_pause_notice': '⏸️ All notifications paused.',
    'admin_resume_notice': '▶️ Notifications resumed.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ Closed {count} {type}.',
    'admin_canceled_limits_total': '✅ Cancelled {count} limit orders.',
    
    # Admin license management
    'admin_license_menu': '🔑 *License Management*',
    'admin_btn_grant_license': '🎁 Grant',
    'admin_btn_view_licenses': '📋 View',
    'admin_btn_create_promo': '🎟 Create Promo',
    'admin_btn_view_promos': '📋 Promos',
    'admin_btn_expiring_soon': '⚠️ Expiring',
    'admin_grant_select_type': 'Select type:',
    'admin_grant_select_period': 'Select period:',
    'admin_grant_enter_user': 'Enter user ID:',
    'admin_license_granted': '✅ {plan} granted to {uid} for {days} days.',
    'admin_license_extended': '✅ Extended by {days} days for {uid}.',
    'admin_license_revoked': '✅ License revoked for {uid}.',
    'admin_promo_created': '✅ Promo: {code}\nType: {type}\nDays: {days}\nMax uses: {max}',
    'license_granted_notification': '🎉 Congratulations!\n\nYou have been granted a **{plan}** subscription for **{days} days**!\n\n📅 Valid until: {end_date}\n\nThank you for using Enliko!',
    
    # Admin user management
    'admin_users_management': '👥 Users',
    'admin_licenses': '🔑 Licenses',
    'admin_search_user': '🔍 Search',
    'admin_users_menu': '👥 *User Management*',
    'admin_all_users': '👥 All',
    'admin_active_users': '✅ Active',
    'admin_banned_users': '🚫 Banned',
    'admin_no_license': '❌ No License',
    'admin_no_users_found': 'No users found.',
    'admin_enter_user_id': '🔍 Enter user ID:',
    'admin_invalid_user_id': '❌ Invalid user ID. Enter a number.',
    'admin_user_found': '✅ User {uid} found.',
    'admin_user_not_found': '❌ User {uid} not found.',
    'admin_invalid_user_id': '❌ Invalid user ID.',
    'admin_view_card': '👤 View',
    
    # User card
    'admin_user_card': (
        '👤 *User*\n\n'
        '📋 ID: `{uid}`\n'
        '{status_emoji} Status: {status}\n'
        '{license_emoji} License: {license_type}\n'
        '📅 Expires: {license_expires}\n'
        '🌐 Language: {lang}\n'
        '📊 Mode: {trading_mode}\n'
        '💰 Entry %: {percent}%\n\n'
        '📊 Positions: {positions}\n'
        '📈 Trades: {trades}\n'
        '💰 P/L: {pnl}\n'
        '📅 First seen: {first_seen}'
    ),
    
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
    
    # User actions
    'admin_btn_grant_lic': '🎁 Grant',
    'admin_btn_extend': '⏳ Extend',
    'admin_btn_revoke': '🚫 Revoke',
    'admin_btn_ban': '🚫 Ban',
    'admin_btn_unban': '✅ Unban',
    'admin_btn_approve': '✅ Approve',
    'admin_btn_message': '✉️ Message',
    'admin_btn_delete': '🗑 Delete',
    
    'admin_user_banned': '✅ User banned.',
    'admin_user_unbanned': '✅ User unbanned.',
    'admin_user_approved': '✅ User approved.',
    'admin_confirm_delete': '⚠️ Confirm deletion of user {uid}?',
    'admin_confirm_yes': '✅ Yes',
    'admin_confirm_no': '❌ No',
    
    'admin_select_license_type': 'Select license type:',
    'admin_select_period': 'Select period:',
    'admin_select_extend_days': 'Select days to extend:',
    'admin_license_granted_short': '✅ Granted.',
    'admin_license_extended_short': '✅ Extended by {days} days.',
    'admin_license_revoked_short': '✅ Revoked.',
    
    'admin_enter_message': '✉️ Message for user {uid}:',
    'admin_message_sent': '✅ Message sent.',
    'admin_message_failed': '❌ Failed: {error}',
    
    # Admin payments & reports
    'admin_payments': '💳 Payments',
    'admin_reports': '📊 Reports',
    'admin_payments_menu': '💳 *Payments*',
    'admin_all_payments': '📜 All',
    'admin_no_payments_found': 'No payments.',
    
    'admin_reports_menu': '📊 *Reports*',
    'admin_global_stats': '📊 Global',
    'admin_demo_stats': '🎮 Demo',
    'admin_real_stats': '💎 Live',
    'admin_strategy_breakdown': '🎯 Strategies',
    'admin_top_traders': '🏆 Top',
    'admin_user_report': '👤 User',
    'admin_enter_user_for_report': '👤 Enter user ID:',
    'admin_generating_report': '📊 Generating...',
    'admin_view_report': '📊 Report',
    'admin_view_user': '👤 User',
    
    # =====================================================
    # ACCESS & MODERATION
    # =====================================================
    
    'banned': '🚫 Access restricted.',
    'invite_only': '🔒 Invite-only. Contact admin for access.',
    'need_terms': '⚠️ Please accept terms: /terms',
    'please_confirm': 'Please confirm:',
    'terms_ok': '✅ Terms accepted.',
    'terms_declined': '❌ Terms declined. Access restricted.',
    'usage_approve': 'Usage: /approve <user_id>',
    'usage_ban': 'Usage: /ban <user_id>',
    'not_allowed': 'Not allowed.',
    'bad_payload': 'Invalid data.',
    'unknown_action': 'Unknown action.',
    
    # Terms - Legal compliance
    'terms_title': (
        '📜 *Terms of Service*\n\n'
        'By using Enliko Trading Tools, you agree:\n\n'
        '1. *Educational Purpose*\n'
        'This platform provides educational tools for learning about '
        'cryptocurrency markets. It is NOT financial advice.\n\n'
        '2. *Risk Acknowledgment*\n'
        'Trading cryptocurrencies involves substantial risk of loss. '
        'You may lose some or all of your investment.\n\n'
        '3. *User Responsibility*\n'
        'You are solely responsible for all trading decisions. '
        'Past performance does not guarantee future results.\n\n'
        '4. *No Guarantees*\n'
        'We do not guarantee profits or specific outcomes. '
        'Market conditions are unpredictable.\n\n'
        '5. *Age Requirement*\n'
        'You must be 18+ years old to use this platform.\n\n'
        '6. *Jurisdiction*\n'
        'You are responsible for compliance with your local laws.\n\n'
        'Do you accept these terms?'
    ),
    
    'terms_btn_accept': '✅ I Accept',
    'terms_btn_decline': '❌ Decline',
    'terms_unavailable': 'Terms unavailable. Contact admin.',
    'terms_confirm_prompt': 'Please confirm:',
    
    # Main menu
    'main_menu_hint': '\n\nSelect an option from the menu below:',
    
    # Admin new user
    'title': 'New user',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Name: {name}\n'
        '• Username: {uname}\n'
        '• Lang: {lang}\n'
        '• Allowed: {allowed}  Ban: {banned}'
    ),
    
    'btn_approve': '✅ Approve',
    'btn_ban': '⛔️ Ban',
    'admin_notify_fail': 'Failed to notify admin: {e}',
    'moderation_approved': '✅ Approved: {target}',
    'moderation_banned': '⛔️ Banned: {target}',
    'approved_user_dm': '✅ Access granted. Press /start.',
    'banned_user_dm': '🚫 Access restricted.',
    
    # Admin users list
    'users_not_found': 'No users found.',
    'users_page_info': '📄 Page {page}/{pages} — Total: {total}',
    'btn_blacklist': '🚫 Blacklist',
    'btn_delete_user': '🗑 Delete',
    'nav_caption': '🧭 Navigation:',
    'bad_page': 'Invalid page.',
    'admin_user_delete_fail': '❌ Delete failed: {error}',
    'admin_user_deleted': '🗑 User {target} deleted.',
    'user_access_approved': '✅ Access granted. Press /start.',
    
    # =====================================================
    # INDICATORS & ANALYSIS
    # =====================================================
    
    'indicators_header': '📈 *Technical Indicators*',
    'indicator_1': '1. RSI + Bollinger Bands',
    'indicator_2': '2. Trading Chaos',
    'indicator_3': '3. Adaptive Trend',
    'indicator_4': '4. Dynamic Regression',
    
    'rsi_bb_analysis': (
        '📈 *RSI + Bollinger Analysis*\n'
        '• Price: `{price:.6f}`\n'
        '• RSI: `{rsi:.1f}` ({zone})\n'
        '• BB Upper: `{bb_hi:.4f}`\n'
        '• BB Lower: `{bb_lo:.4f}`'
    ),
    
    'rsi_zone_oversold': 'Oversold (<30)',
    'rsi_zone_overbought': 'Overbought (>70)',
    'rsi_zone_neutral': 'Neutral (30–70)',
    
    # =====================================================
    # MARKET STATUS
    # =====================================================
    
    'market_header': '📊 *Market Overview*',
    'market_btc': '₿ BTC: {price} ({change:+.2f}%)',
    'market_eth': 'Ξ ETH: {price} ({change:+.2f}%)',
    'market_total_cap': '💰 Total Cap: ${cap}',
    'market_fear_greed': '📊 Fear & Greed: {value}',
    'market_last_update': '🕐 Updated: {time}',
    
    # =====================================================
    # SPOT TRADING
    # =====================================================
    
    'spot_header': '💹 *Spot Trading*',
    'spot_dca_enabled': '✅ Spot DCA Enabled',
    'spot_dca_disabled': '❌ Spot DCA Disabled',
    'spot_balance': '💰 Spot Balance:',
    'spot_holdings': '📦 Holdings:',
    
    'spot_freq_hourly': '⏰ Hourly',
    'spot_freq_daily': '📅 Daily',
    'spot_freq_weekly': '📆 Weekly',
    
    # Spot Portfolios
    'spot_portfolio_header': '📊 *Spot Portfolios*',
    'spot_portfolio_blue_chip': '💎 Blue Chips (BTC, ETH, BNB, SOL)',
    'spot_portfolio_defi': '🏦 DeFi (UNI, AAVE, MKR, LINK)',
    'spot_portfolio_layer2': '⚡ Layer 2 (MATIC, ARB, OP)',
    'spot_portfolio_ai': '🤖 AI & Data (FET, RNDR, TAO)',
    'spot_portfolio_gaming': '🎮 Gaming (AXS, SAND, MANA)',
    'spot_portfolio_meme': '🐕 Memecoins (DOGE, SHIB, PEPE)',
    'spot_portfolio_l1': '⚔️ L1 Killers (SOL, AVAX, NEAR)',
    'spot_portfolio_rwa': '🏛️ RWA (ONDO, MKR, SNX)',
    'spot_portfolio_infra': '🔧 Infrastructure (LINK, GRT, FIL)',
    'spot_portfolio_btc': '₿ BTC Only',
    'spot_portfolio_eth_btc': '💰 ETH + BTC',
    'spot_portfolio_custom': '⚙️ Custom Portfolio',
    'spot_portfolio_select': '📁 Select a portfolio preset:',
    
    # Spot DCA Strategies
    'spot_dca_strategy_header': '📈 *DCA Strategies*',
    'spot_dca_fixed': '📊 Fixed DCA - Same amount at regular intervals',
    'spot_dca_value_avg': '📈 Value Averaging - Buy more when price drops',
    'spot_dca_fear_greed': '😱 Fear & Greed - Buy more during extreme fear',
    'spot_dca_dip_buy': '📉 Dip Buying - Only buy on significant dips',
    'spot_dca_crash_boost': '🚨 Crash Boost - 3x buy when price drops >15%',
    'spot_dca_momentum': '🚀 Momentum - Buy more in uptrends',
    'spot_dca_rsi': '📐 RSI Smart - Buy more when RSI < 30',
    'spot_dca_strategy_select': '🎯 Select DCA strategy:',
    
    # Spot TP Profiles
    'spot_tp_header': '🎯 *Take Profit Profiles*',
    'spot_tp_conservative': '🐢 Conservative - Small gains, frequent sells',
    'spot_tp_balanced': '⚖️ Balanced - Moderate gains',
    'spot_tp_aggressive': '🦁 Aggressive - Hold for bigger gains',
    'spot_tp_moonbag': '🌙 Moonbag - Keep 25% for moonshots',
    'spot_tp_profile_select': '💰 Select TP profile:',
    
    # Spot Performance
    'spot_performance_header': '📊 *Spot Performance*',
    'spot_performance_invested': '💵 Total Invested: ${amount:.2f}',
    'spot_performance_current': '💰 Current Value: ${amount:.2f}',
    'spot_performance_pnl': '📈 Unrealized PnL: {pnl:+.2f} ({pct:+.2f}%)',
    'spot_performance_holdings': '📦 Holdings: {count} coins',
    
    # Spot Advanced Features
    'spot_advanced_header': '⚙️ *Advanced Spot Features*',
    'spot_profit_lock': '🔒 Profit Lock - Sell {pct}% when +{trigger}%',
    'spot_trailing_tp': '📉 Trailing TP - Activation: +{act}%, Trail: {trail}%',
    'spot_auto_rebalance': '⚖️ Auto Rebalance - Threshold: {threshold}%',
    'spot_limit_dca': '🎯 Limit DCA - Offset: -{offset}%',
    
    # Spot Buttons
    'spot_btn_buy': '💰 Buy Now',
    'spot_btn_sell': '💸 Sell Menu',
    'spot_btn_holdings': '💎 Holdings',
    'spot_btn_rebalance': '⚖️ Rebalance',
    'spot_btn_settings': '⚙️ Settings',
    
    # Spot/Grid error messages
    'spot_not_enabled': '❌ Spot trading is not enabled. Enable it in API Settings first.',
    'spot_auto_enabled': '✅ Auto DCA enabled',
    'spot_auto_disabled': '❌ Auto DCA disabled',
    'spot_no_balance': '❌ No spot balance found',
    'spot_no_coins': '❌ No coins to sell',
    'spot_gain_min': '❌ Minimum gain trigger is 1%',
    'spot_gain_max': '❌ Maximum gain trigger is 10000%',
    'spot_sell_min': '❌ Minimum sell amount is 1%',
    'spot_sell_max': '❌ Maximum sell amount is 100%',
    'spot_invalid_pct': '❌ Invalid number. Please enter a valid percentage.',
    'spot_invalid_price': '❌ Invalid price. Please enter a number.',
    'spot_min_5': '❌ Minimum amount is 5 USDT',
    'spot_invalid_amount': '❌ Invalid amount. Please enter a number.',
    'grid_min_10': '❌ Minimum investment is 10 USDT',
    'grid_setup': '⏳ Setting up {coin} grid...',
    'grid_started': '✅ {coin} Grid Bot Started!',
    'grid_range': '📈 Range: ${low:.2f} - ${high:.2f}',
    'grid_levels': '🔢 Levels: {count}',
    'grid_investment': '💵 Investment: ${amount:.2f}',
    'grid_orders_placed': '📊 Orders placed: {count}',
    'grid_step': '📍 Grid step: ${step:.4f}',
    'grid_invalid_format': '❌ Invalid format. Please enter: low_price high_price grid_count investment',
    'grid_invalid_input': '❌ Invalid input. Please enter numbers.',
    'grid_failed': '❌ Failed to stop grid: {error}',
    'grid_cancelled': '❌ Orders Cancelled: {count}',
    
    # =====================================================
    # MANUAL ORDERS
    # =====================================================
    
    'manual_order_header': '📝 *Manual Order*',
    'manual_long': '🟢 LONG',
    'manual_short': '🔴 SHORT',
    
    'manual_order_confirm': (
        '⚠️ *Confirm Order*\n\n'
        '📊 {symbol} {side}\n'
        '💰 Amount: {amount} USDT\n\n'
        '⚠️ _Trading involves risk._\n'
        '_You are responsible for this decision._'
    ),
    
    'manual_order_success': '✅ Order placed: {symbol} {side}',
    'manual_order_failed': '❌ Order failed: {error}',
    
    # TP/SL validation
    'update_tpsl_no_positions': '🚫 No open positions.',
    'update_tpsl_prompt': 'Enter SYMBOL TP SL:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format': '❌ Invalid format. Use: SYMBOL TP SL',
    
    'invalid_tpsl_long': (
        '❌ Invalid TP/SL for LONG.\n'
        'Current: {current:.2f}\n'
        'Required: SL < {current:.2f} < TP'
    ),
    
    'invalid_tpsl_short': (
        '❌ Invalid TP/SL for SHORT.\n'
        'Current: {current:.2f}\n'
        'Required: TP < {current:.2f} < SL'
    ),
    
    'no_position_symbol': '🚫 No position on {symbol}.',
    'tpsl_set_success': '✅ TP={tp:.2f} SL={sl:.2f} for {symbol}',
    
    # =====================================================
    # TP / SL BUTTONS
    # =====================================================
    
    'button_toggle_atr': '📊 ATR',
    'button_lang': '🌍 Language',
    'button_set_tp': '📈 TP %',
    'button_set_sl': '📉 SL %',
    'config_stop_mode': 'Stop mode: *{mode}*',
    'config_dca': 'DCA: L1=-{dca1}%, L2=-{dca2}%',
    
    'enter_tp': '❌ Enter TP % value:',
    'tp_set_success': '✅ TP set: {pct}%',
    'enter_sl': '❌ Enter SL % value:',
    'sl_set_success': '✅ SL set: {pct}%',
    
    'mode_atr': 'ATR-based',
    'mode_fixed': 'Fixed %',
    
    # =====================================================
    # LIMIT ONLY & FEATURES
    # =====================================================
    
    'limit_only_toggled': '🔄 Limit orders {state}',
    'feature_limit_only': 'Limit Orders',
    'feature_oi': 'OI',
    'feature_rsi_bb': 'RSI+BB',
    'status_enabled': '✅',
    'status_disabled': '❌',
    
    # =====================================================
    # PARSING ERRORS
    # =====================================================
    
    'parse_limit_error': 'Limit: requires 4 args (SYMBOL SIDE PRICE QTY)',
    'parse_market_error': 'Market: requires 3 args (SYMBOL SIDE QTY)',
    'parse_side_error': 'SIDE must be LONG or SHORT',
    
    # =====================================================
    # EXCHANGE SELECTION
    # =====================================================
    
    'exchange_header': '🔄 *Select Exchange*',
    'exchange_bybit': '🟠 Bybit',
    'exchange_hyperliquid': '🔷 HyperLiquid',
    'exchange_selected': '✅ {exchange} selected.',
    
    'btn_bybit_demo': '🎮 Demo',
    'btn_bybit_real': '💎 Live',
    'btn_hl_testnet': '🧪 Testnet',
    'btn_hl_mainnet': '🌐 Mainnet',
    
    'button_hyperliquid': '🔷 HyperLiquid',
    'button_webapp': '🌐 WebApp',
    'button_switch_exchange': '🔄 Switch Exchange',
    'button_api_bybit': '🟠 Bybit API',
    'button_api_hl': '🔷 HL API',
    
    'hl_settings': 'HyperLiquid',
    'hl_trading_enabled': 'HyperLiquid Enabled',
    'hl_reset_settings': '🔄 Reset to Bybit',
    
    # =====================================================
    # SUPPORT
    # =====================================================
    
    'support_prompt': '✉️ Need help?',
    'support_button': 'Contact Support',
    
    # =====================================================
    # MISC
    # =====================================================
    
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',
    'emoji_long': '🟢',
    'emoji_short': '🔴',
    'emoji_neutral': '⚪️',
    
    'fallback': '❓ Please use the menu.',
    'db_quarantine_notice': '⚠️ Temporary maintenance mode.',
    
    'your_id': 'Your ID: {uid}',
    'error_validation': '❌ {msg}',
    'error_generic': 'Error: {msg}',
    'error_fetch_balance': '❌ Balance error: {error}',
    'error_fetch_orders': '❌ Orders error: {error}',
    'error_occurred': '❌ Error: {error}',
    'position_closed_error': '⚠️ {symbol} closed but log failed: {error}',
    
    # =====================================================
    # DCA NOTIFICATIONS
    # =====================================================
    
    'dca_10pct': 'DCA -{pct}%: Added to {symbol} qty={qty} @ {price}',
    'dca_25pct': 'DCA -{pct}%: Added to {symbol} qty={qty} @ {price}',
    
    # =====================================================
    # LIMIT LADDER
    # =====================================================
    
    'limit_ladder': '📉 Limit Ladder',
    'limit_ladder_header': '📉 *Limit Ladder*',
    'limit_ladder_settings': '⚙️ Ladder Settings',
    'ladder_count': 'Number of orders',
    'ladder_info': 'Limit orders placed below entry for scaling.',
    'prompt_ladder_pct_entry': '📉 Order {idx} — % below entry:',
    'prompt_ladder_pct_deposit': '💰 Order {idx} — % of deposit:',
    'ladder_order_saved': '✅ Order {idx}: -{pct_entry}% @ {pct_deposit}%',
    'ladder_orders_placed': '📉 Placed {count} ladder orders for {symbol}',
    
    # =====================================================
    # ENLIKO AI INFO
    # =====================================================
    
    'elcaro_ai_info': '🤖 *Enliko Analysis*',
    'elcaro_ai_desc': '_Parameters extracted from market data._',
    
    'fibonacci_info': '📐 *Fibonacci Analysis*',
    'fibonacci_desc': '_Levels based on Fibonacci extensions._',
    'prompt_min_quality': 'Enter Min Quality % (0-100):',
    
    # =====================================================
    # SIDE SETTINGS HEADERS
    # =====================================================
    
    'prompt_long_entry_pct': '📈 LONG Entry %:',
    'prompt_long_sl_pct': '📈 LONG Stop-Loss %:',
    'prompt_long_tp_pct': '📈 LONG Take-Profit %:',
    'prompt_short_entry_pct': '📉 SHORT Entry %:',
    'prompt_short_sl_pct': '📉 SHORT Stop-Loss %:',
    'prompt_short_tp_pct': '📉 SHORT Take-Profit %:',
    
    'scrypto_side_header': '{emoji} *Scryptomera {side} Settings*',
    'scalper_side_header': '{emoji} *Scalper {side} Settings*',
    'strategy_param_header': '⚙️ *{name} Configuration*',
    
    # =====================================================
    # DEEP LOSS ALERTS
    # =====================================================
    
    'btn_close_position': '❌ Close Position',
    'btn_enable_dca': '📈 Enable DCA',
    'btn_ignore': '🔇 Ignore',
    
    'deep_loss_alert': (
        '⚠️ <b>Position Alert</b>\n\n'
        '📊 <b>{symbol}</b> ({side})\n'
        '📉 Drawdown: <code>{loss_pct:.2f}%</code>\n'
        '💰 Entry: <code>{entry}</code>\n'
        '📍 Mark: <code>{mark}</code>\n\n'
        '<b>Options:</b>\n'
        '• Close — Accept current loss\n'
        '• DCA — Add to position (average down)\n'
        '• Ignore — No action'
    ),
    
    'position_already_closed': '❌ Position {symbol} already closed.',
    'deep_loss_closed': '✅ Position {symbol} closed.',
    'deep_loss_close_error': '❌ Close error: {error}',
    'dca_already_enabled': '✅ DCA already enabled for {symbol}.',
    'dca_enabled_for_symbol': '✅ DCA enabled for {symbol}.',
    'dca_enable_error': '❌ Error: {error}',
    'deep_loss_ignored': '🔇 {symbol} left unchanged.',
    
    # =====================================================
    # ERROR MONITOR
    # =====================================================
    
    'error_insufficient_balance': '💰 Insufficient funds. Top up balance or reduce size.',
    'error_order_too_small': '📉 Order too small (min $5). Increase Entry%.',
    'error_api_key_expired': '🔑 API key invalid. Update in settings.',
    'error_api_key_missing': '🔑 API keys not configured.',
    'error_rate_limit': '⏳ Rate limit. Wait and retry.',
    'error_position_not_found': '📊 Position not found.',
    'error_leverage_error': '⚙️ Leverage error. Adjust on exchange.',
    'error_network_error': '🌐 Network error. Retry later.',
    'error_sl_tp_invalid': '⚠️ SL/TP too close. Will retry.',
    'error_equity_zero': '💰 Balance is zero. Deposit funds.',
    
    # =====================================================
    # HARDCODED STRINGS FIX
    # =====================================================
    
    'min_amount_error': '❌ Minimum: 1 USDT',
    'max_amount_error': '❌ Maximum: 100,000 USDT',
    'invalid_amount': '❌ Invalid amount.',
    'hl_no_positions': '📭 No HyperLiquid positions.',
    'hl_no_orders': '📭 No HyperLiquid orders.',
    'hl_no_history': '📭 No HyperLiquid history.',
    'cancelled': '❌ Cancelled.',
    'entry_pct_range_error': '❌ Entry % must be 0.1-100.',
    'sl_tp_range_error': '❌ SL/TP must be 0.1-500.',
    'leverage_range_error': '❌ Leverage must be 1-100.',
    'hl_setup_cancelled': '❌ HyperLiquid setup cancelled.',
    'auto_default': 'Auto',
    
    'terminal_button': '💻 Terminal',
    'exchange_mode_activated_bybit': '🟠 *Bybit mode*',
    'exchange_mode_activated_hl': '🔷 *HyperLiquid mode*',
    'error_processing_request': '⚠️ Error processing request.',
    'unauthorized_admin': '❌ Unauthorized.',
    'error_loading_dashboard': '❌ Dashboard error.',
    'unauthorized': '❌ Unauthorized.',
    'processing_blockchain': '⏳ Processing...',
    'verifying_payment': '⏳ Verifying...',
    'no_wallet_configured': '❌ No wallet configured.',
    'use_start_menu': 'Use /start for menu.',
    
    # 2FA Login confirmation
    'login_approved': '✅ Login approved!\n\nYou can now continue in your browser.',
    'login_denied': '❌ Login denied.\n\nIf this wasn\'t you, we recommend reviewing your security settings.',
    'login_expired': '⏰ Confirmation expired. Please try again.',
    'login_error': '⚠️ Processing error. Please try again later.',
    
    # Hardcore mode (kept for compatibility)
    'hardcore_mode': '💀 *Advanced Mode*',
}
