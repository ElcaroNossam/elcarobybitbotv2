# -*- coding: utf-8 -*-
"""
Enliko Trading Tools — Czech Translations (Čeština)
Version: 4.0.0 | Updated: 28 January 2026
LEGAL: Educational platform, not financial advice.
"""

TEXTS = {
    # Common UI
    'loader': '⏳ Načítání...',
    # =====================================================
    # LEGAL DISCLAIMERS (Právní prohlášení)
    # =====================================================
    
    'disclaimer_trading': (
        '⚠️ *DŮLEŽITÉ PROHLÁŠENÍ*\n\n'
        'Tato platforma poskytuje vzdělávací nástroje pro seznámení s trhy kryptoměn.\n'
        'NENÍ to:\n'
        '• Finanční poradenství\n'
        '• Investiční doporučení\n'
        '• Systém zaručeného zisku\n\n'
        'Obchodování s kryptoměnami zahrnuje značné riziko ztráty. '
        'Můžete ztratit část nebo celou investici. '
        'Obchodujte pouze s prostředky, které si můžete dovolit ztratit.\n\n'
        'Minulé výsledky nezaručují budoucí výnosy.'
    ),
    
    'disclaimer_short': '⚠️ _Pouze vzdělávací nástroje. Není to finanční poradenství. Obchodování zahrnuje riziko._',
    
    'disclaimer_execution': (
        '⚠️ Pokračováním potvrzujete, že:\n'
        '• Nesete odpovědnost za všechna obchodní rozhodnutí\n'
        '• Toto je vzdělávací nástroj, nikoliv finanční poradenství\n'
        '• Chápete rizika obchodování s kryptoměnami\n'
        '• Minulé výsledky nezaručují budoucí výnosy'
    ),
    
    # Welcome - Updated with legal positioning
    'welcome': (
        '📊 *Vítejte v Enliko Trading Tools*\n\n'
        '🎯 Vzdělávací platforma:\n'
        '• Sledování a analýza portfolia\n'
        '• Backtesting strategií\n'
        '• Vizualizace tržních dat\n'
        '• Nástroje řízení rizik\n\n'
        '⚠️ _Pouze pro vzdělávací účely. Není to finanční poradenství._\n'
        '_Obchodování zahrnuje značné riziko ztráty._'
    ),
    
    'welcome_back': (
        '📊 *Enliko Trading Tools*\n\n'
        '⚠️ _Vzdělávací platforma. Není to finanční poradenství._'
    ),
    
    # Legacy keys
    
    # ═══════════════════════════════════════════════════════════════════
    # MODERN MENU BUTTONS - Stylish & Persuasive
    # ═══════════════════════════════════════════════════════════════════
    'button_orders':               '📊 Příkazy',
    'button_positions':            '🎯 Pozice',

    'button_balance': '💎 Portfolio',
    'button_market': '📈 Trh',
    'button_strategies': '🤖 AI Boti',
    'button_subscribe': '🤝 PODPOŘIT',
    'button_terminal': '💻 Terminál',
    'button_terminal': '💻 Terminál',
    'button_history':              '📜 Historie',
    'button_api_keys':             '🔑 API Klíče',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_settings':             '⚙️ Konfigurace',

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
    'positions_header':            '📊 Tvé otevřené pozice:',

    # Position management (inline)
    'btn_close_position':          'Zavřít pozici',
    'btn_cancel':                  '❌ Zrušit',
    'btn_back':                    '🔙 Zpět',
    'position_already_closed':     'Pozice již uzavřena',
    'position_closed_success':     'Pozice uzavřena',
    'position_close_error':        'Chyba při zavírání pozice',

    # % per trade

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Pouze limitní příkazy: {state}',
    'feature_limit_only':          'Pouze Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Indikátory Enliko*',
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

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko Limit vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Enliko Limit chyba: {msg}',
    'elcaro_market_entry':         '🔥 *Enliko Market vstup*\n• {symbol} {side}\n• Cena: {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• Množství: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Enliko Market chyba: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

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
    'select_language':             '🌍 Vyberte jazyk:',
    'language_set':                '✅ Jazyk nastaven:',
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
    'api_key_set':                 '✅ Set',
    'api_test_success':            'Připojení úspěšné!',
    'api_test_failed':             'Chyba připojení',
    'balance_equity':              'Kapitál',
    'balance_available':           'Dostupné',
    'api_missing_notice':          '⚠️ Nemáte nakonfigurováné API klíče burzy. Přidejte prosím svůj API klíč a tajný klíč v nastavení (tlačítka 🔑 API a 🔒 Secret), jinak bot nemůže za vás obchodovat.',
    'elcaro_ai_info':              '🤖 *Obchodování poháněné AI*',

    # Spot Trading
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_balance':                '💰 Spot Balance: {balance}',

    # Strategy trading mode

    # Enliko (Heatmap)

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
    'strat_elcaro':                  '🔥 Enliko',
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

    # Break-Even settings UI
    'be_settings_header':            '🔒 *Nastavení Break-Even*',
    'be_settings_desc':              '_Přesunout SL na vstupní cenu když zisk dosáhne % aktivace_',
    'be_enabled_label':              '🔒 Break-Even',
    'be_trigger_label':              '🎯 Aktivace BE %',
    'prompt_be_trigger':             'Zadejte % aktivace Break-Even (např. 1.0):',
    'prompt_long_be_trigger':        '📈 LONG Aktivace BE %\n\nZadejte % zisku pro přesun SL na vstup:',
    'prompt_short_be_trigger':       '📉 SHORT Aktivace BE %\n\nZadejte % zisku pro přesun SL na vstup:',
    'param_be_trigger':              '🎯 Aktivace BE %',
    'be_moved_to_entry':             '🔒 {symbol}: SL přesunut na break-even @ {entry}',
    'be_status_enabled':             '✅ BE: {trigger}%',
    'be_status_disabled':            '❌ BE: Vypnuto',

    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ Částečný TP',
    'partial_tp_status_enabled':     '✅ Částečný TP zapnut',
    'partial_tp_status_disabled':    '❌ Částečný TP vypnut',
    'partial_tp_step1_menu':         '✂️ *Částečný TP - Krok 1*\n\nZavřít {close}% pozice při +{trigger}% zisku\n\n_Vyberte parametr:_',
    'partial_tp_step2_menu':         '✂️ *Částečný TP - Krok 2*\n\nZavřít {close}% pozice při +{trigger}% zisku\n\n_Vyberte parametr:_',
    'trigger_pct':                   'Aktivace',
    'close_pct':                     'Zavřít',
    'prompt_long_ptp_1_trigger':     '📈 LONG Krok 1: % Aktivace\n\nZadejte % zisku pro zavření první části:',
    'prompt_long_ptp_1_close':       '📈 LONG Krok 1: % Zavření\n\nZadejte % pozice k zavření:',
    'prompt_long_ptp_2_trigger':     '📈 LONG Krok 2: % Aktivace\n\nZadejte % zisku pro zavření druhé části:',
    'prompt_long_ptp_2_close':       '📈 LONG Krok 2: % Zavření\n\nZadejte % pozice k zavření:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT Krok 1: % Aktivace\n\nZadejte % zisku pro zavření první části:',
    'prompt_short_ptp_1_close':      '📉 SHORT Krok 1: % Zavření\n\nZadejte % pozice k zavření:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT Krok 2: % Aktivace\n\nZadejte % zisku pro zavření druhé části:',
    'prompt_short_ptp_2_close':      '📉 SHORT Krok 2: % Zavření\n\nZadejte % pozice k zavření:',
    'partial_tp_executed':           '✂️ {symbol}: Zavřeno {close}% při +{trigger}% zisku',

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
    'param_leverage': '⚡ Páka',
    'prompt_leverage': 'Zadejte páku (1-100):',
    'auto_default': 'Auto',

    # Enliko AI
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
    
    'no_license': '🤝 *Community Membership*\n\nSupport our open-source project to access\nadditional community resources.\n\n👉 /subscribe — Support the project',
    'no_license_trading': '🤝 *Community Resource*\n\nThis resource is available to community supporters.\n\n👉 /subscribe — Support the project',
    'license_required': '🔒 *Supporter Resource*\n\nThis resource requires {required} membership.\n\n👉 /subscribe — Support the project',
    'trial_demo_only': '⚠️ *Explorer Access*\n\nExplorer access is limited to demo environment.\n\n👉 /subscribe — Become a supporter',
    'basic_strategy_limit': '⚠️ *Community Tier*\n\nAvailable templates: {strategies}\n\n👉 /subscribe — Upgrade your support',
    'subscribe_menu_header': '🤝 *Support Enliko*\n\nYour voluntary contribution helps maintain\nfree open-source community tools.\n\nChoose your support level:',
    'subscribe_menu_info': '_Select your support level:_',
    'btn_premium': '💎 Pro',
    'btn_basic': '💚 Podporovatel',
    'btn_trial': '🆓 Průzkumník (Zdarma)',
    'btn_enter_promo': '🎟 Kód pozvánky',
    'btn_my_subscription': '📋 Mé členství',
    'premium_title': '💎 *Pro Plan*',
    'premium_desc': '*Full access to all tools:*\n\n✅ All trading strategies\n✅ Demo & live environments\n✅ Priority support\n✅ ATR risk management\n✅ DCA configuration\n✅ All platform updates\n\n⚠️ _Trading involves risk. Not financial advice._',
    'premium_1m': '💎 1 Month — {price} ELC',
    'premium_3m': '💎 3 Months — {price} ELC',
    'premium_6m': '💎 6 Months — {price} ELC',
    'premium_12m': '💎 12 Months — {price} ELC',
    'basic_title': '💚 *Supporter Membership*',
    'basic_desc': '*Thank you for your support!*\n\n✅ Demo + live environments\n✅ Templates: OI, RSI+BB\n✅ Bybit integration\n✅ ATR risk management tools\n\n⚠️ _Educational tools only. Not financial advice._',
    'basic_1m': '💚 1 Month — {price} ELC',
    'trial_title': '🆓 *Explorer Access — 14 Days*',
    'trial_desc': '*Explore our community tools:*\n\n✅ Full demo environment\n✅ All analysis templates\n✅ 14 days access\n✅ No contribution required\n\n⚠️ _Educational tools only. Not financial advice._',
    'trial_activate': '🆓 Start Exploring',
    'trial_already_used': '⚠️ Explorer access already used. Consider supporting the project.',
    'trial_activated': '🎉 *Explorer Access Activated!*\n\n⏰ 14 days of full demo access.\n\n⚠️ _Educational tools only. Not financial advice._',
    'payment_select_method': '🤝 *How would you like to contribute?*',
    'btn_pay_elc': '◈ ELC',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' Platba přes ELC',
    'payment_elc_desc': 'Bude vám účtováno {amount} ELC za {plan} ({period}).',
    'payment_ton_title': '💎 Platba přes TON',
    'payment_ton_desc': '''Pošlete přesně *{amount} TON* na:

`{wallet}`

Po platbě klikněte na tlačítko níže pro ověření.''',
    'btn_verify_ton': '✅ Zaplatil jsem — Ověřit',
    'payment_processing': '⏳ ...',
    'payment_success': '🎉 Thank you for your support!\n\n{plan} access activated until {expires}.',
    'payment_failed': '❌ Contribution failed: {error}',
    'my_subscription_header': '📋 *My Membership*',
    'my_subscription_active': '''📋 *Aktuální plán:* {plan}
⏰ *Vyprší:* {expires}
📅 *Zbývající dny:* {days}''',
    'my_subscription_none': '❌ No active membership.\n\nUse /subscribe to support the project.',
    'my_subscription_history': '📜 *Historie plateb:*',
    'subscription_expiring_soon': '⚠️ Vaše předplatné {plan} vyprší za {days} dní!\n\nObnovte nyní: /subscribe',
    
    'promo_enter': '🎟 Enter your invite code:',
    'promo_success': '🎉 Invite code applied!\n\n{plan} access for {days} days.',
    'promo_invalid': '❌ Invalid invite code.',
    'promo_expired': '❌ This invite code has expired.',
    'promo_used': '❌ This invite code has already been used.',
    'promo_already_used': '❌ You have already used this invite code.',
    'admin_license_menu': '🤝 *Membership Management*',
    'admin_btn_grant_license': '🎁 Grant Access',
    'admin_btn_view_licenses': '📋 View Members',
    'admin_btn_create_promo': '🎟 Create Invite',
    'admin_btn_view_promos': '📋 View Invites',
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
  ELC: {total_elc}

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
    'btn_check_again': '🔄 Check',
    'payment_session_expired': '❌ Platnost platby vypršela. Začněte prosím znovu.',
    'payment_ton_not_configured': '❌ Platby TON nejsou konfigurovány.',
    'payment_verifying': '⏳ Ověřování platby...',
    'stats_fibonacci': '📐 Fibonacci',

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

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ Nedostatečný zůstatek ELC.

Váš zůstatek: {balance} ELC
Požadováno: {required} ELC

Dobijte peněženku pro pokračování.''',
    'wallet_address': '''📍 Adresa: `{address}`''',
    'wallet_balance': '''💰 *Vaše ELC Peněženka*

◈ Zůstatek: *{balance} ELC*
📈 Stakované: *{staked} ELC*
🎁 Čekající odměny: *{rewards} ELC*

💵 Celková hodnota: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« Zpět''',
    'wallet_btn_deposit': '''📥 Vložit''',
    'wallet_btn_history': '''📋 Historie''',
    'wallet_btn_stake': '''📈 Staking''',
    'wallet_btn_unstake': '''📤 Unstake''',
    'wallet_btn_withdraw': '''📤 Vybrat''',
    'wallet_deposit_demo': '''🎁 Získat 100 ELC (Demo)''',
    'wallet_deposit_desc': '''Pošlete ELC tokeny na adresu vaší peněženky:

`{address}`

💡 *Demo režim:* Klikněte níže pro získání bezplatných testovacích tokenů.''',
    'wallet_deposit_success': '''✅ Vloženo {amount} ELC úspěšně!''',
    'wallet_deposit_title': '''📥 *Vklad ELC*''',
    'wallet_history_empty': '''Žádné transakce.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *Historie transakcí*''',
    'wallet_stake_desc': '''Stakujte své ELC tokeny a vydělávejte *12% APY*!

💰 Dostupné: {available} ELC
📈 Aktuálně stakované: {staked} ELC
🎁 Čekající odměny: {rewards} ELC

Denní odměny • Okamžitý výběr''',
    'wallet_stake_success': '''✅ {amount} ELC úspěšně stakované!''',
    'wallet_stake_title': '''📈 *Staking ELC*''',
    'wallet_title': '''◈ *ELC Peněženka*''',
    'wallet_unstake_success': '''✅ Vybráno {amount} ELC + {rewards} ELC odměn!''',
    'wallet_withdraw_desc': '''Zadejte cílovou adresu a částku:''',
    'wallet_withdraw_failed': '''❌ Výběr se nezdařil: {error}''',
    'wallet_withdraw_success': '''✅ Vybráno {amount} ELC na {address}''',
    'wallet_withdraw_title': '''📤 *Výběr ELC*''',

    'spot_freq_hourly': '⏰ Každou hodinu',

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
    'error_insufficient_balance': '💰 Nedostatečné prostředky na účtu pro otevření pozice. Dobijte zůstatek nebo zmenšete velikost pozice.',
    'error_order_too_small': '📉 Velikost objednávky příliš malá (minimum $5). Zvyšte Entry% nebo dobijte zůstatek.',
    'error_api_key_expired': '🔑 API klíč vypršel nebo je neplatný. Aktualizujte API klíče v nastavení.',
    'error_api_key_missing': '🔑 API klíče nejsou nakonfigurovány. Přidejte klíče Bybit v menu 🔗 API Keys.',
    'error_rate_limit': '⏳ Příliš mnoho požadavků. Počkejte minutu a zkuste znovu.',
    'error_position_not_found': '📊 Pozice nenalezena nebo již uzavřena.',
    'error_leverage_error': '⚙️ Chyba nastavení páky. Zkuste nastavit páku ručně na burze.',
    'error_network_error': '🌐 Problém se sítí. Zkuste to později.',
    'error_sl_tp_invalid': '⚠️ Nelze nastavit SL/TP: cena příliš blízko aktuální. Bude aktualizováno v dalším cyklu.',
    'error_equity_zero': '💰 Zůstatek vašeho účtu je nulový. Dobijte Demo nebo Real účet pro obchodování.',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 Terminál',
    'exchange_mode_activated_bybit': '🟠 *Režim Bybit aktivován*',
    'exchange_mode_activated_hl': '🔷 *Režim HyperLiquid aktivován*',
    'error_processing_request': '⚠️ Chyba zpracování požadavku',
    'unauthorized_admin': '❌ Neautorizováno. Tento příkaz je pouze pro administrátora.',
    'error_loading_dashboard': '❌ Chyba načítání panelu.',
    'unauthorized': '❌ Neautorizováno.',
    'processing_blockchain': '⏳ Zpracování blockchain transakce...',
    'verifying_payment': '⏳ Ověřování platby na blockchainu TON...',
    'no_wallet_configured': '❌ Peněženka není nakonfigurována.',
    'use_start_menu': 'Použijte /start pro návrat do hlavního menu.',

    # 2FA Potvrzení přihlášení
    'login_approved': '✅ Přihlášení schváleno!\n\nNyní můžete pokračovat v prohlížeči.',
    'login_denied': '❌ Přihlášení zamítnuto.\n\nPokud to nebyli vy, zkontrolujte nastavení zabezpečení.',
    'login_expired': '⏰ Potvrzení vypršelo. Zkuste to znovu.',
    'login_error': '⚠️ Chyba zpracování. Zkuste to později.',

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
    "basic_bybit_only": "⚠️ *Basic Plan Limitation*\n\nBasic plan supports Bybit only.\nHyperLiquid is available on Pro plan.\n\n👉 /subscribe — Upgrade to Pro",
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
    'button_spot': '💹 Spot',
    'payment_ton_desc': 'TON payments are currently unavailable.',
    'position_closed_error': '⚠️ {symbol} closed but log failed: {error}',
    'spot_btn_buy': '💰 Buy Now',
    'spot_btn_holdings': '💎 Holdings',
    'spot_btn_rebalance': '⚖️ Rebalance',
    'spot_btn_sell': '💸 Sell Menu',
    'spot_btn_settings': '⚙️ Settings',
    'wallet_deposit_desc': 'Send ELC tokens to:\n\n`{address}`',
    'wallet_history_item': '{type_emoji} {type}: {amount:+.2f} ELC\n   {date}',


    # Daily Digest
    'digest_title': '📊 Denní zpráva',
    'digest_detailed_title': '📋 Podrobná zpráva',
    'digest_date_format': '%d. %B %Y',
    'digest_filter_all': '🌍 Všechny burzy',
    'digest_no_trades': '📭 Žádné obchody pro tento filtr',
    'digest_no_trades_hint': 'Zkuste jinou kombinaci filtrů.',
    'digest_total_pnl': 'Celkový PnL',
    'digest_statistics': 'Statistiky',
    'digest_trades': 'Obchody',
    'digest_wins_losses': 'Výhry/Prohry',
    'digest_win_rate': 'Úspěšnost',
    'digest_avg_pnl': 'Průměrný PnL',
    'digest_best_trade': 'Nejlepší obchod',
    'digest_worst_trade': 'Nejhorší obchod',
    'digest_keep_improving': 'Pokračuj v zlepšování! 💪',
    'digest_vibe_amazing': 'Úžasný den!',
    'digest_vibe_nice': 'Dobrá práce!',
    'digest_vibe_breakeven': 'Den na nule',
    'digest_vibe_small_loss': 'Malá ztráta',
    'digest_vibe_tough': 'Těžký den',
    'digest_btn_all': 'Vše',
    'digest_btn_bybit': '🟠 Bybit',
    'digest_btn_hl': '🔷 HL',
    'digest_btn_demo': '🧪 Demo',
    'digest_btn_real': '💼 Real',
    'digest_btn_testnet': '🧪 Testnet',
    'digest_btn_mainnet': '🌐 Mainnet',
    'digest_btn_detailed': '📋 Podrobnosti',
    'digest_btn_close': '❌ Zavřít',
    'digest_btn_back': '◀️ Zpět',
    'digest_by_exchange': 'Podle burzy',
    'digest_by_strategy': 'Podle strategie',
    'digest_top_symbols': 'Top Symboly',
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
