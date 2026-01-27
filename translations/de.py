# -*- coding: utf-8 -*-
TEXTS = {
    # Hauptmenü - Professionelles Trading-Terminal
    'welcome':                     '''🔥 <b>Lyxen Trading Terminal</b>

⚡ <b>&lt; 100ms</b> Ausführung
🛡️ <b>Risikomanagement</b> integriert
💎 <b>24/7</b> automatisierter Handel

Bybit • HyperLiquid • Multi-Strategie''',
    'no_strategies':               '❌ Keine aktiven Strategien',
    'guide_caption':               '📚 <b>Benutzerhandbuch</b>\n\nAPI-Einrichtung, Strategien, Risikomanagement.',
    'privacy_caption':             '📜 <b>Datenschutz</b>\n\n🔐 Verschlüsselte Speicherung\n✅ Keine Datenweitergabe',
    
    # ═══════════════════════════════════════════════════════════════════
    # MODERN MENU BUTTONS - Stylish & Persuasive (DE)
    # ═══════════════════════════════════════════════════════════════════
    'button_api':                  '🔐 API verbinden',
    'button_secret':               '🔑 Secret',
    'button_api_settings':         '⚙️ API-Einstellungen',
    'button_subscribe':            '👑 PREMIUM',
    'button_licenses':             '🎫 Lizenzen',
    'button_admin':                '🛡️ Admin',
    'button_balance':              '💎 Portfolio',
    'button_orders':               '📊 Aufträge',
    'button_positions':            '🎯 Positionen',
    'button_history':              '📜 Verlauf',
    'button_strategies':           '🤖 KI Bots',
    'button_api_keys':             '🔗 Börse',
    'button_bybit':                '🟠 Bybit',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_switch_bybit':         '🔄 Bybit',
    'button_switch_hl':            '🔄 HL',
    'button_percent':              '⚡ Risiko %',
    'button_coins':                '🪙 Münzen',
    'button_market':               '📈 Markt',
    'button_manual_order':         '🎯 Sniper',
    'button_update_tpsl':          '🛡️ TP/SL',
    'button_cancel_order':         '✖️ Abbrechen',
    'button_limit_only':           '📍 Limit',
    'button_toggle_oi':            '🐋 OI Tracker',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_scalper':              '⚡ Scalper',
    'button_elcaro':               '🔥 Lyxen',
    'button_fibonacci':            '📐 Fibonacci',
    'button_settings':             '⚙️ Konfig',
    'button_indicators':           '📡 Signale',
    'button_support':              '💬 Support',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',
    'config_trade_scalper':        '🎯 Scalper: {state}',
    'config_trade_elcaro':         '🔥 Lyxen: {state}',
    'config_trade_fibonacci':      '📐 Fibonacci: {state}',

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
        "  • Anfängl. Marge : {im:.2f}\n"
        "  • Erhalt. Marge  : {mm:.2f}\n"
        "  • Positionssaldo : {pm:.2f}\n"
        "  • Take-Profit    : {tp}\n"
        "  • Stop-Loss      : {sl}\n"
        "  • Unrealisierter PnL: {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'position_item_v2':            (
        "— #{idx}: {symbol} | {side} (x{leverage}) [{strategy}]\n"
        "  • Größe          : {size}\n"
        "  • Einstiegspreis : {avg:.8f}\n"
        "  • Mark-Preis     : {mark:.8f}\n"
        "  • Liquidation    : {liq}\n"
        "  • Anfängl. Marge : {im:.2f}\n"
        "  • Erhalt. Marge  : {mm:.2f}\n"
        "  • Take Profit    : {tp}\n"
        "  • Stop Loss      : {sl}\n"
        "  {pnl_emoji} Unreal. PnL  : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'pnl_by_strategy':             '📊 *PnL nach Strategie:*',
    'pnl_by_exchange':             '🏦 *PnL nach Börse:*',
    'positions_overall':           'Gesamt nicht realisierter PnL: {pnl:+.2f} ({pct:+.2f}%)',

    # Position management (inline)
    'open_positions_header':       '📊 *Offene Positionen*',
    'positions_count':             'Positionen',
    'positions_count_total':       'Positionen gesamt',
    'total_unrealized_pnl':        'Nicht realisierter Gewinn/Verlust',
    'total_pnl':                   'Gesamter P/L',
    'btn_close_short':             'Schließen',
    'btn_close_all':               'Alle Positionen schließen',
    'btn_close_position':          'Position schließen',
    'btn_confirm_close':           'Schließen bestätigen',
    'btn_confirm_close_all':       'Ja, alle schließen',
    'btn_cancel':                  '❌ Abbrechen',
    'btn_back':                    '🔙 Zurück',
    'confirm_close_position':      'Position schließen',
    'confirm_close_all':           'ALLE Positionen schließen',
    'position_not_found':          'Position nicht gefunden oder bereits geschlossen',
    'position_already_closed':     'Position bereits geschlossen',
    'position_closed_success':     'Position geschlossen',
    'position_close_error':        'Fehler beim Schließen',
    'positions_closed':            'Positionen geschlossen',
    'errors':                      'Fehler',

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
    'indicators_header':           '📈 *Lyxen-Indikatoren*',
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

_Lyxen KI erkannte die Chance. Du bist dabei._''',
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

    # Lyxen (Heatmap)
    'elcaro_limit_entry':          '🔥 *Lyxen Limit Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Lyxen Limit Fehler: {msg}',
    'elcaro_market_entry':         '🔥 *Lyxen Market Einstieg*\n• {symbol} {side}\n• Preis: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Lyxen: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Lyxen Market Fehler: {msg}',
    'elcaro_analysis':             '🔥 Lyxen Heatmap: {side} @ {price}',
    'feature_elcaro':              'Lyxen',

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

    # Lyxen (Heatmap)

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
    'strat_elcaro':                  '🔥 Lyxen',
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
    'stats_elcaro':                  '🔥 Lyxen',
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

    # Lyxen AI settings

    # Leverage settings
    'param_leverage': '⚡ Hebel',
    'prompt_leverage': 'Hebel eingeben (1-100):',
    'auto_default': 'Auto',

    # Lyxen AI
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
    
    # License status messages - BLACK RHETORIC: Loss Aversion + FOMO
    'no_license': '''🚨 *ZUGANG VERWEIGERT*

Während du zögerst, profitieren *847 Trader* bereits.

💸 Jede Minute ohne Lyxen = verpasste Chancen
⏰ Märkte warten nicht. Du solltest es auch nicht.

👉 /subscribe — _Schalte deinen unfairen Vorteil JETZT frei_''',
    'no_license_trading': '''🚨 *HANDEL GESPERRT*

Deine Konkurrenten verdienen GERADE JETZT mit Lyxen.

❌ Manueller Handel = emotionale Fehler
✅ Lyxen = kalte KI-Präzision

_Hör auf zuzuschauen. Fang an zu verdienen._

👉 /subscribe — *Schließe dich 847+ smarten Tradern an*''',
    'license_required': '''🔒 *PREMIUM-FUNKTION*

Dies erfordert {required}-Abonnement — _genutzt von den Top 3% der Trader_.

🎯 Erfolg hinterlässt Spuren. Folge den Gewinnern.

👉 /subscribe — *Jetzt upgraden*''',
    'trial_demo_only': '''⚠️ *Demo-Modus ist zum Lernen, nicht zum Verdienen.*

Echte Gewinne erfordern echten Zugang.

🎁 Du hast die Kraft gekostet. Jetzt *besitze* sie.

👉 /subscribe — *Schalte echten Handel frei*''',
    'basic_strategy_limit': '''⚠️ *Basic = Basic Ergebnisse*

Du bist limitiert auf: {strategies}

Die Profis nutzen *ALLE* Strategien. Deshalb sind sie Profis.

👉 /subscribe — *Werde Premium. Werde Profi.*''',
    
    # Subscribe menu - BLACK RHETORIC: Urgency + Authority + Exclusivity
    'subscribe_menu_header': '''💎 *SCHALTE DEIN TRADING-IMPERIUM FREI*

⚡ 847+ Trader profitieren bereits
🏆 97% Nutzerzufriedenheit
📈 $2.4M+ generiert diesen Monat''',
    'subscribe_menu_info': '''_"Die beste Investition, die ich je gemacht habe"_ — Premium-Nutzer

Wähle dein Level der Dominanz:''',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Test (Kostenlos)',
    'btn_enter_promo': '🎟 Promo-Code',
    'btn_my_subscription': '📋 Mein Abonnement',
    
    # Premium plan - BLACK RHETORIC: Authority + Scarcity + Social Proof
    'premium_title': '''💎 *PREMIUM — TOTALE DOMINANZ*

_"Dieser Bot druckt buchstäblich Geld"_ — @CryptoKing''',
    'premium_desc': '''🔥 *ALLES FREIGESCHALTET:*

✅ Alle 5 KI-Strategien — _$100K+ Trades täglich ausgeführt_
✅ Real + Demo — _Keine Einschränkungen_
✅ Priorität VIP-Support — _Antwort < 1 Stunde_
✅ Dynamischer ATR SL/TP — _KI-optimierte Einstiege_
✅ DCA Limit-Leiter — _Institutionelles Scaling_
✅ Lebenslange Updates — _Immer dem Markt voraus_

⚡ *PREMIUM-STATISTIKEN:*
• Durchschnittlicher ROI: +47%/Monat
• Gewinnrate: 78%
• Aktive Nutzer: 312

_Die Frage ist nicht "Kann ich mir Premium leisten?"
Die Frage ist "Kann ich es mir leisten, NICHT Premium zu haben?"_''',
    'premium_1m': '💎 1 Monat — {price} ELC ⚡',
    'premium_3m': '💎 3 Monate — {price} ELC 🔥 SPARE 10%',
    'premium_6m': '💎 6 Monate — {price} ELC 🎯 SPARE 20%',
    'premium_12m': '💎 12 Monate — {price} ELC 🏆 BESTER WERT -30%',
    
    # Basic plan - BLACK RHETORIC: Stepping stone narrative
    'basic_title': '''🥈 *BASIC — SMARTER START*

_Perfekt zum Testen der Gewässer_''',
    'basic_desc': '''✅ Voller Demo-Zugang — _Risikofreies Lernen_
✅ Real-Konto: OI, RSI+BB, Scryptomera, Scalper
⛔ Lyxen, Fibonacci, Spot — _Premium exklusiv_
✅ Standard-Support
✅ ATR Dynamischer SL/TP

💡 *87% der Basic-Nutzer upgraden innerhalb von 2 Wochen auf Premium*
_Sie sehen die Ergebnisse. Du wirst es auch._''',
    'basic_1m': '🥈 1 Monat — {price} ELC',
    
    # Trial plan - BLACK RHETORIC: Zero risk + Taste of power
    'trial_title': '''🎁 *KOSTENLOSE TESTVERSION — NULL RISIKO*

_Sehen ist Glauben_''',
    'trial_desc': '''✅ Voller Demo-Zugang — *Alle 5 KI-Strategien*
✅ 7 Tage pure Power
✅ Keine Kreditkarte erforderlich
⚡ Ein-Klick-Aktivierung

⚠️ *WARNUNG:* Nach Lyxen KI erleben,
wird manuelles Trading... primitiv wirken.

_91% der Testnutzer werden zahlende Kunden._
_Jetzt wirst du verstehen warum._''',
    'trial_activate': '🎁 KOSTENLOSE TESTVERSION AKTIVIEREN ⚡',
    'trial_already_used': '''⚠️ Testversion bereits verwendet.

Du hast die Kraft gesehen. Jetzt *besitze* sie.

👉 Wähle einen Plan und schließe dich der Elite an.''',
    'trial_activated': '''🎉 *WILLKOMMEN IN DER ZUKUNFT DES TRADINGS!*

⏰ Du hast 7 Tage zum Erleben:
• KI-gesteuerte Einstiege
• Automatisches Risikomanagement
• 24/7 Marktüberwachung

_Deine Reise zur finanziellen Freiheit beginnt JETZT._

💡 Pro-Tipp: Aktiviere alle Strategien für maximale Ergebnisse!''',
    
    # Payment
    'payment_select_method': '💳 *Zahlungsmethode wählen*',
    'btn_pay_elc': '◈ Lyxen Coin (ELC)',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' Zahlung via ELC',
    'payment_elc_desc': 'Ihnen werden {amount} ELC für {plan} ({period}) berechnet.',
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
    'all_positions_closed': 'Alle Positionen geschlossen',
    'btn_check_again': '🔄 Erneut prüfen',
    'current': 'Aktuell',
    'entry': 'Einstieg',
    'max_positions_reached': '⚠️ Maximale Positionen erreicht. Neue Signale werden übersprungen bis eine Position geschlossen wird.',
    'payment_session_expired': '❌ Zahlungssitzung abgelaufen. Bitte erneut starten.',
    'payment_ton_not_configured': '❌ TON-Zahlungen sind nicht konfiguriert.',
    'payment_verifying': '⏳ Zahlung wird verifiziert...',
    'position': 'Position',
    'size': 'Größe',
    'stats_fibonacci': '📐 Fibonacci',

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

    'spot_freq_biweekly': '📅 Alle 2 Wochen',
    'spot_trailing_enabled': '✅ Trailing TP aktiviert: Aktivierung bei +{activation}%, Trail {trail}%',
    'spot_trailing_disabled': '❌ Trailing TP deaktiviert',
    'spot_grid_started': '🔲 Grid Bot gestartet für {coin}: {levels} Ebenen von ${low} bis ${high}',
    'spot_grid_stopped': '⏹ Grid Bot gestoppt für {coin}',
    'spot_limit_placed': '📝 Limit-Order platziert: Kauf {amount} {coin} bei ${price}',
    'spot_limit_cancelled': '❌ Limit-Order storniert für {coin}',
    'spot_freq_hourly': '⏰ Stündlich',

    # ─── SYNCED FROM EN (placeholders) ───
    'button_terminal': '💻 Terminal',
    'button_back': '← Back',
    'button_close': '✖️ Close',
    'button_refresh': '🔄 Refresh',
    'button_confirm': '✅ Confirm',
    'button_cancel': '❌ Cancel',
    'menu_section_demo': '══ 🧪 DEMO ══',
    'menu_section_real': '══ 💼 REAL ══',
    'menu_test_connection': '🔄 Test',
    'menu_delete': '🗑️ Delete',
    'exchange_bybit_demo': '🟠 Bybit 🎮',
    'exchange_bybit_real': '🟠 Bybit 💵',
    'exchange_bybit_both': '🟠 Bybit 🔀',
    'exchange_hl_testnet': '🔷 HL 🧪',
    'exchange_hl_mainnet': '🔷 HL 🌐',
    'not_set': '—',
    'exch_mode_bybit_only': '🟠 Bybit Only',
    'exch_mode_hl_only': '🟢 HyperLiquid Only',
    'exch_mode_both': '🔄 Both Exchanges',
    'btn_connect_hl': '➕ Connect HyperLiquid',
    'exch_not_configured': '❌ Not configured',
    'exch_not_connected': '❌ Not connected',
    'exch_trading_mode': 'Trading Mode',
    'exch_active': '🟢 Active',
    'exch_inactive': '⚪ Inactive',
    'exch_switch_success': '✅ Switched to {exchange}',
    'exch_select_mode': 'Select exchange mode:',
    'toggle_on': '✅ Enabled',
    'toggle_off': '❌ Disabled',
    'mode_demo': '🧪 Demo',
    'mode_real': '💰 Real',
    'mode_testnet': '🧪 Testnet',
    'mode_mainnet': '🌐 Mainnet',
    'btn_confirm': '✅ Confirm',
    'btn_refresh': '🔄 Refresh',
    'btn_settings': '⚙️ Settings',
    'btn_delete': '🗑️ Delete',
    'btn_yes': '✅ Yes',
    'btn_no': '❌ No',
    'elc_balance_title': '💰 <b>LYXEN Balance</b>',
    'elc_available': 'Available',
    'elc_staked': 'Staked',
    'elc_locked': 'Locked',
    'elc_total': 'Total',
    'elc_value_usd': '💵 Value: ~${value:.2f} USD',
    'btn_buy_elc': '🛒 Buy ELC',
    'btn_elc_history': '📊 History',
    'btn_connect_wallet': '🔗 Connect Wallet',
    'btn_disconnect_wallet': '🔓 Disconnect',
    'elc_buy_title': '🛒 <b>Buy LYXEN (ELC)</b>',
    'elc_current_price': '💵 Current Price: <b>$1.00 USD / ELC</b>',
    'elc_platform_fee': '🔥 Platform Fee: <b>0.5%</b>',
    'elc_purchase_hint': '<i>Purchase ELC with USDT on TON Network</i>',
    'elc_choose_amount': 'Choose amount to buy:',
    'elc_custom_amount': '✏️ Custom Amount',
    'elc_custom_amount_title': '✏️ <b>Custom Amount</b>',
    'elc_custom_prompt': '''Reply with the amount of ELC you want to buy
Example: <code>2500</code>

Min: 100 ELC
Max: 100,000 ELC''',
    'elc_purchase_summary': '🛒 <b>Purchase {amount:.2f} ELC</b>',
    'elc_cost': 'Cost: <b>{cost:.2f} USDT</b>',
    'elc_fee_amount': 'Platform Fee: <b>{fee:.2f} USDT</b>',
    'elc_payment_link': 'Payment Link:',
    'elc_payment_hint': '<i>Send USDT to this address on TON Network</i>',
    'btn_open_payment': '🔗 Open Payment',
    'elc_payment_error': '❌ Failed to create payment. Please try again.',
    'elc_balance_error': '❌ Failed to get ELC balance. Please try again.',
    'elc_history_title': '📊 <b>Transaction History</b>',
    'elc_no_transactions': 'No transactions yet.',
    'elc_history_error': '❌ Failed to get transaction history. Please try again.',
    'elc_wallet_connected_title': '🔗 <b>Connected Wallet</b>',
    'elc_wallet_address': 'Address',
    'elc_wallet_type': 'Type',
    'elc_wallet_chain': 'Chain',
    'elc_wallet_connected_at': 'Connected',
    'elc_wallet_hint': '<i>Use this wallet to trade on HyperLiquid without exposing private keys</i>',
    'elc_connect_title': '🔗 <b>Connect Cold Wallet</b>',
    'elc_connect_desc': 'Trade on HyperLiquid without exposing your private keys!',
    'elc_supported_wallets': 'Supported wallets:',
    'elc_wallet_metamask': '• MetaMask (Ethereum, Polygon, BSC)',
    'elc_wallet_wc': '• WalletConnect (Multi-chain)',
    'elc_wallet_tonkeeper': '• Tonkeeper (TON Network)',
    'elc_keys_local': '<i>Your keys never leave your device - all orders are signed locally</i>',
    'btn_metamask': '🦊 MetaMask',
    'btn_walletconnect': '🔗 WalletConnect',
    'btn_tonkeeper': '💎 Tonkeeper',
    'elc_connect_steps_title': '🔗 <b>Connect {wallet}</b>',
    'elc_connect_step1': '1. Open our WebApp',
    'elc_connect_step2': '2. Click \'Connect Wallet\'',
    'elc_connect_step3': '3. Select {wallet}',
    'elc_connect_step4': '4. Approve connection in wallet',
    'elc_connect_keys_hint': '<i>Your private keys stay in your wallet - we only get your public address</i>',
    'btn_open_webapp': '🌐 Open WebApp',
    'elc_disconnected_title': '🔓 <b>Wallet Disconnected</b>',
    'elc_disconnected_msg': 'Your wallet has been successfully disconnected.',
    'elc_disconnected_hint': '<i>You can reconnect anytime to resume cold wallet trading</i>',
    'elc_error_generic': '❌ An error occurred. Please try again.',
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
    'elcaro_entry': '''🔥 *LYXEN* {side_emoji} *{side}*
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
    'elcaro_closed': '''🔥 *LYXEN CLOSED* `{symbol}`

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
}
