#!/bin/bash
# Tunnel Health Monitor - runs every 5 minutes via cron
# Checks tunnel health and restarts if needed

PROJECT_DIR="/home/ubuntu/project/elcarobybitbotv2"
TUNNEL_MANAGER="$PROJECT_DIR/tunnel_manager.sh"
LOG_FILE="$PROJECT_DIR/logs/tunnel_monitor.log"
WEBAPP_PORT=8765

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if webapp is running
if ! pgrep -f "uvicorn webapp.app:app" > /dev/null; then
    log "WebApp not running, starting..."
    cd "$PROJECT_DIR"
    source venv/bin/activate
    nohup python -m uvicorn webapp.app:app --host 0.0.0.0 --port $WEBAPP_PORT >> "$PROJECT_DIR/logs/webapp.log" 2>&1 &
    sleep 5
fi

# Check tunnel health
if ! $TUNNEL_MANAGER check > /dev/null 2>&1; then
    log "Tunnel unhealthy, restarting..."
    $TUNNEL_MANAGER restart
    
    # Verify restart was successful
    sleep 10
    if $TUNNEL_MANAGER check > /dev/null 2>&1; then
        log "Tunnel restarted successfully"
        NEW_URL=$($TUNNEL_MANAGER url)
        log "New URL: $NEW_URL"
    else
        log "ERROR: Tunnel restart failed!"
    fi
else
    log "Tunnel healthy"
fi

# Cleanup old logs (keep last 1000 lines)
if [ -f "$LOG_FILE" ]; then
    tail -1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi
