# -*- coding: utf-8 -*-
# translations/lt.py — lietuvių
TEXTS = {
    # Main menu
    'welcome':                     '👋 Sveiki! Pasirinkite veiksmą:',
    'no_strategies':               '❌ Nėra',
    'guide_caption':               '📚 Prekybos boto naudotojo vadovas\n\nPerskaitykite šį vadovą, kad sužinotumėte, kaip konfigruoti strategijas ir efektyviai naudoti botą.',
    'privacy_caption':             '📜 Privatumo politika ir naudojimo sąlygos\n\nAtidžiai perskaitykite šį dokumentą.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 Slaptas',
    'button_api_settings':         '🔑 API',
    'button_balance':              '💰 USDT balansas',
    'button_orders':               '📜 Mano įsakymai',
    'button_positions':            '📊 Pozicijos',
    'button_percent':              '🎚 % vienam sandoriui',
    'button_coins':                '💠 Monetų grupė',
    'button_market':               '📈 Rinka',
    'button_manual_order':         '✋ Rankinis įsakymas',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ Atšaukti įsakymą',
    'button_limit_only':           '🎯 Tik Limit',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_settings':             '⚙️ Nustatymai',
    'button_indicators':           '💡 Indikatoriai',
    'button_support':              '🆘 Pagalba',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 TP/SL režimas dabar: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Fiksuota %',

    # Limits
    'limit_positions_exceeded':    '🚫 Viršytas atvirų pozicijų limitas ({max})',
    'limit_limit_orders_exceeded': '🚫 Viršytas Limit įsakymų limitas ({max})',

    # Languages
    'select_language':             'Pasirinkite kalbą:',
    'language_set':                'Kalba nustatyta:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'Pasirinkite įsakymo tipą:',
    'limit_order_format': (
        "Įveskite Limit įsakymo parametrus taip:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "kur SIDE = LONG arba SHORT\n"
        "Pavyzdys: `BTCUSDT LONG 20000 0.1`\n\n"
        "Norėdami atšaukti, siųskite ❌ Atšaukti įsakymą"
    ),
    'market_order_format': (
        "Įveskite Market įsakymo parametrus taip:\n"
        "`SYMBOL SIDE QTY`\n"
        "kur SIDE = LONG arba SHORT\n"
        "Pavyzdys: `BTCUSDT SHORT 0.1`\n\n"
        "Norėdami atšaukti, siųskite ❌ Atšaukti įsakymą"
    ),
    'order_success':               '✅ Įsakymas sėkmingai sukurtas!',
    'order_create_error':          '❌ Nepavyko sukurti įsakymo: {msg}',
    'order_fail_leverage':         (
        "❌ Įsakymas nesukurtas: jūsų Bybit paskyros svertas šiam dydžiui per didelis.\n"
        "Prašome sumažinti svertą Bybit nustatymuose."
    ),
    'order_parse_error':           '❌ Nepavyko apdoroti: {error}',
    'price_error_min':             '❌ Kainos klaida: turi būti ≥{min}',
    'price_error_step':            '❌ Kainos klaida: turi būti {step} kartotinis',
    'qty_error_min':               '❌ Kiekio klaida: turi būti ≥{min}',
    'qty_error_step':              '❌ Kiekio klaida: turi būti {step} kartotinis',

    # Loading…
    'loader':                      '⏳ Renkami duomenys…',

    # Market command
    'market_status_heading':       '*Rinkos būsena:*',
    'market_dominance_header':    'Top Monetos pagal Dominavimą',
    'market_total_header':        'Bendra Rinkos Kapitalizacija',
    'market_indices_header':      'Rinkos Indeksai',
    'usdt_dominance':              'USDT dominavimas',
    'btc_dominance':               'BTC dominavimas',
    'dominance_rising':            '↑ kyla',
    'dominance_falling':           '↓ krenta',
    'dominance_stable':            '↔️ stabili',
    'dominance_unknown':           '❔ nėra duomenų',
    'btc_price':                   'BTC kaina',
    'last_24h':                    'per pastarąsias 24 val.',
    'alt_signal_label':            'Altkoinų signalas',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Naujausios naujienos (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'Nepavyko rasti uždarymui reikalingos vykdymo kainos',

    # /account
    'account_balance':             '💰 USDT balansas: `{balance:.2f}`',
    'account_realized_header':     '📈 *Realizuotas PnL:*',
    'account_realized_day':        '  • Šiandien: `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 d.   : `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *Nerealizuotas PnL:*',
    'account_unreal_total':        '  • Iš viso: `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % nuo IM: `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Jūsų nustatymai:*',
    'config_percent':              '• 🎚 % vienam sandoriui : `{percent}%`',
    'config_coins':                '• 💠 Monetos            : `{coins}`',
    'config_limit_only':           '• 🎯 Tik Limit įsakymai : {state}',
    'config_atr_mode':             '• 🏧 SL pagal ATR       : {atr}',
    'config_trade_oi':             '• 📊 Prekyba pagal OI   : {oi}',
    'config_trade_rsi_bb':         '• 📈 Prekyba RSI+BB     : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%                : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%                : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 Nėra atvirų įsakymų',
    'open_orders_header':          '*📒 Atviri įsakymai:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Pusė : `{side}`\n"
        "   • Kiekis: `{qty}`\n"
        "   • Kaina : `{price}`\n"
        "   • ID    : `{id}`"
    ),
    'open_orders_error':           '❌ Klaida gaunant įsakymus: {error}',

    # Manual coin selection
    'enter_coins':                 "Įveskite simbolius, atskirtus kableliais, pvz.:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Pasirinktos monetos: {coins}',

    # Positions
    'no_positions':                '🚫 Nėra atvirų pozicijų',
    'positions_header':            '📊 Jūsų atviros pozicijos:',
    'position_item':               (
        "— Pozicija #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • Dydis            : {size}\n"
        "  • Įėjimo kaina     : {avg:.8f}\n"
        "  • Žymimoji kaina   : {mark:.8f}\n"
        "  • Likvidacija      : {liq}\n"
        "  • Pradinė marža    : {im:.2f}\n"
        "  • Palaikymo marža  : {mm:.2f}\n"
        "  • Pozicijos balansas: {pm:.2f}\n"
        "  • Take Profit      : {tp}\n"
        "  • Stop Loss        : {sl}\n"
        "  • Nereal. PnL      : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'positions_overall':           'Bendras nereal. PnL: {pnl:+.2f} ({pct:+.2f}%)',

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
    'set_percent_prompt':          'Įveskite balanso procentą vienam sandoriui (pvz., 2.5):',
    'percent_set_success':         '✅ Nustatyta % vienam sandoriui: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Tik Limit įsakymai: {state}',
    'feature_limit_only':          'Tik Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Elcaro indikatoriai*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. Adaptyvus trendas',
    'indicator_4':                 '4. Dinaminė regresija',

    # Support
    'support_prompt':              '✉️ Reikia pagalbos? Spustelėkite žemiau:',
    'support_button':              'Susisiekti su pagalba',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 Nėra atvirų pozicijų',
    'update_tpsl_prompt':          'Įveskite SYMBOL TP SL, pvz.:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Netinkamas formatas. Naudokite: SYMBOL TP SL\nPvz.: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Įveskite Bybit API Key:',
    'api_saved':                   '✅ API raktas išsaugotas',
    'enter_secret':                'Įveskite Bybit API Secret:',
    'secret_saved':                '✅ Slaptas raktas išsaugotas',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ Įveskite TP% reikšmę',
    'tp_set_success':              '✅ TP% nustatyta: {pct}%',
    'enter_sl':                    '❌ Įveskite SL% reikšmę',
    'sl_set_success':              '✅ SL% nustatyta: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: reikia 4 argumentų (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: reikia 3 argumentų (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE turi būti LONG arba SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ API raktas/slaptas nenustatyti',
    'bybit_invalid_response':      '❌ Bybit pateikė netinkamą atsakymą',
    'bybit_error':                 '❌ Bybit klaida {path}: {data}',

    # Auto notifications
    'new_position': (
        '🚀 Nauja pozicija {symbol} @ {entry:.6f}, dydis={size}\n'
        '📍 {exchange} • {market_type}'
    ),
    'sl_auto_set':                 '🛑 SL nustatytas automatiškai: {price:.6f}',
    'auto_close_position':         '⏱ Pozicija {symbol} (TF={tf}) atvira > {tf} ir nuostolinga — uždaryta automatiškai.',
    'position_closed': (
        '🔔 Pozicija {symbol} uždaryta dėl *{reason}*:\n'
        '• Strategy: `{strategy}`\n'
        '• Įėjimas: `{entry:.8f}`\n'
        '• Išėjimas: `{exit:.8f}`\n'
        '• PnL    : `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '📍 {exchange} • {market_type}'
    ),

    # Entries & errors - vieningas formatas su pilna informacija
    'oi_limit_entry':              '📉 *OI Limit įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit klaida: {msg}',
    'oi_market_entry':             '📉 *OI Market įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI Market klaida: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Limit įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Market įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Kiekis: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB Market klaida: {msg}',

    'oi_analysis':                 '📊 *OI {symbol} analizė* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Limit įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit klaida: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Market įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market klaida: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>Nepakankamas balansas!</b>\n\n💰 Jūsų {account_type} paskyroje nepakanka lėšų šiai pozicijai atidaryti.\n\n<b>Sprendimai:</b>\n• Papildykite balansą\n• Sumažinkite pozicijos dydį (% per sandorį)\n• Sumažinkite svertą\n• Uždarykite kai kurias atidarytas pozicijas',
    'insufficient_balance_error_extended': '❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Svertas per didelis!</b>\n\n⚙️ Jūsų nustatytas svertas viršija maksimalų leidžiamą šiam simboliui.\n\n<b>Maksimalus leidžiamas:</b> {max_leverage}x\n\n<b>Sprendimas:</b> Eikite į strategijos nustatymus ir sumažinkite svertą.',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>Viršytas pozicijos limitas!</b>\n\n📊 Strategija: <b>{strategy}</b>\n🪙 Simbolis: <b>{symbol}</b>\n\n⚠️ Jūsų pozicija viršytų maksimalų limitą.\n\n<b>Sprendimai:</b>\n• Sumažinkite svertą\n• Sumažinkite pozicijos dydį\n• Uždarykite dalį pozicijų',
    


    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Limit įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit klaida: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Market įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market klaida: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *Elcaro Limit įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Elcaro Limit klaida: {msg}',
    'elcaro_market_entry':         '🔥 *Elcaro Market įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Elcaro Market klaida: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci Limit įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci Limit klaida: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci Market įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci Market klaida: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 Administratoriaus skydelis:',
    'admin_pause':                 '⏸️ Prekyba ir pranešimai pristabdyti visiems.',
    'admin_resume':                '▶️ Prekyba ir pranešimai atnaujinti visiems.',
    'admin_closed':                '✅ Iš viso uždaryta {count} {type}.',
    'admin_canceled_limits':       '✅ Atšaukta {count} Limit įsakymų.',

    # Coin groups
    'select_coin_group':           'Pasirinkite monetų grupę:',
    'group_all':                   'ALL',
    'group_top100':                'TOP100',
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ Monetų grupė nustatyta: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *RSI+BB analizė*\n'
        '• Kaina: `{price:.6f}`\n'
        '• RSI  : `{rsi:.1f}` ({zone})\n'
        '• BB viršus: `{bb_hi:.4f}`\n'
        '• BB apačia: `{bb_lo:.4f}`\n\n'
        '*MARKET {side} pagal RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'Perparduota (<30)',
    'rsi_zone_overbought':         'Perpirkta (>70)',
    'rsi_zone_neutral':            'Neutrali (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ Netinkami TP/SL LONG pozicijai.\n'
        'Dabartinė kaina: {current:.2f}\n'
        'Tikimasi: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ Netinkami TP/SL SHORT pozicijai.\n'
        'Dabartinė kaina: {current:.2f}\n'
        'Tikimasi: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 Neturite atviros pozicijos {symbol}',
    'tpsl_set_success':            '✅ Nustatyta TP={tp:.2f} ir SL={sl:.2f} porai {symbol}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Kalba',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Stabdymo režimas: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ Limit įsakymas {symbol} įvykdytas @ {price}',
    'limit_order_cancelled':       '⚠️ Limit įsakymas {symbol} (ID: {order_id}) atšauktas.',
    'fixed_sl_tp':                 '✅ {symbol}: SL nustatytas {sl}, TP nustatytas {tp}',
    'tp_part':                     ', TP nustatytas {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL nustatytas {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL nustatytas {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP inicijuota ties {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL perkeltas į breakeven ties {entry}',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP atnaujinta į {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Pozicija {symbol} uždaryta, bet įrašyti nepavyko: {error}\n'
        'Prašome kreiptis į pagalbą.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Fiksuota %',

    # System notices
    'db_quarantine_notice':        '⚠️ Žurnalai laikinai pristabdyti. Tylus režimas 1 valandai.',

    # Fallback
    'fallback':                    '❓ Naudokite meniu mygtukus.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 Jūs esate užblokuotas.',
    'invite_only': '🔒 Tik su kvietimu. Palaukite administratoriaus patvirtinimo.',
    'need_terms': '⚠️ Pirmiausia priimkite taisykles: /terms',
    'please_confirm': 'Patvirtinkite:',
    'terms_ok': '✅ Ačiū! Taisyklės priimtos.',
    'terms_declined': '❌ Atsisakėte taisyklių. Prieiga uždaryta. Galite grįžti su /terms.',
    'usage_approve': 'Naudojimas: /approve <user_id>',
    'usage_ban': 'Naudojimas: /ban <user_id>',
    'not_allowed': 'Neleidžiama',
    'bad_payload': 'Neteisingi duomenys',
    'unknown_action': 'Nežinomas veiksmas',

    'title': 'Naujas naudotojas',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Vardas: {name}\n'
        '• Slapyvardis: {uname}\n'
        '• Kalba: {lang}\n'
        '• Leidžiama: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve': '✅ Patvirtinti',
    'btn_ban': '⛔️ Uždrausti',
    'admin_notify_fail': 'Nepavyko pranešti administratoriui: {e}',
    'moderation_approved': '✅ Patvirtinta: {target}',
    'moderation_banned': '⛔️ Uždrausta: {target}',
    'approved_user_dm': '✅ Prieiga patvirtinta. Spauskite /start.',
    'banned_user_dm': '🚫 Jūs užblokuotas.',

    'users_not_found': '😕 Naudotojų nerasta.',
    'users_page_info': '📄 Puslapis {page}/{pages} — iš viso: {total}',
    'user_card_html': (
        '<b>👤 Naudotojas</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Vardas: {full_name}\n'
        '• Slapyvardis: {uname}\n'
        '• Kalba: <code>{lang}</code>\n'
        '• Leidžiama: {allowed}\n'
        '• Uždrausta: {banned}\n'
        '• Taisyklės: {terms}\n'
        '• % sandoriui: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 Juodasis sąrašas',
    'btn_delete_user': '🗑 Ištrinti iš DB',
    'btn_prev': '⬅️ Atgal',
    'btn_next': '➡️ Pirmyn',
    'nav_caption': '🧭 Navigacija:',
    'bad_page': 'Neteisingas puslapis.',
    'admin_user_delete_fail': '❌ Nepavyko ištrinti {target}: {error}',
    'admin_user_deleted': '🗑 Naudotojas {target} ištrintas iš DB.',
    'user_access_approved': '✅ Prieiga patvirtinta. Spauskite /start.',

    'admin_pause_all': '⏸️ Pauzė visiems',
    'admin_resume_all': '▶️ Tęsti',
    'admin_close_longs': '🔒 Uždaryti visus LONG',
    'admin_close_shorts': '🔓 Uždaryti visus SHORT',
    'admin_cancel_limits': '❌ Pašalinti limitinius įsakymus',
    'admin_users': '👥 Naudotojai',
    'admin_pause_notice': '⏸️ Prekyba ir pranešimai pristabdyti visiems.',
    'admin_resume_notice': '▶️ Prekyba ir pranešimai atnaujinti visiems.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ Iš viso uždaryta {count} {type}.',
    'admin_canceled_limits_total': '✅ Atšaukta {count} limitinių įsakymų.',

    'terms_btn_accept': '✅ Sutinku',
    'terms_btn_decline': '❌ Nesutinku',

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
    'api_test_success':            'Prisijungimas sėkmingas!',
    'api_test_no_keys':            'API raktai nenustatyti',
    'api_test_set_keys':           'Pirmiausia nustatykite API Key ir Secret.',
    'api_test_failed':             'Prisijungimo klaida',
    'api_test_error':              'Klaida',
    'api_test_check_keys':         'Patikrinkite savo API duomenis.',
    'api_test_status':             'Statusas',
    'api_test_connected':          'Prisijungta',
    'balance_wallet':              'Piniginės likutis',
    'balance_equity':              'Kapitalas',
    'balance_available':           'Prieinama',
    'api_missing_notice':          '⚠️ Neturite sukonfigūruotų biržos API raktų. Pridėkite savo API raktą ir slaptažodį nustatymuose (🔑 API ir 🔒 Secret mygtukai), kitaip botas negali prekiauti už jus.',
    'elcaro_ai_info':              '🤖 *AI valdoma prekyba*',

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
    'strat_mode_global':           '🌐 Globalus',
    'strat_mode_demo':             '🧪 Demo',
    'strat_mode_real':             '💰 Realus',
    'strat_mode_both':             '🔄 Abu',
    'strat_mode_changed':          '✅ {strategy} prekybos režimas: {mode}',

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

    'scalper_limit_entry':           'Scalper: limit įsakymas {symbol} @ {price}',
    'scalper_limit_error':           'Scalper limit klaida: {msg}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper klaida: {msg}',

    # Strategy Settings
    'button_strategy_settings':      '⚙️ Strategijų nustatymai',
    'strategy_settings_header':      '⚙️ *Strategijų nustatymai*',
    'strategy_param_header':         '⚙️ *{name} nustatymai*',
    'using_global':                  'Globalūs nustatymai',
    'global_default':                'Globalus',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ DCA nustatymai',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA 1 etapas %',
    'dca_leg2':                      '📉 DCA 2 etapas %',
    'param_percent':                 '📊 Įėjimas %',
    'param_sl':                      '🔻 Stop-Loss %',
    'param_tp':                      '🔺 Take-Profit %',
    'param_reset':                   '🔄 Atstatyti į globalų',
    'btn_close':                     '❌ Uždaryti',
    'prompt_entry_pct':              'Įveskite įėjimo % (rizika vienam sandoriui):',
    'prompt_sl_pct':                 'Įveskite Stop-Loss %:',
    'prompt_tp_pct':                 'Įveskite Take-Profit %:',
    'prompt_atr_periods':            'Įveskite ATR periodus (pvz. 7):',
    'prompt_atr_mult':               'Įveskite ATR daugiklį trailing SL (pvz. 1.0):',
    'prompt_atr_trigger':            'Įveskite ATR aktyvavimo % (pvz. 2.0):',
    'prompt_dca_leg1':               'Įveskite DCA 1 etapo % (pvz. 10):',
    'prompt_dca_leg2':               'Įveskite DCA 2 etapo % (pvz. 25):',
    'settings_reset':                'Nustatymai atstatyti į globalius',
    'strat_setting_saved':           '✅ {name} {param} nustatytas į {value}',
    'dca_setting_saved':             '✅ DCA {leg} nustatytas į {value}%',
    'invalid_number':                '❌ Netinkamas skaičius. Įveskite reikšmę nuo 0 iki 100.',
    'dca_10pct':                     'DCA −{pct}%: papildymas {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: papildymas {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: Etapas1=-{dca1}%, Etapas2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 ATR periodai',
    'param_atr_mult':                '📉 ATR daugiklis (SL žingsnis)',
    'param_atr_trigger':             '🎯 ATR aktyvavimas %',

    # Hardcoded strings fix
    'terms_unavailable':             'Paslaugų sąlygos nepasiekiamos. Susisiekite su administratoriumi.',
    'terms_confirm_prompt':          'Prašome patvirtinti:',
    'your_id':                       'Jūsų ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Klaida: {msg}',
    'error_fetch_balance':           '❌ Klaida gaunant balansą: {error}',
    'error_fetch_orders':            '❌ Klaida gaunant užsakymus: {error}',
    'error_occurred':                '❌ Klaida: {error}',

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
    'stats_strategy_settings':       'Strategijos nustatymai',
    'settings_entry_pct':            'Įėjimas',
    'settings_leverage':             'Svertas',
    'settings_trading_mode':         'Režimas',
    'settings_direction':            'Kryptis',
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
    'param_leverage': '⚡ Svertas',
    'prompt_leverage': 'Įveskite svertą (1-100):',
    'auto_default': 'Automatinis',

    # Elcaro AI
    'elcaro_ai_desc': '_Visi parametrai automatiškai išanalizuojami iš AI signalų:_',

    # Scalper entries
    'scalper_market_entry': '🚀 Scalper market {symbol} @ {price:.6f}',
    'scalper_analysis': 'Scalper: {side} @ {price}',

    # Scryptomera feature
    'feature_scryptomera': 'Scryptomera',
    


    # Limit Ladder
    'limit_ladder': '📉 Limitų kopetlės',
    'limit_ladder_header': '📉 *Limitų kopetelių nustatymai*',
    'limit_ladder_settings': '⚙️ Kopetelių nustatymai',
    'ladder_count': 'Užsakymų skaičius',
    'ladder_info': 'Limit užsakymai žemiau įėjimo DCA. Kiekvienas užsakymas turi % nuo įėjimo ir % depozyto.',
    'prompt_ladder_pct_entry': '📉 Įveskite % žemiau įėjimo kainos užsakymui {idx}:',
    'prompt_ladder_pct_deposit': '💰 Įveskite % depozyto užsakymui {idx}:',
    'ladder_order_saved': '✅ Užsakymas {idx} išsaugotas: -{pct_entry}% @ {pct_deposit}% depozyto',
    'ladder_orders_placed': '📉 Pateikta {count} limitinių užsakymų {symbol}',
    
    # Spot Trading Mode
    'spot_trading_mode': 'Prekybos režimas',
    'spot_btn_mode': 'Režimas',
    
    # Stats PnL
    'stats_realized_pnl': 'Realizuotas',
    'stats_unrealized_pnl': 'Nerealizuotas',
    'stats_combined_pnl': 'Bendras',
    'stats_spot': '💹 Spot',
    'stats_spot_title': 'Spot DCA statistika',
    'stats_spot_config': 'Konfigūracija',
    'stats_spot_holdings': 'Pozicijos',
    'stats_spot_summary': 'Santrauka',
    'stats_spot_current_value': 'Dabartinė vertė',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    'no_license': '⚠️ Jums reikia aktyvios prenumeratos, kad galėtumėte naudoti šią funkciją.\n\nNaudokite /subscribe, kad įsigytumėte licenciją.',
    'no_license_trading': '⚠️ Jums reikia aktyvios prenumeratos, kad galėtumėte prekiauti.\n\nNaudokite /subscribe, kad įsigytumėte licenciją.',
    'license_required': '⚠️ Šiai funkcijai reikia {required} prenumeratos.\n\nNaudokite /subscribe, kad atnaujintumėte.',
    'trial_demo_only': '⚠️ Bandomoji licencija leidžia tik demo prekybą.\n\nAtnaujinkite į Premium arba Basic realiai prekybai: /subscribe',
    'basic_strategy_limit': '⚠️ Basic licencija realioje sąskaitoje leidžia tik: {strategies}\n\nAtnaujinkite į Premium visoms strategijoms: /subscribe',
    
    'subscribe_menu_header': '💎 *Prenumeratos planai*',
    'subscribe_menu_info': 'Pasirinkite planą, kad atrakintumėte prekybos funkcijas:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Bandomoji (Nemokama)',
    'btn_enter_promo': '🎟 Promo kodas',
    'btn_my_subscription': '📋 Mano prenumerata',
    
    'premium_title': '💎 *PREMIUM PLANAS*',
    'premium_desc': '''✅ Pilna prieiga prie visų funkcijų
✅ Visos 5 strategijos: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ Reali + Demo prekyba
✅ Prioritetinė pagalba
✅ Dinaminis SL/TP pagal ATR
✅ Limitų kopetėlės DCA
✅ Visi būsimi atnaujinimai''',
    'premium_1m': '💎 1 mėnuo — {price} TRC',
    'premium_3m': '💎 3 mėnesiai — {price} TRC (-10%)',
    'premium_6m': '💎 6 mėnesiai — {price} TRC (-20%)',
    'premium_12m': '💎 12 mėnesių — {price} TRC (-30%)',
    
    'basic_title': '🥈 *BASIC PLANAS*',
    'basic_desc': '''✅ Pilna prieiga prie demo sąskaitos
✅ Reali sąskaita: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Fibonacci, Spot — tik Premium
✅ Standartinė pagalba
✅ Dinaminis SL/TP pagal ATR''',
    'basic_1m': '🥈 1 mėnuo — {price} TRC',
    
    'trial_title': '🎁 *BANDOMASIS PLANAS (NEMOKAMA)*',
    'trial_desc': '''✅ Pilna prieiga prie demo sąskaitos
✅ Visos 5 strategijos demo
❌ Reali prekyba nepasiekiama
⏰ Trukmė: 7 dienos
🎁 Tik vieną kartą''',
    'trial_activate': '🎁 Aktyvuoti nemokamą bandomąją versiją',
    'trial_already_used': '⚠️ Jau panaudojote nemokamą bandomąją versiją.',
    'trial_activated': '🎉 Bandomoji versija aktyvuota! Turite 7 dienas pilnos demo prieigos.',
    
    'payment_select_method': '💳 *Pasirinkite mokėjimo būdą*',
    'btn_pay_trc': '◈ Triacelo Coin (TRC)',
    'btn_pay_ton': '💎 TON',
    'payment_trc_title': ' Mokėjimas per TRC',
    'payment_trc_desc': 'Bus nuskaičiuota {amount} TRC už {plan} ({period}).',
    'payment_ton_title': '💎 Mokėjimas per TON',
    'payment_ton_desc': '''Siųskite tiksliai *{amount} TON* į:

`{wallet}`

Po mokėjimo paspauskite mygtuką žemiau patikrinimui.''',
    'btn_verify_ton': '✅ Sumokėjau — Patikrinti',
    'payment_processing': '⏳ Apdorojamas mokėjimas...',
    'payment_success': '🎉 Mokėjimas sėkmingas!\n\n{plan} aktyvuotas iki {expires}.',
    'payment_failed': '❌ Mokėjimas nepavyko: {error}',
    
    'my_subscription_header': '📋 *Mano prenumerata*',
    'my_subscription_active': '''📋 *Dabartinis planas:* {plan}
⏰ *Baigiasi:* {expires}
📅 *Likusios dienos:* {days}''',
    'my_subscription_none': '❌ Nėra aktyvios prenumeratos.\n\nNaudokite /subscribe, kad įsigytumėte planą.',
    'my_subscription_history': '📜 *Mokėjimų istorija:*',
    'subscription_expiring_soon': '⚠️ Jūsų {plan} prenumerata baigiasi po {days} dienų!\n\nAtnaujinkite dabar: /subscribe',
    
    'promo_enter': '🎟 Įveskite promo kodą:',
    'promo_success': '🎉 Promo kodas pritaikytas!\n\n{plan} aktyvuotas {days} dienų.',
    'promo_invalid': '❌ Neteisingas promo kodas.',
    'promo_expired': '❌ Šis promo kodas pasibaigęs.',
    'promo_used': '❌ Šis promo kodas jau panaudotas.',
    'promo_already_used': '❌ Jau panaudojote šį promo kodą.',
    
    'admin_license_menu': '🔑 *Licencijų valdymas*',
    'admin_btn_grant_license': '🎁 Suteikti licenciją',
    'admin_btn_view_licenses': '📋 Peržiūrėti licencijas',
    'admin_btn_create_promo': '🎟 Sukurti promo',
    'admin_btn_view_promos': '📋 Peržiūrėti promo',
    'admin_btn_expiring_soon': '⚠️ Greitai baigiasi',
    'admin_grant_select_type': 'Pasirinkite licencijos tipą:',
    'admin_grant_select_period': 'Pasirinkite laikotarpį:',
    'admin_grant_enter_user': 'Įveskite vartotojo ID:',
    'admin_license_granted': '✅ {plan} suteikta vartotojui {uid} {days} dienų.',
    'admin_license_extended': '✅ Licencija pratęsta {days} dienų vartotojui {uid}.',
    'admin_license_revoked': '✅ Licencija atšaukta vartotojui {uid}.',
    'admin_promo_created': '✅ Promo kodas sukurtas: {code}\nTipas: {type}\nDienos: {days}\nMaks. panaudojimų: {max}',

    'admin_users_management': '👥 Vartotojai',
    'admin_licenses': '🔑 Licencijos',
    'admin_search_user': '🔍 Rasti vartotoją',
    'admin_users_menu': '👥 *Vartotojų valdymas*\n\nPasirinkite filtrą arba ieškokite:',
    'admin_all_users': '👥 Visi vartotojai',
    'admin_active_users': '✅ Aktyvūs',
    'admin_banned_users': '🚫 Užblokuoti',
    'admin_no_license': '❌ Be licencijos',
    'admin_no_users_found': 'Vartotojų nerasta.',
    'admin_enter_user_id': '🔍 Įveskite vartotojo ID paieškai:',
    'admin_user_found': '✅ Vartotojas {uid} rastas!',
    'admin_user_not_found': '❌ Vartotojas {uid} nerastas.',
    'admin_invalid_user_id': '❌ Neteisingas vartotojo ID. Įveskite skaičių.',
    'admin_view_card': '👤 Peržiūrėti kortelę',
    
    'admin_user_card': '''👤 *Vartotojo kortelė*

📋 *ID:* `{uid}`
{status_emoji} *Būsena:* {status}
📝 *Sąlygos:* {terms}

{license_emoji} *Licencija:* {license_type}
📅 *Baigiasi:* {license_expires}
⏳ *Likusios dienos:* {days_left}

🌐 *Kalba:* {lang}
📊 *Prekybos režimas:* {trading_mode}
💰 *% sandoriui:* {percent}%
🪙 *Monetos:* {coins}

🔌 *API raktai:*
  Demo: {demo_api}
  Realus: {real_api}

📈 *Strategijos:* {strategies}

📊 *Statistika:*
  Pozicijos: {positions}
  Sandoriai: {trades}
  PnL: {pnl}
  Laimėjimų rodiklis: {winrate}%

💳 *Mokėjimai:*
  Viso: {payments_count}
  TRC: {total_trc}

📅 *Pirmas apsilankymas:* {first_seen}
🕐 *Paskutinis apsilankymas:* {last_seen}
''',
    
    'admin_btn_grant_lic': '🎁 Suteikti',
    'admin_btn_extend': '⏳ Pratęsti',
    'admin_btn_revoke': '🚫 Atšaukti',
    'admin_btn_ban': '🚫 Užblokuoti',
    'admin_btn_unban': '✅ Atblokuoti',
    'admin_btn_approve': '✅ Patvirtinti',
    'admin_btn_message': '✉️ Žinutė',
    'admin_btn_delete': '🗑 Ištrinti',
    
    'admin_user_banned': 'Vartotojas užblokuotas!',
    'admin_user_unbanned': 'Vartotojas atblokuotas!',
    'admin_user_approved': 'Vartotojas patvirtintas!',
    'admin_confirm_delete': '⚠️ *Patvirtinti ištrynimą*\n\nVartotojas {uid} bus visam laikui ištrintas!',
    'admin_confirm_yes': '✅ Taip, ištrinti',
    'admin_confirm_no': '❌ Atšaukti',
    
    'admin_select_license_type': 'Pasirinkite licencijos tipą vartotojui {uid}:',
    'admin_select_period': 'Pasirinkite laikotarpį:',
    'admin_select_extend_days': 'Pasirinkite dienas pratęsimui vartotojui {uid}:',
    'admin_license_granted_short': 'Licencija suteikta!',
    'admin_license_extended_short': 'Pratęsta {days} dienų!',
    'admin_license_revoked_short': 'Licencija atšaukta!',
    
    'admin_enter_message': '✉️ Įveskite žinutę siųsti vartotojui {uid}:',
    'admin_message_sent': '✅ Žinutė išsiųsta vartotojui {uid}!',
    'admin_message_failed': '❌ Nepavyko išsiųsti žinutės: {error}',

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
    "hl_trading_enabled": "HyperLiquid prekyba",
    "hl_reset_settings": "🔄 Atstatyti Bybit nustatymus",



    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ Atšaukta.',
    'entry_pct_range_error': '❌ Įėjimo % turi būti nuo 0.1 iki 100.',
    'hl_no_history': '📭 Nėra prekybos istorijos HyperLiquid.',
    'hl_no_orders': '📭 Nėra atvirų orderių HyperLiquid.',
    'hl_no_positions': '📭 Nėra atvirų pozicijų HyperLiquid.',
    'hl_setup_cancelled': '❌ HyperLiquid nustatymas atšauktas.',
    'invalid_amount': '❌ Neteisingas skaičius. Įveskite tinkamą sumą.',
    'leverage_range_error': '❌ Svertas turi būti nuo 1 iki 100.',
    'max_amount_error': '❌ Maksimali suma 100 000 USDT',
    'min_amount_error': '❌ Minimali suma 1 USDT',
    'sl_tp_range_error': '❌ SL/TP % turi būti nuo 0.1 iki 500.',


    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 Įjungti DCA',
    'btn_ignore': '🔇 Ignoruoti',
    'dca_already_enabled': '✅ DCA jau įjungtas!\n\n📊 <b>{symbol}</b>\nBotas automatiškai pirks kritimo metu:\n• -10% → papildymas\n• -25% → papildymas\n\nTai padeda vidurkinti įėjimo kainą.',
    'dca_enable_error': '❌ Klaida: {error}',
    'dca_enabled_for_symbol': '✅ DCA įjungtas!\n\n📊 <b>{symbol}</b>\nBotas automatiškai pirks kritimo metu:\n• -10% → papildymas (vidurkis)\n• -25% → papildymas (vidurkis)\n\n⚠️ DCA reikia pakankamo balanso papildomiems užsakymams.',
    'deep_loss_alert': '⚠️ <b>Pozicija giliame nuostolyje!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Nuostolis: <code>{loss_pct:.2f}%</code>\n💰 Įėjimas: <code>{entry}</code>\n📍 Dabartinė: <code>{mark}</code>\n\n❌ Stop-loss negali būti nustatytas virš įėjimo kainos.\n\n<b>Ką daryti?</b>\n• <b>Uždaryti</b> - užfiksuoti nuostolį\n• <b>DCA</b> - vidurkinti poziciją\n• <b>Ignoruoti</b> - palikti kaip yra',
    'deep_loss_close_error': '❌ Klaida uždarant poziciją: {error}',
    'deep_loss_closed': '✅ Pozicija {symbol} uždaryta.\n\nNuostolis užfiksuotas. Kartais geriau priimti mažą nuostolį nei tikėtis apsisukimo.',
    'deep_loss_ignored': '🔇 Supratau, pozicija {symbol} palikta nepakeista.\n\n⚠️ Atminkite: be stop-loss, nuostolių rizika yra neribota.\nGalite uždaryti poziciją rankiniu būdu per /positions',
    'fibonacci_desc': '_Įėjimas, SL, TP - iš Fibonacci lygių signale._',
    'fibonacci_info': '📐 *Fibonacci Extension Strategija*',
    'prompt_min_quality': 'Įveskite minimalią kokybę % (0-100):',


    # Hardcore trading phrase
    'hardcore_mode': '💀 *HARDCORE REŽIMAS*: Jokios gailesčio, jokių apgailestavimų. Tik pelnas arba mirtis! 🔥',

    # Wallet & TRC translations

    'payment_trc_insufficient': '''❌ Insufficient TRC balance.

Your balance: {balance} TRC
Required: {required} TRC

Top up your wallet to continue.''',
    'wallet_address': '''📍 Address: `{address}`''',
    'wallet_balance': '''💰 *Your TRC Wallet*

◈ Balance: *{balance} TRC*
📈 Staked: *{staked} TRC*
🎁 Pending Rewards: *{rewards} TRC*

�� Total Value: *${total_usd}*
📍 1 TRC = 1 USDT''',
    'wallet_btn_back': '''« Back''',
    'wallet_btn_deposit': '''📥 Deposit''',
    'wallet_btn_history': '''📋 History''',
    'wallet_btn_stake': '''📈 Stake''',
    'wallet_btn_unstake': '''📤 Unstake''',
    'wallet_btn_withdraw': '''📤 Withdraw''',
    'wallet_deposit_demo': '''🎁 Get 100 TRC (Demo)''',
    'wallet_deposit_desc': '''Send TRC tokens to your wallet address:

`{address}`

💡 *Demo mode:* Click below for free test tokens.''',
    'wallet_deposit_success': '''✅ Deposited {amount} TRC successfully!''',
    'wallet_deposit_title': '''📥 *Deposit TRC*''',
    'wallet_history_empty': '''No transactions yet.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} TRC
   {date}''',
    'wallet_history_title': '''�� *Transaction History*''',
    'wallet_stake_desc': '''Stake your TRC tokens to earn *12% APY*!

💰 Available: {available} TRC
📈 Currently Staked: {staked} TRC
🎁 Pending Rewards: {rewards} TRC

Daily rewards • Instant unstaking''',
    'wallet_stake_success': '''✅ Staked {amount} TRC successfully!''',
    'wallet_stake_title': '''📈 *Stake TRC*''',
    'wallet_title': '''◈ *TRC Wallet*''',
    'wallet_unstake_success': '''✅ Unstaked {amount} TRC + {rewards} TRC rewards!''',
    'wallet_withdraw_desc': '''Enter destination address and amount:''',
    'wallet_withdraw_failed': '''❌ Withdrawal failed: {error}''',
    'wallet_withdraw_success': '''✅ Withdrawn {amount} TRC to {address}''',
    'wallet_withdraw_title': '''📤 *Withdraw TRC*''',


    'spot_freq_biweekly': '📅 Kas 2 savaites',
    'spot_trailing_enabled': '✅ Trailing TP įjungtas: aktyvacija +{activation}%, trail {trail}%',
    'spot_trailing_disabled': '❌ Trailing TP išjungtas',
    'spot_grid_started': '🔲 Grid botas paleistas {coin}: {levels} lygiai nuo ${low} iki ${high}',
    'spot_grid_stopped': '⏹ Grid botas sustabdytas {coin}',
    'spot_limit_placed': '📝 Limito orderis pateiktas: Pirkti {amount} {coin} už ${price}',
    'spot_limit_cancelled': '❌ Limito orderis atšauktas {coin}',
    'spot_freq_hourly': '⏰ Kas valandą',
}
