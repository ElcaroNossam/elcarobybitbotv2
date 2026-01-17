"""
Periodic checker that evaluates AlertRule conditions against latest snapshots
and sends Telegram notifications when conditions are met.

Run from the project root (e.g. via cron every minute):

    TELEGRAM_BOT_TOKEN=... python scripts/check_alerts.py
"""

import datetime as dt
import os
import sys
import time
from pathlib import Path
from typing import Callable

import django
import requests


def setup_django() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()


def send_telegram_message(token: str, chat_id: int, text: str, parse_mode: str = "HTML") -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
            timeout=10
        )
        resp.raise_for_status()
    except Exception as exc:
        print(f"Failed to send telegram message to {chat_id}: {exc}")


def check_alert_conditions(snapshot, alert, operator_funcs):
    """Check if snapshot matches alert conditions (main + additional filters)."""
    # Check main condition
    value = getattr(snapshot, alert.metric, None)
    if value is None:
        return False
    
    op_func = operator_funcs.get(alert.operator)
    if not op_func:
        return False
    
    if not op_func(float(value), float(alert.threshold)):
        return False
    
    # Check additional filters if any
    if alert.additional_filters and isinstance(alert.additional_filters, list):
        for filter_cond in alert.additional_filters:
            filter_metric = filter_cond.get('metric')
            filter_operator = filter_cond.get('operator')
            filter_threshold = filter_cond.get('threshold')
            
            if not all([filter_metric, filter_operator, filter_threshold]):
                continue
            
            filter_value = getattr(snapshot, filter_metric, None)
            if filter_value is None:
                return False
            
            filter_op_func = operator_funcs.get(filter_operator)
            if not filter_op_func:
                continue
            
            if not filter_op_func(float(filter_value), float(filter_threshold)):
                return False
    
    return True


def format_metric_value(metric_name: str, val: float) -> str:
    """Format metric value for display."""
    if "change" in metric_name or "oi_change" in metric_name:
        return f"{val:.2f}%"
    elif "volume" in metric_name or "vdelta" in metric_name:
        abs_v = abs(val)
        if abs_v >= 1_000_000_000:
            return f"{val / 1_000_000_000:.2f}B"
        elif abs_v >= 1_000_000:
            return f"{val / 1_000_000:.2f}M"
        elif abs_v >= 1_000:
            return f"{val / 1_000:.2f}K"
        else:
            return f"{val:.2f}"
    elif "funding" in metric_name:
        return f"{val:.4f}"
    else:
        return f"{val:.2f}"


def send_alert_notification(alert, snapshot, bot_token, now):
    """Send Telegram notification for triggered alert."""
    # Get metric display name
    metric_display = dict(alert.METRIC_CHOICES).get(alert.metric, alert.metric)
    
    # Format values
    value = getattr(snapshot, alert.metric, 0)
    threshold_formatted = format_metric_value(alert.metric, float(alert.threshold))
    value_formatted = format_metric_value(alert.metric, float(value))
    
    # Determine emoji based on operator and value
    if alert.operator in [">", ">="]:
        emoji = "📈" if float(value) > float(alert.threshold) else "📉"
    else:
        emoji = "📉" if float(value) < float(alert.threshold) else "📈"
    
    # Build conditions text
    conditions_text = f"{alert.metric} {alert.operator} {threshold_formatted}"
    if alert.additional_filters and isinstance(alert.additional_filters, list):
        for f in alert.additional_filters:
            conditions_text += f"\n  AND {f['metric']} {f['operator']} {format_metric_value(f['metric'], f['threshold'])}"
    
    # Create beautiful HTML message with pink theme
    symbol_name = snapshot.symbol.symbol if snapshot.symbol else "ALL SYMBOLS"
    text = (
        f"{emoji} <b>🔔 Алерт сработал!</b>\n\n"
        f"<b>💎 Символ:</b> {symbol_name}\n"
        f"<b>📊 Тип рынка:</b> {snapshot.symbol.market_type.upper() if snapshot.symbol else 'ALL'}\n"
        f"<b>📈 Показатель:</b> {metric_display}\n"
        f"<b>⚡ Условия:</b>\n{conditions_text}\n"
        f"<b>💹 Текущее значение:</b> <code>{value_formatted}</code>\n"
        f"<b>🎯 Порог:</b> <code>{threshold_formatted}</code>\n\n"
        f"⏰ {now.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )
    
    send_telegram_message(bot_token, alert.telegram_chat_id, text)


def main() -> None:
    setup_django()

    from alerts.models import AlertRule
    from screener.models import ScreenerSnapshot

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN env var is required")

    now = dt.datetime.now(dt.timezone.utc)
    cooldown = dt.timedelta(minutes=5)

    operator_funcs: dict[str, Callable[[float, float], bool]] = {
        ">": lambda v, t: v > t,
        "<": lambda v, t: v < t,
        ">=": lambda v, t: v >= t,
        "<=": lambda v, t: v <= t,
    }

    for alert in AlertRule.objects.filter(active=True).select_related("symbol"):
        if not alert.telegram_chat_id:
            continue

        # Cooldown check
        if alert.last_triggered_at and now - alert.last_triggered_at < cooldown:
            continue

        # Use custom bot token if provided, otherwise use default
        bot_token = alert.telegram_bot_token.strip() if alert.telegram_bot_token else token

        # Handle global alerts (symbol=None) vs symbol-specific alerts
        if alert.symbol is None:
            # Global alert: check all symbols
            from django.utils import timezone
            from datetime import timedelta
            recent_cutoff = timezone.now() - timedelta(minutes=5)
            
            # Get latest snapshot for each symbol (more efficient)
            # Group by symbol and get latest ts
            from django.db.models import Max
            latest_snapshots = ScreenerSnapshot.objects.filter(
                ts__gte=recent_cutoff
            ).values('symbol').annotate(
                latest_ts=Max('ts')
            )[:50]  # Limit to 50 symbols to prevent CPU spike
            
            # Get the actual snapshots
            snapshot_ids = []
            for item in latest_snapshots:
                snap = ScreenerSnapshot.objects.filter(
                    symbol_id=item['symbol'],
                    ts=item['latest_ts']
                ).first()
                if snap:
                    snapshot_ids.append(snap)
            
            # Check conditions and send first match only
            for snapshot in snapshot_ids:
                if check_alert_conditions(snapshot, alert, operator_funcs):
                    send_alert_notification(alert, snapshot, bot_token, now)
                    alert.last_triggered_at = now
                    alert.save(update_fields=["last_triggered_at"])
                    break  # Send only one alert per check
            
            continue
        
        # Symbol-specific alert
        snapshot = (
            ScreenerSnapshot.objects.filter(symbol=alert.symbol)
            .order_by("-ts")
            .first()
        )
        if not snapshot:
            continue

        if not check_alert_conditions(snapshot, alert, operator_funcs):
            continue

        send_alert_notification(alert, snapshot, bot_token, now)
        alert.last_triggered_at = now
        alert.save(update_fields=["last_triggered_at"])

    print("Alert check completed.")


if __name__ == "__main__":
    main()
