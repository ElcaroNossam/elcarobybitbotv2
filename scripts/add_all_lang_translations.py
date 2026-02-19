#!/usr/bin/env python3
"""
Add missing keys to ALL 12 remaining languages in LocalizationManager.swift.
Uses proper native translations for key UI elements.
For less visible keys, uses English as placeholder (better than raw keys).
"""

SWIFT_FILE = "ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift"

import re

def extract_keys(marker, content):
    idx = content.find(marker)
    if idx == -1:
        return set()
    bracket_start = content.find("return [", idx)
    if bracket_start == -1:
        return set()
    bracket_start = content.index("[", bracket_start)
    depth = 0
    end = bracket_start
    for i in range(bracket_start, len(content)):
        if content[i] == "[":
            depth += 1
        elif content[i] == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    section = content[bracket_start:end + 1]
    keys = set(re.findall(r'"([^"]+)":', section))
    return keys

def extract_en_dict(content):
    """Extract English key-value pairs."""
    idx = content.find("// MARK: - English (Reference)")
    bracket_start = content.find("return [", idx)
    bracket_start = content.index("[", bracket_start)
    depth = 0
    end = bracket_start
    for i in range(bracket_start, len(content)):
        if content[i] == "[":
            depth += 1
        elif content[i] == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    section = content[bracket_start:end + 1]
    pairs = re.findall(r'"([^"]+)":\s*"([^"]*)"', section)
    return dict(pairs)

def add_keys_to_section(content, section_marker, keys_dict):
    idx = content.find(section_marker)
    if idx == -1:
        return content
    ret_idx = content.find("return [", idx)
    if ret_idx == -1:
        return content
    bracket_start = content.index("[", ret_idx)
    depth = 0
    close_bracket = bracket_start
    for i in range(bracket_start, len(content)):
        if content[i] == "[":
            depth += 1
        elif content[i] == "]":
            depth -= 1
            if depth == 0:
                close_bracket = i
                break
    entries = []
    for key, value in sorted(keys_dict.items()):
        escaped_value = value.replace('"', '\\"')
        entries.append(f'        "{key}": "{escaped_value}",')
    new_block = "\n        // Auto-synced from English\n" + "\n".join(entries) + "\n    "
    content = content[:close_bracket] + new_block + content[close_bracket:]
    return content

