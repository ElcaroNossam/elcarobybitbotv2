# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu
    'welcome':                     '👋 Hallo! Wähle eine Aktion:',
    'no_strategies':               '❌ Keine',
    'guide_caption':               '📚 Trading Bot Benutzerhandbuch\n\nLesen Sie dieses Handbuch, um zu erfahren, wie Sie Strategien konfigurieren und den Bot effektiv nutzen.',
    'privacy_caption':             '📜 Datenschutzrichtlinie & Nutzungsbedingungen\n\nBitte lesen Sie dieses Dokument sorgfältig durch.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 Secret',
    'button_api_settings':         '🔑 API',
    'button_balance':              '💰 USDT-Kontostand',
    'button_orders':               '📜 Meine Orders',
    'button_positions':            '📊 Positionen',
    'button_percent':              '🎚 % pro Trade',
    'button_coins':                '💠 Münzgruppe',
    'button_market':               '📈 Markt',
    'button_manual_order':         '✋ Manuelle Order',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ Order abbrechen',
    'button_limit_only':           '🎯 Nur Limit',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_settings':             '⚙️ Einstellungen',
    'button_indicators':           '💡 Indikatoren',
    'button_support':              '🆘 Support',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 TP/SL-Modus ist jetzt: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Fester %',

    # Limits
    'limit_positions_exceeded':    '🚫 Limit offener Positionen überschritten ({max})',
    'limit_limit_orders_exceeded': '🚫 Limit für Limit-Orders überschritten ({max})',

    # Languages
    'select_language':             'Sprache wählen:',
    'language_set':                'Sprache eingestellt auf:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'Ordertyp wählen:',
    'limit_order_format': (
        "Parameter der Limit-Order eingeben:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "wobei SIDE = LONG oder SHORT\n"
        "Beispiel: `BTCUSDT LONG 20000 0.1`\n\n"
        "Zum Abbrechen: ❌ Order abbrechen"
    ),
    'market_order_format': (
        "Parameter der Market-Order eingeben:\n"
        "`SYMBOL SIDE QTY`\n"
        "wobei SIDE = LONG oder SHORT\n"
        "Beispiel: `BTCUSDT SHORT 0.1`\n\n"
        "Zum Abbrechen: ❌ Order abbrechen"
    ),
    'order_success':               '✅ Order erfolgreich erstellt!',
    'order_create_error':          '❌ Order konnte nicht erstellt werden: {msg}',
    'order_fail_leverage':         (
        "❌ Order nicht erstellt: Deine Bybit-Hebelwirkung ist für diese Größe zu hoch.\n"
        "Bitte reduziere den Hebel in den Bybit-Einstellungen."
    ),
    'order_parse_error':           '❌ Parsen fehlgeschlagen: {error}',
    'price_error_min':             '❌ Preisfehler: muss ≥{min} sein',
    'price_error_step':            '❌ Preisfehler: Vielfaches von {step} erforderlich',
    'qty_error_min':               '❌ Mengenfehler: muss ≥{min} sein',
    'qty_error_step':              '❌ Mengenfehler: Vielfaches von {step} erforderlich',

    # Loading…
    'loader':                      '⏳ Daten werden gesammelt…',

    # Market command
    'market_status_heading':       '*Marktstatus:*',
    'market_dominance_header':    'Top Coins nach Dominanz',
    'market_total_header':        'Gesamte Marktkapitalisierung',
    'market_indices_header':      'Marktindizes',
    'usdt_dominance':              'USDT-Dominanz',
    'btc_dominance':               'BTC-Dominanz',
    'dominance_rising':            '↑ steigend',
    'dominance_falling':           '↓ fallend',
    'dominance_stable':            '↔️ stabil',
    'dominance_unknown':           '❔ keine Daten',
    'btc_price':                   'BTC-Preis',
    'last_24h':                    'in den letzten 24 h',
    'alt_signal_label':            'Altcoin-Signal',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Neueste News (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'Ausführungspreis zum Schließen nicht gefunden',

    # /account
    'account_balance':             '💰 USDT-Kontostand: `{balance:.2f}`',
    'account_realized_header':     '📈 *Realisierter PnL:*',
    'account_realized_day':        '  • Heute : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 Tage: `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *Nicht realisierter PnL:*',
    'account_unreal_total':        '  • Gesamt: `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % von IM: `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Deine Einstellungen:*',
    'config_percent':              '• 🎚 % pro Trade       : `{percent}%`',
    'config_coins':                '• 💠 Coins            : `{coins}`',
    'config_limit_only':           '• 🎯 Limit-Orders     : {state}',
    'config_atr_mode':             '• 🏧 ATR-Trailing SL  : {atr}',
    'config_trade_oi':             '• 📊 OI handeln       : {oi}',
    'config_trade_rsi_bb':         '• 📈 RSI+BB handeln   : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%              : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%              : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 Keine offenen Orders',
    'open_orders_header':          '*📒 Deine offenen Orders:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Seite: `{side}`\n"
        "   • Menge: `{qty}`\n"
        "   • Preis: `{price}`\n"
        "   • ID   : `{id}`"
    ),
    'open_orders_error':           '❌ Fehler beim Abrufen der Orders: {error}',

    # Manual coin selection
    'enter_coins':                 "Gib Symbole durch Komma getrennt ein, z. B.:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Coins ausgewählt: {coins}',

    # Positions
    'no_positions':                '🚫 Keine offenen Positionen',
    'positions_header':            '📊 Deine offenen Positionen:',
    'position_item':               (
        "— Position #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • Größe          : {size}\n"
        "  • Einstiegspreis : {avg:.8f}\n"
        "  • Mark-Preis     : {mark:.8f}\n"
        "  • Liquidation    : {liq}\n"
        "  • Initial Margin : {im:.2f}\n"
        "  • Maint. Margin  : {mm:.2f}\n"
        "  • Positionssaldo : {pm:.2f}\n"
        "  • Take-Profit    : {tp}\n"
        "  • Stop-Loss      : {sl}\n"
        "  • Unrealisierter PnL: {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'positions_overall':           'Gesamt nicht realisierter PnL: {pnl:+.2f} ({pct:+.2f}%)',

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
    'set_percent_prompt':          'Gib den Prozentanteil pro Trade ein (z. B. 2.5):',
    'percent_set_success':         '✅ % pro Trade gesetzt: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Nur Limit-Orders: {state}',
    'feature_limit_only':          'Nur Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Elcaro-Indikatoren*',
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

    # Auto notifications
    'new_position':                '🚀 Neue Position {symbol} @ {entry:.6f}, Größe={size}',
    'sl_auto_set':                 '🛑 SL automatisch gesetzt: {price:.6f}',
    'auto_close_position':         '⏱ Position {symbol} (TF={tf}) > {tf} offen und im Verlust, automatisch geschlossen.',
    'position_closed': (
        '🔔 Position {symbol} geschlossen durch *{reason}*:\n'
        '• Strategy: `{strategy}`\n'
        '• Entry: `{entry:.8f}`\n'
        '• Exit : `{exit:.8f}`\n'
        '• PnL  : `{pnl:+.2f} USDT ({pct:+.2f}%)`'
    ),

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

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Limit Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit Fehler: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Market Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market Fehler: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *Elcaro Limit Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Elcaro Limit Fehler: {msg}',
    'elcaro_market_entry':         '🔥 *Elcaro Market Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Elcaro Market Fehler: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

    # Wyckoff (Fibonacci Extension)
    'wyckoff_limit_entry':         '📐 *Wyckoff Limit Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'wyckoff_limit_error':         '❌ Wyckoff Limit Fehler: {msg}',
    'wyckoff_market_entry':        '📐 *Wyckoff Market Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'wyckoff_market_ok':           '📐 *Wyckoff: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'wyckoff_market_error':        '❌ Wyckoff Market Fehler: {msg}',
    'wyckoff_analysis':            '📐 Wyckoff: {side} @ {price}',
    'feature_wyckoff':             'Wyckoff',

    # Admin panel
    'admin_panel':                 '👑 Admin-Panel:',
    'admin_pause':                 '⏸️ Handel & Benachrichtigungen für alle pausiert.',
    'admin_resume':                '▶️ Handel & Benachrichtigungen für alle fortgesetzt.',
    'admin_closed':                '✅ Insgesamt geschlossen: {count} {type}.',
    'admin_canceled_limits':       '✅ {count} Limit-Orders storniert.',

    # Coin groups
    'select_coin_group':           'Münzgruppe wählen:',
    'group_all':                   'ALL',
    'group_top100':                'TOP100',
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
    'api_test_success':            'Verbindung erfolgreich!',
    'api_test_no_keys':            'API-Schlüssel nicht eingestellt',
    'api_test_set_keys':           'Bitte zuerst API Key und Secret einstellen.',
    'api_test_failed':             'Verbindung fehlgeschlagen',
    'api_test_error':              'Fehler',
    'api_test_check_keys':         'Bitte überprüfen Sie Ihre API-Anmeldedaten.',
    'api_test_status':             'Status',
    'api_test_connected':          'Verbunden',
    'balance_wallet':              'Wallet-Guthaben',
    'balance_equity':              'Eigenkapital',
    'balance_available':           'Verfügbar',
    'api_missing_notice':          '⚠️ Sie haben keine Exchange-API-Schlüssel konfiguriert. Bitte fügen Sie Ihren API-Key und Secret in den Einstellungen hinzu (🔑 API und 🔒 Secret Schaltflächen), sonst kann der Bot nicht für Sie handeln.',
    'elcaro_ai_info':              '🤖 *KI-gestützter Handel*',

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
    'strat_mode_both':             '🔄 Beide',
    'strat_mode_changed':          '✅ {strategy} Handelsmodus: {mode}',

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
    'wyckoff_limit_entry':         '📐 Wyckoff Limit-Einstieg {symbol} @ {price:.6f}',
    'wyckoff_limit_error':         '❌ Wyckoff Limit-Einstiegsfehler: {msg}',
    'wyckoff_market_entry':        '🚀 Wyckoff Markt {symbol} @ {price:.6f}',
    'wyckoff_market_error':        '❌ Wyckoff Marktfehler: {msg}',
    'wyckoff_market_ok':           '📐 Wyckoff: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'wyckoff_analysis':            'Wyckoff: {side} @ {price}',
    'feature_wyckoff':             'Wyckoff',

    'scalper_limit_entry':           'Scalper: Limit-Order {symbol} @ {price}',
    'scalper_limit_error':           'Scalper Limit-Fehler: {msg}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper-Fehler: {msg}',

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
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_wyckoff':                 '📐 Wyckoff',
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

    # Hardcoded strings fix
    'terms_unavailable':             'Nutzungsbedingungen nicht verfügbar. Kontaktieren Sie den Administrator.',
    'terms_confirm_prompt':          'Bitte bestätigen:',
    'your_id':                       'Ihre ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Fehler: {msg}',

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
    'stats_elcaro':                  '🔥 Elcaro',
    'stats_period_all':              'Gesamtzeit',
    'stats_period_today':            'Heute',
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

    # Elcaro AI settings

    # Leverage settings
    'param_leverage': '⚡ Hebel',
    'prompt_leverage': 'Hebel eingeben (1-100):',
    'auto_default': 'Auto',

    # Elcaro AI
    'elcaro_ai_desc': '_Alle Parameter werden automatisch aus AI-Signalen geparst:_',

    # Scalper entries
    'scalper_market_entry': '🚀 Scalper Market {symbol} @ {price:.6f}',
    'scalper_analysis': 'Scalper: {side} @ {price}',

    # Scryptomera feature
    'feature_scryptomera': 'Scryptomera',

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
    'spot_trading_mode': 'Handelsmodus',
    'spot_btn_mode': 'Modus',
    
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
    
    # License status messages
    'no_license': '⚠️ Sie benötigen ein aktives Abonnement, um diese Funktion zu nutzen.\n\nVerwenden Sie /subscribe, um eine Lizenz zu erwerben.',
    'no_license_trading': '⚠️ Sie benötigen ein aktives Abonnement zum Handeln.\n\nVerwenden Sie /subscribe, um eine Lizenz zu erwerben.',
    'license_required': '⚠️ Diese Funktion erfordert ein {required}-Abonnement.\n\nVerwenden Sie /subscribe zum Upgrade.',
    'trial_demo_only': '⚠️ Die Testlizenz erlaubt nur Demo-Handel.\n\nUpgrade auf Premium oder Basic für echten Handel: /subscribe',
    'basic_strategy_limit': '⚠️ Basic-Lizenz auf echtem Konto erlaubt nur: {strategies}\n\nUpgrade auf Premium für alle Strategien: /subscribe',
    
    # Subscribe menu
    'subscribe_menu_header': '💎 *Abonnement-Pläne*',
    'subscribe_menu_info': 'Wählen Sie Ihren Plan, um Handelsfunktionen freizuschalten:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Test (Kostenlos)',
    'btn_enter_promo': '🎟 Promo-Code',
    'btn_my_subscription': '📋 Mein Abonnement',
    
    # Premium plan
    'premium_title': '💎 *PREMIUM-PLAN*',
    'premium_desc': '''✅ Voller Zugang zu allen Funktionen
✅ Alle 5 Strategien: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ Echt + Demo-Handel
✅ Prioritäts-Support
✅ ATR-basierter dynamischer SL/TP
✅ Limit-Leiter DCA
✅ Alle zukünftigen Updates''',
    'premium_1m': '💎 1 Monat — {price}⭐',
    'premium_3m': '💎 3 Monate — {price}⭐ (-15%)',
    'premium_6m': '💎 6 Monate — {price}⭐ (-25%)',
    'premium_12m': '💎 12 Monate — {price}⭐ (-35%)',
    
    # Basic plan
    'basic_title': '🥈 *BASIC-PLAN*',
    'basic_desc': '''✅ Voller Demo-Konto-Zugang
✅ Echtes Konto: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Wyckoff, Spot — nur Premium
✅ Standard-Support
✅ ATR-basierter dynamischer SL/TP''',
    'basic_1m': '🥈 1 Monat — {price}⭐',
    
    # Trial plan
    'trial_title': '🎁 *TEST-PLAN (KOSTENLOS)*',
    'trial_desc': '''✅ Voller Demo-Konto-Zugang
✅ Alle 5 Strategien auf Demo
❌ Echter Handel nicht verfügbar
⏰ Dauer: 7 Tage
🎁 Nur einmal''',
    'trial_activate': '🎁 Kostenlose Testversion aktivieren',
    'trial_already_used': '⚠️ Sie haben Ihre kostenlose Testversion bereits verwendet.',
    'trial_activated': '🎉 Testversion aktiviert! Sie haben 7 Tage vollen Demo-Zugang.',
    
    # Payment
    'payment_select_method': '💳 *Zahlungsmethode wählen*',
    'btn_pay_stars': '⭐ Telegram Stars',
    'btn_pay_ton': '💎 TON',
    'payment_stars_title': '⭐ Zahlung via Telegram Stars',
    'payment_stars_desc': 'Ihnen werden {amount}⭐ für {plan} ({period}) berechnet.',
    'payment_ton_title': '💎 Zahlung via TON',
    'payment_ton_desc': '''Senden Sie genau *{amount} TON* an:

`{wallet}`

Nach der Zahlung klicken Sie auf die Schaltfläche unten zur Verifizierung.''',
    'btn_verify_ton': '✅ Ich habe bezahlt — Verifizieren',
    'payment_processing': '⏳ Zahlung wird verarbeitet...',
    'payment_success': '🎉 Zahlung erfolgreich!\n\n{plan} aktiviert bis {expires}.',
    'payment_failed': '❌ Zahlung fehlgeschlagen: {error}',
    
    # My subscription
    'my_subscription_header': '📋 *Mein Abonnement*',
    'my_subscription_active': '''📋 *Aktueller Plan:* {plan}
⏰ *Läuft ab:* {expires}
📅 *Tage übrig:* {days}''',
    'my_subscription_none': '❌ Kein aktives Abonnement.\n\nVerwenden Sie /subscribe, um einen Plan zu erwerben.',
    'my_subscription_history': '📜 *Zahlungshistorie:*',
    'subscription_expiring_soon': '⚠️ Ihr {plan}-Abonnement läuft in {days} Tagen ab!\n\nJetzt verlängern: /subscribe',
    
    # Promo codes
    'promo_enter': '🎟 Geben Sie Ihren Promo-Code ein:',
    'promo_success': '🎉 Promo-Code angewendet!\n\n{plan} für {days} Tage aktiviert.',
    'promo_invalid': '❌ Ungültiger Promo-Code.',
    'promo_expired': '❌ Dieser Promo-Code ist abgelaufen.',
    'promo_used': '❌ Dieser Promo-Code wurde bereits verwendet.',
    'promo_already_used': '❌ Sie haben diesen Promo-Code bereits verwendet.',
    
    # Admin license management
    'admin_license_menu': '🔑 *Lizenzverwaltung*',
    'admin_btn_grant_license': '🎁 Lizenz erteilen',
    'admin_btn_view_licenses': '📋 Lizenzen anzeigen',
    'admin_btn_create_promo': '🎟 Promo erstellen',
    'admin_btn_view_promos': '📋 Promos anzeigen',
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
  Stars: {total_stars}⭐

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
    'stats_wyckoff': '📐 Wyckoff',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "HyperLiquid Handel",
    "hl_reset_settings": "🔄 Auf Bybit-Einstellungen zurücksetzen",



    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ Cancelled.',  # TODO: translate from EN
    'entry_pct_range_error': '❌ Entry % must be between 0.1 and 100.',  # TODO: translate from EN
    'hl_no_history': '📭 No trade history on HyperLiquid.',  # TODO: translate from EN
    'hl_no_orders': '📭 No open orders on HyperLiquid.',  # TODO: translate from EN
    'hl_no_positions': '📭 No open positions on HyperLiquid.',  # TODO: translate from EN
    'hl_setup_cancelled': '❌ HyperLiquid setup cancelled.',  # TODO: translate from EN
    'invalid_amount': '❌ Invalid number. Please enter a valid amount.',  # TODO: translate from EN
    'leverage_range_error': '❌ Leverage must be between 1 and 100.',  # TODO: translate from EN
    'max_amount_error': '❌ Maximum amount is 100,000 USDT',  # TODO: translate from EN
    'min_amount_error': '❌ Minimum amount is 1 USDT',  # TODO: translate from EN
    'sl_tp_range_error': '❌ SL/TP % must be between 0.1 and 500.',  # TODO: translate from EN
}
