# -*- coding: utf-8 -*-
"""
Enliko Trading Tools — Albanian Translations (Shqip)
Version: 4.0.0 | Updated: 28 January 2026
LEGAL: Educational platform, not financial advice.
"""

TEXTS = {
    # Common UI
    'loader': '⏳ Po ngarkohet...',
    # =====================================================
    # LEGAL DISCLAIMERS (Mohime ligjore)
    # =====================================================
    
    'disclaimer_trading': (
        '⚠️ *MOHIM I RËNDËSISHËM*\n\n'
        'Kjo platformë ofron mjete edukative për të mësuar rreth tregjeve të kriptomonedhave.\n'
        'Kjo NUK është:\n'
        '• Këshillë financiare\n'
        '• Rekomandim investimi\n'
        '• Sistem fitimi i garantuar\n\n'
        'Tregtimi i kriptomonedhave përfshin rrezik të konsiderueshëm humbjeje. '
        'Ju mund të humbni një pjesë ose të gjithë investimin tuaj. '
        'Tregtoni vetëm me fonde që mund të përballoni të humbni.\n\n'
        'Performanca e kaluar nuk garanton rezultatet e ardhshme.'
    ),
    
    'disclaimer_short': '⚠️ _Vetëm mjete edukative. Nuk është këshillë financiare. Tregtimi përfshin rrezik._',
    
    'disclaimer_execution': (
        '⚠️ Duke vazhduar, ju pranoni se:\n'
        '• Jeni përgjegjës për të gjitha vendimet e tregtimit\n'
        '• Ky është mjet edukativ, jo këshillë financiare\n'
        '• Kuptoni rreziqet e tregtimit të kriptomonedhave\n'
        '• Performanca e kaluar nuk garanton rezultatet e ardhshme'
    ),
    
    # Welcome - Updated with legal positioning
    'welcome': (
        '📊 *Mirësevini në Enliko Trading Tools*\n\n'
        '🎯 Platformë edukative:\n'
        '• Ndjekja dhe analiza e portofolit\n'
        '• Testimi i strategjive\n'
        '• Vizualizimi i të dhënave të tregut\n'
        '• Mjete për menaxhimin e rrezikut\n\n'
        '⚠️ _Vetëm për qëllime edukative. Nuk është këshillë financiare._\n'
        '_Tregtimi përfshin rrezik të konsiderueshëm humbjeje._'
    ),
    
    'welcome_back': (
        '📊 *Enliko Trading Tools*\n\n'
        '⚠️ _Platformë edukative. Nuk është këshillë financiare._'
    ),
    
    # Legacy keys
    'button_orders':               '📜 Porositë e mia',
    'button_positions':            '🎯 Pozicionet',

    'button_balance': '💎 Portofoli',
    'button_market': '📈 Tregu',
    'button_strategies': '🤖 AI Bots',
    'button_subscribe': '🤝 MBËSHTETJE',
    'button_terminal': '💻 Terminal',
    'button_terminal': '💻 Terminal',
    'button_history':              '📋 Historia',
    'button_api_keys':             '🔑 Çelësat API',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_settings':             '⚙️ Cilësimet',

    # Inline buttons for manual order

    # ATR / Stop mode

    # Limits

    # Languages

    # Manual order

    # Loading…

    # Market command

    # Execution price error

    # /account

    # /show_config

    # Open orders

    # Manual coin selection

    # Positions
    'positions_header':            '📊 Pozicionet e tua të hapura:',

    # Position management (inline)
    'btn_close_position':          'Mbyll pozicionin',
    'btn_cancel':                  '❌ Anulo',
    'btn_back':                    '🔙 Kthehu',
    'position_already_closed':     'Pozicioni është mbyllur tashmë',
    'position_closed_success':     'Pozicioni u mbyll',
    'position_close_error':        'Gabim në mbylljen e pozicionit',

    # % per trade

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Vetëm urdhra Limit: {state}',
    'feature_limit_only':          'Vetëm Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Treguesit Enliko*',
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

    # Auto notifications - BLACK RHETORIC: Excitement & Celebration
    'new_position': (
        '🚀🔥 <b>Pozicion i ri u hap!</b>\n'
        '• {symbol} @ {entry:.6f}\n'
        '• Madhësia: {size}\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>AI po punon për ju! 🤖</i>'
    ),
    'sl_auto_set':                 '🛑 SL u vendos automatikisht: {price:.6f}',
    'auto_close_position':         '⏱ Pozicioni {symbol} (TF={tf}) i hapur > {tf} dhe në humbje, u mbyll automatikisht.',
    'position_closed': (
        '🎉 <b>Pozicioni u mbyll!</b> {symbol}\n'
        '• Arsyeja: <b>{reason}</b>\n'
        '• Strategjia: `{strategy}`\n'
        '• Hyrja: `{entry:.8f}`\n'
        '• Dalja: `{exit:.8f}`\n'
        '{pnl_emoji} <b>PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`</b>\n'
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
    'insufficient_balance_error_extended': '❌ <b>Bilanc i pamjaftueshëm!</b>\n\n📊 Strategjia: <b>{strategy}</b>\n🪙 Simboli: <b>{symbol}</b> {side}\n\n💰 Nuk ka mjaftueshëm fonde në llogarinë {account_type}.\n\n<b>Zgjidhjet:</b>\n• Rimbushni bilancin\n• Zvogëloni madhësinë e pozicionit (% për tregti)\n• Ulni levën\n• Mbyllni disa pozicione',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Leva shumë e lartë!</b>\n\n⚙️ Leva juaj e konfiguruar tejkalon maksimumin e lejuar për këtë simbol.\n\n<b>Maksimumi i lejuar:</b> {max_leverage}x\n\n<b>Zgjidhja:</b> Shkoni te cilësimet e strategjisë dhe ulni levën.',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>Limiti i pozicionit u tejkalua!</b>\n\n📊 Strategjia: <b>{strategy}</b>\n🪙 Simboli: <b>{symbol}</b>\n\n⚠️ Pozicioni juaj do të tejkalonte limitin maksimal.\n\n<b>Zgjidhjet:</b>\n• Ulni levën\n• Ulni madhësinë e pozicionit\n• Mbyllni disa pozicione',
    

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Hyrje Limit*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit gabim: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Hyrje Market*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market gabim: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko Hyrje Limit*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Enliko Limit gabim: {msg}',
    'elcaro_market_entry':         '🔥 *Enliko Hyrje Market*\n• {symbol} {side}\n• Çmimi: {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• Sasia: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Enliko Market gabim: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

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
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
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
    'select_language':             '🌍 Zgjidh gjuhën:',
    'language_set':                '✅ Gjuha u vendos:',
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

    # API Settings
    'api_key_set':                 '✅ Set',
    'api_test_success':            'Lidhja e suksesshme!',
    'api_test_failed':             'Lidhja dështoi',
    'balance_equity':              'Kapitali',
    'balance_available':           'Në dispozicion',
    'api_missing_notice':          '⚠️ Nuk keni konfiguruar çelësat API të bursës. Ju lutem shtoni çelësin tuaj API dhe sekretin në cilësimet (butonat 🔑 API dhe 🔒 Secret), përndryshe boti nuk mund të tregtojë për ju.',
    'elcaro_ai_info':              '🤖 *Tregtim i mundësuar nga AI*',

    # Spot Trading
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_balance':                '💰 Spot Balance: {balance}',

    # Strategy trading mode

    # Enliko (Heatmap)

    # Fibonacci (Fibonacci Extension)

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
    'strat_elcaro':                  '🔥 Enliko',
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

    # Break-Even settings UI
    'be_settings_header':            '🔒 *Cilësimet Break-Even*',
    'be_settings_desc':              '_Zhvendos SL në çmimin e hyrjes kur fitimi arrin % e aktivizimit_',
    'be_enabled_label':              '🔒 Break-Even',
    'be_trigger_label':              '🎯 Aktivizimi BE %',
    'prompt_be_trigger':             'Vendosni % e aktivizimit Break-Even (p.sh. 1.0):',
    'prompt_long_be_trigger':        '📈 LONG Aktivizimi BE %\n\nVendosni % e fitimit për të zhvendosur SL në hyrje:',
    'prompt_short_be_trigger':       '📉 SHORT Aktivizimi BE %\n\nVendosni % e fitimit për të zhvendosur SL në hyrje:',
    'param_be_trigger':              '🎯 Aktivizimi BE %',
    'be_moved_to_entry':             '🔒 {symbol}: SL u zhvendos në break-even @ {entry}',
    'be_status_enabled':             '✅ BE: {trigger}%',
    'be_status_disabled':            '❌ BE: Joaktiv',

    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ TP Parciale',
    'partial_tp_status_enabled':     '✅ TP Parciale aktive',
    'partial_tp_status_disabled':    '❌ TP Parciale joaktive',
    'partial_tp_step1_menu':         '✂️ *TP Parciale - Hapi 1*\n\nMbylle {close}% të pozicionit në +{trigger}% fitim\n\n_Zgjidh parametrin:_',
    'partial_tp_step2_menu':         '✂️ *TP Parciale - Hapi 2*\n\nMbylle {close}% të pozicionit në +{trigger}% fitim\n\n_Zgjidh parametrin:_',
    'trigger_pct':                   'Aktivizimi',
    'close_pct':                     'Mbyll',
    'prompt_long_ptp_1_trigger':     '📈 LONG Hapi 1: % Aktivizimi\n\nVendosni % e fitimit për mbylljen e pjesës së parë:',
    'prompt_long_ptp_1_close':       '📈 LONG Hapi 1: % Mbyllje\n\nVendosni % e pozicionit për mbyllje:',
    'prompt_long_ptp_2_trigger':     '📈 LONG Hapi 2: % Aktivizimi\n\nVendosni % e fitimit për mbylljen e pjesës së dytë:',
    'prompt_long_ptp_2_close':       '📈 LONG Hapi 2: % Mbyllje\n\nVendosni % e pozicionit për mbyllje:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT Hapi 1: % Aktivizimi\n\nVendosni % e fitimit për mbylljen e pjesës së parë:',
    'prompt_short_ptp_1_close':      '📉 SHORT Hapi 1: % Mbyllje\n\nVendosni % e pozicionit për mbyllje:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT Hapi 2: % Aktivizimi\n\nVendosni % e fitimit për mbylljen e pjesës së dytë:',
    'prompt_short_ptp_2_close':      '📉 SHORT Hapi 2: % Mbyllje\n\nVendosni % e pozicionit për mbyllje:',
    'partial_tp_executed':           '✂️ {symbol}: U mbyll {close}% në +{trigger}% fitim',

    # Hardcoded strings fix
    'terms_unavailable':             'Kushtet e shërbimit nuk janë të disponueshme. Kontaktoni administratorin.',
    'terms_confirm_prompt':          'Ju lutem konfirmoni:',
    'your_id':                       'ID juaj: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Gabim: {msg}',
    'error_fetch_balance':           '❌ Gabim në marrjen e bilancit: {error}',
    'error_fetch_orders':            '❌ Gabim në marrjen e porosive: {error}',
    'error_occurred':                '❌ Gabim: {error}',

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
    'stats_elcaro':                  '🔥 Enliko',
    'stats_period_all':              'All time',
    'stats_period_today':            '24h',
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

    # Enliko AI settings

    # Leverage settings
    'param_leverage': '⚡ Leva',
    'prompt_leverage': 'Shkruaj levën (1-100):',
    'auto_default': 'Automatike',

    # Enliko AI
    'elcaro_ai_desc': '_Të gjitha parametrat analizohen automatikisht nga sinjalet AI:_',

    # Scalper entries

    # Scryptomera feature
    

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
    
    'no_license': '🤝 *Community Membership*\n\nSupport our open-source project to access\nadditional community resources.\n\n👉 /subscribe — Support the project',
    'no_license_trading': '🤝 *Community Resource*\n\nThis resource is available to community supporters.\n\n👉 /subscribe — Support the project',
    'license_required': '🔒 *Supporter Resource*\n\nThis resource requires {required} membership.\n\n👉 /subscribe — Support the project',
    'trial_demo_only': '⚠️ *Explorer Access*\n\nExplorer access is limited to demo environment.\n\n👉 /subscribe — Become a supporter',
    'basic_strategy_limit': '⚠️ *Community Tier*\n\nAvailable templates: {strategies}\n\n👉 /subscribe — Upgrade your support',
    'subscribe_menu_header': '🤝 *Support Enliko*\n\nYour voluntary contribution helps maintain\nfree open-source community tools.\n\nChoose your support level:',
    'subscribe_menu_info': '_Select your support level:_',
    'btn_premium': '💎 Pro',
    'btn_basic': '💚 Mbështetës',
    'btn_trial': '🆓 Eksplorues (Falas)',
    'btn_enter_promo': '🎟 Kodi ftesës',
    'btn_my_subscription': '📋 Anëtarësia ime',
    'premium_title': '💎 *Pro Plan*',
    'premium_desc': '*Full access to all tools:*\n\n✅ All trading strategies\n✅ Demo & live environments\n✅ Priority support\n✅ ATR risk management\n✅ DCA configuration\n✅ All platform updates\n\n⚠️ _Trading involves risk. Not financial advice._',
    'premium_1m': '💎 1 Month — {price} ELC',
    'premium_3m': '💎 3 Months — {price} ELC',
    'premium_6m': '💎 6 Months — {price} ELC',
    'premium_12m': '💎 12 Months — {price} ELC',
    'basic_title': '💚 *Supporter Membership*',
    'basic_desc': '*Thank you for your support!*\n\n✅ Demo + live environments\n✅ Templates: OI, RSI+BB\n✅ Bybit integration\n✅ ATR risk management tools\n\n⚠️ _Educational tools only. Not financial advice._',
    'basic_1m': '💚 1 Month — {price} ELC',
    'trial_title': '🆓 *Explorer Access — 14 Days*',
    'trial_desc': '*Explore our community tools:*\n\n✅ Full demo environment\n✅ All analysis templates\n✅ 14 days access\n✅ No contribution required\n\n⚠️ _Educational tools only. Not financial advice._',
    'trial_activate': '🆓 Start Exploring',
    'trial_already_used': '⚠️ Explorer access already used. Consider supporting the project.',
    'trial_activated': '🎉 *Explorer Access Activated!*\n\n⏰ 14 days of full demo access.\n\n⚠️ _Educational tools only. Not financial advice._',
    'payment_select_method': '🤝 *How would you like to contribute?*',
    'btn_pay_elc': '◈ ELC',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' Pagesë nëpërmjet ELC',
    'payment_elc_desc': 'Do të tarifoheni {amount} ELC për {plan} ({period}).',
    'payment_ton_title': '💎 Pagesë nëpërmjet TON',
    'payment_ton_desc': '''Dërgoni saktësisht *{amount} TON* në:

`{wallet}`

Pas pagesës, klikoni butonin më poshtë për verifikim.''',
    'btn_verify_ton': '✅ Pagova — Verifiko',
    'payment_processing': '⏳ ...',
    'payment_success': '🎉 Thank you for your support!\n\n{plan} access activated until {expires}.',
    'payment_failed': '❌ Contribution failed: {error}',
    'my_subscription_header': '📋 *My Membership*',
    'my_subscription_active': '''📋 *Plani Aktual:* {plan}
⏰ *Skadon:* {expires}
📅 *Ditë të Mbetura:* {days}''',
    'my_subscription_none': '❌ No active membership.\n\nUse /subscribe to support the project.',
    'my_subscription_history': '📜 *Historia e Pagesave:*',
    'subscription_expiring_soon': '⚠️ Abonimi juaj {plan} skadon në {days} ditë!\n\nRinovoni tani: /subscribe',
    
    'promo_enter': '🎟 Enter your invite code:',
    'promo_success': '🎉 Invite code applied!\n\n{plan} access for {days} days.',
    'promo_invalid': '❌ Invalid invite code.',
    'promo_expired': '❌ This invite code has expired.',
    'promo_used': '❌ This invite code has already been used.',
    'promo_already_used': '❌ You have already used this invite code.',
    'admin_license_menu': '🤝 *Membership Management*',
    'admin_btn_grant_license': '🎁 Grant Access',
    'admin_btn_view_licenses': '📋 View Members',
    'admin_btn_create_promo': '🎟 Create Invite',
    'admin_btn_view_promos': '📋 View Invites',
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
  ELC: {total_elc}

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
    'admin_all_payments': '📜 Të gjitha pagesat',
    'admin_demo_stats': '🎮 Statistika demo',
    'admin_enter_user_for_report': '👤 Futni ID-në e përdoruesit për raport të detajuar:',
    'admin_generating_report': '📊 Duke gjeneruar raportin për përdoruesin {uid}...',
    'admin_global_stats': '📊 Statistika globale',
    'admin_no_payments_found': 'Nuk u gjetën pagesa.',
    'admin_payments': '💳 Pagesat',
    'admin_payments_menu': '💳 *Menaxhimi i pagesave*',
    'admin_real_stats': '💰 Statistika reale',
    'admin_reports': '📊 Raportet',
    'admin_reports_menu': '''📊 *Raporte dhe analiza*

Zgjidhni llojin e raportit:''',
    'admin_strategy_breakdown': '🎯 Sipas strategjisë',
    'admin_top_traders': '🏆 Traderët më të mirë',
    'admin_user_report': '👤 Raport përdoruesi',
    'admin_view_report': '📊 Shiko raportin',
    'admin_view_user': '👤 Karta e përdoruesit',
    'btn_check_again': '🔄 Check',
    'payment_session_expired': '❌ Sesioni i pagesës skadoi. Ju lutemi filloni përsëri.',
    'payment_ton_not_configured': '❌ Pagesat TON nuk janë të konfiguruara.',
    'payment_verifying': '⏳ Duke verifikuar pagesën...',
    'stats_fibonacci': '📐 Fibonacci',

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

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ Bilanc ELC i pamjaftueshëm.

Bilanci juaj: {balance} ELC
E nevojshme: {required} ELC

Rimbushni portofolin për të vazhduar.''',
    'wallet_address': '''📍 Adresa: `{address}`''',
    'wallet_balance': '''💰 *Portofoli Juaj ELC*

◈ Bilanci: *{balance} ELC*
📈 Në Staking: *{staked} ELC*
🎁 Shpërblime në Pritje: *{rewards} ELC*

💵 Vlera Totale: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« Prapa''',
    'wallet_btn_deposit': '''📥 Depozitoni''',
    'wallet_btn_history': '''📋 Historia''',
    'wallet_btn_stake': '''📈 Staking''',
    'wallet_btn_unstake': '''📤 Terhiq nga Staking''',
    'wallet_btn_withdraw': '''📤 Terhiq''',
    'wallet_deposit_demo': '''🎁 Merrni 100 ELC (Demo)''',
    'wallet_deposit_desc': '''Dërgoni tokenë ELC në adresën e portofolit tuaj:

`{address}`

💡 *Modaliteti demo:* Klikoni më poshtë për tokenë testimi falas.''',
    'wallet_deposit_success': '''✅ U depozituan {amount} ELC me sukses!''',
    'wallet_deposit_title': '''📥 *Depozitoni ELC*''',
    'wallet_history_empty': '''Asnjë transaksion ende.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *Historia e Transaksioneve*''',
    'wallet_stake_desc': '''Bëni stake tokenët tuaj ELC për të fituar *12% APY*!

💰 Në Dispozicion: {available} ELC
📈 Aktualisht në Staking: {staked} ELC
🎁 Shpërblime në Pritje: {rewards} ELC

Shpërblime ditore • Tërheqje e menjëhershme''',
    'wallet_stake_success': '''✅ {amount} ELC u bën stake me sukses!''',
    'wallet_stake_title': '''📈 *Staking ELC*''',
    'wallet_title': '''◈ *Portofoli ELC*''',
    'wallet_unstake_success': '''✅ U terhiqën {amount} ELC + {rewards} ELC shpërblime!''',
    'wallet_withdraw_desc': '''Shënoni adresën e destinacionit dhe shumën:''',
    'wallet_withdraw_failed': '''❌ Tërheqja dështoi: {error}''',
    'wallet_withdraw_success': '''✅ U terhiqën {amount} ELC në {address}''',
    'wallet_withdraw_title': '''📤 *Tërheqja ELC*''',

    'spot_freq_hourly': '⏰ Çdo orë',

    # ─── SYNCED FROM EN (placeholders) ───
    'button_back': '← Back',
    'button_close': '✖️ Close',
    'button_refresh': '🔄 Refresh',
    'button_confirm': '✅ Confirm',
    'button_cancel': '❌ Cancel',
    'btn_confirm': '✅ Confirm',
    'btn_refresh': '🔄 Refresh',
    'btn_settings': '⚙️ Settings',
    'btn_delete': '🗑️ Delete',
    'btn_yes': '✅ Yes',
    'btn_no': '❌ No',
    'oi_entry': '''🐋 *OI* {side_emoji} *{side}*
────────────────
🪙 `{symbol}`
💰 Entry: `{price:.6f}`
🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)
🎯 TP: `{tp_price:.6f}` ({tp_pct:.2f}%)

*Accounts:*
{accounts}
{atr_info}''',
    'scryptomera_entry': '''🔮 *SCRYPTOMERA* {side_emoji} *{side}*
────────────────
🪙 `{symbol}`
💰 Entry: `{price:.6f}`
🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)
🎯 TP: `{tp_price:.6f}` ({tp_pct:.2f}%)

