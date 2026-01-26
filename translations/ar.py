# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu - BLACK RHETORIC: FOMO + Authority + Exclusivity
    'welcome':                     '''🔥 <b>مرحباً، أيها المتداول المحترف!</b>

بينما تقرأ هذا — <b>847 متداولاً</b> يحققون أرباحاً مع Lyxen.

⚡ <b>&lt; 100 ملي ثانية</b> سرعة التنفيذ
🛡️ <b>664 اختبار أمان</b> ناجح
💎 <b>24/7</b> تداول مدعوم بالذكاء الاصطناعي

<i>منافسوك لا ينامون. Lyxen أيضاً لا ينام.</i>

اختر طريقك نحو الحرية المالية:''',
    'no_strategies':               '❌ لا شيء — <i>أنت تخسر المال كل ثانية بدون استراتيجيات نشطة</i>',
    'guide_caption':               '📚 <b>أسرار تداول النخبة</b>\n\n⚠️ هذه المعلومات منحت أفضل متداولينا <b>ميزة غير عادلة</b>.\n\n<i>وقت القراءة: 3 دقائق. الربح المحتمل: بلا حدود.</i>',
    'privacy_caption':             '📜 <b>أمانك = هوسنا</b>\n\n🔐 تشفير بنكي\n✅ لا مشاركة بيانات. أبداً.\n\n<i>أنت في أيدٍ أمينة.</i>',
    
    # ═══════════════════════════════════════════════════════════════════
    # MODERN MENU BUTTONS - Stylish & Persuasive
    # ═══════════════════════════════════════════════════════════════════
    'button_api':                  '🔐 ربط API',
    'button_secret':               '🔑 المفتاح السري',
    'button_api_settings':         '⚙️ إعداد API',
    'button_balance':              '💎 المحفظة',
    'button_orders':               '📊 الأوامر',
    'button_positions':            '🎯 المراكز',
    'button_history':              '📜 السجل',
    'button_strategies':           '🤖 روبوتات AI',
    'button_api_keys':             '🔑 مفاتيح API',
    'button_bybit':                '🟠 Bybit',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_switch_bybit':         '🔄 Bybit',
    'button_switch_hl':            '🔄 HL',
    'button_subscribe':            '👑 PREMIUM',
    'button_licenses':             '🎫 التراخيص',
    'button_admin':                '👑 المسؤول',
    'button_percent':              '🎚 ٪ لكل صفقة',
    'button_coins':                '💠 مجموعة العملات',
    'button_market':               '📈 السوق',
    'button_manual_order':         '🎯 Sniper',
    'button_update_tpsl':          '🛡️ TP/SL',
    'button_cancel_order':         '❌ إلغاء الأمر',
    'button_limit_only':           '🎯 ليمت فقط',
    'button_toggle_oi':            '� OI Tracker',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_scalper':              '⚡ Scalper',
    'button_elcaro':               '🔥 Lyxen',
    'button_fibonacci':            '📐 Fibonacci',
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
    'account_balance':             '💰 الرصيد: `{balance:.2f}`',
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
    'position_item_v2':            (
        "— #{idx}: {symbol} | {side} (x{leverage}) [{strategy}]\n"
        "  • الحجم          : {size}\n"
        "  • سعر الدخول     : {avg:.8f}\n"
        "  • سعر المؤشر     : {mark:.8f}\n"
        "  • التصفية        : {liq}\n"
        "  • الهامش الأولي  : {im:.2f}\n"
        "  • هامش الصيانة   : {mm:.2f}\n"
        "  • أخذ الربح      : {tp}\n"
        "  • وقف الخسارة    : {sl}\n"
        "  {pnl_emoji} ربح/خسارة غير محقق: {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'pnl_by_strategy':             '📊 *PnL حسب الاستراتيجية:*',
    'pnl_by_exchange':             '🏦 *PnL حسب البورصة:*',
    'positions_overall':           'إجمالي الربح/الخسارة غير المحقق: {pnl:+.2f} ({pct:+.2f}%)',

    # Position management (inline)
    'open_positions_header':       '📊 *المراكز المفتوحة*',
    'positions_count':             'مركز',
    'positions_count_total':       'إجمالي المراكز',
    'total_unrealized_pnl':        'إجمالي الربح/الخسارة غير المحقق',
    'total_pnl':                   'إجمالي P/L',
    'btn_close_short':             'إغلاق',
    'btn_close_all':               'إغلاق جميع المراكز',
    'btn_close_position':          'إغلاق المركز',
    'btn_confirm_close':           'تأكيد الإغلاق',
    'btn_confirm_close_all':       'نعم، أغلق الكل',
    'btn_cancel':                  '❌ إلغاء',
    'btn_back':                    '🔙 رجوع',
    'confirm_close_position':      'إغلاق المركز',
    'confirm_close_all':           'إغلاق جميع المراكز',
    'position_not_found':          'المركز غير موجود أو مغلق بالفعل',
    'position_already_closed':     'المركز مغلق بالفعل',
    'position_closed_success':     'تم إغلاق المركز',
    'position_close_error':        'خطأ في إغلاق المركز',
    'positions_closed':            'تم إغلاق المراكز',
    'errors':                      'أخطاء',

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
    'indicators_header':           '📈 *مؤشرات Lyxen*',
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

    # Auto notifications - BLACK RHETORIC: Excitement & Celebration
    'new_position': (
        '🚀🔥 <b>تم فتح مركز جديد!</b>\n'
        '• {symbol} @ {entry:.6f}\n'
        '• الحجم: {size}\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>الذكاء الاصطناعي يعمل لأجلك! 🤖</i>'
    ),
    'sl_auto_set':                 '🛑 تم تعيين SL تلقائياً: {price:.6f}',
    'auto_close_position':         '⏱ المركز {symbol} (TF={tf}) مفتوح لأكثر من {tf} ويخسر، تم إغلاقه تلقائياً.',
    'position_closed': (
        '🎉 <b>تم إغلاق المركز!</b> {symbol}\n'
        '• السبب: <b>{reason}</b>\n'
        '• الاستراتيجية: `{strategy}`\n'
        '• الدخول: `{entry:.8f}`\n'
        '• الخروج: `{exit:.8f}`\n'
        '{pnl_emoji} <b>PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`</b>\n'
        '📍 {exchange} • {market_type}'
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
    'insufficient_balance_error_extended': '❌ <b>رصيد غير كافٍ!</b>\n\n📊 الاستراتيجية: <b>{strategy}</b>\n🪙 الرمز: <b>{symbol}</b> {side}\n\n💰 لا توجد أموال كافية في حساب {account_type}.\n\n<b>الحلول:</b>\n• إعادة شحن الرصيد\n• تقليل حجم المركز (% لكل صفقة)\n• تخفيض الرافعة\n• إغلاق بعض المراكز',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>الرافعة المالية عالية جداً!</b>\n\n⚙️ الرافعة المالية المُعدّة تتجاوز الحد الأقصى المسموح به لهذا الرمز.\n\n<b>الحد الأقصى المسموح:</b> {max_leverage}x\n\n<b>الحل:</b> انتقل إلى إعدادات الاستراتيجية وقم بتخفيض الرافعة المالية.',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>تم تجاوز حد المركز!</b>\n\n📊 الاستراتيجية: <b>{strategy}</b>\n🪙 الرمز: <b>{symbol}</b>\n\n⚠️ سيتجاوز مركزك الحد الأقصى.\n\n<b>الحلول:</b>\n• تقليل الرافعة المالية\n• تقليل حجم المركز\n• إغلاق بعض المراكز',
    

    # Scalper
    'scalper_limit_entry':         '⚡ *دخول Scalper Limit*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ خطأ Scalper Limit: {msg}',
    'scalper_market_entry':        '⚡ *دخول Scalper Market*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ خطأ Scalper Market: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Lyxen (Heatmap)
    'elcaro_limit_entry':          '🔥 *دخول Lyxen Limit*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ خطأ Lyxen Limit: {msg}',
    'elcaro_market_entry':         '🔥 *دخول Lyxen Market*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Lyxen: {side}*\n• {symbol} @ {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ خطأ Lyxen Market: {msg}',
    'elcaro_analysis':             '🔥 Lyxen Heatmap: {side} @ {price}',
    'feature_elcaro':              'Lyxen',

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
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
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
    'config_trade_scalper':          '🎯 Scalper: {state}',
    'config_trade_elcaro':           '🔥 Lyxen: {state}',
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
    'strat_mode_global':           '🌐 عالمي',
    'strat_mode_demo':             '🧪 تجريبي',
    'strat_mode_real':             '💰 حقيقي',
    'strat_mode_both':             '🔄 كلاهما',
    'strat_mode_changed':          '✅ وضع تداول {strategy}: {mode}',

    # Lyxen (Heatmap)

    # Fibonacci (Fibonacci Extension)

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
    'strat_elcaro':                  '🔥 Lyxen',
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
    'error_fetch_balance':           '❌ خطأ في جلب الرصيد: {error}',
    'error_fetch_orders':            '❌ خطأ في جلب الأوامر: {error}',
    'error_occurred':                '❌ خطأ: {error}',

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
    'stats_elcaro':                  '🔥 Lyxen',
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

    # Lyxen AI settings

    # Leverage settings
    'param_leverage': '⚡ الرافعة',
    'prompt_leverage': 'أدخل الرافعة (1-100):',
    'auto_default': 'تلقائي',

    # Lyxen AI
    'elcaro_ai_desc': '_يتم تحليل جميع المعلمات تلقائيًا من إشارات AI:_',

    # Scalper entries

    # Scryptomera feature
    

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
    
    # License status messages - BLACK RHETORIC: Loss Aversion + FOMO
    'no_license': '''🚨 <b>تم رفض الوصول</b>

بينما تتردد، <b>847 متداولاً</b> يحققون أرباحاً الآن.

💸 كل دقيقة بدون Lyxen = فرص ضائعة
⏰ الأسواق لا تنتظر. وأنت أيضاً.

👉 /subscribe — <i>افتح ميزتك الفريدة الآن</i>''',
    'no_license_trading': '''🚨 <b>التداول مقفل</b>

⚠️ 847 متداولاً يكسبون الآن مع Lyxen.

❌ التداول اليدوي = أخطاء عاطفية
✅ Lyxen = دقة الذكاء الاصطناعي الباردة

<i>توقف عن المشاهدة. ابدأ الربح.</i>

👉 /subscribe — <b>انضم إلى 847+ متداول ذكي</b>''',
    'license_required': '''🔒 <b>ميزة PREMIUM</b>

هذا يتطلب اشتراك {required} — <i>يستخدمها أفضل 3% من المتداولين</i>.

🎯 النجاح يترك أدلة. اتبع الفائزين.

👉 /subscribe — <b>الترقية الآن</b>''',
    'trial_demo_only': '''⚠️ <b>الوضع التجريبي للتعلم، ليس للربح.</b>

الأرباح الحقيقية تتطلب وصولاً حقيقياً.

🎁 لقد تذوقت القوة. الآن <b>امتلكها</b>.

👉 /subscribe — <b>افتح التداول الحقيقي</b>''',
    'basic_strategy_limit': '''⚠️ <b>Basic = نتائج Basic</b>

أنت مقيد بـ: {strategies}

المحترفون يستخدمون <b>جميع</b> الاستراتيجيات. لهذا هم محترفون.

👉 /subscribe — <b>انتقل إلى Premium. كن محترفاً.</b>''',
    
    'subscribe_menu_header': '👑 *وصول VIP إلى نادي المتداولين النخبة*',
    'subscribe_menu_info': 'اختر خطتك لفتح ميزات التداول:',
    'btn_premium': '💎 Premium',
    'btn_basic': '🥈 Basic', 
    'btn_trial': '🎁 تجربة (مجاني)',
    'btn_enter_promo': '🎟 كود ترويجي',
    'btn_my_subscription': '📋 اشتراكي',
    
    'premium_title': '� *PREMIUM — اختيار الفائزين*',
    'premium_desc': '''✅ وصول كامل لجميع الميزات
✅ جميع الاستراتيجيات الـ5: OI, RSI+BB, Scryptomera, Scalper, Lyxen
✅ تداول حقيقي + تجريبي
✅ دعم أولوية
✅ SL/TP ديناميكي مبني على ATR
✅ سلم الليمت DCA
✅ جميع التحديثات المستقبلية''',
    'premium_1m': '💎 1 شهر — {price} ELC',
    'premium_3m': '💎 3 أشهر — {price} ELC (-10%)',
    'premium_6m': '💎 6 أشهر — {price} ELC (-20%)',
    'premium_12m': '💎 12 شهر — {price} ELC (-30%)',
    
    'basic_title': '🥈 *خطة BASIC*',
    'basic_desc': '''✅ وصول كامل للحساب التجريبي
✅ الحساب الحقيقي: OI, RSI+BB, Scryptomera, Scalper
❌ Lyxen, Fibonacci, Spot — Premium فقط
✅ دعم عادي
✅ SL/TP ديناميكي مبني على ATR''',
    'basic_1m': '🥈 1 شهر — {price} ELC',
    
    'trial_title': '🎁 *تجربة مجانية — عرض محدود!*',
    'trial_desc': '''✅ وصول كامل للحساب التجريبي
✅ جميع الاستراتيجيات الـ5 على التجريبي
❌ التداول الحقيقي غير متاح
⏰ المدة: 7 أيام
🎁 مرة واحدة فقط''',
    'trial_activate': '🎁 تفعيل التجربة المجانية',
    'trial_already_used': '⚠️ لقد استخدمت تجربتك المجانية بالفعل.',
    'trial_activated': '🎉 تم تفعيل التجربة! لديك 7 أيام من الوصول التجريبي الكامل.',
    
    'payment_select_method': '💳 *اختر طريقة الدفع*',
    'btn_pay_elc': '◈ Lyxen Coin (ELC)',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' الدفع عبر ELC',
    'payment_elc_desc': 'سيتم خصم {amount} ELC مقابل {plan} ({period}).',
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
  ELC: {total_elc}

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
    'admin_all_payments': '📜 جميع المدفوعات',
    'admin_demo_stats': '🎮 إحصائيات التجريبي',
    'admin_enter_user_for_report': '👤 أدخل معرّف المستخدم للتقرير المفصل:',
    'admin_generating_report': '📊 جارٍ إنشاء التقرير للمستخدم {uid}...',
    'admin_global_stats': '📊 إحصائيات عامة',
    'admin_no_payments_found': 'لم يتم العثور على مدفوعات.',
    'admin_payments': '💳 المدفوعات',
    'admin_payments_menu': '💳 *إدارة المدفوعات*',
    'admin_real_stats': '💰 إحصائيات حقيقية',
    'admin_reports': '📊 التقارير',
    'admin_reports_menu': '''📊 *التقارير والتحليلات*

اختر نوع التقرير:''',
    'admin_strategy_breakdown': '🎯 حسب الاستراتيجية',
    'admin_top_traders': '🏆 أفضل المتداولين',
    'admin_user_report': '👤 تقرير المستخدم',
    'admin_view_report': '📊 عرض التقرير',
    'admin_view_user': '👤 بطاقة المستخدم',
    'all_positions_closed': 'تم إغلاق جميع المراكز',
    'btn_check_again': '🔄 تحقق مرة أخرى',
    'current': 'الحالي',
    'entry': 'الدخول',
    'max_positions_reached': '⚠️ تم الوصول للحد الأقصى من المراكز. سيتم تخطي الإشارات الجديدة حتى يغلق مركز.',
    'payment_session_expired': '❌ انتهت جلسة الدفع. يرجى البدء من جديد.',
    'payment_ton_not_configured': '❌ مدفوعات TON غير مهيأة.',
    'payment_verifying': '⏳ جارٍ التحقق من الدفع...',
    'position': 'المركز',
    'size': 'الحجم',
    'stats_fibonacci': '📐 فيبوناتشي',

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

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ رصيد ELC غير كافٍ.

رصيدك: {balance} ELC
المطلوب: {required} ELC

قم بشحن المحفظة للمتابعة.''',
    'wallet_address': '''📍 العنوان: `{address}`''',
    'wallet_balance': '''💰 *محفظتك ELC*

◈ الرصيد: *{balance} ELC*
📈 في التخزين: *{staked} ELC*
🎁 مكافآت معلقة: *{rewards} ELC*

💵 القيمة الإجمالية: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« رجوع''',
    'wallet_btn_deposit': '''📥 إيداع''',
    'wallet_btn_history': '''📋 السجل''',
    'wallet_btn_stake': '''📈 تخزين''',
    'wallet_btn_unstake': '''📤 إلغاء التخزين''',
    'wallet_btn_withdraw': '''📤 سحب''',
    'wallet_deposit_demo': '''🎁 احصل على 100 ELC (تجريبي)''',
    'wallet_deposit_desc': '''أرسل رموز ELC إلى عنوان محفظتك:

`{address}`

💡 *الوضع التجريبي:* انقر أدناه للحصول على رموز اختبار مجانية.''',
    'wallet_deposit_success': '''✅ تم إيداع {amount} ELC بنجاح!''',
    'wallet_deposit_title': '''📥 *إيداع ELC*''',
    'wallet_history_empty': '''لا توجد معاملات حتى الآن.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *سجل المعاملات*''',
    'wallet_stake_desc': '''خزّن رموز ELC واربح *12% سنوياً*!

💰 متاح: {available} ELC
📈 مخزّن حالياً: {staked} ELC
🎁 مكافآت معلقة: {rewards} ELC

مكافآت يومية • سحب فوري''',
    'wallet_stake_success': '''✅ تم تخزين {amount} ELC بنجاح!''',
    'wallet_stake_title': '''📈 *تخزين ELC*''',
    'wallet_title': '''◈ *محفظة ELC*''',
    'wallet_unstake_success': '''✅ تم سحب {amount} ELC + {rewards} ELC مكافآت!''',
    'wallet_withdraw_desc': '''أدخل عنوان الوجهة والمبلغ:''',
    'wallet_withdraw_failed': '''❌ فشل السحب: {error}''',
    'wallet_withdraw_success': '''✅ تم سحب {amount} ELC إلى {address}''',
    'wallet_withdraw_title': '''📤 *سحب ELC*''',

    'spot_freq_biweekly': '📅 كل أسبوعين',
    'spot_trailing_enabled': '✅ تم تفعيل Trailing TP: التنشيط عند +{activation}%، التتبع {trail}%',
    'spot_trailing_disabled': '❌ تم إيقاف Trailing TP',
    'spot_grid_started': '🔲 تم بدء Grid bot لـ {coin}: {levels} مستويات من ${low} إلى ${high}',
    'spot_grid_stopped': '⏹ تم إيقاف Grid bot لـ {coin}',
    'spot_limit_placed': '📝 تم وضع أمر محدود: شراء {amount} {coin} بسعر ${price}',
    'spot_limit_cancelled': '❌ تم إلغاء الأمر المحدود لـ {coin}',
    'spot_freq_hourly': '⏰ كل ساعة',

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
    'error_insufficient_balance': '💰 رصيد غير كافٍ في حسابك لفتح مركز. قم بإعادة شحن رصيدك أو تقليل حجم المركز.',
    'error_order_too_small': '📉 حجم الأمر صغير جداً (الحد الأدنى $5). زد Entry% أو أعد شحن رصيدك.',
    'error_api_key_expired': '🔑 مفتاح API منتهي الصلاحية أو غير صالح. قم بتحديث مفاتيح API في الإعدادات.',
    'error_api_key_missing': '🔑 مفاتيح API غير مُعدّة. أضف مفاتيح Bybit في قائمة 🔗 API Keys.',
    'error_rate_limit': '⏳ طلبات كثيرة جداً. انتظر دقيقة وحاول مرة أخرى.',
    'error_position_not_found': '📊 المركز غير موجود أو مغلق بالفعل.',
    'error_leverage_error': '⚙️ خطأ في إعداد الرافعة المالية. حاول ضبطها يدوياً في البورصة.',
    'error_network_error': '🌐 مشكلة في الشبكة. حاول لاحقاً.',
    'error_sl_tp_invalid': '⚠️ لا يمكن تعيين SL/TP: السعر قريب جداً من الحالي. سيتم التحديث في الدورة التالية.',
    'error_equity_zero': '💰 رصيد حسابك صفر. قم بإعادة شحن حساب Demo أو Real للتداول.',

}
