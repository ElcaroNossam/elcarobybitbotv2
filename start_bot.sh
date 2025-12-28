#!/bin/bash
set -e

PROJECT_DIR="/home/ubuntu/project/elcarobybitbotv2"
LOG_FILE="$PROJECT_DIR/logs/startup.log"

mkdir -p "$PROJECT_DIR/logs"

echo "[$(date)] Starting ElCaro bot..." >> "$LOG_FILE"

# Start bot directly (nginx handles domain routing)
cd "$PROJECT_DIR"
exec ./venv/bin/python bot.py
