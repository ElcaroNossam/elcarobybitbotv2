# -*- coding: utf-8 -*-
TEXTS = {
    # Menú principal - Terminal de trading profesional
    'welcome':                     '''🔥 <b>Enliko Trading Terminal</b>

⚡ <b>&lt; 100ms</b> ejecución
🛡️ <b>Gestión de riesgos</b> integrada
💎 <b>24/7</b> trading automatizado

Bybit • HyperLiquid • Multi-estrategia''',
    'no_strategies':               '❌ Sin estrategias activas',
    'guide_caption':               '📚 <b>Guía de usuario</b>\n\nConfiguración API, estrategias, gestión de riesgos.',
    'privacy_caption':             '📜 <b>Privacidad</b>\n\n🔐 Almacenamiento cifrado\n✅ Sin compartir datos',
    
    # ═══════════════════════════════════════════════════════════════════
    # MODERN MENU BUTTONS - Stylish & Persuasive (ES)
    # ═══════════════════════════════════════════════════════════════════
    'button_api':                  '🔐 Conectar API',
    'button_secret':               '🔑 Secreto',
    'button_api_settings':         '⚙️ Config API',
    'button_subscribe':            '👑 PREMIUM',
    'button_licenses':             '🎫 Licencias',
    'button_admin':                '🛡️ Admin',
    'button_balance':              '💎 Portafolio',
    'button_orders':               '📊 Órdenes',
    'button_positions':            '🎯 Posiciones',
    'button_history':              '📜 Historial',
    'button_strategies':           '🤖 Bots IA',
    'button_api_keys':             '🔗 Exchange',
    'button_bybit':                '🟠 Bybit',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_switch_bybit':         '🔄 Bybit',
    'button_switch_hl':            '🔄 HL',
    'button_percent':              '⚡ Riesgo %',
    'button_coins':                '🪙 Monedas',
    'button_market':               '📈 Mercado',
    'button_manual_order':         '🎯 Sniper',
    'button_update_tpsl':          '🛡️ TP/SL',
    'button_cancel_order':         '✖️ Cancelar',
    'button_limit_only':           '📍 Límite',
    'button_toggle_oi':            '🐋 OI Tracker',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_scalper':              '⚡ Scalper',
    'button_elcaro':               '🔥 Enliko',
    'button_fibonacci':            '📐 Fibonacci',
    'button_settings':             '⚙️ Config',
    'button_indicators':           '📡 Señales',
    'button_support':              '💬 Soporte',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',
    'config_trade_scalper':        '🎯 Scalper: {state}',
    'config_trade_elcaro':         '🔥 Enliko: {state}',
    'config_trade_fibonacci':      '📐 Fibonacci: {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 El modo TP/SL ahora es: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'Porcentaje fijo',

    # Limits
    'limit_positions_exceeded':    '🚫 Límite de posiciones abiertas superado ({max})',
    'limit_limit_orders_exceeded': '🚫 Límite de órdenes Limit superado ({max})',

    # Languages
    'select_language':             'Selecciona idioma:',
    'language_set':                'Idioma establecido en:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'Selecciona tipo de orden:',
    'limit_order_format': (
        "Introduce parámetros de orden Limit:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "donde SIDE = LONG o SHORT\n"
        "Ejemplo: `BTCUSDT LONG 20000 0.1`\n\n"
        "Para cancelar, envía ❌ Cancelar orden"
    ),
    'market_order_format': (
        "Introduce parámetros de orden Market:\n"
        "`SYMBOL SIDE QTY`\n"
        "donde SIDE = LONG o SHORT\n"
        "Ejemplo: `BTCUSDT SHORT 0.1`\n\n"
        "Para cancelar, envía ❌ Cancelar orden"
    ),
    'order_success':               '✅ ¡Orden creada con éxito!',
    'order_create_error':          '❌ No se pudo crear la orden: {msg}',
    'order_fail_leverage':         (
        "❌ Orden no creada: el apalancamiento en tu cuenta Bybit es demasiado alto para este tamaño.\n"
        "Reduce el apalancamiento en la configuración de Bybit."
    ),
    'order_parse_error':           '❌ Error al interpretar: {error}',
    'price_error_min':             '❌ Error de precio: debe ser ≥{min}',
    'price_error_step':            '❌ Error de precio: debe ser múltiplo de {step}',
    'qty_error_min':               '❌ Error de cantidad: debe ser ≥{min}',
    'qty_error_step':              '❌ Error de cantidad: debe ser múltiplo de {step}',

    # Loading…
    'loader':                      '⏳ Recopilando datos…',

    # Market command
    'market_status_heading':       '*Estado del mercado:*',
    'market_dominance_header':    'Top Monedas por Dominancia',
    'market_total_header':        'Capitalización Total',
    'market_indices_header':      'Índices del Mercado',
    'usdt_dominance':              'Dominancia USDT',
    'btc_dominance':               'Dominancia BTC',
    'dominance_rising':            '↑ en alza',
    'dominance_falling':           '↓ a la baja',
    'dominance_stable':            '↔️ estable',
    'dominance_unknown':           '❔ sin datos',
    'btc_price':                   'Precio BTC',
    'last_24h':                    'en las últimas 24 h',
    'alt_signal_label':            'Señal de altcoin',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*Últimas noticias (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'No se encontró precio de ejecución para el cierre',

    # /account
    'account_balance':             '💰 Saldo USDT: `{balance:.2f}`',
    'account_realized_header':     '📈 *PnL realizado:*',
    'account_realized_day':        '  • Hoy   : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 días: `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *PnL no realizado:*',
    'account_unreal_total':        '  • Total : `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % de IM: `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *Tu configuración:*',
    'config_percent':              '• 🎚 % por operación : `{percent}%`',
    'config_coins':                '• 💠 Monedas         : `{coins}`',
    'config_limit_only':           '• 🎯 Órdenes Limit   : {state}',
    'config_atr_mode':             '• 🏧 SL con ATR      : {atr}',
    'config_trade_oi':             '• 📊 Operar OI       : {oi}',
    'config_trade_rsi_bb':         '• 📈 Operar RSI+BB   : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%             : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%             : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 No hay órdenes abiertas',
    'open_orders_header':          '*📒 Órdenes abiertas:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • Lado : `{side}`\n"
        "   • Cant.: `{qty}`\n"
        "   • Precio: `{price}`\n"
        "   • ID   : `{id}`"
    ),
    'open_orders_error':           '❌ Error al obtener órdenes: {error}',

    # Manual coin selection
    'enter_coins':                 "Introduce símbolos separados por coma, p. ej.:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ Monedas seleccionadas: {coins}',

    # Positions
    'no_positions':                '🚫 No hay posiciones abiertas',
    'positions_header':            '📊 Tus posiciones abiertas:',
    'position_item':               (
        "— Posición #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • Tamaño          : {size}\n"
        "  • Precio de entrada: {avg:.8f}\n"
        "  • Precio mark     : {mark:.8f}\n"
        "  • Liquidación     : {liq}\n"
        "  • Margen inicial  : {im:.2f}\n"
        "  • Margen mant.    : {mm:.2f}\n"
        "  • Balance posición: {pm:.2f}\n"
        "  • Take Profit     : {tp}\n"
        "  • Stop Loss       : {sl}\n"
        "  • PnL no realizado: {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'position_item_v2':            (
        "— #{idx}: {symbol} | {side} (x{leverage}) [{strategy}]\n"
        "  • Tamaño         : {size}\n"
        "  • Precio entrada : {avg:.8f}\n"
        "  • Precio mark    : {mark:.8f}\n"
        "  • Liquidación    : {liq}\n"
        "  • Margen inicial : {im:.2f}\n"
        "  • Margen mant.   : {mm:.2f}\n"
        "  • Take Profit    : {tp}\n"
        "  • Stop Loss      : {sl}\n"
        "  {pnl_emoji} PnL no real. : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'pnl_by_strategy':             '📊 *PnL por estrategia:*',
    'pnl_by_exchange':             '🏦 *PnL por exchange:*',
    'positions_overall':           'PnL no realizado total: {pnl:+.2f} ({pct:+.2f}%)',

    # Position management (inline)
    'open_positions_header':       '📊 *Posiciones abiertas*',
    'positions_count':             'posiciones',
    'positions_count_total':       'Total de posiciones',
    'total_unrealized_pnl':        'PnL no realizado total',
    'total_pnl':                   'P/L total',
    'btn_close_short':             'Cerrar',
    'btn_close_all':               'Cerrar todas las posiciones',
    'btn_close_position':          'Cerrar posición',
    'btn_confirm_close':           'Confirmar cierre',
    'btn_confirm_close_all':       'Sí, cerrar todas',
    'btn_cancel':                  '❌ Cancelar',
    'btn_back':                    '🔙 Volver',
    'confirm_close_position':      'Cerrar posición',
    'confirm_close_all':           'Cerrar TODAS las posiciones',
    'position_not_found':          'Posición no encontrada o ya cerrada',
    'position_already_closed':     'Posición ya cerrada',
    'position_closed_success':     'Posición cerrada',
    'position_close_error':        'Error al cerrar posición',
    'positions_closed':            'Posiciones cerradas',
    'errors':                      'Errores',

    # % per trade
    'set_percent_prompt':          'Introduce el porcentaje del saldo por operación (ej. 2.5):',
    'percent_set_success':         '✅ % por operación establecido: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 Solo órdenes Limit: {state}',
    'feature_limit_only':          'Solo Limit',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Indicadores Enliko*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. Tendencia adaptativa',
    'indicator_4':                 '4. Regresión dinámica',

    # Support
    'support_prompt':              '✉️ ¿Necesitas ayuda? Pulsa abajo:',
    'support_button':              'Contactar soporte',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 No hay posiciones abiertas',
    'update_tpsl_prompt':          'Introduce SYMBOL TP SL, p. ej.:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ Formato inválido. Usa: SYMBOL TP SL\nEj.: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Introduce tu Bybit API Key:',
    'api_saved':                   '✅ API Key guardada',
    'enter_secret':                'Introduce tu Bybit API Secret:',
    'secret_saved':                '✅ API Secret guardado',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ Introduce el valor de TP%',
    'tp_set_success':              '✅ TP% establecido: {pct}%',
    'enter_sl':                    '❌ Introduce el valor de SL%',
    'sl_set_success':              '✅ SL% establecido: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: requiere 4 argumentos (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: requiere 3 argumentos (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE debe ser LONG o SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ API Key/Secret no establecido',
    'bybit_invalid_response':      '❌ Respuesta inválida de Bybit',
    'bybit_error':                 '❌ Error de Bybit {path}: {data}',

    # Auto notifications - BLACK RHETORIC: Achievement + FOMO
    'new_position': '''💎 *¡TRADE EJECUTADO!*
🎯 {symbol} | {side} @ `{entry:.6f}`
📊 Tamaño: `{size}`
📍 {exchange} • {market_type}

_Enliko IA detectó la oportunidad. Estás dentro._''',
    'sl_auto_set':                 '🛡️ *¡Capital protegido!* SL @ `{price:.6f}`\n_Gestión de riesgo inteligente activada._',
    'auto_close_position':         '⚡ Posición {symbol} cerrada automáticamente — _IA protegiendo tu capital_',
    'position_closed': '''🏆 *¡TRADE COMPLETADO!*
🎯 {symbol} • {reason}
📍 Estrategia: `{strategy}`

📈 Entrada: `{entry:.8f}`
📉 Salida: `{exit:.8f}`
💰 *PnL: {pnl:+.2f} USDT ({pct:+.2f}%)*

_Cada trade es un paso hacia la libertad financiera._
📍 {exchange} • {market_type}''',

    # Entries & errors - formato unificado con info completa
    'oi_limit_entry':              '📉 *OI Entrada Limit*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI Limit error: {msg}',
    'oi_market_entry':             '📉 *OI Entrada Market*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI Market error: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB Entrada Limit*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB Entrada Market*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB Market error: {msg}',

    'oi_analysis':                 '📊 *Análisis OI de {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera Entrada Limit*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera Limit error: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera Entrada Market*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera Market error: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>¡Saldo insuficiente!</b>\n\n💰 No hay fondos suficientes en su cuenta {account_type} para abrir esta posición.\n\n<b>Soluciones:</b>\n• Recargar saldo\n• Reducir tamaño de posición (% por operación)\n• Reducir apalancamiento\n• Cerrar algunas posiciones abiertas',
    'insufficient_balance_error_extended': '❌ <b>¡Saldo insuficiente!</b>\n\n📊 Estrategia: <b>{strategy}</b>\n🪙 Símbolo: <b>{symbol}</b> {side}\n\n💰 No hay fondos suficientes en su cuenta {account_type}.\n\n<b>Soluciones:</b>\n• Recargar saldo\n• Reducir tamaño de posición (% por operación)\n• Reducir apalancamiento\n• Cerrar algunas posiciones abiertas',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>¡Apalancamiento muy alto!</b>\n\n⚙️ Su apalancamiento configurado excede el máximo permitido para este símbolo.\n\n<b>Máximo permitido:</b> {max_leverage}x\n\n<b>Solución:</b> Vaya a la configuración de estrategia y reduzca el apalancamiento.',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>¡Límite de posición excedido!</b>\n\n📊 Estrategia: <b>{strategy}</b>\n🪙 Símbolo: <b>{symbol}</b>\n\n⚠️ Su posición excedería el límite máximo.\n\n<b>Soluciones:</b>\n• Reducir apalancamiento\n• Reducir tamaño de posición\n• Cerrar algunas posiciones',
    

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper Entrada Limit*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper Limit error: {msg}',
    'scalper_market_entry':        '⚡ *Scalper Entrada Market*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper Market error: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko Entrada Limit*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Enliko Limit error: {msg}',
    'elcaro_market_entry':         '🔥 *Enliko Entrada Market*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Enliko Market error: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci Entrada Limit*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci Limit error: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci Entrada Market*\n• {symbol} {side}\n• Precio: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci Market error: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 Panel de administración:',
    'admin_pause':                 '⏸️ Trading y notificaciones pausados para todos.',
    'admin_resume':                '▶️ Trading y notificaciones reanudados para todos.',
    'admin_closed':                '✅ Cerradas en total {count} {type}.',
    'admin_canceled_limits':       '✅ Canceladas {count} órdenes Limit.',

    # Coin groups
    'select_coin_group':           'Selecciona grupo de monedas:',
    'group_all':                   'ALL',
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ Grupo de monedas establecido: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *Análisis RSI+BB*\n'
        '• Precio: `{price:.6f}`\n'
        '• RSI: `{rsi:.1f}` ({zone})\n'
        '• BB superior: `{bb_hi:.4f}`\n'
        '• BB inferior: `{bb_lo:.4f}`\n\n'
        '*Entrada MARKET {side} por RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'Sobreventa (<30)',
    'rsi_zone_overbought':         'Sobrecompra (>70)',
    'rsi_zone_neutral':            'Neutral (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ TP/SL inválido para LONG.\n'
        'Precio actual: {current:.2f}\n'
        'Esperado: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ TP/SL inválido para SHORT.\n'
        'Precio actual: {current:.2f}\n'
        'Esperado: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 No tienes posición abierta en {symbol}',
    'tpsl_set_success':            '✅ TP={tp:.2f} y SL={sl:.2f} establecidos para {symbol}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 Idioma',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'Modo de stop: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ Orden Limit de {symbol} ejecutada @ {price}',
    'limit_order_cancelled':       '⚠️ Orden Limit de {symbol} (ID: {order_id}) cancelada.',
    'fixed_sl_tp':                 '✅ {symbol}: SL en {sl}, TP en {tp}',
    'tp_part':                     ', TP fijado en {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL en {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL en {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP inicializados en {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL movido a break-even en {entry}',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP actualizados a {sl}/{tp}',

    'position_closed_error': (
        '⚠️ Posición {symbol} cerrada pero fallo al registrar: {error}\n'
        'Contacta con soporte.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'Porcentaje fijo',

    # System notices
    'db_quarantine_notice':        '⚠️ Registros pausados temporalmente. Modo silencioso por 1 hora.',

    # Fallback
    'fallback':                    '❓ Usa los botones del menú.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 Estás bloqueado.',
    'invite_only': '🔒 Acceso solo por invitación. Espera la aprobación del administrador.',
    'need_terms': '⚠️ Acepta primero los términos: /terms',
    'please_confirm': 'Por favor confirma:',
    'terms_ok': '✅ ¡Gracias! Términos aceptados.',
    'terms_declined': '❌ Rechazaste los términos. Acceso cerrado. Puedes volver con /terms.',
    'usage_approve': 'Uso: /approve <user_id>',
    'usage_ban': 'Uso: /ban <user_id>',
    'not_allowed': 'No permitido',
    'bad_payload': 'Datos inválidos',
    'unknown_action': 'Acción desconocida',

    'title': 'Nuevo usuario',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Nombre: {name}\n'
        '• Usuario: {uname}\n'
        '• Idioma: {lang}\n'
        '• Permitido: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve': '✅ Aprobar',
    'btn_ban': '⛔️ Banear',
    'admin_notify_fail': 'No se pudo notificar al admin: {e}',
    'moderation_approved': '✅ Aprobado: {target}',
    'moderation_banned': '⛔️ Baneado: {target}',
    'approved_user_dm': '✅ Acceso aprobado. Pulsa /start.',
    'banned_user_dm': '🚫 Estás bloqueado.',

    'users_not_found': '😕 No se encontraron usuarios.',
    'users_page_info': '📄 Página {page}/{pages} — total: {total}',
    'user_card_html': (
        '<b>👤 Usuario</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• Nombre: {full_name}\n'
        '• Usuario: {uname}\n'
        '• Idioma: <code>{lang}</code>\n'
        '• Permitido: {allowed}\n'
        '• Bloqueado: {banned}\n'
        '• Términos: {terms}\n'
        '• % por operación: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 Lista negra',
    'btn_delete_user': '🗑 Eliminar de la BD',
    'btn_prev': '⬅️ Atrás',
    'btn_next': '➡️ Siguiente',
    'nav_caption': '🧭 Navegación:',
    'bad_page': 'Página inválida.',
    'admin_user_delete_fail': '❌ Error al eliminar {target}: {error}',
    'admin_user_deleted': '🗑 Usuario {target} eliminado de la BD.',
    'user_access_approved': '✅ Acceso aprobado. Pulsa /start.',

    'admin_pause_all': '⏸️ Pausar para todos',
    'admin_resume_all': '▶️ Reanudar',
    'admin_close_longs': '🔒 Cerrar todos los LONG',
    'admin_close_shorts': '🔓 Cerrar todos los SHORT',
    'admin_cancel_limits': '❌ Eliminar órdenes limit',
    'admin_users': '👥 Usuarios',
    'admin_pause_notice': '⏸️ Trading y avisos pausados para todos.',
    'admin_resume_notice': '▶️ Trading y avisos reanudados para todos.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ Cerrado total {count} {type}.',
    'admin_canceled_limits_total': '✅ Canceladas {count} órdenes limit.',

    'terms_btn_accept': '✅ Aceptar',
    'terms_btn_decline': '❌ Rechazar',

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
    'api_test_success':            '¡Conexión exitosa!',
    'api_test_no_keys':            'Claves API no configuradas',
    'api_test_set_keys':           'Por favor, configure primero API Key y Secret.',
    'api_test_failed':             'Conexión fallida',
    'api_test_error':              'Error',
    'api_test_check_keys':         'Por favor, verifique sus credenciales API.',
    'api_test_status':             'Estado',
    'api_test_connected':          'Conectado',
    'balance_wallet':              'Saldo de billetera',
    'balance_equity':              'Capital',
    'balance_available':           'Disponible',
    'api_missing_notice':          '⚠️ No ha configurado las claves API del exchange. Por favor, añada su clave API y secreto en la configuración (botones 🔑 API y 🔒 Secret), de lo contrario el bot no podrá operar por usted.',
    'elcaro_ai_info':              '🤖 *Trading impulsado por IA*',

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
    'strat_mode_both':             '🔄 Ambos',
    'strat_mode_changed':          '✅ Modo de trading {strategy}: {mode}',

    # Enliko (Heatmap)

    # Fibonacci (Fibonacci Extension)

    # Strategy Settings
    'button_strategy_settings':      '⚙️ Config. estrategias',
    'strategy_settings_header':      '⚙️ *Configuración de estrategias*',
    'strategy_param_header':         '⚙️ *Configuración de {name}*',
    'using_global':                  'Config. global',
    'global_default':                'Global',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Enliko',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ Configuración DCA',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA Paso 1 %',
    'dca_leg2':                      '📉 DCA Paso 2 %',
    'param_percent':                 '📊 Entrada %',
    'param_sl':                      '🔻 Stop-Loss %',
    'param_tp':                      '🔺 Take-Profit %',
    'param_reset':                   '🔄 Restablecer a global',
    'btn_close':                     '❌ Cerrar',
    'prompt_entry_pct':              'Ingrese % de entrada (riesgo por trade):',
    'prompt_sl_pct':                 'Ingrese % Stop-Loss:',
    'prompt_tp_pct':                 'Ingrese % Take-Profit:',
    'prompt_atr_periods':            'Ingrese períodos ATR (ej: 7):',
    'prompt_atr_mult':               'Ingrese multiplicador ATR para SL dinámico (ej: 1.0):',
    'prompt_atr_trigger':            'Ingrese % de activación ATR (ej: 2.0):',
    'prompt_dca_leg1':               'Ingrese % DCA Paso 1 (ej: 10):',
    'prompt_dca_leg2':               'Ingrese % DCA Paso 2 (ej: 25):',
    'settings_reset':                'Config. restablecida a global',
    'strat_setting_saved':           '✅ {name} {param} establecido en {value}',
    'dca_setting_saved':             '✅ DCA {leg} establecido en {value}%',
    'invalid_number':                '❌ Número inválido. Ingrese un valor entre 0 y 100.',
    'dca_10pct':                     'DCA −{pct}%: refuerzo {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: refuerzo {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: Paso1=-{dca1}%, Paso2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 Períodos ATR',
    'param_atr_mult':                '📉 Multiplicador ATR (paso SL)',
    'param_atr_trigger':             '🎯 Activación ATR %',

    # Break-Even settings UI
    'be_settings_header':            '🔒 *Configuración Break-Even*',
    'be_settings_desc':              '_Mover SL al precio de entrada cuando el beneficio alcance el % de activación_',
    'be_enabled_label':              '🔒 Break-Even',
    'be_trigger_label':              '🎯 Activación BE %',
    'prompt_be_trigger':             'Ingrese el % de activación Break-Even (ej: 1.0):',
    'prompt_long_be_trigger':        '📈 LONG Activación BE %\n\nIngrese % de ganancia para mover SL a entrada:',
    'prompt_short_be_trigger':       '📉 SHORT Activación BE %\n\nIngrese % de ganancia para mover SL a entrada:',
    'param_be_trigger':              '🎯 Activación BE %',
    'be_moved_to_entry':             '🔒 {symbol}: SL movido a break-even @ {entry}',
    'be_status_enabled':             '✅ BE: {trigger}%',
    'be_status_disabled':            '❌ BE: Desactivado',

    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ TP Parcial',
    'partial_tp_status_enabled':     '✅ TP Parcial activado',
    'partial_tp_status_disabled':    '❌ TP Parcial desactivado',
    'partial_tp_step1_menu':         '✂️ *TP Parcial - Paso 1*\n\nCerrar {close}% de la posición al +{trigger}% de ganancia\n\n_Seleccione parámetro:_',
    'partial_tp_step2_menu':         '✂️ *TP Parcial - Paso 2*\n\nCerrar {close}% de la posición al +{trigger}% de ganancia\n\n_Seleccione parámetro:_',
    'trigger_pct':                   'Activación',
    'close_pct':                     'Cerrar',
    'prompt_long_ptp_1_trigger':     '📈 LONG Paso 1: % Activación\n\nIngrese % de ganancia para cerrar primera parte:',
    'prompt_long_ptp_1_close':       '📈 LONG Paso 1: % Cerrar\n\nIngrese % de posición a cerrar:',
    'prompt_long_ptp_2_trigger':     '📈 LONG Paso 2: % Activación\n\nIngrese % de ganancia para cerrar segunda parte:',
    'prompt_long_ptp_2_close':       '📈 LONG Paso 2: % Cerrar\n\nIngrese % de posición a cerrar:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT Paso 1: % Activación\n\nIngrese % de ganancia para cerrar primera parte:',
    'prompt_short_ptp_1_close':      '📉 SHORT Paso 1: % Cerrar\n\nIngrese % de posición a cerrar:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT Paso 2: % Activación\n\nIngrese % de ganancia para cerrar segunda parte:',
    'prompt_short_ptp_2_close':      '📉 SHORT Paso 2: % Cerrar\n\nIngrese % de posición a cerrar:',
    'partial_tp_executed':           '✂️ {symbol}: Cerrado {close}% al +{trigger}% de ganancia',

    # Hardcoded strings fix
    'terms_unavailable':             'Términos de servicio no disponibles. Contacte al administrador.',
    'terms_confirm_prompt':          'Por favor confirme:',
    'your_id':                       'Su ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'Error: {msg}',
    'error_fetch_balance':           '❌ Error al obtener el saldo: {error}',
    'error_fetch_orders':            '❌ Error al obtener las órdenes: {error}',
    'error_occurred':                '❌ Error: {error}',

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
    'stats_strategy_settings':       'Ajustes de estrategia',
    'settings_entry_pct':            'Entrada',
    'settings_leverage':             'Apalancamiento',
    'settings_trading_mode':         'Modo',
    'settings_direction':            'Dirección',
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
    'param_leverage': '⚡ Apalancamiento',
    'prompt_leverage': 'Introduce el apalancamiento (1-100):',
    'auto_default': 'Auto',

    # Enliko AI
    'elcaro_ai_desc': '_Todos los parámetros se parsean automáticamente de las señales AI:_',

    # Scalper entries

    # Scryptomera feature
    

    # Limit Ladder
    'limit_ladder': '📉 Escalera de límites',
    'limit_ladder_header': '📉 *Configuración de escalera de límites*',
    'limit_ladder_settings': '⚙️ Config. escalera',
    'ladder_count': 'Cantidad de órdenes',
    'ladder_info': 'Órdenes límite por debajo de la entrada para DCA. Cada orden tiene un % de distancia de entrada y un % del depósito.',
    'prompt_ladder_pct_entry': '📉 Ingrese % debajo del precio de entrada para orden {idx}:',
    'prompt_ladder_pct_deposit': '💰 Ingrese % del depósito para orden {idx}:',
    'ladder_order_saved': '✅ Orden {idx} guardada: -{pct_entry}% @ {pct_deposit}% depósito',
    'ladder_orders_placed': '📉 {count} órdenes límite colocadas para {symbol}',
    
    # Spot Trading Mode
    'spot_trading_mode': 'Modo de trading',
    'spot_btn_mode': 'Modo',
    
    # Stats PnL
    'stats_realized_pnl': 'Realizado',
    'stats_unrealized_pnl': 'No realizado',
    'stats_combined_pnl': 'Combinado',
    'stats_spot': '💹 Spot',
    'stats_spot_title': 'Estadísticas Spot DCA',
    'stats_spot_config': 'Configuración',
    'stats_spot_holdings': 'Posiciones',
    'stats_spot_summary': 'Resumen',
    'stats_spot_current_value': 'Valor actual',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    # License status messages - BLACK RHETORIC: Loss Aversion + FOMO
    'no_license': '''🚨 *ACCESO DENEGADO*

Mientras dudas, *847 traders* ya están ganando.

💸 Cada minuto sin Enliko = oportunidades perdidas
⏰ Los mercados no esperan. Tú tampoco deberías.

👉 /subscribe — _Desbloquea tu ventaja injusta AHORA_''',
    'no_license_trading': '''🚨 *TRADING BLOQUEADO*

Tus competidores están ganando AHORA MISMO con Enliko.

❌ Trading manual = errores emocionales
✅ Enliko = precisión IA fría

_Deja de mirar. Empieza a ganar._

👉 /subscribe — *Únete a 847+ traders inteligentes*''',
    'license_required': '''🔒 *FUNCIÓN PREMIUM*

Esto requiere suscripción {required} — _usada por el top 3% de traders_.

🎯 El éxito deja pistas. Sigue a los ganadores.

👉 /subscribe — *Actualiza ahora*''',
    'trial_demo_only': '''⚠️ *El modo demo es para aprender, no para ganar.*

Beneficios reales requieren acceso real.

🎁 Has probado el poder. Ahora *poséelo*.

👉 /subscribe — *Desbloquea Trading Real*''',
    'basic_strategy_limit': '''⚠️ *Basic = Resultados Básicos*

Estás limitado a: {strategies}

Los pros usan *TODAS* las estrategias. Por eso son pros.

👉 /subscribe — *Hazte Premium. Hazte Pro.*''',
    
    # Subscribe menu - BLACK RHETORIC: Urgency + Authority + Exclusivity
    'subscribe_menu_header': '''💎 *DESBLOQUEA TU IMPERIO DE TRADING*

⚡ 847+ traders ya ganando
🏆 97% satisfacción de usuarios
📈 $2.4M+ generados este mes''',
    'subscribe_menu_info': '''_"La mejor inversión que he hecho"_ — Usuario Premium

Elige tu nivel de dominación:''',
    'btn_premium': '💎 PREMIUM — Poder Total ⚡',
    'btn_basic': '🥈 Basic — Inicio',
    'btn_trial': '🎁 Prueba Gratis — 7 Días',
    'btn_enter_promo': '🎟 Código Secreto',
    'btn_my_subscription': '📋 Mi Estado',
    
    # Premium plan - BLACK RHETORIC: Authority + Scarcity + Social Proof
    'premium_title': '''💎 *PREMIUM — DOMINACIÓN TOTAL*

_"Este bot literalmente imprime dinero"_ — @CryptoKing''',
    'premium_desc': '''🔥 *TODO DESBLOQUEADO:*

✅ Las 5 Estrategias IA — _$100K+ trades ejecutados diariamente_
✅ Real + Demo — _Sin limitaciones_
✅ Soporte VIP Prioritario — _Respuesta < 1 hora_
✅ SL/TP Dinámico ATR — _Entradas optimizadas por IA_
✅ Escalera Límite DCA — _Escalado institucional_
✅ Actualizaciones de por vida — _Siempre adelante del mercado_

⚡ *ESTADÍSTICAS PREMIUM:*
• ROI Promedio: +47%/mes
• Tasa de Éxito: 78%
• Usuarios Activos: 312

_La pregunta no es "¿Puedo pagar Premium?"
La pregunta es "¿Puedo permitirme NO tenerlo?"_''',
    'premium_1m': '💎 1 Mes — {price} ELC ⚡',
    'premium_3m': '💎 3 Meses — {price} ELC 🔥 AHORRA 10%',
    'premium_6m': '💎 6 Meses — {price} ELC 🎯 AHORRA 20%',
    'premium_12m': '💎 12 Meses — {price} ELC 🏆 MEJOR VALOR -30%',
    
    # Basic plan - BLACK RHETORIC: Stepping stone narrative
    'basic_title': '''🥈 *BASIC — INICIO INTELIGENTE*

_Perfecto para probar las aguas_''',
    'basic_desc': '''✅ Acceso Demo Completo — _Aprendizaje sin riesgo_
✅ Cuenta Real: OI, RSI+BB, Scryptomera, Scalper
⛔ Enliko, Fibonacci, Spot — _Exclusivo Premium_
✅ Soporte Estándar
✅ SL/TP Dinámico ATR

💡 *87% de usuarios Basic actualizan a Premium en 2 semanas*
_Ellos ven los resultados. Tú también lo harás._''',
    'basic_1m': '🥈 1 Mes — {price} ELC',
    
    # Trial plan - BLACK RHETORIC: Zero risk + Taste of power
    'trial_title': '''🎁 *PRUEBA GRATIS — CERO RIESGO*

_Ver para creer_''',
    'trial_desc': '''✅ Acceso Demo Completo — *Las 5 Estrategias IA*
✅ 7 Días de Poder Puro
✅ Sin Tarjeta de Crédito
⚡ Activación con Un Clic

⚠️ *ADVERTENCIA:* Después de experimentar Enliko IA,
el trading manual parecerá... primitivo.

_91% de usuarios de prueba se convierten en clientes._
_Ahora entenderás por qué._''',
    'trial_activate': '🎁 ACTIVAR PRUEBA GRATIS ⚡',
    'trial_already_used': '''⚠️ Prueba ya usada.

Has visto el poder. Ahora *poséelo*.

👉 Elige un plan y únete a la élite.''',
    'trial_activated': '''🎉 *¡BIENVENIDO AL FUTURO DEL TRADING!*

⏰ Tienes 7 días para experimentar:
• Entradas potenciadas por IA
• Gestión de riesgo automática
• Monitoreo de mercado 24/7

_Tu viaje hacia la libertad financiera comienza AHORA._

💡 Pro tip: ¡Activa todas las estrategias para máximos resultados!''',
    
    # Payment
    'payment_select_method': '💳 *Seleccionar Método de Pago*',
    'btn_pay_elc': '◈ Enliko Coin (ELC)',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' Pago via ELC',
    'payment_elc_desc': 'Se te cobrará {amount} ELC por {plan} ({period}).',
    'payment_ton_title': '💎 Pago via TON',
    'payment_ton_desc': '''Envía exactamente *{amount} TON* a:

`{wallet}`

Después del pago, haz clic en el botón de abajo para verificar.''',
    'btn_verify_ton': '✅ Pagué — Verificar',
    'payment_processing': '⏳ Procesando pago...',
    'payment_success': '🎉 ¡Pago exitoso!\n\n{plan} activado hasta {expires}.',
    'payment_failed': '❌ Pago fallido: {error}',
    
    # My subscription
    'my_subscription_header': '📋 *Mi Suscripción*',
    'my_subscription_active': '''📋 *Plan Actual:* {plan}
⏰ *Expira:* {expires}
📅 *Días Restantes:* {days}''',
    'my_subscription_none': '❌ Sin suscripción activa.\n\nUsa /subscribe para comprar un plan.',
    'my_subscription_history': '📜 *Historial de Pagos:*',
    'subscription_expiring_soon': '⚠️ ¡Tu suscripción {plan} expira en {days} días!\n\nRenueva ahora: /subscribe',
    
    # Promo codes
    'promo_enter': '🎟 Ingresa tu código promo:',
    'promo_success': '🎉 ¡Código promo aplicado!\n\n{plan} activado por {days} días.',
    'promo_invalid': '❌ Código promo inválido.',
    'promo_expired': '❌ Este código promo ha expirado.',
    'promo_used': '❌ Este código promo ya ha sido usado.',
    'promo_already_used': '❌ Ya has usado este código promo.',
    
    # Admin license management
    'admin_license_menu': '🔑 *Gestión de Licencias*',
    'admin_btn_grant_license': '🎁 Otorgar Licencia',
    'admin_btn_view_licenses': '📋 Ver Licencias',
    'admin_btn_create_promo': '🎟 Crear Promo',
    'admin_btn_view_promos': '📋 Ver Promos',
    'admin_btn_expiring_soon': '⚠️ Expiran Pronto',
    'admin_grant_select_type': 'Selecciona tipo de licencia:',
    'admin_grant_select_period': 'Selecciona período:',
    'admin_grant_enter_user': 'Ingresa ID de usuario:',
    'admin_license_granted': '✅ {plan} otorgado al usuario {uid} por {days} días.',
    'admin_license_extended': '✅ Licencia extendida {days} días para usuario {uid}.',
    'admin_license_revoked': '✅ Licencia revocada para usuario {uid}.',
    'admin_promo_created': '✅ Código promo creado: {code}\nTipo: {type}\nDías: {days}\nUsos máx: {max}',

    # =====================================================
    # ADMIN USER MANAGEMENT
    # =====================================================
    'admin_users_management': '👥 Usuarios',
    'admin_licenses': '🔑 Licencias',
    'admin_search_user': '🔍 Buscar Usuario',
    'admin_users_menu': '👥 *Gestión de Usuarios*\n\nSelecciona filtro o búsqueda:',
    'admin_all_users': '👥 Todos los Usuarios',
    'admin_active_users': '✅ Activos',
    'admin_banned_users': '🚫 Baneados',
    'admin_no_license': '❌ Sin Licencia',
    'admin_no_users_found': 'No se encontraron usuarios.',
    'admin_enter_user_id': '🔍 Ingresa ID de usuario para buscar:',
    'admin_user_found': '✅ ¡Usuario {uid} encontrado!',
    'admin_user_not_found': '❌ Usuario {uid} no encontrado.',
    'admin_invalid_user_id': '❌ ID de usuario inválido. Ingresa un número.',
    'admin_view_card': '👤 Ver Tarjeta',
    
    # User card
    'admin_user_card': '''👤 *Tarjeta de Usuario*

📋 *ID:* `{uid}`
{status_emoji} *Estado:* {status}
📝 *Términos:* {terms}

{license_emoji} *Licencia:* {license_type}
📅 *Expira:* {license_expires}
⏳ *Días Restantes:* {days_left}

🌐 *Idioma:* {lang}
📊 *Modo Trading:* {trading_mode}
💰 *% por Trade:* {percent}%
🪙 *Monedas:* {coins}

🔌 *Claves API:*
  Demo: {demo_api}
  Real: {real_api}

📈 *Estrategias:* {strategies}

📊 *Estadísticas:*
  Posiciones: {positions}
  Trades: {trades}
  PnL: {pnl}
  Winrate: {winrate}%

💳 *Pagos:*
  Total: {payments_count}
  ELC: {total_elc}

📅 *Primera vez:* {first_seen}
🕐 *Última vez:* {last_seen}
''',
    
    # User actions
    'admin_btn_grant_lic': '🎁 Otorgar',
    'admin_btn_extend': '⏳ Extender',
    'admin_btn_revoke': '🚫 Revocar',
    'admin_btn_ban': '🚫 Banear',
    'admin_btn_unban': '✅ Desbanear',
    'admin_btn_approve': '✅ Aprobar',
    'admin_btn_message': '✉️ Mensaje',
    'admin_btn_delete': '🗑 Eliminar',
    
    'admin_user_banned': '¡Usuario baneado!',
    'admin_user_unbanned': '¡Usuario desbaneado!',
    'admin_user_approved': '¡Usuario aprobado!',
    'admin_confirm_delete': '⚠️ *Confirmar eliminación*\n\n¡El usuario {uid} será eliminado permanentemente!',
    'admin_confirm_yes': '✅ Sí, Eliminar',
    'admin_confirm_no': '❌ Cancelar',
    
    'admin_select_license_type': 'Selecciona tipo de licencia para usuario {uid}:',
    'admin_select_period': 'Selecciona período:',
    'admin_select_extend_days': 'Selecciona días a extender para usuario {uid}:',
    'admin_license_granted_short': '¡Licencia otorgada!',
    'admin_license_extended_short': '¡Extendido {days} días!',
    'admin_license_revoked_short': '¡Licencia revocada!',
    
    'admin_enter_message': '✉️ Ingresa mensaje para enviar al usuario {uid}:',
    'admin_message_sent': '✅ ¡Mensaje enviado al usuario {uid}!',
    'admin_message_failed': '❌ Error al enviar mensaje: {error}',

    # Auto-synced missing keys
    'admin_all_payments': '📜 Todos los pagos',
    'admin_demo_stats': '🎮 Stats demo',
    'admin_enter_user_for_report': '👤 Ingrese ID de usuario para informe detallado:',
    'admin_generating_report': '📊 Generando informe para usuario {uid}...',
    'admin_global_stats': '📊 Stats globales',
    'admin_no_payments_found': 'No se encontraron pagos.',
    'admin_payments': '💳 Pagos',
    'admin_payments_menu': '💳 *Gestión de pagos*',
    'admin_real_stats': '💰 Stats reales',
    'admin_reports': '📊 Informes',
    'admin_reports_menu': '''📊 *Informes y análisis*

Seleccione tipo de informe:''',
    'admin_strategy_breakdown': '🎯 Por estrategia',
    'admin_top_traders': '🏆 Mejores traders',
    'admin_user_report': '👤 Informe de usuario',
    'admin_view_report': '📊 Ver informe',
    'admin_view_user': '👤 Ficha de usuario',
    'all_positions_closed': 'Todas las posiciones cerradas',
    'btn_check_again': '🔄 Verificar de nuevo',
    'current': 'Actual',
    'entry': 'Entrada',
    'max_positions_reached': '⚠️ Máximo de posiciones alcanzado. Las nuevas señales se omitirán hasta que se cierre una posición.',
    'payment_session_expired': '❌ Sesión de pago expirada. Por favor, comience de nuevo.',
    'payment_ton_not_configured': '❌ Los pagos TON no están configurados.',
    'payment_verifying': '⏳ Verificando pago...',
    'position': 'Posición',
    'size': 'Tamaño',
    'stats_fibonacci': '📐 Fibonacci',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "Trading en HyperLiquid",
    "hl_reset_settings": "🔄 Restablecer a configuración de Bybit",

    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ Cancelado.',
    'entry_pct_range_error': '❌ El % de entrada debe estar entre 0.1 y 100.',
    'hl_no_history': '📭 Sin historial de operaciones en HyperLiquid.',
    'hl_no_orders': '📭 Sin órdenes abiertas en HyperLiquid.',
    'hl_no_positions': '📭 Sin posiciones abiertas en HyperLiquid.',
    'hl_setup_cancelled': '❌ Configuración de HyperLiquid cancelada.',
    'invalid_amount': '❌ Número inválido. Ingrese una cantidad válida.',
    'leverage_range_error': '❌ El apalancamiento debe estar entre 1 y 100.',
    'max_amount_error': '❌ Cantidad máxima es 100,000 USDT',
    'min_amount_error': '❌ Cantidad mínima es 1 USDT',
    'sl_tp_range_error': '❌ SL/TP % debe estar entre 0.1 y 500.',

    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 Activar DCA',
    'btn_ignore': '🔇 Ignorar',
    'dca_already_enabled': '✅ El DCA ya está activado!\n\n📊 <b>{symbol}</b>\nEl bot comprará automáticamente en caída:\n• -10% → añadir\n• -25% → añadir\n\nEsto ayuda a promediar el precio de entrada.',
    'dca_enable_error': '❌ Error: {error}',
    'dca_enabled_for_symbol': '✅ DCA activado!\n\n📊 <b>{symbol}</b>\nEl bot comprará automáticamente en caída:\n• -10% → añadir (promediado)\n• -25% → añadir (promediado)\n\n⚠️ DCA requiere saldo suficiente para órdenes adicionales.',
    'deep_loss_alert': '⚠️ <b>¡Posición en pérdida profunda!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 Pérdida: <code>{loss_pct:.2f}%</code>\n💰 Entrada: <code>{entry}</code>\n📍 Actual: <code>{mark}</code>\n\n❌ El stop-loss no puede establecerse por encima del precio de entrada.\n\n<b>¿Qué hacer?</b>\n• <b>Cerrar</b> - bloquear la pérdida\n• <b>DCA</b> - promediar la posición\n• <b>Ignorar</b> - dejar como está',
    'deep_loss_close_error': '❌ Error al cerrar la posición: {error}',
    'deep_loss_closed': '✅ Posición {symbol} cerrada.\n\nPérdida bloqueada. A veces es mejor aceptar una pequeña pérdida que esperar un cambio de tendencia.',
    'deep_loss_ignored': '🔇 Entendido, posición {symbol} dejada sin cambios.\n\n⚠️ Recuerde: sin stop-loss, el riesgo de pérdidas es ilimitado.\nPuede cerrar la posición manualmente a través de /positions',
    'fibonacci_desc': '_Entrada, SL, TP - desde niveles Fibonacci en la señal._',
    'fibonacci_info': '📐 *Estrategia Fibonacci Extension*',
    'prompt_min_quality': 'Ingrese calidad mínima % (0-100):',

    # Hardcore trading phrase
    'hardcore_mode': '💀 *MODO HARDCORE*: Sin piedad, sin remordimientos. ¡Solo beneficio o muerte! 🔥',

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ Saldo ELC insuficiente.

Tu saldo: {balance} ELC
Requerido: {required} ELC

Recarga tu billetera para continuar.''',
    'wallet_address': '''📍 Dirección: `{address}`''',
    'wallet_balance': '''💰 *Tu Billetera ELC*

◈ Saldo: *{balance} ELC*
📈 En Staking: *{staked} ELC*
🎁 Recompensas Pendientes: *{rewards} ELC*

💵 Valor Total: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« Atrás''',
    'wallet_btn_deposit': '''📥 Depositar''',
    'wallet_btn_history': '''📋 Historial''',
    'wallet_btn_stake': '''📈 Staking''',
    'wallet_btn_unstake': '''📤 Retirar Staking''',
    'wallet_btn_withdraw': '''📤 Retirar''',
    'wallet_deposit_demo': '''🎁 Obtener 100 ELC (Demo)''',
    'wallet_deposit_desc': '''Envía tokens ELC a tu dirección de billetera:

`{address}`

💡 *Modo demo:* Haz clic abajo para tokens de prueba gratis.''',
    'wallet_deposit_success': '''✅ ¡{amount} ELC depositados con éxito!''',
    'wallet_deposit_title': '''📥 *Depositar ELC*''',
    'wallet_history_empty': '''Sin transacciones aún.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *Historial de Transacciones*''',
    'wallet_stake_desc': '''¡Haz staking de tus ELC para ganar *12% APY*!

💰 Disponible: {available} ELC
📈 Actualmente en Staking: {staked} ELC
🎁 Recompensas Pendientes: {rewards} ELC

Recompensas diarias • Unstaking instantáneo''',
    'wallet_stake_success': '''✅ ¡{amount} ELC en staking con éxito!''',
    'wallet_stake_title': '''📈 *Staking ELC*''',
    'wallet_title': '''◈ *Billetera ELC*''',
    'wallet_unstake_success': '''✅ ¡Retirados {amount} ELC + {rewards} ELC de recompensas!''',
    'wallet_withdraw_desc': '''Ingresa dirección de destino y monto:''',
    'wallet_withdraw_failed': '''❌ Retiro fallido: {error}''',
    'wallet_withdraw_success': '''✅ Retirados {amount} ELC a {address}''',
    'wallet_withdraw_title': '''📤 *Retirar ELC*''',

    'spot_freq_biweekly': '📅 Cada 2 semanas',
    'spot_trailing_enabled': '✅ Trailing TP activado: activación +{activation}%, trail {trail}%',
    'spot_trailing_disabled': '❌ Trailing TP desactivado',
    'spot_grid_started': '🔲 Grid bot iniciado para {coin}: {levels} niveles de ${low} a ${high}',
    'spot_grid_stopped': '⏹ Grid bot detenido para {coin}',
    'spot_limit_placed': '📝 Orden límite colocada: Comprar {amount} {coin} a ${price}',
    'spot_limit_cancelled': '❌ Orden límite cancelada para {coin}',
    'spot_freq_hourly': '⏰ Cada hora',

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
    'error_insufficient_balance': '💰 Fondos insuficientes en tu cuenta para abrir una posición. Recarga tu saldo o reduce el tamaño de la posición.',
    'error_order_too_small': '📉 Tamaño de orden demasiado pequeño (mínimo $5). Aumenta Entry% o recarga tu saldo.',
    'error_api_key_expired': '🔑 Clave API caducada o inválida. Actualiza tus claves API en la configuración.',
    'error_api_key_missing': '🔑 Claves API no configuradas. Añade claves Bybit en el menú 🔗 API Keys.',
    'error_rate_limit': '⏳ Demasiadas solicitudes. Espera un minuto e inténtalo de nuevo.',
    'error_position_not_found': '📊 Posición no encontrada o ya cerrada.',
    'error_leverage_error': '⚙️ Error al configurar el apalancamiento. Intenta configurarlo manualmente en el exchange.',
    'error_network_error': '🌐 Problema de red. Inténtalo más tarde.',
    'error_sl_tp_invalid': '⚠️ No se puede configurar SL/TP: precio demasiado cerca del actual. Se actualizará en el próximo ciclo.',
    'error_equity_zero': '💰 Tu saldo de cuenta es cero. Recarga tu cuenta Demo o Real para operar.',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 Terminal',
    'exchange_mode_activated_bybit': '🟠 *Modo Bybit activado*',
    'exchange_mode_activated_hl': '🔷 *Modo HyperLiquid activado*',
    'error_processing_request': '⚠️ Error procesando la solicitud',
    'unauthorized_admin': '❌ No autorizado. Este comando es solo para el administrador.',
    'error_loading_dashboard': '❌ Error cargando el panel de control.',
    'unauthorized': '❌ No autorizado.',
    'processing_blockchain': '⏳ Procesando transacción en blockchain...',
    'verifying_payment': '⏳ Verificando pago en la blockchain TON...',
    'no_wallet_configured': '❌ No hay billetera configurada.',
    'use_start_menu': 'Usa /start para volver al menú principal.',
}
