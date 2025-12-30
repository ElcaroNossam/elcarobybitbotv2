# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu
    'welcome':                     '👋 أهلاً! اختر إجراءً:',
    'no_strategies':               '❌ لا شيء',
    'guide_caption':               '📚 دليل مستخدم بوت التداول\n\nاقرأ هذا الدليل لتتعلم كيفية تكوين الاستراتيجيات واستخدام البوت بفعالية.',
    'privacy_caption':             '📜 سياسة الخصوصية وشروط الاستخدام\n\nيرجى قراءة هذا المستند بعناية.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 السر',
    'button_api_settings':         '🔑 API',
    'button_balance':              '💰 رصيد USDT',
    'button_orders':               '📜 أوامري',
    'button_positions':            '📊 المراكز',
    'button_percent':              '🎚 ٪ لكل صفقة',
    'button_coins':                '💠 مجموعة العملات',
    'button_market':               '📈 السوق',
    'button_manual_order':         '✋ أمر يدوي',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ إلغاء الأمر',
    'button_limit_only':           '🎯 ليمت فقط',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_settings':             '⚙️ الإعدادات',
    'button_indicators':           '💡 المؤشرات',
    'button_support':              '🆘 الدعم',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 تم تغيير وضع TP/SL إلى: *{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              'نسبة ثابتة %',

    # Limits
    'limit_positions_exceeded':    '🚫 تم تجاوز حد المراكز المفتوحة ({max})',
    'limit_limit_orders_exceeded': '🚫 تم تجاوز حد أوامر الـ Limit ({max})',

    # Languages
    'select_language':             'اختر اللغة:',
    'language_set':                'تم ضبط اللغة:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'اختر نوع الأمر:',
    'limit_order_format': (
        "أدخل معلمات أمر Limit بالشكل:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "حيث SIDE = LONG أو SHORT\n"
        "مثال: `BTCUSDT LONG 20000 0.1`\n\n"
        "للإلغاء، أرسل ❌ إلغاء الأمر"
    ),
    'market_order_format': (
        "أدخل معلمات أمر Market بالشكل:\n"
        "`SYMBOL SIDE QTY`\n"
        "حيث SIDE = LONG أو SHORT\n"
        "مثال: `BTCUSDT SHORT 0.1`\n\n"
        "للإلغاء، أرسل ❌ إلغاء الأمر"
    ),
    'order_success':               '✅ تم إنشاء الأمر بنجاح!',
    'order_create_error':          '❌ فشل إنشاء الأمر: {msg}',
    'order_fail_leverage':         (
        "❌ لم يتم إنشاء الأمر: الرافعة في حساب Bybit لديك عالية لهذا الحجم.\n"
        "يرجى تقليل الرافعة من إعدادات Bybit."
    ),
    'order_parse_error':           '❌ فشل التحليل: {error}',
    'price_error_min':             '❌ خطأ في السعر: يجب أن يكون ≥{min}',
    'price_error_step':            '❌ خطأ في السعر: يجب أن يكون من مضاعفات {step}',
    'qty_error_min':               '❌ خطأ في الكمية: يجب أن تكون ≥{min}',
    'qty_error_step':              '❌ خطأ في الكمية: يجب أن تكون من مضاعفات {step}',

    # Loading…
    'loader':                      '⏳ جارٍ جمع البيانات…',

    # Market command
    'market_status_heading':       '*حالة السوق:*',
    'market_dominance_header':    'أفضل العملات حسب الهيمنة',
    'market_total_header':        'إجمالي القيمة السوقية',
    'market_indices_header':      'مؤشرات السوق',
    'usdt_dominance':              'هيمنة USDT',
    'btc_dominance':               'هيمنة BTC',
    'dominance_rising':            '↑ ارتفاع',
    'dominance_falling':           '↓ انخفاض',
    'dominance_stable':            '↔️ مستقر',
    'dominance_unknown':           '❔ لا توجد بيانات',
    'btc_price':                   'سعر BTC',
    'last_24h':                    'آخر 24 ساعة',
    'alt_signal_label':            'إشارة ألتكوين',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*آخر الأخبار (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'تعذر العثور على سعر التنفيذ للإغلاق',

    # /account
    'account_balance':             '💰 رصيد USDT: `{balance:.2f}`',
    'account_realized_header':     '📈 *الأرباح/الخسائر المحققة:*',
    'account_realized_day':        '  • اليوم : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 أيام: `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *الأرباح/الخسائر غير المحققة:*',
    'account_unreal_total':        '  • الإجمالي : `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • ٪ من IM: `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *إعداداتك:*',
    'config_percent':              '• 🎚 ٪ لكل صفقة     : `{percent}%`',
    'config_coins':                '• 💠 العملات        : `{coins}`',
    'config_limit_only':           '• 🎯 أوامر Limit    : {state}',
    'config_atr_mode':             '• 🏧 وقف متحرك ATR  : {atr}',
    'config_trade_oi':             '• 📊 تداول OI       : {oi}',
    'config_trade_rsi_bb':         '• 📈 تداول RSI+BB   : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%            : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%            : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 لا توجد أوامر مفتوحة',
    'open_orders_header':          '*📒 أوامرك المفتوحة:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • الاتجاه: `{side}`\n"
        "   • الكمية : `{qty}`\n"
        "   • السعر  : `{price}`\n"
        "   • المعرّف: `{id}`"
    ),
    'open_orders_error':           '❌ خطأ في جلب الأوامر: {error}',

    # Manual coin selection
    'enter_coins':                 "أدخل الرموز مفصولة بفواصل، مثال:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ تم اختيار العملات: {coins}',

    # Positions
    'no_positions':                '🚫 لا توجد مراكز مفتوحة',
    'positions_header':            '📊 مراكزك المفتوحة:',
    'position_item':               (
        "— المركز #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • الحجم          : {size}\n"
        "  • سعر الدخول     : {avg:.8f}\n"
        "  • سعر المؤشر     : {mark:.8f}\n"
        "  • التصفية        : {liq}\n"
        "  • الهامش الأولي  : {im:.2f}\n"
        "  • هامش الصيانة   : {mm:.2f}\n"
        "  • رصيد المركز    : {pm:.2f}\n"
        "  • أخذ الربح      : {tp}\n"
        "  • وقف الخسارة    : {sl}\n"
        "  • ربح/خسارة غير محقّق: {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'positions_overall':           'إجمالي الربح/الخسارة غير المحقق: {pnl:+.2f} ({pct:+.2f}%)',

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
    'set_percent_prompt':          'أدخل نسبة الرصيد لكل صفقة (مثال 2.5):',
    'percent_set_success':         '✅ تم ضبط النسبة: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 أوامر الـ Limit فقط: {state}',
    'feature_limit_only':          'Limit-Only',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *مؤشرات Elcaro*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. الاتجاه التكيفي',
    'indicator_4':                 '4. الانحدار الديناميكي',

    # Support
    'support_prompt':              '✉️ تحتاج مساعدة؟ اضغط بالأسفل:',
    'support_button':              'اتصل بالدعم',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 لا توجد مراكز مفتوحة',
    'update_tpsl_prompt':          'أدخل SYMBOL TP SL، مثال:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ تنسيق غير صالح. استعمل: SYMBOL TP SL\nمثال: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'أدخل مفتاح Bybit API:',
    'api_saved':                   '✅ تم حفظ مفتاح API',
    'enter_secret':                'أدخل سر Bybit API:',
    'secret_saved':                '✅ تم حفظ السر',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ أدخل قيمة TP%',
    'tp_set_success':              '✅ تم ضبط TP%: {pct}%',
    'enter_sl':                    '❌ أدخل قيمة SL%',
    'sl_set_success':              '✅ تم ضبط SL%: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: يتطلب 4 معاملات (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: يتطلب 3 معاملات (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE يجب أن تكون LONG أو SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ لم يتم تعيين مفتاح/سر API',
    'bybit_invalid_response':      '❌ استجابة غير صالحة من Bybit',
    'bybit_error':                 '❌ خطأ Bybit {path}: {data}',

    # Auto notifications
    'new_position': (
        '🚀 مركز جديد {symbol} @ {entry:.6f}، الحجم={size}\n'
        '📍 {exchange} • {market_type}'
    ),
    'sl_auto_set':                 '🛑 تم تعيين SL تلقائياً: {price:.6f}',
    'auto_close_position':         '⏱ المركز {symbol} (TF={tf}) مفتوح لأكثر من {tf} ويخسر، تم إغلاقه تلقائياً.',
    'position_closed': (
        '🔔 تم إغلاق مركز {symbol} بسبب *{reason}*:\n'
        '• Strategy: `{strategy}`\n'
        '• الدخول: `{entry:.8f}`\n'
        '• الخروج: `{exit:.8f}`\n'
        '• الربح/الخسارة: `{pnl:+.2f} USDT ({pct:+.2f}%)`'
    ),

    # Entries & errors - تنسيق موحد مع معلومات كاملة
    'oi_limit_entry':              '📉 *دخول OI Limit*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ خطأ OI Limit: {msg}',
    'oi_market_entry':             '📉 *دخول OI Market*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ خطأ OI Market: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *دخول RSI+BB Limit*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *دخول RSI+BB Market*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• الكمية: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ خطأ RSI+BB Market: {msg}',

    'oi_analysis':                 '📊 *تحليل OI لـ {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *دخول Scryptomera Limit*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ خطأ Scryptomera Limit: {msg}',
    'bitk_market_entry':           '🔮 *دخول Scryptomera Market*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ خطأ Scryptomera Market: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>رصيد غير كافٍ!</b>\n\n💰 لا توجد أموال كافية في حساب {account_type} الخاص بك لفتح هذا المركز.\n\n<b>الحلول:</b>\n• إعادة شحن الرصيد\n• تقليل حجم المركز (% لكل صفقة)\n• تخفيض الرافعة المالية\n• إغلاق بعض المراكز المفتوحة',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>الرافعة المالية عالية جداً!</b>\n\n⚙️ الرافعة المالية المُعدّة تتجاوز الحد الأقصى المسموح به لهذا الرمز.\n\n<b>الحد الأقصى المسموح:</b> {max_leverage}x\n\n<b>الحل:</b> انتقل إلى إعدادات الاستراتيجية وقم بتخفيض الرافعة المالية.',
    


    # Scalper
    'scalper_limit_entry':         '⚡ *دخول Scalper Limit*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ خطأ Scalper Limit: {msg}',
    'scalper_market_entry':        '⚡ *دخول Scalper Market*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ خطأ Scalper Market: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *دخول Elcaro Limit*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ خطأ Elcaro Limit: {msg}',
    'elcaro_market_entry':         '🔥 *دخول Elcaro Market*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ خطأ Elcaro Market: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *دخول Fibonacci Limit*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ خطأ Fibonacci Limit: {msg}',
    'fibonacci_market_entry':        '📐 *دخول Fibonacci Market*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ خطأ Fibonacci Market: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 لوحة الإدارة:',
    'admin_pause':                 '⏸️ تم إيقاف التداول والإشعارات للجميع.',
    'admin_resume':                '▶️ تم استئناف التداول والإشعارات للجميع.',
    'admin_closed':                '✅ تم إغلاق المجموع {count} {type}.',
    'admin_canceled_limits':       '✅ تم إلغاء {count} من أوامر الـ Limit.',

    # Coin groups
    'select_coin_group':           'اختر مجموعة العملات:',
    'group_all':                   'ALL',
    'group_top100':                'TOP100',
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ تم تعيين مجموعة العملات: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *تحليل RSI+BB*\n'
        '• السعر: `{price:.6f}`\n'
        '• RSI: `{rsi:.1f}` ({zone})\n'
        '• الحد العلوي BB: `{bb_hi:.4f}`\n'
        '• الحد السفلي BB: `{bb_lo:.4f}`\n\n'
        '*دخول MARKET {side} وفق RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'بيع مفرط (<30)',
    'rsi_zone_overbought':         'شراء مفرط (>70)',
    'rsi_zone_neutral':            'محايد (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ TP/SL غير صحيح للـ LONG.\n'
        'السعر الحالي: {current:.2f}\n'
        'المتوقع: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ TP/SL غير صحيح للـ SHORT.\n'
        'السعر الحالي: {current:.2f}\n'
        'المتوقع: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 لا يوجد لديك مركز مفتوح على {symbol}',
    'tpsl_set_success':            '✅ تم ضبط TP={tp:.2f} و SL={sl:.2f} لـ {symbol}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 اللغة',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'وضع الإيقاف: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ تم تنفيذ أمر Limit لـ {symbol} عند {price}',
    'limit_order_cancelled':       '⚠️ تم إلغاء أمر Limit لـ {symbol} (ID: {order_id}).',
    'fixed_sl_tp':                 '✅ {symbol}: تم تعيين SL عند {sl}، وTP عند {tp}',
    'tp_part':                     ', تم تعيين TP عند {tp_price}',
    'sl_tp_set':                   '✅ {symbol}: تم ضبط SL عند {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: تم ضبط SL عند {sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: تم تهيئة SL/TP عند {sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: تحريك SL إلى نقطة التعادل عند {entry}',
    'sl_tp_updated':               '✏️ {symbol}: تم تحديث SL/TP إلى {sl}/{tp}',

    'position_closed_error': (
        '⚠️ تم إغلاق مركز {symbol} لكن تعذر تسجيله: {error}\n'
        'يرجى التواصل مع الدعم.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  'نسبة ثابتة %',

    # System notices
    'db_quarantine_notice':        '⚠️ تم إيقاف التسجيل مؤقتاً. تم تفعيل الوضع الهادئ لمدة ساعة.',

    # Fallback
    'fallback':                    '❓ يرجى استخدام أزرار القائمة.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    # Access / terms / moderation
    'banned': '🚫 تم حظرك.',
    'invite_only': '🔒 الوصول بالدعوة فقط. يرجى انتظار موافقة المسؤول.',
    'need_terms': '⚠️ يرجى قبول الشروط أولاً: /terms',
    'please_confirm': 'يرجى التأكيد:',
    'terms_ok': '✅ شكرًا! تم قبول الشروط.',
    'terms_declined': '❌ رفضت الشروط. تم إغلاق الوصول. يمكنك العودة عبر /terms.',
    'usage_approve': 'الاستخدام: /approve <user_id>',
    'usage_ban': 'الاستخدام: /ban <user_id>',
    'not_allowed': 'غير مسموح',
    'bad_payload': 'بيانات غير صالحة',
    'unknown_action': 'إجراء غير معروف',

    # Admin: new user notification
    'title': 'مستخدم جديد',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• الاسم: {name}\n'
        '• اسم المستخدم: {uname}\n'
        '• اللغة: {lang}\n'
        '• مسموح: {allowed}  حظر: {banned}\n'
    ),
    'btn_approve': '✅ موافقة',
    'btn_ban': '⛔️ حظر',
    'admin_notify_fail': 'فشل إشعار المسؤول: {e}',
    'moderation_approved': '✅ تمت الموافقة: {target}',
    'moderation_banned': '⛔️ تم الحظر: {target}',
    'approved_user_dm': '✅ تم منح الوصول. اضغط /start.',
    'banned_user_dm': '🚫 تم حظرك.',

    # Admin: users list / navigation
    'users_not_found': '😕 لم يتم العثور على مستخدمين.',
    'users_page_info': '📄 صفحة {page}/{pages} — الإجمالي: {total}',
    'user_card_html': (
        '<b>👤 مستخدم</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• الاسم: {full_name}\n'
        '• اسم المستخدم: {uname}\n'
        '• اللغة: <code>{lang}</code>\n'
        '• مسموح: {allowed}\n'
        '• محظور: {banned}\n'
        '• الشروط: {terms}\n'
        '• ٪ لكل صفقة: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 القائمة السوداء',
    'btn_delete_user': '🗑 حذف من قاعدة البيانات',
    'btn_prev': '⬅️ رجوع',
    'btn_next': '➡️ التالي',
    'nav_caption': '🧭 التنقل:',
    'bad_page': 'صفحة غير صالحة.',
    'admin_user_delete_fail': '❌ فشل حذف {target}: {error}',
    'admin_user_deleted': '🗑 تم حذف المستخدم {target} من قاعدة البيانات.',
    'user_access_approved': '✅ تم منح الوصول. اضغط /start.',

    # Admin panel & actions
    'admin_pause_all': '⏸️ إيقاف للجميع',
    'admin_resume_all': '▶️ استئناف',
    'admin_close_longs': '🔒 إغلاق جميع LONG',
    'admin_close_shorts': '🔓 إغلاق جميع SHORT',
    'admin_cancel_limits': '❌ حذف أوامر الحد',
    'admin_users': '👥 المستخدمون',
    'admin_pause_notice': '⏸️ تم إيقاف التداول والإشعارات للجميع.',
    'admin_resume_notice': '▶️ تم استئناف التداول والإشعارات للجميع.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ تم إغلاق المجموع {count} {type}.',
    'admin_canceled_limits_total': '✅ تم إلغاء {count} من أوامر الحد.',

    # Terms buttons
    'terms_btn_accept': '✅ أوافق',
    'terms_btn_decline': '❌ أرفض',

    # Market emojis
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
    'api_test_success':            'الاتصال ناجح!',
    'api_test_no_keys':            'مفاتيح API غير معينة',
    'api_test_set_keys':           'يرجى تعيين API Key و Secret أولاً.',
    'api_test_failed':             'فشل الاتصال',
    'api_test_error':              'خطأ',
    'api_test_check_keys':         'يرجى التحقق من بيانات API الخاصة بك.',
    'api_test_status':             'الحالة',
    'api_test_connected':          'متصل',
    'balance_wallet':              'رصيد المحفظة',
    'balance_equity':              'الملكية',
    'balance_available':           'متاح',
    'api_missing_notice':          '⚠️ لم تقم بتكوين مفاتيح API للبورصة. يرجى إضافة مفتاح API والسر في الإعدادات (أزرار 🔑 API و 🔒 Secret)، وإلا لن يتمكن البوت من التداول نيابة عنك.',
    'elcaro_ai_info':              '🤖 *تداول مدعوم بالذكاء الاصطناعي*',

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
    'strat_mode_global':           '🌐 عالمي',
    'strat_mode_demo':             '🧪 تجريبي',
    'strat_mode_real':             '💰 حقيقي',
    'strat_mode_both':             '🔄 كلاهما',
    'strat_mode_changed':          '✅ وضع تداول {strategy}: {mode}',

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

    'scalper_limit_entry':           'Scalper: أمر محدود {symbol} @ {price}',
    'scalper_limit_error':           'Scalper خطأ محدود: {msg}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper خطأ: {msg}',

    # Strategy Settings
    'button_strategy_settings':      '⚙️ إعدادات الاستراتيجيات',
    'strategy_settings_header':      '⚙️ *إعدادات الاستراتيجيات*',
    'strategy_param_header':         '⚙️ *إعدادات {name}*',
    'using_global':                  'إعدادات عامة',
    'global_default':                'عام',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ إعدادات DCA',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA المرحلة 1 %',
    'dca_leg2':                      '📉 DCA المرحلة 2 %',
    'param_percent':                 '📊 الدخول %',
    'param_sl':                      '🔻 وقف الخسارة %',
    'param_tp':                      '🔺 جني الأرباح %',
    'param_reset':                   '🔄 إعادة تعيين للعام',
    'btn_close':                     '❌ إغلاق',
    'prompt_entry_pct':              'أدخل % الدخول (المخاطرة لكل صفقة):',
    'prompt_sl_pct':                 'أدخل % وقف الخسارة:',
    'prompt_tp_pct':                 'أدخل % جني الأرباح:',
    'prompt_atr_periods':            'أدخل فترات ATR (مثلاً: 7):',
    'prompt_atr_mult':               'أدخل مضاعف ATR لوقف الخسارة المتحرك (مثلاً: 1.0):',
    'prompt_atr_trigger':            'أدخل % تفعيل ATR (مثلاً: 2.0):',
    'prompt_dca_leg1':               'أدخل % DCA المرحلة 1 (مثلاً: 10):',
    'prompt_dca_leg2':               'أدخل % DCA المرحلة 2 (مثلاً: 25):',
    'settings_reset':                'تم إعادة تعيين الإعدادات للعام',
    'strat_setting_saved':           '✅ {name} {param} تم تعيينه إلى {value}',
    'dca_setting_saved':             '✅ DCA {leg} تم تعيينه إلى {value}%',
    'invalid_number':                '❌ رقم غير صالح. أدخل قيمة بين 0 و 100.',
    'dca_10pct':                     'DCA −{pct}%: إضافة {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: إضافة {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: المرحلة1=-{dca1}%, المرحلة2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 فترات ATR',
    'param_atr_mult':                '📉 مضاعف ATR (خطوة SL)',
    'param_atr_trigger':             '🎯 تفعيل ATR %',

    # Hardcoded strings fix
    'terms_unavailable':             'شروط الخدمة غير متوفرة. يرجى الاتصال بالمسؤول.',
    'terms_confirm_prompt':          'يرجى التأكيد:',
    'your_id':                       'معرّفك: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'خطأ: {msg}',

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
    'stats_strategy_settings':       'إعدادات الاستراتيجية',
    'settings_entry_pct':            'الدخول',
    'settings_leverage':             'الرافعة',
    'settings_trading_mode':         'الوضع',
    'settings_direction':            'الاتجاه',
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

    # Leverage settings
    'param_leverage': '⚡ الرافعة',
    'prompt_leverage': 'أدخل الرافعة (1-100):',
    'auto_default': 'تلقائي',

    # Elcaro AI
    'elcaro_ai_desc': '_يتم تحليل جميع المعلمات تلقائيًا من إشارات AI:_',

    # Scalper entries
    'scalper_market_entry': '🚀 Scalper سوق {symbol} @ {price:.6f}',
    'scalper_analysis': 'Scalper: {side} @ {price}',

    # Scryptomera feature
    'feature_scryptomera': 'Scryptomera',
    


    # Limit Ladder
    'limit_ladder': '📉 سلم الليمت',
    'limit_ladder_header': '📉 *إعدادات سلم الليمت*',
    'limit_ladder_settings': '⚙️ إعدادات السلم',
    'ladder_count': 'عدد الأوامر',
    'ladder_info': 'أوامر ليمت أسفل الدخول لـDCA. كل أمر له % من الدخول و% من الإيداع.',
    'prompt_ladder_pct_entry': '📉 أدخل % أسفل سعر الدخول للأمر {idx}:',
    'prompt_ladder_pct_deposit': '💰 أدخل % من الإيداع للأمر {idx}:',
    'ladder_order_saved': '✅ تم حفظ الأمر {idx}: -{pct_entry}% @ {pct_deposit}% إيداع',
    'ladder_orders_placed': '📉 تم وضع {count} أمر ليمت لـ{symbol}',
    
    # Spot Trading Mode
    'spot_trading_mode': 'وضع التداول',
    'spot_btn_mode': 'الوضع',
    
    # Stats PnL
    'stats_realized_pnl': 'محقق',
    'stats_unrealized_pnl': 'غير محقق',
    'stats_combined_pnl': 'مجموع',
    'stats_spot': '💹 سبوت',
    'stats_spot_title': 'إحصائيات Spot DCA',
    'stats_spot_config': 'الإعدادات',
    'stats_spot_holdings': 'المراكز',
    'stats_spot_summary': 'ملخص',
    'stats_spot_current_value': 'القيمة الحالية',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    'no_license': '⚠️ تحتاج إلى اشتراك نشط لاستخدام هذه الميزة.\n\nاستخدم /subscribe لشراء ترخيص.',
    'no_license_trading': '⚠️ تحتاج إلى اشتراك نشط للتداول.\n\nاستخدم /subscribe لشراء ترخيص.',
    'license_required': '⚠️ هذه الميزة تتطلب اشتراك {required}.\n\nاستخدم /subscribe للترقية.',
    'trial_demo_only': '⚠️ ترخيص التجربة يسمح فقط بالتداول التجريبي.\n\nقم بالترقية إلى Premium أو Basic للتداول الحقيقي: /subscribe',
    'basic_strategy_limit': '⚠️ ترخيص Basic على الحساب الحقيقي يسمح فقط بـ: {strategies}\n\nقم بالترقية إلى Premium لجميع الاستراتيجيات: /subscribe',
    
    'subscribe_menu_header': '💎 *خطط الاشتراك*',
    'subscribe_menu_info': 'اختر خطتك لفتح ميزات التداول:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 تجربة (مجاني)',
    'btn_enter_promo': '🎟 كود ترويجي',
    'btn_my_subscription': '📋 اشتراكي',
    
    'premium_title': '💎 *خطة PREMIUM*',
    'premium_desc': '''✅ وصول كامل لجميع الميزات
✅ جميع الاستراتيجيات الـ5: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ تداول حقيقي + تجريبي
✅ دعم أولوية
✅ SL/TP ديناميكي مبني على ATR
✅ سلم الليمت DCA
✅ جميع التحديثات المستقبلية''',
    'premium_1m': '💎 1 شهر — {price}⭐',
    'premium_3m': '💎 3 أشهر — {price}⭐ (-15%)',
    'premium_6m': '💎 6 أشهر — {price}⭐ (-25%)',
    'premium_12m': '💎 12 شهر — {price}⭐ (-35%)',
    
    'basic_title': '🥈 *خطة BASIC*',
    'basic_desc': '''✅ وصول كامل للحساب التجريبي
✅ الحساب الحقيقي: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Fibonacci, Spot — Premium فقط
✅ دعم عادي
✅ SL/TP ديناميكي مبني على ATR''',
    'basic_1m': '🥈 1 شهر — {price}⭐',
    
    'trial_title': '🎁 *خطة التجربة (مجاني)*',
    'trial_desc': '''✅ وصول كامل للحساب التجريبي
✅ جميع الاستراتيجيات الـ5 على التجريبي
❌ التداول الحقيقي غير متاح
⏰ المدة: 7 أيام
🎁 مرة واحدة فقط''',
    'trial_activate': '🎁 تفعيل التجربة المجانية',
    'trial_already_used': '⚠️ لقد استخدمت تجربتك المجانية بالفعل.',
    'trial_activated': '🎉 تم تفعيل التجربة! لديك 7 أيام من الوصول التجريبي الكامل.',
    
    'payment_select_method': '💳 *اختر طريقة الدفع*',
    'btn_pay_stars': '⭐ Telegram Stars',
    'btn_pay_ton': '💎 TON',
    'payment_stars_title': '⭐ الدفع عبر Telegram Stars',
    'payment_stars_desc': 'سيتم خصم {amount}⭐ مقابل {plan} ({period}).',
    'payment_ton_title': '💎 الدفع عبر TON',
    'payment_ton_desc': '''أرسل بالضبط *{amount} TON* إلى:

`{wallet}`

بعد الدفع، انقر على الزر أدناه للتحقق.''',
    'btn_verify_ton': '✅ دفعت — تحقق',
    'payment_processing': '⏳ جاري معالجة الدفع...',
    'payment_success': '🎉 نجح الدفع!\n\n{plan} مفعل حتى {expires}.',
    'payment_failed': '❌ فشل الدفع: {error}',
    
    'my_subscription_header': '📋 *اشتراكي*',
    'my_subscription_active': '''📋 *الخطة الحالية:* {plan}
⏰ *ينتهي:* {expires}
📅 *الأيام المتبقية:* {days}''',
    'my_subscription_none': '❌ لا يوجد اشتراك نشط.\n\nاستخدم /subscribe لشراء خطة.',
    'my_subscription_history': '📜 *سجل المدفوعات:*',
    'subscription_expiring_soon': '⚠️ اشتراكك {plan} ينتهي خلال {days} أيام!\n\nجدد الآن: /subscribe',
    
    'promo_enter': '🎟 أدخل الكود الترويجي:',
    'promo_success': '🎉 تم تطبيق الكود الترويجي!\n\n{plan} مفعل لمدة {days} أيام.',
    'promo_invalid': '❌ كود ترويجي غير صالح.',
    'promo_expired': '❌ هذا الكود الترويجي منتهي الصلاحية.',
    'promo_used': '❌ هذا الكود الترويجي مستخدم بالفعل.',
    'promo_already_used': '❌ لقد استخدمت هذا الكود الترويجي بالفعل.',
    
    'admin_license_menu': '🔑 *إدارة التراخيص*',
    'admin_btn_grant_license': '🎁 منح ترخيص',
    'admin_btn_view_licenses': '📋 عرض التراخيص',
    'admin_btn_create_promo': '🎟 إنشاء كود',
    'admin_btn_view_promos': '📋 عرض الأكواد',
    'admin_btn_expiring_soon': '⚠️ ينتهي قريباً',
    'admin_grant_select_type': 'اختر نوع الترخيص:',
    'admin_grant_select_period': 'اختر الفترة:',
    'admin_grant_enter_user': 'أدخل معرف المستخدم:',
    'admin_license_granted': '✅ تم منح {plan} للمستخدم {uid} لمدة {days} أيام.',
    'admin_license_extended': '✅ تم تمديد الترخيص بـ {days} أيام للمستخدم {uid}.',
    'admin_license_revoked': '✅ تم إلغاء الترخيص للمستخدم {uid}.',
    'admin_promo_created': '✅ تم إنشاء الكود الترويجي: {code}\nالنوع: {type}\nالأيام: {days}\nالحد الأقصى للاستخدام: {max}',

    'admin_users_management': '👥 المستخدمون',
    'admin_licenses': '🔑 التراخيص',
    'admin_search_user': '🔍 البحث عن مستخدم',
    'admin_users_menu': '👥 *إدارة المستخدمين*\n\nاختر فلتر أو ابحث:',
    'admin_all_users': '👥 جميع المستخدمين',
    'admin_active_users': '✅ نشط',
    'admin_banned_users': '🚫 محظور',
    'admin_no_license': '❌ بدون ترخيص',
    'admin_no_users_found': 'لم يتم العثور على مستخدمين.',
    'admin_enter_user_id': '🔍 أدخل معرف المستخدم للبحث:',
    'admin_user_found': '✅ تم العثور على المستخدم {uid}!',
    'admin_user_not_found': '❌ لم يتم العثور على المستخدم {uid}.',
    'admin_invalid_user_id': '❌ معرف مستخدم غير صالح. أدخل رقماً.',
    'admin_view_card': '👤 عرض البطاقة',
    
    'admin_user_card': '''👤 *بطاقة المستخدم*

📋 *المعرف:* `{uid}`
{status_emoji} *الحالة:* {status}
📝 *الشروط:* {terms}

{license_emoji} *الترخيص:* {license_type}
📅 *ينتهي:* {license_expires}
⏳ *الأيام المتبقية:* {days_left}

🌐 *اللغة:* {lang}
📊 *وضع التداول:* {trading_mode}
💰 *% لكل صفقة:* {percent}%
🪙 *العملات:* {coins}

🔌 *مفاتيح API:*
  تجريبي: {demo_api}
  حقيقي: {real_api}

📈 *الاستراتيجيات:* {strategies}

📊 *الإحصائيات:*
  المراكز: {positions}
  الصفقات: {trades}
  الربح/الخسارة: {pnl}
  معدل الفوز: {winrate}%

💳 *المدفوعات:*
  الإجمالي: {payments_count}
  Stars: {total_stars}⭐

📅 *أول ظهور:* {first_seen}
🕐 *آخر ظهور:* {last_seen}
''',
    
    'admin_btn_grant_lic': '🎁 منح',
    'admin_btn_extend': '⏳ تمديد',
    'admin_btn_revoke': '🚫 إلغاء',
    'admin_btn_ban': '🚫 حظر',
    'admin_btn_unban': '✅ إلغاء الحظر',
    'admin_btn_approve': '✅ موافقة',
    'admin_btn_message': '✉️ رسالة',
    'admin_btn_delete': '🗑 حذف',
    
    'admin_user_banned': 'تم حظر المستخدم!',
    'admin_user_unbanned': 'تم إلغاء حظر المستخدم!',
    'admin_user_approved': 'تم الموافقة على المستخدم!',
    'admin_confirm_delete': '⚠️ *تأكيد الحذف*\n\nسيتم حذف المستخدم {uid} نهائياً!',
    'admin_confirm_yes': '✅ نعم، احذف',
    'admin_confirm_no': '❌ إلغاء',
    
    'admin_select_license_type': 'اختر نوع الترخيص للمستخدم {uid}:',
    'admin_select_period': 'اختر الفترة:',
    'admin_select_extend_days': 'اختر أيام التمديد للمستخدم {uid}:',
    'admin_license_granted_short': 'تم منح الترخيص!',
    'admin_license_extended_short': 'تم التمديد {days} أيام!',
    'admin_license_revoked_short': 'تم إلغاء الترخيص!',
    
    'admin_enter_message': '✉️ أدخل الرسالة لإرسالها للمستخدم {uid}:',
    'admin_message_sent': '✅ تم إرسال الرسالة للمستخدم {uid}!',
    'admin_message_failed': '❌ فشل إرسال الرسالة: {error}',

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
    'payment_ton_not_found': '''❌ Payment not found or amount incorrect.

Please make sure you:
• Sent the exact amount
• Included the correct comment
• Wait a few minutes for confirmation

Try again after payment is confirmed on blockchain.''',
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
    "hl_trading_enabled": "تداول HyperLiquid",
    "hl_reset_settings": "🔄 إعادة تعيين إلى إعدادات Bybit",



    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ تم الإلغاء.',
    'entry_pct_range_error': '❌ نسبة الدخول يجب أن تكون بين 0.1 و 100.',
    'hl_no_history': '📭 لا يوجد تاريخ تداول على HyperLiquid.',
    'hl_no_orders': '📭 لا توجد أوامر مفتوحة على HyperLiquid.',
    'hl_no_positions': '📭 لا توجد صفقات مفتوحة على HyperLiquid.',
    'hl_setup_cancelled': '❌ تم إلغاء إعداد HyperLiquid.',
    'invalid_amount': '❌ رقم غير صالح. أدخل مبلغاً صالحاً.',
    'leverage_range_error': '❌ الرافعة المالية يجب أن تكون بين 1 و 100.',
    'max_amount_error': '❌ الحد الأقصى 100,000 USDT',
    'min_amount_error': '❌ الحد الأدنى 1 USDT',
    'sl_tp_range_error': '❌ نسبة SL/TP يجب أن تكون بين 0.1 و 500.',


    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 تفعيل DCA',
    'btn_ignore': '🔇 تجاهل',
    'dca_already_enabled': '✅ DCA مفعل بالفعل!\n\n📊 <b>{symbol}</b>\nالبوت سيضيف تلقائياً عند الانخفاض:\n• -10% → إضافة\n• -25% → إضافة\n\nهذا يساعد في تحسين متوسط سعر الدخول.',
    'dca_enable_error': '❌ خطأ: {error}',
    'dca_enabled_for_symbol': '✅ تم تفعيل DCA!\n\n📊 <b>{symbol}</b>\nالبوت سيضيف تلقائياً عند الانخفاض:\n• -10% → إضافة (متوسط)\n• -25% → إضافة (متوسط)\n\n⚠️ DCA يتطلب رصيداً كافياً للأوامر الإضافية.',
    'deep_loss_alert': '⚠️ <b>المركز في خسارة عميقة!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 الخسارة: <code>{loss_pct:.2f}%</code>\n💰 الدخول: <code>{entry}</code>\n📍 الحالي: <code>{mark}</code>\n\n❌ لا يمكن تعيين وقف الخسارة فوق سعر الدخول.\n\n<b>ماذا تفعل؟</b>\n• <b>إغلاق</b> - تثبيت الخسارة\n• <b>DCA</b> - متوسط المركز\n• <b>تجاهل</b> - اتركه كما هو',
    'deep_loss_close_error': '❌ خطأ في إغلاق المركز: {error}',
    'deep_loss_closed': '✅ تم إغلاق المركز {symbol}.\n\nتم تثبيت الخسارة. أحياناً من الأفضل قبول خسارة صغيرة بدلاً من انتظار الانعكاس.',
    'deep_loss_ignored': '🔇 حسناً، المركز {symbol} ترك دون تغيير.\n\n⚠️ تذكر: بدون وقف الخسارة، خطر الخسائر غير محدود.\nيمكنك إغلاق المركز يدوياً عبر /positions',
    'fibonacci_desc': '_الدخول، SL، TP - من مستويات فيبوناتشي في الإشارة_',
    'fibonacci_info': '📐 *استراتيجية فيبوناتشي*',
    'prompt_min_quality': 'أدخل الحد الأدنى للجودة % (0-100):',


    # Hardcore trading phrase
    'hardcore_mode': '💀 *وضع هاردكور*: لا رحمة، لا ندم. فقط الربح أو الموت! 🔥',
}
