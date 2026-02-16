# -*- coding: utf-8 -*-
TEXTS = {
    # Common UI
    'loader': '⏳ Chargement...',
    
    # Menu principal - Terminal de trading professionnel
    'welcome':                     '''🔥 <b>Enliko Trading Terminal</b>

⚡ <b>&lt; 100ms</b> exécution
🛡️ <b>Gestion des risques</b> intégrée
💎 <b>24/7</b> trading automatisé

Bybit • HyperLiquid • Multi-stratégie''',
    'button_orders':               '📊 Ordres',
    'button_positions':            '🎯 Positions',

    'button_balance': '💎 Portefeuille',
    'button_market': '📈 Marché',
    'button_strategies': '🤖 AI Bots',
    'button_subscribe': '🤝 SOUTENIR',
    'button_terminal': '💻 Terminal',
    'button_terminal': '💻 Terminal',
    'button_history':              '📜 Historique',
    'button_api_keys':             '🔑 Clés API',
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
    'positions_header':            '📊 Tes positions ouvertes :',

    # Position management (inline)
    'btn_close_position':          'Fermer la position',
    'btn_cancel':                  '❌ Annuler',
    'btn_back':                    '🔙 Retour',
    'position_already_closed':     'Position déjà fermée',
    'position_closed_success':     'Position fermée',
    'position_close_error':        'Erreur lors de la fermeture',

    # % per trade

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Ordres Limit uniquement : {state}',
    'feature_limit_only':          'Limit uniquement',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Indicateurs Enliko*',
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
        '<i>L\'IA Enliko travaille pour vous 24/7</i>'
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

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko Entrée Limit*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Enliko Limit erreur: {msg}',
    'elcaro_market_entry':         '🔥 *Enliko Entrée Market*\n• {symbol} {side}\n• Prix: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Enliko Market erreur: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

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
    'select_language':             '🌍 Choisissez votre langue:',
    'language_set':                '✅ Langue définie:',
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

    # API Settings
    'api_key_set':                 '✅ Set',
    'api_test_success':            'Connexion réussie!',
    'api_test_failed':             'Échec de la connexion',
    'balance_equity':              'Fonds propres',
    'balance_available':           'Disponible',
    'api_missing_notice':          "⚠️ Vous n'avez pas configuré de clés API. Veuillez ajouter votre clé API et votre secret dans les paramètres (boutons 🔑 API et 🔒 Secret), sinon le bot ne pourra pas trader pour vous.",
    'elcaro_ai_info':              '🤖 *Trading alimenté par l\'IA*',

    # Spot Trading
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_balance':                '💰 Spot Balance: {balance}',

    # Strategy trading mode

    # Enliko (Heatmap)

    # Fibonacci (Fibonacci Extension)

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
    'strat_elcaro':                  '🔥 Enliko',
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
    
    # Break-Even settings UI
    'be_settings_header':            '🔒 *Paramètres Break-Even*',
    'be_settings_desc':              '_Déplacer SL au prix d\'entrée quand le profit atteint le seuil_',
    'be_enabled_label':              '🔒 Break-Even',
    'be_trigger_label':              '🎯 Déclencheur BE %',
    'prompt_be_trigger':             'Entrez le déclencheur Break-Even % (ex: 1.0):',
    'prompt_long_be_trigger':        '📈 LONG Déclencheur BE %\n\nEntrez le % de profit pour déplacer SL:',
    'prompt_short_be_trigger':       '📉 SHORT Déclencheur BE %\n\nEntrez le % de profit pour déplacer SL:',
    'param_be_trigger':              '🎯 Déclencheur BE %',
    'be_moved_to_entry':             '🔒 {symbol}: SL déplacé au break-even @ {entry}',
    'be_status_enabled':             '✅ BE: {trigger}%',
    'be_status_disabled':            '❌ BE: Désactivé',
    
    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ TP Partiel',
    'partial_tp_status_enabled':     '✅ TP Partiel activé',
    'partial_tp_status_disabled':    '❌ TP Partiel désactivé',
    'partial_tp_step1_menu':         '✂️ *TP Partiel - Étape 1*\n\nFermer {close}% de la position à +{trigger}% de profit\n\n_Sélectionner paramètre:_',
    'partial_tp_step2_menu':         '✂️ *TP Partiel - Étape 2*\n\nFermer {close}% de la position à +{trigger}% de profit\n\n_Sélectionner paramètre:_',
    'trigger_pct':                   'Déclencheur',
    'close_pct':                     'Fermer',
    'prompt_long_ptp_1_trigger':     '📈 LONG Étape 1: Déclencheur %\n\nEntrez le % de profit:',
    'prompt_long_ptp_1_close':       '📈 LONG Étape 1: Fermer %\n\nEntrez le % de position à fermer:',
    'prompt_long_ptp_2_trigger':     '📈 LONG Étape 2: Déclencheur %\n\nEntrez le % de profit:',
    'prompt_long_ptp_2_close':       '📈 LONG Étape 2: Fermer %\n\nEntrez le % de position à fermer:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT Étape 1: Déclencheur %\n\nEntrez le % de profit:',
    'prompt_short_ptp_1_close':      '📉 SHORT Étape 1: Fermer %\n\nEntrez le % de position à fermer:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT Étape 2: Déclencheur %\n\nEntrez le % de profit:',
    'prompt_short_ptp_2_close':      '📉 SHORT Étape 2: Fermer %\n\nEntrez le % de position à fermer:',
    'partial_tp_executed':           '✂️ {symbol}: {close}% fermé à +{trigger}% de profit',

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
    'param_leverage': '⚡ Levier',
    'prompt_leverage': 'Entrez le levier (1-100) :',
    'auto_default': 'Auto',

    # Enliko AI
    'elcaro_ai_desc': '_Tous les paramètres sont parsés automatiquement depuis les signaux AI :_',

    # Scalper entries

    # Scryptomera feature
    

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
    'no_license': '🤝 *Community Membership*\n\nSupport our open-source project to access\nadditional community resources.\n\n👉 /subscribe — Support the project',
    'no_license_trading': '🤝 *Community Resource*\n\nThis resource is available to community supporters.\n\n👉 /subscribe — Support the project',
    'license_required': '🔒 *Supporter Resource*\n\nThis resource requires {required} membership.\n\n👉 /subscribe — Support the project',
    'trial_demo_only': '⚠️ *Explorer Access*\n\nExplorer access is limited to demo environment.\n\n👉 /subscribe — Become a supporter',
    'basic_strategy_limit': '⚠️ *Community Tier*\n\nAvailable templates: {strategies}\n\n👉 /subscribe — Upgrade your support',
    # Subscribe menu - BLACK RHETORIC: Exclusivity + Scarcity
    'subscribe_menu_header': '🤝 *Support Enliko*\n\nYour voluntary contribution helps maintain\nfree open-source community tools.\n\nChoose your support level:',
    'subscribe_menu_info': '_Select your support level:_',
    'btn_premium': '🤝 Patron',
    'btn_basic': '💚 Soutien',
    'btn_trial': '🆓 Explorateur (Gratuit)',
    'btn_enter_promo': '🎟 Code d\'invitation',
    'btn_my_subscription': '📋 Mon adhésion',
    # Premium plan - BLACK RHETORIC: Authority + Social Proof
    'premium_title': '🤝 *Patron Membership*',
    'premium_desc': '*Thank you for supporting our community!*\n\nAs a patron, you receive access to:\n✅ All community analysis templates\n✅ Demo & live environments\n✅ Priority community support\n✅ ATR risk management tools\n✅ DCA configuration tools\n✅ Early access to updates\n\n⚠️ _Educational tools only. Not financial advice._',
    'premium_1m': '🤝 1 Month — {price} ELC',
    'premium_3m': '🤝 3 Months — {price} ELC',
    'premium_6m': '🤝 6 Months — {price} ELC',
    'premium_12m': '🤝 12 Months — {price} ELC',
    # Basic plan
    'basic_title': '💚 *Supporter Membership*',
    'basic_desc': '*Thank you for your support!*\n\n✅ Demo + live environments\n✅ Templates: OI, RSI+BB\n✅ Bybit integration\n✅ ATR risk management tools\n\n⚠️ _Educational tools only. Not financial advice._',
    'basic_1m': '💚 1 Month — {price} ELC',
    # Trial plan - BLACK RHETORIC: FOMO + Urgency
    'trial_title': '🆓 *Explorer Access — 14 Days*',
    'trial_desc': '*Explore our community tools:*\n\n✅ Full demo environment\n✅ All analysis templates\n✅ 14 days access\n✅ No contribution required\n\n⚠️ _Educational tools only. Not financial advice._',
    'trial_activate': '🆓 Start Exploring',
    'trial_already_used': '⚠️ Explorer access already used. Consider supporting the project.',
    'trial_activated': '🎉 *Explorer Access Activated!*\n\n⏰ 14 days of full demo access.\n\n⚠️ _Educational tools only. Not financial advice._',
    # Payment
    'payment_select_method': '🤝 *How would you like to contribute?*',
    'btn_pay_elc': '◈ ELC',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' Paiement via ELC',
    'payment_elc_desc': 'Vous serez facturé {amount} ELC pour {plan} ({period}).',
    'payment_ton_title': '💎 Paiement via TON',
    'payment_ton_desc': '''Envoyez exactement *{amount} TON* à:

`{wallet}`

Après le paiement, cliquez sur le bouton ci-dessous pour vérifier.''',
    'btn_verify_ton': '✅ J\'ai payé — Vérifier',
    'payment_processing': '⏳ ...',
    'payment_success': '🎉 Thank you for your support!\n\n{plan} access activated until {expires}.',
    'payment_failed': '❌ Contribution failed: {error}',
    # My subscription
    'my_subscription_header': '📋 *My Membership*',
    'my_subscription_active': '''📋 *Plan Actuel:* {plan}
⏰ *Expire le:* {expires}
📅 *Jours Restants:* {days}''',
    'my_subscription_none': '❌ No active membership.\n\nUse /subscribe to support the project.',
    'my_subscription_history': '📜 *Historique des Paiements:*',
    'subscription_expiring_soon': '⚠️ Votre abonnement {plan} expire dans {days} jours!\n\nRenouvelez maintenant: /subscribe',
    
    # Promo codes
    'promo_enter': '🎟 Enter your invite code:',
    'promo_success': '🎉 Invite code applied!\n\n{plan} access for {days} days.',
    'promo_invalid': '❌ Invalid invite code.',
    'promo_expired': '❌ This invite code has expired.',
    'promo_used': '❌ This invite code has already been used.',
    'promo_already_used': '❌ You have already used this invite code.',
    # Admin license management
    'admin_license_menu': '🤝 *Membership Management*',
    'admin_btn_grant_license': '🎁 Grant Access',
    'admin_btn_view_licenses': '📋 View Members',
    'admin_btn_create_promo': '🎟 Create Invite',
    'admin_btn_view_promos': '📋 View Invites',
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
  ELC: {total_elc}

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
    'btn_check_again': '🔄 Check',
    'payment_session_expired': '❌ Session de paiement expirée. Veuillez recommencer.',
    'payment_ton_not_configured': '❌ Les paiements TON ne sont pas configurés.',
    'payment_verifying': '⏳ Vérification du paiement...',
    'stats_fibonacci': '📐 Fibonacci',

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

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ Solde ELC insuffisant.

Votre solde: {balance} ELC
Requis: {required} ELC

Rechargez votre portefeuille pour continuer.''',
    'wallet_address': '''📍 Adresse: `{address}`''',
    'wallet_balance': '''💰 *Votre Portefeuille ELC*

◈ Solde: *{balance} ELC*
📈 En Staking: *{staked} ELC*
🎁 Récompenses en Attente: *{rewards} ELC*

💵 Valeur Totale: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« Retour''',
    'wallet_btn_deposit': '''📥 Déposer''',
    'wallet_btn_history': '''📋 Historique''',
    'wallet_btn_stake': '''📈 Staking''',
    'wallet_btn_unstake': '''📤 Retirer du Staking''',
    'wallet_btn_withdraw': '''📤 Retirer''',
    'wallet_deposit_demo': '''🎁 Obtenir 100 ELC (Démo)''',
    'wallet_deposit_desc': '''Envoyez des tokens ELC à votre adresse de portefeuille:

`{address}`

💡 *Mode démo:* Cliquez ci-dessous pour des tokens de test gratuits.''',
    'wallet_deposit_success': '''✅ {amount} ELC déposés avec succès!''',
    'wallet_deposit_title': '''📥 *Déposer ELC*''',
    'wallet_history_empty': '''Aucune transaction.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *Historique des Transactions*''',
    'wallet_stake_desc': '''Mettez vos ELC en staking pour gagner *12% APY*!

💰 Disponible: {available} ELC
📈 Actuellement en Staking: {staked} ELC
🎁 Récompenses en Attente: {rewards} ELC

Récompenses quotidiennes • Unstaking instantané''',
    'wallet_stake_success': '''✅ {amount} ELC mis en staking avec succès!''',
    'wallet_stake_title': '''📈 *Staking ELC*''',
    'wallet_title': '''◈ *Portefeuille ELC*''',
    'wallet_unstake_success': '''✅ {amount} ELC retirés + {rewards} ELC de récompenses!''',
    'wallet_withdraw_desc': '''Entrez l'adresse de destination et le montant:''',
    'wallet_withdraw_failed': '''❌ Retrait échoué: {error}''',
    'wallet_withdraw_success': '''✅ {amount} ELC retirés vers {address}''',
    'wallet_withdraw_title': '''📤 *Retirer ELC*''',

    'spot_freq_hourly': '⏰ Toutes les heures',

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
    'error_insufficient_balance': '💰 Fonds insuffisants sur votre compte pour ouvrir une position. Rechargez votre solde ou réduisez la taille de la position.',
    'error_order_too_small': '📉 Taille de l\'ordre trop petite (minimum 5$). Augmentez Entry% ou rechargez votre solde.',
    'error_api_key_expired': '🔑 Clé API expirée ou invalide. Mettez à jour vos clés API dans les paramètres.',
    'error_api_key_missing': '🔑 Clés API non configurées. Ajoutez les clés Bybit dans le menu 🔗 API Keys.',
    'error_rate_limit': '⏳ Trop de requêtes. Attendez une minute et réessayez.',
    'error_position_not_found': '📊 Position non trouvée ou déjà fermée.',
    'error_leverage_error': '⚙️ Erreur de configuration de l\'effet de levier. Essayez de le configurer manuellement sur l\'exchange.',
    'error_network_error': '🌐 Problème réseau. Réessayez plus tard.',
    'error_sl_tp_invalid': '⚠️ Impossible de définir SL/TP: prix trop proche du prix actuel. Sera mis à jour au prochain cycle.',
    'error_equity_zero': '💰 Le solde de votre compte est nul. Rechargez votre compte Demo ou Real pour trader.',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 Terminal',
    'exchange_mode_activated_bybit': '🟠 *Mode Bybit activé*',
    'exchange_mode_activated_hl': '🔷 *Mode HyperLiquid activé*',
    'error_processing_request': '⚠️ Erreur lors du traitement de la demande',
    'unauthorized_admin': '❌ Non autorisé. Cette commande est réservée à l\'administrateur.',
    'error_loading_dashboard': '❌ Erreur de chargement du tableau de bord.',
    'unauthorized': '❌ Non autorisé.',
    'processing_blockchain': '⏳ Traitement de la transaction blockchain...',
    'verifying_payment': '⏳ Vérification du paiement sur la blockchain TON...',
    'no_wallet_configured': '❌ Aucun portefeuille configuré.',
    'use_start_menu': 'Utilisez /start pour revenir au menu principal.',

    # 2FA Confirmation de connexion
    'login_approved': '✅ Connexion approuvée!\n\nVous pouvez maintenant continuer dans votre navigateur.',
    'login_denied': '❌ Connexion refusée.\n\nSi ce n\'était pas vous, vérifiez vos paramètres de sécurité.',
    'login_expired': '⏰ Confirmation expirée. Veuillez réessayer.',
    'login_error': '⚠️ Erreur de traitement. Veuillez réessayer plus tard.',

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
    
    'disclaimer_execution': (
        '⚠️ By proceeding, you acknowledge:\n'
        '• You are responsible for all trading decisions\n'
        '• This is an educational tool, not financial advice\n'
        '• You understand the risks of cryptocurrency trading\n'
        '• Past performance does not guarantee future results'
    ),
    
    # Disclaimer acceptance buttons and messages
    'disclaimer_short': '⚠️ _Educational tools only. Not financial advice. Trading involves risk._',
    'disclaimer_trading': (
        '⚠️ *IMPORTANT DISCLAIMER*\n\n'
        'This platform provides educational tools for learning about '
        'cryptocurrency markets. It is NOT:\n'
        '• Financial advice\n'
        '• Investment recommendation\n'
        '• Guaranteed profit system\n\n'
        'Trading cryptocurrencies involves substantial risk of loss. '
        'You may lose some or all of your investment. '
        'Only trade with funds you can afford to lose.\n\n'
        'Past performance does not guarantee future results.'
    ),
    
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
    
    'welcome_back': (
        '📊 *Enliko Trading Tools*\n\n'
        '⚠️ _Educational platform. Not financial advice._\n\n'
        '👇 Select an option:'
    ),
    
    # =====================================================
    # LEGAL DISCLAIMERS (REQUIRED)
    # =====================================================
    

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
    'subscribe_menu_info': '_Select a plan to continue:_',
    'wallet_deposit_desc': 'Send ELC tokens to:\n\n`{address}`',
    'wallet_history_item': '{type_emoji} {type}: {amount:+.2f} ELC\n   {date}',


    # Daily Digest
    'digest_title': '📊 Rapport Quotidien',
    'digest_detailed_title': '📋 Rapport Détaillé',
    'digest_date_format': '%d %B %Y',
    'digest_filter_all': '🌍 Toutes les bourses',
    'digest_no_trades': '📭 Aucun trade pour ce filtre',
    'digest_no_trades_hint': 'Essayez une autre combinaison.',
    'digest_total_pnl': 'PnL Total',
    'digest_statistics': 'Statistiques',
    'digest_trades': 'Trades',
    'digest_wins_losses': 'Gains/Pertes',
    'digest_win_rate': 'Taux de réussite',
    'digest_avg_pnl': 'PnL Moyen',
    'digest_best_trade': 'Meilleur trade',
    'digest_worst_trade': 'Pire trade',
    'digest_keep_improving': 'Continue à progresser ! 💪',
    'digest_vibe_amazing': 'Journée incroyable !',
    'digest_vibe_nice': 'Bon travail !',
    'digest_vibe_breakeven': 'Journée neutre',
    'digest_vibe_small_loss': 'Petite perte',
    'digest_vibe_tough': 'Journée difficile',
    'digest_btn_all': 'Tout',
    'digest_btn_bybit': '🟠 Bybit',
    'digest_btn_hl': '🔷 HL',
    'digest_btn_demo': '🧪 Démo',
    'digest_btn_real': '💼 Réel',
    'digest_btn_testnet': '🧪 Testnet',
    'digest_btn_mainnet': '🌐 Mainnet',
    'digest_btn_detailed': '📋 Détails',
    'digest_btn_close': '❌ Fermer',
    'digest_btn_back': '◀️ Retour',
    'digest_by_exchange': 'Par bourse',
    'digest_by_strategy': 'Par stratégie',
    'digest_top_symbols': 'Top Symboles',
    'digest_filter_bybit': '🟠 Bybit',
    'digest_filter_hl': '🔷 HyperLiquid',
    'digest_filter_demo': '🧪 Démo',
    'digest_filter_real': '💼 Réel',
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
