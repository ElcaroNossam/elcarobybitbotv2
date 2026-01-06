#!/bin/bash
set -e

PROJECT_DIR="/home/ubuntu/project/elcarobybitbotv2"
LOG_FILE="$PROJECT_DIR/logs/startup.log"
WEBAPP_LOG="$PROJECT_DIR/logs/uvicorn.log"
WEBAPP_PORT=8765

mkdir -p "$PROJECT_DIR/logs"
cd "$PROJECT_DIR"

echo "[$(date)] Starting ElCaro services..." >> "$LOG_FILE"

# Kill any existing uvicorn processes
pkill -f "uvicorn webapp.app" 2>/dev/null || true
sleep 1

# Start webapp (uvicorn) in background
echo "[$(date)] Starting webapp on port $WEBAPP_PORT..." >> "$LOG_FILE"
./venv/bin/python -m uvicorn webapp.app:app --host 0.0.0.0 --port $WEBAPP_PORT >> "$WEBAPP_LOG" 2>&1 &
WEBAPP_PID=$!
echo "[$(date)] Webapp started with PID $WEBAPP_PID" >> "$LOG_FILE"

# Wait for webapp to be ready
for i in {1..10}; do
    if curl -s "http://localhost:$WEBAPP_PORT/health" > /dev/null 2>&1; then
        echo "[$(date)] Webapp is ready" >> "$LOG_FILE"
        break
    fi
    sleep 1
done

# Start Cloudflare tunnel in background
echo "[$(date)] Starting Cloudflare tunnel..." >> "$LOG_FILE"
cloudflared tunnel --url "http://localhost:$WEBAPP_PORT" >> "$PROJECT_DIR/logs/cloudflared.log" 2>&1 &
TUNNEL_PID=$!
echo "[$(date)] Cloudflare tunnel started with PID $TUNNEL_PID" >> "$LOG_FILE"

# Wait a bit for tunnel URL to be generated
sleep 5

echo "[$(date)] Starting bot..." >> "$LOG_FILE"
# Start bot directly (main process)
exec ./venv/bin/python bot.py
