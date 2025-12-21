#!/bin/bash
#
# ═══════════════════════════════════════════════════════════════════════════════
# ElCaro Trading Platform - Full Stack Startup Script
# Bot + WebApp + Screener + ngrok
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./start.sh              - Start all services in foreground
#   ./start.sh --daemon     - Start all services in background
#   ./start.sh --stop       - Stop all services
#   ./start.sh --restart    - Restart all services
#   ./start.sh --status     - Show status
#   ./start.sh --bot        - Start only bot
#   ./start.sh --webapp     - Start only webapp
#   ./start.sh --install    - Install dependencies
#   ./start.sh --clean      - Clean all caches and temp files
#

set -e

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Service names and ports
BOT_NAME="elcaro_bot"
WEBAPP_NAME="elcaro_webapp"
SCREENER_NAME="elcaro_screener"

BOT_PID_FILE="run/bot.pid"
WEBAPP_PID_FILE="run/webapp.pid"
NGROK_PID_FILE="run/ngrok.pid"
CF_TUNNEL_PID_FILE="run/cloudflared.pid"

BOT_LOG="logs/bot.log"
WEBAPP_LOG="logs/webapp.log"
NGROK_LOG="logs/ngrok.log"
CF_TUNNEL_LOG="logs/cloudflared.log"

WEBAPP_PORT=8765
NGROK_PORT=4040

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════

print_banner() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BOLD}${GREEN}⚡ ElCaro Trading Platform${NC}                                  ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}Bot + WebApp + Screener + Analytics${NC}                          ${CYAN}║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠ $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ✗ $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✓ $1${NC}"
}

ensure_dirs() {
    mkdir -p run logs data
    chmod 755 run logs data
}

get_pid() {
    local pidfile=$1
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "$pid"
            return 0
        fi
    fi
    return 1
}

is_port_busy() {
    local port=$1
    lsof -i :$port >/dev/null 2>&1
}