*Accounts:*
{accounts}
{atr_info}''',
    'scalper_entry': '''⚡ *SCALPER* {side_emoji} *{side}*
────────────────
🪙 `{symbol}`
💰 Entry: `{price:.6f}`
🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)
🎯 TP: `{tp_price:.6f}` ({tp_pct:.2f}%)

*Accounts:*
{accounts}
{atr_info}''',
    'elcaro_entry': '''🔥 *ENLIKO* {side_emoji} *{side}*
────────────────
🪙 `{symbol}`
💰 Entry: `{price:.6f}`
🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)
🎯 TP: `{tp_price:.6f}` ({tp_pct:.2f}%)

*Accounts:*
{accounts}
{atr_info}''',
    'fibonacci_entry': '''📐 *FIBONACCI* {side_emoji} *{side}*
────────────────
🪙 `{symbol}`
💰 Entry: `{price:.6f}`
🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)
🎯 TP: `{tp_price:.6f}` ({tp_pct:.2f}%)

*Accounts:*
{accounts}
{atr_info}''',
    'rsi_bb_entry': '''📊 *RSI+BB* {side_emoji} *{side}*
────────────────
🪙 `{symbol}`
💰 Entry: `{price:.6f}`
📈 RSI: `{rsi}` ({rsi_zone})
🛡️ SL: `{sl_price:.6f}` ({sl_pct:.2f}%)

