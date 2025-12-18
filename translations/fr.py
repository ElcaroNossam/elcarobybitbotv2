# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu
    'welcome':                     '👋 Salut ! Choisis une action :',
    'guide_caption':               '📚 Guide Utilisateur du Bot de Trading\n\nLisez ce guide pour apprendre à configurer les stratégies et utiliser le bot efficacement.',
    'privacy_caption':             '📜 Politique de Confidentialité & Conditions d\'Utilisation\n\nVeuillez lire ce document attentivement.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 Secret',
    'button_api_settings':         '🔑 API',
    'button_balance':              '💰 Solde USDT',
    'button_orders':               '📜 Mes ordres',
    'button_positions':            '📊 Positions',
    'button_percent':              '🎚 % par trade',
    'button_coins':                '💠 Groupe de coins',
    'button_market':               '📈 Marché',
    'button_manual_order':         '✋ Ordre manuel',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ Annuler l’ordre',
    'button_limit_only':           '🎯 Limit uniquement',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_settings':             '⚙️ Réglages',
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
    'lang_fr':                     'Français',

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
    'account_balance':             '💰 Solde USDT : `{balance:.2f}`',
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
    'positions_overall':           'PnL non réalisé total : {pnl:+.2f} ({pct:+.2f}%)',

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

    # Auto notifications
    'new_position':                '🚀 Nouvelle position {symbol} @ {entry:.6f}, taille={size}',
    'sl_auto_set':                 '🛑 SL défini automatiquement : {price:.6f}',
    'auto_close_position':         '⏱ Position {symbol} (TF={tf}) ouverte > {tf} et perdante, clôturée auto.',
    'position_closed': (
        '🔔 Position {symbol} clôturée par *{reason}* :\n'
        '• Strategy: `{strategy}`\n'
        '• Entrée : `{entry:.8f}`\n'
        '• Sortie : `{exit:.8f}`\n'
        '• PnL    : `{pnl:+.2f} USDT ({pct:+.2f}%)`'
    ),

    # Entries & errors
    'oi_limit_entry':              '🟡 Entrée Limit OI {symbol} @ {price:.6f}',
    'oi_limit_error':              '❌ Erreur d’entrée Limit : {msg}',
    'oi_market_entry':             '🚀 Entrée Market OI {symbol} @ {price:.6f}',
    'oi_market_error':             '❌ Erreur d’entrée Market : {msg}',

    'rsi_bb_limit_entry':          '🟡 Entrée Limit RSI+BB {symbol} @ {price:.6f}',
    'rsi_bb_market_entry':         '✅ Market RSI+BB {symbol} @ {price:.6f}',
    'rsi_bb_market_error':         '❌ Erreur Market : {msg}',

    'oi_analysis':                 '📊 *Analyse OI {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 Entrée Limit (Scryptomera) {symbol} @ {price:.6f}',
    'bitk_limit_error':            '❌ Erreur Limit (Scryptomera) : {msg}',
    'bitk_market_entry':           '🔮 Market (Scryptomera) {symbol} @ {price:.6f}',
    'bitk_market_error':           '❌ Erreur Market (Scryptomera) : {msg}',

    # Admin panel
    'admin_panel':                 '👑 Panneau admin :',
    'admin_pause':                 '⏸️ Trading & notifications en pause pour tous.',
    'admin_resume':                '▶️ Trading & notifications repris pour tous.',
    'admin_closed':                '✅ Fermetures totales : {count} {type}.',
    'admin_canceled_limits':       '✅ {count} ordres Limit annulés.',

    # Coin groups
    'select_coin_group':           'Choisis le groupe de coins :',
    'group_all':                   'ALL',
    'group_top100':                'TOP100',
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

    # Wyckoff (Fibonacci Extension)
    'wyckoff_limit_entry':           '📐 Wyckoff entrée limite {symbol} @ {price:.6f}',
    'wyckoff_limit_error':           '❌ Wyckoff erreur entrée limite: {msg}',
    'wyckoff_market_entry':          '🚀 Wyckoff marché {symbol} @ {price:.6f}',
    'wyckoff_market_error':          '❌ Wyckoff erreur marché: {msg}',
    'wyckoff_market_ok':             '📐 Wyckoff: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'wyckoff_analysis':              'Wyckoff: {side} @ {price}',
    'feature_wyckoff':               'Wyckoff',

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
    'strat_wyckoff':                 '📐 Wyckoff',
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
    'stats_period_today':            'Today',
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
    'elcaro_ai_note': "🤖 *L'IA fait le travail pour vous!*",
    'elcaro_ai_params_header': 'Les éléments suivants sont analysés à partir de chaque signal:',
    'elcaro_ai_params_list': '• SL% • TP% • ATR • Levier • Période',

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
    'no_license': '⚠️ Vous avez besoin d\'un abonnement actif pour utiliser cette fonctionnalité.\n\nUtilisez /subscribe pour acheter une licence.',
    'no_license_trading': '⚠️ Vous avez besoin d\'un abonnement actif pour trader.\n\nUtilisez /subscribe pour acheter une licence.',
    'license_required': '⚠️ Cette fonctionnalité nécessite un abonnement {required}.\n\nUtilisez /subscribe pour mettre à niveau.',
    'trial_demo_only': '⚠️ La licence d\'essai ne permet que le trading démo.\n\nPassez à Premium ou Basic pour le trading réel: /subscribe',
    'basic_strategy_limit': '⚠️ La licence Basic sur compte réel ne permet que: {strategies}\n\nPassez à Premium pour toutes les stratégies: /subscribe',
    
    # Subscribe menu
    'subscribe_menu_header': '💎 *Plans d\'Abonnement*',
    'subscribe_menu_info': 'Choisissez votre plan pour débloquer les fonctionnalités de trading:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 Essai (Gratuit)',
    'btn_enter_promo': '🎟 Code Promo',
    'btn_my_subscription': '📋 Mon Abonnement',
    
    # Premium plan
    'premium_title': '💎 *PLAN PREMIUM*',
    'premium_desc': '''✅ Accès complet à toutes les fonctionnalités
✅ Les 5 stratégies: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ Trading Réel + Démo
✅ Support prioritaire
✅ SL/TP dynamique basé sur ATR
✅ Échelle limite DCA
✅ Toutes les futures mises à jour''',
    'premium_1m': '💎 1 Mois — {price}⭐',
    'premium_3m': '💎 3 Mois — {price}⭐ (-15%)',
    'premium_6m': '💎 6 Mois — {price}⭐ (-25%)',
    'premium_12m': '💎 12 Mois — {price}⭐ (-35%)',
    
    # Basic plan
    'basic_title': '🥈 *PLAN BASIC*',
    'basic_desc': '''✅ Accès complet au compte démo
✅ Compte réel: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Wyckoff, Spot — Premium uniquement
✅ Support standard
✅ SL/TP dynamique basé sur ATR''',
    'basic_1m': '🥈 1 Mois — {price}⭐',
    
    # Trial plan
    'trial_title': '🎁 *PLAN D\'ESSAI (GRATUIT)*',
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
    'btn_pay_stars': '⭐ Telegram Stars',
    'btn_pay_ton': '💎 TON',
    'payment_stars_title': '⭐ Paiement via Telegram Stars',
    'payment_stars_desc': 'Vous serez facturé {amount}⭐ pour {plan} ({period}).',
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
  Stars: {total_stars}⭐

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
}
