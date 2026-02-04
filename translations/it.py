# -*- coding: utf-8 -*-
TEXTS = {
    # Common UI
    'loader': '⏳ Caricamento...',
    
    # Menu principale - Terminale di trading professionale
    'welcome':                     '''🔥 <b>Enliko Trading Terminal</b>

⚡ <b>&lt; 100ms</b> esecuzione
🛡️ <b>Gestione del rischio</b> integrata
💎 <b>24/7</b> trading automatizzato

Bybit • HyperLiquid • Multi-strategia''',
    'button_orders':               '📊 Ordini',
    'button_positions':            '🎯 Posizioni',
    'button_history':              '📜 Cronologia',
    'button_api_keys':             '🔑 Chiavi API',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_settings':             '⚙️ Config',

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
    'positions_header':            '📊 Le tue posizioni aperte:',

    # Position management (inline)
    'btn_close_position':          'Chiudi posizione',
    'btn_cancel':                  '❌ Annulla',
    'btn_back':                    '🔙 Indietro',
    'position_already_closed':     'Posizione già chiusa',
    'position_closed_success':     'Posizione chiusa',
    'position_close_error':        'Errore nella chiusura',

    # % per trade

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Solo ordini Limit: {state}',
    'feature_limit_only':          'Solo Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Indicatori Enliko*',
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

    # Auto notifications - BLACK RHETORIC: Excitement
    'new_position': (
        '🚀 <b>NUOVA POSIZIONE APERTA!</b>\n\n'
        '💎 {symbol} @ {entry:.6f}\n'
        '📊 Size: {size}\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>L\'IA Enliko lavora per te 24/7</i>'
    ),
    'sl_auto_set':                 '🛑 SL impostato automaticamente: {price:.6f}',
    'auto_close_position':         '⏱ Posizione {symbol} (TF={tf}) aperta > {tf} e in perdita, chiusa automaticamente.',
    'position_closed': (
        '🎯 <b>POSIZIONE CHIUSA!</b>\n\n'
        '📊 {symbol} via *{reason}*\n'
        '🤖 Strategia: `{strategy}`\n'
        '📈 Ingresso: `{entry:.8f}`\n'
        '📉 Uscita: `{exit:.8f}`\n'
        '💰 PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>I tuoi soldi lavorano mentre dormi.</i>'
    ),

    # Entries & errors - formato unificato con info complete
    'oi_limit_entry':              '📉 *OI Ingresso Limit*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit errore: {msg}',
    'oi_market_entry':             '📉 *OI Ingresso Market*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI Market errore: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Ingresso Limit*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Ingresso Market*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB Market errore: {msg}',

    'oi_analysis':                 '📊 *Analisi OI {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Ingresso Limit*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit errore: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Ingresso Market*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market errore: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>Saldo insufficiente!</b>\n\n💰 Non ci sono fondi sufficienti sul tuo account {account_type} per aprire questa posizione.\n\n<b>Soluzioni:</b>\n• Ricarica il saldo\n• Riduci la dimensione della posizione (% per trade)\n• Riduci la leva\n• Chiudi alcune posizioni aperte',
    'insufficient_balance_error_extended': '❌ <b>Saldo insufficiente!</b>\n\n📊 Strategia: <b>{strategy}</b>\n🪙 Simbolo: <b>{symbol}</b> {side}\n\n💰 Fondi insufficienti sul tuo account {account_type}.\n\n<b>Soluzioni:</b>\n• Ricarica il saldo\n• Riduci la dimensione della posizione (% per trade)\n• Riduci la leva\n• Chiudi alcune posizioni aperte',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Leva troppo alta!</b>\n\n⚙️ La tua leva configurata supera il massimo consentito per questo simbolo.\n\n<b>Massimo consentito:</b> {max_leverage}x\n\n<b>Soluzione:</b> Vai alle impostazioni della strategia e riduci la leva.',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>Limite posizione superato!</b>\n\n📊 Strategia: <b>{strategy}</b>\n🪙 Simbolo: <b>{symbol}</b>\n\n⚠️ La tua posizione supererebbe il limite massimo.\n\n<b>Soluzioni:</b>\n• Ridurre la leva\n• Ridurre la dimensione della posizione\n• Chiudere alcune posizioni',
    

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Ingresso Limit*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit errore: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Ingresso Market*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market errore: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko Ingresso Limit*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Enliko Limit errore: {msg}',
    'elcaro_market_entry':         '🔥 *Enliko Ingresso Market*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Enliko Market errore: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci Ingresso Limit*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci Limit errore: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci Ingresso Market*\n• {symbol} {side}\n• Prezzo: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci Market errore: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 Pannello admin:',
    'admin_pause':                 '⏸️ Trading e notifiche in pausa per tutti.',
    'admin_resume':                '▶️ Trading e notifiche ripresi per tutti.',
    'admin_closed':                '✅ Chiuse in totale {count} {type}.',
    'admin_canceled_limits':       '✅ Annullati {count} ordini Limit.',

    # Coin groups
    'select_coin_group':           'Seleziona gruppo coin:',
    'group_all':                   'ALL',
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
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
    'select_language':             '🌍 Seleziona la tua lingua:',
    'language_set':                '✅ Lingua impostata:',
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

    # API Settings
    'api_key_set':                 '✅ Set',
    'api_test_success':            'Connessione riuscita!',
    'api_test_failed':             'Connessione fallita',
    'balance_equity':              'Patrimonio',
    'balance_available':           'Disponibile',
    'api_missing_notice':          "⚠️ Non hai configurato le chiavi API dell'exchange. Per favore, aggiungi la tua API key e il secret nelle impostazioni (pulsanti 🔑 API e 🔒 Secret), altrimenti il bot non potrà fare trading per te.",
    'elcaro_ai_info':              '🤖 *Trading basato sull\'IA*',

    # Spot Trading
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_balance':                '💰 Spot Balance: {balance}',

    # Strategy trading mode

    # Enliko (Heatmap)

    # Fibonacci (Fibonacci Extension)

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
    'strat_elcaro':                  '🔥 Enliko',
    'strat_fibonacci':                 '📐 Fibonacci',
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

    # Break-Even settings UI
    'be_settings_header':            '🔒 *Impostazioni Break-Even*',
    'be_settings_desc':              '_Sposta SL al prezzo di ingresso quando il profitto raggiunge la % di attivazione_',
    'be_enabled_label':              '🔒 Break-Even',
    'be_trigger_label':              '🎯 Attivazione BE %',
    'prompt_be_trigger':             'Inserisci la % di attivazione Break-Even (es: 1.0):',
    'prompt_long_be_trigger':        '📈 LONG Attivazione BE %\n\nInserisci % di profitto per spostare SL all\'ingresso:',
    'prompt_short_be_trigger':       '📉 SHORT Attivazione BE %\n\nInserisci % di profitto per spostare SL all\'ingresso:',
    'param_be_trigger':              '🎯 Attivazione BE %',
    'be_moved_to_entry':             '🔒 {symbol}: SL spostato a break-even @ {entry}',
    'be_status_enabled':             '✅ BE: {trigger}%',
    'be_status_disabled':            '❌ BE: Disattivato',

    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ TP Parziale',
    'partial_tp_status_enabled':     '✅ TP Parziale attivato',
    'partial_tp_status_disabled':    '❌ TP Parziale disattivato',
    'partial_tp_step1_menu':         '✂️ *TP Parziale - Passo 1*\n\nChiudi {close}% della posizione al +{trigger}% di profitto\n\n_Seleziona parametro:_',
    'partial_tp_step2_menu':         '✂️ *TP Parziale - Passo 2*\n\nChiudi {close}% della posizione al +{trigger}% di profitto\n\n_Seleziona parametro:_',
    'trigger_pct':                   'Attivazione',
    'close_pct':                     'Chiudi',
    'prompt_long_ptp_1_trigger':     '📈 LONG Passo 1: % Attivazione\n\nInserisci % di profitto per chiudere prima parte:',
    'prompt_long_ptp_1_close':       '📈 LONG Passo 1: % Chiudere\n\nInserisci % di posizione da chiudere:',
    'prompt_long_ptp_2_trigger':     '📈 LONG Passo 2: % Attivazione\n\nInserisci % di profitto per chiudere seconda parte:',
    'prompt_long_ptp_2_close':       '📈 LONG Passo 2: % Chiudere\n\nInserisci % di posizione da chiudere:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT Passo 1: % Attivazione\n\nInserisci % di profitto per chiudere prima parte:',
    'prompt_short_ptp_1_close':      '📉 SHORT Passo 1: % Chiudere\n\nInserisci % di posizione da chiudere:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT Passo 2: % Attivazione\n\nInserisci % di profitto per chiudere seconda parte:',
    'prompt_short_ptp_2_close':      '📉 SHORT Passo 2: % Chiudere\n\nInserisci % di posizione da chiudere:',
    'partial_tp_executed':           '✂️ {symbol}: Chiuso {close}% al +{trigger}% di profitto',

    # Hardcoded strings fix
    'terms_unavailable':             'Termini di servizio non disponibili. Contattare l\'amministratore.',
    'terms_confirm_prompt':          'Per favore conferma:',
    'your_id':                       'Il tuo ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Errore: {msg}',
    'error_fetch_balance':           '❌ Errore nel recupero del saldo: {error}',
    'error_fetch_orders':            '❌ Errore nel recupero degli ordini: {error}',
    'error_occurred':                '❌ Errore: {error}',

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
    'prompt_leverage': 'Inserisci la leva (1-100):',
    'auto_default': 'Auto',

    # Enliko AI
    'elcaro_ai_desc': '_Tutti i parametri vengono analizzati automaticamente dai segnali AI:_',

    # Scalper entries

    # Scryptomera feature
    

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
    
    'no_license': '🚨 <b>ACCESSO NEGATO</b>\n\n⚠️ Mentre leggi questo, i trader Premium stanno guadagnando.\n\n💎 Sblocca il tuo potenziale: /subscribe\n\n<i>Ogni minuto di attesa = soldi persi</i>',
    'no_license_trading': '🚨 <b>TRADING BLOCCATO</b>\n\n⚠️ 847 trader stanno guadagnando ORA con Enliko.\n\n💎 Unisciti a loro: /subscribe\n\n<i>Il mercato non aspetta nessuno.</i>',
    'license_required': '⚠️ Questa funzione richiede un abbonamento {required}.\n\nUsa /subscribe per aggiornare.',
    'trial_demo_only': '⚠️ La licenza di prova permette solo trading demo.\n\nPassa a Premium o Basic per il trading reale: /subscribe',
    'basic_strategy_limit': '⚠️ La licenza Basic su account reale permette solo: {strategies}\n\nPassa a Premium per tutte le strategie: /subscribe',
    
    # Subscribe menu - BLACK RHETORIC: Exclusivity + Scarcity
    'subscribe_menu_header': '👑 *ACCESSO VIP al Circolo dei Trader d\'Elite*',
    'subscribe_menu_info': '''🔥 <b>847 trader</b> stanno già guadagnando
⚡ Esecuzione <100ms | 🛡️ 664 test di sicurezza

<i>Scegli il tuo livello di accesso:</i>''',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Prova (Gratis)',
    'btn_enter_promo': '🎟 Codice Promo',
    'btn_my_subscription': '📋 Il Mio Abbonamento',
    
    # Premium plan - BLACK RHETORIC: Authority + Social Proof
    'premium_title': '👑 *PREMIUM — La Scelta dei Vincitori*',
    'premium_desc': '''✅ Accesso completo a tutte le funzionalità
✅ Tutte e 5 le strategie: OI, RSI+BB, Scryptomera, Scalper, Enliko
✅ Trading Reale + Demo
✅ Supporto prioritario
✅ SL/TP dinamico basato su ATR
✅ Scala limite DCA
✅ Tutti gli aggiornamenti futuri''',
    'premium_1m': '💎 1 Mese — {price} ELC',
    'premium_3m': '💎 3 Mesi — {price} ELC (-10%)',
    'premium_6m': '💎 6 Mesi — {price} ELC (-20%)',
    'premium_12m': '💎 12 Mesi — {price} ELC (-30%)',
    
    'basic_title': '🥈 *PIANO BASIC*',
    'basic_desc': '''✅ Accesso completo all'account demo
✅ Account reale: OI, RSI+BB, Scryptomera, Scalper
❌ Enliko, Fibonacci, Spot — solo Premium
✅ Supporto standard
✅ SL/TP dinamico basato su ATR''',
    'basic_1m': '🥈 1 Mese — {price} ELC',
    
    # Trial plan - BLACK RHETORIC: FOMO + Urgency
    'trial_title': '🎁 *PROVA GRATUITA — Offerta Limitata!*',
    'trial_desc': '''✅ Accesso completo all'account demo
✅ Tutte e 5 le strategie su demo
❌ Trading reale non disponibile
⏰ Durata: 7 giorni
🎁 Solo una volta''',
    'trial_activate': '🎁 Attiva Prova Gratuita',
    'trial_already_used': '⚠️ Hai già utilizzato la prova gratuita.',
    'trial_activated': '🎉 Prova attivata! Hai 7 giorni di accesso demo completo.',
    
    'payment_select_method': '💳 *Seleziona Metodo di Pagamento*',
    'btn_pay_elc': '◈ Enliko Coin (ELC)',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' Pagamento via ELC',
    'payment_elc_desc': 'Ti verranno addebitati {amount} ELC per {plan} ({period}).',
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
  ELC: {total_elc}

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

    # Auto-synced missing keys
    'admin_all_payments': '📜 Tutti i pagamenti',
    'admin_demo_stats': '🎮 Stats demo',
    'admin_enter_user_for_report': '👤 Inserisci ID utente per report dettagliato:',
    'admin_generating_report': '📊 Generazione report per utente {uid}...',
    'admin_global_stats': '📊 Stats globali',
    'admin_no_payments_found': 'Nessun pagamento trovato.',
    'admin_payments': '💳 Pagamenti',
    'admin_payments_menu': '💳 *Gestione pagamenti*',
    'admin_real_stats': '💰 Stats reali',
    'admin_reports': '📊 Report',
    'admin_reports_menu': '''📊 *Report e analisi*

Seleziona tipo di report:''',
    'admin_strategy_breakdown': '🎯 Per strategia',
    'admin_top_traders': '🏆 Migliori trader',
    'admin_user_report': '👤 Report utente',
    'admin_view_report': '📊 Visualizza report',
    'admin_view_user': '👤 Scheda utente',
    'btn_check_again': '🔄 Controlla di nuovo',
    'payment_session_expired': '❌ Sessione di pagamento scaduta. Per favore ricomincia.',
    'payment_ton_not_configured': '❌ I pagamenti TON non sono configurati.',
    'payment_verifying': '⏳ Verifica pagamento...',
    'stats_fibonacci': '📐 Fibonacci',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "Trading HyperLiquid",
    "hl_reset_settings": "🔄 Ripristina impostazioni Bybit",

    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ Annullato.',
    'entry_pct_range_error': '❌ La % di ingresso deve essere tra 0.1 e 100.',
    'hl_no_history': '📭 Nessuna cronologia di trading su HyperLiquid.',
    'hl_no_orders': '📭 Nessun ordine aperto su HyperLiquid.',
    'hl_no_positions': '📭 Nessuna posizione aperta su HyperLiquid.',
    'hl_setup_cancelled': '❌ Configurazione HyperLiquid annullata.',
    'invalid_amount': '❌ Numero non valido. Inserisci un importo valido.',
    'leverage_range_error': '❌ La leva deve essere tra 1 e 100.',
    'max_amount_error': "❌ L'importo massimo è 100.000 USDT",
    'min_amount_error': "❌ L'importo minimo è 1 USDT",
    'sl_tp_range_error': '❌ SL/TP % deve essere tra 0.1 e 500.',

    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 Attiva DCA',
    'btn_ignore': '🔇 Ignora',
    'dca_already_enabled': '✅ DCA già attivato!\n\n📊 <b>{symbol}</b>\nIl bot acquisterà automaticamente in drawdown:\n• -10% → aggiungi\n• -25% → aggiungi\n\nQuesto aiuta a mediare il prezzo di ingresso.',
    'dca_enable_error': '❌ Errore: {error}',
    'dca_enabled_for_symbol': '✅ DCA attivato!\n\n📊 <b>{symbol}</b>\nIl bot acquisterà automaticamente in drawdown:\n• -10% → aggiungi (averaging)\n• -25% → aggiungi (averaging)\n\n⚠️ DCA richiede saldo sufficiente per ordini aggiuntivi.',
    'deep_loss_alert': '⚠️ <b>Posizione in perdita profonda!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Perdita: <code>{loss_pct:.2f}%</code>\n💰 Ingresso: <code>{entry}</code>\n📍 Attuale: <code>{mark}</code>\n\n❌ Lo stop-loss non può essere impostato sopra il prezzo di ingresso.\n\n<b>Cosa fare?</b>\n• <b>Chiudi</b> - blocca la perdita\n• <b>DCA</b> - media la posizione\n• <b>Ignora</b> - lascia così',
    'deep_loss_close_error': '❌ Errore nella chiusura della posizione: {error}',
    'deep_loss_closed': '✅ Posizione {symbol} chiusa.\n\nPerdita bloccata. A volte è meglio accettare una piccola perdita che sperare in un inversione.',
    'deep_loss_ignored': '🔇 Capito, posizione {symbol} lasciata invariata.\n\n⚠️ Ricorda: senza stop-loss, il rischio di perdite è illimitato.\nPuoi chiudere la posizione manualmente tramite /positions',
    'fibonacci_desc': '_Ingresso, SL, TP - dai livelli Fibonacci nel segnale._',
    'fibonacci_info': '📐 *Strategia Fibonacci Extension*',
    'prompt_min_quality': 'Inserisci qualità minima % (0-100):',

    # Hardcore trading phrase
    'hardcore_mode': '💀 *MODALITÀ HARDCORE*: Nessuna pietà, nessun rimpianto. Solo profitto o morte! 🔥',

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ Saldo ELC insufficiente.

Il tuo saldo: {balance} ELC
Richiesto: {required} ELC

Ricarica il portafoglio per continuare.''',
    'wallet_address': '''📍 Indirizzo: `{address}`''',
    'wallet_balance': '''💰 *Il Tuo Portafoglio ELC*

◈ Saldo: *{balance} ELC*
📈 In Staking: *{staked} ELC*
🎁 Ricompense in Attesa: *{rewards} ELC*

💵 Valore Totale: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« Indietro''',
    'wallet_btn_deposit': '''📥 Deposita''',
    'wallet_btn_history': '''📋 Cronologia''',
    'wallet_btn_stake': '''📈 Staking''',
    'wallet_btn_unstake': '''📤 Rimuovi Staking''',
    'wallet_btn_withdraw': '''📤 Preleva''',
    'wallet_deposit_demo': '''🎁 Ottieni 100 ELC (Demo)''',
    'wallet_deposit_desc': '''Invia token ELC al tuo indirizzo del portafoglio:

`{address}`

💡 *Modalità demo:* Clicca sotto per token di test gratuiti.''',
    'wallet_deposit_success': '''✅ Depositati {amount} ELC con successo!''',
    'wallet_deposit_title': '''📥 *Deposita ELC*''',
    'wallet_history_empty': '''Nessuna transazione.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *Cronologia Transazioni*''',
    'wallet_stake_desc': '''Metti in staking i tuoi ELC per guadagnare *12% APY*!

💰 Disponibili: {available} ELC
📈 Attualmente in Staking: {staked} ELC
🎁 Ricompense in Attesa: {rewards} ELC

Ricompense giornaliere • Unstaking istantaneo''',
    'wallet_stake_success': '''✅ {amount} ELC messi in staking con successo!''',
    'wallet_stake_title': '''📈 *Staking ELC*''',
    'wallet_title': '''◈ *Portafoglio ELC*''',
    'wallet_unstake_success': '''✅ Rimossi dallo staking {amount} ELC + {rewards} ELC di ricompense!''',
    'wallet_withdraw_desc': '''Inserisci indirizzo di destinazione e importo:''',
    'wallet_withdraw_failed': '''❌ Prelievo fallito: {error}''',
    'wallet_withdraw_success': '''✅ Prelevati {amount} ELC a {address}''',
    'wallet_withdraw_title': '''📤 *Preleva ELC*''',

    'spot_freq_hourly': '⏰ Ogni ora',

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
    'error_insufficient_balance': '💰 Fondi insufficienti sul tuo account per aprire una posizione. Ricarica il saldo o riduci la dimensione della posizione.',
    'error_order_too_small': '📉 Dimensione ordine troppo piccola (minimo $5). Aumenta Entry% o ricarica il saldo.',
    'error_api_key_expired': '🔑 Chiave API scaduta o non valida. Aggiorna le tue chiavi API nelle impostazioni.',
    'error_api_key_missing': '🔑 Chiavi API non configurate. Aggiungi le chiavi Bybit nel menu 🔗 API Keys.',
    'error_rate_limit': '⏳ Troppe richieste. Attendi un minuto e riprova.',
    'error_position_not_found': '📊 Posizione non trovata o già chiusa.',
    'error_leverage_error': '⚙️ Errore nell\'impostazione della leva. Prova a impostarla manualmente sull\'exchange.',
    'error_network_error': '🌐 Problema di rete. Riprova più tardi.',
    'error_sl_tp_invalid': '⚠️ Impossibile impostare SL/TP: prezzo troppo vicino a quello attuale. Sarà aggiornato al prossimo ciclo.',
    'error_equity_zero': '💰 Il saldo del tuo account è zero. Ricarica l\'account Demo o Real per fare trading.',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 Terminale',
    'exchange_mode_activated_bybit': '🟠 *Modalità Bybit attivata*',
    'exchange_mode_activated_hl': '🔷 *Modalità HyperLiquid attivata*',
    'error_processing_request': '⚠️ Errore nell\'elaborazione della richiesta',
    'unauthorized_admin': '❌ Non autorizzato. Questo comando è solo per l\'amministratore.',
    'error_loading_dashboard': '❌ Errore nel caricamento della dashboard.',
    'unauthorized': '❌ Non autorizzato.',
    'processing_blockchain': '⏳ Elaborazione transazione blockchain...',
    'verifying_payment': '⏳ Verifica pagamento sulla blockchain TON...',
    'no_wallet_configured': '❌ Nessun wallet configurato.',
    'use_start_menu': 'Usa /start per tornare al menu principale.',

    # 2FA Conferma accesso
    'login_approved': '✅ Accesso approvato!\n\nOra puoi continuare nel browser.',
    'login_denied': '❌ Accesso negato.\n\nSe non eri tu, verifica le impostazioni di sicurezza.',
    'login_expired': '⏰ Conferma scaduta. Riprova.',
    'login_error': '⚠️ Errore di elaborazione. Riprova più tardi.',

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
    'btn_bybit_real': '💎 Live',
    'btn_cancel_all': '❌ Cancel All',
    'btn_cancel_order': '❌ Cancel Order',
    'btn_close_pos': '❌ Close',
    'btn_hl_mainnet': '🌐 Mainnet',
    'btn_hl_testnet': '🧪 Testnet',
    'btn_modify_tpsl': '⚙️ TP/SL',
    'button_ai_bots': '🎯 Strategies',
    'button_api_bybit': '🟠 Bybit API',
    'button_api_hl': '🔷 HL API',
    'button_help': '❓ Help',
    'button_language': '🌍 Language',
    'button_portfolio': '💼 Portfolio',
    'button_premium': '💎 Premium',
    'button_screener': '📈 Screener',
    'button_switch_exchange': '🔄 Switch Exchange',
    'button_webapp': '🌐 WebApp',
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
    
    'disclaimer_execution': (
        '⚠️ By proceeding, you acknowledge:\n'
        '• You are responsible for all trading decisions\n'
        '• This is an educational tool, not financial advice\n'
        '• You understand the risks of cryptocurrency trading\n'
        '• Past performance does not guarantee future results'
    ),
    
    # Disclaimer acceptance buttons and messages
    'disclaimer_short': '⚠️ _Educational tools only. Not financial advice. Trading involves risk._',
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
    
    'welcome_back': (
        '📊 *Enliko Trading Tools*\n\n'
        '⚠️ _Educational platform. Not financial advice._\n\n'
        '👇 Select an option:'
    ),
    
    # =====================================================
    # LEGAL DISCLAIMERS (REQUIRED)
    # =====================================================
    

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
}