*Accounts:*
{accounts}''',
    'oi_closed': '''🐋 *OI CLOSED* `{symbol}`

📌 Reason: `{reason}`
🟢 Entry: `{entry:.8f}`
🔴 Exit: `{exit:.8f}`
💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`
💸 Fee: `{fee:.4f} USDT`
💵 *Net: `{net_pnl:+.2f} USDT`*
📍 {exchange} • {market_type}''',
    'scryptomera_closed': '''🔮 *SCRYPTOMERA CLOSED* `{symbol}`

📌 Reason: `{reason}`
🟢 Entry: `{entry:.8f}`
🔴 Exit: `{exit:.8f}`
💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`
💸 Fee: `{fee:.4f} USDT`
💵 *Net: `{net_pnl:+.2f} USDT`*
📍 {exchange} • {market_type}''',
    'scalper_closed': '''⚡ *SCALPER CLOSED* `{symbol}`

📌 Reason: `{reason}`
🟢 Entry: `{entry:.8f}`
🔴 Exit: `{exit:.8f}`
💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`
💸 Fee: `{fee:.4f} USDT`
💵 *Net: `{net_pnl:+.2f} USDT`*
📍 {exchange} • {market_type}''',
    'elcaro_closed': '''🔥 *ENLIKO CLOSED* `{symbol}`

📌 Reason: `{reason}`
🟢 Entry: `{entry:.8f}`
🔴 Exit: `{exit:.8f}`
💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`
💸 Fee: `{fee:.4f} USDT`
💵 *Net: `{net_pnl:+.2f} USDT`*
📍 {exchange} • {market_type}''',
    'fibonacci_closed': '''📐 *FIBONACCI CLOSED* `{symbol}`

