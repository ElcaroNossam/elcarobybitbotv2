# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu
    'welcome':                     '👋 Përshëndetje! Zgjidh një veprim:',
    'no_strategies':               '❌ Asnjë',
    'guide_caption':               '📚 Udhëzuesi i Përdoruesit të Botit\n\nLexoni këtë udhëzues për të mësuar si të konfiguroni strategjitë dhe të përdorni botin në mënyrë efektive.',
    'privacy_caption':             '📜 Politika e Privatësisë dhe Kushtet e Përdorimit\n\nJu lutemi lexoni këtë dokument me kujdes.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 Sekret',
    'button_api_settings':         '🔑 API',
    'button_balance':              '💰 Bilanci USDT',
    'button_orders':               '📜 Porositë e mia',
    'button_positions':            '📊 Pozicionet',
    'button_percent':              '🎚 % për tregti',
    'button_coins':                '💠 Grupi i monedhave',
    'button_market':               '📈 Tregu',
    'button_manual_order':         '✋ Urdhër manual',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ Anulo urdhrin',
    'button_limit_only':           '🎯 Vetëm Limit',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_settings':             '⚙️ Cilësimet',
    'button_indicators':           '💡 Treguesit',
    'button_support':              '🆘 Asistencë',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 Mënyra TP/SL tani është: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Përqindje fikse',

    # Limits
    'limit_positions_exceeded':    '🚫 U tejkalua kufiri i pozicioneve të hapura ({max})',
    'limit_limit_orders_exceeded': '🚫 U tejkalua kufiri i urdhrave Limit ({max})',

    # Languages
    'select_language':             'Zgjidh gjuhën:',
    'language_set':                'Gjuha u vendos në:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'Zgjidh llojin e urdhrit:',
    'limit_order_format': (
        "Shkruaj parametrat e urdhrit Limit si më poshtë:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "ku SIDE = LONG ose SHORT\n"
        "Shembull: `BTCUSDT LONG 20000 0.1`\n\n"
        "Për të anuluar, dërgo ❌ Anulo urdhrin"
    ),
    'market_order_format': (
        "Shkruaj parametrat e urdhrit Market si më poshtë:\n"
        "`SYMBOL SIDE QTY`\n"
        "ku SIDE = LONG ose SHORT\n"
        "Shembull: `BTCUSDT SHORT 0.1`\n\n"
        "Për të anuluar, dërgo ❌ Anulo urdhrin"
    ),
    'order_success':               '✅ Urdhri u krijua me sukses!',
    'order_create_error':          '❌ Dështoi krijimi i urdhrit: {msg}',
    'order_fail_leverage':         (
        "❌ Urdhri nuk u krijua: leva në llogarinë tënde Bybit është shumë e lartë për këtë madhësi.\n"
        "Ule levën te cilësimet e Bybit."
    ),
    'order_parse_error':           '❌ Dështoi analizimi: {error}',
    'price_error_min':             '❌ Gabim çmimi: duhet të jetë ≥{min}',
    'price_error_step':            '❌ Gabim çmimi: duhet të jetë shumëfish i {step}',
    'qty_error_min':               '❌ Gabim sasia: duhet të jetë ≥{min}',
    'qty_error_step':              '❌ Gabim sasia: duhet të jetë shumëfish i {step}',

    # Loading…
    'loader':                      '⏳ Po mblidhen të dhënat…',

    # Market command
    'market_status_heading':       '*Gjendja e tregut:*',
    'market_dominance_header':    'Monedhat Kryesore sipas Dominimit',
    'market_total_header':        'Kapitalizimi Total i Tregut',
    'market_indices_header':      'Indekset e Tregut',
    'usdt_dominance':              'Dominanca e USDT',
    'btc_dominance':               'Dominanca e BTC',
    'dominance_rising':            '↑ në rritje',
    'dominance_falling':           '↓ në rënie',
    'dominance_stable':            '↔️ e qëndrueshme',
    'dominance_unknown':           '❔ pa të dhëna',
    'btc_price':                   'Çmimi i BTC',
    'last_24h':                    'në 24 orët e fundit',
    'alt_signal_label':            'Sinjal altcoin',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Lajmet e fundit (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'Nuk u gjet çmimi i ekzekutimit për mbyllje',

    # /account
    'account_balance':             '💰 Bilanci USDT: `{balance:.2f}`',
    'account_realized_header':     '📈 *PnL i realizuar:*',
    'account_realized_day':        '  • Sot    : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 ditë : `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *PnL i parealizuar:*',
    'account_unreal_total':        '  • Totali : `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % e IM : `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Cilësimet e tua:*',
    'config_percent':              '• 🎚 % për tregti     : `{percent}%`',
    'config_coins':                '• 💠 Monedhat         : `{coins}`',
    'config_limit_only':           '• 🎯 Urdhra Limit     : {state}',
    'config_atr_mode':             '• 🏧 SL me ATR        : {atr}',
    'config_trade_oi':             '• 📊 Tregti OI        : {oi}',
    'config_trade_rsi_bb':         '• 📈 Tregti RSI+BB    : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%              : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%              : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 Nuk ka urdhra të hapur',
    'open_orders_header':          '*📒 Urdhrat e hapur:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Ana : `{side}`\n"
        "   • Sasia: `{qty}`\n"
        "   • Çmimi: `{price}`\n"
        "   • ID   : `{id}`"
    ),
    'open_orders_error':           '❌ Gabim në marrjen e urdhrave: {error}',

    # Manual coin selection
    'enter_coins':                 "Shkruaj simbolet të ndara me presje, p.sh.:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Monedhat u zgjodhën: {coins}',

    # Positions
    'no_positions':                '🚫 Nuk ka pozicione të hapura',
    'positions_header':            '📊 Pozicionet e tua të hapura:',
    'position_item':               (
        "— Pozicioni #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • Madhësia        : {size}\n"
        "  • Çmimi i hyrjes  : {avg:.8f}\n"
        "  • Çmimi mark      : {mark:.8f}\n"
        "  • Likuidimi       : {liq}\n"
        "  • Marzhi fillestar: {im:.2f}\n"
        "  • Marzhi mirëmbajt.: {mm:.2f}\n"
        "  • Bilanci i pozic.: {pm:.2f}\n"
        "  • Take Profit     : {tp}\n"
        "  • Stop Loss       : {sl}\n"
        "  • PnL i parealiz. : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'positions_overall':           'PnL i parealizuar total: {pnl:+.2f} ({pct:+.2f}%)',

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
    'errors':                      'Errors',

    # % per trade
    'set_percent_prompt':          'Shkruaj përqindjen e bilancit për tregti (p.sh. 2.5):',
    'percent_set_success':         '✅ % për tregti u vendos: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Vetëm urdhra Limit: {state}',
    'feature_limit_only':          'Vetëm Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Treguesit Elcaro*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. Trend adaptiv',
    'indicator_4':                 '4. Regresion dinamik',

    # Support
    'support_prompt':              '✉️ Të duhet ndihmë? Kliko më poshtë:',
    'support_button':              'Kontakto asistencën',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 Nuk ka pozicione të hapura',
    'update_tpsl_prompt':          'Shkruaj SYMBOL TP SL, p.sh.:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Format i pavlefshëm. Përdor: SYMBOL TP SL\nP.sh.: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Shkruaj Bybit API Key:',
    'api_saved':                   '✅ API Key u ruajt',
    'enter_secret':                'Shkruaj Bybit API Secret:',
    'secret_saved':                '✅ API Secret u ruajt',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ Shkruaj vlerën TP%',
    'tp_set_success':              '✅ TP% u vendos: {pct}%',
    'enter_sl':                    '❌ Shkruaj vlerën SL%',
    'sl_set_success':              '✅ SL% u vendos: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: kërkon 4 argumente (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: kërkon 3 argumente (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE duhet të jetë LONG ose SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ API Key/Secret nuk janë vendosur',
    'bybit_invalid_response':      '❌ Përgjigje e pavlefshme nga Bybit',
    'bybit_error':                 '❌ Gabim Bybit {path}: {data}',

    # Auto notifications
    'new_position': (
        '🚀 Pozicion i ri {symbol} @ {entry:.6f}, madhësia={size}\n'
        '📍 {exchange} • {market_type}'
    ),
    'sl_auto_set':                 '🛑 SL u vendos automatikisht: {price:.6f}',
    'auto_close_position':         '⏱ Pozicioni {symbol} (TF={tf}) i hapur > {tf} dhe në humbje, u mbyll automatikisht.',
    'position_closed': (
        '🔔 Pozicioni {symbol} u mbyll nga *{reason}*:\n'
        '• Strategy: `{strategy}`\n'
        '• Hyrja: `{entry:.8f}`\n'
        '• Dalja: `{exit:.8f}`\n'
        '• PnL  : `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '📍 {exchange} • {market_type}'
    ),

    # Entries & errors - format i unifikuar me info të plotë
    'oi_limit_entry':              '📉 *OI Hyrje Limit*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit gabim: {msg}',
    'oi_market_entry':             '📉 *OI Hyrje Market*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI Market gabim: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Hyrje Limit*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Hyrje Market*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Sasia: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB Market gabim: {msg}',

    'oi_analysis':                 '📊 *Analiza OI {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Hyrje Limit*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit gabim: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Hyrje Market*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market gabim: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>Bilanci i pamjaftueshëm!</b>\n\n💰 Nuk ka fonde të mjaftueshme në llogarinë tuaj {account_type} për të hapur këtë pozicion.\n\n<b>Zgjidhjet:</b>\n• Rimbushni bilancin\n• Zvogëloni madhësinë e pozicionit (% për tregti)\n• Ulni levën\n• Mbyllni disa pozicione të hapura',
    'insufficient_balance_error_extended': '❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Leva shumë e lartë!</b>\n\n⚙️ Leva juaj e konfiguruar tejkalon maksimumin e lejuar për këtë simbol.\n\n<b>Maksimumi i lejuar:</b> {max_leverage}x\n\n<b>Zgjidhja:</b> Shkoni te cilësimet e strategjisë dhe ulni levën.',
    


    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Hyrje Limit*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit gabim: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Hyrje Market*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market gabim: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *Elcaro Hyrje Limit*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Elcaro Limit gabim: {msg}',
    'elcaro_market_entry':         '🔥 *Elcaro Hyrje Market*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Elcaro Market gabim: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci Hyrje Limit*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci Limit gabim: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci Hyrje Market*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci Market gabim: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 Paneli i administratorit:',
    'admin_pause':                 '⏸️ Tregtia dhe njoftimet u pezulluan për të gjithë.',
    'admin_resume':                '▶️ Tregtia dhe njoftimet u rifilluan për të gjithë.',
    'admin_closed':                '✅ U mbyllën gjithsej {count} {type}.',
    'admin_canceled_limits':       '✅ U anuluan {count} urdhra Limit.',

    # Coin groups
    'select_coin_group':           'Zgjidh grupin e monedhave:',
    'group_all':                   'ALL',
    'group_top100':                'TOP100',
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ U vendos grupi i monedhave: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *Analiza RSI+BB*\n'
        '• Çmimi: `{price:.6f}`\n'
        '• RSI  : `{rsi:.1f}` ({zone})\n'
        '• BB sipër: `{bb_hi:.4f}`\n'
        '• BB poshtë: `{bb_lo:.4f}`\n\n'
        '*Hyrje MARKET {side} sipas RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'I tepër-shitur (<30)',
    'rsi_zone_overbought':         'I tepër-blerë (>70)',
    'rsi_zone_neutral':            'Neutral (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ TP/SL i pavlefshëm për LONG.\n'
        'Çmimi aktual: {current:.2f}\n'
        'Pritet: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ TP/SL i pavlefshëm për SHORT.\n'
        'Çmimi aktual: {current:.2f}\n'
        'Pritet: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 Nuk ke pozicion të hapur në {symbol}',
    'tpsl_set_success':            '✅ TP={tp:.2f} dhe SL={sl:.2f} u vendosën për {symbol}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Gjuha',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Mënyra stop: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ Urdhri Limit për {symbol} u plotësua @ {price}',
    'limit_order_cancelled':       '⚠️ Urdhri Limit për {symbol} (ID: {order_id}) u anulua.',
    'fixed_sl_tp':                 '✅ {symbol}: SL në {sl}, TP në {tp}',
    'tp_part':                     ', TP u vendos në {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL në {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL në {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP u inic. në {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL u zhvendos në BE te {entry}',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP u përditësuan në {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Pozicioni {symbol} u mbyll por regjistrimi dështoi: {error}\n'
        'Kontakto asistencën.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Përqindje fikse',

    # System notices
    'db_quarantine_notice':        '⚠️ Regjistrimet janë pezulluar përkohësisht. Modaliteti i qetë për 1 orë.',

    # Fallback
    'fallback':                    '❓ Përdor butonat e menysë.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 Je i bllokuar.',
    'invite_only': '🔒 Hyrje vetëm me ftesë. Prisni miratimin e adminit.',
    'need_terms': '⚠️ Së pari pranoni kushtet: /terms',
    'please_confirm': 'Ju lutem konfirmoni:',
    'terms_ok': '✅ Faleminderit! Kushtet u pranuan.',
    'terms_declined': '❌ Refuzuat kushtet. Hyrja u mbyll. Mund të ktheheni me /terms.',
    'usage_approve': 'Përdorimi: /approve <user_id>',
    'usage_ban': 'Përdorimi: /ban <user_id>',
    'not_allowed': 'Nuk lejohet',
    'bad_payload': 'Të dhëna të pavlefshme',
    'unknown_action': 'Veprim i panjohur',

    'title': 'Përdorues i ri',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Emri: {name}\n'
        '• Përdoruesi: {uname}\n'
        '• Gjuha: {lang}\n'
        '• Lejuar: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve': '✅ Aprovo',
    'btn_ban': '⛔️ Blloko',
    'admin_notify_fail': 'Dështoi njoftimi i adminit: {e}',
    'moderation_approved': '✅ U aprovua: {target}',
    'moderation_banned': '⛔️ U bllokua: {target}',
    'approved_user_dm': '✅ Hyrja u aprovua. Shtyp /start.',
    'banned_user_dm': '🚫 Je i bllokuar.',

    'users_not_found': '😕 Nuk u gjetën përdorues.',
    'users_page_info': '📄 Faqja {page}/{pages} — gjithsej: {total}',
    'user_card_html': (
        '<b>👤 Përdorues</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Emri: {full_name}\n'
        '• Përdoruesi: {uname}\n'
        '• Gjuha: <code>{lang}</code>\n'
        '• Lejuar: {allowed}\n'
        '• I bllokuar: {banned}\n'
        '• Kushtet: {terms}\n'
        '• % për tregti: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 Listë e zezë',
    'btn_delete_user': '🗑 Fshi nga DB',
    'btn_prev': '⬅️ Mbrapa',
    'btn_next': '➡️ Para',
    'nav_caption': '🧭 Navigim:',
    'bad_page': 'Faqe e pavlefshme.',
    'admin_user_delete_fail': '❌ Dështoi fshirja e {target}: {error}',
    'admin_user_deleted': '🗑 Përdoruesi {target} u fshi nga DB.',
    'user_access_approved': '✅ Hyrja u aprovua. Shtyp /start.',

    'admin_pause_all': '⏸️ Pauzë për të gjithë',
    'admin_resume_all': '▶️ Vazhdo',
    'admin_close_longs': '🔒 Mbyll të gjithë LONG',
    'admin_close_shorts': '🔓 Mbyll të gjithë SHORT',
    'admin_cancel_limits': '❌ Fshi urdhra limit',
    'admin_users': '👥 Përdoruesit',
    'admin_pause_notice': '⏸️ Tregtia & njoftimet u pezulluan për të gjithë.',
    'admin_resume_notice': '▶️ Tregtia & njoftimet u rikthyen për të gjithë.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ U mbyllën gjithsej {count} {type}.',
    'admin_canceled_limits_total': '✅ U anuluan {count} urdhra limit.',

    'terms_btn_accept': '✅ Pranoj',
    'terms_btn_decline': '❌ Refuzoj',

    'emoji_long': '🟢',
    'emoji_short': '🔴',
    'emoji_neutral': '⚪️',

    # Scalper Strategy
    'button_scalper':                '🎯 Scalper',
    'button_elcaro':                 '🔥 Elcaro',
    'button_fibonacci':                '📐 Fibonacci',
    'config_trade_scalper':          '🎯 Scalper: {state}',
    'config_trade_elcaro':           '🔥 Elcaro: {state}',
    'config_trade_fibonacci':          '📐 Fibonacci: {state}',

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
    'api_test_success':            'Lidhja e suksesshme!',
    'api_test_no_keys':            'Çelësat API nuk janë vendosur',
    'api_test_set_keys':           'Ju lutem vendosni së pari API Key dhe Secret.',
    'api_test_failed':             'Lidhja dështoi',
    'api_test_error':              'Gabim',
    'api_test_check_keys':         'Ju lutem kontrolloni kredencialet tuaja API.',
    'api_test_status':             'Statusi',
    'api_test_connected':          'Lidhur',
    'balance_wallet':              'Bilanci i kulesës',
    'balance_equity':              'Kapitali',
    'balance_available':           'Në dispozicion',
    'api_missing_notice':          '⚠️ Nuk keni konfiguruar çelësat API të bursës. Ju lutem shtoni çelësin tuaj API dhe sekretin në cilësimet (butonat 🔑 API dhe 🔒 Secret), përndryshe boti nuk mund të tregtojë për ju.',
    'elcaro_ai_info':              '🤖 *Tregtim i mundësuar nga AI*',

    # Spot Trading
    'api_spot_trading':            '💹 Spot Trading',
    'api_spot_enabled':            '💹 <b>Spot Trading:</b> ✅ ON',
    'api_spot_disabled':           '💹 <b>Spot Trading:</b> ❌ OFF',
    'api_spot_toggled':            'Spot Trading: {status}',
    'spot_settings_title':         '💹 <b>Spot DCA Settings</b>',
    'spot_coins':                  '🪙 Coins: {coins}',
    'spot_dca_amount':             '💵 DCA Amount: {amount} USDT',
    'spot_dca_frequency':          '⏰ Frequency: {freq}',
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_freq_monthly':           'Monthly',
    'spot_buy_now':                '💰 Buy Now',
    'spot_auto_dca':               '🔄 Auto DCA: {status}',
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
    'spot_select_coins':           'Select coins for Spot DCA:',
    'spot_coins_saved':            '✅ Spot coins set: {coins}',
    'spot_select_frequency':       'Select DCA frequency:',
    'spot_frequency_saved':        '✅ Frequency set to {freq}',
    'spot_auto_enabled':           '✅ Auto DCA enabled',
    'spot_auto_disabled':          '❌ Auto DCA disabled',
    'spot_not_enabled':            '❌ Spot trading is not enabled. Enable it in API Settings first.',

    # Strategy trading mode
    'strat_mode_global':           '🌐 Global',
    'strat_mode_demo':             '🧪 Demo',
    'strat_mode_real':             '💰 Real',
    'strat_mode_both':             '🔄 Të dyja',
    'strat_mode_changed':          '✅ Mënyra e tregtimit {strategy}: {mode}',

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
    'fibonacci_limit_entry':           '📐 Fibonacci limit-entry {symbol} @ {price:.6f}',
    'fibonacci_limit_error':           '❌ Fibonacci limit-entry error: {msg}',
    'fibonacci_market_entry':          '🚀 Fibonacci market {symbol} @ {price:.6f}',
    'fibonacci_market_error':          '❌ Fibonacci market error: {msg}',
    'fibonacci_market_ok':             '📐 Fibonacci: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'fibonacci_analysis':              'Fibonacci: {side} @ {price}',
    'feature_fibonacci':               'Fibonacci',

    'scalper_limit_entry':           'Scalper: urdhër limit {symbol} @ {price}',
    'scalper_limit_error':           'Scalper gabim limit: {msg}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper gabim: {msg}',

    # Strategy Settings
    'button_strategy_settings':      '⚙️ Cilësimet e strategjive',
    'strategy_settings_header':      '⚙️ *Cilësimet e strategjive*',
    'strategy_param_header':         '⚙️ *Cilësimet e {name}*',
    'using_global':                  'Cilësime globale',
    'global_default':                'Global',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ Cilësimet DCA',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA Hapi 1 %',
    'dca_leg2':                      '📉 DCA Hapi 2 %',
    'param_percent':                 '📊 Hyrje %',
    'param_sl':                      '🔻 Stop-Loss %',
    'param_tp':                      '🔺 Take-Profit %',
    'param_reset':                   '🔄 Rivendos në global',
    'btn_close':                     '❌ Mbyll',
    'prompt_entry_pct':              'Shkruaj % hyrje (risku për tregti):',
    'prompt_sl_pct':                 'Shkruaj % Stop-Loss:',
    'prompt_tp_pct':                 'Shkruaj % Take-Profit:',
    'prompt_atr_periods':            'Shkruaj periudhat ATR (p.sh. 7):',
    'prompt_atr_mult':               'Shkruaj shumëzuesin ATR për trailing SL (p.sh. 1.0):',
    'prompt_atr_trigger':            'Shkruaj % aktivizimit ATR (p.sh. 2.0):',
    'prompt_dca_leg1':               'Shkruaj % DCA Hapi 1 (p.sh. 10):',
    'prompt_dca_leg2':               'Shkruaj % DCA Hapi 2 (p.sh. 25):',
    'settings_reset':                'Cilësimet u rivendosën në global',
    'strat_setting_saved':           '✅ {name} {param} u vendos në {value}',
    'dca_setting_saved':             '✅ DCA {leg} u vendos në {value}%',
    'invalid_number':                '❌ Numër i pavlefshëm. Shkruaj vlerë mes 0 dhe 100.',
    'dca_10pct':                     'DCA −{pct}%: shtesë {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: shtesë {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: Hapi1=-{dca1}%, Hapi2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 Periudhat ATR',
    'param_atr_mult':                '📉 Shumëzuesi ATR (hapi SL)',
    'param_atr_trigger':             '🎯 Aktivizimi ATR %',

    # Hardcoded strings fix
    'terms_unavailable':             'Kushtet e shërbimit nuk janë të disponueshme. Kontaktoni administratorin.',
    'terms_confirm_prompt':          'Ju lutem konfirmoni:',
    'your_id':                       'ID juaj: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Gabim: {msg}',

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
    'stats_profit_factor':           'PF',
    'stats_strategy_settings':       'Cilësimet e strategjisë',
    'settings_entry_pct':            'Hyrja',
    'settings_leverage':             'Levë',
    'settings_trading_mode':         'Modaliteti',
    'settings_direction':            'Drejtimi',
    'stats_all':                     '📈 All',
    'stats_oi':                      '📉 OI',
    'stats_rsi_bb':                  '📊 RSI+BB',
    'stats_scryptomera':             '🐱 Scryptomera',
    'stats_scalper':                 '⚡ Scalper',
    'stats_elcaro':                  '🔥 Elcaro',
    'stats_period_all':              'All time',
    'stats_period_today':            'Today',
    'stats_period_week':             'Week',
    'stats_period_month':            'Month',
    'stats_demo':                    '🔵 Demo',
    'stats_real':                    '�� Real',

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

    # Coins group per strategy
    'param_coins_group': '🪙 Coins',
    'select_coins_for_strategy': '🪙 *Select coins group for {name}*',
    'group_global': '📊 Global (use common setting)',

    # Elcaro AI settings

    # Leverage settings
    'param_leverage': '⚡ Leva',
    'prompt_leverage': 'Shkruaj levën (1-100):',
    'auto_default': 'Automatike',

    # Elcaro AI
    'elcaro_ai_desc': '_Të gjitha parametrat analizohen automatikisht nga sinjalet AI:_',

    # Scalper entries
    'scalper_market_entry': '🚀 Scalper market {symbol} @ {price:.6f}',
    'scalper_analysis': 'Scalper: {side} @ {price}',

    # Scryptomera feature
    'feature_scryptomera': 'Scryptomera',
    


    # Limit Ladder
    'limit_ladder': '📉 Shkallë limitesh',
    'limit_ladder_header': '📉 *Cilesimet e shkallës së limiteve*',
    'limit_ladder_settings': '⚙️ Cilësime shkallës',
    'ladder_count': 'Numri i urdhrave',
    'ladder_info': 'Urdhra limit nën hyrje për DCA. Çdo urdhër ka % nga hyrja dhe % të depozitës.',
    'prompt_ladder_pct_entry': '📉 Fut % nën çmimin e hyrjes për urdhrin {idx}:',
    'prompt_ladder_pct_deposit': '💰 Fut % të depozitës për urdhrin {idx}:',
    'ladder_order_saved': '✅ Urdhëri {idx} u ruajt: -{pct_entry}% @ {pct_deposit}% depozitë',
    'ladder_orders_placed': '📉 U vendosën {count} urdhra limit për {symbol}',
    
    # Spot Trading Mode
    'spot_trading_mode': 'Mënyra e tregtimit',
    'spot_btn_mode': 'Mënyra',
    
    # Stats PnL
    'stats_realized_pnl': 'I realizuar',
    'stats_unrealized_pnl': 'I parealizuar',
    'stats_combined_pnl': 'I kombinuar',
    'stats_spot': '💹 Spot',
    'stats_spot_title': 'Statistikat Spot DCA',
    'stats_spot_config': 'Konfigurimi',
    'stats_spot_holdings': 'Pozicionet',
    'stats_spot_summary': 'Përmbledhje',
    'stats_spot_current_value': 'Vlera aktuale',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    'no_license': '⚠️ Ju nevojitet një abonim aktiv për të përdorur këtë veçori.\n\nPërdorni /subscribe për të blerë licencë.',
    'no_license_trading': '⚠️ Ju nevojitet një abonim aktiv për të tregtuar.\n\nPërdorni /subscribe për të blerë licencë.',
    'license_required': '⚠️ Kjo veçori kërkon abonim {required}.\n\nPërdorni /subscribe për të përmirësuar.',
    'trial_demo_only': '⚠️ Licenca provë lejon vetëm tregtim demo.\n\nPërmirësoni në Premium ose Basic për tregtim real: /subscribe',
    'basic_strategy_limit': '⚠️ Licenca Basic në llogari reale lejon vetëm: {strategies}\n\nPërmirësoni në Premium për të gjitha strategjitë: /subscribe',
    
    'subscribe_menu_header': '💎 *Planet e Abonimit*',
    'subscribe_menu_info': 'Zgjidhni planin tuaj për të zhbllokuar veçoritë e tregtimit:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Provë (Falas)',
    'btn_enter_promo': '🎟 Kodi Promo',
    'btn_my_subscription': '📋 Abonimi Im',
    
    'premium_title': '💎 *PLANI PREMIUM*',
    'premium_desc': '''✅ Akses i plotë në të gjitha veçoritë
✅ Të 5 strategjitë: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ Tregtim Real + Demo
✅ Mbështetje prioritare
✅ SL/TP dinamik bazuar në ATR
✅ Shkallë limitesh DCA
✅ Të gjitha përditësimet e ardhshme''',
    'premium_1m': '💎 1 Muaj — {price}⭐',
    'premium_3m': '💎 3 Muaj — {price}⭐ (-15%)',
    'premium_6m': '💎 6 Muaj — {price}⭐ (-25%)',
    'premium_12m': '💎 12 Muaj — {price}⭐ (-35%)',
    
    'basic_title': '🥈 *PLANI BASIC*',
    'basic_desc': '''✅ Akses i plotë në llogarinë demo
✅ Llogari reale: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Fibonacci, Spot — vetëm Premium
✅ Mbështetje standarde
✅ SL/TP dinamik bazuar në ATR''',
    'basic_1m': '🥈 1 Muaj — {price}⭐',
    
    'trial_title': '🎁 *PLANI PROVË (FALAS)*',
    'trial_desc': '''✅ Akses i plotë në llogarinë demo
✅ Të 5 strategjitë në demo
❌ Tregtimi real nuk është i disponueshëm
⏰ Kohëzgjatja: 7 ditë
🎁 Vetëm një herë''',
    'trial_activate': '🎁 Aktivizo Provën Falas',
    'trial_already_used': '⚠️ Ju tashmë keni përdorur provën tuaj falas.',
    'trial_activated': '🎉 Prova u aktivizua! Keni 7 ditë akses demo të plotë.',
    
    'payment_select_method': '💳 *Zgjidhni Metodën e Pagesës*',
    'btn_pay_stars': '⭐ Telegram Stars',
    'btn_pay_ton': '💎 TON',
    'payment_stars_title': '⭐ Pagesë nëpërmjet Telegram Stars',
    'payment_stars_desc': 'Do të tarifoheni {amount}⭐ për {plan} ({period}).',
    'payment_ton_title': '💎 Pagesë nëpërmjet TON',
    'payment_ton_desc': '''Dërgoni saktësisht *{amount} TON* në:

`{wallet}`

Pas pagesës, klikoni butonin më poshtë për verifikim.''',
    'btn_verify_ton': '✅ Pagova — Verifiko',
    'payment_processing': '⏳ Duke përpunuar pagesën...',
    'payment_success': '🎉 Pagesa u krye!\n\n{plan} u aktivizua deri në {expires}.',
    'payment_failed': '❌ Pagesa dështoi: {error}',
    
    'my_subscription_header': '📋 *Abonimi Im*',
    'my_subscription_active': '''📋 *Plani Aktual:* {plan}
⏰ *Skadon:* {expires}
📅 *Ditë të Mbetura:* {days}''',
    'my_subscription_none': '❌ Nuk ka abonim aktiv.\n\nPërdorni /subscribe për të blerë plan.',
    'my_subscription_history': '📜 *Historia e Pagesave:*',
    'subscription_expiring_soon': '⚠️ Abonimi juaj {plan} skadon në {days} ditë!\n\nRinovoni tani: /subscribe',
    
    'promo_enter': '🎟 Futni kodin tuaj promo:',
    'promo_success': '🎉 Kodi promo u aplikua!\n\n{plan} u aktivizua për {days} ditë.',
    'promo_invalid': '❌ Kod promo i pavlefshëm.',
    'promo_expired': '❌ Ky kod promo ka skaduar.',
    'promo_used': '❌ Ky kod promo është përdorur tashmë.',
    'promo_already_used': '❌ Ju tashmë keni përdorur këtë kod promo.',
    
    'admin_license_menu': '🔑 *Menaxhimi i Licencave*',
    'admin_btn_grant_license': '🎁 Jep Licencë',
    'admin_btn_view_licenses': '📋 Shiko Licencat',
    'admin_btn_create_promo': '🎟 Krijo Promo',
    'admin_btn_view_promos': '📋 Shiko Promo',
    'admin_btn_expiring_soon': '⚠️ Skadon së shpejti',
    'admin_grant_select_type': 'Zgjidhni llojin e licencës:',
    'admin_grant_select_period': 'Zgjidhni periudhën:',
    'admin_grant_enter_user': 'Futni ID e përdoruesit:',
    'admin_license_granted': '✅ {plan} u dha përdoruesit {uid} për {days} ditë.',
    'admin_license_extended': '✅ Licenca u zgjat me {days} ditë për përdoruesin {uid}.',
    'admin_license_revoked': '✅ Licenca u revokua për përdoruesin {uid}.',
    'admin_promo_created': '✅ Kodi promo u krijua: {code}\nLloji: {type}\nDitë: {days}\nPërdorime maks: {max}',

    'admin_users_management': '👥 Përdoruesit',
    'admin_licenses': '🔑 Licencat',
    'admin_search_user': '🔍 Gjej Përdorues',
    'admin_users_menu': '👥 *Menaxhimi i Përdoruesve*\n\nZgjidhni filtër ose kërkoni:',
    'admin_all_users': '👥 Të gjithë Përdoruesit',
    'admin_active_users': '✅ Aktivë',
    'admin_banned_users': '🚫 Bllokuar',
    'admin_no_license': '❌ Pa Licencë',
    'admin_no_users_found': 'Nuk u gjetën përdorues.',
    'admin_enter_user_id': '🔍 Futni ID e përdoruesit për kërkim:',
    'admin_user_found': '✅ Përdoruesi {uid} u gjet!',
    'admin_user_not_found': '❌ Përdoruesi {uid} nuk u gjet.',
    'admin_invalid_user_id': '❌ ID e pavlefshme. Futni numër.',
    'admin_view_card': '👤 Shiko Kartën',
    
    'admin_user_card': '''👤 *Karta e Përdoruesit*

📋 *ID:* `{uid}`
{status_emoji} *Statusi:* {status}
📝 *Kushtet:* {terms}

{license_emoji} *Licenca:* {license_type}
📅 *Skadon:* {license_expires}
⏳ *Ditë të Mbetura:* {days_left}

🌐 *Gjuha:* {lang}
📊 *Mënyra e Tregtimit:* {trading_mode}
💰 *% për Tregti:* {percent}%
🪙 *Monedhat:* {coins}

🔌 *Çelësat API:*
  Demo: {demo_api}
  Real: {real_api}

📈 *Strategjitë:* {strategies}

📊 *Statistikat:*
  Pozicionet: {positions}
  Tregtitë: {trades}
  PnL: {pnl}
  Winrate: {winrate}%

💳 *Pagesat:*
  Totali: {payments_count}
  Stars: {total_stars}⭐

📅 *Parë e parë:* {first_seen}
🕐 *Parë e fundit:* {last_seen}
''',
    
    'admin_btn_grant_lic': '🎁 Jep',
    'admin_btn_extend': '⏳ Zgjat',
    'admin_btn_revoke': '🚫 Revoko',
    'admin_btn_ban': '🚫 Blloko',
    'admin_btn_unban': '✅ Zhblloko',
    'admin_btn_approve': '✅ Aprovo',
    'admin_btn_message': '✉️ Mesazh',
    'admin_btn_delete': '🗑 Fshi',
    
    'admin_user_banned': 'Përdoruesi u bllokua!',
    'admin_user_unbanned': 'Përdoruesi u zhbllokua!',
    'admin_user_approved': 'Përdoruesi u aprovua!',
    'admin_confirm_delete': '⚠️ *Konfirmo fshirjen*\n\nPërdoruesi {uid} do të fshihet përgjithmonë!',
    'admin_confirm_yes': '✅ Po, Fshi',
    'admin_confirm_no': '❌ Anulo',
    
    'admin_select_license_type': 'Zgjidhni llojin e licencës për përdoruesin {uid}:',
    'admin_select_period': 'Zgjidhni periudhën:',
    'admin_select_extend_days': 'Zgjidhni ditët për zgjatje për përdoruesin {uid}:',
    'admin_license_granted_short': 'Licenca u dha!',
    'admin_license_extended_short': 'U zgjat me {days} ditë!',
    'admin_license_revoked_short': 'Licenca u revokua!',
    
    'admin_enter_message': '✉️ Futni mesazhin për të dërguar tek përdoruesi {uid}:',
    'admin_message_sent': '✅ Mesazhi u dërgua tek përdoruesi {uid}!',
    'admin_message_failed': '❌ Dërgimi i mesazhit dështoi: {error}',

    # Auto-synced missing keys
    'admin_all_payments': '📜 All Payments',
    'admin_demo_stats': '🎮 Demo Stats',
    'admin_enter_user_for_report': '👤 Enter user ID for detailed report:',
    'admin_generating_report': '📊 Generating report for user {uid}...',
    'admin_global_stats': '📊 Global Stats',
    'admin_no_payments_found': 'No payments found.',
    'admin_payments': '💳 Payments',
    'admin_payments_menu': '💳 *Payments Management*',
    'admin_real_stats': '💰 Real Stats',
    'admin_reports': '📊 Reports',
    'admin_reports_menu': '''📊 *Reports & Analytics*

Select report type:''',
    'admin_strategy_breakdown': '🎯 By Strategy',
    'admin_top_traders': '🏆 Top Traders',
    'admin_user_report': '👤 User Report',
    'admin_view_report': '📊 View Report',
    'admin_view_user': '👤 User Card',
    'all_positions_closed': 'All positions closed',
    'btn_check_again': '🔄 Check Again',
    'button_admin': '👑 Admin',
    'button_licenses': '🔑 Licenses',
    'button_subscribe': '💎 Subscribe',
    'current': 'Current',
    'entry': 'Entry',
    'max_positions_reached': '⚠️ Maximum positions reached. New signals will be skipped until a position closes.',
    'payment_session_expired': '❌ Payment session expired. Please start again.',
    'payment_ton_not_configured': '❌ TON payments are not configured.',
    'payment_ton_not_found': '''❌ Payment not found or amount incorrect.

Please make sure you:
• Sent the exact amount
• Included the correct comment
• Wait a few minutes for confirmation

Try again after payment is confirmed on blockchain.''',
    'payment_verifying': '⏳ Verifying payment...',
    'position': 'Position',
    'size': 'Size',
    'stats_fibonacci': '📐 Fibonacci',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "Tregtimi HyperLiquid",
    "hl_reset_settings": "🔄 Rivendos në cilësimet Bybit",



    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ Anuluar.',
    'entry_pct_range_error': '❌ % hyrje duhet të jetë midis 0.1 dhe 100.',
    'hl_no_history': '�� Nuk ka histori tregtimi në HyperLiquid.',
    'hl_no_orders': '📭 Nuk ka urdhra të hapur në HyperLiquid.',
    'hl_no_positions': '📭 Nuk ka pozicione të hapura në HyperLiquid.',
    'hl_setup_cancelled': '❌ Konfigurimi i HyperLiquid u anulua.',
    'invalid_amount': '❌ Numër i pavlefshëm. Vendosni një shumë të vlefshme.',
    'leverage_range_error': '❌ Levave duhet të jetë midis 1 dhe 100.',
    'max_amount_error': '❌ Shuma maksimale është 100,000 USDT',
    'min_amount_error': '❌ Shuma minimale është 1 USDT',
    'sl_tp_range_error': '❌ SL/TP % duhet të jetë midis 0.1 dhe 500.',


    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 Aktivizo DCA',
    'btn_ignore': '🔇 Injoro',
    'dca_already_enabled': '✅ DCA tashmë i aktivizuar!\n\n📊 <b>{symbol}</b>\nBoti do të blejë automatikisht në rënie:\n• -10% → shtim\n• -25% → shtim\n\nKjo ndihmon për të mesatarizuar çmimin e hyrjes.',
    'dca_enable_error': '❌ Gabim: {error}',
    'dca_enabled_for_symbol': '✅ DCA i aktivizuar!\n\n📊 <b>{symbol}</b>\nBoti do të blejë automatikisht në rënie:\n• -10% → shtim (mesatare)\n• -25% → shtim (mesatare)\n\n⚠️ DCA kërkon bilanc të mjaftueshëm për porosi shtesë.',
    'deep_loss_alert': '⚠️ <b>Pozicioni në humbje të thellë!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Humbja: <code>{loss_pct:.2f}%</code>\n💰 Hyrja: <code>{entry}</code>\n📍 Aktuale: <code>{mark}</code>\n\n❌ Stop-loss nuk mund të vendoset mbi çmimin e hyrjes.\n\n<b>Çfarë të bësh?</b>\n• <b>Mbyll</b> - blloko humbjen\n• <b>DCA</b> - mesatarizo pozicionin\n• <b>Injoro</b> - lërë ashtu',
    'deep_loss_close_error': '❌ Gabim në mbylljen e pozicionit: {error}',
    'deep_loss_closed': '✅ Pozicioni {symbol} u mbyll.\n\nHumbja u bllokua. Ndonjëherë është më mirë të pranosh një humbje të vogël sesa të shpresosh për kthim.',
    'deep_loss_ignored': '🔇 Kuptova, pozicioni {symbol} u la pa ndryshuar.\n\n⚠️ Kujto: pa stop-loss, rreziku i humbjeve është i pakufizuar.\nMund ta mbyllësh pozicionin manualisht përmes /positions',
    'fibonacci_desc': '_Hyrja, SL, TP - nga nivelet Fibonacci në sinjal._',
    'fibonacci_info': '📐 *Strategjia Fibonacci Extension*',
    'prompt_min_quality': 'Vendosni cilësinë minimale % (0-100):',


    # Hardcore trading phrase
    'hardcore_mode': '💀 *MËNYRA HARDCORE*: Pa mëshirë, pa pendim. Vetëm fitim ose vdekje! 🔥',
}
