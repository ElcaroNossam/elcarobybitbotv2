# -*- coding: utf-8 -*-
"""
Enliko Trading Tools — Lithuanian Translations (Lietuvių)
Version: 4.0.0 | Updated: 28 January 2026
LEGAL: Educational platform, not financial advice.
"""

TEXTS = {
    # =====================================================
    # LEGAL DISCLAIMERS (Teisiniai atsakomybės atsisakymai)
    # =====================================================
    
    'disclaimer_trading': (
        '⚠️ *SVARBUS PAREIŠKIMAS*\n\n'
        'Ši platforma teikia švietimo priemones kriptovaliutų rinkoms pažinti.\n'
        'Tai NĖRA:\n'
        '• Finansinė konsultacija\n'
        '• Investicijų rekomendacija\n'
        '• Garantuoto pelno sistema\n\n'
        'Prekyba kriptovaliutomis susijusi su didele nuostolių rizika. '
        'Galite prarasti dalį arba visą savo investiciją. '
        'Prekiaukite tik tais pinigais, kuriuos galite sau leisti prarasti.\n\n'
        'Ankstesni rezultatai negarantuoja būsimų rezultatų.'
    ),
    
    'disclaimer_short': '⚠️ _Tik švietimo priemonės. Tai nėra finansinė konsultacija. Prekyba susijusi su rizika._',
    
    'disclaimer_execution': (
        '⚠️ Tęsdami, jūs patvirtinate, kad:\n'
        '• Esate atsakingi už visus prekybos sprendimus\n'
        '• Tai švietimo priemonė, ne finansinė konsultacija\n'
        '• Suprantate kriptovaliutų prekybos riziką\n'
        '• Ankstesni rezultatai negarantuoja būsimų rezultatų'
    ),
    
    # Welcome - Updated with legal positioning
    'welcome': (
        '📊 *Sveiki atvykę į Enliko Trading Tools*\n\n'
        '🎯 Švietimo platforma:\n'
        '• Portfelio stebėjimas ir analizė\n'
        '• Strategijų testavimas\n'
        '• Rinkos duomenų vizualizacija\n'
        '• Rizikos valdymo priemonės\n\n'
        '⚠️ _Tik švietimo tikslais. Tai nėra finansinė konsultacija._\n'
        '_Prekyba susijusi su didele nuostolių rizika._'
    ),
    
    'welcome_back': (
        '📊 *Enliko Trading Tools*\n\n'
        '⚠️ _Švietimo platforma. Tai nėra finansinė konsultacija._'
    ),
    
    # Legacy keys
    'button_orders':               '📊 Įsakymai',
    'button_positions':            '🎯 Pozicijos',
    'button_history':              '📜 Istorija',
    'button_api_keys':             '🔑 API raktai',
    'button_settings':             '⚙️ Nustatymai',

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
    'positions_header':            '📊 Jūsų atviros pozicijos:',

    # Position management (inline)
    'btn_close_position':          'Uždaryti poziciją',
    'btn_cancel':                  '❌ Atšaukti',
    'btn_back':                    '🔙 Atgal',
    'position_already_closed':     'Pozicija jau uždaryta',
    'position_closed_success':     'Pozicija uždaryta',
    'position_close_error':        'Klaida uždarant poziciją',

    # % per trade

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Tik Limit įsakymai: {state}',
    'feature_limit_only':          'Tik Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Enliko indikatoriai*',
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

    # Auto notifications - BLACK RHETORIC: Excitement & Celebration
    'new_position': (
        '🚀🔥 <b>Nauja pozicija atidaryta!</b>\n'
        '• {symbol} @ {entry:.6f}\n'
        '• Dydis: {size}\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>AI dirba jums! 🤖</i>'
    ),
    'sl_auto_set':                 '🛑 SL nustatytas automatiškai: {price:.6f}',
    'auto_close_position':         '⏱ Pozicija {symbol} (TF={tf}) atvira > {tf} ir nuostolinga — uždaryta automatiškai.',
    'position_closed': (
        '🎉 <b>Pozicija uždaryta!</b> {symbol}\n'
        '• Priežastis: <b>{reason}</b>\n'
        '• Strategija: `{strategy}`\n'
        '• Įėjimas: `{entry:.8f}`\n'
        '• Išėjimas: `{exit:.8f}`\n'
        '{pnl_emoji} <b>PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`</b>\n'
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
    'insufficient_balance_error_extended': '❌ <b>Nepakankamas balansas!</b>\n\n📊 Strategija: <b>{strategy}</b>\n🪙 Simbolis: <b>{symbol}</b> {side}\n\n💰 Jūsų {account_type} paskyroje nepakanka lėšų.\n\n<b>Sprendimai:</b>\n• Papildykite balansą\n• Sumažinkite pozicijos dydį (% per sandorį)\n• Sumažinkite svertą\n• Uždarykite kai kurias pozicijas',

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

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko Limit įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Enliko Limit klaida: {msg}',
    'elcaro_market_entry':         '🔥 *Enliko Market įėjimas*\n• {symbol} {side}\n• Kaina: {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• Kiekis: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Enliko Market klaida: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

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
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
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
    'select_language':             '🌍 Pasirinkite kalbą:',
    'language_set':                '✅ Kalba nustatyta:',
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

    # API Settings
    'api_key_set':                 '✅ Set',
    'api_test_success':            'Prisijungimas sėkmingas!',
    'api_test_failed':             'Prisijungimo klaida',
    'balance_equity':              'Kapitalas',
    'balance_available':           'Prieinama',
    'api_missing_notice':          '⚠️ Neturite sukonfigūruotų biržos API raktų. Pridėkite savo API raktą ir slaptažodį nustatymuose (🔑 API ir 🔒 Secret mygtukai), kitaip botas negali prekiauti už jus.',
    'elcaro_ai_info':              '🤖 *AI valdoma prekyba*',

    # Spot Trading
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_balance':                '💰 Spot Balance: {balance}',

    # Strategy trading mode

    # Enliko (Heatmap)

    # Fibonacci (Fibonacci Extension)

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
    'strat_elcaro':                  '🔥 Enliko',
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

    # Break-Even settings UI
    'be_settings_header':            '🔒 *Break-Even nustatymai*',
    'be_settings_desc':              '_Perkelti SL į įėjimo kainą kai pelnas pasiekia aktyvavimo %_',
    'be_enabled_label':              '🔒 Break-Even',
    'be_trigger_label':              '🎯 BE aktyvavimas %',
    'prompt_be_trigger':             'Įveskite Break-Even aktyvavimo % (pvz. 1.0):',
    'prompt_long_be_trigger':        '📈 LONG BE aktyvavimas %\n\nĮveskite pelno % SL perkėlimui į įėjimą:',
    'prompt_short_be_trigger':       '📉 SHORT BE aktyvavimas %\n\nĮveskite pelno % SL perkėlimui į įėjimą:',
    'param_be_trigger':              '🎯 BE aktyvavimas %',
    'be_moved_to_entry':             '🔒 {symbol}: SL perkeltas į break-even @ {entry}',
    'be_status_enabled':             '✅ BE: {trigger}%',
    'be_status_disabled':            '❌ BE: Išjungta',

    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ Dalinis TP',
    'partial_tp_status_enabled':     '✅ Dalinis TP įjungtas',
    'partial_tp_status_disabled':    '❌ Dalinis TP išjungtas',
    'partial_tp_step1_menu':         '✂️ *Dalinis TP - 1 žingsnis*\n\nUždaryti {close}% pozicijos esant +{trigger}% pelnui\n\n_Pasirinkite parametrą:_',
    'partial_tp_step2_menu':         '✂️ *Dalinis TP - 2 žingsnis*\n\nUždaryti {close}% pozicijos esant +{trigger}% pelnui\n\n_Pasirinkite parametrą:_',
    'trigger_pct':                   'Aktyvavimas',
    'close_pct':                     'Uždaryti',
    'prompt_long_ptp_1_trigger':     '📈 LONG 1 žingsnis: Aktyvavimo %\n\nĮveskite pelno % pirmai daliai uždaryti:',
    'prompt_long_ptp_1_close':       '📈 LONG 1 žingsnis: Uždarymo %\n\nĮveskite pozicijos % uždarymui:',
    'prompt_long_ptp_2_trigger':     '📈 LONG 2 žingsnis: Aktyvavimo %\n\nĮveskite pelno % antrai daliai uždaryti:',
    'prompt_long_ptp_2_close':       '📈 LONG 2 žingsnis: Uždarymo %\n\nĮveskite pozicijos % uždarymui:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT 1 žingsnis: Aktyvavimo %\n\nĮveskite pelno % pirmai daliai uždaryti:',
    'prompt_short_ptp_1_close':      '📉 SHORT 1 žingsnis: Uždarymo %\n\nĮveskite pozicijos % uždarymui:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT 2 žingsnis: Aktyvavimo %\n\nĮveskite pelno % antrai daliai uždaryti:',
    'prompt_short_ptp_2_close':      '📉 SHORT 2 žingsnis: Uždarymo %\n\nĮveskite pozicijos % uždarymui:',
    'partial_tp_executed':           '✂️ {symbol}: Uždaryta {close}% esant +{trigger}% pelnui',

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
    'param_leverage': '⚡ Svertas',
    'prompt_leverage': 'Įveskite svertą (1-100):',
    'auto_default': 'Automatinis',

    # Enliko AI
    'elcaro_ai_desc': '_Visi parametrai automatiškai išanalizuojami iš AI signalų:_',

    # Scalper entries

    # Scryptomera feature
    

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
    
    # License status messages - BLACK RHETORIC: Loss Aversion + FOMO
    'no_license': '''🚨 <b>PRIEIGA ATMESTA</b>

Kol dvejojate, <b>847 prekiautojai</b> jau uždirba.

💸 Kiekviena minutė be Enliko = praleistos galimybės
⏰ Rinkos nelaukia. Jūs taip pat neturėtumėte.

👉 /subscribe — <i>Atrakinkite savo nesąžiningą pranašumą DABAR</i>''',
    'no_license_trading': '''🚨 <b>PREKYBA UŽRAKINTA</b>

⚠️ 847 prekiautojai uždirba ŠIUO METU su Enliko.

❌ Rankinė prekyba = emocionės klaidos
✅ Enliko = šaltas AI tikslumas

<i>Nustokite žiūrėti. Pradėkite uždirbti.</i>

👉 /subscribe — <b>Prisijunkite prie 847+ išmaningų prekiautojų</b>''',
    'license_required': '''🔒 <b>PREMIUM FUNKCIJA</b>

Tam reikia {required} prenumeratos — <i>naudoja top 3% prekiautojų</i>.

🎯 Sėkmė palieka pėdsakus. Sekite laimėtojus.

👉 /subscribe — <b>Atnaujinkite dabar</b>''',
    'trial_demo_only': '''⚠️ <b>Demo režimas mokymui, ne uždarbiui.</b>

Tikram pelnui reikia tikros prieigos.

🎁 Paragavote galios. Dabar <b>vald</b>ykite ją.

👉 /subscribe — <b>Atrakinkite realią prekybą</b>''',
    'basic_strategy_limit': '''⚠️ <b>Basic = Basic rezultatai</b>

Apribota: {strategies}

Profesionalai naudoja <b>visas</b> strategijas. Todėl jie profesionalai.

👉 /subscribe — <b>Eikite į Premium. Eikite į Pro.</b>''',
    
    'subscribe_menu_header': '👑 *VIP PRIEIGA prie Elitinių Prekiautojų Klubo*',
    'subscribe_menu_info': 'Pasirinkite planą, kad atrakintumėte prekybos funkcijas:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Bandomoji (Nemokama)',
    'btn_enter_promo': '🎟 Promo kodas',
    'btn_my_subscription': '📋 Mano prenumerata',
    
    'premium_title': '� *PREMIUM — Laimėtojų pasirinkimas*',
    'premium_desc': '''✅ Pilna prieiga prie visų funkcijų
✅ Visos 5 strategijos: OI, RSI+BB, Scryptomera, Scalper, Enliko
✅ Reali + Demo prekyba
✅ Prioritetinė pagalba
✅ Dinaminis SL/TP pagal ATR
✅ Limitų kopetėlės DCA
✅ Visi būsimi atnaujinimai''',
    'premium_1m': '💎 1 mėnuo — {price} ELC',
    'premium_3m': '💎 3 mėnesiai — {price} ELC (-10%)',
    'premium_6m': '💎 6 mėnesiai — {price} ELC (-20%)',
    'premium_12m': '💎 12 mėnesių — {price} ELC (-30%)',
    
    'basic_title': '🥈 *BASIC PLANAS*',
    'basic_desc': '''✅ Pilna prieiga prie demo sąskaitos
✅ Reali sąskaita: OI, RSI+BB, Scryptomera, Scalper
❌ Enliko, Fibonacci, Spot — tik Premium
✅ Standartinė pagalba
✅ Dinaminis SL/TP pagal ATR''',
    'basic_1m': '🥈 1 mėnuo — {price} ELC',
    
    'trial_title': '🎁 *NEMOKAMA BANDOMOJI — Ribota pasiūla!*',
    'trial_desc': '''✅ Pilna prieiga prie demo sąskaitos
✅ Visos 5 strategijos demo
❌ Reali prekyba nepasiekiama
⏰ Trukmė: 7 dienos
🎁 Tik vieną kartą''',
    'trial_activate': '🎁 Aktyvuoti nemokamą bandomąją versiją',
    'trial_already_used': '⚠️ Jau panaudojote nemokamą bandomąją versiją.',
    'trial_activated': '🎉 Bandomoji versija aktyvuota! Turite 7 dienas pilnos demo prieigos.',
    
    'payment_select_method': '💳 *Pasirinkite mokėjimo būdą*',
    'btn_pay_elc': '◈ Enliko Coin (ELC)',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' Mokėjimas per ELC',
    'payment_elc_desc': 'Bus nuskaičiuota {amount} ELC už {plan} ({period}).',
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
  ELC: {total_elc}

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
    'admin_all_payments': '📜 Visi mokėjimai',
    'admin_demo_stats': '🎮 Demo statistika',
    'admin_enter_user_for_report': '👤 Įveskite vartotojo ID detaliai ataskaitai:',
    'admin_generating_report': '📊 Generuojama ataskaita vartotojui {uid}...',
    'admin_global_stats': '📊 Globali statistika',
    'admin_no_payments_found': 'Mokėjimų nerasta.',
    'admin_payments': '💳 Mokėjimai',
    'admin_payments_menu': '💳 *Mokėjimų valdymas*',
    'admin_real_stats': '💰 Real statistika',
    'admin_reports': '📊 Ataskaitos',
    'admin_reports_menu': '''📊 *Ataskaitos ir analitika*

Pasirinkite ataskaitos tipą:''',
    'admin_strategy_breakdown': '🎯 Pagal strategiją',
    'admin_top_traders': '🏆 Top prekiautojai',
    'admin_user_report': '👤 Vartotojo ataskaita',
    'admin_view_report': '📊 Žiūrėti ataskaitą',
    'admin_view_user': '👤 Vartotojo kortelė',
    'btn_check_again': '🔄 Tikrinti vėl',
    'payment_session_expired': '❌ Mokėjimo sesija pasibaigė. Pradėkite iš naujo.',
    'payment_ton_not_configured': '❌ TON mokėjimai nesukonfigūruoti.',
    'payment_verifying': '⏳ Tikrinamas mokėjimas...',
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

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ Nepakankamas ELC balansas.

Jūsų balansas: {balance} ELC
Reikalinga: {required} ELC

Papildykite piniginę, kad tęstumėte.''',
    'wallet_address': '''📍 Adresas: `{address}`''',
    'wallet_balance': '''💰 *Jūsų ELC Piniginė*

◈ Balansas: *{balance} ELC*
📈 Stakinta: *{staked} ELC*
🎁 Laukiantys atlygiai: *{rewards} ELC*

💵 Bendra vertė: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« Atgal''',
    'wallet_btn_deposit': '''📥 Įnėšimas''',
    'wallet_btn_history': '''📋 Istorija''',
    'wallet_btn_stake': '''📈 Stakinti''',
    'wallet_btn_unstake': '''📤 Atšaukti stakinimą''',
    'wallet_btn_withdraw': '''📤 Išėmimas''',
    'wallet_deposit_demo': '''🎁 Gauti 100 ELC (Demo)''',
    'wallet_deposit_desc': '''Siųskite ELC žetonus į savo piniginės adresą:

`{address}`

💡 *Demo režimas:* Spustelėkite žemiau, kad gautumėte nemokamus bandomuosius žetonus.''',
    'wallet_deposit_success': '''✅ Sėkmingai įnėšta {amount} ELC!''',
    'wallet_deposit_title': '''📥 *ELC įnėšimas*''',
    'wallet_history_empty': '''Kol kas nėra operacijų.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *Operacijų istorija*''',
    'wallet_stake_desc': '''Stakinkite savo ELC žetonus ir uždirbkite *12% APY*!

💰 Galima: {available} ELC
📈 Šiuo metu stakinta: {staked} ELC
🎁 Laukiantys atlygiai: {rewards} ELC

Kasdieniai atlygiai • Momentinis išėmimas''',
    'wallet_stake_success': '''✅ Sėkmingai stakinta {amount} ELC!''',
    'wallet_stake_title': '''📈 *ELC Stakinimas*''',
    'wallet_title': '''◈ *ELC Piniginė*''',
    'wallet_unstake_success': '''✅ Išimta {amount} ELC + {rewards} ELC atlygių!''',
    'wallet_withdraw_desc': '''Įveskite paskirties adresą ir sumą:''',
    'wallet_withdraw_failed': '''❌ Išėmimas nepavyko: {error}''',
    'wallet_withdraw_success': '''✅ Išimta {amount} ELC į {address}''',
    'wallet_withdraw_title': '''📤 *ELC Išėmimas*''',

    'spot_freq_hourly': '⏰ Kas valandą',

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
    'error_insufficient_balance': '💰 Nepakanka lėšų sąskaitoje pozicijai atidaryti. Papildykite balansą arba sumažinkite pozicijos dydį.',
    'error_order_too_small': '📉 Užsakymo dydis per mažas (minimumas $5). Padidinkite Entry% arba papildykite balansą.',
    'error_api_key_expired': '🔑 API raktas pasibaigęs arba negaliojantis. Atnaujinkite API raktus nustatymuose.',
    'error_api_key_missing': '🔑 API raktai nesukonfigūruoti. Pridėkite Bybit raktus meniu 🔗 API Keys.',
    'error_rate_limit': '⏳ Per daug užklausų. Palaukite minutę ir bandykite dar kartą.',
    'error_position_not_found': '📊 Pozicija nerasta arba jau uždaryta.',
    'error_leverage_error': '⚙️ Sverto nustatymo klaida. Pabandykite nustatyti svertą rankiniu būdu biržoje.',
    'error_network_error': '🌐 Tinklo problema. Bandykite vėliau.',
    'error_sl_tp_invalid': '⚠️ Nepavyksta nustatyti SL/TP: kaina per arti dabartinės. Bus atnaujinta kitame cikle.',
    'error_equity_zero': '💰 Jūsų sąskaitos balansas lygus nuliui. Papildykite Demo arba Real sąskaitą prekybai.',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 Terminalas',
    'exchange_mode_activated_bybit': '🟠 *Bybit režimas aktyvuotas*',
    'exchange_mode_activated_hl': '🔷 *HyperLiquid režimas aktyvuotas*',
    'error_processing_request': '⚠️ Užklausos apdorojimo klaida',
    'unauthorized_admin': '❌ Neautorizuota. Ši komanda tik administratoriui.',
    'error_loading_dashboard': '❌ Skydelio įkėlimo klaida.',
    'unauthorized': '❌ Neautorizuota.',
    'processing_blockchain': '⏳ Apdorojama blockchain transakcija...',
    'verifying_payment': '⏳ Tikrinamas mokėjimas TON blockchain...',
    'no_wallet_configured': '❌ Piniginė nesukonfigūruota.',
    'use_start_menu': 'Naudokite /start norėdami grįžti į pagrindinį meniu.',

    # 2FA Prisijungimo patvirtinimas
    'login_approved': '✅ Prisijungimas patvirtintas!\n\nDabar galite tęsti naršyklėje.',
    'login_denied': '❌ Prisijungimas atmestas.\n\nJei tai nebuvote jūs, patikrinkite saugumo nustatymus.',
    'login_expired': '⏰ Patvirtinimo laikas baigėsi. Bandykite dar kartą.',
    'login_error': '⚠️ Apdorojimo klaida. Bandykite vėliau.',

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
    'button_hyperliquid': '🔷 HyperLiquid',
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
}
