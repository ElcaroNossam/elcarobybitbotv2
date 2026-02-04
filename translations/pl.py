# -*- coding: utf-8 -*-
"""
Enliko Trading Tools — Polish Translations (Polski)
Version: 4.0.0 | Updated: 28 January 2026
LEGAL: Educational platform, not financial advice.
"""

TEXTS = {
    # Common UI
    'loader': '⏳ Ładowanie...',
    # =====================================================
    # LEGAL DISCLAIMERS (Zastrzeżenia prawne)
    # =====================================================
    
    'disclaimer_trading': (
        '⚠️ *WAŻNE ZASTRZEŻENIE*\n\n'
        'Ta platforma zapewnia narzędzia edukacyjne do nauki o rynkach kryptowalut.\n'
        'NIE jest to:\n'
        '• Porada finansowa\n'
        '• Rekomendacja inwestycyjna\n'
        '• System gwarantowanego zysku\n\n'
        'Handel kryptowalutami wiąże się ze znacznym ryzykiem straty. '
        'Możesz stracić część lub całość swojej inwestycji. '
        'Handluj tylko środkami, które możesz stracić.\n\n'
        'Wyniki historyczne nie gwarantują przyszłych rezultatów.'
    ),
    
    'disclaimer_short': '⚠️ _Tylko narzędzia edukacyjne. To nie jest porada finansowa. Handel wiąże się z ryzykiem._',
    
    'disclaimer_execution': (
        '⚠️ Kontynuując, potwierdzasz że:\n'
        '• Ponosisz odpowiedzialność za wszystkie decyzje handlowe\n'
        '• To jest narzędzie edukacyjne, nie porada finansowa\n'
        '• Rozumiesz ryzyko handlu kryptowalutami\n'
        '• Wyniki historyczne nie gwarantują przyszłych rezultatów'
    ),
    
    # Welcome - Updated with legal positioning
    'welcome': (
        '📊 *Witamy w Enliko Trading Tools*\n\n'
        '🎯 Platforma edukacyjna:\n'
        '• Śledzenie i analiza portfela\n'
        '• Backtesting strategii\n'
        '• Wizualizacja danych rynkowych\n'
        '• Narzędzia zarządzania ryzykiem\n\n'
        '⚠️ _Tylko do celów edukacyjnych. To nie jest porada finansowa._\n'
        '_Handel wiąże się ze znacznym ryzykiem straty._'
    ),
    
    'welcome_back': (
        '📊 *Enliko Trading Tools*\n\n'
        '⚠️ _Platforma edukacyjna. To nie jest porada finansowa._'
    ),
    
    # Legacy keys
    'button_orders':               '📊 Zlecenia',
    'button_positions':            '🎯 Pozycje',
    'button_history':              '📋 Historia',
    'button_api_keys':             '🔑 Klucze API',
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
    'positions_header':            '📊 Twoje otwarte pozycje:',

    # Position management (inline)
    'btn_close_position':          'Zamknij pozycję',
    'btn_cancel':                  '❌ Anuluj',
    'btn_back':                    '🔙 Wstecz',
    'position_already_closed':     'Pozycja już zamknięta',
    'position_closed_success':     'Pozycja zamknięta',
    'position_close_error':        'Błąd zamykania pozycji',

    # % per trade

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Tylko zlecenia Limit: {state}',
    'feature_limit_only':          'Tylko Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Wskaźniki Enliko*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. Trend adaptacyjny',
    'indicator_4':                 '4. Regresja dynamiczna',

    # Support
    'support_prompt':              '✉️ Potrzebujesz pomocy? Kliknij poniżej:',
    'support_button':              'Skontaktuj się ze wsparciem',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 Brak otwartych pozycji',
    'update_tpsl_prompt':          'Podaj SYMBOL TP SL, np.:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Błędny format. Użyj: SYMBOL TP SL\nNp.: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Podaj klucz Bybit API:',
    'api_saved':                   '✅ Klucz API zapisany',
    'enter_secret':                'Podaj sekret Bybit API:',
    'secret_saved':                '✅ Sekret API zapisany',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ Podaj wartość TP%',
    'tp_set_success':              '✅ Ustawiono TP%: {pct}%',
    'enter_sl':                    '❌ Podaj wartość SL%',
    'sl_set_success':              '✅ Ustawiono SL%: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: wymagane 4 argumenty (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: wymagane 3 argumenty (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE musi być LONG lub SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ Brak klucza/sekretu API',
    'bybit_invalid_response':      '❌ Nieprawidłowa odpowiedź Bybit',
    'bybit_error':                 '❌ Błąd Bybit {path}: {data}',

    # Auto notifications - BLACK RHETORIC: Excitement
    'new_position': (
        '🚀 <b>NOWA POZYCJA OTWARTA!</b>\n\n'
        '💎 {symbol} @ {entry:.6f}\n'
        '📊 Rozmiar: {size}\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>AI Enliko pracuje dla Ciebie 24/7</i>'
    ),
    'sl_auto_set':                 '🛑 SL ustawiony automatycznie: {price:.6f}',
    'auto_close_position':         '⏱ Pozycja {symbol} (TF={tf}) otwarta > {tf} i stratna – zamknięta automatycznie.',
    'position_closed': (
        '🎯 <b>POZYCJA ZAMKNIĘTA!</b>\n\n'
        '📊 {symbol} przez *{reason}*\n'
        '🤖 Strategia: `{strategy}`\n'
        '📈 Wejście: `{entry:.8f}`\n'
        '📉 Wyjście: `{exit:.8f}`\n'
        '💰 PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>Twoje pieniądze pracują gdy śpisz.</i>'
    ),

    # Entries & errors - ujednolicony format z pełnymi info
    'oi_limit_entry':              '📉 *OI Wejście Limit*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit błąd: {msg}',
    'oi_market_entry':             '📉 *OI Wejście Market*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI Market błąd: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Wejście Limit*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Wejście Market*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB Market błąd: {msg}',

    'oi_analysis':                 '📊 *Analiza OI {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Wejście Limit*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit błąd: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Wejście Market*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market błąd: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>Niewystarczające saldo!</b>\n\n💰 Na Twoim koncie {account_type} brakuje środków do otwarcia tej pozycji.\n\n<b>Rozwiązania:</b>\n• Doładuj saldo\n• Zmniejsz rozmiar pozycji (% na transakcję)\n• Zmniejsz dźwignię\n• Zamknij niektóre otwarte pozycje',
    'insufficient_balance_error_extended': '❌ <b>Niewystarczające saldo!</b>\n\n📊 Strategia: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Brakuje środków na koncie {account_type}.\n\n<b>Rozwiązania:</b>\n• Doładuj saldo\n• Zmniejsz rozmiar pozycji (% na transakcję)\n• Zmniejsz dźwignię\n• Zamknij niektóre pozycje',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Zbyt wysoka dźwignia!</b>\n\n⚙️ Skonfigurowana dźwignia przekracza maksimum dozwolone dla tego symbolu.\n\n<b>Maksymalna dozwolona:</b> {max_leverage}x\n\n<b>Rozwiązanie:</b> Przejdź do ustawień strategii i zmniejsz dźwignię.',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>Przekroczono limit pozycji!</b>\n\n📊 Strategia: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b>\n\n⚠️ Twoja pozycja przekroczyłaby maksymalny limit.\n\n<b>Rozwiązania:</b>\n• Zmniejsz dźwignię\n• Zmniejsz rozmiar pozycji\n• Zamknij część pozycji',
    

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Wejście Limit*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit błąd: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Wejście Market*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market błąd: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko Wejście Limit*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Enliko Limit błąd: {msg}',
    'elcaro_market_entry':         '🔥 *Enliko Wejście Market*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Enliko Market błąd: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci Wejście Limit*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci Limit błąd: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci Wejście Market*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci Market błąd: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 Panel administratora:',
    'admin_pause':                 '⏸️ Handel i powiadomienia wstrzymane dla wszystkich.',
    'admin_resume':                '▶️ Handel i powiadomienia wznowione dla wszystkich.',
    'admin_closed':                '✅ Zamknięto łącznie {count} {type}.',
    'admin_canceled_limits':       '✅ Anulowano {count} zleceń Limit.',

    # Coin groups
    'select_coin_group':           'Wybierz grupę monet:',
    'group_all':                   'ALL',
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ Ustawiono grupę monet: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *Analiza RSI+BB*\n'
        '• Cena : `{price:.6f}`\n'
        '• RSI  : `{rsi:.1f}` ({zone})\n'
        '• BB górne: `{bb_hi:.4f}`\n'
        '• BB dolne: `{bb_lo:.4f}`\n\n'
        '*Wejście MARKET {side} wg RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'Wyprzedanie (<30)',
    'rsi_zone_overbought':         'Wykuppienie (>70)',
    'rsi_zone_neutral':            'Neutralny (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ Nieprawidłowe TP/SL dla LONG.\n'
        'Aktualna cena: {current:.2f}\n'
        'Oczekiwane: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ Nieprawidłowe TP/SL dla SHORT.\n'
        'Aktualna cena: {current:.2f}\n'
        'Oczekiwane: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 Nie masz otwartej pozycji na {symbol}',
    'tpsl_set_success':            '✅ Ustawiono TP={tp:.2f} i SL={sl:.2f} dla {symbol}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Język',
    'select_language':             '🌍 Wybierz język:',
    'language_set':                '✅ Język ustawiony:',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Tryb stop: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ Zlecenie Limit dla {symbol} zrealizowane @ {price}',
    'limit_order_cancelled':       '⚠️ Zlecenie Limit dla {symbol} (ID: {order_id}) anulowano.',
    'fixed_sl_tp':                 '✅ {symbol}: SL ustawiony na {sl}, TP na {tp}',
    'tp_part':                     ', TP ustawiony na {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL na {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL na {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP zainicjalizowano na {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL przeniesiony na BE przy {entry}',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP zaktualizowano do {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Pozycja {symbol} zamknięta, ale zapis nie powiódł się: {error}\n'
        'Skontaktuj się ze wsparciem.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Stały %',

    # System notices
    'db_quarantine_notice':        '⚠️ Logi tymczasowo wstrzymane. Tryb cichy na 1 godzinę.',

    # Fallback
    'fallback':                    '❓ Użyj przycisków menu.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 Zostałeś zablokowany.',
    'invite_only': '🔒 Dostęp tylko na zaproszenie. Poczekaj na akceptację admina.',
    'need_terms': '⚠️ Najpierw zaakceptuj regulamin: /terms',
    'please_confirm': 'Proszę potwierdzić:',
    'terms_ok': '✅ Dziękujemy! Regulamin zaakceptowany.',
    'terms_declined': '❌ Odrzuciłeś regulamin. Dostęp zamknięty. Możesz wrócić przez /terms.',
    'usage_approve': 'Użycie: /approve <user_id>',
    'usage_ban': 'Użycie: /ban <user_id>',
    'not_allowed': 'Niedozwolone',
    'bad_payload': 'Nieprawidłowe dane',
    'unknown_action': 'Nieznana akcja',

    'title': 'Nowy użytkownik',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Imię: {name}\n'
        '• Nazwa użytk.: {uname}\n'
        '• Język: {lang}\n'
        '• Dozwolone: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve': '✅ Zatwierdź',
    'btn_ban': '⛔️ Zablokuj',
    'admin_notify_fail': 'Nie udało się powiadomić admina: {e}',
    'moderation_approved': '✅ Zatwierdzono: {target}',
    'moderation_banned': '⛔️ Zablokowano: {target}',
    'approved_user_dm': '✅ Dostęp zatwierdzony. Naciśnij /start.',
    'banned_user_dm': '🚫 Zostałeś zablokowany.',

    'users_not_found': '😕 Nie znaleziono użytkowników.',
    'users_page_info': '📄 Strona {page}/{pages} — razem: {total}',
    'user_card_html': (
        '<b>👤 Użytkownik</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Imię: {full_name}\n'
        '• Nazwa użytk.: {uname}\n'
        '• Język: <code>{lang}</code>\n'
        '• Dozwolone: {allowed}\n'
        '• Zablokowany: {banned}\n'
        '• Regulamin: {terms}\n'
        '• % na transakcję: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 Czarna lista',
    'btn_delete_user': '🗑 Usuń z DB',
    'btn_prev': '⬅️ Wstecz',
    'btn_next': '➡️ Dalej',
    'nav_caption': '🧭 Nawigacja:',
    'bad_page': 'Nieprawidłowa strona.',
    'admin_user_delete_fail': '❌ Nie udało się usunąć {target}: {error}',
    'admin_user_deleted': '🗑 Użytkownik {target} usunięty z DB.',
    'user_access_approved': '✅ Dostęp zatwierdzony. Naciśnij /start.',

    'admin_pause_all': '⏸️ Pauza dla wszystkich',
    'admin_resume_all': '▶️ Wznów',
    'admin_close_longs': '🔒 Zamknij wszystkie LONG',
    'admin_close_shorts': '🔓 Zamknij wszystkie SHORT',
    'admin_cancel_limits': '❌ Usuń zlecenia limit',
    'admin_users': '👥 Użytkownicy',
    'admin_pause_notice': '⏸️ Handel i powiadomienia wstrzymane dla wszystkich.',
    'admin_resume_notice': '▶️ Handel i powiadomienia wznowione dla wszystkich.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ Zamknięto łącznie {count} {type}.',
    'admin_canceled_limits_total': '✅ Anulowano {count} zleceń limit.',

    'terms_btn_accept': '✅ Akceptuję',
    'terms_btn_decline': '❌ Odrzucam',

    'emoji_long': '🟢',
    'emoji_short': '🔴',
    'emoji_neutral': '⚪️',

    # Scalper Strategy

    # API Settings
    'api_key_set':                 '✅ Set',
    'api_test_success':            'Połączenie udane!',
    'api_test_failed':             'Błąd połączenia',
    'balance_equity':              'Kapitał',
    'balance_available':           'Dostępne',
    'api_missing_notice':          '⚠️ Nie masz skonfigurowanych kluczy API giełdy. Dodaj swój klucz API i sekret w ustawieniach (przyciski 🔑 API i 🔒 Secret), w przeciwnym razie bot nie może handlować za Ciebie.',
    'elcaro_ai_info':              '🤖 *Handel wspierany przez AI*',

    # Spot Trading
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_balance':                '💰 Spot Balance: {balance}',

    # Strategy trading mode

    # Enliko (Heatmap)

    # Fibonacci (Fibonacci Extension)

    # Strategy Settings
    'button_strategy_settings':      '⚙️ Ustawienia strategii',
    'strategy_settings_header':      '⚙️ *Ustawienia strategii*',
    'strategy_param_header':         '⚙️ *Ustawienia {name}*',
    'using_global':                  'Ustawienia globalne',
    'global_default':                'Globalny',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Enliko',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ Ustawienia DCA',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA Krok 1 %',
    'dca_leg2':                      '📉 DCA Krok 2 %',
    'param_percent':                 '📊 Wejście %',
    'param_sl':                      '🔻 Stop-Loss %',
    'param_tp':                      '🔺 Take-Profit %',
    'param_reset':                   '🔄 Resetuj do globalnych',
    'btn_close':                     '❌ Zamknij',
    'prompt_entry_pct':              'Wprowadź % wejścia (ryzyko na transakcję):',
    'prompt_sl_pct':                 'Wprowadź % Stop-Loss:',
    'prompt_tp_pct':                 'Wprowadź % Take-Profit:',
    'prompt_atr_periods':            'Wprowadź okresy ATR (np. 7):',
    'prompt_atr_mult':               'Wprowadź mnożnik ATR dla trailing SL (np. 1.0):',
    'prompt_atr_trigger':            'Wprowadź % aktywacji ATR (np. 2.0):',
    'prompt_dca_leg1':               'Wprowadź % DCA Krok 1 (np. 10):',
    'prompt_dca_leg2':               'Wprowadź % DCA Krok 2 (np. 25):',
    'settings_reset':                'Ustawienia zresetowane do globalnych',
    'strat_setting_saved':           '✅ {name} {param} ustawiono na {value}',
    'dca_setting_saved':             '✅ DCA {leg} ustawiono na {value}%',
    'invalid_number':                '❌ Nieprawidłowa liczba. Wprowadź wartość od 0 do 100.',
    'dca_10pct':                     'DCA −{pct}%: dokupienie {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: dokupienie {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: Krok1=-{dca1}%, Krok2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 Okresy ATR',
    'param_atr_mult':                '📉 Mnożnik ATR (krok SL)',
    'param_atr_trigger':             '🎯 Aktywacja ATR %',

    # Break-Even settings UI
    'be_settings_header':            '🔒 *Ustawienia Break-Even*',
    'be_settings_desc':              '_Przesuń SL do ceny wejścia gdy zysk osiągnie % aktywacji_',
    'be_enabled_label':              '🔒 Break-Even',
    'be_trigger_label':              '🎯 Aktywacja BE %',
    'prompt_be_trigger':             'Wprowadź % aktywacji Break-Even (np. 1.0):',
    'prompt_long_be_trigger':        '📈 LONG Aktywacja BE %\n\nWprowadź % zysku do przesunięcia SL do wejścia:',
    'prompt_short_be_trigger':       '📉 SHORT Aktywacja BE %\n\nWprowadź % zysku do przesunięcia SL do wejścia:',
    'param_be_trigger':              '🎯 Aktywacja BE %',
    'be_moved_to_entry':             '🔒 {symbol}: SL przesunięty do break-even @ {entry}',
    'be_status_enabled':             '✅ BE: {trigger}%',
    'be_status_disabled':            '❌ BE: Wyłączony',

    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ Częściowy TP',
    'partial_tp_status_enabled':     '✅ Częściowy TP włączony',
    'partial_tp_status_disabled':    '❌ Częściowy TP wyłączony',
    'partial_tp_step1_menu':         '✂️ *Częściowy TP - Krok 1*\n\nZamknij {close}% pozycji przy +{trigger}% zysku\n\n_Wybierz parametr:_',
    'partial_tp_step2_menu':         '✂️ *Częściowy TP - Krok 2*\n\nZamknij {close}% pozycji przy +{trigger}% zysku\n\n_Wybierz parametr:_',
    'trigger_pct':                   'Aktywacja',
    'close_pct':                     'Zamknij',
    'prompt_long_ptp_1_trigger':     '📈 LONG Krok 1: % Aktywacji\n\nWprowadź % zysku do zamknięcia pierwszej części:',
    'prompt_long_ptp_1_close':       '📈 LONG Krok 1: % Zamknięcia\n\nWprowadź % pozycji do zamknięcia:',
    'prompt_long_ptp_2_trigger':     '📈 LONG Krok 2: % Aktywacji\n\nWprowadź % zysku do zamknięcia drugiej części:',
    'prompt_long_ptp_2_close':       '📈 LONG Krok 2: % Zamknięcia\n\nWprowadź % pozycji do zamknięcia:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT Krok 1: % Aktywacji\n\nWprowadź % zysku do zamknięcia pierwszej części:',
    'prompt_short_ptp_1_close':      '📉 SHORT Krok 1: % Zamknięcia\n\nWprowadź % pozycji do zamknięcia:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT Krok 2: % Aktywacji\n\nWprowadź % zysku do zamknięcia drugiej części:',
    'prompt_short_ptp_2_close':      '📉 SHORT Krok 2: % Zamknięcia\n\nWprowadź % pozycji do zamknięcia:',
    'partial_tp_executed':           '✂️ {symbol}: Zamknięto {close}% przy +{trigger}% zysku',

    # Hardcoded strings fix
    'terms_unavailable':             'Regulamin niedostępny. Skontaktuj się z administratorem.',
    'terms_confirm_prompt':          'Proszę potwierdzić:',
    'your_id':                       'Twoje ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Błąd: {msg}',
    'error_fetch_balance':           '❌ Błąd pobierania salda: {error}',
    'error_fetch_orders':            '❌ Błąd pobierania zleceń: {error}',
    'error_occurred':                '❌ Błąd: {error}',

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
    'stats_strategy_settings':       'Ustawienia strategii',
    'settings_entry_pct':            'Wejście',
    'settings_leverage':             'Dźwignia',
    'settings_trading_mode':         'Tryb',
    'settings_direction':            'Kierunek',
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
    'param_leverage': '⚡ Dźwignia',
    'prompt_leverage': 'Podaj dźwignię (1-100):',
    'auto_default': 'Auto',

    # Enliko AI
    'elcaro_ai_desc': '_Wszystkie parametry są automatycznie parsowane z sygnałów AI:_',

    # Scalper entries

    # Scryptomera feature
    

    # Limit Ladder
    'limit_ladder': '📉 Drabina limitów',
    'limit_ladder_header': '📉 *Ustawienia drabiny limitów*',
    'limit_ladder_settings': '⚙️ Ustawienia drabiny',
    'ladder_count': 'Liczba zleceń',
    'ladder_info': 'Zlecenia limit poniżej wejścia dla DCA. Każde zlecenie ma % odległości od wejścia i % depozytu.',
    'prompt_ladder_pct_entry': '📉 Wprowadź % poniżej ceny wejścia dla zlecenia {idx}:',
    'prompt_ladder_pct_deposit': '💰 Wprowadź % depozytu dla zlecenia {idx}:',
    'ladder_order_saved': '✅ Zlecenie {idx} zapisane: -{pct_entry}% @ {pct_deposit}% depozytu',
    'ladder_orders_placed': '📉 {count} zleceń limit złożonych dla {symbol}',
    
    # Spot Trading Mode
    
    # Stats PnL
    'stats_realized_pnl': 'Zrealizowany',
    'stats_unrealized_pnl': 'Niezrealizowany',
    'stats_combined_pnl': 'Łączny',
    'stats_spot': '💹 Spot',
    'stats_spot_title': 'Statystyki Spot DCA',
    'stats_spot_config': 'Konfiguracja',
    'stats_spot_holdings': 'Pozycje',
    'stats_spot_summary': 'Podsumowanie',
    'stats_spot_current_value': 'Aktualna wartość',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    'no_license': '🚨 <b>DOSTĘP ZABLOKOWANY</b>\n\n⚠️ Podczas gdy to czytasz, traderzy Premium zarabiają.\n\n💎 Odblokuj swój potencjał: /subscribe\n\n<i>Każda minuta czekania = stracone pieniądze</i>',
    'no_license_trading': '🚨 <b>TRADING ZABLOKOWANY</b>\n\n⚠️ 847 traderów zarabia TERAZ z Enliko.\n\n💎 Dołącz do nich: /subscribe\n\n<i>Rynek nie czeka na nikogo.</i>',
    'license_required': '⚠️ Ta funkcja wymaga subskrypcji {required}.\n\nUżyj /subscribe, aby ulepszyć.',
    'trial_demo_only': '⚠️ Licencja próbna pozwala tylko na handel demo.\n\nUlepsz do Premium lub Basic dla prawdziwego handlu: /subscribe',
    'basic_strategy_limit': '⚠️ Licencja Basic na prawdziwym koncie pozwala tylko: {strategies}\n\nUlepsz do Premium dla wszystkich strategii: /subscribe',
    
    # Subscribe menu - BLACK RHETORIC: Exclusivity + Scarcity
    'subscribe_menu_header': '👑 *DOSTĘP VIP do Klubu Elitarnych Traderów*',
    'subscribe_menu_info': '''🔥 <b>847 traderów</b> już zarabia
⚡ Realizacja <100ms | 🛡️ 664 testy bezpieczeństwa

<i>Wybierz swój poziom dostępu:</i>''',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Próbny (Za darmo)',
    'btn_enter_promo': '🎟 Kod Promo',
    'btn_my_subscription': '📋 Moja Subskrypcja',
    
    # Premium plan - BLACK RHETORIC: Authority + Social Proof
    'premium_title': '👑 *PREMIUM — Wybór Zwycięzców*',
    'premium_desc': '''✅ Pełny dostęp do wszystkich funkcji
✅ Wszystkie 5 strategii: OI, RSI+BB, Scryptomera, Scalper, Enliko
✅ Handel prawdziwy + Demo
✅ Priorytetowe wsparcie
✅ Dynamiczny SL/TP oparty na ATR
✅ Drabina limitów DCA
✅ Wszystkie przyszłe aktualizacje''',
    'premium_1m': '💎 1 Miesiąc — {price} ELC',
    'premium_3m': '💎 3 Miesiące — {price} ELC (-10%)',
    'premium_6m': '💎 6 Miesięcy — {price} ELC (-20%)',
    'premium_12m': '💎 12 Miesięcy — {price} ELC (-30%)',
    
    'basic_title': '🥈 *PLAN BASIC*',
    'basic_desc': '''✅ Pełny dostęp do konta demo
✅ Prawdziwe konto: OI, RSI+BB, Scryptomera, Scalper
❌ Enliko, Fibonacci, Spot — tylko Premium
✅ Standardowe wsparcie
✅ Dynamiczny SL/TP oparty na ATR''',
    'basic_1m': '🥈 1 Miesiąc — {price} ELC',
    
    # Trial plan - BLACK RHETORIC: FOMO + Urgency
    'trial_title': '🎁 *BEZPŁATNY PRÓBNY — Limitowana Oferta!*',
    'trial_desc': '''✅ Pełny dostęp do konta demo
✅ Wszystkie 5 strategii na demo
❌ Handel prawdziwy niedostępny
⏰ Czas trwania: 7 dni
🎁 Tylko raz''',
    'trial_activate': '🎁 Aktywuj Darmową Próbę',
    'trial_already_used': '⚠️ Już wykorzystałeś darmową próbę.',
    'trial_activated': '🎉 Próba aktywowana! Masz 7 dni pełnego dostępu demo.',
    
    'payment_select_method': '💳 *Wybierz Metodę Płatności*',
    'btn_pay_elc': '◈ Enliko Coin (ELC)',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' Płatność przez ELC',
    'payment_elc_desc': 'Zostaniesz obciążony {amount} ELC za {plan} ({period}).',
    'payment_ton_title': '💎 Płatność przez TON',
    'payment_ton_desc': '''Wyślij dokładnie *{amount} TON* na:

`{wallet}`

Po płatności kliknij przycisk poniżej, aby zweryfikować.''',
    'btn_verify_ton': '✅ Zapłaciłem — Zweryfikuj',
    'payment_processing': '⏳ Przetwarzanie płatności...',
    'payment_success': '🎉 Płatność udana!\n\n{plan} aktywowany do {expires}.',
    'payment_failed': '❌ Płatność nieudana: {error}',
    
    'my_subscription_header': '📋 *Moja Subskrypcja*',
    'my_subscription_active': '''📋 *Obecny Plan:* {plan}
⏰ *Wygasa:* {expires}
📅 *Dni Pozostało:* {days}''',
    'my_subscription_none': '❌ Brak aktywnej subskrypcji.\n\nUżyj /subscribe, aby kupić plan.',
    'my_subscription_history': '📜 *Historia Płatności:*',
    'subscription_expiring_soon': '⚠️ Twoja subskrypcja {plan} wygasa za {days} dni!\n\nOdnów teraz: /subscribe',
    
    'promo_enter': '🎟 Wprowadź kod promo:',
    'promo_success': '🎉 Kod promo zastosowany!\n\n{plan} aktywowany na {days} dni.',
    'promo_invalid': '❌ Nieprawidłowy kod promo.',
    'promo_expired': '❌ Ten kod promo wygasł.',
    'promo_used': '❌ Ten kod promo został już użyty.',
    'promo_already_used': '❌ Już użyłeś tego kodu promo.',
    
    'admin_license_menu': '🔑 *Zarządzanie Licencjami*',
    'admin_btn_grant_license': '🎁 Przyznaj Licencję',
    'admin_btn_view_licenses': '📋 Pokaż Licencje',
    'admin_btn_create_promo': '🎟 Utwórz Promo',
    'admin_btn_view_promos': '📋 Pokaż Promo',
    'admin_btn_expiring_soon': '⚠️ Wkrótce Wygasa',
    'admin_grant_select_type': 'Wybierz typ licencji:',
    'admin_grant_select_period': 'Wybierz okres:',
    'admin_grant_enter_user': 'Wprowadź ID użytkownika:',
    'admin_license_granted': '✅ {plan} przyznane użytkownikowi {uid} na {days} dni.',
    'admin_license_extended': '✅ Licencja przedłużona o {days} dni dla użytkownika {uid}.',
    'admin_license_revoked': '✅ Licencja cofnięta dla użytkownika {uid}.',
    'admin_promo_created': '✅ Kod promo utworzony: {code}\nTyp: {type}\nDni: {days}\nMaks. użyć: {max}',

    'admin_users_management': '👥 Użytkownicy',
    'admin_licenses': '🔑 Licencje',
    'admin_search_user': '🔍 Znajdź Użytkownika',
    'admin_users_menu': '👥 *Zarządzanie Użytkownikami*\n\nWybierz filtr lub szukaj:',
    'admin_all_users': '👥 Wszyscy Użytkownicy',
    'admin_active_users': '✅ Aktywni',
    'admin_banned_users': '🚫 Zbanowani',
    'admin_no_license': '❌ Bez Licencji',
    'admin_no_users_found': 'Nie znaleziono użytkowników.',
    'admin_enter_user_id': '🔍 Wprowadź ID użytkownika do wyszukania:',
    'admin_user_found': '✅ Użytkownik {uid} znaleziony!',
    'admin_user_not_found': '❌ Użytkownik {uid} nie znaleziony.',
    'admin_invalid_user_id': '❌ Nieprawidłowe ID użytkownika. Wprowadź liczbę.',
    'admin_view_card': '👤 Pokaż Kartę',
    
    'admin_user_card': '''👤 *Karta Użytkownika*

📋 *ID:* `{uid}`
{status_emoji} *Status:* {status}
📝 *Warunki:* {terms}

{license_emoji} *Licencja:* {license_type}
📅 *Wygasa:* {license_expires}
⏳ *Dni Pozostało:* {days_left}

🌐 *Język:* {lang}
📊 *Tryb Handlu:* {trading_mode}
💰 *% na Trade:* {percent}%
🪙 *Monety:* {coins}

🔌 *Klucze API:*
  Demo: {demo_api}
  Prawdziwe: {real_api}

📈 *Strategie:* {strategies}

📊 *Statystyki:*
  Pozycje: {positions}
  Transakcje: {trades}
  PnL: {pnl}
  Winrate: {winrate}%

💳 *Płatności:*
  Razem: {payments_count}
  ELC: {total_elc}

📅 *Pierwsza wizyta:* {first_seen}
🕐 *Ostatnia wizyta:* {last_seen}
''',
    
    'admin_btn_grant_lic': '🎁 Przyznaj',
    'admin_btn_extend': '⏳ Przedłuż',
    'admin_btn_revoke': '🚫 Cofnij',
    'admin_btn_ban': '🚫 Zbanuj',
    'admin_btn_unban': '✅ Odbanuj',
    'admin_btn_approve': '✅ Zatwierdź',
    'admin_btn_message': '✉️ Wiadomość',
    'admin_btn_delete': '🗑 Usuń',
    
    'admin_user_banned': 'Użytkownik zbanowany!',
    'admin_user_unbanned': 'Użytkownik odbanowany!',
    'admin_user_approved': 'Użytkownik zatwierdzony!',
    'admin_confirm_delete': '⚠️ *Potwierdź usunięcie*\n\nUżytkownik {uid} zostanie trwale usunięty!',
    'admin_confirm_yes': '✅ Tak, Usuń',
    'admin_confirm_no': '❌ Anuluj',
    
    'admin_select_license_type': 'Wybierz typ licencji dla użytkownika {uid}:',
    'admin_select_period': 'Wybierz okres:',
    'admin_select_extend_days': 'Wybierz dni do przedłużenia dla użytkownika {uid}:',
    'admin_license_granted_short': 'Licencja przyznana!',
    'admin_license_extended_short': 'Przedłużono o {days} dni!',
    'admin_license_revoked_short': 'Licencja cofnięta!',
    
    'admin_enter_message': '✉️ Wprowadź wiadomość do wysłania użytkownikowi {uid}:',
    'admin_message_sent': '✅ Wiadomość wysłana do użytkownika {uid}!',
    'admin_message_failed': '❌ Nie udało się wysłać wiadomości: {error}',

    # Auto-synced missing keys
    'admin_all_payments': '📜 Wszystkie płatności',
    'admin_demo_stats': '🎮 Statystyki demo',
    'admin_enter_user_for_report': '👤 Wprowadź ID użytkownika dla szczegółowego raportu:',
    'admin_generating_report': '📊 Generowanie raportu dla użytkownika {uid}...',
    'admin_global_stats': '📊 Globalne statystyki',
    'admin_no_payments_found': 'Nie znaleziono płatności.',
    'admin_payments': '💳 Płatności',
    'admin_payments_menu': '💳 *Zarządzanie płatnościami*',
    'admin_real_stats': '💰 Prawdziwe statystyki',
    'admin_reports': '📊 Raporty',
    'admin_reports_menu': '''📊 *Raporty i analityka*

Wybierz typ raportu:''',
    'admin_strategy_breakdown': '🎯 Według strategii',
    'admin_top_traders': '🏆 Najlepsi traderzy',
    'admin_user_report': '👤 Raport użytkownika',
    'admin_view_report': '📊 Pokaż raport',
    'admin_view_user': '👤 Karta użytkownika',
    'btn_check_again': '🔄 Sprawdź ponownie',
    'payment_session_expired': '❌ Sesja płatności wygasła. Proszę zacząć od nowa.',
    'payment_ton_not_configured': '❌ Płatności TON nie są skonfigurowane.',
    'payment_verifying': '⏳ Weryfikacja płatności...',
    'stats_fibonacci': '📐 Fibonacci',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "Handel HyperLiquid",
    "hl_reset_settings": "🔄 Przywróć ustawienia Bybit",

    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ Anulowano.',
    'entry_pct_range_error': '❌ % wejścia musi być między 0.1 a 100.',
    'hl_no_history': '📭 Brak historii transakcji na HyperLiquid.',
    'hl_no_orders': '📭 Brak otwartych zleceń na HyperLiquid.',
    'hl_no_positions': '📭 Brak otwartych pozycji na HyperLiquid.',
    'hl_setup_cancelled': '❌ Konfiguracja HyperLiquid anulowana.',
    'invalid_amount': '❌ Nieprawidłowa liczba. Wprowadź poprawną kwotę.',
    'leverage_range_error': '❌ Dźwignia musi być między 1 a 100.',
    'max_amount_error': '❌ Maksymalna kwota to 100 000 USDT',
    'min_amount_error': '❌ Minimalna kwota to 1 USDT',
    'sl_tp_range_error': '❌ SL/TP % musi być między 0.1 a 500.',

    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 Włącz DCA',
    'btn_ignore': '🔇 Ignoruj',
    'dca_already_enabled': '✅ DCA jest już włączone!\n\n📊 <b>{symbol}</b>\nBot automatycznie dokupuje przy spadku:\n• -10% → dokup\n• -25% → dokup\n\nTo pomaga uśrednić cenę wejścia.',
    'dca_enable_error': '❌ Błąd: {error}',
    'dca_enabled_for_symbol': '✅ DCA włączone!\n\n📊 <b>{symbol}</b>\nBot automatycznie dokupuje przy spadku:\n• -10% → dokup (uśrednianie)\n• -25% → dokup (uśrednianie)\n\n⚠️ DCA wymaga wystarczającego salda na dodatkowe zlecenia.',
    'deep_loss_alert': '⚠️ <b>Pozycja w głębokiej stracie!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Strata: <code>{loss_pct:.2f}%</code>\n💰 Wejście: <code>{entry}</code>\n📍 Obecna: <code>{mark}</code>\n\n❌ Stop-loss nie może być ustawiony powyżej ceny wejścia.\n\n<b>Co robić?</b>\n• <b>Zamknij</b> - zablokuj stratę\n• <b>DCA</b> - uśrednij pozycję\n• <b>Ignoruj</b> - zostaw jak jest',
    'deep_loss_close_error': '❌ Błąd zamykania pozycji: {error}',
    'deep_loss_closed': '✅ Pozycja {symbol} zamknięta.\n\nStrata zablokowana. Czasami lepiej zaakceptować małą stratę niż liczyć na odwrócenie.',
    'deep_loss_ignored': '🔇 Rozumiem, pozycja {symbol} pozostawiona bez zmian.\n\n⚠️ Pamiętaj: bez stop-lossa ryzyko strat jest nieograniczone.\nMożesz zamknąć pozycję ręcznie przez /positions',
    'fibonacci_desc': '_Wejście, SL, TP - z poziomów Fibonacci w sygnale._',
    'fibonacci_info': '📐 *Strategia Fibonacci Extension*',
    'prompt_min_quality': 'Wprowadź minimalną jakość % (0-100):',

    # Hardcore trading phrase
    'hardcore_mode': '💀 *TRYB HARDCORE*: Bez litości, bez żalu. Tylko zysk albo śmierć! 🔥',

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ Niewystarczające saldo ELC.

Twoje saldo: {balance} ELC
Wymagane: {required} ELC

Doładuj portfel, aby kontynuować.''',
    'wallet_address': '''📍 Adres: `{address}`''',
    'wallet_balance': '''💰 *Twój Portfel ELC*

◈ Saldo: *{balance} ELC*
📈 W stakingu: *{staked} ELC*
🎁 Oczekujące nagrody: *{rewards} ELC*

💵 Łączna wartość: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« Wstecz''',
    'wallet_btn_deposit': '''📥 Wpłać''',
    'wallet_btn_history': '''📋 Historia''',
    'wallet_btn_stake': '''📈 Staking''',
    'wallet_btn_unstake': '''📤 Wypłać ze stakingu''',
    'wallet_btn_withdraw': '''📤 Wypłać''',
    'wallet_deposit_demo': '''🎁 Odbierz 100 ELC (Demo)''',
    'wallet_deposit_desc': '''Wyślij tokeny ELC na adres portfela:

`{address}`

💡 *Tryb demo:* Kliknij poniżej, aby otrzymać darmowe tokeny testowe.''',
    'wallet_deposit_success': '''✅ Wpłacono {amount} ELC pomyślnie!''',
    'wallet_deposit_title': '''📥 *Wpłata ELC*''',
    'wallet_history_empty': '''Brak transakcji.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *Historia transakcji*''',
    'wallet_stake_desc': '''Stakuj swoje ELC i zarabiaj *12% APY*!

💰 Dostępne: {available} ELC
📈 Obecnie w stakingu: {staked} ELC
🎁 Oczekujące nagrody: {rewards} ELC

Codzienne nagrody • Natychmiastowa wypłata''',
    'wallet_stake_success': '''✅ {amount} ELC pomyślnie zestakowane!''',
    'wallet_stake_title': '''📈 *Staking ELC*''',
    'wallet_title': '''◈ *Portfel ELC*''',
    'wallet_unstake_success': '''✅ Wypłacono {amount} ELC + {rewards} ELC nagród!''',
    'wallet_withdraw_desc': '''Podaj adres docelowy i kwotę:''',
    'wallet_withdraw_failed': '''❌ Wypłata nie powiodła się: {error}''',
    'wallet_withdraw_success': '''✅ Wypłacono {amount} ELC na {address}''',
    'wallet_withdraw_title': '''📤 *Wypłata ELC*''',

    'spot_freq_hourly': '⏰ Co godzinę',

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
    'error_insufficient_balance': '💰 Niewystarczające środki na koncie do otwarcia pozycji. Doładuj saldo lub zmniejsz rozmiar pozycji.',
    'error_order_too_small': '📉 Rozmiar zlecenia za mały (minimum $5). Zwiększ Entry% lub doładuj saldo.',
    'error_api_key_expired': '🔑 Klucz API wygasł lub jest nieprawidłowy. Zaktualizuj klucze API w ustawieniach.',
    'error_api_key_missing': '🔑 Klucze API nie są skonfigurowane. Dodaj klucze Bybit w menu 🔗 API Keys.',
    'error_rate_limit': '⏳ Zbyt wiele żądań. Poczekaj minutę i spróbuj ponownie.',
    'error_position_not_found': '📊 Pozycja nie znaleziona lub już zamknięta.',
    'error_leverage_error': '⚙️ Błąd ustawienia dźwigni. Spróbuj ustawić dźwignię ręcznie na giełdzie.',
    'error_network_error': '🌐 Problem z siecią. Spróbuj później.',
    'error_sl_tp_invalid': '⚠️ Nie można ustawić SL/TP: cena zbyt blisko aktualnej. Zostanie zaktualizowane w następnym cyklu.',
    'error_equity_zero': '💰 Saldo Twojego konta wynosi zero. Doładuj konto Demo lub Real, aby handlować.',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 Terminal',
    'exchange_mode_activated_bybit': '🟠 *Tryb Bybit aktywowany*',
    'exchange_mode_activated_hl': '🔷 *Tryb HyperLiquid aktywowany*',
    'error_processing_request': '⚠️ Błąd przetwarzania żądania',
    'unauthorized_admin': '❌ Brak autoryzacji. To polecenie jest tylko dla administratora.',
    'error_loading_dashboard': '❌ Błąd ładowania panelu.',
    'unauthorized': '❌ Brak autoryzacji.',
    'processing_blockchain': '⏳ Przetwarzanie transakcji blockchain...',
    'verifying_payment': '⏳ Weryfikacja płatności w blockchain TON...',
    'no_wallet_configured': '❌ Portfel nie skonfigurowany.',
    'use_start_menu': 'Użyj /start aby wrócić do menu głównego.',

    # 2FA Potwierdzenie logowania
    'login_approved': '✅ Logowanie zatwierdzone!\n\nMożesz teraz kontynuować w przeglądarce.',
    'login_denied': '❌ Logowanie odrzucone.\n\nJeśli to nie byłeś Ty, sprawdź ustawienia bezpieczeństwa.',
    'login_expired': '⏰ Potwierdzenie wygasło. Spróbuj ponownie.',
    'login_error': '⚠️ Błąd przetwarzania. Spróbuj później.',

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
    "basic_bybit_only": "⚠️ *Basic Plan Limitation*\n\nBasic plan supports Bybit only.\nHyperLiquid is available on Premium.\n\n👉 /subscribe — Upgrade to Premium",
    "btn_check_payment": "✅ Check Payment",
    "btn_copy_address": "📋 Copy Address",
    "btn_new_currency": "🔄 Different Currency",
    "btn_retry": "🔄 Retry",
    "button_balance": "💎 Portfolio",
    "button_coins": "🪙 Coins",
    "button_elcaro": "🎯 Elcaro",
    "button_fibonacci": "📐 Fibonacci",
    "button_indicators": "📊 Indicators",
    "button_limit_only": "📝 Limit Only",
    "button_market": "📈 Market",
    "button_scalper": "⚡ Scalper",
    "button_scryptomera": "🔮 Scryptomera",
    "button_strategies": "🤖 AI Bots",
    "button_subscribe": "👑 PREMIUM",
    "button_support": "📞 Support",
    "button_terminal": "💻 Terminal",
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
}
