# -*- coding: utf-8 -*-
"""
Enliko Trading Tools — Arabic Translations (العربية)
Version: 4.0.0 | Updated: 28 January 2026
LEGAL: Educational platform, not financial advice.
RTL Language: Right-to-Left text direction
"""

TEXTS = {
    # Common UI
    'loader': '⏳ جاري التحميل...',
    
    # =====================================================
    # LEGAL DISCLAIMERS (إخلاء المسؤولية القانونية)
    # =====================================================
    
    'disclaimer_trading': (
        '⚠️ *إخلاء مسؤولية مهم*\n\n'
        'توفر هذه المنصة أدوات تعليمية للتعرف على أسواق العملات المشفرة.\n'
        'هذه المنصة ليست:\n'
        '• نصيحة مالية\n'
        '• توصية استثمارية\n'
        '• نظام أرباح مضمون\n\n'
        'ينطوي تداول العملات المشفرة على مخاطر خسارة كبيرة. '
        'قد تخسر بعض أو كل استثمارك. '
        'تداول فقط بأموال يمكنك تحمل خسارتها.\n\n'
        'الأداء السابق لا يضمن النتائج المستقبلية.'
    ),
    
    'disclaimer_short': '⚠️ _أدوات تعليمية فقط. ليست نصيحة مالية. التداول ينطوي على مخاطر._',
    
    'disclaimer_execution': (
        '⚠️ بالمتابعة، أنت تقر بأن:\n'
        '• أنت مسؤول عن جميع قرارات التداول\n'
        '• هذه أداة تعليمية، وليست نصيحة مالية\n'
        '• تفهم مخاطر تداول العملات المشفرة\n'
        '• الأداء السابق لا يضمن النتائج المستقبلية'
    ),
    
    # Welcome - Updated with legal positioning
    'welcome': (
        '📊 *مرحبًا بك في Enliko Trading Tools*\n\n'
        '🎯 منصة تعليمية:\n'
        '• تتبع وتحليل المحفظة\n'
        '• اختبار الاستراتيجيات\n'
        '• تصور بيانات السوق\n'
        '• أدوات إدارة المخاطر\n\n'
        '⚠️ _للأغراض التعليمية فقط. ليست نصيحة مالية._\n'
        '_التداول ينطوي على مخاطر خسارة كبيرة._'
    ),
    
    'welcome_back': (
        '📊 *Enliko Trading Tools*\n\n'
        '⚠️ _منصة تعليمية. ليست نصيحة مالية._'
    ),
    
    # Legacy keys
    
    # ═══════════════════════════════════════════════════════════════════
    # MODERN MENU BUTTONS - Stylish & Persuasive
    # ═══════════════════════════════════════════════════════════════════
    'button_orders':               '📊 الأوامر',
    'button_positions':            '🎯 المراكز',

    'button_balance': '💎 المحفظة',
    'button_market': '📈 السوق',
    'button_strategies': '🤖 روبوتات AI',
    'button_subscribe': '👑 بريميوم',
    'button_terminal': '💻 الطرفية',
    'button_terminal': '💻 الطرفية',
    'button_history':              '📜 السجل',
    'button_api_keys':             '🔑 مفاتيح API',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_settings':             '⚙️ الإعدادات',

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
    'positions_header':            '📊 مراكزك المفتوحة:',

    # Position management (inline)
    'btn_close_position':          'إغلاق المركز',
    'btn_cancel':                  '❌ إلغاء',
    'btn_back':                    '🔙 رجوع',
    'position_already_closed':     'المركز مغلق بالفعل',
    'position_closed_success':     'تم إغلاق المركز',
    'position_close_error':        'خطأ في إغلاق المركز',

    # % per trade

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 أوامر الـ Limit فقط: {state}',
    'feature_limit_only':          'Limit-Only',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *مؤشرات Enliko*',
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

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *دخول Enliko Limit*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ خطأ Enliko Limit: {msg}',
    'elcaro_market_entry':         '🔥 *دخول Enliko Market*\n• {symbol} {side}\n• السعر: {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• الكمية: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ خطأ Enliko Market: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

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
    'select_language':             '🌍 اختر لغتك:',
    'language_set':                '✅ تم تعيين اللغة إلى',
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

    # API Settings
    'api_key_set':                 '✅ Set',
    'api_test_success':            'الاتصال ناجح!',
    'api_test_failed':             'فشل الاتصال',
    'balance_equity':              'الملكية',
    'balance_available':           'متاح',
    'api_missing_notice':          '⚠️ لم تقم بتكوين مفاتيح API للبورصة. يرجى إضافة مفتاح API والسر في الإعدادات (أزرار 🔑 API و 🔒 Secret)، وإلا لن يتمكن البوت من التداول نيابة عنك.',
    'elcaro_ai_info':              '🤖 *تداول مدعوم بالذكاء الاصطناعي*',

    # Spot Trading
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_balance':                '💰 Spot Balance: {balance}',

    # Strategy trading mode

    # Enliko (Heatmap)

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
    'strat_elcaro':                  '🔥 Enliko',
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

    # Break-Even settings UI
    'be_settings_header':            '🔒 *إعدادات نقطة التعادل*',
    'be_settings_desc':              '_نقل وقف الخسارة إلى سعر الدخول عند وصول الربح إلى نسبة التفعيل_',
    'be_enabled_label':              '🔒 نقطة التعادل',
    'be_trigger_label':              '🎯 تفعيل نقطة التعادل %',
    'prompt_be_trigger':             'أدخل نسبة تفعيل نقطة التعادل (مثال: 1.0):',
    'prompt_long_be_trigger':        '📈 LONG تفعيل نقطة التعادل %\n\nأدخل نسبة الربح لنقل وقف الخسارة إلى الدخول:',
    'prompt_short_be_trigger':       '📉 SHORT تفعيل نقطة التعادل %\n\nأدخل نسبة الربح لنقل وقف الخسارة إلى الدخول:',
    'param_be_trigger':              '🎯 تفعيل نقطة التعادل %',
    'be_moved_to_entry':             '🔒 {symbol}: تم نقل وقف الخسارة إلى نقطة التعادل @ {entry}',
    'be_status_enabled':             '✅ نقطة التعادل: {trigger}%',
    'be_status_disabled':            '❌ نقطة التعادل: معطل',

    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ جني أرباح جزئي',
    'partial_tp_status_enabled':     '✅ جني الأرباح الجزئي مفعل',
    'partial_tp_status_disabled':    '❌ جني الأرباح الجزئي معطل',
    'partial_tp_step1_menu':         '✂️ *جني أرباح جزئي - الخطوة 1*\n\nإغلاق {close}% من المركز عند ربح +{trigger}%\n\n_اختر المعامل:_',
    'partial_tp_step2_menu':         '✂️ *جني أرباح جزئي - الخطوة 2*\n\nإغلاق {close}% من المركز عند ربح +{trigger}%\n\n_اختر المعامل:_',
    'trigger_pct':                   'التفعيل',
    'close_pct':                     'الإغلاق',
    'prompt_long_ptp_1_trigger':     '📈 LONG الخطوة 1: نسبة التفعيل\n\nأدخل نسبة الربح لإغلاق الجزء الأول:',
    'prompt_long_ptp_1_close':       '📈 LONG الخطوة 1: نسبة الإغلاق\n\nأدخل نسبة المركز للإغلاق:',
    'prompt_long_ptp_2_trigger':     '📈 LONG الخطوة 2: نسبة التفعيل\n\nأدخل نسبة الربح لإغلاق الجزء الثاني:',
    'prompt_long_ptp_2_close':       '📈 LONG الخطوة 2: نسبة الإغلاق\n\nأدخل نسبة المركز للإغلاق:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT الخطوة 1: نسبة التفعيل\n\nأدخل نسبة الربح لإغلاق الجزء الأول:',
    'prompt_short_ptp_1_close':      '📉 SHORT الخطوة 1: نسبة الإغلاق\n\nأدخل نسبة المركز للإغلاق:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT الخطوة 2: نسبة التفعيل\n\nأدخل نسبة الربح لإغلاق الجزء الثاني:',
    'prompt_short_ptp_2_close':      '📉 SHORT الخطوة 2: نسبة الإغلاق\n\nأدخل نسبة المركز للإغلاق:',
    'partial_tp_executed':           '✂️ {symbol}: تم إغلاق {close}% عند ربح +{trigger}%',

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
    'param_leverage': '⚡ الرافعة',
    'prompt_leverage': 'أدخل الرافعة (1-100):',
    'auto_default': 'تلقائي',

    # Enliko AI
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

💸 كل دقيقة بدون Enliko = فرص ضائعة
⏰ الأسواق لا تنتظر. وأنت أيضاً.

👉 /subscribe — <i>افتح ميزتك الفريدة الآن</i>''',
    'no_license_trading': '''🚨 <b>التداول مقفل</b>

⚠️ 847 متداولاً يكسبون الآن مع Enliko.

❌ التداول اليدوي = أخطاء عاطفية
✅ Enliko = دقة الذكاء الاصطناعي الباردة

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
✅ جميع الاستراتيجيات الـ5: OI, RSI+BB, Scryptomera, Scalper, Enliko
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
❌ Enliko, Fibonacci, Spot — Premium فقط
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
    'btn_pay_elc': '◈ Enliko Coin (ELC)',
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
    'btn_check_again': '🔄 تحقق مرة أخرى',
    'payment_session_expired': '❌ انتهت جلسة الدفع. يرجى البدء من جديد.',
    'payment_ton_not_configured': '❌ مدفوعات TON غير مهيأة.',
    'payment_verifying': '⏳ جارٍ التحقق من الدفع...',
    'stats_fibonacci': '📐 فيبوناتشي',

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

    'spot_freq_hourly': '⏰ كل ساعة',

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
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 الطرفية',
    'exchange_mode_activated_bybit': '🟠 *تم تفعيل وضع Bybit*',
    'exchange_mode_activated_hl': '🔷 *تم تفعيل وضع HyperLiquid*',
    'error_processing_request': '⚠️ خطأ في معالجة الطلب',
    'unauthorized_admin': '❌ غير مصرح. هذا الأمر للمسؤول فقط.',
    'error_loading_dashboard': '❌ خطأ في تحميل لوحة التحكم.',
    'unauthorized': '❌ غير مصرح.',
    'processing_blockchain': '⏳ جاري معالجة معاملة البلوكتشين...',
    'verifying_payment': '⏳ جاري التحقق من الدفع على بلوكتشين TON...',
    'no_wallet_configured': '❌ لم يتم تكوين المحفظة.',
    'use_start_menu': 'استخدم /start للعودة إلى القائمة الرئيسية.',

    # 2FA تأكيد تسجيل الدخول
    'login_approved': '✅ تمت الموافقة على تسجيل الدخول!\n\nيمكنك الآن المتابعة في المتصفح.',
    'login_denied': '❌ تم رفض تسجيل الدخول.\n\nإذا لم تكن أنت، راجع إعدادات الأمان.',
    'login_expired': '⏰ انتهت صلاحية التأكيد. حاول مرة أخرى.',
    'login_error': '⚠️ خطأ في المعالجة. حاول لاحقاً.',

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
    'wallet_deposit_desc': 'Send ELC tokens to:\n\n`{address}`',
    'wallet_history_item': '{type_emoji} {type}: {amount:+.2f} ELC\n   {date}',

}
