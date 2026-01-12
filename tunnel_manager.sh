#!/bin/bash
# Cloudflare Tunnel Manager for ElCaro Bot WebApp
# Manages tunnel lifecycle, monitors health, auto-restarts

PROJECT_DIR="/home/ubuntu/project/elcarobybitbotv2"
WEBAPP_PORT=8765
TUNNEL_PID_FILE="$PROJECT_DIR/run/tunnel.pid"
TUNNEL_URL_FILE="$PROJECT_DIR/run/tunnel_url.txt"
TUNNEL_LOG="$PROJECT_DIR/logs/tunnel.log"
ENV_FILE="$PROJECT_DIR/.env"

# Create directories
mkdir -p "$PROJECT_DIR/run" "$PROJECT_DIR/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$TUNNEL_LOG"
}

get_tunnel_url() {
    # Wait for tunnel to establish and get URL
    for i in {1..30}; do
        sleep 1
        URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG" 2>/dev/null | tail -1)
        if [ -n "$URL" ]; then
            echo "$URL"
            return 0
        fi
    done
    return 1
}

start_tunnel() {
    log "Starting cloudflared tunnel..."
    
    # Kill existing tunnel if any
    if [ -f "$TUNNEL_PID_FILE" ]; then
        OLD_PID=$(cat "$TUNNEL_PID_FILE")
        kill $OLD_PID 2>/dev/null
        sleep 2
    fi
    pkill -f "cloudflared tunnel --url http://localhost:$WEBAPP_PORT" 2>/dev/null
    
    # Start new tunnel
    nohup cloudflared tunnel --url http://localhost:$WEBAPP_PORT >> "$TUNNEL_LOG" 2>&1 &
    TUNNEL_PID=$!
    echo $TUNNEL_PID > "$TUNNEL_PID_FILE"
    
    log "Tunnel started with PID: $TUNNEL_PID"
    
    # Get URL
    URL=$(get_tunnel_url)
    if [ -n "$URL" ]; then
        echo "$URL" > "$TUNNEL_URL_FILE"
        log "Tunnel URL: $URL"
        
        # Update .env file
        if grep -q "^WEBAPP_URL=" "$ENV_FILE" 2>/dev/null; then
            sed -i "s|^WEBAPP_URL=.*|WEBAPP_URL=$URL|" "$ENV_FILE"
        else
            echo "WEBAPP_URL=$URL" >> "$ENV_FILE"
        fi
        
        log "Updated .env with WEBAPP_URL"
        
        # Restart bot to pick up new URL
        log "Restarting elcaro-bot service..."
        sudo systemctl restart elcaro-bot
        sleep 3
        if systemctl is-active --quiet elcaro-bot; then
            log "Bot restarted successfully with new URL"
        else
            log "ERROR: Bot restart failed!"
        fi
        
        return 0
    else
        log "ERROR: Failed to get tunnel URL"
        return 1
    fi
}

stop_tunnel() {
    log "Stopping tunnel..."
    if [ -f "$TUNNEL_PID_FILE" ]; then
        PID=$(cat "$TUNNEL_PID_FILE")
        kill $PID 2>/dev/null
        rm -f "$TUNNEL_PID_FILE"
    fi
    pkill -f "cloudflared tunnel --url http://localhost:$WEBAPP_PORT" 2>/dev/null
    log "Tunnel stopped"
}

check_tunnel() {
    # Check if tunnel process is running
    if [ ! -f "$TUNNEL_PID_FILE" ]; then
        return 1
    fi
    
    PID=$(cat "$TUNNEL_PID_FILE")
    if ! kill -0 $PID 2>/dev/null; then
        return 1
    fi
    
    # Check if URL is accessible
    if [ -f "$TUNNEL_URL_FILE" ]; then
        URL=$(cat "$TUNNEL_URL_FILE")
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$URL/health" 2>/dev/null)
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
            return 0
        fi
    fi
    
    return 1
}

restart_all() {
    log "Restarting all services..."
    
    # 1. Stop tunnel
    stop_tunnel
    
    # 2. Restart webapp
    pkill -f "uvicorn webapp.app:app" 2>/dev/null
    sleep 2
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    nohup python -m uvicorn webapp.app:app --host 0.0.0.0 --port $WEBAPP_PORT >> "$PROJECT_DIR/logs/webapp.log" 2>&1 &
    WEBAPP_PID=$!
    echo $WEBAPP_PID > "$PROJECT_DIR/run/webapp.pid"
    log "WebApp started with PID: $WEBAPP_PID"
    
    sleep 3
    
    # 3. Start tunnel
    start_tunnel
}

status() {
    echo "=== Tunnel Status ==="
    if [ -f "$TUNNEL_PID_FILE" ]; then
        PID=$(cat "$TUNNEL_PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo "Tunnel: RUNNING (PID: $PID)"
        else
            echo "Tunnel: DEAD (stale PID file)"
        fi
    else
        echo "Tunnel: NOT RUNNING"
    fi
    
    if [ -f "$TUNNEL_URL_FILE" ]; then
        echo "URL: $(cat $TUNNEL_URL_FILE)"
    fi
    
    echo ""
    echo "=== WebApp Status ==="
    if pgrep -f "uvicorn webapp.app:app" > /dev/null; then
        echo "WebApp: RUNNING"
    else
        echo "WebApp: NOT RUNNING"
    fi
    
    echo ""
    echo "=== Bot Status ==="
    systemctl is-active elcaro-bot 2>/dev/null || echo "Bot service status unknown"
}

case "$1" in
    start)
        start_tunnel
        ;;
    stop)
        stop_tunnel
        ;;
    restart)
        stop_tunnel
        sleep 2
        start_tunnel
        ;;
    restart-all)
        restart_all
        ;;
    check)
        if check_tunnel; then
            echo "Tunnel is healthy"
            exit 0
        else
            echo "Tunnel needs restart"
            exit 1
        fi
        ;;
    status)
        status
        ;;
    url)
        if [ -f "$TUNNEL_URL_FILE" ]; then
            cat "$TUNNEL_URL_FILE"
        else
            echo "No URL available"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|restart-all|check|status|url}"
        exit 1
        ;;
esac