# Native translations for key UI strings per language
# Format: { lang_marker: { key: native_translation } }
NATIVE_OVERRIDES = {
    "German": {
        "settings": "Einstellungen", "language": "Sprache", "premium": "Premium",
        "notifications": "Benachrichtigungen", "logout": "Abmelden",
        "trade_history": "Handelshistorie", "trading": "Handel",
        "portfolio_title": "Portfolio", "strategies_title": "Strategien",
        "strategy_settings": "Strategieeinstellungen", "quick_tools": "Schnellzugriff",
        "futures": "Futures", "spot": "Spot", "buy": "Kaufen",
        "leverage": "Hebel", "stop_loss": "Stop-Loss", "take_profit": "Take-Profit",
        "save_settings": "Speichern", "history": "Geschichte",
        "market_overview": "Marktübersicht", "full_screener": "Vollständiger Screener",
        "tokens": "Token", "connected": "Verbunden", "active": "Aktiv",
        "configure_all_strategies": "Alle Strategien konfigurieren",
        "screener": "Screener", "signals": "Signale", "stats": "Statistiken",
        "more": "Mehr", "activity": "Aktivität", "ai": "KI",
        "tap_to_configure": "Tippe zum Konfigurieren",
        "trading_close_position": "Position schließen", "trading_cancel_order": "Order stornieren",
        "trading_order_placed": "Order platziert", "trading_entry_price": "Einstiegspreis",
        "trading_current_price": "Aktueller Preis", "trading_leverage": "Hebel",
        "trading_tab_positions": "Positionen", "trading_tab_orders": "Orders",
        "trading_tab_history": "Geschichte", "trading_place_long": "Long eröffnen",
        "trading_place_short": "Short eröffnen", "trading_quantity": "Menge",
        "futures_balance": "Futures-Saldo", "no_orders_subtitle": "Keine aktiven Orders",
        "no_positions_subtitle": "Keine offenen Positionen",
        "quick_tools": "Schnellzugriff", "synced_at": "Synchronisiert",
        "history_empty": "Verlauf leer", "history_no_trades": "Keine Trades",
        "history_title": "Geschichte", "exchange": "Börse",
        "manage_alerts": "Benachrichtigungen verwalten",
        "trading_long": "Long", "trading_short": "Short",
        "trading_24h_change": "24h Änderung", "trading_24h_volume": "24h Volumen",
        "disconnected": "Getrennt",
        "trading_liq_price": "Liquidationspreis", "trading_mark_price": "Markpreis",
        "trading_margin_required": "Erforderliche Margin", "trading_order_value": "Orderwert",
        "trading_open_interest": "Open Interest", "trading_order_failed": "Order fehlgeschlagen",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "Order",
    },
    "Spanish": {
        "settings": "Configuración", "language": "Idioma", "premium": "Premium",
        "notifications": "Notificaciones", "logout": "Cerrar sesión",
        "trade_history": "Historial de operaciones", "trading": "Trading",
        "portfolio_title": "Portafolio", "strategies_title": "Estrategias",
        "strategy_settings": "Configuración de estrategias", "quick_tools": "Herramientas rápidas",
        "futures": "Futuros", "spot": "Spot", "buy": "Comprar",
        "leverage": "Apalancamiento", "stop_loss": "Stop Loss", "take_profit": "Take Profit",
        "save_settings": "Guardar", "history": "Historial",
        "market_overview": "Resumen del mercado", "full_screener": "Screener completo",
        "tokens": "Tokens", "connected": "Conectado", "active": "Activo",
        "configure_all_strategies": "Configurar todas las estrategias",
        "screener": "Screener", "signals": "Señales", "stats": "Estadísticas",
        "more": "Más", "activity": "Actividad", "ai": "IA",
        "tap_to_configure": "Toca para configurar",
        "trading_close_position": "Cerrar posición", "trading_cancel_order": "Cancelar orden",
        "trading_order_placed": "Orden colocada", "trading_entry_price": "Precio de entrada",
        "trading_current_price": "Precio actual", "trading_leverage": "Apalancamiento",
        "trading_tab_positions": "Posiciones", "trading_tab_orders": "Órdenes",
        "trading_tab_history": "Historial", "trading_place_long": "Abrir Long",
        "trading_place_short": "Abrir Short", "trading_quantity": "Cantidad",
        "futures_balance": "Balance de futuros", "no_orders_subtitle": "Sin órdenes activas",
        "no_positions_subtitle": "Sin posiciones abiertas",
        "synced_at": "Sincronizado", "exchange": "Exchange",
        "history_empty": "Historial vacío", "history_no_trades": "Sin operaciones",
        "history_title": "Historial", "disconnected": "Desconectado",
        "manage_alerts": "Gestionar alertas",
        "trading_long": "Long", "trading_short": "Short",
        "trading_24h_change": "Cambio 24h", "trading_24h_volume": "Volumen 24h",
        "trading_liq_price": "Precio liquidación", "trading_mark_price": "Precio marca",
        "trading_margin_required": "Margen requerido", "trading_order_value": "Valor de orden",
        "trading_open_interest": "Interés abierto", "trading_order_failed": "Orden fallida",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "Orden",
    },
    "French": {
        "settings": "Paramètres", "language": "Langue", "premium": "Premium",
        "notifications": "Notifications", "logout": "Déconnexion",
        "trade_history": "Historique des trades", "trading": "Trading",
        "portfolio_title": "Portefeuille", "strategies_title": "Stratégies",
        "strategy_settings": "Configuration des stratégies", "quick_tools": "Outils rapides",
        "futures": "Futures", "spot": "Spot", "buy": "Acheter",
        "leverage": "Levier", "stop_loss": "Stop Loss", "take_profit": "Take Profit",
        "save_settings": "Enregistrer", "history": "Historique",
        "market_overview": "Aperçu du marché", "full_screener": "Screener complet",
        "tokens": "Jetons", "connected": "Connecté", "active": "Actif",
        "configure_all_strategies": "Configurer toutes les stratégies",
        "screener": "Screener", "signals": "Signaux", "stats": "Statistiques",
        "more": "Plus", "activity": "Activité", "ai": "IA",
        "tap_to_configure": "Appuyez pour configurer",
        "trading_close_position": "Fermer la position", "trading_cancel_order": "Annuler l'ordre",
        "trading_order_placed": "Ordre placé", "trading_entry_price": "Prix d'entrée",
        "trading_current_price": "Prix actuel", "trading_leverage": "Levier",
        "trading_tab_positions": "Positions", "trading_tab_orders": "Ordres",
        "trading_tab_history": "Historique", "trading_place_long": "Ouvrir Long",
        "trading_place_short": "Ouvrir Short", "trading_quantity": "Quantité",
        "futures_balance": "Solde futures", "no_orders_subtitle": "Aucun ordre actif",
        "no_positions_subtitle": "Aucune position ouverte",
        "synced_at": "Synchronisé", "exchange": "Exchange",
        "history_empty": "Historique vide", "history_no_trades": "Aucun trade",
        "history_title": "Historique", "disconnected": "Déconnecté",
        "manage_alerts": "Gérer les alertes",
        "trading_long": "Long", "trading_short": "Short",
        "trading_24h_change": "Variation 24h", "trading_24h_volume": "Volume 24h",
        "trading_liq_price": "Prix liquidation", "trading_mark_price": "Prix mark",
        "trading_margin_required": "Marge requise", "trading_order_value": "Valeur de l'ordre",
        "trading_open_interest": "Intérêt ouvert", "trading_order_failed": "Ordre échoué",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "Ordre",
    },
    "Italian": {
        "settings": "Impostazioni", "language": "Lingua", "premium": "Premium",
        "notifications": "Notifiche", "logout": "Esci",
        "trade_history": "Cronologia operazioni", "trading": "Trading",
        "portfolio_title": "Portafoglio", "strategies_title": "Strategie",
        "strategy_settings": "Impostazioni strategia", "quick_tools": "Strumenti rapidi",
        "futures": "Futures", "spot": "Spot", "buy": "Compra",
        "leverage": "Leva", "stop_loss": "Stop Loss", "take_profit": "Take Profit",
        "save_settings": "Salva", "history": "Cronologia",
        "market_overview": "Panoramica mercato", "full_screener": "Screener completo",
        "tokens": "Token", "connected": "Connesso", "active": "Attivo",
        "configure_all_strategies": "Configura tutte le strategie",
        "screener": "Screener", "signals": "Segnali", "stats": "Statistiche",
        "more": "Altro", "activity": "Attività", "ai": "IA",
        "tap_to_configure": "Tocca per configurare",
        "trading_close_position": "Chiudi posizione", "trading_cancel_order": "Annulla ordine",
        "trading_order_placed": "Ordine inserito", "trading_entry_price": "Prezzo di ingresso",
        "trading_current_price": "Prezzo attuale", "trading_leverage": "Leva",
        "trading_tab_positions": "Posizioni", "trading_tab_orders": "Ordini",
        "trading_tab_history": "Cronologia", "trading_place_long": "Apri Long",
        "trading_place_short": "Apri Short", "trading_quantity": "Quantità",
        "futures_balance": "Saldo futures", "no_orders_subtitle": "Nessun ordine attivo",
        "no_positions_subtitle": "Nessuna posizione aperta",
        "synced_at": "Sincronizzato", "exchange": "Exchange",
        "history_empty": "Cronologia vuota", "history_no_trades": "Nessun trade",
        "history_title": "Cronologia", "disconnected": "Disconnesso",
        "manage_alerts": "Gestisci avvisi",
        "trading_long": "Long", "trading_short": "Short",
        "trading_24h_change": "Variazione 24h", "trading_24h_volume": "Volume 24h",
        "trading_liq_price": "Prezzo liquidazione", "trading_mark_price": "Prezzo mark",
        "trading_margin_required": "Margine richiesto", "trading_order_value": "Valore ordine",
        "trading_open_interest": "Open Interest", "trading_order_failed": "Ordine fallito",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "Ordine",
    },
    "Japanese": {
        "settings": "設定", "language": "言語", "premium": "プレミアム",
        "notifications": "通知", "logout": "ログアウト",
        "trade_history": "取引履歴", "trading": "トレード",
        "portfolio_title": "ポートフォリオ", "strategies_title": "戦略",
        "strategy_settings": "戦略設定", "quick_tools": "クイックツール",
        "futures": "先物", "spot": "現物", "buy": "購入",
        "leverage": "レバレッジ", "stop_loss": "ストップロス", "take_profit": "テイクプロフィット",
        "save_settings": "保存", "history": "履歴",
        "market_overview": "市場概要", "full_screener": "フルスクリーナー",
        "tokens": "トークン", "connected": "接続済み", "active": "アクティブ",
        "configure_all_strategies": "全戦略を設定",
        "screener": "スクリーナー", "signals": "シグナル", "stats": "統計",
        "more": "その他", "activity": "アクティビティ", "ai": "AI",
        "tap_to_configure": "タップして設定",
        "trading_close_position": "ポジション決済", "trading_cancel_order": "注文キャンセル",
        "trading_order_placed": "注文完了", "trading_entry_price": "エントリー価格",
        "trading_current_price": "現在価格", "trading_leverage": "レバレッジ",
        "trading_tab_positions": "ポジション", "trading_tab_orders": "注文",
        "trading_tab_history": "履歴", "trading_place_long": "ロング注文",
        "trading_place_short": "ショート注文", "trading_quantity": "数量",
        "futures_balance": "先物残高", "no_orders_subtitle": "アクティブな注文なし",
        "no_positions_subtitle": "オープンポジションなし",
        "synced_at": "同期済み", "exchange": "取引所",
        "history_empty": "履歴なし", "history_no_trades": "取引なし",
        "history_title": "履歴", "disconnected": "切断",
        "manage_alerts": "アラート管理",
        "trading_long": "ロング", "trading_short": "ショート",
        "trading_24h_change": "24h変動", "trading_24h_volume": "24h出来高",
        "trading_liq_price": "清算価格", "trading_mark_price": "マーク価格",
        "trading_margin_required": "必要証拠金", "trading_order_value": "注文金額",
        "trading_open_interest": "建玉", "trading_order_failed": "注文失敗",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "注文",
    },
    "Chinese": {
        "settings": "设置", "language": "语言", "premium": "高级版",
        "notifications": "通知", "logout": "退出登录",
        "trade_history": "交易历史", "trading": "交易",
        "portfolio_title": "投资组合", "strategies_title": "策略",
        "strategy_settings": "策略设置", "quick_tools": "快捷工具",
        "futures": "合约", "spot": "现货", "buy": "买入",
        "leverage": "杠杆", "stop_loss": "止损", "take_profit": "止盈",
        "save_settings": "保存", "history": "历史",
        "market_overview": "市场概览", "full_screener": "完整筛选器",
        "tokens": "代币", "connected": "已连接", "active": "活跃",
        "configure_all_strategies": "配置所有策略",
        "screener": "筛选器", "signals": "信号", "stats": "统计",
        "more": "更多", "activity": "活动", "ai": "AI",
        "tap_to_configure": "点击配置",
        "trading_close_position": "平仓", "trading_cancel_order": "取消订单",
        "trading_order_placed": "下单成功", "trading_entry_price": "入场价",
        "trading_current_price": "当前价", "trading_leverage": "杠杆",
        "trading_tab_positions": "持仓", "trading_tab_orders": "订单",
        "trading_tab_history": "历史", "trading_place_long": "开多",
        "trading_place_short": "开空", "trading_quantity": "数量",
        "futures_balance": "合约余额", "no_orders_subtitle": "无活跃订单",
        "no_positions_subtitle": "无持仓",
        "synced_at": "已同步", "exchange": "交易所",
        "history_empty": "历史为空", "history_no_trades": "无交易",
        "history_title": "历史", "disconnected": "已断开",
        "manage_alerts": "管理提醒",
        "trading_long": "做多", "trading_short": "做空",
        "trading_24h_change": "24h涨跌", "trading_24h_volume": "24h成交量",
        "trading_liq_price": "强平价", "trading_mark_price": "标记价",
        "trading_margin_required": "所需保证金", "trading_order_value": "订单价值",
        "trading_open_interest": "持仓量", "trading_order_failed": "下单失败",
        "trading_tp_sl_section": "止盈/止损", "trading_tab_order": "下单",
    },
    "Arabic": {
        "settings": "الإعدادات", "language": "اللغة", "premium": "بريميوم",
        "notifications": "الإشعارات", "logout": "تسجيل الخروج",
        "trade_history": "سجل التداول", "trading": "التداول",
        "portfolio_title": "المحفظة", "strategies_title": "الاستراتيجيات",
        "strategy_settings": "إعدادات الاستراتيجية", "quick_tools": "أدوات سريعة",
        "futures": "العقود الآجلة", "spot": "فوري", "buy": "شراء",
        "leverage": "الرافعة المالية", "stop_loss": "وقف الخسارة", "take_profit": "جني الأرباح",
        "save_settings": "حفظ", "history": "السجل",
        "market_overview": "نظرة عامة على السوق", "full_screener": "ماسح كامل",
        "tokens": "الرموز", "connected": "متصل", "active": "نشط",
        "configure_all_strategies": "تكوين جميع الاستراتيجيات",
        "screener": "الماسح", "signals": "إشارات", "stats": "إحصائيات",
        "more": "المزيد", "activity": "النشاط", "ai": "ذكاء اصطناعي",
        "tap_to_configure": "انقر للتكوين",
        "trading_close_position": "إغلاق المركز", "trading_cancel_order": "إلغاء الأمر",
        "trading_order_placed": "تم وضع الأمر", "trading_entry_price": "سعر الدخول",
        "trading_current_price": "السعر الحالي", "trading_leverage": "الرافعة",
        "trading_tab_positions": "المراكز", "trading_tab_orders": "الأوامر",
        "trading_tab_history": "السجل", "trading_place_long": "فتح لونج",
        "trading_place_short": "فتح شورت", "trading_quantity": "الكمية",
        "futures_balance": "رصيد العقود", "no_orders_subtitle": "لا توجد أوامر نشطة",
        "no_positions_subtitle": "لا توجد مراكز مفتوحة",
        "synced_at": "تمت المزامنة", "exchange": "المنصة",
        "history_empty": "السجل فارغ", "history_no_trades": "لا توجد صفقات",
        "history_title": "السجل", "disconnected": "غير متصل",
        "manage_alerts": "إدارة التنبيهات",
        "trading_long": "لونج", "trading_short": "شورت",
        "trading_24h_change": "تغيير 24س", "trading_24h_volume": "حجم 24س",
        "trading_liq_price": "سعر التصفية", "trading_mark_price": "سعر العلامة",
        "trading_margin_required": "الهامش المطلوب", "trading_order_value": "قيمة الأمر",
        "trading_open_interest": "الفائدة المفتوحة", "trading_order_failed": "فشل الأمر",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "أمر",
    },
    "Hebrew": {
        "settings": "הגדרות", "language": "שפה", "premium": "פרימיום",
        "notifications": "התראות", "logout": "התנתק",
        "trade_history": "היסטוריית מסחר", "trading": "מסחר",
        "portfolio_title": "תיק השקעות", "strategies_title": "אסטרטגיות",
        "strategy_settings": "הגדרות אסטרטגיה", "quick_tools": "כלים מהירים",
        "futures": "חוזים עתידיים", "spot": "ספוט", "buy": "קנייה",
        "leverage": "מינוף", "stop_loss": "סטופ לוס", "take_profit": "טייק פרופיט",
        "save_settings": "שמור", "history": "היסטוריה",
        "market_overview": "סקירת שוק", "full_screener": "סורק מלא",
        "tokens": "טוקנים", "connected": "מחובר", "active": "פעיל",
        "configure_all_strategies": "הגדר את כל האסטרטגיות",
        "screener": "סורק", "signals": "איתותים", "stats": "סטטיסטיקה",
        "more": "עוד", "activity": "פעילות", "ai": "בינה מלאכותית",
        "tap_to_configure": "הקש להגדרה",
        "trading_close_position": "סגור פוזיציה", "trading_cancel_order": "בטל הוראה",
        "trading_order_placed": "הוראה בוצעה", "trading_entry_price": "מחיר כניסה",
        "trading_current_price": "מחיר נוכחי", "trading_leverage": "מינוף",
        "trading_tab_positions": "פוזיציות", "trading_tab_orders": "הוראות",
        "trading_tab_history": "היסטוריה", "trading_place_long": "פתח לונג",
        "trading_place_short": "פתח שורט", "trading_quantity": "כמות",
        "futures_balance": "יתרת חוזים", "no_orders_subtitle": "אין הוראות פעילות",
        "no_positions_subtitle": "אין פוזיציות פתוחות",
        "synced_at": "מסונכרן", "exchange": "בורסה",
        "history_empty": "היסטוריה ריקה", "history_no_trades": "אין עסקאות",
        "history_title": "היסטוריה", "disconnected": "מנותק",
        "manage_alerts": "ניהול התראות",
        "trading_long": "לונג", "trading_short": "שורט",
        "trading_24h_change": "שינוי 24ש", "trading_24h_volume": "נפח 24ש",
        "trading_liq_price": "מחיר חיסול", "trading_mark_price": "מחיר סימון",
        "trading_margin_required": "ביטחונות נדרשים", "trading_order_value": "ערך הוראה",
        "trading_open_interest": "פוזיציות פתוחות", "trading_order_failed": "הוראה נכשלה",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "הוראה",
    },
    "Polish": {
        "settings": "Ustawienia", "language": "Język", "premium": "Premium",
        "notifications": "Powiadomienia", "logout": "Wyloguj",
        "trade_history": "Historia transakcji", "trading": "Trading",
        "portfolio_title": "Portfel", "strategies_title": "Strategie",
        "strategy_settings": "Ustawienia strategii", "quick_tools": "Szybkie narzędzia",
        "futures": "Kontrakty", "spot": "Spot", "buy": "Kup",
        "leverage": "Dźwignia", "stop_loss": "Stop Loss", "take_profit": "Take Profit",
        "save_settings": "Zapisz", "history": "Historia",
        "market_overview": "Przegląd rynku", "full_screener": "Pełny screener",
        "tokens": "Tokeny", "connected": "Połączono", "active": "Aktywny",
        "configure_all_strategies": "Skonfiguruj wszystkie strategie",
        "screener": "Screener", "signals": "Sygnały", "stats": "Statystyki",
        "more": "Więcej", "activity": "Aktywność", "ai": "AI",
        "tap_to_configure": "Dotknij aby skonfigurować",
        "trading_close_position": "Zamknij pozycję", "trading_cancel_order": "Anuluj zlecenie",
        "trading_order_placed": "Zlecenie złożone", "trading_entry_price": "Cena wejścia",
        "trading_current_price": "Aktualna cena", "trading_leverage": "Dźwignia",
        "trading_tab_positions": "Pozycje", "trading_tab_orders": "Zlecenia",
        "trading_tab_history": "Historia", "trading_place_long": "Otwórz Long",
        "trading_place_short": "Otwórz Short", "trading_quantity": "Ilość",
        "futures_balance": "Saldo kontraktów", "no_orders_subtitle": "Brak aktywnych zleceń",
        "no_positions_subtitle": "Brak otwartych pozycji",
        "synced_at": "Zsynchronizowano", "exchange": "Giełda",
        "history_empty": "Historia pusta", "history_no_trades": "Brak transakcji",
        "history_title": "Historia", "disconnected": "Rozłączono",
        "manage_alerts": "Zarządzaj alertami",
        "trading_long": "Long", "trading_short": "Short",
        "trading_24h_change": "Zmiana 24h", "trading_24h_volume": "Wolumen 24h",
        "trading_liq_price": "Cena likwidacji", "trading_mark_price": "Cena mark",
        "trading_margin_required": "Wymagany depozyt", "trading_order_value": "Wartość zlecenia",
        "trading_open_interest": "Open Interest", "trading_order_failed": "Zlecenie nieudane",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "Zlecenie",
    },
    "Czech": {
        "settings": "Nastavení", "language": "Jazyk", "premium": "Premium",
        "notifications": "Oznámení", "logout": "Odhlásit",
        "trade_history": "Historie obchodů", "trading": "Obchodování",
        "portfolio_title": "Portfolio", "strategies_title": "Strategie",
        "strategy_settings": "Nastavení strategie", "quick_tools": "Rychlé nástroje",
        "futures": "Futures", "spot": "Spot", "buy": "Koupit",
        "leverage": "Páka", "stop_loss": "Stop Loss", "take_profit": "Take Profit",
        "save_settings": "Uložit", "history": "Historie",
        "market_overview": "Přehled trhu", "full_screener": "Kompletní screener",
        "tokens": "Tokeny", "connected": "Připojeno", "active": "Aktivní",
        "configure_all_strategies": "Konfigurovat všechny strategie",
        "screener": "Screener", "signals": "Signály", "stats": "Statistiky",
        "more": "Více", "activity": "Aktivita", "ai": "AI",
        "tap_to_configure": "Klepněte pro konfiguraci",
        "trading_close_position": "Zavřít pozici", "trading_cancel_order": "Zrušit příkaz",
        "trading_order_placed": "Příkaz zadán", "trading_entry_price": "Vstupní cena",
        "trading_current_price": "Aktuální cena", "trading_leverage": "Páka",
        "trading_tab_positions": "Pozice", "trading_tab_orders": "Příkazy",
        "trading_tab_history": "Historie", "trading_place_long": "Otevřít Long",
        "trading_place_short": "Otevřít Short", "trading_quantity": "Množství",
        "futures_balance": "Zůstatek futures", "no_orders_subtitle": "Žádné aktivní příkazy",
        "no_positions_subtitle": "Žádné otevřené pozice",
        "synced_at": "Synchronizováno", "exchange": "Burza",
        "history_empty": "Historie prázdná", "history_no_trades": "Žádné obchody",
        "history_title": "Historie", "disconnected": "Odpojeno",
        "manage_alerts": "Správa upozornění",
        "trading_long": "Long", "trading_short": "Short",
        "trading_24h_change": "Změna 24h", "trading_24h_volume": "Objem 24h",
        "trading_liq_price": "Likvidační cena", "trading_mark_price": "Mark cena",
        "trading_margin_required": "Požadovaná marže", "trading_order_value": "Hodnota příkazu",
        "trading_open_interest": "Open Interest", "trading_order_failed": "Příkaz selhal",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "Příkaz",
    },
    "Lithuanian": {
        "settings": "Nustatymai", "language": "Kalba", "premium": "Premium",
        "notifications": "Pranešimai", "logout": "Atsijungti",
        "trade_history": "Sandorių istorija", "trading": "Prekyba",
        "portfolio_title": "Portfelis", "strategies_title": "Strategijos",
        "strategy_settings": "Strategijos nustatymai", "quick_tools": "Greiti įrankiai",
        "futures": "Ateities sandoriai", "spot": "Spot", "buy": "Pirkti",
        "leverage": "Svertas", "stop_loss": "Stop Loss", "take_profit": "Take Profit",
        "save_settings": "Išsaugoti", "history": "Istorija",
        "market_overview": "Rinkos apžvalga", "full_screener": "Pilnas skeneris",
        "tokens": "Žetonai", "connected": "Prisijungta", "active": "Aktyvus",
        "configure_all_strategies": "Konfigūruoti visas strategijas",
        "screener": "Skeneris", "signals": "Signalai", "stats": "Statistika",
        "more": "Daugiau", "activity": "Veikla", "ai": "DI",
        "tap_to_configure": "Bakstelėkite konfigūruoti",
        "trading_close_position": "Uždaryti poziciją", "trading_cancel_order": "Atšaukti užsakymą",
        "trading_order_placed": "Užsakymas pateiktas", "trading_entry_price": "Įėjimo kaina",
        "trading_current_price": "Dabartinė kaina", "trading_leverage": "Svertas",
        "trading_tab_positions": "Pozicijos", "trading_tab_orders": "Užsakymai",
        "trading_tab_history": "Istorija", "trading_place_long": "Atidaryti Long",
        "trading_place_short": "Atidaryti Short", "trading_quantity": "Kiekis",
        "futures_balance": "Ateities sandorių balansas", "no_orders_subtitle": "Nėra aktyvių užsakymų",
        "no_positions_subtitle": "Nėra atvirų pozicijų",
        "synced_at": "Sinchronizuota", "exchange": "Birža",
        "history_empty": "Istorija tuščia", "history_no_trades": "Nėra sandorių",
        "history_title": "Istorija", "disconnected": "Atjungta",
        "manage_alerts": "Tvarkyti perspėjimus",
        "trading_long": "Long", "trading_short": "Short",
        "trading_24h_change": "24h pokytis", "trading_24h_volume": "24h apyvarta",
        "trading_liq_price": "Likvidacijos kaina", "trading_mark_price": "Mark kaina",
        "trading_margin_required": "Reikalaujama marža", "trading_order_value": "Užsakymo vertė",
        "trading_open_interest": "Open Interest", "trading_order_failed": "Užsakymas nepavyko",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "Užsakymas",
    },
    "Albanian": {
        "settings": "Cilësimet", "language": "Gjuha", "premium": "Premium",
        "notifications": "Njoftimet", "logout": "Dil",
        "trade_history": "Historiku i tregtimit", "trading": "Tregtimi",
        "portfolio_title": "Portofoli", "strategies_title": "Strategjitë",
        "strategy_settings": "Cilësimet e strategjisë", "quick_tools": "Mjete të shpejta",
        "futures": "Kontrata", "spot": "Spot", "buy": "Bli",
        "leverage": "Leva", "stop_loss": "Stop Loss", "take_profit": "Take Profit",
        "save_settings": "Ruaj", "history": "Historiku",
        "market_overview": "Pasqyrë e tregut", "full_screener": "Skaneri i plotë",
        "tokens": "Tokenë", "connected": "I lidhur", "active": "Aktiv",
        "configure_all_strategies": "Konfiguro të gjitha strategjitë",
        "screener": "Skaneri", "signals": "Sinjale", "stats": "Statistika",
        "more": "Më shumë", "activity": "Aktiviteti", "ai": "IA",
        "tap_to_configure": "Prek për konfigurim",
        "trading_close_position": "Mbyll pozicionin", "trading_cancel_order": "Anulo urdhrin",
        "trading_order_placed": "Urdhri u vendos", "trading_entry_price": "Çmimi i hyrjes",
        "trading_current_price": "Çmimi aktual", "trading_leverage": "Leva",
        "trading_tab_positions": "Pozicionet", "trading_tab_orders": "Urdhrat",
        "trading_tab_history": "Historiku", "trading_place_long": "Hap Long",
        "trading_place_short": "Hap Short", "trading_quantity": "Sasia",
        "futures_balance": "Balanca e kontratave", "no_orders_subtitle": "Nuk ka urdhra aktive",
        "no_positions_subtitle": "Nuk ka pozicione të hapura",
        "synced_at": "Sinkronizuar", "exchange": "Shkëmbimi",
        "history_empty": "Historiku bosh", "history_no_trades": "Nuk ka tregtime",
        "history_title": "Historiku", "disconnected": "I shkëputur",
        "manage_alerts": "Menaxho alarmet",
        "trading_long": "Long", "trading_short": "Short",
        "trading_24h_change": "Ndryshimi 24o", "trading_24h_volume": "Vëllimi 24o",
        "trading_liq_price": "Çmimi i likuidimit", "trading_mark_price": "Çmimi mark",
        "trading_margin_required": "Marzhi i nevojshëm", "trading_order_value": "Vlera e urdhrit",
        "trading_open_interest": "Open Interest", "trading_order_failed": "Urdhri dështoi",
        "trading_tp_sl_section": "TP / SL", "trading_tab_order": "Urdhri",
    },
}

