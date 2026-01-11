# -*- coding: utf-8 -*-
TEXTS = {
    # Main menu
    'welcome':                     '👋 こんにちは！ 操作を選んでください:',
    'no_strategies':               '❌ なし',
    'guide_caption':               '📚 トレーディングボットユーザーガイド\n\nこのガイドを読んで、戦略の設定方法とボットの効果的な使い方を学んでください。',
    'privacy_caption':             '📜 プライバシーポリシーと利用規約\n\nこの文書をよくお読みください。',
    'button_api':                  '🔑 API',
    'button_secret':               '🔒 シークレット',
    'button_api_settings':         '🔑 API',
    'button_balance':              '💰 USDT残高',
    'button_orders':               '📜 注文一覧',
    'button_positions':            '📊 建玉',
    'button_percent':              '🎚 取引ごとの％',
    'button_coins':                '💠 コイングループ',
    'button_market':               '📈 マーケット',
    'button_manual_order':         '✋ 手動注文',
    'button_update_tpsl':          '🆕 TP/SL',
    'button_cancel_order':         '❌ 注文を取消',
    'button_limit_only':           '🎯 Limitのみ',
    'button_toggle_oi':            '🔀 OI',
    'button_toggle_rsi_bb':        '📊 RSI+BB',
    'button_scryptomera':          '🔮 Scryptomera',
    'button_settings':             '⚙️ 設定',
    'button_indicators':           '💡 インジケーター',
    'button_support':              '🆘 サポート',
    'toggle_oi_status':            '🔀 {feature}: {status}',
    'toggle_rsi_bb_status':        '📊 {feature}: {status}',
    'config_trade_scryptomera':    '🔮 Scryptomera: {state}',

    # Inline buttons for manual order
    'button_order_limit':          'Limit',
    'button_order_market':         'Market',

    # ATR / Stop mode
    'atr_mode_changed':            '🔄 TP/SLモードが *{mode_text}* に変更されました',
    'atr_mode_wilder':             'Wilder-ATR',
    'atr_mode_fixed':              '固定％',

    # Limits
    'limit_positions_exceeded':    '🚫 建玉の上限を超えました ({max})',
    'limit_limit_orders_exceeded': '🚫 指値注文の上限を超えました ({max})',

    # Languages
    'select_language':             '言語を選択:',
    'language_set':                '言語を設定しました:',
    'lang_en':                     'English',

    # Manual order
    'order_type_prompt':           '注文タイプを選択:',
    'limit_order_format': (
        "指値注文のパラメータを入力:\n"
        "`SYMBOL SIDE PRICE QTY`\n"
        "SIDE は LONG または SHORT\n"
        "例: `BTCUSDT LONG 20000 0.1`\n\n"
        "取消するには ❌ 注文を取消 を送信"
    ),
    'market_order_format': (
        "成行注文のパラメータを入力:\n"
        "`SYMBOL SIDE QTY`\n"
        "SIDE は LONG または SHORT\n"
        "例: `BTCUSDT SHORT 0.1`\n\n"
        "取消するには ❌ 注文を取消 を送信"
    ),
    'order_success':               '✅ 注文を作成しました！',
    'order_create_error':          '❌ 注文作成に失敗: {msg}',
    'order_fail_leverage':         (
        "❌ 注文未作成: Bybit口座のレバレッジがこのサイズに対して高すぎます。\n"
        "Bybitの設定でレバレッジを下げてください。"
    ),
    'order_parse_error':           '❌ 解析に失敗: {error}',
    'price_error_min':             '❌ 価格エラー: {min}以上である必要があります',
    'price_error_step':            '❌ 価格エラー: {step}の倍数である必要があります',
    'qty_error_min':               '❌ 数量エラー: {min}以上である必要があります',
    'qty_error_step':              '❌ 数量エラー: {step}の倍数である必要があります',

    # Loading…
    'loader':                      '⏳ データを収集中…',

    # Market command
    'market_status_heading':       '*マーケット状況:*',
    'market_dominance_header':    'ドミナンス上位コイン',
    'market_total_header':        '総時価総額',
    'market_indices_header':      '市場指数',
    'usdt_dominance':              'USDTドミナンス',
    'btc_dominance':               'BTCドミナンス',
    'dominance_rising':            '↑ 上昇',
    'dominance_falling':           '↓ 下降',
    'dominance_stable':            '↔️ 横ばい',
    'dominance_unknown':           '❔ データなし',
    'btc_price':                   'BTC価格',
    'last_24h':                    '過去24時間',
    'alt_signal_label':            'アルトコインシグナル',
    'alt_signal_long':             'LONG',
    'alt_signal_short':            'SHORT',
    'alt_signal_neutral':          'NEUTRAL',
    'latest_news_coindesk':        '*最新ニュース (CoinDesk):*',

    # Execution price error
    'exec_price_not_found':        'クローズの約定価格が見つかりません',

    # /account
    'account_balance':             '💰 USDT残高: `{balance:.2f}`',
    'account_realized_header':     '📈 *実現損益:*',
    'account_realized_day':        '  • 今日 : `{pnl:+.2f}` USDT',
    'account_realized_week':       '  • 7日 : `{pnl:+.2f}` USDT',
    'account_unreal_header':       '📊 *含み損益:*',
    'account_unreal_total':        '  • 合計 : `{unreal:+.2f}` USDT',
    'account_unreal_pct':          '  • IM比率: `{pct:+.2f}%`',
    'account_error':               '❌ {error}',

    # /show_config
    'config_header':               '🛠 *あなたの設定:*',
    'config_percent':              '• 🎚 取引％          : `{percent}%`',
    'config_coins':                '• 💠 コイン         : `{coins}`',
    'config_limit_only':           '• 🎯 指値のみ       : {state}',
    'config_atr_mode':             '• 🏧 ATRトレーリングSL : {atr}',
    'config_trade_oi':             '• 📊 OI取引         : {oi}',
    'config_trade_rsi_bb':         '• 📈 RSI+BB取引     : {rsi_bb}',
    'config_tp_pct':               '• 🎯 TP%            : `{tp}%`',
    'config_sl_pct':               '• 🛑 SL%            : `{sl}%`',

    # Open orders
    'no_open_orders':              '🚫 開いている注文はありません',
    'open_orders_header':          '*📒 オープン注文:*',
    'open_orders_item':            (
        "{idx}️⃣ *{symbol}*\n"
        "   • サイド: `{side}`\n"
        "   • 数量  : `{qty}`\n"
        "   • 価格  : `{price}`\n"
        "   • ID    : `{id}`"
    ),
    'open_orders_error':           '❌ 注文取得エラー: {error}',

    # Manual coin selection
    'enter_coins':                 "記号をカンマ区切りで入力（例）:\n`BTCUSDT,ETHUSDT`",
    'coins_set_success':           '✅ 選択したコイン: {coins}',

    # Positions
    'no_positions':                '🚫 建玉はありません',
    'positions_header':            '📊 保有中の建玉:',
    'position_item':               (
        "— 建玉 #{idx}: {symbol} | {side} (x{leverage})\n"
        "  • サイズ        : {size}\n"
        "  • エントリー価格: {avg:.8f}\n"
        "  • マーク価格    : {mark:.8f}\n"
        "  • 清算価格      : {liq}\n"
        "  • 初期証拠金    : {im:.2f}\n"
        "  • 維持証拠金    : {mm:.2f}\n"
        "  • ポジション残高: {pm:.2f}\n"
        "  • テイクプロフィット: {tp}\n"
        "  • ストップロス      : {sl}\n"
        "  • 含み損益        : {pnl:+.2f} ({pct:+.2f}%)"
    ),
    'positions_overall':           '含み損益 合計: {pnl:+.2f} ({pct:+.2f}%)',

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
    'set_percent_prompt':          '1取引あたりの残高％を入力（例 2.5）:',
    'percent_set_success':         '✅ 取引％を設定: {pct}%',

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 指値のみ: {state}',
    'feature_limit_only':          'Limitのみ',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Elcaro インジケーター*',
    'indicator_1':                 '1. RSI + BB',
    'indicator_2':                 '2. Trading Chaos',
    'indicator_3':                 '3. アダプティブ・トレンド',
    'indicator_4':                 '4. ダイナミック回帰',

    # Support
    'support_prompt':              '✉️ ヘルプが必要？ 下をタップ:',
    'support_button':              'サポートに連絡',

    # Update TP/SL
    'update_tpsl_no_positions':    '🚫 建玉はありません',
    'update_tpsl_prompt':          'SYMBOL TP SL を入力（例）:\n`BTCUSDT 21000 19500`',
    'invalid_tpsl_format':         '❌ フォーマット無効。SYMBOL TP SL を使用\n例: BTCUSDT 21000 19500',

    # API / Secret
    'enter_api':                   'Bybit APIキーを入力:',
    'api_saved':                   '✅ APIキーを保存しました',
    'enter_secret':                'Bybit APIシークレットを入力:',
    'secret_saved':                '✅ シークレットを保存しました',

    # Manual TP/SL (%)
    'enter_tp':                    '❌ TP% の値を入力',
    'tp_set_success':              '✅ TP% を設定: {pct}%',
    'enter_sl':                    '❌ SL% の値を入力',
    'sl_set_success':              '✅ SL% を設定: {pct}%',

    # Parsing errors
    'parse_limit_error':           'Limit: 引数は4つ (SYMBOL SIDE PRICE QTY)',
    'parse_market_error':          'Market: 引数は3つ (SYMBOL SIDE QTY)',
    'parse_side_error':            'SIDE は LONG または SHORT',

    # Bybit HTTP helper
    'api_missing_credentials':     '❌ APIキー/シークレットが未設定',
    'bybit_invalid_response':      '❌ Bybitから不正な応答',
    'bybit_error':                 '❌ Bybit エラー {path}: {data}',

    # Auto notifications
    'new_position': (
        '🚀 新規建玉 {symbol} @ {entry:.6f}, サイズ={size}\n'
        '📍 {exchange} • {market_type}'
    ),
    'sl_auto_set':                 '🛑 SL を自動設定: {price:.6f}',
    'auto_close_position':         '⏱ 建玉 {symbol} (TF={tf}) が {tf}超かつ損失のため自動クローズ。',
    'position_closed': (
        '🔔 建玉 {symbol} は *{reason}* でクローズ:\n'
        '• Strategy: `{strategy}`\n'
        '• エントリー: `{entry:.8f}`\n'
        '• エグジット : `{exit:.8f}`\n'
        '• PnL        : `{pnl:+.2f} USDT ({pct:+.2f}%)`\n'
        '📍 {exchange} • {market_type}'
    ),

    # Entries & errors - 統一フォーマット（詳細情報付き）
    'oi_limit_entry':              '📉 *OI 指値エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'oi_limit_error':              '❌ OI 指値エラー: {msg}',
    'oi_market_entry':             '📉 *OI 成行エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'oi_market_error':             '❌ OI 成行エラー: {msg}',
    'oi_market_ok':                '📉 *OI: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',

    'rsi_bb_limit_entry':          '📊 *RSI+BB 指値エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_entry':         '📊 *RSI+BB 成行エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'rsi_bb_market_ok':            '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%',
    'rsi_bb_market_error':         '❌ RSI+BB 成行エラー: {msg}',

    'oi_analysis':                 '📊 *OI {symbol} 解析* {side}',

    # Scryptomera
    'bitk_limit_entry':            '🔮 *Scryptomera 指値エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'bitk_limit_error':            '❌ Scryptomera 指値エラー: {msg}',
    'bitk_market_entry':           '🔮 *Scryptomera 成行エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'bitk_market_ok':              '🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'bitk_market_error':           '❌ Scryptomera 成行エラー: {msg}',
    'bitk_analysis':               '🔮 Scryptomera: {side} @ {price}',
    'feature_scryptomera':         'Scryptomera',

    # Insufficient balance error
    'insufficient_balance_error':  '❌ <b>残高不足！</b>\n\n💰 {account_type}アカウントにこのポジションを開くのに十分な資金がありません。\n\n<b>解決策:</b>\n• 残高をチャージする\n• ポジションサイズを縮小する (取引あたりの%)\n• レバレッジを下げる\n• 一部のオープンポジションを閉じる',
    'insufficient_balance_error_extended': '❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions',

    # Leverage too high error
    'leverage_too_high_error':     '❌ <b>レバレッジが高すぎます！</b>\n\n⚙️ 設定されたレバレッジがこのシンボルの最大許容値を超えています。\n\n<b>最大許容:</b> {max_leverage}x\n\n<b>解決策:</b> ストラテジー設定に移動し、レバレッジを減らしてください。',

    # Position limit exceeded error (110090)
    'position_limit_error':        '❌ <b>ポジション制限超過！</b>\n\n📊 戦略: <b>{strategy}</b>\n🪙 シンボル: <b>{symbol}</b>\n\n⚠️ ポジションが最大制限を超えます。\n\n<b>解決策:</b>\n• レバレッジを下げる\n• ポジションサイズを減らす\n• 一部のポジションを決済',
    


    # Scalper
    'scalper_limit_entry':         '⚡ *Scalper 指値エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'scalper_limit_error':         '❌ Scalper 指値エラー: {msg}',
    'scalper_market_entry':        '⚡ *Scalper 成行エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'scalper_market_ok':           '⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'scalper_market_error':        '❌ Scalper 成行エラー: {msg}',
    'scalper_analysis':            '⚡ Scalper: {side} @ {price}',
    'feature_scalper':             'Scalper',

    # Elcaro (Heatmap)
    'elcaro_limit_entry':          '🔥 *Elcaro 指値エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Elcaro 指値エラー: {msg}',
    'elcaro_market_entry':         '🔥 *Elcaro 成行エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Elcaro: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Elcaro 成行エラー: {msg}',
    'elcaro_analysis':             '🔥 Elcaro Heatmap: {side} @ {price}',
    'feature_elcaro':              'Elcaro',

    # Fibonacci (Fibonacci Extension)
    'fibonacci_limit_entry':         '📐 *Fibonacci 指値エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'fibonacci_limit_error':         '❌ Fibonacci 指値エラー: {msg}',
    'fibonacci_market_entry':        '📐 *Fibonacci 成行エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_ok':           '📐 *Fibonacci: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'fibonacci_market_error':        '❌ Fibonacci 成行エラー: {msg}',
    'fibonacci_analysis':            '📐 Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    # Admin panel
    'admin_panel':                 '👑 管理パネル:',
    'admin_pause':                 '⏸️ すべての取引と通知を一時停止しました。',
    'admin_resume':                '▶️ すべての取引と通知を再開しました。',
    'admin_closed':                '✅ 合計 {count} {type} をクローズしました。',
    'admin_canceled_limits':       '✅ 指値注文を {count} 件キャンセルしました。',

    # Coin groups
    'select_coin_group':           'コイングループを選択:',
    'group_all':                   'ALL',
    'group_top':                   'TOP',
    'group_top100':                'TOP',  # backward compatibility
    'group_volatile':              'VOLATILE',
    'group_set':                   '✅ コイングループを設定: {group}',

    # RSI+BB analysis & helpers
    'rsi_bb_analysis':     (
        '📈 *RSI+BB 解析*\n'
        '• 価格: `{price:.6f}`\n'
        '• RSI: `{rsi:.1f}` ({zone})\n'
        '• BB上限: `{bb_hi:.4f}`\n'
        '• BB下限: `{bb_lo:.4f}`\n\n'
        '*RSI+BB による {side} のMARKETエントリー*'
    ),
    'sl_set':                      '🛑 SL={price:.6f}',

    'rsi_zone_oversold':           '売られ過ぎ (<30)',
    'rsi_zone_overbought':         '買われ過ぎ (>70)',
    'rsi_zone_neutral':            '中立 (30–70)',

    # TP/SL validation
    'invalid_tpsl_long': (
        '❌ LONGのTP/SLが無効です。\n'
        '現在価格: {current:.2f}\n'
        '想定: SL < {current:.2f} < TP'
    ),
    'invalid_tpsl_short': (
        '❌ SHORTのTP/SLが無効です。\n'
        '現在価格: {current:.2f}\n'
        '想定: TP < {current:.2f} < SL'
    ),
    'no_position_symbol':          '🚫 {symbol} の建玉はありません',
    'tpsl_set_success':            '✅ {symbol} の TP={tp:.2f}, SL={sl:.2f} を設定しました',

    # Buttons & stop mode line items
    'button_toggle_atr':           '🏧 ATR',
    'button_lang':                 '🌐 言語',
    'button_set_tp':               '🆙 TP %',
    'button_set_sl':               '⬇️ SL %',
    'config_stop_mode':            'ストップモード: *{mode}*',

    # Order life-cycle & updates
    'limit_order_filled':          '✅ {symbol} の指値注文が約定 @ {price}',
    'limit_order_cancelled':       '⚠️ {symbol} の指値注文 (ID: {order_id}) を取消しました。',
    'fixed_sl_tp':                 '✅ {symbol}: SL {sl}, TP {tp} を設定',
    'tp_part':                     '、TPを {tp_price} に設定',
    'sl_tp_set':                   '✅ {symbol}: SL {sl_price}{tp_part}',
    'sl_set_only':                 '✅ {symbol}: SL {sl_price} を設定',
    'sl_tp_initialized':           '✅ {symbol}: SL/TP を {sl}/{tp} に初期化',
    'sl_breakeven':                '🔄 {symbol}: エントリー {entry} でSLを同値に移動',
    'sl_tp_updated':               '✏️ {symbol}: SL/TP を {sl}/{tp} に更新',

    'position_closed_error': (
        '⚠️ {symbol} をクローズしましたが記録に失敗: {error}\n'
        'サポートへ連絡してください。'
    ),

    # possible values
    'mode_atr':                    'Wilder-ATR',
    'mode_fixed':                  '固定％',

    # System notices
    'db_quarantine_notice':        '⚠️ ログを一時停止しました。1時間のサイレントモード。',

    # Fallback
    'fallback':                    '❓ メニューのボタンを使用してください。',
    'dash': '—',
    'mark_yes': '✅',
    'mark_no': '—',
    'mark_ban': '⛔️',

    'banned': '🚫 ブロックされています。',
    'invite_only': '🔒 招待制のみ。管理者の承認をお待ちください。',
    'need_terms': '⚠️ まず利用規約を受け入れてください: /terms',
    'please_confirm': '確認してください:',
    'terms_ok': '✅ ありがとうございます！ 規約を承認しました。',
    'terms_declined': '❌ 規約を拒否しました。アクセスは閉鎖されました。/terms で戻れます。',
    'usage_approve': '使用方法: /approve <user_id>',
    'usage_ban': '使用方法: /ban <user_id>',
    'not_allowed': '許可されていません',
    'bad_payload': '無効なデータ',
    'unknown_action': '不明な操作',

    'title': '新規ユーザー',
    'wave': '👋',
    'admin_new_user_html': (
        '<b>{wave} {title}</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• 名前: {name}\n'
        '• ユーザー名: {uname}\n'
        '• 言語: {lang}\n'
        '• 許可: {allowed}  Ban: {banned}\n'
    ),
    'btn_approve': '✅ 承認',
    'btn_ban': '⛔️ BAN',
    'admin_notify_fail': '管理者への通知に失敗しました: {e}',
    'moderation_approved': '✅ 承認: {target}',
    'moderation_banned': '⛔️ BAN: {target}',
    'approved_user_dm': '✅ アクセスが承認されました。/start を押してください。',
    'banned_user_dm': '🚫 ブロックされています。',

    'users_not_found': '😕 ユーザーが見つかりません。',
    'users_page_info': '📄 ページ {page}/{pages} — 合計: {total}',
    'user_card_html': (
        '<b>👤 ユーザー</b>\n'
        '• ID: <code>{uid}</code>\n'
        '• 名前: {full_name}\n'
        '• ユーザー名: {uname}\n'
        '• 言語: <code>{lang}</code>\n'
        '• 許可: {allowed}\n'
        '• BAN: {banned}\n'
        '• 規約: {terms}\n'
        '• 取引ごとの％: <code>{percent}</code>'
    ),
    'btn_blacklist': '🚫 ブラックリスト',
    'btn_delete_user': '🗑 DB から削除',
    'btn_prev': '⬅️ 戻る',
    'btn_next': '➡️ 次へ',
    'nav_caption': '🧭 ナビゲーション:',
    'bad_page': '無効なページです。',
    'admin_user_delete_fail': '❌ {target} の削除に失敗: {error}',
    'admin_user_deleted': '🗑 ユーザー {target} を DB から削除しました。',
    'user_access_approved': '✅ アクセス承認済み。/start を押してください。',

    'admin_pause_all': '⏸️ 全員を一時停止',
    'admin_resume_all': '▶️ 再開',
    'admin_close_longs': '🔒 すべてのLONGをクローズ',
    'admin_close_shorts': '🔓 すべてのSHORTをクローズ',
    'admin_cancel_limits': '❌ 指値注文を削除',
    'admin_users': '👥 ユーザー',
    'admin_pause_notice': '⏸️ 取引と通知を全員で一時停止しました。',
    'admin_resume_notice': '▶️ 取引と通知を全員で再開しました。',
    'type_longs': 'longs',
    'type_shorts': 'shorts',
    'admin_closed_total': '✅ 合計 {count} {type} をクローズ。',
    'admin_canceled_limits_total': '✅ 指値注文 {count} 件をキャンセル。',

    'terms_btn_accept': '✅ 同意する',
    'terms_btn_decline': '❌ 拒否する',

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
    'api_test_success':            '接続成功！',
    'api_test_no_keys':            'APIキーが設定されていません',
    'api_test_set_keys':           '先にAPI KeyとSecretを設定してください。',
    'api_test_failed':             '接続失敗',
    'api_test_error':              'エラー',
    'api_test_check_keys':         'API認証情報を確認してください。',
    'api_test_status':             'ステータス',
    'api_test_connected':          '接続済み',
    'balance_wallet':              'ウォレット残高',
    'balance_equity':              '資産',
    'balance_available':           '利用可能',
    'api_missing_notice':          '⚠️ 取引所のAPIキーが設定されていません。設定でAPIキーとシークレットを追加してください（🔑 APIと🔒 Secretボタン）。そうしないと、ボットはあなたの代わりに取引できません。',
    'elcaro_ai_info':              '🤖 *AI搭載トレーディング*',

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
    'strat_mode_global':           '🌐 グローバル',
    'strat_mode_demo':             '🧪 デモ',
    'strat_mode_real':             '💰 リアル',
    'strat_mode_both':             '🔄 両方',
    'strat_mode_changed':          '✅ {strategy} 取引モード: {mode}',

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
    'fibonacci_limit_entry':         '📐 Fibonacci limit-entry {symbol} @ {price:.6f}',
    'fibonacci_limit_error':         '❌ Fibonacci limit-entry error: {msg}',
    'fibonacci_market_entry':        '🚀 Fibonacci market {symbol} @ {price:.6f}',
    'fibonacci_market_error':        '❌ Fibonacci market error: {msg}',
    'fibonacci_market_ok':           '📐 Fibonacci: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'fibonacci_analysis':            'Fibonacci: {side} @ {price}',
    'feature_fibonacci':             'Fibonacci',

    'scalper_limit_entry':           'Scalper: 指値注文 {symbol} @ {price}',
    'scalper_limit_error':           'Scalper 指値エラー: {msg}',
    'scalper_market_ok':             'Scalper: MARKET {symbol} qty={q} (SL={sl_risk}%)',
    'scalper_market_error':          'Scalper エラー: {msg}',

    # Strategy Settings
    'button_strategy_settings':      '⚙️ 戦略設定',
    'strategy_settings_header':      '⚙️ *戦略設定*',
    'strategy_param_header':         '⚙️ *{name} 設定*',
    'using_global':                  'グローバル設定',
    'global_default':                'グローバル',
    'strat_oi':                      '🔀 OI',
    'strat_rsi_bb':                  '📊 RSI+BB',
    'strat_scryptomera':             '🔮 Scryptomera',
    'strat_scalper':                 '🎯 Scalper',
    'strat_elcaro':                  '🔥 Elcaro',
    'strat_fibonacci':                 '📐 Fibonacci',
    'dca_settings':                  '⚙️ DCA設定',
    'dca_settings_header':           '⚙️ *DCA Settings (Futures)*\n\n',
    'dca_toggle':                    'DCA Enabled',
    'dca_status':                    'Status',
    'dca_description':               '_DCA will add to position when price moves against you._',
    'dca_leg1':                      '📉 DCA レベル1 %',
    'dca_leg2':                      '📉 DCA レベル2 %',
    'param_percent':                 '📊 エントリー %',
    'param_sl':                      '🔻 ストップロス %',
    'param_tp':                      '🔺 テイクプロフィット %',
    'param_reset':                   '🔄 グローバルにリセット',
    'btn_close':                     '❌ 閉じる',
    'prompt_entry_pct':              'エントリー%を入力（トレードあたりのリスク）:',
    'prompt_sl_pct':                 'ストップロス%を入力:',
    'prompt_tp_pct':                 'テイクプロフィット%を入力:',
    'prompt_atr_periods':            'ATR期間を入力（例: 7）:',
    'prompt_atr_mult':               'トレーリングSL用ATR倍率を入力（例: 1.0）:',
    'prompt_atr_trigger':            'ATRトリガー%を入力（例: 2.0）:',
    'prompt_dca_leg1':               'DCAレベル1%を入力（例: 10）:',
    'prompt_dca_leg2':               'DCAレベル2%を入力（例: 25）:',
    'settings_reset':                '設定をグローバルにリセットしました',
    'strat_setting_saved':           '✅ {name} {param} を {value} に設定',
    'dca_setting_saved':             '✅ DCA {leg} を {value}% に設定',
    'invalid_number':                '❌ 無効な数値です。0から100の値を入力してください。',
    'dca_10pct':                     'DCA −{pct}%: ナンピン {symbol} qty={qty} @ {price}',
    'dca_25pct':                     'DCA −{pct}%: ナンピン {symbol} qty={qty} @ {price}',
    'config_dca':                    'DCA: レベル1=-{dca1}%, レベル2=-{dca2}%',

    # ATR settings UI
    'param_atr_periods':             '📈 ATR期間',
    'param_atr_mult':                '📉 ATR倍率（SLステップ）',
    'param_atr_trigger':             '🎯 ATRトリガー%',

    # Hardcoded strings fix
    'terms_unavailable':             '利用規約が利用できません。管理者に連絡してください。',
    'terms_confirm_prompt':          '確認してください:',
    'your_id':                       'あなたのID: {uid}',
    'error_validation':              '❌ {msg}',
    'error_generic':                 'エラー: {msg}',
    'error_fetch_balance':           '❌ 残高取得エラー: {error}',
    'error_fetch_orders':            '❌ 注文取得エラー: {error}',
    'error_occurred':                '❌ エラー: {error}',

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
    'stats_strategy_settings':       '戦略設定',
    'settings_entry_pct':            'エントリー',
    'settings_leverage':             'レバレッジ',
    'settings_trading_mode':         'モード',
    'settings_direction':            '方向',
    'stats_all':                     '📈 All',
    'stats_oi':                      '📉 OI',
    'stats_rsi_bb':                  '📊 RSI+BB',
    'stats_scryptomera':             '🐱 Scryptomera',
    'stats_scalper':                 '⚡ Scalper',
    'stats_elcaro':                  '🔥 Elcaro',
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

    # Elcaro AI settings

    # Leverage settings
    'param_leverage': '⚡ レバレッジ',
    'prompt_leverage': 'レバレッジを入力 (1-100):',
    'auto_default': '自動',

    # Elcaro AI
    'elcaro_ai_desc': '_すべてのパラメータはAIシグナルから自動で解析されます:_',

    # Scalper entries
    'scalper_market_entry': '🚀 Scalper マーケット {symbol} @ {price:.6f}',
    'scalper_analysis': 'Scalper: {side} @ {price}',

    # Scryptomera feature
    'feature_scryptomera': 'Scryptomera',
    


    # Limit Ladder
    'limit_ladder': '📉 指値ラダー',
    'limit_ladder_header': '📉 *指値ラダー設定*',
    'limit_ladder_settings': '⚙️ ラダー設定',
    'ladder_count': '注文数',
    'ladder_info': 'DCA用のエントリー以下の指値注文。各注文にはエントリーからの%と証拠金の%があります。',
    'prompt_ladder_pct_entry': '📉 注文 {idx} のエントリー価格以下の%を入力:',
    'prompt_ladder_pct_deposit': '💰 注文 {idx} の証拠金%を入力:',
    'ladder_order_saved': '✅ 注文 {idx} 保存済み: -{pct_entry}% @ {pct_deposit}% 証拠金',
    'ladder_orders_placed': '📉 {symbol} に {count} 件の指値注文を発注',
    
    # Spot Trading Mode
    'spot_trading_mode': '取引モード',
    'spot_btn_mode': 'モード',
    
    # Stats PnL
    'stats_realized_pnl': '実現',
    'stats_unrealized_pnl': '未実現',
    'stats_combined_pnl': '合計',
    'stats_spot': '💹 現物',
    'stats_spot_title': '現物DCA統計',
    'stats_spot_config': '設定',
    'stats_spot_holdings': '保有',
    'stats_spot_summary': '概要',
    'stats_spot_current_value': '現在価値',

    # =====================================================
    # LICENSING SYSTEM
    # =====================================================
    
    'no_license': '⚠️ この機能を使用するにはアクティブなサブスクリプションが必要です。\n\n/subscribe でライセンスを購入してください。',
    'no_license_trading': '⚠️ 取引するにはアクティブなサブスクリプションが必要です。\n\n/subscribe でライセンスを購入してください。',
    'license_required': '⚠️ この機能には{required}サブスクリプションが必要です。\n\n/subscribe でアップグレードしてください。',
    'trial_demo_only': '⚠️ トライアルライセンスはデモ取引のみ可能です。\n\n実取引にはPremiumまたはBasicにアップグレード: /subscribe',
    'basic_strategy_limit': '⚠️ Basicライセンスの実口座では以下のみ可能: {strategies}\n\n全戦略にはPremiumにアップグレード: /subscribe',
    
    'subscribe_menu_header': '💎 *サブスクリプションプラン*',
    'subscribe_menu_info': '取引機能をアンロックするプランを選択:',
    'btn_premium': '💎 プレミアム',
    'btn_basic': '🥈 ベーシック', 
    'btn_trial': '🎁 トライアル（無料）',
    'btn_enter_promo': '🎟 プロモコード',
    'btn_my_subscription': '📋 マイサブスクリプション',
    
    'premium_title': '💎 *プレミアムプラン*',
    'premium_desc': '''✅ 全機能へのフルアクセス
✅ 5つの戦略すべて: OI, RSI+BB, Scryptomera, Scalper, Elcaro
✅ 実取引 + デモ取引
✅ 優先サポート
✅ ATRベースの動的SL/TP
✅ リミットラダーDCA
✅ 将来の全アップデート''',
    'premium_1m': '💎 1ヶ月 — {price} TRC',
    'premium_3m': '💎 3ヶ月 — {price} TRC (-10%)',
    'premium_6m': '💎 6ヶ月 — {price} TRC (-20%)',
    'premium_12m': '💎 12ヶ月 — {price} TRC (-30%)',
    
    'basic_title': '🥈 *ベーシックプラン*',
    'basic_desc': '''✅ デモ口座へのフルアクセス
✅ 実口座: OI, RSI+BB, Scryptomera, Scalper
❌ Elcaro, Fibonacci, Spot — Premiumのみ
✅ 標準サポート
✅ ATRベースの動的SL/TP''',
    'basic_1m': '🥈 1ヶ月 — {price} TRC',
    
    'trial_title': '🎁 *トライアルプラン（無料）*',
    'trial_desc': '''✅ デモ口座へのフルアクセス
✅ デモで5つの戦略すべて
❌ 実取引は利用不可
⏰ 期間: 7日間
🎁 一度きり''',
    'trial_activate': '🎁 無料トライアルを有効化',
    'trial_already_used': '⚠️ 無料トライアルは既に使用済みです。',
    'trial_activated': '🎉 トライアル有効化！7日間のフルデモアクセスがあります。',
    
    'payment_select_method': '💳 *支払い方法を選択*',
    'btn_pay_trc': '◈ Triacelo Coin (TRC)',
    'btn_pay_ton': '💎 TON',
    'payment_trc_title': '◈ Triacelo Coin (TRC)での支払い',
    'payment_trc_desc': '{plan}（{period}）に{amount} TRCが請求されます。',
    'payment_ton_title': '💎 TONでの支払い',
    'payment_ton_desc': '''正確に*{amount} TON*を以下に送金:

`{wallet}`

支払い後、下のボタンをクリックして確認。''',
    'btn_verify_ton': '✅ 支払い済み — 確認',
    'payment_processing': '⏳ 支払い処理中...',
    'payment_success': '🎉 支払い成功！\n\n{plan}が{expires}まで有効化されました。',
    'payment_failed': '❌ 支払い失敗: {error}',
    
    'my_subscription_header': '📋 *マイサブスクリプション*',
    'my_subscription_active': '''📋 *現在のプラン:* {plan}
⏰ *有効期限:* {expires}
📅 *残り日数:* {days}''',
    'my_subscription_none': '❌ アクティブなサブスクリプションがありません。\n\n/subscribe でプランを購入してください。',
    'my_subscription_history': '📜 *支払い履歴:*',
    'subscription_expiring_soon': '⚠️ {plan}サブスクリプションが{days}日後に期限切れ！\n\n今すぐ更新: /subscribe',
    
    'promo_enter': '🎟 プロモコードを入力:',
    'promo_success': '🎉 プロモコード適用！\n\n{plan}が{days}日間有効化されました。',
    'promo_invalid': '❌ 無効なプロモコード。',
    'promo_expired': '❌ このプロモコードは期限切れです。',
    'promo_used': '❌ このプロモコードは既に使用されています。',
    'promo_already_used': '❌ このプロモコードは既に使用済みです。',
    
    'admin_license_menu': '🔑 *ライセンス管理*',
    'admin_btn_grant_license': '🎁 ライセンス付与',
    'admin_btn_view_licenses': '📋 ライセンス表示',
    'admin_btn_create_promo': '🎟 プロモ作成',
    'admin_btn_view_promos': '📋 プロモ表示',
    'admin_btn_expiring_soon': '⚠️ まもなく期限切れ',
    'admin_grant_select_type': 'ライセンスタイプを選択:',
    'admin_grant_select_period': '期間を選択:',
    'admin_grant_enter_user': 'ユーザーIDを入力:',
    'admin_license_granted': '✅ {plan}をユーザー{uid}に{days}日間付与しました。',
    'admin_license_extended': '✅ ユーザー{uid}のライセンスを{days}日延長しました。',
    'admin_license_revoked': '✅ ユーザー{uid}のライセンスを取り消しました。',
    'admin_promo_created': '✅ プロモコード作成: {code}\nタイプ: {type}\n日数: {days}\n最大使用回数: {max}',

    'admin_users_management': '👥 ユーザー',
    'admin_licenses': '🔑 ライセンス',
    'admin_search_user': '🔍 ユーザー検索',
    'admin_users_menu': '👥 *ユーザー管理*\n\nフィルターまたは検索を選択:',
    'admin_all_users': '👥 全ユーザー',
    'admin_active_users': '✅ アクティブ',
    'admin_banned_users': '🚫 バン済み',
    'admin_no_license': '❌ ライセンスなし',
    'admin_no_users_found': 'ユーザーが見つかりません。',
    'admin_enter_user_id': '🔍 検索するユーザーIDを入力:',
    'admin_user_found': '✅ ユーザー{uid}が見つかりました！',
    'admin_user_not_found': '❌ ユーザー{uid}が見つかりません。',
    'admin_invalid_user_id': '❌ 無効なユーザーID。数字を入力してください。',
    'admin_view_card': '👤 カード表示',
    
    'admin_user_card': '''👤 *ユーザーカード*

📋 *ID:* `{uid}`
{status_emoji} *ステータス:* {status}
📝 *規約:* {terms}

{license_emoji} *ライセンス:* {license_type}
📅 *有効期限:* {license_expires}
⏳ *残り日数:* {days_left}

🌐 *言語:* {lang}
📊 *取引モード:* {trading_mode}
💰 *取引あたり%:* {percent}%
🪙 *コイン:* {coins}

🔌 *APIキー:*
  デモ: {demo_api}
  実: {real_api}

📈 *戦略:* {strategies}

📊 *統計:*
  ポジション: {positions}
  取引: {trades}
  PnL: {pnl}
  勝率: {winrate}%

💳 *支払い:*
  合計: {payments_count}
  TRC: {total_trc}

📅 *初回: {first_seen}
🕐 *最終: {last_seen}
''',
    
    'admin_btn_grant_lic': '🎁 付与',
    'admin_btn_extend': '⏳ 延長',
    'admin_btn_revoke': '🚫 取消',
    'admin_btn_ban': '🚫 バン',
    'admin_btn_unban': '✅ バン解除',
    'admin_btn_approve': '✅ 承認',
    'admin_btn_message': '✉️ メッセージ',
    'admin_btn_delete': '🗑 削除',
    
    'admin_user_banned': 'ユーザーをバンしました！',
    'admin_user_unbanned': 'ユーザーのバンを解除しました！',
    'admin_user_approved': 'ユーザーを承認しました！',
    'admin_confirm_delete': '⚠️ *削除確認*\n\nユーザー{uid}は永久に削除されます！',
    'admin_confirm_yes': '✅ はい、削除',
    'admin_confirm_no': '❌ キャンセル',
    
    'admin_select_license_type': 'ユーザー{uid}のライセンスタイプを選択:',
    'admin_select_period': '期間を選択:',
    'admin_select_extend_days': 'ユーザー{uid}の延長日数を選択:',
    'admin_license_granted_short': 'ライセンス付与完了！',
    'admin_license_extended_short': '{days}日延長しました！',
    'admin_license_revoked_short': 'ライセンス取り消し完了！',
    
    'admin_enter_message': '✉️ ユーザー{uid}に送信するメッセージを入力:',
    'admin_message_sent': '✅ ユーザー{uid}にメッセージを送信しました！',
    'admin_message_failed': '❌ メッセージ送信失敗: {error}',

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
    "hl_trading_enabled": "HyperLiquid取引",
    "hl_reset_settings": "🔄 Bybit設定にリセット",



    # === AUTO-ADDED FROM ENGLISH (needs translation) ===
    'cancelled': '❌ キャンセルしました。',
    'entry_pct_range_error': '❌ エントリー%は0.1から100の間でなければなりません。',
    'hl_no_history': '📭 HyperLiquidに取引履歴がありません。',
    'hl_no_orders': '📭 HyperLiquidに未決注文がありません。',
    'hl_no_positions': '📭 HyperLiquidにオープンポジションがありません。',
    'hl_setup_cancelled': '❌ HyperLiquidの設定がキャンセルされました。',
    'invalid_amount': '❌ 無効な数字です。有効な金額を入力してください。',
    'leverage_range_error': '❌ レバレッジは1から100の間でなければなりません。',
    'max_amount_error': '❌ 最大金額は100,000 USDTです',
    'min_amount_error': '❌ 最小金額は1 USDTです',
    'sl_tp_range_error': '❌ SL/TP%は0.1から500の間でなければなりません。',


    # DCA and Deep Loss notifications
    'btn_enable_dca': '📈 DCA平均化を有効にする',
    'btn_ignore': '🔇 無視する',
    'dca_already_enabled': '✅ DCA平均化は既に有効です！\n\n📊 <b>{symbol}</b>\nボットはドローダウン時に自動的に追加します:\n• -10% → 追加\n• -25% → 追加\n\nこれはエントリー価格を平均化するのに役立ちます。',
    'dca_enable_error': '❌ エラー: {error}',
    'dca_enabled_for_symbol': '✅ DCA平均化が有効になりました！\n\n📊 <b>{symbol}</b>\nボットはドローダウン時に自動的に追加します:\n• -10% → 追加(平均化)\n• -25% → 追加(平均化)\n\n⚠️ DCAには追加注文のための十分な残高が必要です。',
    'deep_loss_alert': '⚠️ <b>ポジションが大きな損失中！</b>\n\n📊 <b>{symbol}</b> ({side})\n📉 損失: <code>{loss_pct:.2f}%</code>\n💰 エントリー: <code>{entry}</code>\n📍 現在: <code>{mark}</code>\n\n❌ ストップロスはエントリー価格より上に設定できません。\n\n<b>どうする？</b>\n• <b>クローズ</b> - 損失を確定\n• <b>DCA</b> - ポジションを平均化\n• <b>無視</b> - そのまま',
    'deep_loss_close_error': '❌ ポジションクローズエラー: {error}',
    'deep_loss_closed': '✅ ポジション {symbol} クローズしました。\n\n損失確定。時には反転を期待するよりも小さな損失を受け入れる方が良いこともあります。',
    'deep_loss_ignored': '🔇 了解、ポジション {symbol} は変更なしで残しました。\n\n⚠️ 注意: ストップロスなしでは損失リスクは無制限です。\n/positions から手動でポジションをクローズできます',
    'fibonacci_desc': '_エントリー、SL、TP - シグナルのフィボナッチレベルから_',
    'fibonacci_info': '📐 *フィボナッチ拡張戦略*',
    'prompt_min_quality': '最小品質 % を入力 (0-100):',


    # Hardcore trading phrase
    'hardcore_mode': '💀 *ハードコアモード*: 容赦なし、後悔なし。利益か死か！ 🔥',

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


    'spot_freq_biweekly': '📅 2週間ごと',
    'spot_trailing_enabled': '✅ Trailing TP有効: +{activation}%で発動、{trail}%トレール',
    'spot_trailing_disabled': '❌ Trailing TP無効',
    'spot_grid_started': '🔲 {coin}のグリッドボット開始: ${low}から${high}まで{levels}レベル',
    'spot_grid_stopped': '⏹ {coin}のグリッドボット停止',
    'spot_limit_placed': '📝 指値注文作成: {coin} {amount}を${price}で購入',
    'spot_limit_cancelled': '❌ {coin}の指値注文がキャンセルされました',
    'spot_freq_hourly': '⏰ 毎時',
}
