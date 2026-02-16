# -*- coding: utf-8 -*-
"""
Enliko Trading Tools — Japanese Translations (日本語)
Version: 4.0.0 | Updated: 28 January 2026
LEGAL: Educational platform, not financial advice.
"""

TEXTS = {
    # Common UI
    'loader': '⏳ 読み込み中...',
    # =====================================================
    # LEGAL DISCLAIMERS (法的免責事項)
    # =====================================================
    
    'disclaimer_trading': (
        '⚠️ *重要な免責事項*\n\n'
        'このプラットフォームは暗号通貨市場について学ぶための教育ツールを提供しています。\n'
        '以下ではありません：\n'
        '• 金融アドバイス\n'
        '• 投資推奨\n'
        '• 保証された利益システム\n\n'
        '暗号通貨取引には重大な損失リスクがあります。'
        '投資の一部または全部を失う可能性があります。'
        '失っても良い資金でのみ取引してください。\n\n'
        '過去の実績は将来の結果を保証しません。'
    ),
    
    'disclaimer_short': '⚠️ _教育ツールのみ。金融アドバイスではありません。取引にはリスクがあります。_',
    
    'disclaimer_execution': (
        '⚠️ 続行することで、以下を認めます：\n'
        '• すべての取引決定に責任を負います\n'
        '• これは教育ツールであり、金融アドバイスではありません\n'
        '• 暗号通貨取引のリスクを理解しています\n'
        '• 過去の実績は将来の結果を保証しません'
    ),
    
    # Welcome - Updated with legal positioning
    'welcome': (
        '📊 *Enliko Trading Toolsへようこそ*\n\n'
        '🎯 教育プラットフォーム:\n'
        '• ポートフォリオ追跡と分析\n'
        '• 戦略バックテスト\n'
        '• 市場データ可視化\n'
        '• リスク管理ツール\n\n'
        '⚠️ _教育目的のみ。金融アドバイスではありません。_\n'
        '_取引には重大な損失リスクがあります。_'
    ),
    
    'welcome_back': (
        '📊 *Enliko Trading Tools*\n\n'
        '⚠️ _教育プラットフォーム。金融アドバイスではありません。_'
    ),
    
    # ═══════════════════════════════════════════════════════════════════
    # MODERN MENU BUTTONS - Stylish & Persuasive
    # ═══════════════════════════════════════════════════════════════════
    'button_orders':               '📊 注文',
    'button_positions':            '🎯 建玉',

    'button_balance': '💎 ポートフォリオ',
    'button_market': '📈 マーケット',
    'button_strategies': '🤖 AI ボット',
    'button_subscribe': '🤝 サポート',
    'button_terminal': '💻 ターミナル',
    'button_terminal': '💻 ターミナル',
    'button_history':              '📜 履歴',
    'button_api_keys':             '🔑 APIキー',
    'button_hyperliquid':          '🔷 HyperLiquid',
    'button_settings':             '⚙️ 設定',

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
    'positions_header':            '📊 保有中の建玉:',

    # Position management (inline)
    'btn_close_position':          '建玉を決済',
    'btn_cancel':                  '❌ キャンセル',
    'btn_back':                    '🔙 戻る',
    'position_already_closed':     '建玉は既に決済済み',
    'position_closed_success':     '建玉を決済しました',
    'position_close_error':        '決済エラー',

    # % per trade

    # Limit-Only toggle
    'limit_only_toggled':          '🔄 指値のみ: {state}',
    'feature_limit_only':          'Limitのみ',
    'feature_oi':                  'OI',
    'feature_rsi_bb':              'RSI+BB',
    'status_enabled':              '✅',
    'status_disabled':             '❌',

    # Indicators
    'indicators_header':           '📈 *Enliko インジケーター*',
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

    # Auto notifications - BLACK RHETORIC: Excitement & Celebration
    'new_position': (
        '🚀🔥 <b>新規ポジションオープン！</b>\n'
        '• {symbol} @ {entry:.6f}\n'
        '• サイズ: {size}\n'
        '📍 {exchange} • {market_type}\n\n'
        '<i>AIがあなたのために働いています！ 🤖</i>'
    ),
    'sl_auto_set':                 '🛑 SL を自動設定: {price:.6f}',
    'auto_close_position':         '⏱ 建玉 {symbol} (TF={tf}) が {tf}超かつ損失のため自動クローズ。',
    'position_closed': (
        '🎉 <b>ポジションクローズ！</b> {symbol}\n'
        '• 理由: <b>{reason}</b>\n'
        '• 戦略: `{strategy}`\n'
        '• エントリー: `{entry:.8f}`\n'
        '• エグジット: `{exit:.8f}`\n'
        '{pnl_emoji} <b>PnL: `{pnl:+.2f} USDT ({pct:+.2f}%)`</b>\n'
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
    'insufficient_balance_error_extended': '❌ <b>残高不足！</b>\n\n📊 戦略: <b>{strategy}</b>\n🪙 シンボル: <b>{symbol}</b> {side}\n\n💰 {account_type}アカウントに十分な資金がありません。\n\n<b>解決策:</b>\n• 残高をチャージする\n• ポジションサイズを縮小 (取引あたりの%)\n• レバレッジを下げる\n• 一部のポジションを決済',

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

    # Enliko (Heatmap)
    'elcaro_limit_entry':          '🔥 *Enliko 指値エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'elcaro_limit_error':          '❌ Enliko 指値エラー: {msg}',
    'elcaro_market_entry':         '🔥 *Enliko 成行エントリー*\n• {symbol} {side}\n• 価格: {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_ok':            '🔥 *Enliko: {side}*\n• {symbol} @ {price:.6f}\n• 数量: {qty}\n• SL: {sl_pct}%',
    'elcaro_market_error':         '❌ Enliko 成行エラー: {msg}',
    'elcaro_analysis':             '🔥 Enliko Heatmap: {side} @ {price}',
    'feature_elcaro':              'Enliko',

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
    'select_language':             '🌍 言語を選択:',
    'language_set':                '✅ 言語が設定されました:',
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

    # API Settings
    'api_key_set':                 '✅ Set',
    'api_test_success':            '接続成功！',
    'api_test_failed':             '接続失敗',
    'balance_equity':              '資産',
    'balance_available':           '利用可能',
    'api_missing_notice':          '⚠️ 取引所のAPIキーが設定されていません。設定でAPIキーとシークレットを追加してください（🔑 APIと🔒 Secretボタン）。そうしないと、ボットはあなたの代わりに取引できません。',
    'elcaro_ai_info':              '🤖 *AI搭載トレーディング*',

    # Spot Trading
    'spot_freq_daily':             'Daily',
    'spot_freq_weekly':            'Weekly',
    'spot_holdings':               '💎 Holdings: {holdings}',
    'spot_balance':                '💰 Spot Balance: {balance}',

    # Strategy trading mode

    # Enliko (Heatmap)

    # Fibonacci (Fibonacci Extension)

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
    'strat_elcaro':                  '🔥 Enliko',
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

    # Break-Even settings UI
    'be_settings_header':            '🔒 *ブレークイーブン設定*',
    'be_settings_desc':              '_利益がトリガー%に達したらSLをエントリー価格に移動_',
    'be_enabled_label':              '🔒 ブレークイーブン',
    'be_trigger_label':              '🎯 BEトリガー %',
    'prompt_be_trigger':             'ブレークイーブントリガー%を入力（例：1.0）:',
    'prompt_long_be_trigger':        '📈 LONG BEトリガー%\n\nSLをエントリーに移動する利益%を入力:',
    'prompt_short_be_trigger':       '📉 SHORT BEトリガー%\n\nSLをエントリーに移動する利益%を入力:',
    'param_be_trigger':              '🎯 BEトリガー %',
    'be_moved_to_entry':             '🔒 {symbol}: SLをブレークイーブン @ {entry} に移動',
    'be_status_enabled':             '✅ BE: {trigger}%',
    'be_status_disabled':            '❌ BE: オフ',

    # Partial Take Profit settings UI
    'partial_tp_label':              '✂️ 部分利確',
    'partial_tp_status_enabled':     '✅ 部分利確有効',
    'partial_tp_status_disabled':    '❌ 部分利確無効',
    'partial_tp_step1_menu':         '✂️ *部分利確 - ステップ1*\n\n+{trigger}%の利益でポジションの{close}%を決済\n\n_パラメータを選択:_',
    'partial_tp_step2_menu':         '✂️ *部分利確 - ステップ2*\n\n+{trigger}%の利益でポジションの{close}%を決済\n\n_パラメータを選択:_',
    'trigger_pct':                   'トリガー',
    'close_pct':                     '決済',
    'prompt_long_ptp_1_trigger':     '📈 LONG ステップ1: トリガー%\n\n最初の部分を決済する利益%を入力:',
    'prompt_long_ptp_1_close':       '📈 LONG ステップ1: 決済%\n\n決済するポジション%を入力:',
    'prompt_long_ptp_2_trigger':     '📈 LONG ステップ2: トリガー%\n\n2番目の部分を決済する利益%を入力:',
    'prompt_long_ptp_2_close':       '📈 LONG ステップ2: 決済%\n\n決済するポジション%を入力:',
    'prompt_short_ptp_1_trigger':    '📉 SHORT ステップ1: トリガー%\n\n最初の部分を決済する利益%を入力:',
    'prompt_short_ptp_1_close':      '📉 SHORT ステップ1: 決済%\n\n決済するポジション%を入力:',
    'prompt_short_ptp_2_trigger':    '📉 SHORT ステップ2: トリガー%\n\n2番目の部分を決済する利益%を入力:',
    'prompt_short_ptp_2_close':      '📉 SHORT ステップ2: 決済%\n\n決済するポジション%を入力:',
    'partial_tp_executed':           '✂️ {symbol}: +{trigger}%の利益で{close}%を決済',

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
    'param_leverage': '⚡ レバレッジ',
    'prompt_leverage': 'レバレッジを入力 (1-100):',
    'auto_default': '自動',

    # Enliko AI
    'elcaro_ai_desc': '_すべてのパラメータはAIシグナルから自動で解析されます:_',

    # Scalper entries

    # Scryptomera feature
    

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
    
    # License status messages - BLACK RHETORIC: Loss Aversion + FOMO
    'no_license': '🤝 *Community Membership*\n\nSupport our open-source project to access\nadditional community resources.\n\n👉 /subscribe — Support the project',
    'no_license_trading': '🤝 *Community Resource*\n\nThis resource is available to community supporters.\n\n👉 /subscribe — Support the project',
    'license_required': '🔒 *Supporter Resource*\n\nThis resource requires {required} membership.\n\n👉 /subscribe — Support the project',
    'trial_demo_only': '⚠️ *Explorer Access*\n\nExplorer access is limited to demo environment.\n\n👉 /subscribe — Become a supporter',
    'basic_strategy_limit': '⚠️ *Community Tier*\n\nAvailable templates: {strategies}\n\n👉 /subscribe — Upgrade your support',
    'subscribe_menu_header': '🤝 *Support Enliko*\n\nYour voluntary contribution helps maintain\nfree open-source community tools.\n\nChoose your support level:',
    'subscribe_menu_info': '_Select your support level:_',
    'btn_premium': '💎 Pro',
    'btn_basic': '💚 サポーター',
    'btn_trial': '🆓 お試し (無料)',
    'btn_enter_promo': '🎟 招待コード',
    'btn_my_subscription': '📋 メンバーシップ',
    'premium_title': '💎 *Pro Plan*',
    'premium_desc': '*Full access to all tools:*\n\n✅ All trading strategies\n✅ Demo & live environments\n✅ Priority support\n✅ ATR risk management\n✅ DCA configuration\n✅ All platform updates\n\n⚠️ _Trading involves risk. Not financial advice._',
    'premium_1m': '💎 1 Month — {price} ELC',
    'premium_3m': '💎 3 Months — {price} ELC',
    'premium_6m': '💎 6 Months — {price} ELC',
    'premium_12m': '💎 12 Months — {price} ELC',
    'basic_title': '💚 *Supporter Membership*',
    'basic_desc': '*Thank you for your support!*\n\n✅ Demo + live environments\n✅ Templates: OI, RSI+BB\n✅ Bybit integration\n✅ ATR risk management tools\n\n⚠️ _Educational tools only. Not financial advice._',
    'basic_1m': '💚 1 Month — {price} ELC',
    'trial_title': '🆓 *Explorer Access — 14 Days*',
    'trial_desc': '*Explore our community tools:*\n\n✅ Full demo environment\n✅ All analysis templates\n✅ 14 days access\n✅ No contribution required\n\n⚠️ _Educational tools only. Not financial advice._',
    'trial_activate': '🆓 Start Exploring',
    'trial_already_used': '⚠️ Explorer access already used. Consider supporting the project.',
    'trial_activated': '🎉 *Explorer Access Activated!*\n\n⏰ 14 days of full demo access.\n\n⚠️ _Educational tools only. Not financial advice._',
    'payment_select_method': '🤝 *How would you like to contribute?*',
    'btn_pay_elc': '◈ ELC',
    'btn_pay_ton': '💎 TON',
    'payment_elc_title': '◈ Enliko Coin (ELC)での支払い',
    'payment_elc_desc': '{plan}（{period}）に{amount} ELCが請求されます。',
    'payment_ton_title': '💎 TONでの支払い',
    'payment_ton_desc': '''正確に*{amount} TON*を以下に送金:

`{wallet}`

支払い後、下のボタンをクリックして確認。''',
    'btn_verify_ton': '✅ 支払い済み — 確認',
    'payment_processing': '⏳ ...',
    'payment_success': '🎉 Thank you for your support!\n\n{plan} access activated until {expires}.',
    'payment_failed': '❌ Contribution failed: {error}',
    'my_subscription_header': '📋 *My Membership*',
    'my_subscription_active': '''📋 *現在のプラン:* {plan}
⏰ *有効期限:* {expires}
📅 *残り日数:* {days}''',
    'my_subscription_none': '❌ No active membership.\n\nUse /subscribe to support the project.',
    'my_subscription_history': '📜 *支払い履歴:*',
    'subscription_expiring_soon': '⚠️ {plan}サブスクリプションが{days}日後に期限切れ！\n\n今すぐ更新: /subscribe',
    
    'promo_enter': '🎟 Enter your invite code:',
    'promo_success': '🎉 Invite code applied!\n\n{plan} access for {days} days.',
    'promo_invalid': '❌ Invalid invite code.',
    'promo_expired': '❌ This invite code has expired.',
    'promo_used': '❌ This invite code has already been used.',
    'promo_already_used': '❌ You have already used this invite code.',
    'admin_license_menu': '🤝 *Membership Management*',
    'admin_btn_grant_license': '🎁 Grant Access',
    'admin_btn_view_licenses': '📋 View Members',
    'admin_btn_create_promo': '🎟 Create Invite',
    'admin_btn_view_promos': '📋 View Invites',
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
  ELC: {total_elc}

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
    'admin_all_payments': '📜 すべての支払い',
    'admin_demo_stats': '🎮 デモ統計',
    'admin_enter_user_for_report': '👤 詳細レポートのユーザーIDを入力:',
    'admin_generating_report': '📊 ユーザー {uid} のレポートを生成中...',
    'admin_global_stats': '📊 グローバル統計',
    'admin_no_payments_found': '支払いが見つかりません。',
    'admin_payments': '💳 支払い',
    'admin_payments_menu': '💳 *支払い管理*',
    'admin_real_stats': '💰 リアル統計',
    'admin_reports': '📊 レポート',
    'admin_reports_menu': '''📊 *レポートと分析*

レポートタイプを選択:''',
    'admin_strategy_breakdown': '🎯 戦略別',
    'admin_top_traders': '🏆 トップトレーダー',
    'admin_user_report': '👤 ユーザーレポート',
    'admin_view_report': '📊 レポートを見る',
    'admin_view_user': '👤 ユーザーカード',
    'btn_check_again': '🔄 Check',
    'payment_session_expired': '❌ 支払いセッションが期限切れです。最初からやり直してください。',
    'payment_ton_not_configured': '❌ TON支払いは設定されていません。',
    'payment_verifying': '⏳ 支払い確認中...',
    'stats_fibonacci': '📐 フィボナッチ',

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

    # Wallet & ELC translations

    'payment_elc_insufficient': '''❌ ELC残高が不足しています。

現在の残高: {balance} ELC
必要額: {required} ELC

続行するにはウォレットをチャージしてください。''',
    'wallet_address': '''📍 アドレス: `{address}`''',
    'wallet_balance': '''💰 *あなたのELCウォレット*

◈ 残高: *{balance} ELC*
📈 ステーク中: *{staked} ELC*
🎁 保留中の報酬: *{rewards} ELC*

💵 合計価値: *${total_usd}*
📍 1 ELC = 1 USDT''',
    'wallet_btn_back': '''« 戻る''',
    'wallet_btn_deposit': '''📥 入金''',
    'wallet_btn_history': '''📋 履歴''',
    'wallet_btn_stake': '''📈 ステーク''',
    'wallet_btn_unstake': '''📤 アンステーク''',
    'wallet_btn_withdraw': '''📤 出金''',
    'wallet_deposit_demo': '''🎁 100 ELCを取得 (デモ)''',
    'wallet_deposit_desc': '''ELCトークンをウォレットアドレスに送信してください:

`{address}`

💡 *デモモード:* 以下をクリックして無料テストトークンを取得。''',
    'wallet_deposit_success': '''✅ {amount} ELCの入金に成功しました！''',
    'wallet_deposit_title': '''📥 *ELC入金*''',
    'wallet_history_empty': '''取引はまだありません。''',
    'wallet_history_item': '''{type_emoji} {type}: {amount:+.2f} ELC
   {date}''',
    'wallet_history_title': '''📋 *取引履歴*''',
    'wallet_stake_desc': '''ELCをステークして*年力12%*を稼ぎましょう！

💰 利用可能: {available} ELC
📈 現在ステーク中: {staked} ELC
🎁 保留中の報酬: {rewards} ELC

毎日報酬 • 即時アンステーク''',
    'wallet_stake_success': '''✅ {amount} ELCのステークに成功しました！''',
    'wallet_stake_title': '''📈 *ELCステーク*''',
    'wallet_title': '''◈ *ELCウォレット*''',
    'wallet_unstake_success': '''✅ {amount} ELC + {rewards} ELC報酬を引き出しました！''',
    'wallet_withdraw_desc': '''宛先アドレスと金額を入力してください:''',
    'wallet_withdraw_failed': '''❌ 出金に失敗しました: {error}''',
    'wallet_withdraw_success': '''✅ {amount} ELCを{address}に出金しました''',
    'wallet_withdraw_title': '''📤 *ELC出金*''',

    'spot_freq_hourly': '⏰ 毎時',

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
    'error_insufficient_balance': '💰 ポジションを開くための残高が不足しています。残高をチャージするか、ポジションサイズを減らしてください。',
    'error_order_too_small': '📉 注文サイズが小さすぎます（最小$5）。Entry%を増やすか、残高をチャージしてください。',
    'error_api_key_expired': '🔑 APIキーが期限切れまたは無効です。設定でAPIキーを更新してください。',
    'error_api_key_missing': '🔑 APIキーが設定されていません。🔗 API KeysメニューでBybitキーを追加してください。',
    'error_rate_limit': '⏳ リクエストが多すぎます。1分待ってから再試行してください。',
    'error_position_not_found': '📊 ポジションが見つからないか、既にクローズされています。',
    'error_leverage_error': '⚙️ レバレッジ設定エラー。取引所で手動でレバレッジを設定してみてください。',
    'error_network_error': '🌐 ネットワークの問題。後でもう一度お試しください。',
    'error_sl_tp_invalid': '⚠️ SL/TPを設定できません：価格が現在価格に近すぎます。次のサイクルで更新されます。',
    'error_equity_zero': '💰 アカウント残高がゼロです。取引するにはDemoまたはRealアカウントをチャージしてください。',
    
    # =====================================================
    # HARDCODED STRINGS FIX (Jan 27, 2026)
    # =====================================================
    'terminal_button': '💻 ターミナル',
    'exchange_mode_activated_bybit': '🟠 *Bybitモード有効*',
    'exchange_mode_activated_hl': '🔷 *HyperLiquidモード有効*',
    'error_processing_request': '⚠️ リクエストの処理中にエラーが発生しました',
    'unauthorized_admin': '❌ 権限がありません。このコマンドは管理者専用です。',
    'error_loading_dashboard': '❌ ダッシュボードの読み込みエラー。',
    'unauthorized': '❌ 権限がありません。',
    'processing_blockchain': '⏳ ブロックチェーン取引を処理中...',
    'verifying_payment': '⏳ TONブロックチェーンで支払いを検証中...',
    'no_wallet_configured': '❌ ウォレットが設定されていません。',
    'use_start_menu': 'メインメニューに戻るには /start を使用してください。',

    # 2FA ログイン確認
    'login_approved': '✅ ログインが承認されました！\n\nブラウザで続行できます。',
    'login_denied': '❌ ログインが拒否されました。\n\n心当たりがない場合は、セキュリティ設定を確認してください。',
    'login_expired': '⏰ 確認の有効期限が切れました。もう一度お試しください。',
    'login_error': '⚠️ 処理エラー。後でもう一度お試しください。',

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
    "basic_bybit_only": "⚠️ *Basic Plan Limitation*\n\nBasic plan supports Bybit only.\nHyperLiquid is available on Pro plan.\n\n👉 /subscribe — Upgrade to Pro",
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


    # Daily Digest
    'digest_title': '📊 デイリーレポート',
    'digest_detailed_title': '📋 詳細レポート',
    'digest_date_format': '%Y年%m月%d日',
    'digest_filter_all': '🌍 全取引所',
    'digest_no_trades': '📭 該当する取引がありません',
    'digest_no_trades_hint': '別のフィルターをお試しください。',
    'digest_total_pnl': '合計PnL',
    'digest_statistics': '統計',
    'digest_trades': '取引',
    'digest_wins_losses': '勝ち/負け',
    'digest_win_rate': '勝率',
    'digest_avg_pnl': '平均PnL',
    'digest_best_trade': 'ベスト取引',
    'digest_worst_trade': 'ワースト取引',
    'digest_keep_improving': '改善を続けよう！ 💪',
    'digest_vibe_amazing': '素晴らしい日！',
    'digest_vibe_nice': 'いい仕事！',
    'digest_vibe_breakeven': '収支トントン',
    'digest_vibe_small_loss': '小さな損失',
    'digest_vibe_tough': '厳しい日',
    'digest_btn_all': '全て',
    'digest_btn_bybit': '🟠 Bybit',
    'digest_btn_hl': '🔷 HL',
    'digest_btn_demo': '🧪 デモ',
    'digest_btn_real': '💼 リアル',
    'digest_btn_testnet': '🧪 テストネット',
    'digest_btn_mainnet': '🌐 メインネット',
    'digest_btn_detailed': '📋 詳細',
    'digest_btn_close': '❌ 閉じる',
    'digest_btn_back': '◀️ 戻る',
    'digest_by_exchange': '取引所別',
    'digest_by_strategy': '戦略別',
    'digest_top_symbols': 'トップ銘柄',
    'digest_filter_bybit': '🟠 Bybit',
    'digest_filter_hl': '🔷 HyperLiquid',
    'digest_filter_demo': '🧪 デモ',
    'digest_filter_real': '💼 リアル',
    'digest_filter_testnet': '🧪 テストネット',
    'digest_filter_mainnet': '🌐 メインネット',
    'stats_testnet': '🧪 Testnet',
    'stats_mainnet': '🌐 Mainnet',
    'trades_title': 'Trade History',
    'trades_list_btn': 'Trade List',
    'trades_page': 'Page',
    'trades_total': 'trades',
    'trades_empty': 'No trades found for this filter.',
    'trades_to_stats': 'Statistics',
}
