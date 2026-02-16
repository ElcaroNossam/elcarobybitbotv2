# -*- coding: utf-8 -*-
TEXTS = {
    # Common UI
    'loader': '⏳ Laden...',
    
    # Hauptmenü - Professionelles Trading-Terminal
    'welcome':                     '''🔥 <b>Enliko Trading Terminal</b>

⚡ <b>&lt; 100ms</b> Ausführung
🛡️ <b>Risikomanagement</b> integriert
💎 <b>24/7</b> automatisierter Handel

Bybit • HyperLiquid • Multi-Strategie''',
    
    # ═══════════════════════════════════════════════════════════════════
    # MODERN MENU BUTTONS - Stylish & Persuasive (DE)
    # ═══════════════════════════════════════════════════════════════════
    'button_orders':               '📊 Aufträge',
    'button_positions':            '🎯 Positionen',

    'button_balance': '💎 Portfolio',
    'button_market': '📈 Markt',
    'button_strategies': '🤖 AI Bots',
    'button_subscribe': '🤝 UNTERSTÜTZEN',
    'button_terminal': '💻 Terminal',
    'button_terminal': '💻 Terminal',
    'button_history':              '📜 Verlauf',
    'button_api_keys':             '🔗 Börse',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_settings':             '⚙️ Konfig',

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
    'positions_header':            '📊 Deine offenen Positionen:',

    # Position management (inline)
    'btn_close_position':          'Position schließen',
    'btn_cancel':                  '❌ Abbrechen',
    'btn_back':                    '🔙 Zurück',
    'position_already_closed':     'Position bereits geschlossen',
    'position_closed_success':     'Position geschlossen',
    'position_close_error':        'Fehler beim Schließen',

    # % per trade

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Nur Limit-Orders: {state}',
    'feature_limit_only':          'Nur Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Enliko-Indikatoren*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. Adaptiver Trend',
    'indicator_4':                 '4. Dynamische Regression',

    # Support
    'support_prompt':              '✉️ Hilfe nötig? Klicke unten:',
    'support_button':              'Support kontaktieren',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 Keine offenen Positionen',
    'update_tpsl_prompt':          'Gib SYMBOL TP SL ein, z. B.:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Ungültiges Format. Verwende: SYMBOL TP SL\nz. B.: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Gib deinen Bybit API-Key ein:',
    'api_saved':                   '✅ API-Key gespeichert',
    'enter_secret':                'Gib dein Bybit API-Secret ein:',
    'secret_saved':                '✅ API-Secret gespeichert',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ Gib einen TP%-Wert ein',
    'tp_set_success':              '✅ TP% gesetzt: {pct}%',
    'enter_sl':                    '❌ Gib einen SL%-Wert ein',
    'sl_set_success':              '✅ SL% gesetzt: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: benötigt 4 Argumente (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: benötigt 3 Argumente (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE muss LONG oder SHORT sein',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ API-Key/Secret nicht gesetzt',
    'bybit_invalid_response':      '❌ Ungültige Antwort von Bybit',
    'bybit_error':                 '❌ Bybit-Fehler {path}: {data}',

    # Auto notifications - BLACK RHETORIC: Achievement + FOMO
    'new_position': '''💎 *TRADE AUSGEFÜHRT!*
🎯 {symbol} | {side} @ `{entry:.6f}`
📊 Größe: `{size}`
📍 {exchange} • {market_type}

_Enliko KI erkannte die Chance. Du bist dabei._''',
    'sl_auto_set':                 '🛡️ *Kapital geschützt!* SL @ `{price:.6f}`\n_Intelligentes Risikomanagement aktiviert._',
    'auto_close_position':         '⚡ Position {symbol} automatisch geschlossen — _KI schützt dein Kapital_',
    'position_closed': '''🏆 *TRADE ABGESCHLOSSEN!*
🎯 {symbol} • {reason}
📍 Strategie: `{strategy}`

📈 Entry: `{entry:.8f}`
📉 Exit: `{exit:.8f}`
💰 *PnL: {pnl:+.2f} USDT ({pct:+.2f}%)*

_Jeder Trade ist ein Schritt zur finanziellen Freiheit._
📍 {exchange} • {market_type}''',

    # Entries & errors - einheitliches Format mit vollständigen Infos
    'oi_limit_entry':              '📉 *OI Limit Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit Fehler: {msg}',
    'oi_market_entry':             '📉 *OI Market Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI Market Fehler: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Limit Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Market Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB Market Fehler: {msg}',

    'oi_analysis':                 '📊 *OI-Analyse {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Limit Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit Fehler: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Market Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market Fehler: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error - BLACK RHETORIC: Problem + Solution + Urgency
    'insufficient_balance_error':  '''🚨 <b>KAPITAL BLOCKIERT!</b>

💰 Deine {account_type} Margin ist in Positionen gebunden.

<b>🧠 Smart Money Move:</b>
• Verlustpositionen schließen — _schnell Verluste begrenzen_
• Entry % reduzieren — _Risikomanagement ist entscheidend_
• Hebel senken — _Profis nutzen max 5-10x_

<i>Der Markt wartet auf niemanden. Befreie dein Kapital JETZT.</i>

👉 /positions — <b>Übernimm die Kontrolle</b>''',
    'insufficient_balance_error_extended': '''🚨 <b>EINSTIEG BLOCKIERT!</b>

📊 Strategie: <b>{strategy}</b> versuchte einzusteigen
🪙 {symbol} {side}

💰 Nicht genug FREIE Margin auf {account_type}.

<b>🧠 Was Top-Trader tun:</b>
• Verlustreiche Positionen sofort schließen
• Positionsgröße für neue Einstiege reduzieren
• DCA-Leiter für bessere Einstiege nutzen

<i>Kapital ist deine Munition. Verschwende es nicht.</i>''',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Hebel zu hoch!</b>\n\n⚙️ Ihr konfigurierter Hebel überschreitet das Maximum für dieses Symbol.\n\n<b>Maximal erlaubt:</b> {max_leverage}x\n\n<b>Lösung:</b> Gehen Sie zu den Strategieeinstellungen und reduzieren Sie den Hebel.',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>Positionslimit überschritten!</b>\n\n📊 Strategie: <b>{strategy}</b>\n�� Symbol: <b>{symbol}</b>\n\n⚠️ Ihre Position würde das maximale Limit überschreiten.\n\n<b>Lösungen:</b>\n• Hebel in Strategieeinstellungen reduzieren\n• Positionsgröße reduzieren\n• Offene Positionen schließen',
    

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Limit Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit Fehler: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Market Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market Fehler: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko Limit Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Enliko Limit Fehler: {msg}',
    'elcaro_market_entry':         '🔥 *Enliko Market Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Enliko Market Fehler: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci Limit Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci Limit Fehler: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci Market Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci Market Fehler: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 Admin-Panel:',
    'admin_pause':                 '⏸️ Handel & Benachrichtigungen für alle pausiert.',
    'admin_resume':                '▶️ Handel & Benachrichtigungen für alle fortgesetzt.',
    'admin_closed':                '✅ Insgesamt geschlossen: {count} {type}.',
    'admin_canceled_limits':       '✅ {count} Limit-Orders storniert.',

    # Coin groups
    'select_coin_group':           'Münzgruppe wählen:',
    'group_all':                   'ALL',
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ Münzgruppe gesetzt: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *RSI+BB-Analyse*\n'
        '• Preis: `{price:.6f}`\n'
        '• RSI : `{rsi:.1f}` ({zone})\n'
        '• BB oben : `{bb_hi:.4f}`\n'
        '• BB unten: `{bb_lo:.4f}`\n\n'
        '*MARKET-Einstieg {side} per RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'Überverkauft (<30)',
    'rsi_zone_overbought':         'Überkauft (>70)',
    'rsi_zone_neutral':            'Neutral (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ Ungültiges TP/SL für LONG.\n'
        'Aktueller Preis: {current:.2f}\n'
        'Erwartet: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ Ungültiges TP/SL für SHORT.\n'
        'Aktueller Preis: {current:.2f}\n'
        'Erwartet: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 Keine offene Position auf {symbol}',
    'tpsl_set_success':            '✅ TP={tp:.2f} und SL={sl:.2f} für {symbol} gesetzt',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Sprache',
    'select_language':             '🌍 Sprache wählen:',
    'language_set':                '✅ Sprache gesetzt auf',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Stop-Modus: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ Limit-Order für {symbol} gefüllt @ {price}',
    'limit_order_cancelled':       '⚠️ Limit-Order für {symbol} (ID: {order_id}) storniert.',
    'fixed_sl_tp':                 '✅ {symbol}: SL bei {sl}, TP bei {tp}',
    'tp_part':                     ', TP gesetzt bei {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL bei {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL bei {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP initialisiert bei {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL auf Break-Even bei {entry} verschoben',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP aktualisiert auf {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Position {symbol} geschlossen, aber Log fehlgeschlagen: {error}\n'
        'Bitte Support kontaktieren.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Fester %',

    # System notices
    'db_quarantine_notice':        '⚠️ Logs vorübergehend pausiert. Leisemodus für 1 Stunde aktiv.',

    # Fallback
    'fallback':                    '❓ Bitte nutze die Menü-Buttons.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 Du bist gesperrt.',
    'invite_only': '🔒 Zugang nur per Einladung. Bitte auf Admin-Freigabe warten.',
    'need_terms': '⚠️ Bitte zuerst die Bedingungen akzeptieren: /terms',
    'please_confirm': 'Bitte bestätigen:',
    'terms_ok': '✅ Danke! Bedingungen akzeptiert.',
    'terms_declined': '❌ Bedingungen abgelehnt. Zugriff gesperrt. Rückkehr mit /terms möglich.',
    'usage_approve': 'Verwendung: /approve <user_id>',
    'usage_ban': 'Verwendung: /ban <user_id>',
    'not_allowed': 'Nicht erlaubt',
    'bad_payload': 'Ungültige Daten',
    'unknown_action': 'Unbekannte Aktion',

    'title': 'Neuer Nutzer',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Name: {name}\n'
        '• Benutzername: {uname}\n'
        '• Sprache: {lang}\n'
        '• Erlaubt: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve': '✅ Freigeben',
    'btn_ban': '⛔️ Sperren',
    'admin_notify_fail': 'Admin konnte nicht benachrichtigt werden: {e}',
    'moderation_approved': '✅ Freigegeben: {target}',
    'moderation_banned': '⛔️ Gesperrt: {target}',
    'approved_user_dm': '✅ Zugriff freigegeben. Drücke /start.',
    'banned_user_dm': '🚫 Du bist gesperrt.',

    'users_not_found': '😕 Keine Nutzer gefunden.',
    'users_page_info': '📄 Seite {page}/{pages} — gesamt: {total}',
    'user_card_html': (
        '<b>👤 Nutzer</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Name: {full_name}\n'
        '• Benutzername: {uname}\n'
        '• Sprache: <code>{lang}</code>\n'
        '• Erlaubt: {allowed}\n'
        '• Gesperrt: {banned}\n'
        '• Bedingungen: {terms}\n'
        '• % pro Trade: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 Blacklist',
    'btn_delete_user': '🗑 Aus DB löschen',
    'btn_prev': '⬅️ Zurück',
    'btn_next': '➡️ Weiter',
    'nav_caption': '🧭 Navigation:',
    'bad_page': 'Ungültige Seite.',
    'admin_user_delete_fail': '❌ Löschen fehlgeschlagen {target}: {error}',
    'admin_user_deleted': '🗑 Nutzer {target} aus DB gelöscht.',
    'user_access_approved': '✅ Zugriff freigegeben. Drücke /start.',

    'admin_pause_all': '⏸️ Für alle pausieren',
    'admin_resume_all': '▶️ Fortsetzen',
    'admin_close_longs': '🔒 Alle LONGs schließen',
    'admin_close_shorts': '🔓 Alle SHORTs schließen',
    'admin_cancel_limits': '❌ Limitorders löschen',
    'admin_users': '👥 Nutzer',
    'admin_pause_notice': '⏸️ Handel & Benachrichtigungen für alle pausiert.',
    'admin_resume_notice': '▶️ Handel & Benachrichtigungen wieder aktiv.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ Insgesamt geschlossen: {count} {type}.',
    'admin_canceled_limits_total': '✅ {count} Limitorders storniert.',

    'terms_btn_accept': '✅ Akzeptieren',
    'terms_btn_decline': '❌ Ablehnen',

    'emoji_long': '🟢',
    'emoji_short': '🔴',
    'emoji_neutral': '⚪️',

    # Scalper Strategy

    # API Settings
    'api_key_set':                 '✅ Set',
    'api_test_success':            'Verbindung erfolgreich!',
    'api_test_failed':             'Verbindung fehlgeschlagen',
    'balance_equity':              'Eigenkapital',
    'balance_available':           'Verfügbar',
    'api_missing_notice':          '⚠️ Sie haben keine Exchange-API-Schlüssel konfiguriert. Bitte fügen Sie Ihren API-Key und Secret in den Einstellungen hinzu (🔑 API und 🔒 Secret Schaltflächen), sonst kann der Bot nicht für Sie handeln.',
    'elcaro_ai_info':              '🤖 *KI-gestützter Handel*',

    # Spot Trading
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_balance':                '💰 Spot Balance: {balance}',

    # Strategy trading mode

    # Enliko (Heatmap)

    # Fibonacci (Fibonacci Extension)

    # Strategy Settings
    'button_strategy_settings':      '⚙️ Strategie-Einstellungen',
    'strategy_settings_header':      '⚙️ *Strategie-Einstellungen*',
    'strategy_param_header':         '⚙️ *{name} Einstellungen*',
    'using_global':                  'Globale Einstellungen',
    'global_default':                'Global',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Enliko',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ DCA-Einstellungen',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA Stufe 1 %',
    'dca_leg2':                      '📉 DCA Stufe 2 %',
    'param_percent':                 '📊 Einstieg %',
    'param_sl':                      '🔻 Stop-Loss %',
    'param_tp':                      '🔺 Take-Profit %',
    'param_reset':                   '🔄 Auf Global zurücksetzen',
    'btn_close':                     '❌ Schließen',
    'prompt_entry_pct':              'Einstieg % eingeben (Risiko pro Trade):',
    'prompt_sl_pct':                 'Stop-Loss % eingeben:',
    'prompt_tp_pct':                 'Take-Profit % eingeben:',
    'prompt_atr_periods':            'ATR-Perioden eingeben (z.B. 7):',
    'prompt_atr_mult':               'ATR-Multiplikator für Trailing-SL eingeben (z.B. 1.0):',
    'prompt_atr_trigger':            'ATR-Trigger % für Trailing-Aktivierung eingeben (z.B. 2.0):',
    'prompt_dca_leg1':               'DCA Stufe 1 % eingeben (z.B. 10):',
    'prompt_dca_leg2':               'DCA Stufe 2 % eingeben (z.B. 25):',
    'settings_reset':                'Einstellungen auf Global zurückgesetzt',
    'strat_setting_saved':           '✅ {name} {param} auf {value} gesetzt',
    'dca_setting_saved':             '✅ DCA {leg} auf {value}% gesetzt',
    'invalid_number':                '❌ Ungültige Zahl. Wert zwischen 0 und 100 eingeben.',
    'dca_10pct':                     'DCA −{pct}%: Nachkauf {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: Nachkauf {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: Stufe1=-{dca1}%, Stufe2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 ATR-Perioden',
    'param_atr_mult':                '📉 ATR-Multiplikator (SL-Schritt)',
    'param_atr_trigger':             '🎯 ATR-Trigger %',
    
    # Break-Even settings UI
    'be_settings_header':            '🔒 *Break-Even Einstellungen*',
    'be_settings_desc':              '_SL auf Einstiegspreis verschieben wenn Gewinn erreicht_',
    'be_enabled_label':              '🔒 Break-Even',
    'be_trigger_label':              '🎯 BE Trigger %',
    'prompt_be_trigger':             'Break-Even Trigger % eingeben (z.B. 1.0):',
    'prompt_long_be_trigger':        '📈 LONG BE Trigger %\n\nGewinn % eingeben um SL auf Einstieg zu verschieben:',
    'prompt_short_be_trigger':       '📉 SHORT BE Trigger %\n\nGewinn % eingeben um SL auf Einstieg zu verschieben:',
    'param_be_trigger':              '🎯 BE Trigger %',
    'be_moved_to_entry':             '🔒 {symbol}: SL auf Break-Even verschoben @ {entry}',
    'be_status_enabled':             '✅ BE: {trigger}%',
    'be_status_disabled':            '❌ BE: Aus',
    
    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ Teil-TP',
    'partial_tp_status_enabled':     '✅ Teil-TP aktiviert',
    'partial_tp_status_disabled':    '❌ Teil-TP deaktiviert',
    'partial_tp_step1_menu':         '✂️ *Teil-TP - Schritt 1*\n\n{close}% der Position bei +{trigger}% Gewinn schließen\n\n_Parameter auswählen:_',
    'partial_tp_step2_menu':         '✂️ *Teil-TP - Schritt 2*\n\n{close}% der Position bei +{trigger}% Gewinn schließen\n\n_Parameter auswählen:_',
    'trigger_pct':                   'Trigger',
    'close_pct':                     'Schließen',
    'prompt_long_ptp_1_trigger':     '📈 LONG Schritt 1: Trigger %\n\nGewinn % für ersten Teil eingeben:',
    'prompt_long_ptp_1_close':       '📈 LONG Schritt 1: Schließen %\n\n% der Position zum Schließen eingeben:',
    'prompt_long_ptp_2_trigger':     '📈 LONG Schritt 2: Trigger %\n\nGewinn % für zweiten Teil eingeben:',
    'prompt_long_ptp_2_close':       '📈 LONG Schritt 2: Schließen %\n\n% der Position zum Schließen eingeben:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT Schritt 1: Trigger %\n\nGewinn % für ersten Teil eingeben:',
    'prompt_short_ptp_1_close':      '📉 SHORT Schritt 1: Schließen %\n\n% der Position zum Schließen eingeben:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT Schritt 2: Trigger %\n\nGewinn % für zweiten Teil eingeben:',
    'prompt_short_ptp_2_close':      '📉 SHORT Schritt 2: Schließen %\n\n% der Position zum Schließen eingeben:',
    'partial_tp_executed':           '✂️ {symbol}: {close}% bei +{trigger}% Gewinn geschlossen',

    # Hardcoded strings fix
    'terms_unavailable':             'Nutzungsbedingungen nicht verfügbar. Kontaktieren Sie den Administrator.',
    'terms_confirm_prompt':          'Bitte bestätigen:',
    'your_id':                       'Ihre ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Fehler: {msg}',
    'error_fetch_balance':           '❌ Fehler beim Abrufen des Guthabens: {error}',
    'error_fetch_orders':            '❌ Fehler beim Abrufen der Aufträge: {error}',
    'error_occurred':                '❌ Fehler: {error}',

    # Trading Statistics
    'button_stats':                  '📊 Statistik',
    'stats_title':                   'Handelsstatistik',
    'stats_strategy':                'Strategie',
    'stats_period':                  'Zeitraum',
    'stats_overview':                'Übersicht',
    'stats_total_trades':            'Trades gesamt',
    'stats_closed':                  'Geschlossen',
    'stats_open':                    'Offen',
    'stats_results':                 'Ergebnisse',
    'stats_winrate':                 'Gewinnrate',
    'stats_total_r':                 'Gesamt R',
    'stats_avg_r':                   'Durchschn. R',
    'stats_by_direction':            'Nach Richtung',
    'stats_long':                    'Long',
    'stats_short':                   'Short',
    'stats_pnl':                     'Gewinn/Verlust',
    'stats_gross_profit':            'Gewinn',
    'stats_gross_loss':              'Verlust',
    'stats_total_pnl':               'Gesamt P/L',
    'stats_profit_factor':           'PF',
    'stats_strategy_settings':       'Strategieeinstellungen',
    'settings_entry_pct':            'Einstieg',
    'settings_leverage':             'Hebel',
    'settings_trading_mode':         'Modus',
    'settings_direction':            'Richtung',
    'stats_all':                     '📈 Alle',
    'stats_oi':                      '📉 OI',
    'stats_rsi_bb':                  '📊 RSI+BB',
    'stats_scryptomera':             '🐱 Scryptomera',
    'stats_scalper':                 '⚡ Scalper',
    'stats_elcaro':                  '🔥 Enliko',
    'stats_period_all':              'Gesamtzeit',
    'stats_period_today':            '24h',
    'stats_period_week':             'Woche',
    'stats_period_month':            'Monat',
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

    # Coins group per strategy
    'param_coins_group': '🪙 Coins',
    'select_coins_for_strategy': '🪙 *Select coins group for {name}*',
    'group_global': '📊 Global (use common setting)',

    # Enliko AI settings

    # Leverage settings
    'param_leverage': '⚡ Hebel',
    'prompt_leverage': 'Hebel eingeben (1-100):',
    'auto_default': 'Auto',

    # Enliko AI
    'elcaro_ai_desc': '_Alle Parameter werden automatisch aus AI-Signalen geparst:_',

    # Scalper entries

    # Scryptomera feature
    

    # Limit Ladder
    'limit_ladder': '📉 Limit-Leiter',
    'limit_ladder_header': '📉 *Limit-Leiter Einstellungen*',
    'limit_ladder_settings': '⚙️ Leiter-Einstellungen',
    'ladder_count': 'Anzahl Aufträge',
    'ladder_info': 'Limitaufträge unterhalb des Einstiegs für DCA. Jeder Auftrag hat einen % Abstand vom Einstieg und einen % des Depots.',
    'prompt_ladder_pct_entry': '📉 Geben Sie % unter Einstiegspreis für Auftrag {idx} ein:',
    'prompt_ladder_pct_deposit': '💰 Geben Sie % des Depots für Auftrag {idx} ein:',
    'ladder_order_saved': '✅ Auftrag {idx} gespeichert: -{pct_entry}% @ {pct_deposit}% Depot',
    'ladder_orders_placed': '📉 {count} Limit-Aufträge für {symbol} platziert',
    
    # Spot Trading Mode
    
    # Stats PnL
    'stats_realized_pnl': 'Realisiert',
    'stats_unrealized_pnl': 'Unrealisiert',
    'stats_combined_pnl': 'Kombiniert',
    'stats_spot': '💹 Spot',
    'stats_spot_title': 'Spot DCA Statistiken',
    'stats_spot_config': 'Konfiguration',
    'stats_spot_holdings': 'Bestände',
    'stats_spot_summary': 'Zusammenfassung',
    'stats_spot_current_value': 'Aktueller Wert',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    # License status messages - BLACK RHETORIC: Loss Aversion + FOMO
    'no_license': '🤝 *Community Membership*\n\nSupport our open-source project to access\nadditional community resources.\n\n👉 /subscribe — Support the project',
    'no_license_trading': '🤝 *Community Resource*\n\nThis resource is available to community supporters.\n\n👉 /subscribe — Support the project',
    'license_required': '🔒 *Supporter Resource*\n\nThis resource requires {required} membership.\n\n👉 /subscribe — Support the project',
    'trial_demo_only': '⚠️ *Explorer Access*\n\nExplorer access is limited to demo environment.\n\n👉 /subscribe — Become a supporter',
    'basic_strategy_limit': '⚠️ *Community Tier*\n\nAvailable templates: {strategies}\n\n👉 /subscribe — Upgrade your support',
    # Subscribe menu - BLACK RHETORIC: Urgency + Authority + Exclusivity
    'subscribe_menu_header': '🤝 *Support Enliko*\n\nYour voluntary contribution helps maintain\nfree open-source community tools.\n\nChoose your support level:',
    'subscribe_menu_info': '_Select your support level:_',
    'btn_premium': '🤝 Patron',
    'btn_basic': '💚 Unterstützer',
    'btn_trial': '🆓 Entdecker (Kostenlos)',
    'btn_enter_promo': '🎟 Einladungscode',
    'btn_my_subscription': '📋 Meine Mitgliedschaft',
    # Premium plan - BLACK RHETORIC: Authority + Scarcity + Social Proof
    'premium_title': '''💎 *PREMIUM — TOTALE DOMINANZ*

_"Dieser Bot druckt buchstäblich Geld"_ — @CryptoKing''',
    'premium_desc': '*Thank you for supporting our community!*\n\nAs a patron, you receive access to:\n✅ All community analysis templates\n✅ Demo & live environments\n✅ Priority community support\n✅ ATR risk management tools\n✅ DCA configuration tools\n✅ Early access to updates\n\n⚠️ _Educational tools only. Not financial advice._',
    'premium_1m': '🤝 1 Month — {price} ELC',
    'premium_3m': '🤝 3 Months — {price} ELC',
    'premium_6m': '🤝 6 Months — {price} ELC',
    'premium_12m': '🤝 12 Months — {price} ELC',
    # Basic plan - BLACK RHETORIC: Stepping stone narrative
    'basic_title': '''🥈 *BASIC — SMARTER START*

_Perfekt zum Testen der Gewässer_''',
    'basic_desc': '*Thank you for your support!*\n\n✅ Demo + live environments\n✅ Templates: OI, RSI+BB\n✅ Bybit integration\n✅ ATR risk management tools\n\n⚠️ _Educational tools only. Not financial advice._',
    'basic_1m': '💚 1 Month — {price} ELC',
    # Trial plan - BLACK RHETORIC: Zero risk + Taste of power
    'trial_title': '''🎁 *KOSTENLOSE TESTVERSION — NULL RISIKO*

_Sehen ist Glauben_''',
    'trial_desc': '*Explore our community tools:*\n\n✅ Full demo environment\n✅ All analysis templates\n✅ 14 days access\n✅ No contribution required\n\n⚠️ _Educational tools only. Not financial advice._',
    'trial_activate': '🆓 Start Exploring',
    'trial_already_used': '⚠️ Explorer access already used. Consider supporting the project.',
    'trial_activated': '🎉 *Explorer Access Activated!*\n\n⏰ 14 days of full demo access.\n\n⚠️ _Educational tools only. Not financial advice._',
    # Payment
    'payment_select_method': '🤝 *How would you like to contribute?*',
    'btn_pay_elc': '◈ ELC',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' Zahlung via ELC',
    'payment_elc_desc': 'Ihnen werden {amount} ELC für {plan} ({period}) berechnet.',
    'payment_ton_title': '💎 Zahlung via TON',
    'payment_ton_desc': '''Senden Sie genau *{amount} TON* an:

`{wallet}`

Nach der Zahlung klicken Sie auf die Schaltfläche unten zur Verifizierung.''',
    'btn_verify_ton': '✅ Ich habe bezahlt — Verifizieren',
    'payment_processing': '⏳ ...',
    'payment_success': '🎉 Thank you for your support!\n\n{plan} access activated until {expires}.',
    'payment_failed': '❌ Contribution failed: {error}',
    # My subscription
    'my_subscription_header': '📋 *My Membership*',
    'my_subscription_active': '''📋 *Aktueller Plan:* {plan}
⏰ *Läuft ab:* {expires}
📅 *Tage übrig:* {days}''',
    'my_subscription_none': '❌ No active membership.\n\nUse /subscribe to support the project.',
    'my_subscription_history': '📜 *Zahlungshistorie:*',
    'subscription_expiring_soon': '⚠️ Ihr {plan}-Abonnement läuft in {days} Tagen ab!\n\nJetzt verlängern: /subscribe',
    
    # Promo codes
    'promo_enter': '🎟 Enter your invite code:',
    'promo_success': '🎉 Invite code applied!\n\n{plan} access for {days} days.',
    'promo_invalid': '❌ Invalid invite code.',
    'promo_expired': '❌ This invite code has expired.',
    'promo_used': '❌ This invite code has already been used.',
    'promo_already_used': '❌ You have already used this invite code.',
    # Admin license management
    'admin_license_menu': '🤝 *Membership Management*',
    'admin_btn_grant_license': '🎁 Grant Access',
    'admin_btn_view_licenses': '📋 View Members',
    'admin_btn_create_promo': '🎟 Create Invite',
    'admin_btn_view_promos': '📋 View Invites',
    'admin_btn_expiring_soon': '⚠️ Bald ablaufend',
    'admin_grant_select_type': 'Lizenztyp auswählen:',
    'admin_grant_select_period': 'Zeitraum auswählen:',
    'admin_grant_enter_user': 'Benutzer-ID eingeben:',
    'admin_license_granted': '✅ {plan} an Benutzer {uid} für {days} Tage erteilt.',
    'admin_license_extended': '✅ Lizenz um {days} Tage für Benutzer {uid} verlängert.',
    'admin_license_revoked': '✅ Lizenz für Benutzer {uid} widerrufen.',
    'admin_promo_created': '✅ Promo-Code erstellt: {code}\nTyp: {type}\nTage: {days}\nMax. Nutzungen: {max}',

    # =====================================================
    # ADMIN USER MANAGEMENT
    # =====================================================
    'admin_users_management': '👥 Benutzer',
    'admin_licenses': '🔑 Lizenzen',
    'admin_search_user': '🔍 Benutzer suchen',
    'admin_users_menu': '👥 *Benutzerverwaltung*\n\nFilter oder Suche auswählen:',
    'admin_all_users': '👥 Alle Benutzer',
    'admin_active_users': '✅ Aktive',
    'admin_banned_users': '🚫 Gesperrte',
    'admin_no_license': '❌ Ohne Lizenz',
    'admin_no_users_found': 'Keine Benutzer gefunden.',
    'admin_enter_user_id': '🔍 Benutzer-ID zur Suche eingeben:',
    'admin_user_found': '✅ Benutzer {uid} gefunden!',
    'admin_user_not_found': '❌ Benutzer {uid} nicht gefunden.',
    'admin_invalid_user_id': '❌ Ungültige Benutzer-ID. Geben Sie eine Zahl ein.',
    'admin_view_card': '👤 Karte anzeigen',
    
    # User card
    'admin_user_card': '''👤 *Benutzerkarte*

📋 *ID:* `{uid}`
{status_emoji} *Status:* {status}
📝 *Bedingungen:* {terms}

{license_emoji} *Lizenz:* {license_type}
📅 *Läuft ab:* {license_expires}
⏳ *Tage übrig:* {days_left}

🌐 *Sprache:* {lang}
📊 *Handelsmodus:* {trading_mode}
💰 *% pro Trade:* {percent}%
🪙 *Münzen:* {coins}

🔌 *API-Schlüssel:*
  Demo: {demo_api}
  Echt: {real_api}

📈 *Strategien:* {strategies}

📊 *Statistik:*
  Positionen: {positions}
  Trades: {trades}
  PnL: {pnl}
  Winrate: {winrate}%

💳 *Zahlungen:*
  Gesamt: {payments_count}
  ELC: {total_elc}

📅 *Erstes Mal gesehen:* {first_seen}
🕐 *Zuletzt gesehen:* {last_seen}
''',
    
    # User actions
    'admin_btn_grant_lic': '🎁 Erteilen',
    'admin_btn_extend': '⏳ Verlängern',
    'admin_btn_revoke': '🚫 Widerrufen',
    'admin_btn_ban': '🚫 Sperren',
    'admin_btn_unban': '✅ Entsperren',
    'admin_btn_approve': '✅ Genehmigen',
    'admin_btn_message': '✉️ Nachricht',
    'admin_btn_delete': '🗑 Löschen',
    
    'admin_user_banned': 'Benutzer gesperrt!',
    'admin_user_unbanned': 'Benutzer entsperrt!',
    'admin_user_approved': 'Benutzer genehmigt!',
    'admin_confirm_delete': '⚠️ *Löschung bestätigen*\n\nBenutzer {uid} wird dauerhaft gelöscht!',
    'admin_confirm_yes': '✅ Ja, löschen',
    'admin_confirm_no': '❌ Abbrechen',
    
    'admin_select_license_type': 'Lizenztyp für Benutzer {uid} auswählen:',
    'admin_select_period': 'Zeitraum auswählen:',
    'admin_select_extend_days': 'Tage zur Verlängerung für Benutzer {uid} auswählen:',
    'admin_license_granted_short': 'Lizenz erteilt!',
    'admin_license_extended_short': 'Um {days} Tage verlängert!',
    'admin_license_revoked_short': 'Lizenz widerrufen!',
    
    'admin_enter_message': '✉️ Nachricht an Benutzer {uid} eingeben:',
    'admin_message_sent': '✅ Nachricht an Benutzer {uid} gesendet!',
    'admin_message_failed': '❌ Nachricht konnte nicht gesendet werden: {error}',

    # Auto-synced missing keys
    'admin_all_payments': '📜 Alle Zahlungen',
    'admin_demo_stats': '🎮 Demo-Statistik',
    'admin_enter_user_for_report': '👤 Benutzer-ID für detaillierten Bericht eingeben:',
    'admin_generating_report': '📊 Bericht für Benutzer {uid} wird erstellt...',
    'admin_global_stats': '📊 Globale Statistik',
    'admin_no_payments_found': 'Keine Zahlungen gefunden.',
    'admin_payments': '💳 Zahlungen',
    'admin_payments_menu': '💳 *Zahlungsverwaltung*',
    'admin_real_stats': '💰 Echte Statistik',
    'admin_reports': '📊 Berichte',
    'admin_reports_menu': '''📊 *Berichte & Analysen*

Berichtstyp auswählen:''',
    'admin_strategy_breakdown': '🎯 Nach Strategie',
    'admin_top_traders': '🏆 Top-Trader',
    'admin_user_report': '👤 Benutzerbericht',
    'admin_view_report': '📊 Bericht anzeigen',
    'admin_view_user': '👤 Benutzerkarte',
    'btn_check_again': '🔄 Check',
    'payment_session_expired': '❌ Zahlungssitzung abgelaufen. Bitte erneut starten.',
    'payment_ton_not_configured': '❌ TON-Zahlungen sind nicht konfiguriert.',
    'payment_verifying': '⏳ Zahlung wird verifiziert...',
    'stats_fibonacci': '📐 Fibonacci',

    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "HyperLiquid Handel",
    "hl_reset_settings": "🔄 Auf Bybit-Einstellungen zurücksetzen",

    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ Abgebrochen.',
    'entry_pct_range_error': '❌ Einstiegs-% muss zwischen 0.1 und 100 liegen.',
    'hl_no_history': '📭 Keine Handelshistorie auf HyperLiquid.',
    'hl_no_orders': '📭 Keine offenen Orders auf HyperLiquid.',
    'hl_no_positions': '📭 Keine offenen Positionen auf HyperLiquid.',
    'hl_setup_cancelled': '❌ HyperLiquid-Einrichtung abgebrochen.',
    'invalid_amount': '❌ Ungültige Zahl. Bitte geben Sie einen gültigen Betrag ein.',
    'leverage_range_error': '❌ Hebel muss zwischen 1 und 100 liegen.',
    'max_amount_error': '❌ Maximalbetrag ist 100.000 USDT',
    'min_amount_error': '❌ Mindestbetrag ist 1 USDT',
    'sl_tp_range_error': '❌ SL/TP % muss zwischen 0.1 und 500 liegen.',

    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 DCA-Averaging aktivieren',
    'btn_ignore': '🔇 Ignorieren',
    'dca_already_enabled': '✅ DCA-Averaging ist bereits aktiviert!\n\n📊 <b>{symbol}</b>\nBot kauft automatisch bei Drawdown:\n• -10% → Nachkauf\n• -25% → Nachkauf\n\nDies hilft, den Einstiegspreis zu mitteln.',
    'dca_enable_error': '❌ Fehler: {error}',
    'dca_enabled_for_symbol': '✅ DCA-Averaging aktiviert!\n\n📊 <b>{symbol}</b>\nBot kauft automatisch bei Drawdown:\n• -10% → Nachkauf (Averaging)\n• -25% → Nachkauf (Averaging)\n\n⚠️ DCA benötigt ausreichend Guthaben für zusätzliche Orders.',
    'deep_loss_alert': '⚠️ <b>Position im tiefen Verlust!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Verlust: <code>{loss_pct:.2f}%</code>\n💰 Einstieg: <code>{entry}</code>\n📍 Aktuell: <code>{mark}</code>\n\n❌ Stop-Loss kann nicht über dem Einstiegspreis gesetzt werden.\n\n<b>Was tun?</b>\n• <b>Schließen</b> - Verlust realisieren\n• <b>DCA</b> - Position mitteln\n• <b>Ignorieren</b> - so lassen',
    'deep_loss_close_error': '❌ Fehler beim Schließen der Position: {error}',
    'deep_loss_closed': '✅ Position {symbol} geschlossen.\n\nVerlust realisiert. Manchmal ist es besser, einen kleinen Verlust zu akzeptieren, als auf eine Umkehr zu hoffen.',
    'deep_loss_ignored': '🔇 Verstanden, Position {symbol} unverändert gelassen.\n\n⚠️ Denken Sie daran: Ohne Stop-Loss ist das Verlustrisiko unbegrenzt.\nSie können die Position manuell über /positions schließen',
    'fibonacci_desc': '_Einstieg, SL, TP - aus Fibonacci-Levels im Signal._',
    'fibonacci_info': '📐 *Fibonacci Extension Strategie*',
    'prompt_min_quality': 'Mindestqualität % eingeben (0-100):',

    # Hardcore trading phrase
    'hardcore_mode': '💀 *HARDCORE-MODUS*: Keine Gnade, keine Reue. Nur Profit oder Tod! 🔥',

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ Unzureichendes ELC-Guthaben.

Ihr Guthaben: {balance} ELC
Erforderlich: {required} ELC

Laden Sie Ihr Wallet auf, um fortzufahren.''',
    'wallet_address': '''📍 Adresse: `{address}`''',
    'wallet_balance': '''💰 *Ihr ELC-Wallet*

◈ Guthaben: *{balance} ELC*
📈 Gestaked: *{staked} ELC*
🎁 Ausstehende Belohnungen: *{rewards} ELC*

💵 Gesamtwert: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« Zurück''',
    'wallet_btn_deposit': '''📥 Einzahlen''',
    'wallet_btn_history': '''📋 Verlauf''',
    'wallet_btn_stake': '''📈 Staken''',
    'wallet_btn_unstake': '''📤 Unstaken''',
    'wallet_btn_withdraw': '''📤 Abheben''',
    'wallet_deposit_demo': '''🎁 100 ELC erhalten (Demo)''',
    'wallet_deposit_desc': '''Senden Sie ELC-Token an Ihre Wallet-Adresse:

`{address}`

💡 *Demo-Modus:* Klicken Sie unten für kostenlose Test-Token.''',
    'wallet_deposit_success': '''✅ {amount} ELC erfolgreich eingezahlt!''',
    'wallet_deposit_title': '''📥 *ELC einzahlen*''',
    'wallet_history_empty': '''Noch keine Transaktionen.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *Transaktionsverlauf*''',
    'wallet_stake_desc': '''Staken Sie Ihre ELC-Token für *12% APY*!

💰 Verfügbar: {available} ELC
📈 Derzeit gestaked: {staked} ELC
🎁 Ausstehende Belohnungen: {rewards} ELC

Tägliche Belohnungen • Sofortiges Unstaking''',
    'wallet_stake_success': '''✅ {amount} ELC erfolgreich gestaked!''',
    'wallet_stake_title': '''📈 *ELC staken*''',
    'wallet_title': '''◈ *ELC-Wallet*''',
    'wallet_unstake_success': '''✅ {amount} ELC + {rewards} ELC Belohnungen abgehoben!''',
    'wallet_withdraw_desc': '''Zieladresse und Betrag eingeben:''',
    'wallet_withdraw_failed': '''❌ Abhebung fehlgeschlagen: {error}''',
    'wallet_withdraw_success': '''✅ {amount} ELC an {address} abgehoben''',
    'wallet_withdraw_title': '''📤 *ELC abheben*''',

    'spot_freq_hourly': '⏰ Stündlich',

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
    'error_insufficient_balance': '💰 Nicht genügend Guthaben auf Ihrem Konto, um eine Position zu eröffnen. Laden Sie Ihr Guthaben auf oder reduzieren Sie die Positionsgröße.',
    'error_order_too_small': '📉 Ordergröße zu klein (Minimum $5). Erhöhen Sie Entry% oder laden Sie Ihr Guthaben auf.',
    'error_api_key_expired': '🔑 API-Schlüssel abgelaufen oder ungültig. Aktualisieren Sie Ihre API-Schlüssel in den Einstellungen.',
    'error_api_key_missing': '🔑 API-Schlüssel nicht konfiguriert. Fügen Sie Bybit-Schlüssel im Menü 🔗 API Keys hinzu.',
    'error_rate_limit': '⏳ Zu viele Anfragen. Warten Sie eine Minute und versuchen Sie es erneut.',
    'error_position_not_found': '📊 Position nicht gefunden oder bereits geschlossen.',
    'error_leverage_error': '⚙️ Fehler bei der Hebeleinstellung. Versuchen Sie, den Hebel manuell an der Börse einzustellen.',
    'error_network_error': '🌐 Netzwerkproblem. Versuchen Sie es später erneut.',
    'error_sl_tp_invalid': '⚠️ SL/TP kann nicht gesetzt werden: Preis zu nah am aktuellen. Wird beim nächsten Zyklus aktualisiert.',
    'error_equity_zero': '💰 Ihr Kontostand ist null. Laden Sie Demo- oder Real-Konto auf, um zu handeln.',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 Terminal',
    'exchange_mode_activated_bybit': '🟠 *Bybit-Modus aktiviert*',
    'exchange_mode_activated_hl': '🔷 *HyperLiquid-Modus aktiviert*',
    'error_processing_request': '⚠️ Fehler bei der Verarbeitung der Anfrage',
    'unauthorized_admin': '❌ Nicht autorisiert. Dieser Befehl ist nur für den Admin.',
    'error_loading_dashboard': '❌ Fehler beim Laden des Dashboards.',
    'unauthorized': '❌ Nicht autorisiert.',
    'processing_blockchain': '⏳ Blockchain-Transaktion wird verarbeitet...',
    'verifying_payment': '⏳ Zahlung auf TON-Blockchain wird überprüft...',
    'no_wallet_configured': '❌ Kein Wallet konfiguriert.',
    'use_start_menu': 'Verwenden Sie /start, um zum Hauptmenü zurückzukehren.',

    # 2FA Login-Bestätigung
    'login_approved': '✅ Anmeldung bestätigt!\n\nSie können jetzt im Browser fortfahren.',
    'login_denied': '❌ Anmeldung abgelehnt.\n\nFalls das nicht Sie waren, überprüfen Sie Ihre Sicherheitseinstellungen.',
    'login_expired': '⏰ Bestätigung abgelaufen. Bitte erneut versuchen.',
    'login_error': '⚠️ Verarbeitungsfehler. Bitte später erneut versuchen.',

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

    # === AUTO-SYNCED FROM EN (need translation) ===
    "app_login_approved": "✅ <b>Login confirmed!</b>\n\nYou can continue in the app.",
    "app_login_error": "⚠️ Processing error. Please try later.",
    "app_login_expired": "⏰ Login request expired. Please try again.",
    "app_login_prompt": "🔐 <b>Login to Enliko App</b>\n\nClick the button below to login to iOS or Android app.\nLink is valid for 5 minutes.\n\n⚠️ Do not share this link with anyone!",
    "app_login_rejected": "❌ <b>Login rejected</b>\n\nIf this wasn't you, we recommend checking your security settings.",
    "atr_disabled_restored": "🔄 <b>ATR Disabled</b>\n\n📊 {symbol}\n🛡️ SL restored: {sl_price:.4f}\n🎯 TP restored: {tp_price:.4f}",
    "basic_bybit_only": "⚠️ *Basic Plan Limitation*\n\nBasic plan supports Bybit only.\nHyperLiquid is available on Premium.\n\n👉 /subscribe — Upgrade to Premium",
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
    'basic_title': '💚 *Supporter Membership*',
    'button_spot': '💹 Spot',
    'payment_ton_desc': 'TON payments are currently unavailable.',
    'position_closed_error': '⚠️ {symbol} closed but log failed: {error}',
    'premium_title': '🤝 *Patron Membership*',
    'spot_btn_buy': '💰 Buy Now',
    'spot_btn_holdings': '💎 Holdings',
    'spot_btn_rebalance': '⚖️ Rebalance',
    'spot_btn_sell': '💸 Sell Menu',
    'spot_btn_settings': '⚙️ Settings',
    'subscribe_menu_info': '_Select a plan to continue:_',
    'trial_already_used': '⚠️ Trial already used. Choose a paid plan.',
    'trial_title': '🆓 *Explorer Access — 14 Days*',
    'wallet_deposit_desc': 'Send ELC tokens to:\n\n`{address}`',
    'wallet_history_item': '{type_emoji} {type}: {amount:+.2f} ELC\n   {date}',


    # Daily Digest
    'digest_title': '📊 Täglicher Handelsbericht',
    'digest_detailed_title': '📋 Detaillierter Bericht',
    'digest_date_format': '%d. %B %Y',
    'digest_filter_all': '🌍 Alle Börsen',
    'digest_no_trades': '📭 Keine Trades für diesen Filter',
    'digest_no_trades_hint': 'Versuchen Sie eine andere Filterkombination.',
    'digest_total_pnl': 'Gesamt-PnL',
    'digest_statistics': 'Statistiken',
    'digest_trades': 'Trades',
    'digest_wins_losses': 'Gewinne/Verluste',
    'digest_win_rate': 'Gewinnrate',
    'digest_avg_pnl': 'Durchschn. PnL',
    'digest_best_trade': 'Bester Trade',
    'digest_worst_trade': 'Schlechtester Trade',
    'digest_keep_improving': 'Weiter verbessern! 💪',
    'digest_vibe_amazing': 'Fantastischer Tag!',
    'digest_vibe_nice': 'Gute Arbeit!',
    'digest_vibe_breakeven': 'Breakeven-Tag',
    'digest_vibe_small_loss': 'Kleiner Verlust',
    'digest_vibe_tough': 'Harter Tag',
    'digest_btn_all': 'Alle',
    'digest_btn_bybit': '🟠 Bybit',
    'digest_btn_hl': '🔷 HL',
    'digest_btn_demo': '🧪 Demo',
    'digest_btn_real': '💼 Real',
    'digest_btn_testnet': '🧪 Testnet',
    'digest_btn_mainnet': '🌐 Mainnet',
    'digest_btn_detailed': '📋 Details',
    'digest_btn_close': '❌ Schließen',
    'digest_btn_back': '◀️ Zurück',
    'digest_by_exchange': 'Nach Börse',
    'digest_by_strategy': 'Nach Strategie',
    'digest_top_symbols': 'Top Symbole',
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
