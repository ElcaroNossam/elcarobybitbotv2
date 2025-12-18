#!/bin/bash
#
# Bybit Demo Trading Bot - Server Startup Script
# Usage: ./start.sh [--install] [--background] [--stop] [--restart] [--status]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BOT_NAME="bybit_demo_bot"
PID_FILE="bot.pid"
LOG_FILE="bot.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}   Bybit Demo Trading Bot${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    else
        pgrep -f "python.*bot.py" 2>/dev/null | head -1
    fi
}

is_running() {
    local pid=$(get_pid)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        return 0
    fi
    return 1
}

stop_bot() {
    echo -e "${YELLOW}Stopping bot...${NC}"
    local pid=$(get_pid)
    if [ -n "$pid" ]; then
        kill -TERM "$pid" 2>/dev/null || true
        sleep 2
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}Force killing...${NC}"
            kill -9 "$pid" 2>/dev/null || true
        fi
    fi
    # Also kill any orphan processes
    pkill -9 -f "python.*bot.py" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo -e "${GREEN}✓ Bot stopped${NC}"
}

show_status() {
    if is_running; then
        local pid=$(get_pid)
        echo -e "${GREEN}● Bot is RUNNING (PID: $pid)${NC}"
        echo -e "  Uptime: $(ps -o etime= -p $pid 2>/dev/null || echo 'unknown')"
        echo -e "  Memory: $(ps -o rss= -p $pid 2>/dev/null | awk '{print int($1/1024)"MB"}' || echo 'unknown')"
        echo -e "  Log: tail -f $LOG_FILE"
    else
        echo -e "${RED}○ Bot is STOPPED${NC}"
    fi
}

# Parse arguments
INSTALL=false
BACKGROUND=false
STOP=false
RESTART=false
STATUS=false

for arg in "$@"; do
    case $arg in
        --install|-i)
            INSTALL=true
            ;;
        --background|-b|-d|--daemon)
            BACKGROUND=true
            ;;
        --stop)
            STOP=true
            ;;
        --restart|-r)
            RESTART=true
            ;;
        --status|-s)
            STATUS=true
            ;;
        --help|-h)
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --install, -i      Install/update dependencies"
            echo "  --background, -b   Run bot in background (daemon mode)"
            echo "  --stop             Stop running bot"
            echo "  --restart, -r      Restart bot"
            echo "  --status, -s       Show bot status"
            echo "  --help, -h         Show this help"
            echo ""
            echo "Examples:"
            echo "  ./start.sh                    # Run in foreground"
            echo "  ./start.sh -b                 # Run in background"
            echo "  ./start.sh --install -b       # Install deps and run in background"
            echo "  ./start.sh --restart          # Restart running bot"
            echo "  ./start.sh --stop             # Stop bot"
            echo ""
            exit 0
            ;;
    esac
done

print_header

# Handle status
if [ "$STATUS" = true ]; then
    show_status
    exit 0
fi

# Handle stop
if [ "$STOP" = true ]; then
    stop_bot
    exit 0
fi

# Handle restart
if [ "$RESTART" = true ]; then
    stop_bot
    BACKGROUND=true
fi

# Check Python version
echo -e "${YELLOW}Checking Python...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python not found!${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}Error: Python 3.10+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Create .env file with:${NC}"
    echo "  TELEGRAM_TOKEN=your_bot_token"
    echo "  SIGNAL_CHANNEL_IDS=-123456789"
    exit 1
fi
echo -e "${GREEN}✓ .env found${NC}"

# Create/activate virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
    INSTALL=true
fi

echo -e "${YELLOW}Activating venv...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ venv activated${NC}"

# Install dependencies
if [ "$INSTALL" = true ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Check if already running
if is_running; then
    echo -e "${YELLOW}Warning: Bot already running (PID: $(get_pid))${NC}"
    if [ "$BACKGROUND" = true ]; then
        echo -e "${YELLOW}Stopping old instance...${NC}"
        stop_bot
    else
        echo -e "Use './start.sh --stop' to stop it first"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Start the bot
if [ "$BACKGROUND" = true ]; then
    echo -e "${BLUE}Starting bot in background...${NC}"
    nohup $PYTHON_CMD bot.py >> "$LOG_FILE" 2>&1 &
    BOT_PID=$!
    echo $BOT_PID > "$PID_FILE"
    sleep 2
    
    if is_running; then
        echo -e "${GREEN}✓ Bot started (PID: $BOT_PID)${NC}"
        echo -e ""
        echo -e "${YELLOW}Useful commands:${NC}"
        echo -e "  View logs:  tail -f $LOG_FILE"
        echo -e "  Status:     ./start.sh --status"
        echo -e "  Stop:       ./start.sh --stop"
        echo -e "  Restart:    ./start.sh --restart"
    else
        echo -e "${RED}✗ Bot failed to start!${NC}"
        echo -e "Check logs: tail -50 $LOG_FILE"
        exit 1
    fi
else
    echo -e "${BLUE}Starting bot in foreground...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""
    $PYTHON_CMD bot.py
fi