📌 Reason: `{reason}`
🟢 Entry: `{entry:.8f}`
🔴 Exit: `{exit:.8f}`
💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`
💸 Fee: `{fee:.4f} USDT`
💵 *Net: `{net_pnl:+.2f} USDT`*
📍 {exchange} • {market_type}''',
    'rsi_bb_closed': '''📊 *RSI+BB CLOSED* `{symbol}`

📌 Reason: `{reason}`
🟢 Entry: `{entry:.8f}`
🔴 Exit: `{exit:.8f}`
💰 Gross: `{pnl:+.2f} USDT ({pct:+.2f}%)`
💸 Fee: `{fee:.4f} USDT`
💵 *Net: `{net_pnl:+.2f} USDT`*
📍 {exchange} • {market_type}''',
    # Daily error notifications (once per 24h)
    'daily_zero_balance':          """⚠️ <b>BALANCE ALERT</b>

💰 Your <b>{account_type}</b> account has <b>$0</b>.

📊 <b>Missed signals:</b> {missed_count}

👉 Deposit funds to resume trading.""",

    'daily_api_keys_invalid':      '🔑 <b>API KEYS ISSUE</b> - Your {account_type} keys are invalid. Missed: {missed_count}. Update in /api_settings',

    'daily_connection_error':      '🌐 <b>CONNECTION ISSUE</b> - Cannot connect to {exchange} ({account_type}). Missed: {missed_count}',

    'daily_margin_exhausted':      '📊 <b>MARGIN ALERT</b> - {account_type} margin exhausted. Positions: {open_count}. Missed: {missed_count}',

    # =====================================================
    # ERROR MONITOR USER MESSAGES
    # =====================================================
    'error_insufficient_balance': '💰 Fonde të pamjaftueshme në llogarinë tuaj për të hapur pozicion. Rimbushni bilancin ose zvogëloni madhësinë e pozicionit.',
    'error_order_too_small': '📉 Madhësia e porosisë shumë e vogël (minimumi $5). Rritni Entry% ose rimbushni bilancin.',
    'error_api_key_expired': '🔑 Çelësi API ka skaduar ose është i pavlefshëm. Përditësoni çelësat API në cilësimet.',
    'error_api_key_missing': '🔑 Çelësat API nuk janë konfiguruar. Shtoni çelësat Bybit në menunë 🔗 API Keys.',
    'error_rate_limit': '⏳ Shumë kërkesa. Prisni një minutë dhe provoni përsëri.',
    'error_position_not_found': '📊 Pozicioni nuk u gjet ose është mbyllur tashmë.',
    'error_leverage_error': '⚙️ Gabim në vendosjen e levës. Provoni ta vendosni levën manualisht në bursë.',
    'error_network_error': '🌐 Problem me rrjetin. Provoni më vonë.',
    'error_sl_tp_invalid': '⚠️ Nuk mund të vendoset SL/TP: çmimi shumë afër atij aktual. Do të përditësohet në ciklin e ardhshëm.',
    'error_equity_zero': '💰 Bilanci i llogarisë suaj është zero. Rimbushni llogarinë Demo ose Real për të tregtuar.',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 Terminali',
    'exchange_mode_activated_bybit': '🟠 *Modaliteti Bybit u aktivizua*',
    'exchange_mode_activated_hl': '🔷 *Modaliteti HyperLiquid u aktivizua*',
    'error_processing_request': '⚠️ Gabim në përpunimin e kërkesës',
    'unauthorized_admin': '❌ I paautorizuar. Kjo komandë është vetëm për administratorin.',
    'error_loading_dashboard': '❌ Gabim në ngarkimin e panelit.',
    'unauthorized': '❌ I paautorizuar.',
    'processing_blockchain': '⏳ Duke përpunuar transaksionin blockchain...',
    'verifying_payment': '⏳ Duke verifikuar pagesën në blockchain TON...',
    'no_wallet_configured': '❌ Portofoli nuk është konfiguruar.',
    'use_start_menu': 'Përdorni /start për t\'u kthyer te menyja kryesore.',

    # 2FA Konfirmimi i hyrjes
    'login_approved': '✅ Hyrja u miratua!\n\nTani mund të vazhdoni në shfletues.',
    'login_denied': '❌ Hyrja u refuzua.\n\nNëse nuk ishit ju, kontrolloni cilësimet e sigurisë.',
    'login_expired': '⏰ Konfirmimi ka skaduar. Provoni përsëri.',
    'login_error': '⚠️ Gabim përpunimi. Provoni më vonë.',

    # =====================================================
    # MISSING KEYS (Added from EN - needs translation)
    # =====================================================

    'api_bybit_demo': '🎮 Bybit Demo',
    'api_bybit_real': '💎 Bybit Live',
    'api_hl_mainnet': '🌐 HyperLiquid Mainnet',
    'api_hl_testnet': '🧪 HyperLiquid Testnet',
    'api_key_missing': '❌ Not configured',
    'api_settings_header': '🔗 *Exchange API Configuration*',
    'api_settings_info': (
        'Connect your exchange API keys to enable portfolio tracking.\n\n'
        '⚠️ _Only read & trade permissions needed. Withdrawal NOT required._'
    ),
    
    'balance_demo': '🎮 Demo Account',
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
    
    'balance_empty': (
        '📊 *Account Balance*\n\n'
        '💰 No funds detected in this account.\n\n'
        '_Tip: Transfer funds to your exchange account to start tracking._'
    ),
    
    'balance_error': '❌ Unable to fetch balance. Check API configuration.',
    'balance_mainnet': '🌐 Mainnet',
    'balance_margin_used': 'Used Margin',
    'balance_real': '💎 Live Account',
    'balance_testnet': '🧪 Testnet',
    'balance_title': '💰 *Account Balance*',
    'balance_today_pnl': 'Today P/L',
    'balance_unrealized': 'Unrealized P/L',
    'balance_week_pnl': '7-Day P/L',
    'btn_bybit_demo': '🎮 Demo',

    # =====================================================
    # MISSING KEYS (Added from EN - needs translation)
    # =====================================================

    'btn_bybit_real': '💎 Live',
    'btn_cancel_all': '❌ Cancel All',
    'btn_cancel_order': '❌ Cancel Order',
    'btn_close_pos': '❌ Close',
    'btn_hl_mainnet': '🌐 Mainnet',
    'btn_hl_testnet': '🧪 Testnet',
    'btn_modify_tpsl': '⚙️ TP/SL',
    'button_ai_bots': '🎯 Strategies',
    'button_help': '❓ Help',
    'button_language': '🌍 Language',
    'button_portfolio': '💼 Portfolio',
    'button_premium': '💎 Premium',
    'button_screener': '📈 Screener',
    'close_position_confirm': (
        '⚠️ *Close Position?*\n\n'
        '📊 {symbol} {side}\n'
        '💰 P/L: {pnl:+.2f} USDT ({pnl_pct:+.2f}%)\n\n'
        '_This action cannot be undone._'
    ),
    
    'disclaimer_accept_btn': '✅ I Understand & Accept',
    'disclaimer_accepted_msg': (
        '✅ *Disclaimer Accepted*\n\n'
        'You have acknowledged that:\n'
        '• This is an educational platform\n'
        '• You are responsible for all trading decisions\n'
        '• Past performance does not guarantee future results\n\n'
        'Welcome to Enliko Trading Tools!'
    ),
    'disclaimer_decline_btn': '❌ I Decline',
    'disclaimer_declined_msg': (
        '❌ *Disclaimer Declined*\n\n'
        'You must accept the disclaimer to use Enliko Trading Tools.\n\n'
        'If you change your mind, use /start to begin again.'
    ),
    
    # =====================================================
    # MAIN MENU BUTTONS
    # =====================================================
    
    'exchange_bybit': '🟠 Bybit',
    'exchange_header': '🔄 *Select Exchange*',
    'exchange_hyperliquid': '🔷 HyperLiquid',
    'exchange_selected': '✅ {exchange} selected.',
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
    
    'execution_failed': '❌ Order failed: {error}',
    'execution_header': '📊 *Order Execution*',
    'execution_success': (
        '✅ *Order Executed*\n\n'
        '📊 {symbol} {side}\n'
        '💰 Entry: {entry:.6f}\n'
        '📦 Size: {size}\n'
        '⚡ Leverage: {leverage}x\n\n'
        '🔻 SL: {sl_price:.6f}\n'
        '🔺 TP: {tp_price:.6f}'
    ),
    
    'hl_reset_settings': '🔄 Reset to Bybit',
    'hl_settings': 'HyperLiquid',
    'hl_trading_enabled': 'HyperLiquid Enabled',
    'manual_long': '🟢 LONG',
    'manual_order_confirm': (
        '⚠️ *Confirm Order*\n\n'
        '📊 {symbol} {side}\n'
        '💰 Amount: {amount} USDT\n\n'
        '⚠️ _Trading involves risk._\n'
        '_You are responsible for this decision._'
    ),
    
    'manual_order_failed': '❌ Order failed: {error}',
    'manual_order_header': '📝 *Manual Order*',
    'manual_order_success': '✅ Order placed: {symbol} {side}',
    'manual_short': '🔴 SHORT',
    'market_btc': '₿ BTC: {price} ({change:+.2f}%)',
    'market_eth': 'Ξ ETH: {price} ({change:+.2f}%)',
    'market_fear_greed': '📊 Fear & Greed: {value}',
    'market_header': '📊 *Market Overview*',
    'market_last_update': '🕐 Updated: {time}',
    'market_total_cap': '💰 Total Cap: ${cap}',
    'order_cancelled': '✅ Order cancelled.',
    'order_card': (
        '📋 *{symbol}*\n'
        '├ Type: `{order_type}`\n'
        '├ Side: `{side}`\n'
        '├ Price: `{price:.6f}`\n'
        '├ Qty: `{qty}`\n'
        '└ Status: `{status}`'
    ),
    
    'orders_cancelled_all': '✅ All orders cancelled.',
    'orders_empty': '📭 No open orders.',
    'orders_header': '📋 *Open Orders*',
    'orders_pending': '⏳ Pending Limit Orders',
    'portfolio_header': '💼 *Portfolio Overview*',
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
    'positions_empty': '📭 No open positions.',
    'positions_page': 'Page {current}/{total}',
    'signal_header': '📊 *Market Analysis*',
    'spot_dca_disabled': '❌ Spot DCA Disabled',
    'spot_dca_enabled': '✅ Spot DCA Enabled',
    'spot_header': '💹 *Spot Trading*',
    'stats_disclaimer': '⚠️ _Past performance does not guarantee future results._',
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
    

    # [AUTO-ADDED FROM EN]
    'elc_min_convert': '❌ Minimum 10 ELC required for conversion',
    'elc_min_stake': '❌ Minimum 1 ELC required for staking',
    'grid_cancelled': '❌ Orders Cancelled: {count}',
    'grid_failed': '❌ Failed to stop grid: {error}',
    'grid_invalid_format': '❌ Invalid format. Please enter: low_price high_price grid_count investment',
    'grid_invalid_input': '❌ Invalid input. Please enter numbers.',
    'grid_investment': '💵 Investment: ${amount:.2f}',
    'grid_levels': '🔢 Levels: {count}',
    'grid_min_10': '❌ Minimum investment is 10 USDT',
    'grid_orders_placed': '📊 Orders placed: {count}',
    'grid_range': '📈 Range: ${low:.2f} - ${high:.2f}',
    'grid_setup': '⏳ Setting up {coin} grid...',
    'grid_started': '✅ {coin} Grid Bot Started!',
    'grid_step': '📍 Grid step: ${step:.4f}',
    'spot_auto_disabled': '❌ Auto DCA disabled',
    'spot_auto_enabled': '✅ Auto DCA enabled',
    'spot_gain_max': '❌ Maximum gain trigger is 10000%',
    'spot_gain_min': '❌ Minimum gain trigger is 1%',
    'spot_invalid_amount': '❌ Invalid amount. Please enter a number.',
    'spot_invalid_pct': '❌ Invalid number. Please enter a valid percentage.',
    'spot_invalid_price': '❌ Invalid price. Please enter a number.',
    'spot_min_5': '❌ Minimum amount is 5 USDT',
    'spot_no_balance': '❌ No spot balance found',
    'spot_no_coins': '❌ No coins to sell',
    'spot_not_enabled': '❌ Spot trading is not enabled. Enable it in API Settings first.',
    'spot_sell_max': '❌ Maximum sell amount is 100%',
    'spot_sell_min': '❌ Minimum sell amount is 1%',
    'strategy_invalid': '❌ Invalid strategy',

    # === AUTO-SYNCED FROM EN (need translation) ===
    "app_login_approved": "✅ <b>Login confirmed!</b>\n\nYou can continue in the app.",
    "app_login_error": "⚠️ Processing error. Please try later.",
    "app_login_expired": "⏰ Login request expired. Please try again.",
    "app_login_prompt": "🔐 <b>Login to Enliko App</b>\n\nClick the button below to login to iOS or Android app.\nLink is valid for 5 minutes.\n\n⚠️ Do not share this link with anyone!",
    "app_login_rejected": "❌ <b>Login rejected</b>\n\nIf this wasn't you, we recommend checking your security settings.",
    "atr_disabled_restored": "🔄 <b>ATR Disabled</b>\n\n📊 {symbol}\n🛡️ SL restored: {sl_price:.4f}\n🎯 TP restored: {tp_price:.4f}",
    "basic_bybit_only": "⚠️ *Basic Plan Limitation*\n\nBasic plan supports Bybit only.\nHyperLiquid is available on Pro plan.\n\n👉 /subscribe — Upgrade to Pro",
    "btn_check_payment": "✅ Check Payment",
    "btn_copy_address": "📋 Copy Address",
    "btn_new_currency": "🔄 Different Currency",
    "btn_retry": "🔄 Retry",
    "button_coins": "🪙 Coins",
    "button_elcaro": "🎯 Elcaro",
    "button_fibonacci": "📐 Fibonacci",
    "button_indicators": "📊 Indicators",
    "button_limit_only": "📝 Limit Only",
    "button_scalper": "⚡ Scalper",
    "button_scryptomera": "🔮 Scryptomera",
    "button_support": "📞 Support",
    "button_toggle_oi": "📊 OI",
    "button_toggle_rsi_bb": "📈 RSI/BB",
    "button_update_tpsl": "🎯 TP/SL",
    "checking_payment": "Checking payment status...",
    "creating_payment": "⏳ Creating payment invoice...",
    "crypto_creating_invoice": "⏳ Creating payment invoice...",
    "crypto_payment_confirmed": "✅ *Payment Confirmed!*\n\nYour subscription has been activated.\nThank you for using Enliko!",
    "crypto_payment_confirming": "⏳ Payment detected, waiting for confirmations...",
    "crypto_payment_error": "❌ Failed to create payment: {error}",
    "crypto_payment_expired": "❌ Payment expired. Please create a new payment.",
    "crypto_payment_instructions": "💳 *Crypto Payment*\n\n📦 *Plan:* {plan}\n⏰ *Period:* {period}\n💰 *Amount:* {amount_crypto:.6f} {currency}\n📍 *Network:* {network}\n\n📋 *Send exactly this amount to:*\n`{address}`\n\n⚠️ *Important:*\n• Send EXACTLY the amount shown\n• Use the correct network ({network})\n• Payment expires in 30 minutes\n\n🆔 Payment ID: `{payment_id}`",
    "crypto_payment_invoice": "💳 *Crypto Payment Invoice*\n\n📦 *Plan:* {plan}\n⏰ *Duration:* {duration}\n💰 *Amount:* {amount}\n🔗 *Network:* {network}\n\n📋 *Payment Address:*\n`{address}`\n\n⏱ *Expires in:* 60 minutes\n\n⚠️ Send exact amount to this address.\nAfter payment, click Check to verify.\n\n🚫 *All cryptocurrency payments are final and non-refundable.*",
    "crypto_payment_pending": "⏳ Payment not yet received. Please complete the transfer.",
    "crypto_select_currency": "💳 *Crypto Payment*\n\n📦 *Plan:* {plan}\n⏰ *Duration:* {duration}\n💰 *Price:* ${price:.2f} USD\n\nSelect payment currency:",
    "global_settings_removed": "⚠️ *Global Settings Removed*\n\nPlease use per-strategy Long/Short settings instead.\n\nEach strategy now has its own Entry%, SL%, TP%, ATR settings.",
    "invalid_plan": "Invalid plan or duration",
    "license_granted_notification": "🎉 Congratulations!\n\nYou have been granted a **{plan}** subscription for **{days} days**!\n\n📅 Valid until: {end_date}\n\nThank you for using Enliko!",
    "main_menu_hint": "\n\nSelect an option from the menu below:",
    "partial_tp_notification": "✂️ <b>Partial TP Step {step}</b>\n\n📊 {symbol}\n📉 Closed: {close_pct:.0f}% ({close_qty})\n📈 Profit: +{profit_pct:.2f}%\n💰 PnL: ~${pnl:.2f}",
    "payment_creation_failed": "❌ Failed to create payment. Please try again.",
    "payment_error": "❌ Payment service error. Please try again later.\n\nError: {error}",
    "spot_advanced_header": "⚙️ *Advanced Spot Features*",
    "spot_auto_rebalance": "⚖️ Auto Rebalance - Threshold: {threshold}%",
    "spot_dca_crash_boost": "🚨 Crash Boost - 3x buy when price drops >15%",
    "spot_dca_dip_buy": "📉 Dip Buying - Only buy on significant dips",
    "spot_dca_fear_greed": "😱 Fear & Greed - Buy more during extreme fear",
    "spot_dca_fixed": "📊 Fixed DCA - Same amount at regular intervals",
    "spot_dca_momentum": "🚀 Momentum - Buy more in uptrends",
    "spot_dca_rsi": "📐 RSI Smart - Buy more when RSI < 30",
    "spot_dca_strategy_header": "📈 *DCA Strategies*",
    "spot_dca_strategy_select": "🎯 Select DCA strategy:",
    "spot_dca_value_avg": "📈 Value Averaging - Buy more when price drops",
    "spot_limit_dca": "🎯 Limit DCA - Offset: -{offset}%",
    "spot_performance_current": "💰 Current Value: ${amount:.2f}",
    "spot_performance_header": "📊 *Spot Performance*",
    "spot_performance_holdings": "📦 Holdings: {count} coins",
    "spot_performance_invested": "💵 Total Invested: ${amount:.2f}",
    "spot_performance_pnl": "📈 Unrealized PnL: {pnl:+.2f} ({pct:+.2f}%)",
    "spot_portfolio_ai": "🤖 AI & Data (FET, RNDR, TAO)",
    "spot_portfolio_blue_chip": "💎 Blue Chips (BTC, ETH, BNB, SOL)",
    "spot_portfolio_btc": "₿ BTC Only",
    "spot_portfolio_custom": "⚙️ Custom Portfolio",
    "spot_portfolio_defi": "🏦 DeFi (UNI, AAVE, MKR, LINK)",
    "spot_portfolio_eth_btc": "💰 ETH + BTC",
    "spot_portfolio_gaming": "🎮 Gaming (AXS, SAND, MANA)",
    "spot_portfolio_header": "📊 *Spot Portfolios*",
    "spot_portfolio_infra": "🔧 Infrastructure (LINK, GRT, FIL)",
    "spot_portfolio_l1": "⚔️ L1 Killers (SOL, AVAX, NEAR)",
    "spot_portfolio_layer2": "⚡ Layer 2 (MATIC, ARB, OP)",
    "spot_portfolio_meme": "🐕 Memecoins (DOGE, SHIB, PEPE)",
    "spot_portfolio_rwa": "🏛️ RWA (ONDO, MKR, SNX)",
    "spot_portfolio_select": "📁 Select a portfolio preset:",
    "spot_profit_lock": "🔒 Profit Lock - Sell {pct}% when +{trigger}%",
    "spot_tp_aggressive": "🦁 Aggressive - Hold for bigger gains",
    "spot_tp_balanced": "⚖️ Balanced - Moderate gains",
    "spot_tp_conservative": "🐢 Conservative - Small gains, frequent sells",
    "spot_tp_header": "🎯 *Take Profit Profiles*",
    "spot_tp_moonbag": "🌙 Moonbag - Keep 25% for moonshots",
    "spot_tp_profile_select": "💰 Select TP profile:",
    "spot_trailing_tp": "📉 Trailing TP - Activation: +{act}%, Trail: {trail}%",
    # === Auto-added missing keys from EN ===
    'admin_reports_menu': '📊 *Reports*',
    'button_spot': '💹 Spot',
    'payment_ton_desc': 'TON payments are currently unavailable.',
    'position_closed_error': '⚠️ {symbol} closed but log failed: {error}',
    'spot_btn_buy': '💰 Buy Now',
    'spot_btn_holdings': '💎 Holdings',
    'spot_btn_rebalance': '⚖️ Rebalance',
    'spot_btn_sell': '💸 Sell Menu',
    'spot_btn_settings': '⚙️ Settings',
    'wallet_deposit_desc': 'Send ELC tokens to:\n\n`{address}`',
    'wallet_history_item': '{type_emoji} {type}: {amount:+.2f} ELC\n   {date}',


    # Daily Digest
    'digest_title': '📊 Raporti Ditor',
    'digest_detailed_title': '📋 Raporti i Detajuar',
    'digest_date_format': '%d %B %Y',
    'digest_filter_all': '🌍 Të gjitha bursat',
    'digest_no_trades': '📭 Nuk ka transaksione',
    'digest_no_trades_hint': 'Provoni një kombinim tjetër.',
    'digest_total_pnl': 'PnL Total',
    'digest_statistics': 'Statistika',
    'digest_trades': 'Transaksione',
    'digest_wins_losses': 'Fitime/Humbje',
    'digest_win_rate': 'Shkalla e suksesit',
    'digest_avg_pnl': 'PnL Mesatar',
    'digest_best_trade': 'Transaksioni më i mirë',
    'digest_worst_trade': 'Transaksioni më i keq',
    'digest_keep_improving': 'Vazhdo të përmirësohesh! 💪',
    'digest_vibe_amazing': 'Ditë e mrekullueshme!',
    'digest_vibe_nice': 'Punë e mirë!',
    'digest_vibe_breakeven': 'Ditë neutrale',
    'digest_vibe_small_loss': 'Humbje e vogël',
    'digest_vibe_tough': 'Ditë e vështirë',
    'digest_btn_all': 'Të gjitha',
    'digest_btn_bybit': '🟠 Bybit',
    'digest_btn_hl': '🔷 HL',
    'digest_btn_demo': '🧪 Demo',
    'digest_btn_real': '💼 Real',
    'digest_btn_testnet': '🧪 Testnet',
    'digest_btn_mainnet': '🌐 Mainnet',
    'digest_btn_detailed': '📋 Detaje',
    'digest_btn_close': '❌ Mbyll',
    'digest_btn_back': '◀️ Kthehu',
    'digest_by_exchange': 'Sipas bursës',
    'digest_by_strategy': 'Sipas strategjisë',
    'digest_top_symbols': 'Top Simbole',
    'digest_filter_bybit': '🟠 Bybit',
    'digest_filter_hl': '🔷 HyperLiquid',
    'digest_filter_demo': '🧪 Demo',
    'digest_filter_real': '💼 Real',
    'digest_filter_testnet': '🧪 Testnet',
    'digest_filter_mainnet': '🌐 Mainnet',
    'stats_testnet': '🧪 Testnet',
    'stats_mainnet': '🌐 Mainnet',
    'trades_title': 'Trade History',
    'trades_list_btn': 'Trade List',
    'trades_page': 'Page',
    'trades_total': 'trades',
    'trades_empty': 'No trades found for this filter.',
    'trades_to_stats': 'Statistics',
}