LANGUAGE_MARKERS = {
    "German": "// MARK: - German",
    "Spanish": "// MARK: - Spanish",
    "French": "// MARK: - French",
    "Italian": "// MARK: - Italian",
    "Japanese": "// MARK: - Japanese",
    "Chinese": "// MARK: - Chinese",
    "Arabic": "// MARK: - Arabic",
    "Hebrew": "// MARK: - Hebrew",
    "Polish": "// MARK: - Polish",
    "Czech": "// MARK: - Czech",
    "Lithuanian": "// MARK: - Lithuanian",
    "Albanian": "// MARK: - Albanian",
}


def main():
    with open(SWIFT_FILE, "r") as f:
        content = f.read()

    en_dict = extract_en_dict(content)
    print(f"English reference: {len(en_dict)} keys")

    for lang_name, marker in LANGUAGE_MARKERS.items():
        existing = extract_keys(marker, content)
        missing_keys = set(en_dict.keys()) - existing
        
        if not missing_keys:
            print(f"  {lang_name}: already complete!")
            continue

        # Build the keys to add with native overrides when available
        native = NATIVE_OVERRIDES.get(lang_name, {})
        keys_to_add = {}
        for key in missing_keys:
            if key in native:
                keys_to_add[key] = native[key]
            else:
                # Use English as fallback
                keys_to_add[key] = en_dict.get(key, key)

        print(f"  {lang_name}: adding {len(keys_to_add)} keys ({len(native)} native, {len(keys_to_add) - len([k for k in keys_to_add if k in native])} English fallback)")
        content = add_keys_to_section(content, marker, keys_to_add)

    with open(SWIFT_FILE, "w") as f:
        f.write(content)

    print("\nDone! All languages synced.")


if __name__ == "__main__":
    main()
