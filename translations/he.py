# -*- coding: utf-8 -*-
"""
Enliko Trading Tools — Hebrew Translations (עברית)
Version: 4.0.0 | Updated: 28 January 2026
LEGAL: Educational platform, not financial advice.
RTL Language: Right-to-Left text direction
"""

TEXTS = {
    # Common UI
    'loader': '⏳ טוען...',
    # =====================================================
    # LEGAL DISCLAIMERS (הצהרות משפטיות)
    # =====================================================
    
    'disclaimer_trading': (
        '⚠️ *הצהרה חשובה*\n\n'
        'פלטפורמה זו מספקת כלים חינוכיים ללימוד שוקי המטבעות הקריפטוגרפיים.\n'
        'זה לא:\n'
        '• ייעוץ פיננסי\n'
        '• המלצת השקעה\n'
        '• מערכת רווח מובטח\n\n'
        'מסחר במטבעות קריפטוגרפיים כרוך בסיכון משמעותי להפסד. '
        'אתה עלול להפסיד חלק מההשקעה שלך או את כולה. '
        'סחור רק בכספים שאתה יכול להרשות לעצמך להפסיד.\n\n'
        'ביצועים בעבר אינם מבטיחים תוצאות עתידיות.'
    ),
    
    'disclaimer_short': '⚠️ _כלים חינוכיים בלבד. לא ייעוץ פיננסי. מסחר כרוך בסיכון._',
    
    'disclaimer_execution': (
        '⚠️ בהמשך, אתה מאשר:\n'
        '• אתה אחראי לכל החלטות המסחר\n'
        '• זהו כלי חינוכי, לא ייעוץ פיננסי\n'
        '• אתה מבין את הסיכונים במסחר מטבעות קריפטו\n'
        '• ביצועים בעבר אינם מבטיחים תוצאות עתידיות'
    ),
    
    # Welcome - Updated with legal positioning
    'welcome': (
        '📊 *ברוכים הבאים ל-Enliko Trading Tools*\n\n'
        '🎯 פלטפורמה חינוכית:\n'
        '• מעקב וניתוח תיק השקעות\n'
        '• בדיקת אסטרטגיות\n'
        '• הדמיית נתוני שוק\n'
        '• כלי ניהול סיכונים\n\n'
        '⚠️ _למטרות חינוכיות בלבד. לא ייעוץ פיננסי._\n'
        '_מסחר כרוך בסיכון משמעותי להפסד._'
    ),
    
    'welcome_back': (
        '📊 *Enliko Trading Tools*\n\n'
        '⚠️ _פלטפורמה חינוכית. לא ייעוץ פיננסי._'
    ),
    
    # Legacy keys
    
    # ═══════════════════════════════════════════════════════════════════
    # MODERN MENU BUTTONS - Stylish & Persuasive
    # ═══════════════════════════════════════════════════════════════════
    'button_orders':               '📊 הזמנות',
    'button_positions':            '🎯 פוזיציות',
    'button_history':              '📜 היסטוריה',
    'button_api_keys':             '🔑 מפתחות API',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_settings':             '⚙️ הגדרות',

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
    'positions_header':            '📊 הפוזיציות הפתוחות שלך:',

    # Position management (inline)
    'btn_close_position':          'סגור פוזיציה',
    'btn_cancel':                  '❌ ביטול',
    'btn_back':                    '🔙 חזרה',
    'position_already_closed':     'פוזיציה כבר נסגרה',
    'position_closed_success':     'פוזיציה נסגרה',
    'position_close_error':        'שגיאה בסגירה',

    # % per trade

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 הוראות Limit בלבד: {state}',
    'feature_limit_only':          'Limit בלבד',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Enliko אינדיקטורים*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. מגמה אדפטיבית',
    'indicator_4':                 '4. רגרסיה דינמית',

    # Support
    'support_prompt':              '✉️ צריך עזרה? לחץ למטה:',
    'support_button':              'צור קשר עם התמיכה',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 אין פוזיציות פתוחות',
    'update_tpsl_prompt':          'הזן SYMBOL TP SL, למשל:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ פורמט לא תקין. השתמש: SYMBOL TP SL\nלדוגמה: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'הזן את מפתח ה-API של Bybit:',
    'api_saved':                   '✅ מפתח API נשמר',
    'enter_secret':                'הזן את ה-Secret של Bybit API:',
    'secret_saved':                '✅ ה-Secret נשמר',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ הזן ערך TP%',
    'tp_set_success':              '✅ TP% נקבע: {pct}%',
    'enter_sl':                    '❌ הזן ערך SL%',
    'sl_set_success':              '✅ SL% נקבע: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: דורש 4 פרמטרים (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: דורש 3 פרמטרים (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE חייב להיות LONG או SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ מפתח/סוד API לא הוגדרו',
    'bybit_invalid_response':      '❌ תגובה לא תקינה מ-Bybit',
    'bybit_error':                 '❌ שגיאת Bybit {path}: {data}',

    # Auto notifications - BLACK RHETORIC: Excitement & Celebration
    'new_position': (
        '🚀🔥 <b>פוזיציה חדשה נפתחה!</b>\n'
        '• {symbol} @ {entry:.6f}\n'
        '• גודל: {size}\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>ה-AI עובד בשבילך! 🤖</i>'
    ),
    'sl_auto_set':                 '🛑 SL הוגדר אוטומטית: {price:.6f}',
    'auto_close_position':         '⏱ פוזיציה {symbol} (TF={tf}) פתוחה > {tf} ומפסידה, נסגרה אוטומטית.',
    'position_closed': (
        '🎉 <b>פוזיציה נסגרה!</b> {symbol}\n'
        '• סיבה: <b>{reason}</b>\n'
        '• אסטרטגיה: `{strategy}`\n'
        '• כניסה: `{entry:.8f}`\n'
        '• יציאה: `{exit:.8f}`\n'
        '{pnl_emoji} <b>PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`</b>\n'
        '📍 {exchange} • {market_type}'
    ),

    # Entries & errors - פורמט אחיד עם מידע מלא
    'oi_limit_entry':              '📉 *OI כניסת Limit*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ שגיאת OI Limit: {msg}',
    'oi_market_entry':             '📉 *OI כניסת Market*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ שגיאת OI Market: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB כניסת Limit*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB כניסת Market*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• כמות: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ שגיאת RSI+BB Market: {msg}',

    'oi_analysis':                 '📊 *ניתוח OI עבור {symbol}* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera כניסת Limit*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ שגיאת Scryptomera Limit: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera כניסת Market*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ שגיאת Scryptomera Market: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>יתרה לא מספקת!</b>\n\n💰 אין מספיק כספים בחשבון {account_type} שלך כדי לפתוח פוזיציה זו.\n\n<b>פתרונות:</b>\n• טען מחדש את היתרה\n• הקטן את גודל הפוזיציה (% לעסקה)\n• הורד את המינוף\n• סגור חלק מהפוזיציות הפתוחות',
    'insufficient_balance_error_extended': '❌ <b>יתרה לא מספקת!</b>\n\n📊 אסטרטגיה: <b>{strategy}</b>\n🪙 סמל: <b>{symbol}</b> {side}\n\n💰 אין מספיק כספים בחשבון {account_type}.\n\n<b>פתרונות:</b>\n• טען מחדש את היתרה\n• הקטן את גודל הפוזיציה (% לעסקה)\n• הורד מינוף\n• סגור חלק מהפוזיציות',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>מינוף גבוה מדי!</b>\n\n⚙️ המינוף שהוגדר חורג מהמקסימום המותר עבור סמל זה.\n\n<b>מקסימום מותר:</b> {max_leverage}x\n\n<b>פתרון:</b> עבור להגדרות האסטרטגיה והפחת את המינוף.',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>חריגה ממגבלת פוזיציה!</b>\n\n📊 אסטרטגיה: <b>{strategy}</b>\n🪙 סמל: <b>{symbol}</b>\n\n⚠️ הפוזיציה שלך תחרוג מהמגבלה המקסימלית.\n\n<b>פתרונות:</b>\n• הפחת מינוף\n• הקטן גודל פוזיציה\n• סגור חלק מהפוזיציות',
    

    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper כניסת Limit*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ שגיאת Scalper Limit: {msg}',
    'scalper_market_entry':        '⚡ *Scalper כניסת Market*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ שגיאת Scalper Market: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko כניסת Limit*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ שגיאת Enliko Limit: {msg}',
    'elcaro_market_entry':         '🔥 *Enliko כניסת Market*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ שגיאת Enliko Market: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci כניסת Limit*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ שגיאת Fibonacci Limit: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci כניסת Market*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ שגיאת Fibonacci Market: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 פאנל מנהל:',
    'admin_pause':                 '⏸️ מסחר והתראות הושהו לכולם.',
    'admin_resume':                '▶️ מסחר והתראות חודשו לכולם.',
    'admin_closed':                '✅ נסגרו בסה״כ {count} {type}.',
    'admin_canceled_limits':       '✅ בוטלו {count} הוראות Limit.',

    # Coin groups
    'select_coin_group':           'בחר קבוצת מטבעות:',
    'group_all':                   'ALL',
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ קבוצת מטבעות הוגדרה: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *ניתוח RSI+BB*\n'
        '• מחיר: `{price:.6f}`\n'
        '• RSI: `{rsi:.1f}` ({zone})\n'
        '• BB עליון: `{bb_hi:.4f}`\n'
        '• BB תחתון: `{bb_lo:.4f}`\n\n'
        '*כניסת MARKET {side} לפי RSI+BB*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           'מכירות יתר (<30)',
    'rsi_zone_overbought':         'קניות יתר (>70)',
    'rsi_zone_neutral':            'נייטרלי (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ TP/SL לא תקין ל-LONG.\n'
        'מחיר נוכחי: {current:.2f}\n'
        'מצופה: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ TP/SL לא תקין ל-SHORT.\n'
        'מחיר נוכחי: {current:.2f}\n'
        'מצופה: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 אין לך פוזיציה פתוחה על {symbol}',
    'tpsl_set_success':            '✅ TP={tp:.2f} ו-SL={sl:.2f} הוגדרו עבור {symbol}',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 שפה',
    'select_language':             '🌍 בחר שפה:',
    'language_set':                '✅ השפה נקבעה:',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'מצב עצירה: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ הוראת Limit ל-{symbol} מולאה @ {price}',
    'limit_order_cancelled':       '⚠️ הוראת Limit ל-{symbol} (ID: {order_id}) בוטלה.',
    'fixed_sl_tp':                 '✅ {symbol}: SL ב-{sl}, TP ב-{tp}',
    'tp_part':                     ', TP נקבע ב-{tp_price}',
    'sl_tp_set':                   '✅ {symbol}: SL ב-{sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL ב-{sl_price}',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP אותחל ב-{sl}/{tp}',
    'sl_breakeven':                '🔄 {symbol}: SL הועבר ל-BE ב-{entry}',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP עודכן ל-{sl}/{tp}',

    'position_closed_error': (
        '⚠️ פוזיציה {symbol} נסגרה אך הלוג נכשל: {error}\n'
        'אנא פנה לתמיכה.'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  '% קבוע',

    # System notices
    'db_quarantine_notice':        '⚠️ הלוגים מושהים זמנית. מצב שקט הופעל לשעה.',

    # Fallback
    'fallback':                    '❓ השתמש בכפתורי התפריט.',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 נחסמת.',
    'invite_only': '🔒 גישה בהזמנה בלבד. המתן לאישור מנהל.',
    'need_terms': '⚠️ אנא קבל תחילה את התנאים: /terms',
    'please_confirm': 'אנא אשר:',
    'terms_ok': '✅ תודה! התנאים אושרו.',
    'terms_declined': '❌ דחית את התנאים. הגישה נסגרה. אפשר לחזור עם /terms.',
    'usage_approve': 'שימוש: /approve <user_id>',
    'usage_ban': 'שימוש: /ban <user_id>',
    'not_allowed': 'לא מורשה',
    'bad_payload': 'נתונים שגויים',
    'unknown_action': 'פעולה לא ידועה',

    'title': 'משתמש חדש',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• מזהה: <code>{uid}</code>\n'
        '• שם: {name}\n'
        '• משתמש: {uname}\n'
        '• שפה: {lang}\n'
        '• מותר: {allowed}  חסום: {banned}\n'
    ),
    'btn_approve': '✅ אישור',
    'btn_ban': '⛔️ חסום',
    'admin_notify_fail': 'כשל בהודעה למנהל: {e}',
    'moderation_approved': '✅ אושר: {target}',
    'moderation_banned': '⛔️ נחסם: {target}',
    'approved_user_dm': '✅ הגישה אושרה. לחץ /start.',
    'banned_user_dm': '🚫 נחסמת.',

    'users_not_found': '😕 לא נמצאו משתמשים.',
    'users_page_info': '📄 עמוד {page}/{pages} — סה״כ: {total}',
    'user_card_html': (
        '<b>👤 משתמש</b>\n'
        '• מזהה: <code>{uid}</code>\n'
        '• שם: {full_name}\n'
        '• משתמש: {uname}\n'
        '• שפה: <code>{lang}</code>\n'
        '• מותר: {allowed}\n'
        '• חסום: {banned}\n'
        '• תנאים: {terms}\n'
        '• % לעסקה: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 רשימה שחורה',
    'btn_delete_user': '🗑 מחיקה מה-DB',
    'btn_prev': '⬅️ הקודם',
    'btn_next': '➡️ הבא',
    'nav_caption': '🧭 ניווט:',
    'bad_page': 'עמוד לא תקין.',
    'admin_user_delete_fail': '❌ כשל במחיקת {target}: {error}',
    'admin_user_deleted': '🗑 המשתמש {target} נמחק מה-DB.',
    'user_access_approved': '✅ הגישה אושרה. לחץ /start.',

    'admin_pause_all': '⏸️ השהה לכולם',
    'admin_resume_all': '▶️ המשך',
    'admin_close_longs': '🔒 סגור את כל LONG',
    'admin_close_shorts': '🔓 סגור את כל SHORT',
    'admin_cancel_limits': '❌ מחק הוראות לימיט',
    'admin_users': '👥 משתמשים',
    'admin_pause_notice': '⏸️ מסחר והתראות הושהו לכולם.',
    'admin_resume_notice': '▶️ מסחר והתראות חזרו לכולם.',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ נסגרו סה״כ {count} {type}.',
    'admin_canceled_limits_total': '✅ בוטלו {count} הוראות לימיט.',

    'terms_btn_accept': '✅ מאשר',
    'terms_btn_decline': '❌ דוחה',

    'emoji_long': '🟢',
    'emoji_short': '🔴',
    'emoji_neutral': '⚪️',

    # Scalper Strategy

    # API Settings
    'api_key_set':                 '✅ Set',
    'api_test_success':            'החיבור הצליח!',
    'api_test_failed':             'החיבור נכשל',
    'balance_equity':              'הון',
    'balance_available':           'זמין',
    'api_missing_notice':          '⚠️ לא הגדרת מפתחות API של הבורסה. אנא הוסף את מפתח ה-API והסוד שלך בהגדרות (כפתורי 🔑 API ו-🔒 Secret), אחרת הבוט לא יכול לסחור עבורך.',
    'elcaro_ai_info':              '🤖 *מסחר מונע בינה מלאכותית*',

    # Spot Trading
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_balance':                '💰 Spot Balance: {balance}',

    # Strategy trading mode

    # Enliko (Heatmap)

    # Fibonacci (Fibonacci Extension)

    # Strategy Settings
    'button_strategy_settings':      '⚙️ הגדרות אסטרטגיות',
    'strategy_settings_header':      '⚙️ *הגדרות אסטרטגיות*',
    'strategy_param_header':         '⚙️ *הגדרות {name}*',
    'using_global':                  'הגדרות גלובליות',
    'global_default':                'גלובלי',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Enliko',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ הגדרות DCA',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA שלב 1 %',
    'dca_leg2':                      '📉 DCA שלב 2 %',
    'param_percent':                 '📊 כניסה %',
    'param_sl':                      '🔻 סטופ-לוס %',
    'param_tp':                      '🔺 טייק-פרופיט %',
    'param_reset':                   '🔄 אפס לגלובלי',
    'btn_close':                     '❌ סגור',
    'prompt_entry_pct':              'הזן % כניסה (סיכון לעסקה):',
    'prompt_sl_pct':                 'הזן % סטופ-לוס:',
    'prompt_tp_pct':                 'הזן % טייק-פרופיט:',
    'prompt_atr_periods':            'הזן תקופות ATR (למשל: 7):',
    'prompt_atr_mult':               'הזן מכפיל ATR ל-SL נגרר (למשל: 1.0):',
    'prompt_atr_trigger':            'הזן % הפעלת ATR (למשל: 2.0):',
    'prompt_dca_leg1':               'הזן % DCA שלב 1 (למשל: 10):',
    'prompt_dca_leg2':               'הזן % DCA שלב 2 (למשל: 25):',
    'settings_reset':                'ההגדרות אופסו לגלובליות',
    'strat_setting_saved':           '✅ {name} {param} הוגדר ל-{value}',
    'dca_setting_saved':             '✅ DCA {leg} הוגדר ל-{value}%',
    'invalid_number':                '❌ מספר לא חוקי. הזן ערך בין 0 ל-100.',
    'dca_10pct':                     'DCA −{pct}%: הוספה {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: הוספה {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: שלב1=-{dca1}%, שלב2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 תקופות ATR',
    'param_atr_mult':                '📉 מכפיל ATR (צעד SL)',
    'param_atr_trigger':             '🎯 הפעלת ATR %',

    # Break-Even settings UI
    'be_settings_header':            '🔒 *הגדרות נקודת איזון*',
    'be_settings_desc':              '_הזז עצירת הפסד למחיר כניסה כאשר הרווח מגיע לאחוז ההפעלה_',
    'be_enabled_label':              '🔒 נקודת איזון',
    'be_trigger_label':              '🎯 הפעלת נקודת איזון %',
    'prompt_be_trigger':             'הזן אחוז הפעלת נקודת איזון (לדוגמה: 1.0):',
    'prompt_long_be_trigger':        '📈 LONG הפעלת נקודת איזון %\n\nהזן אחוז רווח להזזת עצירת הפסד לכניסה:',
    'prompt_short_be_trigger':       '📉 SHORT הפעלת נקודת איזון %\n\nהזן אחוז רווח להזזת עצירת הפסד לכניסה:',
    'param_be_trigger':              '🎯 הפעלת נקודת איזון %',
    'be_moved_to_entry':             '🔒 {symbol}: עצירת הפסד הועברה לנקודת איזון @ {entry}',
    'be_status_enabled':             '✅ נקודת איזון: {trigger}%',
    'be_status_disabled':            '❌ נקודת איזון: כבוי',

    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ לקיחת רווח חלקית',
    'partial_tp_status_enabled':     '✅ לקיחת רווח חלקית מופעלת',
    'partial_tp_status_disabled':    '❌ לקיחת רווח חלקית מושבתת',
    'partial_tp_step1_menu':         '✂️ *לקיחת רווח חלקית - שלב 1*\n\nסגור {close}% מהפוזיציה ברווח +{trigger}%\n\n_בחר פרמטר:_',
    'partial_tp_step2_menu':         '✂️ *לקיחת רווח חלקית - שלב 2*\n\nסגור {close}% מהפוזיציה ברווח +{trigger}%\n\n_בחר פרמטר:_',
    'trigger_pct':                   'הפעלה',
    'close_pct':                     'סגירה',
    'prompt_long_ptp_1_trigger':     '📈 LONG שלב 1: אחוז הפעלה\n\nהזן אחוז רווח לסגירת חלק ראשון:',
    'prompt_long_ptp_1_close':       '📈 LONG שלב 1: אחוז סגירה\n\nהזן אחוז פוזיציה לסגירה:',
    'prompt_long_ptp_2_trigger':     '📈 LONG שלב 2: אחוז הפעלה\n\nהזן אחוז רווח לסגירת חלק שני:',
    'prompt_long_ptp_2_close':       '📈 LONG שלב 2: אחוז סגירה\n\nהזן אחוז פוזיציה לסגירה:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT שלב 1: אחוז הפעלה\n\nהזן אחוז רווח לסגירת חלק ראשון:',
    'prompt_short_ptp_1_close':      '📉 SHORT שלב 1: אחוז סגירה\n\nהזן אחוז פוזיציה לסגירה:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT שלב 2: אחוז הפעלה\n\nהזן אחוז רווח לסגירת חלק שני:',
    'prompt_short_ptp_2_close':      '📉 SHORT שלב 2: אחוז סגירה\n\nהזן אחוז פוזיציה לסגירה:',
    'partial_tp_executed':           '✂️ {symbol}: נסגר {close}% ברווח +{trigger}%',

    # Hardcoded strings fix
    'terms_unavailable':             'תנאי השימוש אינם זמינים. אנא פנה למנהל.',
    'terms_confirm_prompt':          'אנא אשר:',
    'your_id':                       'המזהה שלך: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'שגיאה: {msg}',
    'error_fetch_balance':           '❌ שגיאה בהבאת יתרה: {error}',
    'error_fetch_orders':            '❌ שגיאה בהבאת הזמנות: {error}',
    'error_occurred':                '❌ שגיאה: {error}',

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
    'stats_strategy_settings':       'הגדרות אסטרטגיה',
    'settings_entry_pct':            'כניסה',
    'settings_leverage':             'מינוף',
    'settings_trading_mode':         'מצב',
    'settings_direction':            'כיוון',
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
    'param_leverage': '⚡ מינוף',
    'prompt_leverage': 'הזן מינוף (1-100):',
    'auto_default': 'אוטומטי',

    # Enliko AI
    'elcaro_ai_desc': '_כל הפרמטרים מנותחים אוטומטית מאותות AI:_',

    # Scalper entries

    # Scryptomera feature
    

    # Limit Ladder
    'limit_ladder': '📉 סולם לימיט',
    'limit_ladder_header': '📉 *הגדרות סולם לימיט*',
    'limit_ladder_settings': '⚙️ הגדרות סולם',
    'ladder_count': 'מספר הזמנות',
    'ladder_info': 'הזמנות לימיט מתחת לכניסה ל-DCA. לכל הזמנה יש % מרחק מהכניסה ו-% מהפיקדון.',
    'prompt_ladder_pct_entry': '📉 הזן % מתחת למחיר הכניסה להזמנה {idx}:',
    'prompt_ladder_pct_deposit': '💰 הזן % מהפיקדון להזמנה {idx}:',
    'ladder_order_saved': '✅ הזמנה {idx} נשמרה: -{pct_entry}% @ {pct_deposit}% פיקדון',
    'ladder_orders_placed': '📉 הוצבו {count} הזמנות לימיט עבור {symbol}',
    
    # Spot Trading Mode
    
    # Stats PnL
    'stats_realized_pnl': 'ממומש',
    'stats_unrealized_pnl': 'לא ממומש',
    'stats_combined_pnl': 'משולב',
    'stats_spot': '💹 ספוט',
    'stats_spot_title': 'סטטיסטיקות Spot DCA',
    'stats_spot_config': 'הגדרות',
    'stats_spot_holdings': 'אחזקות',
    'stats_spot_summary': 'סיכום',
    'stats_spot_current_value': 'ערך נוכחי',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    # License status messages - BLACK RHETORIC: Loss Aversion + FOMO
    'no_license': '''🚨 <b>גישה נדחתה</b>

בזמן שאתה מהסס, <b>847 סוחרים</b> כבר מרוויחים.

💸 כל דקה ללא Enliko = הזדמנויות שהוחמצו
⏰ השווקים לא מחכים. גם אתה לא צריך.

👉 /subscribe — <i>פתח את היתרון שלך עכשיו</i>''',
    'no_license_trading': '''🚨 <b>המסחר נעול</b>

⚠️ 847 סוחרים מרוויחים עכשיו עם Enliko.

❌ מסחר ידני = טעויות רגשיות
✅ Enliko = דיוק AI קר

<i>תפסיק לצפות. תתחיל להרוויח.</i>

👉 /subscribe — <b>הצטרף ל-847+ סוחרים חכמים</b>''',
    'license_required': '''🔒 <b>תכונה PREMIUM</b>

זה דורש מנוי {required} — <i>משמש את 3% הסוחרים המובילים</i>.

🎯 הצלחה משאירה רמזים. עקוב אחרי המנצחים.

👉 /subscribe — <b>שדרג עכשיו</b>''',
    'trial_demo_only': '''⚠️ <b>מצב דמו ללימוד, לא להרווחה.</b>

רווחים אמיתיים דורשים גישה אמיתית.

🎁 טעמת את הכוח. עכשיו <b>החזק בו</b>.

👉 /subscribe — <b>פתח מסחר אמיתי</b>''',
    'basic_strategy_limit': '''⚠️ <b>Basic = תוצאות Basic</b>

אתה מוגבל ל-: {strategies}

המקצוענים משתמשים ב<b>כל</b> האסטרטגיות. לכן הם מקצוענים.

👉 /subscribe — <b>לך ל-Premium. היה מקצועני.</b>''',
    
    'subscribe_menu_header': '👑 *גישת VIP למועדון סוחרים מובילים*',
    'subscribe_menu_info': 'בחר תוכנית לפתיחת תכונות מסחר:',
    'btn_premium': '💎 פרימיום',
    'btn_basic': '🥈 בסיסי', 
    'btn_trial': '🎁 ניסיון (חינם)',
    'btn_enter_promo': '🎟 קוד פרומו',
    'btn_my_subscription': '📋 המנוי שלי',
    
    'premium_title': '� *PREMIUM — הבחירה של המנצחים*',
    'premium_desc': '''✅ גישה מלאה לכל התכונות
✅ כל 5 האסטרטגיות: OI, RSI+BB, Scryptomera, Scalper, Enliko
✅ מסחר אמיתי + דמו
✅ תמיכה עדיפה
✅ SL/TP דינמי מבוסס ATR
✅ סולם לימיט DCA
✅ כל העדכונים העתידיים''',
    'premium_1m': '💎 חודש 1 — {price} ELC',
    'premium_3m': '💎 3 חודשים — {price} ELC (-10%)',
    'premium_6m': '💎 6 חודשים — {price} ELC (-20%)',
    'premium_12m': '💎 12 חודשים — {price} ELC (-30%)',
    
    'basic_title': '🥈 *תוכנית BASIC*',
    'basic_desc': '''✅ גישה מלאה לחשבון דמו
✅ חשבון אמיתי: OI, RSI+BB, Scryptomera, Scalper
❌ Enliko, Fibonacci, Spot — Premium בלבד
✅ תמיכה רגילה
✅ SL/TP דינמי מבוסס ATR''',
    'basic_1m': '🥈 חודש 1 — {price} ELC',
    
    'trial_title': '🎁 *ניסיון חינם — הצעה מוגבלת!*',
    'trial_desc': '''✅ גישה מלאה לחשבון דמו
✅ כל 5 האסטרטגיות בדמו
❌ מסחר אמיתי לא זמין
⏰ משך: 7 ימים
🎁 פעם אחת בלבד''',
    'trial_activate': '🎁 הפעל ניסיון חינם',
    'trial_already_used': '⚠️ כבר השתמשת בניסיון החינמי.',
    'trial_activated': '🎉 ניסיון הופעל! יש לך 7 ימים של גישה מלאה לדמו.',
    
    'payment_select_method': '💳 *בחר אמצעי תשלום*',
    'btn_pay_elc': '◈ Enliko Coin (ELC)',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': ' תשלום דרך ELC',
    'payment_elc_desc': 'יחויבו {amount} ELC עבור {plan} ({period}).',
    'payment_ton_title': '💎 תשלום דרך TON',
    'payment_ton_desc': '''שלח בדיוק *{amount} TON* ל:

`{wallet}`

אחרי התשלום, לחץ על הכפתור למטה לאימות.''',
    'btn_verify_ton': '✅ שילמתי — אמת',
    'payment_processing': '⏳ מעבד תשלום...',
    'payment_success': '🎉 התשלום הצליח!\n\n{plan} הופעל עד {expires}.',
    'payment_failed': '❌ התשלום נכשל: {error}',
    
    'my_subscription_header': '📋 *המנוי שלי*',
    'my_subscription_active': '''📋 *תוכנית נוכחית:* {plan}
⏰ *פג תוקף:* {expires}
📅 *ימים שנותרו:* {days}''',
    'my_subscription_none': '❌ אין מנוי פעיל.\n\nהשתמש ב-/subscribe כדי לרכוש תוכנית.',
    'my_subscription_history': '📜 *היסטוריית תשלומים:*',
    'subscription_expiring_soon': '⚠️ המנוי שלך {plan} פג תוקף בעוד {days} ימים!\n\nחדש עכשיו: /subscribe',
    
    'promo_enter': '🎟 הכנס קוד פרומו:',
    'promo_success': '🎉 קוד פרומו הוחל!\n\n{plan} הופעל ל-{days} ימים.',
    'promo_invalid': '❌ קוד פרומו לא תקין.',
    'promo_expired': '❌ קוד פרומו זה פג תוקף.',
    'promo_used': '❌ קוד פרומו זה כבר נוצל.',
    'promo_already_used': '❌ כבר השתמשת בקוד פרומו זה.',
    
    'admin_license_menu': '🔑 *ניהול רישיונות*',
    'admin_btn_grant_license': '🎁 הענק רישיון',
    'admin_btn_view_licenses': '📋 צפה ברישיונות',
    'admin_btn_create_promo': '🎟 צור פרומו',
    'admin_btn_view_promos': '📋 צפה בפרומו',
    'admin_btn_expiring_soon': '⚠️ פג תוקף בקרוב',
    'admin_grant_select_type': 'בחר סוג רישיון:',
    'admin_grant_select_period': 'בחר תקופה:',
    'admin_grant_enter_user': 'הכנס מזהה משתמש:',
    'admin_license_granted': '✅ {plan} הוענק למשתמש {uid} ל-{days} ימים.',
    'admin_license_extended': '✅ רישיון הוארך ב-{days} ימים למשתמש {uid}.',
    'admin_license_revoked': '✅ רישיון בוטל למשתמש {uid}.',
    'admin_promo_created': '✅ קוד פרומו נוצר: {code}\nסוג: {type}\nימים: {days}\nשימושים מקסימלי: {max}',

    'admin_users_management': '👥 משתמשים',
    'admin_licenses': '🔑 רישיונות',
    'admin_search_user': '🔍 מצא משתמש',
    'admin_users_menu': '👥 *ניהול משתמשים*\n\nבחר פילטר או חפש:',
    'admin_all_users': '👥 כל המשתמשים',
    'admin_active_users': '✅ פעילים',
    'admin_banned_users': '🚫 חסומים',
    'admin_no_license': '❌ ללא רישיון',
    'admin_no_users_found': 'לא נמצאו משתמשים.',
    'admin_enter_user_id': '🔍 הכנס מזהה משתמש לחיפוש:',
    'admin_user_found': '✅ משתמש {uid} נמצא!',
    'admin_user_not_found': '❌ משתמש {uid} לא נמצא.',
    'admin_invalid_user_id': '❌ מזהה משתמש לא תקין. הכנס מספר.',
    'admin_view_card': '👤 צפה בכרטיס',
    
    'admin_user_card': '''👤 *כרטיס משתמש*

📋 *מזהה:* `{uid}`
{status_emoji} *סטטוס:* {status}
📝 *תנאים:* {terms}

{license_emoji} *רישיון:* {license_type}
📅 *פג תוקף:* {license_expires}
⏳ *ימים שנותרו:* {days_left}

🌐 *שפה:* {lang}
📊 *מצב מסחר:* {trading_mode}
💰 *% לעסקה:* {percent}%
🪙 *מטבעות:* {coins}

🔌 *מפתחות API:*
  דמו: {demo_api}
  אמיתי: {real_api}

📈 *אסטרטגיות:* {strategies}

📊 *סטטיסטיקה:*
  פוזיציות: {positions}
  עסקאות: {trades}
  רווח/הפסד: {pnl}
  אחוז הצלחה: {winrate}%

💳 *תשלומים:*
  סה"כ: {payments_count}
  ELC: {total_elc}

📅 *נראה לראשונה:* {first_seen}
🕐 *נראה לאחרונה:* {last_seen}
''',
    
    'admin_btn_grant_lic': '🎁 הענק',
    'admin_btn_extend': '⏳ הארך',
    'admin_btn_revoke': '🚫 בטל',
    'admin_btn_ban': '🚫 חסום',
    'admin_btn_unban': '✅ בטל חסימה',
    'admin_btn_approve': '✅ אשר',
    'admin_btn_message': '✉️ הודעה',
    'admin_btn_delete': '🗑 מחק',
    
    'admin_user_banned': 'משתמש נחסם!',
    'admin_user_unbanned': 'משתמש בוטלה חסימתו!',
    'admin_user_approved': 'משתמש אושר!',
    'admin_confirm_delete': '⚠️ *אשר מחיקה*\n\nמשתמש {uid} יימחק לצמיתות!',
    'admin_confirm_yes': '✅ כן, מחק',
    'admin_confirm_no': '❌ ביטול',
    
    'admin_select_license_type': 'בחר סוג רישיון למשתמש {uid}:',
    'admin_select_period': 'בחר תקופה:',
    'admin_select_extend_days': 'בחר ימים להארכה למשתמש {uid}:',
    'admin_license_granted_short': 'רישיון הוענק!',
    'admin_license_extended_short': 'הוארך ב-{days} ימים!',
    'admin_license_revoked_short': 'רישיון בוטל!',
    
    'admin_enter_message': '✉️ הכנס הודעה לשליחה למשתמש {uid}:',
    'admin_message_sent': '✅ הודעה נשלחה למשתמש {uid}!',
    'admin_message_failed': '❌ שליחת הודעה נכשלה: {error}',

    # Auto-synced missing keys
    'admin_all_payments': '📜 כל התשלומים',
    'admin_demo_stats': '🎮 סטטיסטיקות דמו',
    'admin_enter_user_for_report': '👤 הזן ID משתמש לדוח מפורט:',
    'admin_generating_report': '📊 מייצר דוח למשתמש {uid}...',
    'admin_global_stats': '📊 סטטיסטיקות גלובליות',
    'admin_no_payments_found': 'לא נמצאו תשלומים.',
    'admin_payments': '💳 תשלומים',
    'admin_payments_menu': '💳 *ניהול תשלומים*',
    'admin_real_stats': '💰 סטטיסטיקות אמיתיות',
    'admin_reports': '📊 דוחות',
    'admin_reports_menu': '''📊 *דוחות וניתוחים*

בחר סוג דוח:''',
    'admin_strategy_breakdown': '🎯 לפי אסטרטגיה',
    'admin_top_traders': '🏆 הסוחרים המובילים',
    'admin_user_report': '👤 דוח משתמש',
    'admin_view_report': '📊 הצג דוח',
    'admin_view_user': '👤 כרטיס משתמש',
    'btn_check_again': '🔄 בדוק שוב',
    'payment_session_expired': '❌ פג התוקף של התשלום. אנא התחל מחדש.',
    'payment_ton_not_configured': '❌ תשלומי TON אינם מוגדרים.',
    'payment_verifying': '⏳ מאמת תשלום...',
    'stats_fibonacci': '📐 פיבונאצ\'י',

    "button_hyperliquid": "🔷 HyperLiquid",
    "button_webapp": "🌐 WebApp",
    "button_switch_exchange": "🔄 Switch Exchange",
    "button_api_bybit": "🟠 Bybit API",
    "button_api_hl": "🔷 HL API",

    # HyperLiquid Strategy Settings
    "hl_settings": "HyperLiquid",
    "hl_trading_enabled": "מסחר HyperLiquid",
    "hl_reset_settings": "🔄 איפוס להגדרות Bybit",

    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ בוטל.',
    'entry_pct_range_error': '❌ אחוז כניסה חייב להיות בין 0.1 ל-100.',
    'hl_no_history': '📭 אין היסטוריית מסחר ב-HyperLiquid.',
    'hl_no_orders': '📭 אין פקודות פתוחות ב-HyperLiquid.',
    'hl_no_positions': '📭 אין פוזיציות פתוחות ב-HyperLiquid.',
    'hl_setup_cancelled': '❌ הגדרת HyperLiquid בוטלה.',
    'invalid_amount': '❌ מספר לא תקין. הזן סכום תקין.',
    'leverage_range_error': '❌ מינוף חייב להיות בין 1 ל-100.',
    'max_amount_error': '❌ סכום מקסימלי 100,000 USDT',
    'min_amount_error': '❌ סכום מינימלי 1 USDT',
    'sl_tp_range_error': '❌ אחוז SL/TP חייב להיות בין 0.1 ל-500.',

    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 הפעל DCA',
    'btn_ignore': '🔇 התעלם',
    'dca_already_enabled': '✅ ממוצע DCA כבר מופעל!\n\n📊 <b>{symbol}</b>\nהבוט יוסיף אוטומטית בירידה:\n• -10% → הוספה\n• -25% → הוספה\n\nזה עוזר לממוצע את מחיר הכניסה.',
    'dca_enable_error': '❌ שגיאה: {error}',
    'dca_enabled_for_symbol': '✅ ממוצע DCA הופעל!\n\n📊 <b>{symbol}</b>\nהבוט יוסיף אוטומטית בירידה:\n• -10% → הוספה (ממוצע)\n• -25% → הוספה (ממוצע)\n\n⚠️ DCA דורש יתרה מספקת לפקודות נוספות.',
    'deep_loss_alert': '⚠️ <b>פוזיציה בהפסד עמוק!</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 הפסד: <code>{loss_pct:.2f}%</code>\n💰 כניסה: <code>{entry}</code>\n📍 נוכחי: <code>{mark}</code>\n\n❌ לא ניתן להגדיר סטופ-לוס מעל מחיר הכניסה.\n\n<b>מה לעשות?</b>\n• <b>סגור</b> - נעל את ההפסד\n• <b>DCA</b> - ממוצע הפוזיציה\n• <b>התעלם</b> - השאר כמו שזה',
    'deep_loss_close_error': '❌ שגיאה בסגירת הפוזיציה: {error}',
    'deep_loss_closed': '✅ פוזיציה {symbol} נסגרה.\n\nההפסד ננעל. לפעמים עדיף לקבל הפסד קטן מאשר לקוות להיפוך.',
    'deep_loss_ignored': '🔇 הבנתי, פוזיציה {symbol} נשארה ללא שינוי.\n\n⚠️ זכור: בלי סטופ-לוס, הסיכון להפסדים הוא בלתי מוגבל.\nאתה יכול לסגור את הפוזיציה ידנית דרך /positions',
    'fibonacci_desc': '_כניסה, SL, TP - מרמות פיבונאצ\'י באות_',
    'fibonacci_info': '📐 *אסטרטגיית הרחבת פיבונאצ\'י*',
    'prompt_min_quality': 'הזן איכות מינימלית % (0-100):',

    # Hardcore trading phrase
    'hardcore_mode': '💀 *מצב הארדקור*: ללא רחמים, ללא חרטות. רק רווח או מוות! 🔥',

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ יתרת ELC לא מספיקה.

היתרה שלך: {balance} ELC
נדרש: {required} ELC

טען את הארנק כדי להמשיך.''',
    'wallet_address': '''📍 כתובת: `{address}`''',
    'wallet_balance': '''💰 *ארנק ELC שלך*

◈ יתרה: *{balance} ELC*
📈 בהימור: *{staked} ELC*
🎁 תגמולים ממתינים: *{rewards} ELC*

💵 ערך כולל: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« חזרה''',
    'wallet_btn_deposit': '''📥 הפקדה''',
    'wallet_btn_history': '''📋 היסטוריה''',
    'wallet_btn_stake': '''📈 הימור''',
    'wallet_btn_unstake': '''📤 ביטול הימור''',
    'wallet_btn_withdraw': '''📤 משיכה''',
    'wallet_deposit_demo': '''🎁 קבל 100 ELC (דמו)''',
    'wallet_deposit_desc': '''שלח טוקני ELC לכתובת הארנק שלך:

`{address}`

💡 *מצב דמו:* לחץ למטה לטוקני בדיקה חינם.''',
    'wallet_deposit_success': '''✅ הופקדו {amount} ELC בהצלחה!''',
    'wallet_deposit_title': '''📥 *הפקדת ELC*''',
    'wallet_history_empty': '''אין עסקאות עדיין.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *היסטוריית עסקאות*''',
    'wallet_stake_desc': '''הימר את טוקני ה-ELC שלך והרווח *12% APY*!

💰 זמין: {available} ELC
📈 כרגע בהימור: {staked} ELC
🎁 תגמולים ממתינים: {rewards} ELC

תגמולים יומיים • ביטול מיידי''',
    'wallet_stake_success': '''✅ הומרו {amount} ELC בהצלחה!''',
    'wallet_stake_title': '''📈 *הימור ELC*''',
    'wallet_title': '''◈ *ארנק ELC*''',
    'wallet_unstake_success': '''✅ נמשכו {amount} ELC + {rewards} ELC תגמולים!''',
    'wallet_withdraw_desc': '''הזן כתובת יעד וסכום:''',
    'wallet_withdraw_failed': '''❌ המשיכה נכשלה: {error}''',
    'wallet_withdraw_success': '''✅ נמשכו {amount} ELC ל-{address}''',
    'wallet_withdraw_title': '''📤 *משיכת ELC*''',

    'spot_freq_hourly': '⏰ כל שעה',

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
    'error_insufficient_balance': '💰 אין מספיק כספים בחשבונך לפתיחת פוזיציה. טען את היתרה או הקטן את גודל הפוזיציה.',
    'error_order_too_small': '📉 גודל ההזמנה קטן מדי (מינימום $5). הגדל Entry% או טען את היתרה.',
    'error_api_key_expired': '🔑 מפתח API פג תוקף או לא תקין. עדכן את מפתחות ה-API בהגדרות.',
    'error_api_key_missing': '🔑 מפתחות API לא מוגדרים. הוסף מפתחות Bybit בתפריט 🔗 API Keys.',
    'error_rate_limit': '⏳ יותר מדי בקשות. המתן דקה ונסה שוב.',
    'error_position_not_found': '📊 הפוזיציה לא נמצאה או כבר נסגרה.',
    'error_leverage_error': '⚙️ שגיאה בהגדרת המינוף. נסה להגדיר את המינוף ידנית בבורסה.',
    'error_network_error': '🌐 בעיית רשת. נסה מאוחר יותר.',
    'error_sl_tp_invalid': '⚠️ לא ניתן להגדיר SL/TP: המחיר קרוב מדי לנוכחי. יעודכן במחזור הבא.',
    'error_equity_zero': '💰 יתרת החשבון שלך אפס. טען חשבון Demo או Real כדי לסחור.',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 טרמינל',
    'exchange_mode_activated_bybit': '🟠 *מצב Bybit הופעל*',
    'exchange_mode_activated_hl': '🔷 *מצב HyperLiquid הופעל*',
    'error_processing_request': '⚠️ שגיאה בעיבוד הבקשה',
    'unauthorized_admin': '❌ לא מורשה. פקודה זו למנהל בלבד.',
    'error_loading_dashboard': '❌ שגיאה בטעינת לוח הבקרה.',
    'unauthorized': '❌ לא מורשה.',
    'processing_blockchain': '⏳ מעבד עסקת בלוקצ\'יין...',
    'verifying_payment': '⏳ מאמת תשלום בבלוקצ\'יין TON...',
    'no_wallet_configured': '❌ ארנק לא מוגדר.',
    'use_start_menu': 'השתמש ב-/start לחזרה לתפריט הראשי.',

    # 2FA אישור התחברות
    'login_approved': '✅ ההתחברות אושרה!\n\nתוכל להמשיך בדפדפן.',
    'login_denied': '❌ ההתחברות נדחתה.\n\nאם זה לא היית אתה, בדוק את הגדרות האבטחה.',
    'login_expired': '⏰ האישור פג. נסה שוב.',
    'login_error': '⚠️ שגיאת עיבוד. נסה מאוחר יותר.',

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
    'button_api_bybit': '🟠 Bybit API',
    'button_api_hl': '🔷 HL API',
    'button_help': '❓ Help',
    'button_language': '🌍 Language',
    'button_portfolio': '💼 Portfolio',
    'button_premium': '💎 Premium',
    'button_screener': '📈 Screener',
    'button_switch_exchange': '🔄 Switch Exchange',
    'button_webapp': '🌐 WebApp',
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
    "button_balance": "💎 Portfolio",
    "button_coins": "🪙 Coins",
    "button_elcaro": "🎯 Elcaro",
    "button_fibonacci": "📐 Fibonacci",
    "button_indicators": "📊 Indicators",
    "button_limit_only": "📝 Limit Only",
    "button_market": "📈 Market",
    "button_scalper": "⚡ Scalper",
    "button_scryptomera": "🔮 Scryptomera",
    "button_strategies": "🤖 AI Bots",
    "button_subscribe": "👑 PREMIUM",
    "button_support": "📞 Support",
    "button_terminal": "💻 Terminal",
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
}
