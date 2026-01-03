# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu
    'welcome':                     '👋 היי! בחר פעולה:',
    'no_strategies':               '❌ אין',
    'guide_caption':               '📚 מדריך למשתמש בוט מסחר\n\nקרא מדריך זה כדי ללמוד כיצד להגדיר אסטרטגיות ולהשתמש בבוט ביעילות.',
    'privacy_caption':             '📜 מדיניות פרטיות ותנאי שימוש\n\nאנא קרא מסמך זה בעיון.',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 סוד',
    'button_api_settings':         '🔑 API',
    'button_balance':              '💰 יתרת USDT',
    'button_orders':               '📜 ההזמנות שלי',
    'button_positions':            '📊 פוזיציות',
    'button_percent':              '🎚 % לעסקה',
    'button_coins':                '💠 קבוצת מטבעות',
    'button_market':               '📈 שוק',
    'button_manual_order':         '✋ פקודה ידנית',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ ביטול פקודה',
    'button_limit_only':           '🎯 Limit בלבד',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_settings':             '⚙️ הגדרות',
    'button_indicators':           '💡 אינדיקטורים',
    'button_support':              '🆘 תמיכה',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 מצב TP/SL עודכן ל-*{mode_text}*',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              '% קבוע',

    # Limits
    'limit_positions_exceeded':    '🚫 חרגת ממספר הפוזיציות הפתוחות ({max})',
    'limit_limit_orders_exceeded': '🚫 חרגת ממספר הוראות ה-Limit ({max})',

    # Languages
    'select_language':             'בחר שפה:',
    'language_set':                'השפה הוגדרה ל:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           'בחר סוג פקודה:',
    'limit_order_format': (
        "הזן פרמטרים לפקודת Limit כך:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "כאשר SIDE = LONG או SHORT\n"
        "דוגמה: `BTCUSDT LONG 20000 0.1`\n\n"
        "לביטול שלח ❌ ביטול פקודה"
    ),
    'market_order_format': (
        "הזן פרמטרים לפקודת Market כך:\n"
        "`SYMBOL SIDE QTY`\n"
        "כאשר SIDE = LONG או SHORT\n"
        "דוגמה: `BTCUSDT SHORT 0.1`\n\n"
        "לביטול שלח ❌ ביטול פקודה"
    ),
    'order_success':               '✅ הפקודה נוצרה בהצלחה!',
    'order_create_error':          '❌ יצירת הפקודה נכשלה: {msg}',
    'order_fail_leverage':         (
        "❌ הפקודה לא נוצרה: המינוף בחשבון Bybit גבוה מדי לגודל זה.\n"
        "אנא הפחת את המינוף בהגדרות Bybit."
    ),
    'order_parse_error':           '❌ כשל בפענוח: {error}',
    'price_error_min':             '❌ שגיאת מחיר: חייב להיות ≥{min}',
    'price_error_step':            '❌ שגיאת מחיר: חייב להיות כפולה של {step}',
    'qty_error_min':               '❌ שגיאת כמות: חייב להיות ≥{min}',
    'qty_error_step':              '❌ שגיאת כמות: חייב להיות כפולה של {step}',

    # Loading…
    'loader':                      '⏳ אוסף נתונים…',

    # Market command
    'market_status_heading':       '*מצב השוק:*',
    'market_dominance_header':    'מטבעות מובילים לפי דומיננטיות',
    'market_total_header':        'שווי שוק כולל',
    'market_indices_header':      'מדדי שוק',
    'usdt_dominance':              'דומיננטיות USDT',
    'btc_dominance':               'דומיננטיות BTC',
    'dominance_rising':            '↑ עולה',
    'dominance_falling':           '↓ יורד',
    'dominance_stable':            '↔️ יציב',
    'dominance_unknown':           '❔ אין נתונים',
    'btc_price':                   'מחיר BTC',
    'last_24h':                    'ב־24 השעות האחרונות',
    'alt_signal_label':            'איתות אלטקוין',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*חדשות אחרונות (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'לא נמצא מחיר ביצוע לסגירה',

    # /account
    'account_balance':             '💰 יתרת USDT: `{balance:.2f}`',
    'account_realized_header':     '📈 *PnL ממומש:*',
    'account_realized_day':        '  • היום : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7 ימים: `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *PnL לא ממומש:*',
    'account_unreal_total':        '  • סה״כ : `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • % מ־IM: `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *ההגדרות שלך:*',
    'config_percent':              '• 🎚 % לעסקה       : `{percent}%`',
    'config_coins':                '• 💠 מטבעות        : `{coins}`',
    'config_limit_only':           '• 🎯 הוראות Limit  : {state}',
    'config_atr_mode':             '• 🏧 SL נגרר ATR   : {atr}',
    'config_trade_oi':             '• 📊 מסחר לפי OI  : {oi}',
    'config_trade_rsi_bb':         '• 📈 מסחר RSI+BB   : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%           : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%           : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 אין הוראות פתוחות',
    'open_orders_header':          '*📒 הוראות פתוחות:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • צד  : `{side}`\n"
        "   • כמות: `{qty}`\n"
        "   • מחיר: `{price}`\n"
        "   • מזהה: `{id}`"
    ),
    'open_orders_error':           '❌ שגיאה בשליפה: {error}',

    # Manual coin selection
    'enter_coins':                 "הכנס סמלים מופרדים בפסיק, למשל:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ המטבעות נבחרו: {coins}',

    # Positions
    'no_positions':                '🚫 אין פוזיציות פתוחות',
    'positions_header':            '📊 הפוזיציות הפתוחות שלך:',
    'position_item':               (
        "— פוזיציה #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • גודל           : {size}\n"
        "  • מחיר כניסה     : {avg:.8f}\n"
        "  • מחיר Mark      : {mark:.8f}\n"
        "  • חיסול          : {liq}\n"
        "  • מרווח התחלתי  : {im:.2f}\n"
        "  • מרווח אחזקה    : {mm:.2f}\n"
        "  • יתרת פוזיציה   : {pm:.2f}\n"
        "  • Take Profit     : {tp}\n"
        "  • Stop Loss       : {sl}\n"
        "  • PnL לא ממומש   : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'positions_overall':           'PnL לא ממומש כולל: {pnl:+.2f} ({pct:+.2f}%)',

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
    'set_percent_prompt':          'הזן אחוז מהיתרה לכל עסקה (לדוגמה 2.5):',
    'percent_set_success':         '✅ אחוז לעסקה נקבע: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 הוראות Limit בלבד: {state}',
    'feature_limit_only':          'Limit בלבד',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Elcaro אינדיקטורים*',
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

    # Auto notifications
    'new_position': (
        '🚀 פוזיציה חדשה {symbol} @ {entry:.6f}, גודל={size}\n'
        '📍 {exchange} • {market_type}'
    ),
    'sl_auto_set':                 '🛑 SL הוגדר אוטומטית: {price:.6f}',
    'auto_close_position':         '⏱ פוזיציה {symbol} (TF={tf}) פתוחה > {tf} ומפסידה, נסגרה אוטומטית.',
    'position_closed': (
        '🔔 פוזיציה {symbol} נסגרה בגלל *{reason}*:\n'
        '• Strategy: `{strategy}`\n'
        '• כניסה: `{entry:.8f}`\n'
        '• יציאה: `{exit:.8f}`\n'
        '• PnL  : `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
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
    'insufficient_balance_error_extended': '❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>מינוף גבוה מדי!</b>\n\n⚙️ המינוף שהוגדר חורג מהמקסימום המותר עבור סמל זה.\n\n<b>מקסימום מותר:</b> {max_leverage}x\n\n<b>פתרון:</b> עבור להגדרות האסטרטגיה והפחת את המינוף.',
    


    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper כניסת Limit*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ שגיאת Scalper Limit: {msg}',
    'scalper_market_entry':        '⚡ *Scalper כניסת Market*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ שגיאת Scalper Market: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *Elcaro כניסת Limit*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ שגיאת Elcaro Limit: {msg}',
    'elcaro_market_entry':         '🔥 *Elcaro כניסת Market*\n• {symbol} {side}\n• מחיר: {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• כמות: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ שגיאת Elcaro Market: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

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
    'group_top100':                'TOP100',
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
    'api_test_success':            'החיבור הצליח!',
    'api_test_no_keys':            'מפתחות API לא הוגדרו',
    'api_test_set_keys':           'הגדר תחילה API Key ו-Secret.',
    'api_test_failed':             'החיבור נכשל',
    'api_test_error':              'שגיאה',
    'api_test_check_keys':         'בדוק את פרטי ה-API שלך.',
    'api_test_status':             'סטטוס',
    'api_test_connected':          'מחובר',
    'balance_wallet':              'יתרת ארנק',
    'balance_equity':              'הון',
    'balance_available':           'זמין',
    'api_missing_notice':          '⚠️ לא הגדרת מפתחות API של הבורסה. אנא הוסף את מפתח ה-API והסוד שלך בהגדרות (כפתורי 🔑 API ו-🔒 Secret), אחרת הבוט לא יכול לסחור עבורך.',
    'elcaro_ai_info':              '🤖 *מסחר מונע בינה מלאכותית*',

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
    'strat_mode_global':           '🌐 גלובלי',
    'strat_mode_demo':             '🧪 דמו',
    'strat_mode_real':             '💰 אמיתי',
    'strat_mode_both':             '🔄 שניהם',
    'strat_mode_changed':          '✅ מצב מסחר {strategy}: {mode}',

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

    'scalper_limit_entry':           'Scalper: הוראת לימיט {symbol} @ {price}',
    'scalper_limit_error':           'Scalper שגיאת לימיט: {msg}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper שגיאה: {msg}',

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
    'strat_elcaro':                  '🔥 Elcaro',
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
    'param_leverage': '⚡ מינוף',
    'prompt_leverage': 'הזן מינוף (1-100):',
    'auto_default': 'אוטומטי',

    # Elcaro AI
    'elcaro_ai_desc': '_כל הפרמטרים מנותחים אוטומטית מאותות AI:_',

    # Scalper entries
    'scalper_market_entry': '🚀 Scalper שוק {symbol} @ {price:.6f}',
    'scalper_analysis': 'Scalper: {side} @ {price}',

    # Scryptomera feature
    'feature_scryptomera': 'Scryptomera',
    


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
    'spot_trading_mode': 'מצב מסחר',
    'spot_btn_mode': 'מצב',
    
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
    
    'no_license': '⚠️ אתה צריך מנוי פעיל כדי להשתמש בתכונה זו.\n\nהשתמש ב-/subscribe כדי לרכוש רישיון.',
    'no_license_trading': '⚠️ אתה צריך מנוי פעיל כדי לסחור.\n\nהשתמש ב-/subscribe כדי לרכוש רישיון.',
    'license_required': '⚠️ תכונה זו דורשת מנוי {required}.\n\nהשתמש ב-/subscribe לשדרוג.',
    'trial_demo_only': '⚠️ רישיון ניסיון מאפשר רק מסחר דמו.\n\nשדרג ל-Premium או Basic למסחר אמיתי: /subscribe',
    'basic_strategy_limit': '⚠️ רישיון Basic בחשבון אמיתי מאפשר רק: {strategies}\n\nשדרג ל-Premium לכל האסטרטגיות: /subscribe',
    
    'subscribe_menu_header': '💎 *תוכניות מנוי*',
    'subscribe_menu_info': 'בחר תוכנית לפתיחת תכונות מסחר:',
    'btn_premium': '💎 פרימיום',
    'btn_basic': '🥈 בסיסי', 
    'btn_trial': '🎁 ניסיון (חינם)',
    'btn_enter_promo': '🎟 קוד פרומו',
    'btn_my_subscription': '📋 המנוי שלי',
    
    'premium_title': '💎 *תוכנית PREMIUM*',
    'premium_desc': '''✅ גישה מלאה לכל התכונות
✅ כל 5 האסטרטגיות: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ מסחר אמיתי + דמו
✅ תמיכה עדיפה
✅ SL/TP דינמי מבוסס ATR
✅ סולם לימיט DCA
✅ כל העדכונים העתידיים''',
    'premium_1m': '💎 חודש 1 — {price} TRC',
    'premium_3m': '💎 3 חודשים — {price} TRC (-10%)',
    'premium_6m': '💎 6 חודשים — {price} TRC (-20%)',
    'premium_12m': '💎 12 חודשים — {price} TRC (-30%)',
    
    'basic_title': '🥈 *תוכנית BASIC*',
    'basic_desc': '''✅ גישה מלאה לחשבון דמו
✅ חשבון אמיתי: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Fibonacci, Spot — Premium בלבד
✅ תמיכה רגילה
✅ SL/TP דינמי מבוסס ATR''',
    'basic_1m': '🥈 חודש 1 — {price} TRC',
    
    'trial_title': '🎁 *תוכנית ניסיון (חינם)*',
    'trial_desc': '''✅ גישה מלאה לחשבון דמו
✅ כל 5 האסטרטגיות בדמו
❌ מסחר אמיתי לא זמין
⏰ משך: 7 ימים
🎁 פעם אחת בלבד''',
    'trial_activate': '🎁 הפעל ניסיון חינם',
    'trial_already_used': '⚠️ כבר השתמשת בניסיון החינמי.',
    'trial_activated': '🎉 ניסיון הופעל! יש לך 7 ימים של גישה מלאה לדמו.',
    
    'payment_select_method': '💳 *בחר אמצעי תשלום*',
    'btn_pay_trc': '◈ Triacelo Coin (TRC)',
    'btn_pay_ton': '💎 TON',
    'payment_trc_title': ' תשלום דרך TRC',
    'payment_trc_desc': 'יחויבו {amount} TRC עבור {plan} ({period}).',
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
  TRC: {total_trc}

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

    # Wallet & TRC translations

    'payment_trc_insufficient': '''❌ Insufficient TRC balance.

Your balance: {balance} TRC
Required: {required} TRC

Top up your wallet to continue.''',
    'wallet_address': '''📍 Address: `{address}`''',
    'wallet_balance': '''💰 *Your TRC Wallet*

◈ Balance: *{balance} TRC*
📈 Staked: *{staked} TRC*
🎁 Pending Rewards: *{rewards} TRC*

�� Total Value: *${total_usd}*
📍 1 TRC = 1 USDT''',
    'wallet_btn_back': '''« Back''',
    'wallet_btn_deposit': '''📥 Deposit''',
    'wallet_btn_history': '''📋 History''',
    'wallet_btn_stake': '''📈 Stake''',
    'wallet_btn_unstake': '''📤 Unstake''',
    'wallet_btn_withdraw': '''📤 Withdraw''',
    'wallet_deposit_demo': '''🎁 Get 100 TRC (Demo)''',
    'wallet_deposit_desc': '''Send TRC tokens to your wallet address:

`{address}`

💡 *Demo mode:* Click below for free test tokens.''',
    'wallet_deposit_success': '''✅ Deposited {amount} TRC successfully!''',
    'wallet_deposit_title': '''📥 *Deposit TRC*''',
    'wallet_history_empty': '''No transactions yet.''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} TRC
   {date}''',
    'wallet_history_title': '''�� *Transaction History*''',
    'wallet_stake_desc': '''Stake your TRC tokens to earn *12% APY*!

💰 Available: {available} TRC
📈 Currently Staked: {staked} TRC
🎁 Pending Rewards: {rewards} TRC

Daily rewards • Instant unstaking''',
    'wallet_stake_success': '''✅ Staked {amount} TRC successfully!''',
    'wallet_stake_title': '''📈 *Stake TRC*''',
    'wallet_title': '''◈ *TRC Wallet*''',
    'wallet_unstake_success': '''✅ Unstaked {amount} TRC + {rewards} TRC rewards!''',
    'wallet_withdraw_desc': '''Enter destination address and amount:''',
    'wallet_withdraw_failed': '''❌ Withdrawal failed: {error}''',
    'wallet_withdraw_success': '''✅ Withdrawn {amount} TRC to {address}''',
    'wallet_withdraw_title': '''📤 *Withdraw TRC*''',

}