kill_port() {
    local port=$1
    if is_port_busy $port; then
        warn "Killing processes on port $port"
        fuser -k $port/tcp 2>/dev/null || true
        sleep 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# Service Management
# ═══════════════════════════════════════════════════════════════════════════════

stop_bot() {
    log "Stopping Bot..."
    local pid=$(get_pid "$BOT_PID_FILE")
    if [ -n "$pid" ]; then
        kill -TERM "$pid" 2>/dev/null || true
        sleep 2
        kill -9 "$pid" 2>/dev/null || true
    fi
    pkill -9 -f "python.*bot.py" 2>/dev/null || true
    rm -f "$BOT_PID_FILE"
    success "Bot stopped"
}

stop_webapp() {
    log "Stopping WebApp..."
    local pid=$(get_pid "$WEBAPP_PID_FILE")
    if [ -n "$pid" ]; then
        kill -TERM "$pid" 2>/dev/null || true
        sleep 1
        kill -9 "$pid" 2>/dev/null || true
    fi
    pkill -9 -f "uvicorn webapp.app" 2>/dev/null || true
    kill_port $WEBAPP_PORT
    rm -f "$WEBAPP_PID_FILE"
    success "WebApp stopped"
}

stop_ngrok() {
    log "Stopping ngrok..."
    local pid=$(get_pid "$NGROK_PID_FILE")
    if [ -n "$pid" ]; then
        kill -9 "$pid" 2>/dev/null || true
    fi
    pkill -9 -f "ngrok" 2>/dev/null || true
    rm -f "$NGROK_PID_FILE"
    success "ngrok stopped"
}

stop_all() {
    echo ""
    log "Stopping all services..."
    stop_cloudflare
    stop_ngrok
    stop_webapp
    stop_bot
    echo ""
    success "All services stopped"
}

start_bot() {
    local daemon=$1
    log "Starting Bot..."
    
    if [ "$daemon" = "true" ]; then
        nohup $PYTHON_CMD bot.py >> "$BOT_LOG" 2>&1 &
        echo $! > "$BOT_PID_FILE"
        sleep 2
        if get_pid "$BOT_PID_FILE" >/dev/null; then
            success "Bot started (PID: $(cat $BOT_PID_FILE))"
        else
            error "Bot failed to start! Check $BOT_LOG"
            return 1
        fi
    else
        $PYTHON_CMD bot.py 2>&1 | tee -a "$BOT_LOG"
    fi
}

start_webapp() {
    local daemon=$1
    log "Starting WebApp on port $WEBAPP_PORT..."
    
    # Ensure port is free
    kill_port $WEBAPP_PORT
    
    if [ "$daemon" = "true" ]; then
        nohup $PYTHON_CMD -m uvicorn webapp.app:app --host 0.0.0.0 --port $WEBAPP_PORT >> "$WEBAPP_LOG" 2>&1 &
        echo $! > "$WEBAPP_PID_FILE"
        sleep 3
        if is_port_busy $WEBAPP_PORT; then
            success "WebApp started (PID: $(cat $WEBAPP_PID_FILE)) → http://localhost:$WEBAPP_PORT"
        else
            error "WebApp failed to start! Check $WEBAPP_LOG"
            return 1
        fi
    else
        $PYTHON_CMD -m uvicorn webapp.app:app --host 0.0.0.0 --port $WEBAPP_PORT --reload 2>&1 | tee -a "$WEBAPP_LOG"
    fi
}

# Cloudflare Tunnel Configuration
CF_TUNNEL_PID_FILE="run/cloudflare.pid"
CF_TUNNEL_LOG="logs/cloudflare.log"

stop_cloudflare() {
    log "Stopping Cloudflare tunnel..."
    local pid=$(get_pid "$CF_TUNNEL_PID_FILE")
    if [ -n "$pid" ]; then
        kill -9 "$pid" 2>/dev/null || true
    fi
    pkill -9 -f "cloudflared" 2>/dev/null || true
    rm -f "$CF_TUNNEL_PID_FILE"
    success "Cloudflare tunnel stopped"
}

start_cloudflare() {
    log "Starting Cloudflare tunnel..."
    
    if ! command -v cloudflared &>/dev/null; then
        warn "cloudflared not installed, trying ngrok..."
        start_ngrok
        return $?
    fi
    
    # Start cloudflared quick tunnel
    nohup cloudflared tunnel --url http://localhost:$WEBAPP_PORT > "$CF_TUNNEL_LOG" 2>&1 &
    echo $! > "$CF_TUNNEL_PID_FILE"
    sleep 5
    
    # Get tunnel URL from log
    local cf_url=""
    for i in {1..10}; do
        cf_url=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' "$CF_TUNNEL_LOG" 2>/dev/null | head -1 || echo "")
        if [ -n "$cf_url" ]; then
            break
        fi
        sleep 1
    done
    
    if [ -n "$cf_url" ]; then
        success "Cloudflare tunnel → $cf_url"
        echo "$cf_url" > run/ngrok_url.txt
        
        # Update .env with new URL
        update_env_webapp_url "$cf_url"
        return 0
    else
        warn "Cloudflare failed, trying ngrok..."
        stop_cloudflare
        start_ngrok
        return $?
    fi
}

update_env_webapp_url() {
    local url=$1
    
    # Update or add WEBAPP_URL in .env
    if grep -q "^WEBAPP_URL=" .env 2>/dev/null; then
        sed -i "s|^WEBAPP_URL=.*|WEBAPP_URL=$url|" .env
    else
        echo "WEBAPP_URL=$url" >> .env
    fi
    
    log "Updated .env with WEBAPP_URL=$url"
}

start_ngrok() {
    log "Starting ngrok tunnel..."
    
    if ! command -v ngrok &>/dev/null; then
        warn "ngrok not installed, skipping tunnel..."
        echo "http://localhost:$WEBAPP_PORT" > run/ngrok_url.txt
        return 0
    fi
    
    nohup ngrok http $WEBAPP_PORT --log=stdout > "$NGROK_LOG" 2>&1 &
    echo $! > "$NGROK_PID_FILE"
    sleep 3
    
    # Get public URL
    local ngrok_url=$(curl -s localhost:$NGROK_PORT/api/tunnels 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['tunnels'][0]['public_url'] if d.get('tunnels') else '')" 2>/dev/null || echo "")
    
    if [ -n "$ngrok_url" ]; then
        success "ngrok tunnel → $ngrok_url"
        echo "$ngrok_url" > run/ngrok_url.txt
        
        # Update .env with new URL
        update_env_webapp_url "$ngrok_url"
    else
        warn "ngrok started but could not get URL"
        echo "http://localhost:$WEBAPP_PORT" > run/ngrok_url.txt
    fi
}

show_status() {
    echo ""
    echo -e "${BOLD}Service Status:${NC}"
    echo -e "─────────────────────────────────────────"
    
    # Bot
    if get_pid "$BOT_PID_FILE" >/dev/null; then
        local pid=$(cat "$BOT_PID_FILE")
        local mem=$(ps -o rss= -p $pid 2>/dev/null | awk '{print int($1/1024)"MB"}' || echo "?")
        local uptime=$(ps -o etime= -p $pid 2>/dev/null | xargs || echo "?")
        echo -e "${GREEN}● Bot${NC}        Running (PID: $pid, Mem: $mem, Up: $uptime)"
    else
        echo -e "${RED}○ Bot${NC}        Stopped"
    fi
    
    # WebApp
    if is_port_busy $WEBAPP_PORT; then
        local pid=$(get_pid "$WEBAPP_PID_FILE")
        echo -e "${GREEN}● WebApp${NC}     Running on :$WEBAPP_PORT (PID: ${pid:-?})"
    else
        echo -e "${RED}○ WebApp${NC}     Stopped"
    fi
    
    # Tunnel (Cloudflare or ngrok)
    if [ -f "run/ngrok_url.txt" ]; then
        local tunnel_url=$(cat run/ngrok_url.txt)
        if get_pid "$CF_TUNNEL_PID_FILE" >/dev/null; then
            echo -e "${GREEN}● Cloudflare${NC} $tunnel_url"
        elif get_pid "$NGROK_PID_FILE" >/dev/null; then
            echo -e "${GREEN}● ngrok${NC}      $tunnel_url"
        else
            echo -e "${YELLOW}○ Tunnel${NC}     Not running"
        fi
    else
        echo -e "${YELLOW}○ Tunnel${NC}     Not running"
    fi
    
    echo -e "─────────────────────────────────────────"
    
    # Database info
    echo ""
    echo -e "${BOLD}Databases:${NC}"
    [ -f "bot.db" ] && echo -e "  ${CYAN}●${NC} Main DB:      bot.db ($(du -h bot.db 2>/dev/null | cut -f1 || echo '?'))"
    [ -f "data/analytics.db" ] && echo -e "  ${CYAN}●${NC} Analytics:    data/analytics.db ($(du -h data/analytics.db 2>/dev/null | cut -f1 || echo '?'))"
    [ -f "data/screener.db" ] && echo -e "  ${CYAN}●${NC} Screener:     data/screener.db ($(du -h data/screener.db 2>/dev/null | cut -f1 || echo '?'))"
    
    echo ""
    echo -e "${BOLD}Commands:${NC}"
    echo "  ./start.sh --restart   Restart all"
    echo "  ./start.sh --stop      Stop all"
    echo "  tail -f logs/bot.log   Bot logs"
    echo "  tail -f logs/webapp.log WebApp logs"
    echo ""
}

clean_all() {
    log "Cleaning caches and temp files..."
    
    # Stop services first
    stop_all
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    
    # Remove logs (keep last)
    if [ -f "$BOT_LOG" ]; then
        tail -1000 "$BOT_LOG" > "${BOT_LOG}.bak" 2>/dev/null
        mv "${BOT_LOG}.bak" "$BOT_LOG"
    fi
    if [ -f "$WEBAPP_LOG" ]; then
        tail -1000 "$WEBAPP_LOG" > "${WEBAPP_LOG}.bak" 2>/dev/null
        mv "${WEBAPP_LOG}.bak" "$WEBAPP_LOG"
    fi
    
    # Remove PID files
    rm -f run/*.pid run/*.txt
    
    # Clean indicator cache in analytics db
    if [ -f "data/analytics.db" ]; then
        sqlite3 data/analytics.db "DELETE FROM indicator_cache WHERE expires_at < strftime('%s', 'now');" 2>/dev/null || true
    fi
    
    success "Cleanup complete"
}

install_deps() {
    log "Installing dependencies..."
    
    # Create venv if not exists
    if [ ! -d "venv" ]; then
        log "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    source venv/bin/activate
    
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    
    # Initialize databases
    log "Initializing databases..."
    $PYTHON_CMD -c "
from config.analytics_db import init_analytics_db
init_analytics_db()
print('Analytics DB ready')
"
    
    success "Dependencies installed"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main Logic
# ═══════════════════════════════════════════════════════════════════════════════

# Parse arguments
DAEMON=false
STOP=false
RESTART=false
STATUS=false
CLEAN=false
INSTALL=false
BOT_ONLY=false
WEBAPP_ONLY=false

for arg in "$@"; do
    case $arg in
        --daemon|-d|--background|-b)
            DAEMON=true ;;
        --stop)
            STOP=true ;;
        --restart|-r)
            RESTART=true ;;
        --status|-s)
            STATUS=true ;;
        --clean|-c)
            CLEAN=true ;;
        --install|-i)
            INSTALL=true ;;
        --bot)
            BOT_ONLY=true ;;
        --webapp|--web)
            WEBAPP_ONLY=true ;;
        --help|-h)
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --daemon, -d     Run in background"
            echo "  --stop           Stop all services"
            echo "  --restart, -r    Restart all services"
            echo "  --status, -s     Show status"
            echo "  --clean, -c      Clean caches"
            echo "  --install, -i    Install dependencies"
            echo "  --bot            Start only bot"
            echo "  --webapp         Start only webapp"
            echo "  --help, -h       Show help"
            exit 0
            ;;
    esac
done

print_banner
ensure_dirs

# Handle status
if [ "$STATUS" = true ]; then
    show_status
    exit 0
fi

# Handle stop
if [ "$STOP" = true ]; then
    stop_all
    exit 0
fi

# Handle clean
if [ "$CLEAN" = true ]; then
    clean_all
    exit 0
fi

# Handle restart
if [ "$RESTART" = true ]; then
    stop_all
    sleep 2
    DAEMON=true
fi

# Check Python
log "Checking Python..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    error "Python not found!"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
success "Python $PYTHON_VERSION"

# Check .env
if [ ! -f ".env" ]; then
    error ".env file not found!"
    echo "Create .env with:"
    echo "  TELEGRAM_TOKEN=your_token"
    echo "  SIGNAL_CHANNEL_IDS=-123456789"
    exit 1
fi
success ".env found"

# Virtual environment
if [ ! -d "venv" ]; then
    log "Creating venv..."
    $PYTHON_CMD -m venv venv
    INSTALL=true
fi

source venv/bin/activate
success "venv activated"

# Install dependencies
if [ "$INSTALL" = true ]; then
    install_deps
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Start Services
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${BOLD}Starting services...${NC}"
echo -e "─────────────────────────────────────────"

if [ "$BOT_ONLY" = true ]; then
    start_bot "$DAEMON"
elif [ "$WEBAPP_ONLY" = true ]; then
    start_webapp "$DAEMON"
else
    # Start all services
    if [ "$DAEMON" = true ]; then
        start_bot "true"
        start_webapp "true"
        
        # Start tunnel (tries Cloudflare first, falls back to ngrok)
        start_cloudflare
        
        echo ""
        echo -e "─────────────────────────────────────────"
        success "All services started!"
        echo ""
        show_status
    else
        # Foreground mode - start webapp only (bot needs separate terminal)
        warn "Foreground mode: Starting WebApp only"
        warn "Run bot in separate terminal: ./start.sh --bot"
        echo ""
        start_webapp "false"
    fi
fi
