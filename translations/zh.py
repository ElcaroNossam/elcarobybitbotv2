# -*- coding: utf-8 -*-
TEXTS = {
    # 主菜单 - 专业交易终端
    'welcome':                     '''🔥 <b>Enliko Trading Terminal</b>

⚡ <b>&lt; 100ms</b> 执行速度
🛡️ <b>风险管理</b>内置
💎 <b>24/7</b> 自动交易

Bybit • HyperLiquid • 多策略''',
    'no_strategies':               '❌ 无活跃策略',
    'guide_caption':               '📚 <b>用户指南</b>\n\nAPI设置、策略、风险管理。',
    'privacy_caption':             '📜 <b>隐私政策</b>\n\n🔐 加密存储\n✅ 不共享数据',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 密钥',
    'button_api_settings':         '🔑 API',
    'button_balance':              '� 投资组合',
    'button_orders':               '📜 我的订单',
    'button_positions':            '🎯 持仓',
'button_history':              '📋 历史',
    'button_strategies':           '🤖 AI机器人',
    'button_api_keys':             '🔑 API密钥',
    'button_bybit':                '🟠 Bybit',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_switch_bybit':         '🔄 Bybit',
    'button_switch_hl':            '🔄 HyperLiquid',
    'button_subscribe':            '� PREMIUM',
    'button_licenses':             '🔑 许可证',
    'button_admin':                '👑 管理员',
    'button_percent':              '🎚 每笔交易百分比',
    'button_coins':                '💠 币组',
    'button_market':               '📈 市场',
    'button_manual_order':         '✋ 手动下单',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ 取消订单',
    'button_limit_only':           '🎯 仅限价',
    'button_toggle_oi':            '� OI追踪器',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_settings':             '⚙️ 设置',
    'button_indicators':           '💡 指标',
    'button_support':              '🆘 支持',
    'toggle_oi_status':            '🔀 {feature}：{status}',
    'toggle_rsi_bb_status':        '📊 {feature}：{status}',
    'config_trade_scryptomera':    '🔮 Scryptomera：{state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 TP/SL 模式已切换为：*{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              '固定百分比',

    # Limits
    'limit_positions_exceeded':    '🚫 超出持仓数量上限 ({max})',
    'limit_limit_orders_exceeded': '🚫 超出限价单数量上限 ({max})',

    # Languages
    'select_language':             '选择语言：',
    'language_set':                '语言已设置为：',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           '选择订单类型：',
    'limit_order_format': (
        "按如下格式输入限价单参数：\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "其中 SIDE = LONG 或 SHORT\n"
        "示例：`BTCUSDT LONG 20000 0.1`\n\n"
        "要取消请发送 ❌ 取消订单"
    ),
    'market_order_format': (
        "按如下格式输入市价单参数：\n"
        "`SYMBOL SIDE QTY`\n"
        "其中 SIDE = LONG 或 SHORT\n"
        "示例：`BTCUSDT SHORT 0.1`\n\n"
        "要取消请发送 ❌ 取消订单"
    ),
    'order_success':               '✅ 订单创建成功！',
    'order_create_error':          '❌ 创建订单失败：{msg}',
    'order_fail_leverage':         (
        "❌ 未创建订单：你的 Bybit 账户杠杆对该规模过高。\n"
        "请在 Bybit 设置中降低杠杆。"
    ),
    'order_parse_error':           '❌ 解析失败：{error}',
    'price_error_min':             '❌ 价格错误：必须 ≥{min}',
    'price_error_step':            '❌ 价格错误：必须是 {step} 的倍数',
    'qty_error_min':               '❌ 数量错误：必须 ≥{min}',
    'qty_error_step':              '❌ 数量错误：必须是 {step} 的倍数',

    # Loading…
    'loader':                      '⏳ 正在收集数据…',

    # Market command
    'market_status_heading':       '*市场状况：*',
    'market_dominance_header':    '市场占比排行',
    'market_total_header':        '总市值',
    'market_indices_header':      '市场指数',
    'usdt_dominance':              'USDT 主导率',
    'btc_dominance':               'BTC 主导率',
    'dominance_rising':            '↑ 上升',
    'dominance_falling':           '↓ 下降',
    'dominance_stable':            '↔️ 稳定',
    'dominance_unknown':           '❔ 无数据',
    'btc_price':                   'BTC 价格',
    'last_24h':                    '近 24 小时',
    'alt_signal_label':            '山寨币信号',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*最新资讯（CoinDesk）：*',

    # Execution price error
    'exec_price_not_found':        '未找到用于平仓的成交价',

    # /account
    'account_balance':             '💰 余额：`{balance:.2f}`',
    'account_realized_header':     '📈 *已实现盈亏：*',
    'account_realized_day':        '  • 今日 ：`{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7天  ：`{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *未实现盈亏：*',
    'account_unreal_total':        '  • 合计：`{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • 占 IM：`{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *你的设置：*',
    'config_percent':              '• 🎚 每笔％          ：`{percent}%`',
    'config_coins':                '• 💠 币种            ：`{coins}`',
    'config_limit_only':           '• 🎯 仅限价          ：{state}',
    'config_atr_mode':             '• 🏧 ATR 跟踪 SL     ：{atr}',
    'config_trade_oi':             '• 📊 依据 OI 交易    ：{oi}',
    'config_trade_rsi_bb':         '• 📈 依据 RSI+BB 交易：{rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%             ：`{tp}%`',
    'config_sl_pct':               '• 🛑 SL%             ：`{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 无未完成订单',
    'open_orders_header':          '*📒 未完成订单：*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • 方向：`{side}`\n"
        "   • 数量：`{qty}`\n"
        "   • 价格：`{price}`\n"
        "   • ID ：`{id}`"
    ),
    'open_orders_error':           '❌ 获取订单出错：{error}',

    # Manual coin selection
    'enter_coins':                 "输入以逗号分隔的交易对，例如：\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ 已选择币种：{coins}',

    # Positions
    'no_positions':                '🚫 无持仓',
    'positions_header':            '📊 当前持仓：',
    'position_item':               (
        "— 持仓 #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • 仓位大小      ：{size}\n"
        "  • 开仓价        ：{avg:.8f}\n"
        "  • 标记价格      ：{mark:.8f}\n"
        "  • 强平价        ：{liq}\n"
        "  • 初始保证金    ：{im:.2f}\n"
        "  • 维持保证金    ：{mm:.2f}\n"
        "  • 持仓余额      ：{pm:.2f}\n"
        "  • 止盈 (TP)     ：{tp}\n"
        "  • 止损 (SL)     ：{sl}\n"
        "  • 未实现盈亏    ：{pnl:+.2f} ({pct:+.2f}%)"
    ),
    'position_item_v2':            (
        "— #{idx}: {symbol} | {side} (x{leverage}) [{strategy}]\n"
        "  • 仓位大小      ：{size}\n"
        "  • 开仓价        ：{avg:.8f}\n"
        "  • 标记价格      ：{mark:.8f}\n"
        "  • 强平价        ：{liq}\n"
        "  • 初始保证金    ：{im:.2f}\n"
        "  • 维持保证金    ：{mm:.2f}\n"
        "  • 止盈 (TP)     ：{tp}\n"
        "  • 止损 (SL)     ：{sl}\n"
        "  {pnl_emoji} 未实现盈亏   ：{pnl:+.2f} ({pct:+.2f}%)"
    ),
    'pnl_by_strategy':             '📊 *按策略 PnL：*',
    'pnl_by_exchange':             '🏦 *按交易所 PnL：*',
    'positions_overall':           '未实现盈亏合计：{pnl:+.2f} ({pct:+.2f}%)',

    # Position management (inline)
    'open_positions_header':       '📊 *当前持仓*',
    'positions_count':             '个持仓',
    'positions_count_total':       '持仓总数',
    'total_unrealized_pnl':        '未实现盈亏合计',
    'total_pnl':                   '总盈亏',
    'btn_close_short':             '平仓',
    'btn_close_all':               '全部平仓',
    'btn_close_position':          '平仓',
    'btn_confirm_close':           '确认平仓',
    'btn_confirm_close_all':       '是，全部平仓',
    'btn_cancel':                  '❌ 取消',
    'btn_back':                    '🔙 返回',
    'confirm_close_position':      '平仓',
    'confirm_close_all':           '平掉所有持仓',
    'position_not_found':          '持仓未找到或已平仓',
    'position_already_closed':     '持仓已平仓',
    'position_closed_success':     '持仓已平仓',
    'position_close_error':        '平仓出错',
    'positions_closed':            '持仓已平仓',
    'errors':                      '错误',

    # % per trade
    'set_percent_prompt':          '输入每笔交易使用余额的百分比（例如 2.5）：',
    'percent_set_success':         '✅ 已设置每笔％：{pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 仅限价订单：{state}',
    'feature_limit_only':          '仅限价',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Enliko 指标*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. 交易混沌理论',
    'indicator_3':                 '3. 自适应趋势',
    'indicator_4':                 '4. 动态回归',

    # Support
    'support_prompt':              '✉️ 需要帮助？点击下方：',
    'support_button':              '联系支持',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 无持仓',
    'update_tpsl_prompt':          '输入 SYMBOL TP SL，例如：\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ 格式无效。使用：SYMBOL TP SL\n例：BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   '请输入 Bybit API Key：',
    'api_saved':                   '✅ API Key 已保存',
    'enter_secret':                '请输入 Bybit API Secret：',
    'secret_saved':                '✅ API Secret 已保存',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ 请输入 TP% 值',
    'tp_set_success':              '✅ 已设置 TP%：{pct}%',
    'enter_sl':                    '❌ 请输入 SL% 值',
    'sl_set_success':              '✅ 已设置 SL%：{pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit：需要 4 个参数 (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market：需要 3 个参数 (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE 必须是 LONG 或 SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ 未设置 API Key/Secret',
    'bybit_invalid_response':      '❌ Bybit 返回了无效响应',
    'bybit_error':                 '❌ Bybit 错误 {path}: {data}',

    # Auto notifications - BLACK RHETORIC: Excitement & Celebration
    'new_position': (
        '🚀🔥 <b>新持仓已开启！</b>\n'
        '• {symbol} @ {entry:.6f}\n'
        '• 大小: {size}\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>AI正在为您工作！ 🤖</i>'
    ),
    'sl_auto_set':                 '🛑 已自动设置 SL：{price:.6f}',
    'auto_close_position':         '⏱ 持仓 {symbol} (TF={tf}) 已开仓超过 {tf} 且亏损，已自动平仓。',
    'position_closed': (
        '🎉 <b>持仓已平仓！</b> {symbol}\n'
        '• 原因: <b>{reason}</b>\n'
        '• 策略: `{strategy}`\n'
        '• 开仓价: `{entry:.8f}`\n'
        '• 平仓价: `{exit:.8f}`\n'
        '{pnl_emoji} <b>PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`</b>\n'
        '📍 {exchange} • {market_type}'
    ),

    # Entries & errors - 统一格式（完整信息）
    'oi_limit_entry':              '📉 *OI 限价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI 限价错误：{msg}',
    'oi_market_entry':             '📉 *OI 市价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI 市价错误：{msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB 限价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB 市价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB 市价错误：{msg}',

    'oi_analysis':                 '📊 *OI {symbol} 分析* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera 限价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera 限价错误：{msg}',
    'bitk_market_entry':           '🔮 *Scryptomera 市价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera 市价错误：{msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>余额不足！</b>\n\n💰 您的{account_type}账户余额不足以开设此仓位。\n\n<b>解决方案：</b>\n• 充值余额\n• 减少仓位大小（每笔交易的%）\n• 降低杠杆\n• 关闭部分持仓',
    'insufficient_balance_error_extended': '❌ <b>余额不足！</b>\n\n📊 策略: <b>{strategy}</b>\n🪙 品种: <b>{symbol}</b> {side}\n\n💰 您的{account_type}账户余额不足。\n\n<b>解决方案:</b>\n• 充值余额\n• 减少仓位大小 (每笔交易的%)\n• 降低杠杆\n• 平掉部分持仓',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>杠杆过高！</b>\n\n⚙️ 您配置的杠杆超过了该品种允许的最大值。\n\n<b>最大允许:</b> {max_leverage}x\n\n<b>解决方案:</b> 前往策略设置并降低杠杆。',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>超出持仓限制！</b>\n\n📊 策略: <b>{strategy}</b>\n🪙 品种: <b>{symbol}</b>\n\n⚠️ 您的持仓将超过最大限制。\n\n<b>解决方案:</b>\n• 降低杠杆\n• 减少仓位大小\n• 平掉部分持仓',
    

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper 限价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper 限价错误：{msg}',
    'scalper_market_entry':        '⚡ *Scalper 市价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper 市价错误：{msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko 限价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Enliko 限价错误：{msg}',
    'elcaro_market_entry':         '🔥 *Enliko 市价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Enliko 市价错误：{msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci 限价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci 限价错误：{msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci 市价入场*\n• {symbol} {side}\n• 价格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci 市价错误：{msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 管理面板：',
    'admin_pause':                 '⏸️ 已为所有用户暂停交易与通知。',
    'admin_resume':                '▶️ 已为所有用户恢复交易与通知。',
    'admin_closed':                '✅ 共关闭 {count} 个 {type}。',
    'admin_canceled_limits':       '✅ 已取消 {count} 个限价单。',

    # Coin groups
    'select_coin_group':           '选择币组：',
    'group_all':                   'ALL',
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ 币组已设置：{group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *RSI+BB 分析*\n'
        '• 价格：`{price:.6f}`\n'
        '• RSI ：`{rsi:.1f}`（{zone}）\n'
        '• 布林带上轨：`{bb_hi:.4f}`\n'
        '• 布林带下轨：`{bb_lo:.4f}`\n\n'
        '*依据 RSI+BB 进行 {side} 市价入场*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           '超卖 (<30)',
    'rsi_zone_overbought':         '超买 (>70)',
    'rsi_zone_neutral':            '中性 (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ LONG 的 TP/SL 无效。\n'
        '当前价格：{current:.2f}\n'
        '应满足：SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ SHORT 的 TP/SL 无效。\n'
        '当前价格：{current:.2f}\n'
        '应满足：TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 你在 {symbol} 没有持仓',
    'tpsl_set_success':            '✅ 已为 {symbol} 设置 TP={tp:.2f}、SL={sl:.2f}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 语言',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            '止损模式：*{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ {symbol} 的限价单已成交 @ {price}',
    'limit_order_cancelled':       '⚠️ 已取消 {symbol} 的限价单 (ID: {order_id})。',
    'fixed_sl_tp':                 '✅ {symbol}：SL 设为 {sl}，TP 设为 {tp}',
    'tp_part':                     '，TP 设为 {tp_price}',
    'sl_tp_set':                   '✅ {symbol}：SL 设为 {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}：仅设置 SL 为 {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}：已初始化 SL/TP 为 {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}：SL 移至保本价 {entry}',
    'sl_tp_updated':               '✏️ {symbol}：SL/TP 更新为 {sl}/{tp}',

    'position_closed_error': (
        '⚠️ {symbol} 已平仓但记录失败：{error}\n'
        '请联系支持。'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  '固定百分比',

    # System notices
    'db_quarantine_notice':        '⚠️ 日志暂时暂停。静默模式 1 小时。',

    # Fallback
    'fallback':                    '❓ 请使用菜单按钮。',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 你已被封禁。',
    'invite_only': '🔒 仅限邀请访问。请等待管理员审批。',
    'need_terms': '⚠️ 请先接受条款：/terms',
    'please_confirm': '请确认：',
    'terms_ok': '✅ 已接受条款。',
    'terms_declined': '❌ 你拒绝了条款。访问已关闭。可通过 /terms 返回。',
    'usage_approve': '用法：/approve <user_id>',
    'usage_ban': '用法：/ban <user_id>',
    'not_allowed': '不允许',
    'bad_payload': '无效数据',
    'unknown_action': '未知操作',

    'title': '新用户',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID：<code>{uid}</code>\n'
        '• 姓名：{name}\n'
        '• 用户名：{uname}\n'
        '• 语言：{lang}\n'
        '• 允许：{allowed}  Ban：{banned}\n'
    ),
    'btn_approve': '✅ 通过',
    'btn_ban': '⛔️ 封禁',
    'admin_notify_fail': '通知管理员失败：{e}',
    'moderation_approved': '✅ 已通过：{target}',
    'moderation_banned': '⛔️ 已封禁：{target}',
    'approved_user_dm': '✅ 访问已通过。请输入 /start。',
    'banned_user_dm': '🚫 你已被封禁。',

    'users_not_found': '😕 未找到用户。',
    'users_page_info': '📄 第 {page}/{pages} 页 — 共：{total}',
    'user_card_html': (
        '<b>👤 用户</b>\n'
        '• ID：<code>{uid}</code>\n'
        '• 姓名：{full_name}\n'
        '• 用户名：{uname}\n'
        '• 语言：<code>{lang}</code>\n'
        '• 允许：{allowed}\n'
        '• 封禁：{banned}\n'
        '• 条款：{terms}\n'
        '• 每笔交易百分比：<code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 黑名单',
    'btn_delete_user': '🗑 从数据库删除',
    'btn_prev': '⬅️ 上一页',
    'btn_next': '➡️ 下一页',
    'nav_caption': '🧭 导航：',
    'bad_page': '无效页面。',
    'admin_user_delete_fail': '❌ 删除 {target} 失败：{error}',
    'admin_user_deleted': '🗑 已从数据库删除用户 {target}。',
    'user_access_approved': '✅ 访问已通过。请输入 /start。',

    'admin_pause_all': '⏸️ 全体暂停',
    'admin_resume_all': '▶️ 全体恢复',
    'admin_close_longs': '🔒 关闭全部 LONG',
    'admin_close_shorts': '🔓 关闭全部 SHORT',
    'admin_cancel_limits': '❌ 删除限价单',
    'admin_users': '👥 用户',
    'admin_pause_notice': '⏸️ 所有人的交易与通知已暂停。',
    'admin_resume_notice': '▶️ 所有人的交易与通知已恢复。',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ 共关闭 {count} 个 {type}。',
    'admin_canceled_limits_total': '✅ 取消 {count} 个限价单。',

    'terms_btn_accept': '✅ 接受',
    'terms_btn_decline': '❌ 拒绝',

    'emoji_long': '🟢',
    'emoji_short': '🔴',
    'emoji_neutral': '⚪️',

    # Scalper Strategy
    'button_scalper':                '🎯 Scalper',
    'button_elcaro':                 '🔥 Enliko',
    'button_fibonacci':                '📐 Fibonacci',
    'config_trade_scalper':          '🎯 Scalper: {state}',
    'config_trade_elcaro':           '🔥 Enliko: {state}',
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
    'api_test_success':            '连接成功！',
    'api_test_no_keys':            'API密钥未设置',
    'api_test_set_keys':           '请先设置API Key和Secret。',
    'api_test_failed':             '连接失败',
    'api_test_error':              '错误',
    'api_test_check_keys':         '请检查您的API凭证。',
    'api_test_status':             '状态',
    'api_test_connected':          '已连接',
    'balance_wallet':              '钱包余额',
    'balance_equity':              '资产',
    'balance_available':           '可用',
    'api_missing_notice':          '⚠️ 您尚未配置交易所API密钥。请在设置中添加您的API密钥和密钥（🔑 API和🔒 Secret按钮），否则机器人无法为您交易。',
    'elcaro_ai_info':              '🤖 *AI驱动交易*',

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
    'strat_mode_global':           '🌐 全局',
    'strat_mode_demo':             '🧪 模拟',
    'strat_mode_real':             '💰 实盘',
    'strat_mode_both':             '🔄 两者',
    'strat_mode_changed':          '✅ {strategy} 交易模式: {mode}',

    # Enliko (Heatmap)

    # Fibonacci (Fibonacci Extension)

    # Strategy Settings
    'button_strategy_settings':      '⚙️ 策略设置',
    'strategy_settings_header':      '⚙️ *策略设置*',
    'strategy_param_header':         '⚙️ *{name} 设置*',
    'using_global':                  '使用全局设置',
    'global_default':                '全局',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Enliko',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ DCA设置',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA 第1阶段 %',
    'dca_leg2':                      '📉 DCA 第2阶段 %',
    'param_percent':                 '📊 入场 %',
    'param_sl':                      '🔻 止损 %',
    'param_tp':                      '🔺 止盈 %',
    'param_reset':                   '🔄 重置为全局',
    'btn_close':                     '❌ 关闭',
    'prompt_entry_pct':              '输入入场 %（每笔交易风险）:',
    'prompt_sl_pct':                 '输入止损 %:',
    'prompt_tp_pct':                 '输入止盈 %:',
    'prompt_atr_periods':            '输入 ATR 周期（例如: 7）:',
    'prompt_atr_mult':               '输入追踪止损的 ATR 乘数（例如: 1.0）:',
    'prompt_atr_trigger':            '输入 ATR 触发 %（例如: 2.0）:',
    'prompt_dca_leg1':               '输入 DCA 第1阶段 %（例如: 10）:',
    'prompt_dca_leg2':               '输入 DCA 第2阶段 %（例如: 25）:',
    'settings_reset':                '设置已重置为全局',
    'strat_setting_saved':           '✅ {name} {param} 设置为 {value}',
    'dca_setting_saved':             '✅ DCA {leg} 设置为 {value}%',
    'invalid_number':                '❌ 无效数字。请输入 0 到 100 之间的值。',
    'dca_10pct':                     'DCA −{pct}%: 补仓 {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: 补仓 {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: 阶段1=-{dca1}%, 阶段2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 ATR 周期',
    'param_atr_mult':                '📉 ATR 乘数（SL步幅）',
    'param_atr_trigger':             '🎯 ATR 触发 %',

    # Break-Even settings UI
    'be_settings_header':            '🔒 *保本设置*',
    'be_settings_desc':              '_当利润达到触发%时将止损移至入场价_',
    'be_enabled_label':              '🔒 保本',
    'be_trigger_label':              '🎯 保本触发 %',
    'prompt_be_trigger':             '输入保本触发%（例如：1.0）:',
    'prompt_long_be_trigger':        '📈 LONG 保本触发%\n\n输入将止损移至入场价的利润%:',
    'prompt_short_be_trigger':       '📉 SHORT 保本触发%\n\n输入将止损移至入场价的利润%:',
    'param_be_trigger':              '🎯 保本触发 %',
    'be_moved_to_entry':             '🔒 {symbol}: 止损已移至保本价 @ {entry}',
    'be_status_enabled':             '✅ 保本: {trigger}%',
    'be_status_disabled':            '❌ 保本: 关闭',

    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ 部分止盈',
    'partial_tp_status_enabled':     '✅ 部分止盈已启用',
    'partial_tp_status_disabled':    '❌ 部分止盈已禁用',
    'partial_tp_step1_menu':         '✂️ *部分止盈 - 步骤1*\n\n在+{trigger}%利润时平仓{close}%仓位\n\n_选择参数:_',
    'partial_tp_step2_menu':         '✂️ *部分止盈 - 步骤2*\n\n在+{trigger}%利润时平仓{close}%仓位\n\n_选择参数:_',
    'trigger_pct':                   '触发',
    'close_pct':                     '平仓',
    'prompt_long_ptp_1_trigger':     '📈 LONG 步骤1: 触发%\n\n输入平仓第一部分的利润%:',
    'prompt_long_ptp_1_close':       '📈 LONG 步骤1: 平仓%\n\n输入要平仓的仓位%:',
    'prompt_long_ptp_2_trigger':     '📈 LONG 步骤2: 触发%\n\n输入平仓第二部分的利润%:',
    'prompt_long_ptp_2_close':       '📈 LONG 步骤2: 平仓%\n\n输入要平仓的仓位%:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT 步骤1: 触发%\n\n输入平仓第一部分的利润%:',
    'prompt_short_ptp_1_close':      '📉 SHORT 步骤1: 平仓%\n\n输入要平仓的仓位%:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT 步骤2: 触发%\n\n输入平仓第二部分的利润%:',
    'prompt_short_ptp_2_close':      '📉 SHORT 步骤2: 平仓%\n\n输入要平仓的仓位%:',
    'partial_tp_executed':           '✂️ {symbol}: 在+{trigger}%利润时平仓{close}%',

    # Hardcoded strings fix
    'terms_unavailable':             '服务条款不可用。请联系管理员。',
    'terms_confirm_prompt':          '请确认:',
    'your_id':                       '您的ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 '错误: {msg}',
    'error_fetch_balance':           '❌ 获取余额错误: {error}',
    'error_fetch_orders':            '❌ 获取订单错误: {error}',
    'error_occurred':                '❌ 错误: {error}',

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
    'stats_strategy_settings':       '策略设置',
    'settings_entry_pct':            '入场',
    'settings_leverage':             '杠杆',
    'settings_trading_mode':         '模式',
    'settings_direction':            '方向',
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
    'param_leverage': '⚡ 杠杆',
    'prompt_leverage': '输入杠杆 (1-100)：',
    'auto_default': '自动',

    # Enliko AI
    'elcaro_ai_desc': '_所有参数均今AI信号自动解析：_',

    # Scalper entries

    # Scryptomera feature
    

    # Limit Ladder
    'limit_ladder': '📉 限价梯子',
    'limit_ladder_header': '📉 *限价梯子设置*',
    'limit_ladder_settings': '⚙️ 梯子设置',
    'ladder_count': '订单数量',
    'ladder_info': 'DCA入场以下的限价单。每个订单有从入场价格的%和保证金的%。',
    'prompt_ladder_pct_entry': '📉 输入订单 {idx} 低于入场价的%:',
    'prompt_ladder_pct_deposit': '💰 输入订单 {idx} 的保证金%:',
    'ladder_order_saved': '✅ 订单 {idx} 已保存: -{pct_entry}% @ {pct_deposit}% 保证金',
    'ladder_orders_placed': '📉 已为 {symbol} 下达 {count} 个限价单',
    
    # Spot Trading Mode
    'spot_trading_mode': '交易模式',
    'spot_btn_mode': '模式',
    
    # Stats PnL
    'stats_realized_pnl': '已实现',
    'stats_unrealized_pnl': '未实现',
    'stats_combined_pnl': '合计',
    'stats_spot': '💹 现货',
    'stats_spot_title': '现货DCA统计',
    'stats_spot_config': '配置',
    'stats_spot_holdings': '持仓',
    'stats_spot_summary': '摘要',
    'stats_spot_current_value': '当前价值',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    'no_license': (
        '🚫 <b>访问被拒绝</b>\n\n'
        '📊 847名交易者正在获利，而您被排除在外。\n'
        '⏰ 没有Enliko的每一分钟 = 错过的机会\n\n'
        '👑 立即解锁您的不公平优势: /subscribe'
    ),
    'no_license_trading': (
        '🚫 <b>交易已锁定</b>\n\n'
        '在您等待的同时，847名交易者正在用Enliko获利。\n\n'
        '⚡ 立即开始盈利: /subscribe'
    ),
    'license_required': '⚠️ 此功能需要{required}订阅。\n\n使用 /subscribe 升级。',
    'trial_demo_only': '⚠️ 试用许可证仅允许模拟交易。\n\n升级到Premium或Basic进行实盘交易: /subscribe',
    'basic_strategy_limit': '⚠️ Basic许可证在实盘账户仅允许: {strategies}\n\n升级到Premium解锁所有策略: /subscribe',
    
    'subscribe_menu_header': '� <b>LYXEN VIP访问</b>',
    'subscribe_menu_info': '🔓 解锁精英交易者策略:',
    'btn_premium': '💎 高级版',
    'btn_basic': '🥈 基础版', 
    'btn_trial': '🎁 试用（免费）',
    'btn_enter_promo': '🎟 优惠码',
    'btn_my_subscription': '📋 我的订阅',
    
    'premium_title': '� <b>精英PREMIUM访问</b>',
    'premium_desc': '''✅ 完全访问所有功能
✅ 所有5种策略: OI, RSI+BB, Scryptomera, Scalper, Enliko
✅ 实盘 + 模拟交易
✅ 优先支持
✅ 基于ATR的动态SL/TP
✅ 限价梯子DCA
✅ 所有未来更新''',
    'premium_1m': '💎 1个月 — {price} ELC',
    'premium_3m': '💎 3个月 — {price} ELC (-10%)',
    'premium_6m': '💎 6个月 — {price} ELC (-20%)',
    'premium_12m': '💎 12个月 — {price} ELC (-30%)',
    
    'basic_title': '🥈 *基础计划*',
    'basic_desc': '''✅ 完全访问模拟账户
✅ 实盘账户: OI, RSI+BB, Scryptomera, Scalper
❌ Enliko, Fibonacci, Spot — 仅限Premium
✅ 标准支持
✅ 基于ATR的动态SL/TP''',
    'basic_1m': '🥈 1个月 — {price} ELC',
    
    'trial_title': '🚀 <b>今天就开始您的优势</b>',
    'trial_desc': '''✅ 完全访问模拟账户
✅ 模拟所有5种策略
❌ 实盘交易不可用
⏰ 期限: 7天
🎁 仅限一次''',
    'trial_activate': '🎁 激活免费试用',
    'trial_already_used': '⚠️ 您已使用过免费试用。',
    'trial_activated': '🎉 试用已激活！您有7天完整模拟访问权限。',
    
    'payment_select_method': '💳 *选择支付方式*',
    'btn_pay_elc': '◈ Enliko Coin (ELC)',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' 通过ELC支付',
    'payment_elc_desc': '将收取{amount} ELC用于{plan}（{period}）。',
    'payment_ton_title': '💎 通过TON支付',
    'payment_ton_desc': '''发送正好*{amount} TON*到:

`{wallet}`

支付后，点击下方按钮验证。''',
    'btn_verify_ton': '✅ 已支付 — 验证',
    'payment_processing': '⏳ 处理支付中...',
    'payment_success': '🎉 支付成功！\n\n{plan}已激活至{expires}。',
    'payment_failed': '❌ 支付失败: {error}',
    
    'my_subscription_header': '📋 *我的订阅*',
    'my_subscription_active': '''📋 *当前计划:* {plan}
⏰ *到期时间:* {expires}
📅 *剩余天数:* {days}''',
    'my_subscription_none': '❌ 没有有效订阅。\n\n使用 /subscribe 购买计划。',
    'my_subscription_history': '📜 *支付历史:*',
    'subscription_expiring_soon': '⚠️ 您的{plan}订阅将在{days}天后到期！\n\n立即续订: /subscribe',
    
    'promo_enter': '🎟 输入您的优惠码:',
    'promo_success': '🎉 优惠码已应用！\n\n{plan}已激活{days}天。',
    'promo_invalid': '❌ 无效的优惠码。',
    'promo_expired': '❌ 此优惠码已过期。',
    'promo_used': '❌ 此优惠码已被使用。',
    'promo_already_used': '❌ 您已使用过此优惠码。',
    
    'admin_license_menu': '🔑 *许可证管理*',
    'admin_btn_grant_license': '🎁 授予许可证',
    'admin_btn_view_licenses': '📋 查看许可证',
    'admin_btn_create_promo': '🎟 创建优惠码',
    'admin_btn_view_promos': '📋 查看优惠码',
    'admin_btn_expiring_soon': '⚠️ 即将到期',
    'admin_grant_select_type': '选择许可证类型:',
    'admin_grant_select_period': '选择期限:',
    'admin_grant_enter_user': '输入用户ID:',
    'admin_license_granted': '✅ 已向用户{uid}授予{plan} {days}天。',
    'admin_license_extended': '✅ 用户{uid}的许可证已延长{days}天。',
    'admin_license_revoked': '✅ 用户{uid}的许可证已撤销。',
    'admin_promo_created': '✅ 优惠码已创建: {code}\n类型: {type}\n天数: {days}\n最大使用次数: {max}',

    'admin_users_management': '👥 用户',
    'admin_licenses': '🔑 许可证',
    'admin_search_user': '🔍 查找用户',
    'admin_users_menu': '👥 *用户管理*\n\n选择筛选或搜索:',
    'admin_all_users': '👥 所有用户',
    'admin_active_users': '✅ 活跃',
    'admin_banned_users': '🚫 已封禁',
    'admin_no_license': '❌ 无许可证',
    'admin_no_users_found': '未找到用户。',
    'admin_enter_user_id': '🔍 输入要搜索的用户ID:',
    'admin_user_found': '✅ 找到用户{uid}！',
    'admin_user_not_found': '❌ 未找到用户{uid}。',
    'admin_invalid_user_id': '❌ 无效的用户ID。请输入数字。',
    'admin_view_card': '👤 查看卡片',
    
    'admin_user_card': '''👤 *用户卡片*

📋 *ID:* `{uid}`
{status_emoji} *状态:* {status}
📝 *条款:* {terms}

{license_emoji} *许可证:* {license_type}
📅 *到期时间:* {license_expires}
⏳ *剩余天数:* {days_left}

🌐 *语言:* {lang}
📊 *交易模式:* {trading_mode}
💰 *每笔交易%:* {percent}%
🪙 *币种:* {coins}

🔌 *API密钥:*
  模拟: {demo_api}
  实盘: {real_api}

📈 *策略:* {strategies}

📊 *统计:*
  持仓: {positions}
  交易: {trades}
  盈亏: {pnl}
  胜率: {winrate}%

💳 *支付:*
  总计: {payments_count}
  ELC: {total_elc}

📅 *首次访问:* {first_seen}
🕐 *最后访问:* {last_seen}
''',
    
    'admin_btn_grant_lic': '🎁 授予',
    'admin_btn_extend': '⏳ 延长',
    'admin_btn_revoke': '🚫 撤销',
    'admin_btn_ban': '🚫 封禁',
    'admin_btn_unban': '✅ 解封',
    'admin_btn_approve': '✅ 批准',
    'admin_btn_message': '✉️ 消息',
    'admin_btn_delete': '🗑 删除',
    
    'admin_user_banned': '用户已封禁！',
    'admin_user_unbanned': '用户已解封！',
    'admin_user_approved': '用户已批准！',
    'admin_confirm_delete': '⚠️ *确认删除*\n\n用户{uid}将被永久删除！',
    'admin_confirm_yes': '✅ 是，删除',
    'admin_confirm_no': '❌ 取消',
    
    'admin_select_license_type': '选择用户{uid}的许可证类型:',
    'admin_select_period': '选择期限:',
    'admin_select_extend_days': '选择为用户{uid}延长的天数:',
    'admin_license_granted_short': '许可证已授予！',
    'admin_license_extended_short': '已延长{days}天！',
    'admin_license_revoked_short': '许可证已撤销！',
    
    'admin_enter_message': '✉️ 输入要发送给用户{uid}的消息:',
    'admin_message_sent': '✅ 消息已发送给用户{uid}！',
    'admin_message_failed': '❌ 发送消息失败: {error}',

    # Auto-synced missing keys
    'admin_all_payments': '📜 所有支付',
    'admin_demo_stats': '🎮 演示统计',
    'admin_enter_user_for_report': '👤 输入用户ID获取详细报告:',
    'admin_generating_report': '📊 正在生成用户 {uid} 的报告...',
    'admin_global_stats': '📊 全局统计',
    'admin_no_payments_found': '未找到支付记录。',
    'admin_payments': '💳 支付',
    'admin_payments_menu': '💳 *支付管理*',
    'admin_real_stats': '💰 实盘统计',
    'admin_reports': '📊 报告',
    'admin_reports_menu': '''📊 *报告与分析*

选择报告类型:''',
    'admin_strategy_breakdown': '🎯 按策略',
    'admin_top_traders': '🏆 顶级交易员',
    'admin_user_report': '👤 用户报告',
    'admin_view_report': '📊 查看报告',
    'admin_view_user': '👤 用户卡片',
    'all_positions_closed': '所有持仓已平仓',
    'btn_check_again': '🔄 重新检查',
    'current': '当前',
    'entry': '入场',
    'max_positions_reached': '⚠️ 已达到最大持仓数。新信号将被跳过，直到平仓。',
    'payment_session_expired': '❌ 支付会话已过期。请重新开始。',
    'payment_ton_not_configured': '❌ TON支付未配置。',
    'payment_verifying': '⏳ 验证支付中...',
    'position': '持仓',
    'size': '大小',
    'stats_fibonacci': '📐 斐波那契',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "HyperLiquid交易",
    "hl_reset_settings": "🔄 重置为Bybit设置",

    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ 已取消。',
    'entry_pct_range_error': '❌ 入场百分比必须在0.1到100之间。',
    'hl_no_history': '📭 HyperLiquid上没有交易历史。',
    'hl_no_orders': '📭 HyperLiquid上没有未完成的订单。',
    'hl_no_positions': '📭 HyperLiquid上没有未平仓的头寸。',
    'hl_setup_cancelled': '❌ HyperLiquid设置已取消。',
    'invalid_amount': '❌ 无效数字。请输入有效金额。',
    'leverage_range_error': '❌ 杠杆必须在1到100之间。',
    'max_amount_error': '❌ 最大金额为100,000 USDT',
    'min_amount_error': '❌ 最小金额为1 USDT',
    'sl_tp_range_error': '❌ SL/TP百分比必须在0.1到500之间。',

    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 启用DCA平均',
    'btn_ignore': '🔇 忽略',
    'dca_already_enabled': '✅ DCA平均已启用！\n\n📊 <b>{symbol}</b>\n机器人将在回撤时自动加仓:\n• -10% → 加仓\n• -25% → 加仓\n\n这有助于平均入场价格。',
    'dca_enable_error': '❌ 错误: {error}',
    'dca_enabled_for_symbol': '✅ DCA平均已启用！\n\n📊 <b>{symbol}</b>\n机器人将在回撤时自动加仓:\n• -10% → 加仓(平均)\n• -25% → 加仓(平均)\n\n⚠️ DCA需要足够的余额来进行额外订单。',
    'deep_loss_alert': '⚠️ <b>仓位深度亏损！</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 亏损: <code>{loss_pct:.2f}%</code>\n💰 入场: <code>{entry}</code>\n📍 当前: <code>{mark}</code>\n\n❌ 止损无法设置在入场价格之上。\n\n<b>怎么办？</b>\n• <b>平仓</b> - 锁定亏损\n• <b>DCA</b> - 平均仓位\n• <b>忽略</b> - 保持原样',
    'deep_loss_close_error': '❌ 平仓错误: {error}',
    'deep_loss_closed': '✅ 仓位 {symbol} 已平仓。\n\n亏损已锁定。有时候接受小亏损比期待反转更好。',
    'deep_loss_ignored': '🔇 明白了，仓位 {symbol} 保持不变。\n\n⚠️ 记住：没有止损，亏损风险是无限的。\n您可以通过 /positions 手动平仓',
    'fibonacci_desc': '_入场、止损、止盈 - 来自信号中的斐波那契水平_',
    'fibonacci_info': '📐 *斐波那契扩展策略*',
    'prompt_min_quality': '输入最低质量 % (0-100):',

    # Hardcore trading phrase
    'hardcore_mode': '💀 *硬核模式*: 无怜悯，无遗憾。只有盈利或死亡！ 🔥',

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ ELC余额不足。

您的余额: {balance} ELC
需要: {required} ELC

请充值钱包后继续。''',
    'wallet_address': '''📍 地址: `{address}`''',
    'wallet_balance': '''💰 *您的ELC钱包*

◈ 余额: *{balance} ELC*
📈 质押中: *{staked} ELC*
🎁 待领取奖励: *{rewards} ELC*

💵 总价值: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« 返回''',
    'wallet_btn_deposit': '''📥 充值''',
    'wallet_btn_history': '''📋 记录''',
    'wallet_btn_stake': '''📈 质押''',
    'wallet_btn_unstake': '''📤 取消质押''',
    'wallet_btn_withdraw': '''📤 提现''',
    'wallet_deposit_demo': '''🎁 获取100 ELC (演示)''',
    'wallet_deposit_desc': '''将ELC代币发送到您的钱包地址:

`{address}`

💡 *演示模式:* 点击下方获取免费测试代币。''',
    'wallet_deposit_success': '''✅ 成功充值 {amount} ELC！''',
    'wallet_deposit_title': '''📥 *充值ELC*''',
    'wallet_history_empty': '''暂无交易记录。''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *交易记录*''',
    'wallet_stake_desc': '''质押您的ELC代币赚取*12%年化收益*！

💰 可用: {available} ELC
📈 当前质押: {staked} ELC
🎁 待领取奖励: {rewards} ELC

每日奖励 • 即时取消质押''',
    'wallet_stake_success': '''✅ 成功质押 {amount} ELC！''',
    'wallet_stake_title': '''📈 *质押ELC*''',
    'wallet_title': '''◈ *ELC钱包*''',
    'wallet_unstake_success': '''✅ 已取消质押 {amount} ELC + {rewards} ELC奖励！''',
    'wallet_withdraw_desc': '''输入目标地址和金额:''',
    'wallet_withdraw_failed': '''❌ 提现失败: {error}''',
    'wallet_withdraw_success': '''✅ 已向 {address} 提现 {amount} ELC''',
    'wallet_withdraw_title': '''📤 *提现ELC*''',

    'spot_freq_biweekly': '📅 每两周',
    'spot_trailing_enabled': '✅ 追踪止盈已启用：+{activation}%激活，追踪{trail}%',
    'spot_trailing_disabled': '❌ 追踪止盈已禁用',
    'spot_grid_started': '🔲 {coin}网格机器人已启动：{levels}个级别，从${low}到${high}',
    'spot_grid_stopped': '⏹ {coin}网格机器人已停止',
    'spot_limit_placed': '📝 限价单已下：以${price}买入{amount} {coin}',
    'spot_limit_cancelled': '❌ {coin}限价单已取消',
    'spot_freq_hourly': '⏰ 每小时',

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
    'error_insufficient_balance': '💰 账户余额不足，无法开仓。请充值余额或减少仓位大小。',
    'error_order_too_small': '📉 订单金额太小（最低$5）。请增加Entry%或充值余额。',
    'error_api_key_expired': '🔑 API密钥已过期或无效。请在设置中更新您的API密钥。',
    'error_api_key_missing': '🔑 API密钥未配置。请在🔗 API Keys菜单中添加Bybit密钥。',
    'error_rate_limit': '⏳ 请求过多。请等待一分钟后重试。',
    'error_position_not_found': '📊 仓位未找到或已平仓。',
    'error_leverage_error': '⚙️ 杠杆设置错误。请尝试在交易所手动设置杠杆。',
    'error_network_error': '🌐 网络问题。请稍后重试。',
    'error_sl_tp_invalid': '⚠️ 无法设置止损/止盈：价格太接近当前价格。将在下一周期更新。',
    'error_equity_zero': '💰 您的账户余额为零。请充值Demo或Real账户以进行交易。',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 终端',
    'exchange_mode_activated_bybit': '🟠 *Bybit模式已激活*',
    'exchange_mode_activated_hl': '🔷 *HyperLiquid模式已激活*',
    'error_processing_request': '⚠️ 处理请求时出错',
    'unauthorized_admin': '❌ 未授权。此命令仅限管理员使用。',
    'error_loading_dashboard': '❌ 加载仪表板失败。',
    'unauthorized': '❌ 未授权。',
    'processing_blockchain': '⏳ 正在处理区块链交易...',
    'verifying_payment': '⏳ 正在TON区块链上验证付款...',
    'no_wallet_configured': '❌ 未配置钱包。',
    'use_start_menu': '使用 /start 返回主菜单。',
}
