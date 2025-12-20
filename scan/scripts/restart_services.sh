#!/usr/bin/env bash
# Restart Noet-Dat systemd services (project conventions)
# Usage: sudo ./scripts/restart_services.sh

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE="noetdat"
TIMER="noetdat-cleanup.timer"

echo "Restarting main service: $SERVICE"
sudo systemctl restart "$SERVICE"
echo "Status for $SERVICE:"
sudo systemctl status "$SERVICE" --no-pager -n 20 || true

echo "Restarting cleanup timer: $TIMER"
sudo systemctl restart "$TIMER" || true
echo "Status for $TIMER:"
sudo systemctl status "$TIMER" --no-pager -n 20 || true

echo "Done. Follow logs with: sudo journalctl -u $SERVICE -f"
