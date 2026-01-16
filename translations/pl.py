# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu
    'welcome':                     '👋 Cześć! Wybierz działanie:',
    'no_strategies':               '❌ Brak',
    'guide_caption':               '📚 Przewodnik Użytkownika Bota\n\nPrzeczytaj ten przewodnik, aby dowiedzieć się jak skonfigurować strategie i efektywnie korzystać z bota.',
    'privacy_caption':             '📜 Polityka Prywatności i Warunki Użytkowania\n\nProsimy o uważne przeczytanie tego dokumentu.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 Sekret',
    'button_api_settings':         '🔑 API',
    'button_subscribe':            '💎 Subskrybuj',
    'button_licenses':             '🔑 Licencje',
    'button_admin':                '👑 Admin',
    'button_balance':              '💰 Saldo',
    'button_orders':               '📈 Zlecenia',
    'button_positions':            '📊 Pozycje',
    'button_history':              '📋 Historia',
    'button_strategies':           '🤖 Strategie',
    'button_api_keys':             '🔑 Klucze API',
    'button_bybit':                '🟠 Bybit',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_switch_bybit':         '🔄 Bybit',
    'button_switch_hl':            '🔄 HyperLiquid',
    'button_percent':              '🎚 % na transakcję',
    'button_coins':                '💠 Grupa monet',
    'button_market':               '📉 Rynek',
    'button_manual_order':         '✋ Zlecenie ręczne',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ Anuluj zlecenie',
    'button_limit_only':           '🎯 Tylko Limit',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_scalper':              '🎯 Scalper',
    'button_elcaro':               '🔥 Elcaro',
    'button_fibonacci':            '📐 Fibonacci',
    'button_settings':             '📋 Moja Konfiguracja',
    'button_indicators':           '💡 Wskaźniki',
    'button_support':              '🆘 Wsparcie',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',
    'config_trade_scalper':        '🎯 Scalper: {state}',
    'config_trade_elcaro':         '🔥 Elcaro: {state}',
    'config_trade_fibonacci':      '📐 Fibonacci: {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 Tryb TP/SL to teraz: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Stały %',

    # Limits
    'limit_positions_exceeded':    '🚫 Przekroczono limit otwartych pozycji ({max})',
    'limit_limit_orders_exceeded': '🚫 Przekroczono limit zleceń Limit ({max})',

    # Languages
    'select_language':             'Wybierz język:',
    'language_set':                'Ustawiono język:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'Wybierz typ zlecenia:',
    'limit_order_format': (
        "Podaj parametry zlecenia Limit w formacie:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "gdzie SIDE = LONG lub SHORT\n"
        "Przykład: `BTCUSDT LONG 20000 0.1`\n\n"
        "Aby anulować, wyślij ❌ Anuluj zlecenie"
    ),
    'market_order_format': (
        "Podaj parametry zlecenia Market w formacie:\n"
        "`SYMBOL SIDE QTY`\n"
        "gdzie SIDE = LONG lub SHORT\n"
        "Przykład: `BTCUSDT SHORT 0.1`\n\n"
        "Aby anulować, wyślij ❌ Anuluj zlecenie"
    ),
    'order_success':               '✅ Zlecenie utworzone pomyślnie!',
    'order_create_error':          '❌ Nie udało się utworzyć zlecenia: {msg}',
    'order_fail_leverage':         (
        "❌ Zlecenie nieutworzone: dźwignia na Twoim koncie Bybit jest zbyt wysoka dla tego rozmiaru.\n"
        "Zmniejsz dźwignię w ustawieniach Bybit."
    ),
    'order_parse_error':           '❌ Błąd parsowania: {error}',
    'price_error_min':             '❌ Błąd ceny: musi być ≥{min}',
    'price_error_step':            '❌ Błąd ceny: musi być wielokrotnością {step}',
    'qty_error_min':               '❌ Błąd ilości: musi być ≥{min}',
    'qty_error_step':              '❌ Błąd ilości: musi być wielokrotnością {step}',

    # Loading…
    'loader':                      '⏳ Pobieranie danych…',

    # Market command
    'market_status_heading':       '*Sytuacja rynkowa:*',
    'market_dominance_header':    'Top Monety wg Dominacji',
    'market_total_header':        'Całkowita Kapitalizacja',
    'market_indices_header':      'Indeksy Rynkowe',
    'usdt_dominance':              'Dominacja USDT',
    'btc_dominance':               'Dominacja BTC',
    'dominance_rising':            '↑ rośnie',
    'dominance_falling':           '↓ spada',
    'dominance_stable':            '↔️ stabilnie',
    'dominance_unknown':           '❔ brak danych',
    'btc_price':                   'Cena BTC',
    'last_24h':                    'w ostatnich 24 h',
    'alt_signal_label':            'Sygnał altcoin',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Najnowsze wiadomości (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'Nie znaleziono ceny wykonania do zamknięcia',

    # /account
    'account_balance':             '💰 Saldo USDT: `{balance:.2f}`',
    'account_realized_header':     '📈 *Zrealizowany PnL:*',
    'account_realized_day':        '  • Dziś : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 dni: `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *Niezrealizowany PnL:*',
    'account_unreal_total':        '  • Razem: `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % IM  : `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Twoje ustawienia:*',
    'config_percent':              '• 🎚 % na transakcję : `{percent}%`',
    'config_coins':                '• 💠 Monety         : `{coins}`',
    'config_limit_only':           '• 🎯 Zlecenia Limit : {state}',
    'config_atr_mode':             '• 🏧 SL w oparciu o ATR: {atr}',
    'config_trade_oi':             '• 📊 Handel OI      : {oi}',
    'config_trade_rsi_bb':         '• 📈 Handel RSI+BB  : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%            : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%            : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 Brak otwartych zleceń',
    'open_orders_header':          '*📒 Twoje otwarte zlecenia:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Strona: `{side}`\n"
        "   • Ilość : `{qty}`\n"
        "   • Cena  : `{price}`\n"
        "   • ID    : `{id}`"
    ),
    'open_orders_error':           '❌ Błąd pobierania zleceń: {error}',

    # Manual coin selection
    'enter_coins':                 "Podaj symbole oddzielone przecinkami, np.:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Wybrane monety: {coins}',

    # Positions
    'no_positions':                '🚫 Brak otwartych pozycji',
    'positions_header':            '📊 Twoje otwarte pozycje:',
    'position_item':               (
        "— Pozycja #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • Rozmiar         : {size}\n"
        "  • Cena wejścia    : {avg:.8f}\n"
        "  • Cena mark       : {mark:.8f}\n"
        "  • Likwidacja      : {liq}\n"
        "  • Marża początkowa: {im:.2f}\n"
        "  • Marża utrzymania: {mm:.2f}\n"
        "  • Saldo pozycji   : {pm:.2f}\n"
        "  • Take Profit     : {tp}\n"
        "  • Stop Loss       : {sl}\n"
        "  • Niezreal. PnL   : {pnl:+.2f} ({pct:+.2f}%)"
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
    'positions_overall':           'Suma niezreal. PnL: {pnl:+.2f} ({pct:+.2f}%)',

    # Position management (inline)
    'open_positions_header':       '📊 *Otwarte pozycje*',
    'positions_count':             'pozycji',
    'positions_count_total':       'Łącznie pozycji',
    'total_unrealized_pnl':        'Całkowity niezreal. P/L',
    'total_pnl':                   'Całkowity P/L',
    'btn_close_short':             'Zamknij',
    'btn_close_all':               'Zamknij wszystkie pozycje',
    'btn_close_position':          'Zamknij pozycję',
    'btn_confirm_close':           'Potwierdź zamknięcie',
    'btn_confirm_close_all':       'Tak, zamknij wszystkie',
    'btn_cancel':                  '❌ Anuluj',
    'btn_back':                    '🔙 Wstecz',
    'confirm_close_position':      'Zamknij pozycję',
    'confirm_close_all':           'Zamknij WSZYSTKIE pozycje',
    'position_not_found':          'Pozycja nie znaleziona lub już zamknięta',
    'position_already_closed':     'Pozycja już zamknięta',
    'position_closed_success':     'Pozycja zamknięta',
    'position_close_error':        'Błąd zamykania pozycji',
    'positions_closed':            'Pozycje zamknięte',
    'errors':                      'Błędy',

    # % per trade
    'set_percent_prompt':          'Podaj procent salda na transakcję (np. 2.5):',
    'percent_set_success':         '✅ Ustawiono % na transakcję: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Tylko zlecenia Limit: {state}',
    'feature_limit_only':          'Tylko Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Wskaźniki Elcaro*',
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

    # Auto notifications
    'new_position': (
        '🚀 Nowa pozycja {symbol} @ {entry:.6f}, rozmiar={size}\n'
        '📍 {exchange} • {market_type}'
    ),
    'sl_auto_set':                 '🛑 SL ustawiony automatycznie: {price:.6f}',
    'auto_close_position':         '⏱ Pozycja {symbol} (TF={tf}) otwarta > {tf} i stratna – zamknięta automatycznie.',
    'position_closed': (
        '🔔 Pozycja {symbol} zamknięta przez *{reason}*:\n'
        '• Strategy: `{strategy}`\n'
        '• Wejście: `{entry:.8f}`\n'
        '• Wyjście: `{exit:.8f}`\n'
        '• PnL    : `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '📍 {exchange} • {market_type}'
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

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *Elcaro Wejście Limit*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Elcaro Limit błąd: {msg}',
    'elcaro_market_entry':         '🔥 *Elcaro Wejście Market*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Elcaro Market błąd: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

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
    'api_test_success':            'Połączenie udane!',
    'api_test_no_keys':            'Klucze API nie ustawione',
    'api_test_set_keys':           'Najpierw ustaw API Key i Secret.',
    'api_test_failed':             'Błąd połączenia',
    'api_test_error':              'Błąd',
    'api_test_check_keys':         'Sprawdź swoje dane API.',
    'api_test_status':             'Status',
    'api_test_connected':          'Połączono',
    'balance_wallet':              'Saldo portfela',
    'balance_equity':              'Kapitał',
    'balance_available':           'Dostępne',
    'api_missing_notice':          '⚠️ Nie masz skonfigurowanych kluczy API giełdy. Dodaj swój klucz API i sekret w ustawieniach (przyciski 🔑 API i 🔒 Secret), w przeciwnym razie bot nie może handlować za Ciebie.',
    'elcaro_ai_info':              '🤖 *Handel wspierany przez AI*',

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
    'strat_mode_global':           '🌐 Globalny',
    'strat_mode_demo':             '🧪 Demo',
    'strat_mode_real':             '💰 Rzeczywisty',
    'strat_mode_both':             '🔄 Oba',
    'strat_mode_changed':          '✅ Tryb handlu {strategy}: {mode}',

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
    'fibonacci_limit_entry':         '📐 Fibonacci limit-entry {symbol} @ {price:.6f}',
    'fibonacci_limit_error':         '❌ Fibonacci limit-entry error: {msg}',
    'fibonacci_market_entry':        '🚀 Fibonacci market {symbol} @ {price:.6f}',
    'fibonacci_market_error':        '❌ Fibonacci market error: {msg}',
    'fibonacci_market_ok':           '📐 Fibonacci: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'fibonacci_analysis':            'Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    'scalper_limit_entry':           'Scalper: zlecenie limit {symbol} @ {price}',
    'scalper_limit_error':           'Scalper błąd limit: {msg}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper błąd: {msg}',

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
    'strat_elcaro':                  '🔥 Elcaro',
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
    'stats_elcaro':                  '🔥 Elcaro',
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

    # Elcaro AI settings

    # Leverage settings
    'param_leverage': '⚡ Dźwignia',
    'prompt_leverage': 'Podaj dźwignię (1-100):',
    'auto_default': 'Auto',

    # Elcaro AI
    'elcaro_ai_desc': '_Wszystkie parametry są automatycznie parsowane z sygnałów AI:_',

    # Scalper entries
    'scalper_market_entry': '🚀 Scalper market {symbol} @ {price:.6f}',
    'scalper_analysis': 'Scalper: {side} @ {price}',

    # Scryptomera feature
    'feature_scryptomera': 'Scryptomera',
    


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
    'spot_trading_mode': 'Tryb handlu',
    'spot_btn_mode': 'Tryb',
    
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
    
    'no_license': '⚠️ Potrzebujesz aktywnej subskrypcji, aby użyć tej funkcji.\n\nUżyj /subscribe, aby kupić licencję.',
    'no_license_trading': '⚠️ Potrzebujesz aktywnej subskrypcji, aby handlować.\n\nUżyj /subscribe, aby kupić licencję.',
    'license_required': '⚠️ Ta funkcja wymaga subskrypcji {required}.\n\nUżyj /subscribe, aby ulepszyć.',
    'trial_demo_only': '⚠️ Licencja próbna pozwala tylko na handel demo.\n\nUlepsz do Premium lub Basic dla prawdziwego handlu: /subscribe',
    'basic_strategy_limit': '⚠️ Licencja Basic na prawdziwym koncie pozwala tylko: {strategies}\n\nUlepsz do Premium dla wszystkich strategii: /subscribe',
    
    'subscribe_menu_header': '💎 *Plany Subskrypcji*',
    'subscribe_menu_info': 'Wybierz plan, aby odblokować funkcje handlowe:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Próbny (Za darmo)',
    'btn_enter_promo': '🎟 Kod Promo',
    'btn_my_subscription': '📋 Moja Subskrypcja',
    
    'premium_title': '💎 *PLAN PREMIUM*',
    'premium_desc': '''✅ Pełny dostęp do wszystkich funkcji
✅ Wszystkie 5 strategii: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ Handel prawdziwy + Demo
✅ Priorytetowe wsparcie
✅ Dynamiczny SL/TP oparty na ATR
✅ Drabina limitów DCA
✅ Wszystkie przyszłe aktualizacje''',
    'premium_1m': '💎 1 Miesiąc — {price} TRC',
    'premium_3m': '💎 3 Miesiące — {price} TRC (-10%)',
    'premium_6m': '💎 6 Miesięcy — {price} TRC (-20%)',
    'premium_12m': '💎 12 Miesięcy — {price} TRC (-30%)',
    
    'basic_title': '🥈 *PLAN BASIC*',
    'basic_desc': '''✅ Pełny dostęp do konta demo
✅ Prawdziwe konto: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Fibonacci, Spot — tylko Premium
✅ Standardowe wsparcie
✅ Dynamiczny SL/TP oparty na ATR''',
    'basic_1m': '🥈 1 Miesiąc — {price} TRC',
    
    'trial_title': '🎁 *PLAN PRÓBNY (ZA DARMO)*',
    'trial_desc': '''✅ Pełny dostęp do konta demo
✅ Wszystkie 5 strategii na demo
❌ Handel prawdziwy niedostępny
⏰ Czas trwania: 7 dni
🎁 Tylko raz''',
    'trial_activate': '🎁 Aktywuj Darmową Próbę',
    'trial_already_used': '⚠️ Już wykorzystałeś darmową próbę.',
    'trial_activated': '🎉 Próba aktywowana! Masz 7 dni pełnego dostępu demo.',
    
    'payment_select_method': '💳 *Wybierz Metodę Płatności*',
    'btn_pay_trc': '◈ Triacelo Coin (TRC)',
    'btn_pay_ton': '💎 TON',
    'payment_trc_title': ' Płatność przez TRC',
    'payment_trc_desc': 'Zostaniesz obciążony {amount} TRC za {plan} ({period}).',
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
  TRC: {total_trc}

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
    'all_positions_closed': 'Wszystkie pozycje zamknięte',
    'btn_check_again': '🔄 Sprawdź ponownie',
    'button_admin': '👑 Admin',
    'button_licenses': '🔑 Licencje',
    'button_subscribe': '💎 Subskrybuj',
    'current': 'Aktualny',
    'entry': 'Wejście',
    'max_positions_reached': '⚠️ Osiągnięto maksymalną liczbę pozycji. Nowe sygnały będą pomijane do zamknięcia pozycji.',
    'payment_session_expired': '❌ Sesja płatności wygasła. Proszę zacząć od nowa.',
    'payment_ton_not_configured': '❌ Płatności TON nie są skonfigurowane.',
    'payment_verifying': '⏳ Weryfikacja płatności...',
    'position': 'Pozycja',
    'size': 'Rozmiar',
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

    # Wallet & TRC translations

    'payment_trc_insufficient': '''❌ Niewystarczające saldo TRC.

Twoje saldo: {balance} TRC
Wymagane: {required} TRC

Doładuj portfel, aby kontynuować.''',
    'wallet_address': '''📍 Adres: `{address}`''',
    'wallet_balance': '''💰 *Twój Portfel TRC*

◈ Saldo: *{balance} TRC*
📈 W stakingu: *{staked} TRC*
🎁 Oczekujące nagrody: *{rewards} TRC*

💵 Łączna wartość: *${total_usd}*
📍 1 TRC = 1 USDT''',
    'wallet_btn_back': '''« Wstecz''',
    'wallet_btn_deposit': '''📥 Wpłać''',
    'wallet_btn_history': '''📋 Historia''',
    'wallet_btn_stake': '''📈 Staking''',
    'wallet_btn_unstake': '''📤 Wypłać ze stakingu''',
    'wallet_btn_withdraw': '''📤 Wypłać''',
    'wallet_deposit_demo': '''🎁 Odbierz 100 TRC (Demo)''',
    'wallet_deposit_desc': '''Wyślij tokeny TRC na adres portfela:

`{address}`

💡 *Tryb demo:* Kliknij poniżej, aby otrzymać darmowe tokeny testowe.''',
    'wallet_deposit_success': '''✅ Wpłacono {amount} TRC pomyślnie!''',
    'wallet_deposit_title': '''📥 *Wpłata TRC*''',
    'wallet_history_empty': '''Brak transakcji.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} TRC
   {date}''',
    'wallet_history_title': '''📋 *Historia transakcji*''',
    'wallet_stake_desc': '''Stakuj swoje TRC i zarabiaj *12% APY*!

💰 Dostępne: {available} TRC
📈 Obecnie w stakingu: {staked} TRC
🎁 Oczekujące nagrody: {rewards} TRC

Codzienne nagrody • Natychmiastowa wypłata''',
    'wallet_stake_success': '''✅ {amount} TRC pomyślnie zestakowane!''',
    'wallet_stake_title': '''📈 *Staking TRC*''',
    'wallet_title': '''◈ *Portfel TRC*''',
    'wallet_unstake_success': '''✅ Wypłacono {amount} TRC + {rewards} TRC nagród!''',
    'wallet_withdraw_desc': '''Podaj adres docelowy i kwotę:''',
    'wallet_withdraw_failed': '''❌ Wypłata nie powiodła się: {error}''',
    'wallet_withdraw_success': '''✅ Wypłacono {amount} TRC na {address}''',
    'wallet_withdraw_title': '''📤 *Wypłata TRC*''',


    'spot_freq_biweekly': '📅 Co 2 tygodnie',
    'spot_trailing_enabled': '✅ Trailing TP włączony: aktywacja +{activation}%, trail {trail}%',
    'spot_trailing_disabled': '❌ Trailing TP wyłączony',
    'spot_grid_started': '🔲 Grid bot uruchomiony dla {coin}: {levels} poziomów od ${low} do ${high}',
    'spot_grid_stopped': '⏹ Grid bot zatrzymany dla {coin}',
    'spot_limit_placed': '📝 Zlecenie limit złożone: Kup {amount} {coin} za ${price}',
    'spot_limit_cancelled': '❌ Zlecenie limit anulowane dla {coin}',
    'spot_freq_hourly': '⏰ Co godzinę',
}
