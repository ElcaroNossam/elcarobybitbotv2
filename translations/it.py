# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu
    'welcome':                     '👋 Ciao! Scegli un’azione:',
    'guide_caption':               '📚 Guida Utente del Bot di Trading\n\nLeggi questa guida per imparare a configurare le strategie e usare il bot in modo efficace.',
    'privacy_caption':             '📜 Informativa sulla Privacy & Termini di Utilizzo\n\nSi prega di leggere attentamente questo documento.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 Segreto',
    'button_api_settings':         '🔑 API',
    'button_balance':              '💰 Saldo USDT',
    'button_orders':               '📜 I miei ordini',
    'button_positions':            '📊 Posizioni',
    'button_percent':              '🎚 % per trade',
    'button_coins':                '💠 Gruppo coin',
    'button_market':               '📈 Mercato',
    'button_manual_order':         '✋ Ordine manuale',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ Annulla ordine',
    'button_limit_only':           '🎯 Solo Limit',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_settings':             '⚙️ Impostazioni',
    'button_indicators':           '💡 Indicatori',
    'button_support':              '🆘 Supporto',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 Il modo TP/SL è ora: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Percentuale fissa',

    # Limits
    'limit_positions_exceeded':    '🚫 Limite posizioni aperte superato ({max})',
    'limit_limit_orders_exceeded': '🚫 Limite ordini Limit superato ({max})',

    # Languages
    'select_language':             'Seleziona lingua:',
    'language_set':                'Lingua impostata su:',
    'lang_en':                     'English',
    'lang_it':                     'Italiano',

    # Manual order
    'order_type_prompt':           'Seleziona tipo di ordine:',
    'limit_order_format': (
        "Inserisci i parametri dell’ordine Limit:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "dove SIDE = LONG o SHORT\n"
        "Esempio: `BTCUSDT LONG 20000 0.1`\n\n"
        "Per annullare invia ❌ Annulla ordine"
    ),
    'market_order_format': (
        "Inserisci i parametri dell’ordine Market:\n"
        "`SYMBOL SIDE QTY`\n"
        "dove SIDE = LONG o SHORT\n"
        "Esempio: `BTCUSDT SHORT 0.1`\n\n"
        "Per annullare invia ❌ Annulla ordine"
    ),
    'order_success':               '✅ Ordine creato con successo!',
    'order_create_error':          '❌ Impossibile creare l’ordine: {msg}',
    'order_fail_leverage':         (
        "❌ Ordine non creato: leva troppo alta sul tuo conto Bybit per questa dimensione.\n"
        "Riduci la leva nelle impostazioni Bybit."
    ),
    'order_parse_error':           '❌ Errore di parsing: {error}',
    'price_error_min':             '❌ Errore prezzo: deve essere ≥{min}',
    'price_error_step':            '❌ Errore prezzo: deve essere multiplo di {step}',
    'qty_error_min':               '❌ Errore quantità: deve essere ≥{min}',
    'qty_error_step':              '❌ Errore quantità: deve essere multiplo di {step}',

    # Loading…
    'loader':                      '⏳ Raccolta dati…',

    # Market command
    'market_status_heading':       '*Stato del mercato:*',
    'market_dominance_header':    'Top Coin per Dominanza',
    'market_total_header':        'Capitalizzazione Totale',
    'market_indices_header':      'Indici di Mercato',
    'usdt_dominance':              'Dominanza USDT',
    'btc_dominance':               'Dominanza BTC',
    'dominance_rising':            '↑ in aumento',
    'dominance_falling':           '↓ in calo',
    'dominance_stable':            '↔️ stabile',
    'dominance_unknown':           '❔ nessun dato',
    'btc_price':                   'Prezzo BTC',
    'last_24h':                    'nelle ultime 24 h',
    'alt_signal_label':            'Segnale altcoin',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Ultime notizie (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'Prezzo di esecuzione per la chiusura non trovato',

    # /account
    'account_balance':             '💰 Saldo USDT: `{balance:.2f}`',
    'account_realized_header':     '📈 *PnL realizzato:*',
    'account_realized_day':        '  • Oggi  : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 giorni: `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *PnL non realizzato:*',
    'account_unreal_total':        '  • Totale: `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % di IM: `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Le tue impostazioni:*',
    'config_percent':              '• 🎚 % per trade     : `{percent}%`',
    'config_coins':                '• 💠 Coin            : `{coins}`',
    'config_limit_only':           '• 🎯 Ordini Limit    : {state}',
    'config_atr_mode':             '• 🏧 SL con ATR      : {atr}',
    'config_trade_oi':             '• 📊 Trading OI      : {oi}',
    'config_trade_rsi_bb':         '• 📈 Trading RSI+BB  : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%             : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%             : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 Nessun ordine aperto',
    'open_orders_header':          '*📒 Ordini aperti:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Lato : `{side}`\n"
        "   • Quant.: `{qty}`\n"
        "   • Prezzo: `{price}`\n"
        "   • ID   : `{id}`"
    ),
    'open_orders_error':           '❌ Errore nel recupero ordini: {error}',

    # Manual coin selection
    'enter_coins':                 "Inserisci simboli separati da virgola, es.:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Coin selezionate: {coins}',

    # Positions
    'no_positions':                '🚫 Nessuna posizione aperta',
    'positions_header':            '📊 Le tue posizioni aperte:',
    'position_item':               (
        "— Posizione #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • Dimensione       : {size}\n"
        "  • Prezzo d’ingresso: {avg:.8f}\n"
        "  • Prezzo mark      : {mark:.8f}\n"
        "  • Liquidazione     : {liq}\n"
        "  • Margine iniziale : {im:.2f}\n"
        "  • Margine di manten.: {mm:.2f}\n"
        "  • Saldo posizione  : {pm:.2f}\n"
        "  • Take Profit      : {tp}\n"
        "  • Stop Loss        : {sl}\n"
        "  • PnL non real.    : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'positions_overall':           'PnL non realizzato totale: {pnl:+.2f} ({pct:+.2f}%)',

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
    'set_percent_prompt':          'Inserisci la percentuale del saldo per trade (es. 2.5):',
    'percent_set_success':         '✅ % per trade impostato: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Solo ordini Limit: {state}',
    'feature_limit_only':          'Solo Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Indicatori Elcaro*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. Trend adattivo',
    'indicator_4':                 '4. Regressione dinamica',

    # Support
    'support_prompt':              '✉️ Hai bisogno di aiuto? Clicca sotto:',
    'support_button':              'Contatta il supporto',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 Nessuna posizione aperta',
    'update_tpsl_prompt':          'Inserisci SYMBOL TP SL, es.:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Formato non valido. Usa: SYMBOL TP SL\nEs.: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Inserisci la tua Bybit API Key:',
    'api_saved':                   '✅ API Key salvata',
    'enter_secret':                'Inserisci il Bybit API Secret:',
    'secret_saved':                '✅ API Secret salvato',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ Inserisci valore TP%',
    'tp_set_success':              '✅ TP% impostato: {pct}%',
    'enter_sl':                    '❌ Inserisci valore SL%',
    'sl_set_success':              '✅ SL% impostato: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: richiede 4 argomenti (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: richiede 3 argomenti (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE deve essere LONG o SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ API Key/Secret non impostati',
    'bybit_invalid_response':      '❌ Risposta Bybit non valida',
    'bybit_error':                 '❌ Errore Bybit {path}: {data}',

    # Auto notifications
    'new_position':                '🚀 Nuova posizione {symbol} @ {entry:.6f}, size={size}',
    'sl_auto_set':                 '🛑 SL impostato automaticamente: {price:.6f}',
    'auto_close_position':         '⏱ Posizione {symbol} (TF={tf}) aperta > {tf} e in perdita, chiusa automaticamente.',
    'position_closed': (
        '🔔 Posizione {symbol} chiusa per *{reason}*:\n'
        '• Strategy: `{strategy}`\n'
        '• Ingresso: `{entry:.8f}`\n'
        '• Uscita : `{exit:.8f}`\n'
        '• PnL    : `{pnl:+.2f} USDT ({pct:+.2f}%)`'
    ),

    # Entries & errors
    'oi_limit_entry':              '🟡 Ingresso Limit OI {symbol} @ {price:.6f}',
    'oi_limit_error':              '❌ Errore ingresso Limit: {msg}',
    'oi_market_entry':             '🚀 Ingresso Market OI {symbol} @ {price:.6f}',
    'oi_market_error':             '❌ Errore ingresso Market: {msg}',

    'rsi_bb_limit_entry':          '🟡 Ingresso Limit RSI+BB {symbol} @ {price:.6f}',
    'rsi_bb_market_entry':         '✅ Market RSI+BB {symbol} @ {price:.6f}',
    'rsi_bb_market_error':         '❌ Errore Market: {msg}',

    'oi_analysis':                 '📊 *Analisi OI {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 Scryptomera Limit {symbol} @ {price:.6f}',
    'bitk_limit_error':            '❌ Errore Scryptomera Limit: {msg}',
    'bitk_market_entry':           '🔮 Scryptomera Market {symbol} @ {price:.6f}',
    'bitk_market_error':           '❌ Errore Scryptomera Market: {msg}',

    # Admin panel
    'admin_panel':                 '👑 Pannello admin:',
    'admin_pause':                 '⏸️ Trading e notifiche in pausa per tutti.',
    'admin_resume':                '▶️ Trading e notifiche ripresi per tutti.',
    'admin_closed':                '✅ Chiuse in totale {count} {type}.',
    'admin_canceled_limits':       '✅ Annullati {count} ordini Limit.',

    # Coin groups
    'select_coin_group':           'Seleziona gruppo coin:',
    'group_all':                   'ALL',
    'group_top100':                'TOP100',
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ Gruppo coin impostato: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *Analisi RSI+BB*\n'
        '• Prezzo: `{price:.6f}`\n'
        '• RSI   : `{rsi:.1f}` ({zone})\n'
        '• BB superiore: `{bb_hi:.4f}`\n'
        '• BB inferiore: `{bb_lo:.4f}`\n\n'
        '*Ingresso MARKET {side} via RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'Ipervenduto (<30)',
    'rsi_zone_overbought':         'Ipercomprato (>70)',
    'rsi_zone_neutral':            'Neutro (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ TP/SL non valido per LONG.\n'
        'Prezzo attuale: {current:.2f}\n'
        'Atteso: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ TP/SL non valido per SHORT.\n'
        'Prezzo attuale: {current:.2f}\n'
        'Atteso: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 Non hai posizioni aperte su {symbol}',
    'tpsl_set_success':            '✅ TP={tp:.2f} e SL={sl:.2f} impostati per {symbol}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Lingua',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Modo stop: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ Ordine Limit su {symbol} eseguito @ {price}',
    'limit_order_cancelled':       '⚠️ Ordine Limit su {symbol} (ID: {order_id}) annullato.',
    'fixed_sl_tp':                 '✅ {symbol}: SL a {sl}, TP a {tp}',
    'tp_part':                     ', TP impostato a {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL a {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL a {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP inizializzati a {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL spostato a BE a {entry}',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP aggiornati a {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Posizione {symbol} chiusa ma registrazione fallita: {error}\n'
        'Contatta il supporto.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Percentuale fissa',

    # System notices
    'db_quarantine_notice':        '⚠️ Log temporaneamente sospesi. Modalità silenziosa per 1 ora.',

    # Fallback
    'fallback':                    '❓ Usa i pulsanti del menu.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 Sei bloccato.',
    'invite_only': '🔒 Accesso solo su invito. Attendi l’approvazione dell’admin.',
    'need_terms': '⚠️ Accetta prima i termini: /terms',
    'please_confirm': 'Conferma per favore:',
    'terms_ok': '✅ Grazie! Termini accettati.',
    'terms_declined': '❌ Termini rifiutati. Accesso chiuso. Puoi tornare con /terms.',
    'usage_approve': 'Uso: /approve <user_id>',
    'usage_ban': 'Uso: /ban <user_id>',
    'not_allowed': 'Non consentito',
    'bad_payload': 'Dati non validi',
    'unknown_action': 'Azione sconosciuta',

    'title': 'Nuovo utente',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Nome: {name}\n'
        '• Username: {uname}\n'
        '• Lingua: {lang}\n'
        '• Consentito: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve': '✅ Approva',
    'btn_ban': '⛔️ Ban',
    'admin_notify_fail': 'Impossibile notificare l’admin: {e}',
    'moderation_approved': '✅ Approvato: {target}',
    'moderation_banned': '⛔️ Bannato: {target}',
    'approved_user_dm': '✅ Accesso approvato. Premi /start.',
    'banned_user_dm': '🚫 Sei bloccato.',

    'users_not_found': '😕 Nessun utente trovato.',
    'users_page_info': '📄 Pagina {page}/{pages} — totale: {total}',
    'user_card_html': (
        '<b>👤 Utente</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Nome: {full_name}\n'
        '• Username: {uname}\n'
        '• Lingua: <code>{lang}</code>\n'
        '• Consentito: {allowed}\n'
        '• Bannato: {banned}\n'
        '• Termini: {terms}\n'
        '• % per trade: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 Lista nera',
    'btn_delete_user': '🗑 Elimina dal DB',
    'btn_prev': '⬅️ Indietro',
    'btn_next': '➡️ Avanti',
    'nav_caption': '🧭 Navigazione:',
    'bad_page': 'Pagina non valida.',
    'admin_user_delete_fail': '❌ Impossibile eliminare {target}: {error}',
    'admin_user_deleted': '🗑 Utente {target} eliminato dal DB.',
    'user_access_approved': '✅ Accesso approvato. Premi /start.',

    'admin_pause_all': '⏸️ Pausa per tutti',
    'admin_resume_all': '▶️ Riprendi',
    'admin_close_longs': '🔒 Chiudi tutti i LONG',
    'admin_close_shorts': '🔓 Chiudi tutti gli SHORT',
    'admin_cancel_limits': '❌ Elimina ordini limit',
    'admin_users': '👥 Utenti',
    'admin_pause_notice': '⏸️ Trading e notifiche in pausa per tutti.',
    'admin_resume_notice': '▶️ Trading e notifiche ripresi per tutti.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ Chiusi in totale {count} {type}.',
    'admin_canceled_limits_total': '✅ Annullati {count} ordini limit.',

    'terms_btn_accept': '✅ Accetto',
    'terms_btn_decline': '❌ Rifiuto',

    'emoji_long': '🟢',
    'emoji_short': '🔴',
    'emoji_neutral': '⚪️',

    # Scalper Strategy
    'button_scalper':                '🎯 Scalper',
    'button_elcaro':                 '🔥 Elcaro',
    'button_wyckoff':                '📐 Wyckoff',
    'config_trade_scalper':          '🎯 Scalper: {state}',
    'config_trade_elcaro':           '🔥 Elcaro: {state}',
    'config_trade_wyckoff':          '📐 Wyckoff: {state}',

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
    'api_test_success':            'Connessione riuscita!',
    'api_test_no_keys':            'Chiavi API non impostate',
    'api_test_set_keys':           'Per favore, imposta prima API Key e Secret.',
    'api_test_failed':             'Connessione fallita',
    'api_test_error':              'Errore',
    'api_test_check_keys':         'Per favore, verifica le tue credenziali API.',
    'api_test_status':             'Stato',
    'api_test_connected':          'Connesso',
    'balance_wallet':              'Saldo portafoglio',
    'balance_equity':              'Patrimonio',
    'balance_available':           'Disponibile',
    'api_missing_notice':          "⚠️ Non hai configurato le chiavi API dell'exchange. Per favore, aggiungi la tua API key e il secret nelle impostazioni (pulsanti 🔑 API e 🔒 Secret), altrimenti il bot non potrà fare trading per te.",
    'elcaro_ai_info':              '🤖 *Trading basato sull\'IA*',

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
    'strat_mode_global':           '🌐 Globale',
    'strat_mode_demo':             '🧪 Demo',
    'strat_mode_real':             '💰 Reale',
    'strat_mode_both':             '🔄 Entrambi',
    'strat_mode_changed':          '✅ Modalità trading {strategy}: {mode}',

    'feature_scalper':               'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':            '🔥 Elcaro limit-entry {symbol} @ {price:.6f}',
    'elcaro_limit_error':            '❌ Elcaro limit-entry error: {msg}',
    'elcaro_market_entry':           '🚀 Elcaro market {symbol} @ {price:.6f}',
    'elcaro_market_error':           '❌ Elcaro market error: {msg}',
    'elcaro_market_ok':              '🔥 Elcaro: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'elcaro_analysis':               'Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':                'Elcaro',

    # Wyckoff (Fibonacci Extension)
    'wyckoff_limit_entry':           '📐 Wyckoff limit-entry {symbol} @ {price:.6f}',
    'wyckoff_limit_error':           '❌ Wyckoff limit-entry error: {msg}',
    'wyckoff_market_entry':          '🚀 Wyckoff market {symbol} @ {price:.6f}',
    'wyckoff_market_error':          '❌ Wyckoff market error: {msg}',
    'wyckoff_market_ok':             '📐 Wyckoff: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'wyckoff_analysis':              'Wyckoff: {side} @ {price}',
    'feature_wyckoff':               'Wyckoff',

    'scalper_limit_entry':           'Scalper: ordine limit {symbol} @ {price}',
    'scalper_limit_error':           'Scalper errore limit: {msg}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper errore: {msg}',

    # Strategy Settings
    'button_strategy_settings':      '⚙️ Impostazioni strategie',
    'strategy_settings_header':      '⚙️ *Impostazioni strategie*',
    'strategy_param_header':         '⚙️ *Impostazioni {name}*',
    'using_global':                  'Impostazioni globali',
    'global_default':                'Globale',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_wyckoff':                 '📐 Wyckoff',
    'dca_settings':                  '⚙️ Impostazioni DCA',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA Fase 1 %',
    'dca_leg2':                      '📉 DCA Fase 2 %',
    'param_percent':                 '📊 Entrata %',
    'param_sl':                      '🔻 Stop-Loss %',
    'param_tp':                      '🔺 Take-Profit %',
    'param_reset':                   '🔄 Ripristina a globale',
    'btn_close':                     '❌ Chiudi',
    'prompt_entry_pct':              'Inserisci % entrata (rischio per trade):',
    'prompt_sl_pct':                 'Inserisci % Stop-Loss:',
    'prompt_tp_pct':                 'Inserisci % Take-Profit:',
    'prompt_atr_periods':            'Inserisci periodi ATR (es: 7):',
    'prompt_atr_mult':               'Inserisci moltiplicatore ATR per SL trailing (es: 1.0):',
    'prompt_atr_trigger':            'Inserisci % attivazione ATR (es: 2.0):',
    'prompt_dca_leg1':               'Inserisci % DCA Fase 1 (es: 10):',
    'prompt_dca_leg2':               'Inserisci % DCA Fase 2 (es: 25):',
    'settings_reset':                'Impostazioni ripristinate a globale',
    'strat_setting_saved':           '✅ {name} {param} impostato a {value}',
    'dca_setting_saved':             '✅ DCA {leg} impostato a {value}%',
    'invalid_number':                '❌ Numero non valido. Inserisci un valore tra 0 e 100.',
    'dca_10pct':                     'DCA −{pct}%: accumulo {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: accumulo {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: Fase1=-{dca1}%, Fase2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 Periodi ATR',
    'param_atr_mult':                '📉 Moltiplicatore ATR (passo SL)',
    'param_atr_trigger':             '🎯 Attivazione ATR %',

    # Hardcoded strings fix
    'terms_unavailable':             'Termini di servizio non disponibili. Contattare l\'amministratore.',
    'terms_confirm_prompt':          'Per favore conferma:',
    'your_id':                       'Il tuo ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Errore: {msg}',

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
    'stats_strategy_settings':       'Impostazioni strategia',
    'settings_entry_pct':            'Ingresso',
    'settings_leverage':             'Leva',
    'settings_trading_mode':         'Modalità',
    'settings_direction':            'Direzione',
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
    'elcaro_ai_note': '🤖 *L\'IA fa il lavoro per te!*',
    'elcaro_ai_params_header': 'I seguenti sono analizzati da ogni segnale:',
    'elcaro_ai_params_list': '• SL% • TP% • ATR • Leva • Timeframe',

    # Leverage settings
    'param_leverage': '⚡ Leva',
    'prompt_leverage': 'Inserisci la leva (1-100):',
    'auto_default': 'Auto',

    # Elcaro AI
    'elcaro_ai_desc': '_Tutti i parametri vengono analizzati automaticamente dai segnali AI:_',

    # Scalper entries
    'scalper_market_entry': '🚀 Scalper market {symbol} @ {price:.6f}',
    'scalper_analysis': 'Scalper: {side} @ {price}',

    # Scryptomera feature
    'feature_scryptomera': 'Scryptomera',

    # Limit Ladder
    'limit_ladder': '📉 Scala limite',
    'limit_ladder_header': '📉 *Impostazioni scala limite*',
    'limit_ladder_settings': '⚙️ Impostazioni scala',
    'ladder_count': 'Numero ordini',
    'ladder_info': "_Ordini limite sotto l'ingresso per DCA. Ogni ordine ha una % di distanza dall'ingresso e una % del deposito._",
    'prompt_ladder_pct_entry': "📉 Inserisci % sotto il prezzo di ingresso per l'ordine {idx}:",
    'prompt_ladder_pct_deposit': "💰 Inserisci % del deposito per l'ordine {idx}:",
    'ladder_order_saved': '✅ Ordine {idx} salvato: -{pct_entry}% @ {pct_deposit}% deposito',
    'ladder_orders_placed': '📉 {count} ordini limite piazzati per {symbol}',
    
    # Spot Trading Mode
    'spot_trading_mode': 'Modalità trading',
    'spot_btn_mode': 'Modalità',
    
    # Stats PnL
    'stats_realized_pnl': 'Realizzato',
    'stats_unrealized_pnl': 'Non realizzato',
    'stats_combined_pnl': 'Combinato',
    'stats_spot': '💹 Spot',
    'stats_spot_title': 'Statistiche Spot DCA',
    'stats_spot_config': 'Configurazione',
    'stats_spot_holdings': 'Posizioni',
    'stats_spot_summary': 'Riepilogo',
    'stats_spot_current_value': 'Valore attuale',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    'no_license': '⚠️ È necessario un abbonamento attivo per utilizzare questa funzione.\n\nUsa /subscribe per acquistare una licenza.',
    'no_license_trading': '⚠️ È necessario un abbonamento attivo per fare trading.\n\nUsa /subscribe per acquistare una licenza.',
    'license_required': '⚠️ Questa funzione richiede un abbonamento {required}.\n\nUsa /subscribe per aggiornare.',
    'trial_demo_only': '⚠️ La licenza di prova permette solo trading demo.\n\nPassa a Premium o Basic per il trading reale: /subscribe',
    'basic_strategy_limit': '⚠️ La licenza Basic su account reale permette solo: {strategies}\n\nPassa a Premium per tutte le strategie: /subscribe',
    
    'subscribe_menu_header': '💎 *Piani di Abbonamento*',
    'subscribe_menu_info': 'Scegli il tuo piano per sbloccare le funzionalità di trading:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Prova (Gratis)',
    'btn_enter_promo': '🎟 Codice Promo',
    'btn_my_subscription': '📋 Il Mio Abbonamento',
    
    'premium_title': '💎 *PIANO PREMIUM*',
    'premium_desc': '''✅ Accesso completo a tutte le funzionalità
✅ Tutte e 5 le strategie: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ Trading Reale + Demo
✅ Supporto prioritario
✅ SL/TP dinamico basato su ATR
✅ Scala limite DCA
✅ Tutti gli aggiornamenti futuri''',
    'premium_1m': '💎 1 Mese — {price}⭐',
    'premium_3m': '💎 3 Mesi — {price}⭐ (-15%)',
    'premium_6m': '💎 6 Mesi — {price}⭐ (-25%)',
    'premium_12m': '💎 12 Mesi — {price}⭐ (-35%)',
    
    'basic_title': '🥈 *PIANO BASIC*',
    'basic_desc': '''✅ Accesso completo all'account demo
✅ Account reale: tutte le strategie
✅ OI, RSI+BB, Elcaro, Scryptomera, Scalper, Wyckoff
✅ Supporto standard
✅ SL/TP dinamico basato su ATR''',
    'basic_1m': '🥈 1 Mese — {price}⭐',
    
    'trial_title': '🎁 *PIANO DI PROVA (GRATUITO)*',
    'trial_desc': '''✅ Accesso completo all'account demo
✅ Tutte e 5 le strategie su demo
❌ Trading reale non disponibile
⏰ Durata: 7 giorni
🎁 Solo una volta''',
    'trial_activate': '🎁 Attiva Prova Gratuita',
    'trial_already_used': '⚠️ Hai già utilizzato la prova gratuita.',
    'trial_activated': '🎉 Prova attivata! Hai 7 giorni di accesso demo completo.',
    
    'payment_select_method': '💳 *Seleziona Metodo di Pagamento*',
    'btn_pay_stars': '⭐ Telegram Stars',
    'btn_pay_ton': '💎 TON',
    'payment_stars_title': '⭐ Pagamento via Telegram Stars',
    'payment_stars_desc': 'Ti verranno addebitati {amount}⭐ per {plan} ({period}).',
    'payment_ton_title': '💎 Pagamento via TON',
    'payment_ton_desc': '''Invia esattamente *{amount} TON* a:

`{wallet}`

Dopo il pagamento, clicca il pulsante sotto per verificare.''',
    'btn_verify_ton': '✅ Ho Pagato — Verifica',
    'payment_processing': '⏳ Elaborazione pagamento...',
    'payment_success': '🎉 Pagamento riuscito!\n\n{plan} attivato fino al {expires}.',
    'payment_failed': '❌ Pagamento fallito: {error}',
    
    'my_subscription_header': '📋 *Il Mio Abbonamento*',
    'my_subscription_active': '''📋 *Piano Attuale:* {plan}
⏰ *Scade:* {expires}
📅 *Giorni Rimasti:* {days}''',
    'my_subscription_none': '❌ Nessun abbonamento attivo.\n\nUsa /subscribe per acquistare un piano.',
    'my_subscription_history': '📜 *Cronologia Pagamenti:*',
    'subscription_expiring_soon': '⚠️ Il tuo abbonamento {plan} scade tra {days} giorni!\n\nRinnova ora: /subscribe',
    
    'promo_enter': '🎟 Inserisci il tuo codice promo:',
    'promo_success': '🎉 Codice promo applicato!\n\n{plan} attivato per {days} giorni.',
    'promo_invalid': '❌ Codice promo non valido.',
    'promo_expired': '❌ Questo codice promo è scaduto.',
    'promo_used': '❌ Questo codice promo è già stato utilizzato.',
    'promo_already_used': '❌ Hai già utilizzato questo codice promo.',
    
    'admin_license_menu': '🔑 *Gestione Licenze*',
    'admin_btn_grant_license': '🎁 Concedi Licenza',
    'admin_btn_view_licenses': '📋 Vedi Licenze',
    'admin_btn_create_promo': '🎟 Crea Promo',
    'admin_btn_view_promos': '📋 Vedi Promos',
    'admin_btn_expiring_soon': '⚠️ In Scadenza',
    'admin_grant_select_type': 'Seleziona tipo licenza:',
    'admin_grant_select_period': 'Seleziona periodo:',
    'admin_grant_enter_user': 'Inserisci ID utente:',
    'admin_license_granted': '✅ {plan} concesso all\'utente {uid} per {days} giorni.',
    'admin_license_extended': '✅ Licenza estesa di {days} giorni per l\'utente {uid}.',
    'admin_license_revoked': '✅ Licenza revocata per l\'utente {uid}.',
    'admin_promo_created': '✅ Codice promo creato: {code}\nTipo: {type}\nGiorni: {days}\nUsi max: {max}',

    'admin_users_management': '👥 Utenti',
    'admin_licenses': '🔑 Licenze',
    'admin_search_user': '🔍 Trova Utente',
    'admin_users_menu': '👥 *Gestione Utenti*\n\nSeleziona filtro o cerca:',
    'admin_all_users': '👥 Tutti gli Utenti',
    'admin_active_users': '✅ Attivi',
    'admin_banned_users': '🚫 Bannati',
    'admin_no_license': '❌ Senza Licenza',
    'admin_no_users_found': 'Nessun utente trovato.',
    'admin_enter_user_id': '🔍 Inserisci ID utente per cercare:',
    'admin_user_found': '✅ Utente {uid} trovato!',
    'admin_user_not_found': '❌ Utente {uid} non trovato.',
    'admin_invalid_user_id': '❌ ID utente non valido. Inserisci un numero.',
    'admin_view_card': '👤 Vedi Scheda',
    
    'admin_user_card': '''👤 *Scheda Utente*

📋 *ID:* `{uid}`
{status_emoji} *Stato:* {status}
📝 *Termini:* {terms}

{license_emoji} *Licenza:* {license_type}
📅 *Scade:* {license_expires}
⏳ *Giorni Rimasti:* {days_left}

🌐 *Lingua:* {lang}
📊 *Modalità Trading:* {trading_mode}
💰 *% per Trade:* {percent}%
🪙 *Monete:* {coins}

🔌 *Chiavi API:*
  Demo: {demo_api}
  Reale: {real_api}

📈 *Strategie:* {strategies}

📊 *Statistiche:*
  Posizioni: {positions}
  Trade: {trades}
  PnL: {pnl}
  Winrate: {winrate}%

💳 *Pagamenti:*
  Totale: {payments_count}
  Stars: {total_stars}⭐

📅 *Prima visita:* {first_seen}
🕐 *Ultima visita:* {last_seen}
''',
    
    'admin_btn_grant_lic': '🎁 Concedi',
    'admin_btn_extend': '⏳ Estendi',
    'admin_btn_revoke': '🚫 Revoca',
    'admin_btn_ban': '🚫 Banna',
    'admin_btn_unban': '✅ Sbanna',
    'admin_btn_approve': '✅ Approva',
    'admin_btn_message': '✉️ Messaggio',
    'admin_btn_delete': '🗑 Elimina',
    
    'admin_user_banned': 'Utente bannato!',
    'admin_user_unbanned': 'Utente sbannato!',
    'admin_user_approved': 'Utente approvato!',
    'admin_confirm_delete': '⚠️ *Conferma eliminazione*\n\nL\'utente {uid} verrà eliminato permanentemente!',
    'admin_confirm_yes': '✅ Sì, Elimina',
    'admin_confirm_no': '❌ Annulla',
    
    'admin_select_license_type': 'Seleziona tipo licenza per utente {uid}:',
    'admin_select_period': 'Seleziona periodo:',
    'admin_select_extend_days': 'Seleziona giorni da estendere per utente {uid}:',
    'admin_license_granted_short': 'Licenza concessa!',
    'admin_license_extended_short': 'Esteso di {days} giorni!',
    'admin_license_revoked_short': 'Licenza revocata!',
    
    'admin_enter_message': '✉️ Inserisci messaggio da inviare all\'utente {uid}:',
    'admin_message_sent': '✅ Messaggio inviato all\'utente {uid}!',
    'admin_message_failed': '❌ Invio messaggio fallito: {error}',
}
