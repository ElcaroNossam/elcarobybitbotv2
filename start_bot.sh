#!/bin/bash
set -e

PROJECT_DIR="/home/ubuntu/project/elcarobybitbotv2"
LOG_FILE="$PROJECT_DIR/logs/startup.log"
WEBAPP_LOG="$PROJECT_DIR/logs/uvicorn.log"
WEBAPP_PORT=8765

# ===== PRODUCTION DOMAIN =====
WEBAPP_URL="https://enliko.com"
# =============================

mkdir -p "$PROJECT_DIR/logs"
cd "$PROJECT_DIR"

# Load environment variables
source .env 2>/dev/null || true

# PostgreSQL mode
export USE_POSTGRES=1
export DATABASE_URL="postgresql://elcaro:elcaro_prod_2026@127.0.0.1:5432/elcaro"
export REDIS_URL="redis://127.0.0.1:6379/0"
export WEBAPP_URL="$WEBAPP_URL"

echo "[$(date)] Starting Enliko services (PostgreSQL mode)..." >> "$LOG_FILE"
echo "[$(date)] WEBAPP_URL=$WEBAPP_URL" >> "$LOG_FILE"

# Kill any existing uvicorn processes gracefully
echo "[$(date)] Cleaning up old processes..." >> "$LOG_FILE"
pkill -SIGTERM -f "uvicorn webapp.app" 2>/dev/null || true
sleep 2
# Force kill any remaining
pkill -SIGKILL -f "uvicorn webapp.app" 2>/dev/null || true
sleep 1

# Detect CPU cores and RAM for optimal workers
CPU_CORES=$(nproc 2>/dev/null || echo 2)
RAM_MB=$(free -m | awk '/^Mem:/{print $2}' 2>/dev/null || echo 2048)

# For low-memory servers (<=2GB), limit workers to 1
# Each worker uses ~150MB RAM + duplicates real-time WebSocket workers
if [ "$RAM_MB" -le 2048 ]; then
    WORKERS=1
else
    WORKERS=$((CPU_CORES + 1))
    [ $WORKERS -gt 4 ] && WORKERS=4
fi
echo "[$(date)] Detected $CPU_CORES cores, ${RAM_MB}MB RAM, using $WORKERS workers" >> "$LOG_FILE"

# Ensure nginx is running (SSL termination)
if systemctl is-active --quiet nginx; then
    echo "[$(date)] nginx is running" >> "$LOG_FILE"
else
    echo "[$(date)] Starting nginx..." >> "$LOG_FILE"
    sudo systemctl start nginx
fi

# Start webapp (uvicorn) in background with multiple workers
echo "[$(date)] Starting webapp on port $WEBAPP_PORT with $WORKERS workers..." >> "$LOG_FILE"
./venv/bin/python -m uvicorn webapp.app:app --host 127.0.0.1 --port $WEBAPP_PORT --workers $WORKERS --limit-concurrency 500 >> "$WEBAPP_LOG" 2>&1 &
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

# Update .env with production URL
if grep -q "^WEBAPP_URL=" .env 2>/dev/null; then
    sed -i "s|^WEBAPP_URL=.*|WEBAPP_URL=$WEBAPP_URL|" .env
else
    echo "WEBAPP_URL=$WEBAPP_URL" >> .env
fi

echo "[$(date)] Starting bot with WEBAPP_URL=$WEBAPP_URL..." >> "$LOG_FILE"
# Start bot directly (main process)
exec ./venv/bin/python bot.py
