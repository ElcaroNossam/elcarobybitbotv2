# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu - BLACK RHETORIC: FOMO + Authority + Exclusivity
    'welcome':                     '''🔥 <b>Bienvenue, Trader Alpha !</b>

Pendant que vous lisez ceci — <b>847 traders</b> profitent déjà avec ElCaro.

⚡ <b>&lt; 100ms</b> vitesse d'exécution
🛡️ <b>664 tests de sécurité</b> réussis
💎 <b>24/7</b> trading propulsé par IA

<i>Vos concurrents ne dorment pas. ElCaro non plus.</i>

Choisissez votre voie vers la liberté financière :''',
    'no_strategies':               '❌ Aucune — <i>Vous perdez de l\'argent chaque seconde sans stratégies actives</i>',
    'guide_caption':               '📚 <b>SECRETS des Traders d\'ÉLITE</b>\n\n⚠️ Cette information a donné à nos meilleurs traders un <b>avantage déloyal</b>.\n\n<i>Temps de lecture : 3 min. Profit potentiel : illimité.</i>',
    'privacy_caption':             '📜 <b>Votre Sécurité = Notre Obsession</b>\n\n🔐 Cryptage bancaire\n✅ Aucun partage de données. Jamais.\n\n<i>Vous êtes entre de bonnes mains.</i>',
    'button_api':                  '� Connecter API',
    'button_secret':               '🔑 Clé Secrète',
    'button_api_settings':         '⚙️ Config API',
    'button_subscribe':            '👑 PREMIUM',
    'button_licenses':             '🎫 Licences',
    'button_admin':                '🛡️ Admin',
    'button_balance':              '💎 Portfolio',
    'button_orders':               '📊 Ordres',
    'button_positions':            '🎯 Positions',
    'button_history':              '📜 Historique',
    'button_strategies':           '🤖 Bots IA',
    'button_api_keys':             '🔑 Clés API',
    'button_bybit':                '🟠 Bybit',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_switch_bybit':         '🔄 Bybit',
    'button_switch_hl':            '🔄 HyperLiquid',
    'button_percent':              '🎚 % par trade',
    'button_coins':                '💠 Groupe de coins',
    'button_market':               '📈 Marché',
    'button_manual_order':         '🎯 Sniper',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ Annuler l’ordre',
    'button_limit_only':           '🎯 Limit uniquement',
    'button_toggle_oi':            '� OI Tracker',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_scalper':              '⚡ Scalper',
    'button_elcaro':               '🔥 Elcaro',
    'button_fibonacci':            '📐 Fibonacci',
    'button_settings':             '⚙️ Config',
    'button_indicators':           '💡 Indicateurs',
    'button_support':              '🆘 Support',
    'toggle_oi_status':            '🔀 {feature} : {status}',
    'toggle_rsi_bb_status':        '📊 {feature} : {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera : {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 Le mode TP/SL est maintenant : *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Pourcentage fixe',

    # Limits
    'limit_positions_exceeded':    '🚫 Limite de positions ouvertes dépassée ({max})',
    'limit_limit_orders_exceeded': '🚫 Limite d’ordres Limit dépassée ({max})',

    # Languages
    'select_language':             'Choisis la langue :',
    'language_set':                'Langue définie sur :',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'Choisis le type d’ordre :',
    'limit_order_format': (
        "Saisis les paramètres d’un ordre Limit :\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "où SIDE = LONG ou SHORT\n"
        "Exemple : `BTCUSDT LONG 20000 0.1`\n\n"
        "Pour annuler, envoie ❌ Annuler l’ordre"
    ),
    'market_order_format': (
        "Saisis les paramètres d’un ordre Market :\n"
        "`SYMBOL SIDE QTY`\n"
        "où SIDE = LONG ou SHORT\n"
        "Exemple : `BTCUSDT SHORT 0.1`\n\n"
        "Pour annuler, envoie ❌ Annuler l’ordre"
    ),
    'order_success':               '✅ Ordre créé avec succès !',
    'order_create_error':          '❌ Échec de création de l’ordre : {msg}',
    'order_fail_leverage':         (
        "❌ Ordre non créé : l’effet de levier sur ton compte Bybit est trop élevé pour cette taille.\n"
        "Réduis l’effet de levier dans les réglages Bybit."
    ),
    'order_parse_error':           '❌ Échec d’analyse : {error}',
    'price_error_min':             '❌ Erreur de prix : doit être ≥{min}',
    'price_error_step':            '❌ Erreur de prix : doit être un multiple de {step}',
    'qty_error_min':               '❌ Erreur de quantité : doit être ≥{min}',
    'qty_error_step':              '❌ Erreur de quantité : doit être un multiple de {step}',

    # Loading…
    'loader':                      '⏳ Récupération des données…',

    # Market command
    'market_status_heading':       '*État du marché :*',
    'market_dominance_header':    'Top Coins par Dominance',
    'market_total_header':        'Capitalisation Totale',
    'market_indices_header':      'Indices du Marché',
    'usdt_dominance':              'Dominance USDT',
    'btc_dominance':               'Dominance BTC',
    'dominance_rising':            '↑ en hausse',
    'dominance_falling':           '↓ en baisse',
    'dominance_stable':            '↔️ stable',
    'dominance_unknown':           '❔ pas de données',
    'btc_price':                   'Prix BTC',
    'last_24h':                    'sur 24 h',
    'alt_signal_label':            'Signal altcoin',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Dernières actus (CoinDesk) :*',

    # Execution price error
    'exec_price_not_found':        'Impossible de trouver le prix d’exécution pour la clôture',

    # /account
    'account_balance':             '💰 Solde : `{balance:.2f}`',
    'account_realized_header':     '📈 *PnL réalisé :*',
    'account_realized_day':        '  • Aujourd’hui : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 jours    : `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *PnL non réalisé :*',
    'account_unreal_total':        '  • Total : `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % de IM : `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Tes réglages :*',
    'config_percent':              '• 🎚 % par trade      : `{percent}%`',
    'config_coins':                '• 💠 Coins           : `{coins}`',
    'config_limit_only':           '• 🎯 Ordres Limit    : {state}',
    'config_atr_mode':             '• 🏧 SL suiveur ATR  : {atr}',
    'config_trade_oi':             '• 📊 Trader OI       : {oi}',
    'config_trade_rsi_bb':         '• 📈 Trader RSI+BB   : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%             : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%             : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 Aucun ordre ouvert',
    'open_orders_header':          '*📒 Ordres ouverts :*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Côté : `{side}`\n"
        "   • Qté  : `{qty}`\n"
        "   • Prix : `{price}`\n"
        "   • ID   : `{id}`"
    ),
    'open_orders_error':           '❌ Erreur lors de la récupération : {error}',

    # Manual coin selection
    'enter_coins':                 "Entre des symboles séparés par des virgules, ex. :\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Coins sélectionnés : {coins}',

    # Positions
    'no_positions':                '🚫 Aucune position ouverte',
    'positions_header':            '📊 Tes positions ouvertes :',
    'position_item':               (
        "— Position #{idx} : {symbol} | {side} (x{leverage})\n"
        "  • Taille          : {size}\n"
        "  • Prix d’entrée   : {avg:.8f}\n"
        "  • Prix mark       : {mark:.8f}\n"
        "  • Liquidation     : {liq}\n"
        "  • Marge initiale  : {im:.2f}\n"
        "  • Marge d’entretien: {mm:.2f}\n"
        "  • Solde position  : {pm:.2f}\n"
        "  • Take Profit     : {tp}\n"
        "  • Stop Loss       : {sl}\n"
        "  • PnL non réalisé : {pnl:+.2f} ({pct:+.2f}%)"
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
    'positions_overall':           'PnL non réalisé total : {pnl:+.2f} ({pct:+.2f}%)',

    # Position management (inline)
    'open_positions_header':       '📊 *Positions ouvertes*',
    'positions_count':             'positions',
    'positions_count_total':       'Total des positions',
    'total_unrealized_pnl':        'PnL non réalisé total',
    'total_pnl':                   'P/L total',
    'btn_close_short':             'Fermer',
    'btn_close_all':               'Fermer toutes les positions',
    'btn_close_position':          'Fermer la position',
    'btn_confirm_close':           'Confirmer la fermeture',
    'btn_confirm_close_all':       'Oui, tout fermer',
    'btn_cancel':                  '❌ Annuler',
    'btn_back':                    '🔙 Retour',
    'confirm_close_position':      'Fermer la position',
    'confirm_close_all':           'Fermer TOUTES les positions',
    'position_not_found':          'Position introuvable ou déjà fermée',
    'position_already_closed':     'Position déjà fermée',
    'position_closed_success':     'Position fermée',
    'position_close_error':        'Erreur lors de la fermeture',
    'positions_closed':            'Positions fermées',
    'errors':                      'Erreurs',

    # % per trade
    'set_percent_prompt':          'Entre le pourcentage du solde par trade (ex. 2.5) :',
    'percent_set_success':         '✅ % par trade défini : {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Ordres Limit uniquement : {state}',
    'feature_limit_only':          'Limit uniquement',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Indicateurs Elcaro*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. Tendance adaptative',
    'indicator_4':                 '4. Régression dynamique',

    # Support
    'support_prompt':              '✉️ Besoin d’aide ? Clique ci-dessous :',
    'support_button':              'Contacter le support',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 Aucune position ouverte',
    'update_tpsl_prompt':          'Entre SYMBOL TP SL, ex. :\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Format invalide. Utilise : SYMBOL TP SL\nEx. : BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Entre ta clé Bybit API :',
    'api_saved':                   '✅ Clé API enregistrée',
    'enter_secret':                'Entre ton secret Bybit API :',
    'secret_saved':                '✅ Secret API enregistré',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ Saisis une valeur de TP%',
    'tp_set_success':              '✅ TP% défini : {pct}%',
    'enter_sl':                    '❌ Saisis une valeur de SL%',
    'sl_set_success':              '✅ SL% défini : {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit : nécessite 4 args (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market : nécessite 3 args (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE doit être LONG ou SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ Clé/secret API non définis',
    'bybit_invalid_response':      '❌ Réponse Bybit invalide',
    'bybit_error':                 '❌ Erreur Bybit {path} : {data}',

    # Auto notifications - BLACK RHETORIC: Excitement
    'new_position': (
        '🚀 <b>NOUVELLE POSITION OUVERTE!</b>\n\n'
        '💎 {symbol} @ {entry:.6f}\n'
        '📊 Taille: {size}\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>L\'IA ElCaro travaille pour vous 24/7</i>'
    ),
    'sl_auto_set':                 '🛑 SL défini automatiquement : {price:.6f}',
    'auto_close_position':         '⏱ Position {symbol} (TF={tf}) ouverte > {tf} et perdante, clôturée auto.',
    'position_closed': (
        '🎯 <b>POSITION CLÔTURÉE!</b>\n\n'
        '📊 {symbol} via *{reason}*\n'
        '🤖 Stratégie: `{strategy}`\n'
        '📈 Entrée: `{entry:.8f}`\n'
        '📉 Sortie: `{exit:.8f}`\n'
        '💰 PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>Votre argent travaille pendant que vous dormez.</i>'
    ),

    # Entries & errors - format unifié avec infos complètes
    'oi_limit_entry':              '📉 *OI Entrée Limit*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit erreur: {msg}',
    'oi_market_entry':             '📉 *OI Entrée Market*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI Market erreur: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Entrée Limit*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Entrée Market*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB Market erreur: {msg}',

    'oi_analysis':                 '📊 *Analyse OI {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Entrée Limit*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit erreur: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Entrée Market*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market erreur: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>Solde insuffisant!</b>\n\n💰 Le solde de votre compte {account_type} est insuffisant pour ouvrir cette position.\n\n<b>Solutions:</b>\n• Recharger votre solde\n• Réduire la taille de position (% par trade)\n• Réduire l\'effet de levier\n• Fermer certaines positions ouvertes',
    'insufficient_balance_error_extended': '❌ <b>Solde insuffisant!</b>\n\n📊 Stratégie: <b>{strategy}</b>\n🪙 Symbole: <b>{symbol}</b> {side}\n\n💰 Le solde de votre compte {account_type} est insuffisant.\n\n<b>Solutions:</b>\n• Recharger votre solde\n• Réduire la taille de position (% par trade)\n• Réduire l\'effet de levier\n• Fermer certaines positions ouvertes',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>Effet de levier trop élevé!</b>\n\n⚙️ Votre effet de levier dépasse le maximum autorisé pour ce symbole.\n\n<b>Maximum autorisé:</b> {max_leverage}x\n\n<b>Solution:</b> Allez dans les paramètres de stratégie et réduisez l\'effet de levier.',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>Limite de position dépassée!</b>\n\n📊 Stratégie: <b>{strategy}</b>\n🪙 Symbole: <b>{symbol}</b>\n\n⚠️ Votre position dépasserait la limite maximale.\n\n<b>Solutions:</b>\n• Réduire l\'effet de levier\n• Réduire la taille de position\n• Fermer des positions',

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Entrée Limit*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit erreur: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Entrée Market*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market erreur: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *Elcaro Entrée Limit*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Elcaro Limit erreur: {msg}',
    'elcaro_market_entry':         '🔥 *Elcaro Entrée Market*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Elcaro Market erreur: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci Entrée Limit*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci Limit erreur: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci Entrée Market*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci Market erreur: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 Panneau admin :',
    'admin_pause':                 '⏸️ Trading & notifications en pause pour tous.',
    'admin_resume':                '▶️ Trading & notifications repris pour tous.',
    'admin_closed':                '✅ Fermetures totales : {count} {type}.',
    'admin_canceled_limits':       '✅ {count} ordres Limit annulés.',

    # Coin groups
    'select_coin_group':           'Choisis le groupe de coins :',
    'group_all':                   'ALL',
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ Groupe défini : {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *Analyse RSI+BB*\n'
        '• Prix : `{price:.6f}`\n'
        '• RSI  : `{rsi:.1f}` ({zone})\n'
        '• BB haut : `{bb_hi:.4f}`\n'
        '• BB bas  : `{bb_lo:.4f}`\n\n'
        '*Entrée MARKET {side} via RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'Survendu (<30)',
    'rsi_zone_overbought':         'Suracheté (>70)',
    'rsi_zone_neutral':            'Neutre (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ TP/SL invalide pour LONG.\n'
        'Prix actuel : {current:.2f}\n'
        'Attendu : SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ TP/SL invalide pour SHORT.\n'
        'Prix actuel : {current:.2f}\n'
        'Attendu : TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 Aucune position ouverte sur {symbol}',
    'tpsl_set_success':            '✅ TP={tp:.2f} et SL={sl:.2f} définis pour {symbol}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Langue',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Mode stop : *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ Ordre Limit {symbol} exécuté @ {price}',
    'limit_order_cancelled':       '⚠️ Ordre Limit {symbol} (ID : {order_id}) annulé.',
    'fixed_sl_tp':                 '✅ {symbol} : SL à {sl}, TP à {tp}',
    'tp_part':                     ', TP fixé à {tp_price}',
    'sl_tp_set':                   '✅ {symbol} : SL à {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol} : SL à {sl_price}',
    'sl_tp_initialized':           '✅ {symbol} : SL/TP initialisés à {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol} : SL déplacé au break-even à {entry}',
    'sl_tp_updated':               '✏️ {symbol} : SL/TP mis à jour à {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Position {symbol} clôturée mais enregistrement échoué : {error}\n'
        'Contacte le support.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Pourcentage fixe',

    # System notices
    'db_quarantine_notice':        '⚠️ Logs temporairement en pause. Mode silencieux pendant 1 h.',

    # Fallback
    'fallback':                    '❓ Utilise les boutons du menu.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 Vous êtes bloqué.',
    'invite_only': '🔒 Accès sur invitation uniquement. Veuillez attendre la validation de l’admin.',
    'need_terms': '⚠️ Veuillez d’abord accepter les conditions : /terms',
    'please_confirm': 'Veuillez confirmer :',
    'terms_ok': '✅ Merci ! Conditions acceptées.',
    'terms_declined': '❌ Conditions refusées. Accès fermé. Vous pouvez revenir avec /terms.',
    'usage_approve': 'Usage : /approve <user_id>',
    'usage_ban': 'Usage : /ban <user_id>',
    'not_allowed': 'Non autorisé',
    'bad_payload': 'Données invalides',
    'unknown_action': 'Action inconnue',

    'title': 'Nouvel utilisateur',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID : <code>{uid}</code>\n'
        '• Nom : {name}\n'
        '• Pseudo : {uname}\n'
        '• Langue : {lang}\n'
        '• Autorisé : {allowed}  Ban : {banned}\n'
    ),
    'btn_approve': '✅ Approuver',
    'btn_ban': '⛔️ Bannir',
    'admin_notify_fail': 'Impossible de notifier l’admin : {e}',
    'moderation_approved': '✅ Approuvé : {target}',
    'moderation_banned': '⛔️ Banni : {target}',
    'approved_user_dm': '✅ Accès approuvé. Tapez /start.',
    'banned_user_dm': '🚫 Vous êtes bloqué.',

    'users_not_found': '😕 Aucun utilisateur trouvé.',
    'users_page_info': '📄 Page {page}/{pages} — total : {total}',
    'user_card_html': (
        '<b>👤 Utilisateur</b>\n'
        '• ID : <code>{uid}</code>\n'
        '• Nom : {full_name}\n'
        '• Pseudo : {uname}\n'
        '• Langue : <code>{lang}</code>\n'
        '• Autorisé : {allowed}\n'
        '• Banni : {banned}\n'
        '• Conditions : {terms}\n'
        '• % par trade : <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 Liste noire',
    'btn_delete_user': '🗑 Supprimer de la BD',
    'btn_prev': '⬅️ Précédent',
    'btn_next': '➡️ Suivant',
    'nav_caption': '🧭 Navigation :',
    'bad_page': 'Page invalide.',
    'admin_user_delete_fail': '❌ Échec de suppression {target} : {error}',
    'admin_user_deleted': '🗑 Utilisateur {target} supprimé de la BD.',
    'user_access_approved': '✅ Accès approuvé. Tapez /start.',

    'admin_pause_all': '⏸️ Pause pour tous',
    'admin_resume_all': '▶️ Reprendre',
    'admin_close_longs': '🔒 Fermer tous les LONG',
    'admin_close_shorts': '🔓 Fermer tous les SHORT',
    'admin_cancel_limits': '❌ Supprimer les ordres limit',
    'admin_users': '👥 Utilisateurs',
    'admin_pause_notice': '⏸️ Trading & notifications en pause pour tous.',
    'admin_resume_notice': '▶️ Trading & notifications repris pour tous.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ Fermés au total {count} {type}.',
    'admin_canceled_limits_total': '✅ {count} ordres limit annulés.',

    'terms_btn_accept': '✅ Accepter',
    'terms_btn_decline': '❌ Refuser',

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
    'api_test_success':            'Connexion réussie!',
    'api_test_no_keys':            'Clés API non définies',
    'api_test_set_keys':           "Veuillez d'abord définir API Key et Secret.",
    'api_test_failed':             'Échec de la connexion',
    'api_test_error':              'Erreur',
    'api_test_check_keys':         'Veuillez vérifier vos identifiants API.',
    'api_test_status':             'Statut',
    'api_test_connected':          'Connecté',
    'balance_wallet':              'Solde du portefeuille',
    'balance_equity':              'Fonds propres',
    'balance_available':           'Disponible',
    'api_missing_notice':          "⚠️ Vous n'avez pas configuré de clés API. Veuillez ajouter votre clé API et votre secret dans les paramètres (boutons 🔑 API et 🔒 Secret), sinon le bot ne pourra pas trader pour vous.",
    'elcaro_ai_info':              '🤖 *Trading alimenté par l\'IA*',

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
    'strat_mode_demo':             '🧪 Démo',
    'strat_mode_real':             '💰 Réel',
    'strat_mode_both':             '🔄 Les deux',
    'strat_mode_changed':          '✅ Mode de trading {strategy}: {mode}',

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
    'fibonacci_limit_entry':           '📐 Fibonacci entrée limite {symbol} @ {price:.6f}',
    'fibonacci_limit_error':           '❌ Fibonacci erreur entrée limite: {msg}',
    'fibonacci_market_entry':          '🚀 Fibonacci marché {symbol} @ {price:.6f}',
    'fibonacci_market_error':          '❌ Fibonacci erreur marché: {msg}',
    'fibonacci_market_ok':             '📐 Fibonacci: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'fibonacci_analysis':              'Fibonacci: {side} @ {price}',
    'feature_fibonacci':               'Fibonacci',

    'scalper_limit_entry':           'Scalper: ordre limite {symbol} @ {price}',
    'scalper_limit_error':           'Scalper erreur limite: {msg}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper erreur: {msg}',

    # Strategy Settings
    'button_strategy_settings':      '⚙️ Paramètres stratégies',
    'strategy_settings_header':      '⚙️ *Paramètres des stratégies*',
    'strategy_param_header':         '⚙️ *Paramètres {name}*',
    'using_global':                  'Paramètres globaux',
    'global_default':                'Global',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ Paramètres DCA',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA Étape 1 %',
    'dca_leg2':                      '📉 DCA Étape 2 %',
    'param_percent':                 '📊 Entrée %',
    'param_sl':                      '🔻 Stop-Loss %',
    'param_tp':                      '🔺 Take-Profit %',
    'param_reset':                   '🔄 Réinitialiser au global',
    'btn_close':                     '❌ Fermer',
    'prompt_entry_pct':              'Entrez le % d\'entrée (risque par trade):',
    'prompt_sl_pct':                 'Entrez le % Stop-Loss:',
    'prompt_tp_pct':                 'Entrez le % Take-Profit:',
    'prompt_atr_periods':            'Entrez les périodes ATR (ex: 7):',
    'prompt_atr_mult':               'Entrez le multiplicateur ATR pour SL suiveur (ex: 1.0):',
    'prompt_atr_trigger':            'Entrez le % de déclenchement ATR (ex: 2.0):',
    'prompt_dca_leg1':               'Entrez % DCA Étape 1 (ex: 10):',
    'prompt_dca_leg2':               'Entrez % DCA Étape 2 (ex: 25):',
    'settings_reset':                'Paramètres réinitialisés au global',
    'strat_setting_saved':           '✅ {name} {param} défini à {value}',
    'dca_setting_saved':             '✅ DCA {leg} défini à {value}%',
    'invalid_number':                '❌ Nombre invalide. Entrez une valeur entre 0 et 100.',
    'dca_10pct':                     'DCA −{pct}%: renforcement {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: renforcement {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: Étape1=-{dca1}%, Étape2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 Périodes ATR',
    'param_atr_mult':                '📉 Multiplicateur ATR (pas SL)',
    'param_atr_trigger':             '🎯 Déclencheur ATR %',

    # Hardcoded strings fix
    'terms_unavailable':             'Conditions d\'utilisation non disponibles. Contactez l\'administrateur.',
    'terms_confirm_prompt':          'Veuillez confirmer:',
    'your_id':                       'Votre ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Erreur: {msg}',
    'error_fetch_balance':           '❌ Erreur de récupération du solde: {error}',
    'error_fetch_orders':            '❌ Erreur de récupération des ordres: {error}',
    'error_occurred':                '❌ Erreur: {error}',

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
    'stats_strategy_settings':       'Paramètres de stratégie',
    'settings_entry_pct':            'Entrée',
    'settings_leverage':             'Levier',
    'settings_trading_mode':         'Mode',
    'settings_direction':            'Direction',
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
    'param_leverage': '⚡ Levier',
    'prompt_leverage': 'Entrez le levier (1-100) :',
    'auto_default': 'Auto',

    # Elcaro AI
    'elcaro_ai_desc': '_Tous les paramètres sont parsés automatiquement depuis les signaux AI :_',

    # Scalper entries
    'scalper_market_entry': '🚀 Scalper market {symbol} @ {price:.6f}',
    'scalper_analysis': 'Scalper : {side} @ {price}',

    # Scryptomera feature
    'feature_scryptomera': 'Scryptomera',
    


    # Limit Ladder
    'limit_ladder': '📉 Échelle limite',
    'limit_ladder_header': "📉 *Paramètres de l'échelle limite*",
    'limit_ladder_settings': '⚙️ Paramètres échelle',
    'ladder_count': "Nombre d'ordres",
    'ladder_info': "_Ordres limites placés en dessous de l'entrée pour DCA. Chaque ordre a un % d'écart de l'entrée et un % du dépôt._",
    'prompt_ladder_pct_entry': "📉 Entrez % en dessous du prix d'entrée pour l'ordre {idx}:",
    'prompt_ladder_pct_deposit': '💰 Entrez % du dépôt pour l\'ordre {idx}:',
    'ladder_order_saved': '✅ Ordre {idx} enregistré: -{pct_entry}% @ {pct_deposit}% dépôt',
    'ladder_orders_placed': '📉 {count} ordres limite placés pour {symbol}',
    
    # Spot Trading Mode
    'spot_trading_mode': 'Mode de trading',
    'spot_btn_mode': 'Mode',
    
    # Stats PnL
    'stats_realized_pnl': 'Réalisé',
    'stats_unrealized_pnl': 'Non réalisé',
    'stats_combined_pnl': 'Combiné',
    'stats_spot': '💹 Spot',
    'stats_spot_title': 'Statistiques Spot DCA',
    'stats_spot_config': 'Configuration',
    'stats_spot_holdings': 'Positions',
    'stats_spot_summary': 'Résumé',
    'stats_spot_current_value': 'Valeur actuelle',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    # License status messages
    'no_license': '🚨 <b>ACCÈS REFUSÉ</b>\n\n⚠️ Pendant que vous lisez ceci, les traders Premium font des profits.\n\n💎 Débloquez votre potentiel: /subscribe\n\n<i>Chaque minute d\'attente = argent perdu</i>',
    'no_license_trading': '🚨 <b>TRADING BLOQUÉ</b>\n\n⚠️ 847 traders profitent EN CE MOMENT avec ElCaro.\n\n💎 Rejoignez-les: /subscribe\n\n<i>Le marché n\'attend personne.</i>',
    'license_required': '⚠️ Cette fonctionnalité nécessite un abonnement {required}.\n\nUtilisez /subscribe pour mettre à niveau.',
    'trial_demo_only': '⚠️ La licence d\'essai ne permet que le trading démo.\n\nPassez à Premium ou Basic pour le trading réel: /subscribe',
    'basic_strategy_limit': '⚠️ La licence Basic sur compte réel ne permet que: {strategies}\n\nPassez à Premium pour toutes les stratégies: /subscribe',
    
    # Subscribe menu - BLACK RHETORIC: Exclusivity + Scarcity
    'subscribe_menu_header': '👑 *ACCÈS VIP au Cercle des Traders d\'Élite*',
    'subscribe_menu_info': '''🔥 <b>847 traders</b> profitent déjà
⚡ Exécution <100ms | 🛡️ 664 tests de sécurité

<i>Choisissez votre niveau d\'accès :</i>''',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Essai (Gratuit)',
    'btn_enter_promo': '🎟 Code Promo',
    'btn_my_subscription': '📋 Mon Abonnement',
    
    # Premium plan - BLACK RHETORIC: Authority + Social Proof
    'premium_title': '👑 *PREMIUM — Le Choix des Gagnants*',
    'premium_desc': '''✅ Accès complet à toutes les fonctionnalités
✅ Les 5 stratégies: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ Trading Réel + Démo
✅ Support prioritaire
✅ SL/TP dynamique basé sur ATR
✅ Échelle limite DCA
✅ Toutes les futures mises à jour''',
    'premium_1m': '💎 1 Mois — {price} TRC',
    'premium_3m': '💎 3 Mois — {price} TRC (-10%)',
    'premium_6m': '💎 6 Mois — {price} TRC (-20%)',
    'premium_12m': '💎 12 Mois — {price} TRC (-30%)',
    
    # Basic plan
    'basic_title': '🥈 *PLAN BASIC*',
    'basic_desc': '''✅ Accès complet au compte démo
✅ Compte réel: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Fibonacci, Spot — Premium uniquement
✅ Support standard
✅ SL/TP dynamique basé sur ATR''',
    'basic_1m': '🥈 1 Mois — {price} TRC',
    
    # Trial plan - BLACK RHETORIC: FOMO + Urgency
    'trial_title': '🎁 *ESSAI GRATUIT — Offre Limitée!*',
    'trial_desc': '''✅ Accès complet au compte démo
✅ Les 5 stratégies en démo
❌ Trading réel non disponible
⏰ Durée: 7 jours
🎁 Une seule fois''',
    'trial_activate': '🎁 Activer l\'Essai Gratuit',
    'trial_already_used': '⚠️ Vous avez déjà utilisé votre essai gratuit.',
    'trial_activated': '🎉 Essai activé! Vous avez 7 jours d\'accès démo complet.',
    
    # Payment
    'payment_select_method': '💳 *Sélectionner le Mode de Paiement*',
    'btn_pay_trc': '◈ Triacelo Coin (TRC)',
    'btn_pay_ton': '💎 TON',
    'payment_trc_title': ' Paiement via TRC',
    'payment_trc_desc': 'Vous serez facturé {amount} TRC pour {plan} ({period}).',
    'payment_ton_title': '💎 Paiement via TON',
    'payment_ton_desc': '''Envoyez exactement *{amount} TON* à:

`{wallet}`

Après le paiement, cliquez sur le bouton ci-dessous pour vérifier.''',
    'btn_verify_ton': '✅ J\'ai payé — Vérifier',
    'payment_processing': '⏳ Traitement du paiement...',
    'payment_success': '🎉 Paiement réussi!\n\n{plan} activé jusqu\'au {expires}.',
    'payment_failed': '❌ Échec du paiement: {error}',
    
    # My subscription
    'my_subscription_header': '📋 *Mon Abonnement*',
    'my_subscription_active': '''📋 *Plan Actuel:* {plan}
⏰ *Expire le:* {expires}
📅 *Jours Restants:* {days}''',
    'my_subscription_none': '❌ Pas d\'abonnement actif.\n\nUtilisez /subscribe pour acheter un plan.',
    'my_subscription_history': '📜 *Historique des Paiements:*',
    'subscription_expiring_soon': '⚠️ Votre abonnement {plan} expire dans {days} jours!\n\nRenouvelez maintenant: /subscribe',
    
    # Promo codes
    'promo_enter': '🎟 Entrez votre code promo:',
    'promo_success': '🎉 Code promo appliqué!\n\n{plan} activé pour {days} jours.',
    'promo_invalid': '❌ Code promo invalide.',
    'promo_expired': '❌ Ce code promo a expiré.',
    'promo_used': '❌ Ce code promo a déjà été utilisé.',
    'promo_already_used': '❌ Vous avez déjà utilisé ce code promo.',
    
    # Admin license management
    'admin_license_menu': '🔑 *Gestion des Licences*',
    'admin_btn_grant_license': '🎁 Accorder Licence',
    'admin_btn_view_licenses': '📋 Voir Licences',
    'admin_btn_create_promo': '🎟 Créer Promo',
    'admin_btn_view_promos': '📋 Voir Promos',
    'admin_btn_expiring_soon': '⚠️ Expire Bientôt',
    'admin_grant_select_type': 'Sélectionnez le type de licence:',
    'admin_grant_select_period': 'Sélectionnez la période:',
    'admin_grant_enter_user': 'Entrez l\'ID utilisateur:',
    'admin_license_granted': '✅ {plan} accordé à l\'utilisateur {uid} pour {days} jours.',
    'admin_license_extended': '✅ Licence prolongée de {days} jours pour l\'utilisateur {uid}.',
    'admin_license_revoked': '✅ Licence révoquée pour l\'utilisateur {uid}.',
    'admin_promo_created': '✅ Code promo créé: {code}\nType: {type}\nJours: {days}\nUtilisations max: {max}',

    # =====================================================
    # ADMIN USER MANAGEMENT
    # =====================================================
    'admin_users_management': '👥 Utilisateurs',
    'admin_licenses': '🔑 Licences',
    'admin_search_user': '🔍 Trouver Utilisateur',
    'admin_users_menu': '👥 *Gestion des Utilisateurs*\n\nSélectionnez un filtre ou recherchez:',
    'admin_all_users': '👥 Tous les Utilisateurs',
    'admin_active_users': '✅ Actifs',
    'admin_banned_users': '🚫 Bannis',
    'admin_no_license': '❌ Sans Licence',
    'admin_no_users_found': 'Aucun utilisateur trouvé.',
    'admin_enter_user_id': '🔍 Entrez l\'ID utilisateur pour rechercher:',
    'admin_user_found': '✅ Utilisateur {uid} trouvé!',
    'admin_user_not_found': '❌ Utilisateur {uid} non trouvé.',
    'admin_invalid_user_id': '❌ ID utilisateur invalide. Entrez un nombre.',
    'admin_view_card': '👤 Voir Fiche',
    
    # User card
    'admin_user_card': '''👤 *Fiche Utilisateur*

📋 *ID:* `{uid}`
{status_emoji} *Statut:* {status}
📝 *Conditions:* {terms}

{license_emoji} *Licence:* {license_type}
📅 *Expire le:* {license_expires}
⏳ *Jours Restants:* {days_left}

🌐 *Langue:* {lang}
📊 *Mode Trading:* {trading_mode}
💰 *% par Trade:* {percent}%
🪙 *Monnaies:* {coins}

🔌 *Clés API:*
  Démo: {demo_api}
  Réel: {real_api}

📈 *Stratégies:* {strategies}

📊 *Statistiques:*
  Positions: {positions}
  Trades: {trades}
  PnL: {pnl}
  Winrate: {winrate}%

💳 *Paiements:*
  Total: {payments_count}
  TRC: {total_trc}

📅 *Première visite:* {first_seen}
🕐 *Dernière visite:* {last_seen}
''',
    
    # User actions
    'admin_btn_grant_lic': '🎁 Accorder',
    'admin_btn_extend': '⏳ Prolonger',
    'admin_btn_revoke': '🚫 Révoquer',
    'admin_btn_ban': '🚫 Bannir',
    'admin_btn_unban': '✅ Débannir',
    'admin_btn_approve': '✅ Approuver',
    'admin_btn_message': '✉️ Message',
    'admin_btn_delete': '🗑 Supprimer',
    
    'admin_user_banned': 'Utilisateur banni!',
    'admin_user_unbanned': 'Utilisateur débanni!',
    'admin_user_approved': 'Utilisateur approuvé!',
    'admin_confirm_delete': '⚠️ *Confirmer la suppression*\n\nL\'utilisateur {uid} sera définitivement supprimé!',
    'admin_confirm_yes': '✅ Oui, Supprimer',
    'admin_confirm_no': '❌ Annuler',
    
    'admin_select_license_type': 'Sélectionnez le type de licence pour l\'utilisateur {uid}:',
    'admin_select_period': 'Sélectionnez la période:',
    'admin_select_extend_days': 'Sélectionnez les jours à prolonger pour l\'utilisateur {uid}:',
    'admin_license_granted_short': 'Licence accordée!',
    'admin_license_extended_short': 'Prolongé de {days} jours!',
    'admin_license_revoked_short': 'Licence révoquée!',
    
    'admin_enter_message': '✉️ Entrez le message à envoyer à l\'utilisateur {uid}:',
    'admin_message_sent': '✅ Message envoyé à l\'utilisateur {uid}!',
    'admin_message_failed': '❌ Échec de l\'envoi du message: {error}',

    # Auto-synced missing keys
    'admin_all_payments': '📜 Tous les paiements',
    'admin_demo_stats': '🎮 Stats démo',
    'admin_enter_user_for_report': '👤 Entrez l\'ID utilisateur pour un rapport détaillé:',
    'admin_generating_report': '📊 Génération du rapport pour l\'utilisateur {uid}...',
    'admin_global_stats': '📊 Stats globales',
    'admin_no_payments_found': 'Aucun paiement trouvé.',
    'admin_payments': '💳 Paiements',
    'admin_payments_menu': '💳 *Gestion des paiements*',
    'admin_real_stats': '💰 Stats réelles',
    'admin_reports': '📊 Rapports',
    'admin_reports_menu': '''📊 *Rapports et analyses*

Sélectionnez le type de rapport:''',
    'admin_strategy_breakdown': '🎯 Par stratégie',
    'admin_top_traders': '🏆 Meilleurs traders',
    'admin_user_report': '👤 Rapport utilisateur',
    'admin_view_report': '📊 Voir le rapport',
    'admin_view_user': '👤 Fiche utilisateur',
    'all_positions_closed': 'Toutes les positions fermées',
    'btn_check_again': '🔄 Vérifier à nouveau',
    'button_admin': '👑 Admin',
    'button_licenses': '🔑 Licences',
    'button_subscribe': '💎 S\'abonner',
    'current': 'Actuel',
    'entry': 'Entrée',
    'max_positions_reached': '⚠️ Nombre maximum de positions atteint. Les nouveaux signaux seront ignorés jusqu\'à la fermeture d\'une position.',
    'payment_session_expired': '❌ Session de paiement expirée. Veuillez recommencer.',
    'payment_ton_not_configured': '❌ Les paiements TON ne sont pas configurés.',
    'payment_verifying': '⏳ Vérification du paiement...',
    'position': 'Position',
    'size': 'Taille',
    'stats_fibonacci': '📐 Fibonacci',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "Trading HyperLiquid",
    "hl_reset_settings": "🔄 Réinitialiser aux paramètres Bybit",



    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ Annulé.',
    'entry_pct_range_error': "❌ Le % d'entrée doit être entre 0.1 et 100.",
    'hl_no_history': '📭 Aucun historique de trades sur HyperLiquid.',
    'hl_no_orders': '📭 Aucun ordre ouvert sur HyperLiquid.',
    'hl_no_positions': '📭 Aucune position ouverte sur HyperLiquid.',
    'hl_setup_cancelled': '❌ Configuration HyperLiquid annulée.',
    'invalid_amount': '❌ Nombre invalide. Entrez un montant valide.',
    'leverage_range_error': "❌ L'effet de levier doit être entre 1 et 100.",
    'max_amount_error': '❌ Montant maximum est 100 000 USDT',
    'min_amount_error': '❌ Montant minimum est 1 USDT',
    'sl_tp_range_error': '❌ SL/TP % doit être entre 0.1 et 500.',


    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 Activer le DCA',
    'btn_ignore': '🔇 Ignorer',
    'dca_already_enabled': '✅ Le DCA est déjà activé!\n\n📊 <b>{symbol}</b>\nLe bot achètera automatiquement en cas de baisse:\n• -10% → ajout\n• -25% → ajout\n\nCela aide à moyenner le prix dentrée.',
    'dca_enable_error': '❌ Erreur: {error}',
    'dca_enabled_for_symbol': '✅ DCA activé!\n\n📊 <b>{symbol}</b>\nLe bot achètera automatiquement en cas de baisse:\n• -10% → ajout (moyennage)\n• -25% → ajout (moyennage)\n\n⚠️ Le DCA nécessite un solde suffisant pour les ordres supplémentaires.',
    'deep_loss_alert': '⚠️ <b>Position en perte profonde!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Perte: <code>{loss_pct:.2f}%</code>\n💰 Entrée: <code>{entry}</code>\n📍 Actuel: <code>{mark}</code>\n\n❌ Le stop-loss ne peut pas être défini au-dessus du prix dentrée.\n\n<b>Que faire?</b>\n• <b>Fermer</b> - verrouiller la perte\n• <b>DCA</b> - moyenner la position\n• <b>Ignorer</b> - laisser tel quel',
    'deep_loss_close_error': '❌ Erreur lors de la fermeture de la position: {error}',
    'deep_loss_closed': '✅ Position {symbol} fermée.\n\nPerte verrouillée. Parfois il vaut mieux accepter une petite perte que despérer un retournement.',
    'deep_loss_ignored': '�� Compris, position {symbol} laissée inchangée.\n\n⚠️ Rappel: sans stop-loss, le risque de pertes est illimité.\nVous pouvez fermer la position manuellement via /positions',
    'fibonacci_desc': '_Entrée, SL, TP - selon les niveaux Fibonacci du signal._',
    'fibonacci_info': '📐 *Stratégie Fibonacci Extension*',
    'prompt_min_quality': 'Entrez la qualité minimale % (0-100):',


    # Hardcore trading phrase
    'hardcore_mode': '💀 *MODE HARDCORE*: Pas de pitié, pas de regrets. Seulement le profit ou la mort! 🔥',

    # Wallet & TRC translations

    'payment_trc_insufficient': '''❌ Solde TRC insuffisant.

Votre solde: {balance} TRC
Requis: {required} TRC

Rechargez votre portefeuille pour continuer.''',
    'wallet_address': '''📍 Adresse: `{address}`''',
    'wallet_balance': '''💰 *Votre Portefeuille TRC*

◈ Solde: *{balance} TRC*
📈 En Staking: *{staked} TRC*
🎁 Récompenses en Attente: *{rewards} TRC*

💵 Valeur Totale: *${total_usd}*
📍 1 TRC = 1 USDT''',
    'wallet_btn_back': '''« Retour''',
    'wallet_btn_deposit': '''📥 Déposer''',
    'wallet_btn_history': '''📋 Historique''',
    'wallet_btn_stake': '''📈 Staking''',
    'wallet_btn_unstake': '''📤 Retirer du Staking''',
    'wallet_btn_withdraw': '''📤 Retirer''',
    'wallet_deposit_demo': '''🎁 Obtenir 100 TRC (Démo)''',
    'wallet_deposit_desc': '''Envoyez des tokens TRC à votre adresse de portefeuille:

`{address}`

💡 *Mode démo:* Cliquez ci-dessous pour des tokens de test gratuits.''',
    'wallet_deposit_success': '''✅ {amount} TRC déposés avec succès!''',
    'wallet_deposit_title': '''📥 *Déposer TRC*''',
    'wallet_history_empty': '''Aucune transaction.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} TRC
   {date}''',
    'wallet_history_title': '''📋 *Historique des Transactions*''',
    'wallet_stake_desc': '''Mettez vos TRC en staking pour gagner *12% APY*!

💰 Disponible: {available} TRC
📈 Actuellement en Staking: {staked} TRC
🎁 Récompenses en Attente: {rewards} TRC

Récompenses quotidiennes • Unstaking instantané''',
    'wallet_stake_success': '''✅ {amount} TRC mis en staking avec succès!''',
    'wallet_stake_title': '''📈 *Staking TRC*''',
    'wallet_title': '''◈ *Portefeuille TRC*''',
    'wallet_unstake_success': '''✅ {amount} TRC retirés + {rewards} TRC de récompenses!''',
    'wallet_withdraw_desc': '''Entrez l'adresse de destination et le montant:''',
    'wallet_withdraw_failed': '''❌ Retrait échoué: {error}''',
    'wallet_withdraw_success': '''✅ {amount} TRC retirés vers {address}''',
    'wallet_withdraw_title': '''📤 *Retirer TRC*''',


    'spot_freq_biweekly': '📅 Toutes les 2 semaines',
    'spot_trailing_enabled': '✅ Trailing TP activé : activation à +{activation}%, trail {trail}%',
    'spot_trailing_disabled': '❌ Trailing TP désactivé',
    'spot_grid_started': '🔲 Grid bot démarré pour {coin} : {levels} niveaux de ${low} à ${high}',
    'spot_grid_stopped': '⏹ Grid bot arrêté pour {coin}',
    'spot_limit_placed': '📝 Ordre limite placé : Achat {amount} {coin} à ${price}',
    'spot_limit_cancelled': '❌ Ordre limite annulé pour {coin}',
    'spot_freq_hourly': '⏰ Toutes les heures',
}
