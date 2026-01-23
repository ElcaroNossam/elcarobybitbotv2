# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu - BLACK RHETORIC: FOMO + Authority + Exclusivity
    'welcome':                     '''🔥 <b>Vítej, Alpha Tradere!</b>

Zatímco čteš toto — <b>847 traderů</b> už vydělává s Lyxen.

⚡ <b>&lt; 100ms</b> rychlost exekuce
🛡️ <b>664 bezpečnostních testů</b> prošlo
💎 <b>24/7</b> AI-řízené obchodování

<i>Tvoí konkurenti nespí. Lyxen taky ne.</i>

Vyber si cestu k finanční svobodě:''',
    'no_strategies':               '❌ Žádné — <i>Každou sekundu bez strategií ztrácíš peníze</i>',
    'guide_caption':               '📚 <b>TAJEMSTVÍ ELÍTNÍCH TRADERŮ</b>\n\n⚠️ Tyto informace daly našim top traderům <b>nespravedlivou výhodu</b>.\n\n<i>Čas čtení: 3 min. Potenciální zisk: neomezený.</i>',
    'privacy_caption':             '📜 <b>Tvoje bezpečnost = Naše posedlost</b>\n\n🔐 Bankovní šifrování\n✅ Žádné sdílení dat. Nikdy.\n\n<i>Jsi v bezpečných rukou.</i>',
    
    # ═══════════════════════════════════════════════════════════════════
    # MODERN MENU BUTTONS - Stylish & Persuasive
    # ═══════════════════════════════════════════════════════════════════
    'button_api':                  '🔐 Připojit API',
    'button_secret':               '🔑 Tajný klíč',
    'button_api_settings':         '⚙️ Nastavení API',
    'button_subscribe':            '👑 PREMIUM',
    'button_licenses':             '🔑 Licence',
    'button_admin':                '👑 Admin',
    'button_balance':              '� Portfolio',
    'button_orders':               '📊 Příkazy',
    'button_positions':            '🎯 Pozice',
    'button_history':              '📜 Historie',
    'button_strategies':           '🤖 AI Boty',
    'button_api_keys':             '🔑 API Klíče',
    'button_bybit':                '🟠 Bybit',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_switch_bybit':         '🔄 Bybit',
    'button_switch_hl':            '🔄 HyperLiquid',
    'button_percent':              '🎚 % na obchod',
    'button_coins':                '💠 Skupina mincí',
    'button_market':               '📉 Trh',
    'button_manual_order':         '🎯 Sniper',
    'button_update_tpsl':          '🛡️ TP/SL',
    'button_cancel_order':         '❌ Zrušit příkaz',
    'button_limit_only':           '🎯 Pouze Limit',
    'button_toggle_oi':            '� OI Tracker',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_scalper':              '⚡ Scalper',
    'button_elcaro':               '🔥 Lyxen',
    'button_fibonacci':            '📐 Fibonacci',
    'button_settings':             '⚙️ Konfigurace',
    'button_indicators':           '💡 Indikátory',
    'button_support':              '🆘 Podpora',
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
    'atr_mode_changed':            '🔄 Režim TP/SL je nyní: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Pevné %',

    # Limits
    'limit_positions_exceeded':    '🚫 Překročen limit otevřených pozic ({max})',
    'limit_limit_orders_exceeded': '🚫 Překročen limit limitních příkazů ({max})',

    # Languages
    'select_language':             'Vyber jazyk:',
    'language_set':                'Jazyk nastaven na:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'Vyber typ příkazu:',
    'limit_order_format': (
        "Zadej parametry limitního příkazu:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "kde SIDE = LONG nebo SHORT\n"
        "Příklad: `BTCUSDT LONG 20000 0.1`\n\n"
        "Pro zrušení pošli ❌ Zrušit příkaz"
    ),
    'market_order_format': (
        "Zadej parametry market příkazu:\n"
        "`SYMBOL SIDE QTY`\n"
        "kde SIDE = LONG nebo SHORT\n"
        "Příklad: `BTCUSDT SHORT 0.1`\n\n"
        "Pro zrušení pošli ❌ Zrušit příkaz"
    ),
    'order_success':               '✅ Příkaz vytvořen úspěšně!',
    'order_create_error':          '❌ Nepodařilo se vytvořit příkaz: {msg}',
    'order_fail_leverage':         (
        "❌ Příkaz nebyl vytvořen: na tvém Bybit účtu je pro tuto velikost příliš vysoká páka.\n"
        "Sniž páku v nastavení Bybit."
    ),
    'order_parse_error':           '❌ Chyba parsování: {error}',
    'price_error_min':             '❌ Chyba ceny: musí být ≥{min}',
    'price_error_step':            '❌ Chyba ceny: musí být násobkem {step}',
    'qty_error_min':               '❌ Chyba množství: musí být ≥{min}',
    'qty_error_step':              '❌ Chyba množství: musí být násobkem {step}',

    # Loading…
    'loader':                      '⏳ Načítám data…',

    # Market command
    'market_status_heading':       '*Stav trhu:*',
    'market_dominance_header':    'Top Mince dle Dominance',
    'market_total_header':        'Celková Tržní Kapitalizace',
    'market_indices_header':      'Tržní Indexy',
    'usdt_dominance':              'Dominance USDT',
    'btc_dominance':               'Dominance BTC',
    'dominance_rising':            '↑ roste',
    'dominance_falling':           '↓ klesá',
    'dominance_stable':            '↔️ stabilní',
    'dominance_unknown':           '❔ bez dat',
    'btc_price':                   'Cena BTC',
    'last_24h':                    'za posledních 24 h',
    'alt_signal_label':            'Signál altů',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Nejnovější zprávy (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'Nepodařilo se najít cenu provedení pro uzavření',

    # /account
    'account_balance':             '💰 Zůstatek USDT: `{balance:.2f}`',
    'account_realized_header':     '📈 *Realizované PnL:*',
    'account_realized_day':        '  • Dnes : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 dní: `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *Nerealizované PnL:*',
    'account_unreal_total':        '  • Celkem: `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % z IM: `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Tvé nastavení:*',
    'config_percent':              '• 🎚 % na obchod     : `{percent}%`',
    'config_coins':                '• 💠 Mince           : `{coins}`',
    'config_limit_only':           '• 🎯 Limitní příkazy : {state}',
    'config_atr_mode':             '• 🏧 ATR trailing SL : {atr}',
    'config_trade_oi':             '• 📊 Obchodovat OI   : {oi}',
    'config_trade_rsi_bb':         '• 📈 Obchodovat RSI+BB: {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%             : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%             : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 Žádné otevřené příkazy',
    'open_orders_header':          '*📒 Otevřené příkazy:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Směr: `{side}`\n"
        "   • Množ.: `{qty}`\n"
        "   • Cena : `{price}`\n"
        "   • ID   : `{id}`"
    ),
    'open_orders_error':           '❌ Chyba při načítání příkazů: {error}',

    # Manual coin selection
    'enter_coins':                 "Zadej symboly oddělené čárkou, např.:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Vybrané mince: {coins}',

    # Positions
    'no_positions':                '🚫 Žádné otevřené pozice',
    'positions_header':            '📊 Tvé otevřené pozice:',
    'position_item':               (
        "— Pozice #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • Velikost        : {size}\n"
        "  • Vstupní cena    : {avg:.8f}\n"
        "  • Mark cena       : {mark:.8f}\n"
        "  • Likvidace       : {liq}\n"
        "  • Poč. margin     : {im:.2f}\n"
        "  • Udrž. margin    : {mm:.2f}\n"
        "  • Zůstatek pozice : {pm:.2f}\n"
        "  • TP              : {tp}\n"
        "  • SL              : {sl}\n"
        "  • Nereal. PnL     : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'position_item_v2':            (
        "— #{idx}: {symbol} | {side} (x{leverage}) [{strategy}]\n"
        "  • Velikost       : {size}\n"
        "  • Vstupní cena   : {avg:.8f}\n"
        "  • Mark cena      : {mark:.8f}\n"
        "  • Likvidace      : {liq}\n"
        "  • Poč. margin    : {im:.2f}\n"
        "  • Udrž. margin   : {mm:.2f}\n"
        "  • Take Profit    : {tp}\n"
        "  • Stop Loss      : {sl}\n"
        "  {pnl_emoji} Nereal. PnL : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'pnl_by_strategy':             '📊 *PnL podle strategie:*',
    'pnl_by_exchange':             '🏦 *PnL podle burzy:*',
    'positions_overall':           'Celkové nerealizované PnL: {pnl:+.2f} ({pct:+.2f}%)',

    # Position management (inline)
    'open_positions_header':       '📊 *Otevřené pozice*',
    'positions_count':             'pozic',
    'positions_count_total':       'Celkem pozic',
    'total_unrealized_pnl':        'Celkový nereal. P/L',
    'total_pnl':                   'Celkový P/L',
    'btn_close_short':             'Zavřít',
    'btn_close_all':               'Zavřít všechny pozice',
    'btn_close_position':          'Zavřít pozici',
    'btn_confirm_close':           'Potvrdit zavření',
    'btn_confirm_close_all':       'Ano, zavřít všechny',
    'btn_cancel':                  '❌ Zrušit',
    'btn_back':                    '🔙 Zpět',
    'confirm_close_position':      'Zavřít pozici',
    'confirm_close_all':           'Zavřít VŠECHNY pozice',
    'position_not_found':          'Pozice nenalezena nebo již uzavřena',
    'position_already_closed':     'Pozice již uzavřena',
    'position_closed_success':     'Pozice uzavřena',
    'position_close_error':        'Chyba při zavírání pozice',
    'positions_closed':            'Pozice uzavřeny',
    'errors':                      'Chyby',

    # % per trade
    'set_percent_prompt':          'Zadej procento zůstatku na obchod (např. 2.5):',
    'percent_set_success':         '✅ % na obchod nastaveno: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Pouze limitní příkazy: {state}',
    'feature_limit_only':          'Pouze Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Indikátory Lyxen*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. Adaptivní trend',
    'indicator_4':                 '4. Dynamická regrese',

    # Support
    'support_prompt':              '✉️ Potřebuješ pomoc? Klikni dole:',
    'support_button':              'Kontaktovat podporu',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 Žádné otevřené pozice',
    'update_tpsl_prompt':          'Zadej SYMBOL TP SL, např.:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Neplatný formát. Použij: SYMBOL TP SL\nNapř.: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Zadej svůj Bybit API Key:',
    'api_saved':                   '✅ API klíč uložen',
    'enter_secret':                'Zadej svůj Bybit API Secret:',
    'secret_saved':                '✅ API secret uložen',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ Zadej hodnotu TP%',
    'tp_set_success':              '✅ TP% nastaveno: {pct}%',
    'enter_sl':                    '❌ Zadej hodnotu SL%',
    'sl_set_success':              '✅ SL% nastaveno: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: vyžaduje 4 argumenty (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: vyžaduje 3 argumenty (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE musí být LONG nebo SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ API klíč/secret nenastaven',
    'bybit_invalid_response':      '❌ Neplatná odpověď od Bybit',
    'bybit_error':                 '❌ Chyba Bybit {path}: {data}',

    # Auto notifications - BLACK RHETORIC: Excitement & Celebration
    'new_position': (
        '🚀🔥 <b>Nová pozice otevřena!</b>\n'
        '• {symbol} @ {entry:.6f}\n'
        '• Velikost: {size}\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>AI pracuje pro tebe! 🤖</i>'
    ),
    'sl_auto_set':                 '🛑 SL nastaven automaticky: {price:.6f}',
    'auto_close_position':         '⏱ Pozice {symbol} (TF={tf}) otevřená > {tf} a ve ztrátě, uzavřena automaticky.',
    'position_closed': (
        '🎉 <b>Pozice uzavřena!</b> {symbol}\n'
        '• Důvod: <b>{reason}</b>\n'
        '• Strategie: `{strategy}`\n'
        '• Vstup: `{entry:.8f}`\n'
        '• Výstup: `{exit:.8f}`\n'
        '{pnl_emoji} <b>PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`</b>\n'
        '📍 {exchange} • {market_type}'
    ),

    # Entries & errors - jednotný formát s kompletními informacemi
    'oi_limit_entry':              '📉 *OI Limit vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit chyba: {msg}',
    'oi_market_entry':             '📉 *OI Market vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI Market chyba: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Limit vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Market vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Množství: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB Market chyba: {msg}',

    'oi_analysis':                 '📊 *OI analýza {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Limit vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit chyba: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Market vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market chyba: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>Nedostatečný zůstatek!</b>\n\n💰 Na vašem {account_type} účtu není dostatek prostředků k otevření této pozice.\n\n<b>Řešení:</b>\n• Dobijte zůstatek\n• Zmenšete velikost pozice (% na obchod)\n• Snižte páku\n• Zavřete některé otevřené pozice',
    'insufficient_balance_error_extended': '❌ <b>Nedostatečný zůstatek!</b>\n\n📊 Strategie: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Na vašem {account_type} účtu není dostatek prostředků.\n\n<b>Řešení:</b>\n• Dobijte zůstatek\n• Zmenšete velikost pozice (% na obchod)\n• Snižte páku\n• Zavřete některé pozice',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Příliš vysoká páka!</b>\n\n⚙️ Vaše nakonfigurovaná páka překračuje maximum povolené pro tento symbol.\n\n<b>Maximálně povoleno:</b> {max_leverage}x\n\n<b>Řešení:</b> Přejděte do nastavení strategie a snižte páku.',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>Překročen limit pozice!</b>\n\n📊 Strategie: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b>\n\n⚠️ Vaše pozice by překročila maximální limit.\n\n<b>Řešení:</b>\n• Snižte páku\n• Zmenšete velikost pozice\n• Zavřete některé pozice',
    

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Limit vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit chyba: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Market vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market chyba: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Lyxen (Heatmap)
    'elcaro_limit_entry':          '🔥 *Lyxen Limit vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Lyxen Limit chyba: {msg}',
    'elcaro_market_entry':         '🔥 *Lyxen Market vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Lyxen: {side}*\n• {symbol} @ {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Lyxen Market chyba: {msg}',
    'elcaro_analysis':             '🔥 Lyxen Heatmap: {side} @ {price}',
    'feature_elcaro':              'Lyxen',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci Limit vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci Limit chyba: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci Market vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci Market chyba: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 Admin panel:',
    'admin_pause':                 '⏸️ Obchodování a notifikace pozastaveny pro všechny.',
    'admin_resume':                '▶️ Obchodování a notifikace obnoveny pro všechny.',
    'admin_closed':                '✅ Uzavřeno celkem {count} {type}.',
    'admin_canceled_limits':       '✅ Zrušeno {count} limitních příkazů.',

    # Coin groups
    'select_coin_group':           'Vyber skupinu mincí:',
    'group_all':                   'ALL',
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ Skupina mincí nastavena: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *Analýza RSI+BB*\n'
        '• Cena: `{price:.6f}`\n'
        '• RSI: `{rsi:.1f}` ({zone})\n'
        '• BB horní: `{bb_hi:.4f}`\n'
        '• BB dolní: `{bb_lo:.4f}`\n\n'
        '*Vstup MARKET {side} dle RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'Přeprodané (<30)',
    'rsi_zone_overbought':         'Překoupené (>70)',
    'rsi_zone_neutral':            'Neutrální (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ Neplatné TP/SL pro LONG.\n'
        'Aktuální cena: {current:.2f}\n'
        'Očekáváno: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ Neplatné TP/SL pro SHORT.\n'
        'Aktuální cena: {current:.2f}\n'
        'Očekáváno: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 Nemáš otevřenou pozici na {symbol}',
    'tpsl_set_success':            '✅ TP={tp:.2f} a SL={sl:.2f} nastaveno pro {symbol}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Jazyk',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Režim stopu: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ Limit příkaz pro {symbol} vyplněn @ {price}',
    'limit_order_cancelled':       '⚠️ Limit příkaz pro {symbol} (ID: {order_id}) zrušen.',
    'fixed_sl_tp':                 '✅ {symbol}: SL na {sl}, TP na {tp}',
    'tp_part':                     ', TP nastaven na {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL na {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL na {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP inicializován na {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL posunut na BE při {entry}',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP aktualizován na {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Pozice {symbol} uzavřena, ale zápis selhal: {error}\n'
        'Kontaktuj podporu.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Pevné %',

    # System notices
    'db_quarantine_notice':        '⚠️ Logy jsou dočasně pozastaveny. Tichý režim na 1 hodinu.',

    # Fallback
    'fallback':                    '❓ Použij prosím tlačítka menu.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 Máte blokovaný přístup.',
    'invite_only': '🔒 Přístup jen na pozvání. Počkejte na schválení adminem.',
    'need_terms': '⚠️ Nejprve prosím přijměte podmínky: /terms',
    'please_confirm': 'Potvrďte prosím:',
    'terms_ok': '✅ Díky! Podmínky byly přijaty.',
    'terms_declined': '❌ Podmínky jste odmítli. Přístup uzavřen. Můžete se vrátit přes /terms.',
    'usage_approve': 'Použití: /approve <user_id>',
    'usage_ban': 'Použití: /ban <user_id>',
    'not_allowed': 'Nepovoleno',
    'bad_payload': 'Neplatná data',
    'unknown_action': 'Neznámá akce',

    'title': 'Nový uživatel',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Jméno: {name}\n'
        '• Uživatelské jméno: {uname}\n'
        '• Jazyk: {lang}\n'
        '• Povolen: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve': '✅ Schválit',
    'btn_ban': '⛔️ Zabanovat',
    'admin_notify_fail': 'Nepodařilo se upozornit admina: {e}',
    'moderation_approved': '✅ Schváleno: {target}',
    'moderation_banned': '⛔️ Zabanován: {target}',
    'approved_user_dm': '✅ Přístup schválen. Stiskněte /start.',
    'banned_user_dm': '🚫 Máte blokovaný přístup.',

    'users_not_found': '😕 Nebyli nalezeni žádní uživatelé.',
    'users_page_info': '📄 Strana {page}/{pages} — celkem: {total}',
    'user_card_html': (
        '<b>👤 Uživatel</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Jméno: {full_name}\n'
        '• Uživatelské jméno: {uname}\n'
        '• Jazyk: <code>{lang}</code>\n'
        '• Povolen: {allowed}\n'
        '• Zabanován: {banned}\n'
        '• Podmínky: {terms}\n'
        '• % na obchod: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 Blacklist',
    'btn_delete_user': '🗑 Smazat z DB',
    'btn_prev': '⬅️ Zpět',
    'btn_next': '➡️ Další',
    'nav_caption': '🧭 Navigace:',
    'bad_page': 'Neplatná stránka.',
    'admin_user_delete_fail': '❌ Nepodařilo se smazat {target}: {error}',
    'admin_user_deleted': '🗑 Uživatel {target} smazán z DB.',
    'user_access_approved': '✅ Přístup schválen. Stiskněte /start.',

    'admin_pause_all': '⏸️ Pauza pro všechny',
    'admin_resume_all': '▶️ Pokračovat',
    'admin_close_longs': '🔒 Zavřít všechny LONGy',
    'admin_close_shorts': '🔓 Zavřít všechny SHORTy',
    'admin_cancel_limits': '❌ Smazat limitní příkazy',
    'admin_users': '👥 Uživatelé',
    'admin_pause_notice': '⏸️ Obchodování a oznámení pozastaveno pro všechny.',
    'admin_resume_notice': '▶️ Obchodování a oznámení obnoveno pro všechny.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ Uzavřeno celkem {count} {type}.',
    'admin_canceled_limits_total': '✅ Zrušeno {count} limitních příkazů.',

    'terms_btn_accept': '✅ Přijmout',
    'terms_btn_decline': '❌ Odmítnout',

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
    'api_test_success':            'Připojení úspěšné!',
    'api_test_no_keys':            'API klíče nenastaveny',
    'api_test_set_keys':           'Nejprve nastavte API Key a Secret.',
    'api_test_failed':             'Chyba připojení',
    'api_test_error':              'Chyba',
    'api_test_check_keys':         'Zkontrolujte své API údaje.',
    'api_test_status':             'Stav',
    'api_test_connected':          'Připojeno',
    'balance_wallet':              'Zůstatek peněženky',
    'balance_equity':              'Kapitál',
    'balance_available':           'Dostupné',
    'api_missing_notice':          '⚠️ Nemáte nakonfigurováné API klíče burzy. Přidejte prosím svůj API klíč a tajný klíč v nastavení (tlačítka 🔑 API a 🔒 Secret), jinak bot nemůže za vás obchodovat.',
    'elcaro_ai_info':              '🤖 *Obchodování poháněné AI*',

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
    'strat_mode_global':           '🌐 Globální',
    'strat_mode_demo':             '🧪 Demo',
    'strat_mode_real':             '💰 Reálný',
    'strat_mode_both':             '🔄 Oba',
    'strat_mode_changed':          '✅ Režim obchodování {strategy}: {mode}',

    # Lyxen (Heatmap)

    # Fibonacci (Fibonacci Extension)

    # Strategy Settings
    'button_strategy_settings':      '⚙️ Nastavení strategií',
    'strategy_settings_header':      '⚙️ *Nastavení strategií*',
    'strategy_param_header':         '⚙️ *Nastavení {name}*',
    'using_global':                  'Globální nastavení',
    'global_default':                'Globální',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Lyxen',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ Nastavení DCA',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA Krok 1 %',
    'dca_leg2':                      '📉 DCA Krok 2 %',
    'param_percent':                 '📊 Vstup %',
    'param_sl':                      '🔻 Stop-Loss %',
    'param_tp':                      '🔺 Take-Profit %',
    'param_reset':                   '🔄 Obnovit na globální',
    'btn_close':                     '❌ Zavřít',
    'prompt_entry_pct':              'Zadejte % vstupu (riziko na obchod):',
    'prompt_sl_pct':                 'Zadejte % Stop-Loss:',
    'prompt_tp_pct':                 'Zadejte % Take-Profit:',
    'prompt_atr_periods':            'Zadejte periody ATR (např. 7):',
    'prompt_atr_mult':               'Zadejte násobitel ATR pro trailing SL (např. 1.0):',
    'prompt_atr_trigger':            'Zadejte % aktivace ATR (např. 2.0):',
    'prompt_dca_leg1':               'Zadejte % DCA Krok 1 (např. 10):',
    'prompt_dca_leg2':               'Zadejte % DCA Krok 2 (např. 25):',
    'settings_reset':                'Nastavení obnoveno na globální',
    'strat_setting_saved':           '✅ {name} {param} nastaveno na {value}',
    'dca_setting_saved':             '✅ DCA {leg} nastaveno na {value}%',
    'invalid_number':                '❌ Neplatné číslo. Zadejte hodnotu mezi 0 a 100.',
    'dca_10pct':                     'DCA −{pct}%: dokup {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: dokup {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: Krok1=-{dca1}%, Krok2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 Periody ATR',
    'param_atr_mult':                '📉 Násobitel ATR (krok SL)',
    'param_atr_trigger':             '🎯 Aktivace ATR %',

    # Hardcoded strings fix
    'terms_unavailable':             'Podmínky služby nejsou dostupné. Kontaktujte administrátora.',
    'terms_confirm_prompt':          'Potvrďte prosím:',
    'your_id':                       'Vaše ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Chyba: {msg}',
    'error_fetch_balance':           '❌ Chyba při načítání zůstatku: {error}',
    'error_fetch_orders':            '❌ Chyba při načítání objednávek: {error}',
    'error_occurred':                '❌ Chyba: {error}',

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
    'stats_strategy_settings':       'Nastavení strategie',
    'settings_entry_pct':            'Vstup',
    'settings_leverage':             'Páka',
    'settings_trading_mode':         'Režim',
    'settings_direction':            'Směr',
    'stats_all':                     '📈 All',
    'stats_oi':                      '📉 OI',
    'stats_rsi_bb':                  '📊 RSI+BB',
    'stats_scryptomera':             '🐱 Scryptomera',
    'stats_scalper':                 '⚡ Scalper',
    'stats_elcaro':                  '🔥 Lyxen',
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

    # Lyxen AI settings

    # Leverage settings
    'param_leverage': '⚡ Páka',
    'prompt_leverage': 'Zadejte páku (1-100):',
    'auto_default': 'Auto',

    # Lyxen AI
    'elcaro_ai_desc': '_Všechny parametry jsou automaticky parsovány z AI signálů:_',

    # Scalper entries

    # Scryptomera feature
    

    # Limit Ladder
    'limit_ladder': '📉 Limitní žebřík',
    'limit_ladder_header': '📉 *Nastavení limitního žebříku*',
    'limit_ladder_settings': '⚙️ Nastavení žebříku',
    'ladder_count': 'Počet příkazů',
    'ladder_info': 'Limitní příkazy pod vstupem pro DCA. Každý příkaz má % vzdálenosti od vstupu a % depozytu.',
    'prompt_ladder_pct_entry': '📉 Zadejte % pod vstupní cenou pro příkaz {idx}:',
    'prompt_ladder_pct_deposit': '💰 Zadejte % depozytu pro příkaz {idx}:',
    'ladder_order_saved': '✅ Příkaz {idx} uložen: -{pct_entry}% @ {pct_deposit}% depozytu',
    'ladder_orders_placed': '📉 Umístěno {count} limitních příkazů pro {symbol}',
    
    # Spot Trading Mode
    'spot_trading_mode': 'Obchodní režim',
    'spot_btn_mode': 'Režim',
    
    # Stats PnL
    'stats_realized_pnl': 'Realizovaný',
    'stats_unrealized_pnl': 'Nerealizovaný',
    'stats_combined_pnl': 'Kombinovaný',
    'stats_spot': '💹 Spot',
    'stats_spot_title': 'Statistiky Spot DCA',
    'stats_spot_config': 'Konfigurace',
    'stats_spot_holdings': 'Držby',
    'stats_spot_summary': 'Souhrn',
    'stats_spot_current_value': 'Aktuální hodnota',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    'no_license': '⚠️ Potřebujete aktivní předplatné pro použití této funkce.\n\nPoužijte /subscribe k nákupu licence.',
    'no_license_trading': '⚠️ Potřebujete aktivní předplatné pro obchodování.\n\nPoužijte /subscribe k nákupu licence.',
    'license_required': '⚠️ Tato funkce vyžaduje předplatné {required}.\n\nPoužijte /subscribe pro upgrade.',
    'trial_demo_only': '⚠️ Zkušební licence umožňuje pouze demo obchodování.\n\nUpgradujte na Premium nebo Basic pro skutečné obchodování: /subscribe',
    'basic_strategy_limit': '⚠️ Basic licence na skutečném účtu umožňuje pouze: {strategies}\n\nUpgradujte na Premium pro všechny strategie: /subscribe',
    
    'subscribe_menu_header': '💎 *Plány předplatného*',
    'subscribe_menu_info': 'Vyberte si plán pro odemčení obchodních funkcí:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Zkušební (Zdarma)',
    'btn_enter_promo': '🎟 Promo kód',
    'btn_my_subscription': '📋 Moje předplatné',
    
    'premium_title': '� *PREMIUM — Volba vítězů*',
    'premium_desc': '''✅ Plný přístup ke všem funkcím
✅ Všech 5 strategií: OI, RSI+BB, Scryptomera, Scalper, Lyxen
✅ Skutečné + Demo obchodování
✅ Prioritní podpora
✅ Dynamický SL/TP založený na ATR
✅ Limitní žebřík DCA
✅ Všechny budoucí aktualizace''',
    'premium_1m': '💎 1 měsíc — {price} TRC',
    'premium_3m': '💎 3 měsíce — {price} TRC (-10%)',
    'premium_6m': '💎 6 měsíců — {price} TRC (-20%)',
    'premium_12m': '💎 12 měsíců — {price} TRC (-30%)',
    
    'basic_title': '🥈 *BASIC PLÁN*',
    'basic_desc': '''✅ Plný přístup k demo účtu
✅ Skutečný účet: OI, RSI+BB, Scryptomera, Scalper
❌ Lyxen, Fibonacci, Spot — pouze Premium
✅ Standardní podpora
✅ Dynamický SL/TP založený na ATR''',
    'basic_1m': '🥈 1 měsíc — {price} TRC',
    
    'trial_title': '🎁 *BEZPLATNÁ ZKUŠEBNÍ VERZE — Omezená nabídka!*',
    'trial_desc': '''✅ Plný přístup k demo účtu
✅ Všech 5 strategií na demo
❌ Skutečné obchodování není k dispozici
⏰ Trvání: 7 dní
🎁 Pouze jednou''',
    'trial_activate': '🎁 Aktivovat zkušební verzi zdarma',
    'trial_already_used': '⚠️ Již jste využili zkušební verzi zdarma.',
    'trial_activated': '🎉 Zkušební verze aktivována! Máte 7 dní plného demo přístupu.',
    
    'payment_select_method': '💳 *Vyberte způsob platby*',
    'btn_pay_trc': '◈ Triacelo Coin (TRC)',
    'btn_pay_ton': '💎 TON',
    'payment_trc_title': ' Platba přes TRC',
    'payment_trc_desc': 'Bude vám účtováno {amount} TRC za {plan} ({period}).',
    'payment_ton_title': '💎 Platba přes TON',
    'payment_ton_desc': '''Pošlete přesně *{amount} TON* na:

`{wallet}`

Po platbě klikněte na tlačítko níže pro ověření.''',
    'btn_verify_ton': '✅ Zaplatil jsem — Ověřit',
    'payment_processing': '⏳ Zpracování platby...',
    'payment_success': '🎉 Platba úspěšná!\n\n{plan} aktivován do {expires}.',
    'payment_failed': '❌ Platba selhala: {error}',
    
    'my_subscription_header': '📋 *Moje předplatné*',
    'my_subscription_active': '''📋 *Aktuální plán:* {plan}
⏰ *Vyprší:* {expires}
📅 *Zbývající dny:* {days}''',
    'my_subscription_none': '❌ Žádné aktivní předplatné.\n\nPoužijte /subscribe k nákupu plánu.',
    'my_subscription_history': '📜 *Historie plateb:*',
    'subscription_expiring_soon': '⚠️ Vaše předplatné {plan} vyprší za {days} dní!\n\nObnovte nyní: /subscribe',
    
    'promo_enter': '🎟 Zadejte promo kód:',
    'promo_success': '🎉 Promo kód aplikován!\n\n{plan} aktivován na {days} dní.',
    'promo_invalid': '❌ Neplatný promo kód.',
    'promo_expired': '❌ Tento promo kód vypršel.',
    'promo_used': '❌ Tento promo kód byl již použit.',
    'promo_already_used': '❌ Tento promo kód jste již použili.',
    
    'admin_license_menu': '🔑 *Správa licencí*',
    'admin_btn_grant_license': '🎁 Udělit licenci',
    'admin_btn_view_licenses': '📋 Zobrazit licence',
    'admin_btn_create_promo': '🎟 Vytvořit promo',
    'admin_btn_view_promos': '📋 Zobrazit promo',
    'admin_btn_expiring_soon': '⚠️ Brzy vyprší',
    'admin_grant_select_type': 'Vyberte typ licence:',
    'admin_grant_select_period': 'Vyberte období:',
    'admin_grant_enter_user': 'Zadejte ID uživatele:',
    'admin_license_granted': '✅ {plan} uděleno uživateli {uid} na {days} dní.',
    'admin_license_extended': '✅ Licence prodloužena o {days} dní pro uživatele {uid}.',
    'admin_license_revoked': '✅ Licence odvolána pro uživatele {uid}.',
    'admin_promo_created': '✅ Promo kód vytvořen: {code}\nTyp: {type}\nDny: {days}\nMax. použití: {max}',

    'admin_users_management': '👥 Uživatelé',
    'admin_licenses': '🔑 Licence',
    'admin_search_user': '🔍 Najít uživatele',
    'admin_users_menu': '👥 *Správa uživatelů*\n\nVyberte filtr nebo hledejte:',
    'admin_all_users': '👥 Všichni uživatelé',
    'admin_active_users': '✅ Aktivní',
    'admin_banned_users': '🚫 Zabanovaní',
    'admin_no_license': '❌ Bez licence',
    'admin_no_users_found': 'Uživatelé nenalezeni.',
    'admin_enter_user_id': '🔍 Zadejte ID uživatele pro hledání:',
    'admin_user_found': '✅ Uživatel {uid} nalezen!',
    'admin_user_not_found': '❌ Uživatel {uid} nenalezen.',
    'admin_invalid_user_id': '❌ Neplatné ID uživatele. Zadejte číslo.',
    'admin_view_card': '👤 Zobrazit kartu',
    
    'admin_user_card': '''👤 *Karta uživatele*

📋 *ID:* `{uid}`
{status_emoji} *Stav:* {status}
📝 *Podmínky:* {terms}

{license_emoji} *Licence:* {license_type}
📅 *Vyprší:* {license_expires}
⏳ *Zbývající dny:* {days_left}

🌐 *Jazyk:* {lang}
📊 *Obchodní režim:* {trading_mode}
💰 *% na obchod:* {percent}%
🪙 *Mince:* {coins}

🔌 *API klíče:*
  Demo: {demo_api}
  Skutečný: {real_api}

📈 *Strategie:* {strategies}

📊 *Statistiky:*
  Pozice: {positions}
  Obchody: {trades}
  PnL: {pnl}
  Úspěšnost: {winrate}%

💳 *Platby:*
  Celkem: {payments_count}
  TRC: {total_trc}

📅 *První návštěva:* {first_seen}
🕐 *Poslední návštěva:* {last_seen}
''',
    
    'admin_btn_grant_lic': '🎁 Udělit',
    'admin_btn_extend': '⏳ Prodloužit',
    'admin_btn_revoke': '🚫 Odvolat',
    'admin_btn_ban': '🚫 Zabanovat',
    'admin_btn_unban': '✅ Odbanovat',
    'admin_btn_approve': '✅ Schválit',
    'admin_btn_message': '✉️ Zpráva',
    'admin_btn_delete': '🗑 Smazat',
    
    'admin_user_banned': 'Uživatel zabanován!',
    'admin_user_unbanned': 'Uživatel odbanován!',
    'admin_user_approved': 'Uživatel schválen!',
    'admin_confirm_delete': '⚠️ *Potvrdit smazání*\n\nUživatel {uid} bude trvale smazán!',
    'admin_confirm_yes': '✅ Ano, smazat',
    'admin_confirm_no': '❌ Zrušit',
    
    'admin_select_license_type': 'Vyberte typ licence pro uživatele {uid}:',
    'admin_select_period': 'Vyberte období:',
    'admin_select_extend_days': 'Vyberte dny k prodloužení pro uživatele {uid}:',
    'admin_license_granted_short': 'Licence udělena!',
    'admin_license_extended_short': 'Prodlouženo o {days} dní!',
    'admin_license_revoked_short': 'Licence odvolána!',
    
    'admin_enter_message': '✉️ Zadejte zprávu k odeslání uživateli {uid}:',
    'admin_message_sent': '✅ Zpráva odeslána uživateli {uid}!',
    'admin_message_failed': '❌ Odeslání zprávy selhalo: {error}',

    # Auto-synced missing keys
    'admin_all_payments': '📜 Všechny platby',
    'admin_demo_stats': '🎮 Demo statistiky',
    'admin_enter_user_for_report': '👤 Zadejte ID uživatele pro podrobnou zprávu:',
    'admin_generating_report': '📊 Generování zprávy pro uživatele {uid}...',
    'admin_global_stats': '📊 Globální statistiky',
    'admin_no_payments_found': 'Platby nenalezeny.',
    'admin_payments': '💳 Platby',
    'admin_payments_menu': '💳 *Správa plateb*',
    'admin_real_stats': '💰 Reálné statistiky',
    'admin_reports': '📊 Zprávy',
    'admin_reports_menu': '''📊 *Zprávy a analýzy*

Vyberte typ zprávy:''',
    'admin_strategy_breakdown': '🎯 Podle strategie',
    'admin_top_traders': '🏆 Nejlepší tradeři',
    'admin_user_report': '👤 Zpráva uživatele',
    'admin_view_report': '📊 Zobrazit zprávu',
    'admin_view_user': '👤 Karta uživatele',
    'all_positions_closed': 'Všechny pozice uzavřeny',
    'btn_check_again': '🔄 Zkontrolovat znovu',
    'current': 'Aktuální',
    'entry': 'Vstup',
    'max_positions_reached': '⚠️ Dosaženo maximálního počtu pozic. Nové signály budou přeskočeny dokud se pozice nezavře.',
    'payment_session_expired': '❌ Platnost platby vypršela. Začněte prosím znovu.',
    'payment_ton_not_configured': '❌ Platby TON nejsou konfigurovány.',
    'payment_verifying': '⏳ Ověřování platby...',
    'position': 'Pozice',
    'size': 'Velikost',
    'stats_fibonacci': '📐 Fibonacci',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "HyperLiquid obchodování",
    "hl_reset_settings": "🔄 Obnovit nastavení Bybit",

    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ Zrušeno.',
    'entry_pct_range_error': '❌ % vstupu musí být mezi 0.1 a 100.',
    'hl_no_history': '📭 Žádná historie obchodů na HyperLiquid.',
    'hl_no_orders': '📭 Žádné otevřené příkazy na HyperLiquid.',
    'hl_no_positions': '📭 Žádné otevřené pozice na HyperLiquid.',
    'hl_setup_cancelled': '❌ Nastavení HyperLiquid zrušeno.',
    'invalid_amount': '❌ Neplatné číslo. Zadejte platnou částku.',
    'leverage_range_error': '❌ Páka musí být mezi 1 a 100.',
    'max_amount_error': '❌ Maximální částka je 100 000 USDT',
    'min_amount_error': '❌ Minimální částka je 1 USDT',
    'sl_tp_range_error': '❌ SL/TP % musí být mezi 0.1 a 500.',

    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 Aktivovat DCA',
    'btn_ignore': '🔇 Ignorovat',
    'dca_already_enabled': '✅ DCA averaging je již aktivní!\n\n📊 <b>{symbol}</b>\nBot automaticky přikoupí při poklesu:\n• -10% → dokup\n• -25% → dokup\n\nToto pomáhá průměrovat vstupní cenu.',
    'dca_enable_error': '❌ Chyba: {error}',
    'dca_enabled_for_symbol': '✅ DCA aktivováno!\n\n📊 <b>{symbol}</b>\nBot automaticky přikoupí při poklesu:\n• -10% → dokup (průměrování)\n• -25% → dokup (průměrování)\n\n⚠️ DCA vyžaduje dostatečný zůstatek pro další příkazy.',
    'deep_loss_alert': '⚠️ <b>Pozice v hluboké ztrátě!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Ztráta: <code>{loss_pct:.2f}%</code>\n💰 Vstup: <code>{entry}</code>\n📍 Aktuální: <code>{mark}</code>\n\n❌ Stop-loss nelze nastavit nad vstupní cenou.\n\n<b>Co dělat?</b>\n• <b>Zavřít</b> - uzamknout ztrátu\n• <b>DCA</b> - zprůměrovat pozici\n• <b>Ignorovat</b> - nechat tak',
    'deep_loss_close_error': '❌ Chyba při zavírání pozice: {error}',
    'deep_loss_closed': '✅ Pozice {symbol} uzavřena.\n\nZtráta uzamčena. Někdy je lepší přijmout malou ztrátu než doufat v obrat.',
    'deep_loss_ignored': '🔇 Rozumím, pozice {symbol} ponechána beze změny.\n\n⚠️ Pamatujte: bez stop-lossu je riziko ztrát neomezené.\nPozici můžete zavřít ručně přes /positions',
    'fibonacci_desc': '_Vstup, SL, TP - z Fibonacci úrovní v signálu._',
    'fibonacci_info': '📐 *Strategie Fibonacci Extension*',
    'prompt_min_quality': 'Zadejte minimální kvalitu % (0-100):',

    # Hardcore trading phrase
    'hardcore_mode': '💀 *HARDCORE REŽIM*: Žádná milost, žádná lítost. Pouze zisk nebo smrt! 🔥',

    # Wallet & TRC translations

    'payment_trc_insufficient': '''❌ Nedostatečný zůstatek TRC.

Váš zůstatek: {balance} TRC
Požadováno: {required} TRC

Dobijte peněženku pro pokračování.''',
    'wallet_address': '''📍 Adresa: `{address}`''',
    'wallet_balance': '''💰 *Vaše TRC Peněženka*

◈ Zůstatek: *{balance} TRC*
📈 Stakované: *{staked} TRC*
🎁 Čekající odměny: *{rewards} TRC*

💵 Celková hodnota: *${total_usd}*
📍 1 TRC = 1 USDT''',
    'wallet_btn_back': '''« Zpět''',
    'wallet_btn_deposit': '''📥 Vložit''',
    'wallet_btn_history': '''📋 Historie''',
    'wallet_btn_stake': '''📈 Staking''',
    'wallet_btn_unstake': '''📤 Unstake''',
    'wallet_btn_withdraw': '''📤 Vybrat''',
    'wallet_deposit_demo': '''🎁 Získat 100 TRC (Demo)''',
    'wallet_deposit_desc': '''Pošlete TRC tokeny na adresu vaší peněženky:

`{address}`

💡 *Demo režim:* Klikněte níže pro získání bezplatných testovacích tokenů.''',
    'wallet_deposit_success': '''✅ Vloženo {amount} TRC úspěšně!''',
    'wallet_deposit_title': '''📥 *Vklad TRC*''',
    'wallet_history_empty': '''Žádné transakce.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} TRC
   {date}''',
    'wallet_history_title': '''📋 *Historie transakcí*''',
    'wallet_stake_desc': '''Stakujte své TRC tokeny a vydělávejte *12% APY*!

💰 Dostupné: {available} TRC
📈 Aktuálně stakované: {staked} TRC
🎁 Čekající odměny: {rewards} TRC

Denní odměny • Okamžitý výběr''',
    'wallet_stake_success': '''✅ {amount} TRC úspěšně stakované!''',
    'wallet_stake_title': '''📈 *Staking TRC*''',
    'wallet_title': '''◈ *TRC Peněženka*''',
    'wallet_unstake_success': '''✅ Vybráno {amount} TRC + {rewards} TRC odměn!''',
    'wallet_withdraw_desc': '''Zadejte cílovou adresu a částku:''',
    'wallet_withdraw_failed': '''❌ Výběr se nezdařil: {error}''',
    'wallet_withdraw_success': '''✅ Vybráno {amount} TRC na {address}''',
    'wallet_withdraw_title': '''📤 *Výběr TRC*''',

    'spot_freq_biweekly': '📅 Každé 2 týdny',
    'spot_trailing_enabled': '✅ Trailing TP zapnutý: aktivace +{activation}%, trail {trail}%',
    'spot_trailing_disabled': '❌ Trailing TP vypnutý',
    'spot_grid_started': '🔲 Grid bot spuštěn pro {coin}: {levels} úrovní od ${low} do ${high}',
    'spot_grid_stopped': '⏹ Grid bot zastaven pro {coin}',
    'spot_limit_placed': '📝 Limit příkaz zadán: Nákup {amount} {coin} za ${price}',
    'spot_limit_cancelled': '❌ Limit příkaz zrušen pro {coin}',
    'spot_freq_hourly': '⏰ Každou hodinu',

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
}
