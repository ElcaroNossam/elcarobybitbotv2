# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu
    'welcome':                     '👋 你好！请选择操作：',
    'guide_caption':               '📚 交易机器人用户指南\n\n请阅读此指南，了解如何配置策略并有效使用机器人。',
    'privacy_caption':             '📜 隐私政策和使用条款\n\n请仔细阅读本文档。',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 密钥',
    'button_api_settings':         '🔑 API',
    'button_balance':              '💰 USDT 余额',
    'button_orders':               '📜 我的订单',
    'button_positions':            '📊 持仓',
    'button_percent':              '🎚 每笔交易百分比',
    'button_coins':                '💠 币组',
    'button_market':               '📈 市场',
    'button_manual_order':         '✋ 手动下单',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ 取消订单',
    'button_limit_only':           '🎯 仅限价',
    'button_toggle_oi':            '🔀 OI',
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
    'lang_zh':                     '中文',

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
    'account_balance':             '💰 USDT 余额：`{balance:.2f}`',
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
    'positions_overall':           '未实现盈亏合计：{pnl:+.2f} ({pct:+.2f}%)',

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
    'indicators_header':           '📈 *Elcaro 指标*',
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

    # Auto notifications
    'new_position':                '🚀 新持仓 {symbol} @ {entry:.6f}，大小={size}',
    'sl_auto_set':                 '🛑 已自动设置 SL：{price:.6f}',
    'auto_close_position':         '⏱ 持仓 {symbol} (TF={tf}) 已开仓超过 {tf} 且亏损，已自动平仓。',
    'position_closed': (
        '🔔 持仓 {symbol} 因 *{reason}* 已平仓：\n'
        '• Strategy: `{strategy}`\n'
        '• 开仓价：`{entry:.8f}`\n'
        '• 平仓价：`{exit:.8f}`\n'
        '• PnL  ：`{pnl:+.2f} USDT ({pct:+.2f}%)`'
    ),

    # Entries & errors
    'oi_limit_entry':              '🟡 OI 限价入场 {symbol} @ {price:.6f}',
    'oi_limit_error':              '❌ 限价入场出错：{msg}',
    'oi_market_entry':             '🚀 OI 市价入场 {symbol} @ {price:.6f}',
    'oi_market_error':             '❌ 市价入场出错：{msg}',

    'rsi_bb_limit_entry':          '🟡 RSI+BB 限价入场 {symbol} @ {price:.6f}',
    'rsi_bb_market_entry':         '✅ RSI+BB 市价入场 {symbol} @ {price:.6f}',
    'rsi_bb_market_error':         '❌ 市价错误：{msg}',

    'oi_analysis':                 '📊 *OI {symbol} 分析* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 Scryptomera 限价 {symbol} @ {price:.6f}',
    'bitk_limit_error':            '❌ Scryptomera 限价错误：{msg}',
    'bitk_market_entry':           '🔮 Scryptomera 市价 {symbol} @ {price:.6f}',
    'bitk_market_error':           '❌ Scryptomera 市价错误：{msg}',

    # Admin panel
    'admin_panel':                 '👑 管理面板：',
    'admin_pause':                 '⏸️ 已为所有用户暂停交易与通知。',
    'admin_resume':                '▶️ 已为所有用户恢复交易与通知。',
    'admin_closed':                '✅ 共关闭 {count} 个 {type}。',
    'admin_canceled_limits':       '✅ 已取消 {count} 个限价单。',

    # Coin groups
    'select_coin_group':           '选择币组：',
    'group_all':                   'ALL',
    'group_top100':                'TOP100',
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
    'strat_mode_global':           '🌐 全局',
    'strat_mode_demo':             '🧪 模拟',
    'strat_mode_real':             '💰 实盘',
    'strat_mode_both':             '🔄 两者',
    'strat_mode_changed':          '✅ {strategy} 交易模式: {mode}',

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
    'wyckoff_limit_entry':         '📐 Wyckoff limit-entry {symbol} @ {price:.6f}',
    'wyckoff_limit_error':         '❌ Wyckoff limit-entry error: {msg}',
    'wyckoff_market_entry':        '🚀 Wyckoff market {symbol} @ {price:.6f}',
    'wyckoff_market_error':        '❌ Wyckoff market error: {msg}',
    'wyckoff_market_ok':           '📐 Wyckoff: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'wyckoff_analysis':            'Wyckoff: {side} @ {price}',
    'feature_wyckoff':             'Wyckoff',

    'scalper_limit_entry':           'Scalper: 限价单 {symbol} @ {price}',
    'scalper_limit_error':           'Scalper 限价错误: {msg}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper 错误: {msg}',

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
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_wyckoff':                 '📐 Wyckoff',
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

    # Hardcoded strings fix
    'terms_unavailable':             '服务条款不可用。请联系管理员。',
    'terms_confirm_prompt':          '请确认:',
    'your_id':                       '您的ID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 '错误: {msg}',

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
    'elcaro_ai_note': '🤖 *AI替你完成工作！*',
    'elcaro_ai_params_header': '从每个信号中解析以下内容:',
    'elcaro_ai_params_list': '• SL% • TP% • ATR • 杠杆 • 时间框架',

    # Leverage settings
    'param_leverage': '⚡ 杠杆',
    'prompt_leverage': '输入杠杆 (1-100)：',
    'auto_default': '自动',

    # Elcaro AI
    'elcaro_ai_desc': '_所有参数均今AI信号自动解析：_',

    # Scalper entries
    'scalper_market_entry': '🚀 Scalper 市价 {symbol} @ {price:.6f}',
    'scalper_analysis': 'Scalper：{side} @ {price}',

    # Scryptomera feature
    'feature_scryptomera': 'Scryptomera',

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
    
    'no_license': '⚠️ 您需要有效订阅才能使用此功能。\n\n使用 /subscribe 购买许可证。',
    'no_license_trading': '⚠️ 您需要有效订阅才能交易。\n\n使用 /subscribe 购买许可证。',
    'license_required': '⚠️ 此功能需要{required}订阅。\n\n使用 /subscribe 升级。',
    'trial_demo_only': '⚠️ 试用许可证仅允许模拟交易。\n\n升级到Premium或Basic进行实盘交易: /subscribe',
    'basic_strategy_limit': '⚠️ Basic许可证在实盘账户仅允许: {strategies}\n\n升级到Premium解锁所有策略: /subscribe',
    
    'subscribe_menu_header': '💎 *订阅计划*',
    'subscribe_menu_info': '选择计划解锁交易功能:',
    'btn_premium': '💎 高级版',
    'btn_basic': '🥈 基础版', 
    'btn_trial': '🎁 试用（免费）',
    'btn_enter_promo': '🎟 优惠码',
    'btn_my_subscription': '📋 我的订阅',
    
    'premium_title': '💎 *高级计划*',
    'premium_desc': '''✅ 完全访问所有功能
✅ 所有5种策略: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ 实盘 + 模拟交易
✅ 优先支持
✅ 基于ATR的动态SL/TP
✅ 限价梯子DCA
✅ 所有未来更新''',
    'premium_1m': '💎 1个月 — {price}⭐',
    'premium_3m': '💎 3个月 — {price}⭐ (-15%)',
    'premium_6m': '💎 6个月 — {price}⭐ (-25%)',
    'premium_12m': '💎 12个月 — {price}⭐ (-35%)',
    
    'basic_title': '🥈 *基础计划*',
    'basic_desc': '''✅ 完全访问模拟账户
✅ 实盘账户: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Wyckoff, Spot — 仅限Premium
✅ 标准支持
✅ 基于ATR的动态SL/TP''',
    'basic_1m': '🥈 1个月 — {price}⭐',
    
    'trial_title': '🎁 *试用计划（免费）*',
    'trial_desc': '''✅ 完全访问模拟账户
✅ 模拟所有5种策略
❌ 实盘交易不可用
⏰ 期限: 7天
🎁 仅限一次''',
    'trial_activate': '🎁 激活免费试用',
    'trial_already_used': '⚠️ 您已使用过免费试用。',
    'trial_activated': '🎉 试用已激活！您有7天完整模拟访问权限。',
    
    'payment_select_method': '💳 *选择支付方式*',
    'btn_pay_stars': '⭐ Telegram Stars',
    'btn_pay_ton': '💎 TON',
    'payment_stars_title': '⭐ 通过Telegram Stars支付',
    'payment_stars_desc': '将收取{amount}⭐用于{plan}（{period}）。',
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
  Stars: {total_stars}⭐

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
}
