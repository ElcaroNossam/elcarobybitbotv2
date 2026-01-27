#!/bin/bash
# Enliko Bot - Local Optimization Script
# Automatically cleans cache, logs, and optimizes database

set -e

echo "🧹 Enliko Bot - Local Optimization"
echo "=================================="
echo ""

# Stop any running processes
echo "1. Checking for running processes..."
RUNNING_PIDS=$(ps aux | grep -E "python.*bot\.py|cloudflared|uvicorn.*webapp" | grep -v grep | awk '{print $2}' || true)
if [ -n "$RUNNING_PIDS" ]; then
    echo "   ⚠️  Found running processes: $RUNNING_PIDS"
    echo "   Stopping them..."
    echo "$RUNNING_PIDS" | xargs kill -9 2>/dev/null || true
    echo "   ✓ Processes stopped"
else
    echo "   ✓ No processes running"
fi
echo ""

# Clean Python cache
echo "2. Cleaning Python cache..."
CACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
echo "   ✓ Removed $CACHE_COUNT __pycache__ directories"
echo ""

# Clean logs
echo "3. Cleaning logs..."
if [ -d "logs" ]; then
    LOG_SIZE=$(du -sh logs/ 2>/dev/null | awk '{print $1}')
    find logs/ -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
    truncate -s 0 logs/*.log 2>/dev/null || true
    echo "   ✓ Cleaned logs (was $LOG_SIZE)"
else
    echo "   ℹ️  No logs directory"
fi
echo ""

# Clean runtime files
echo "4. Cleaning runtime files..."
if [ -d "run" ]; then
    rm -f run/*.pid run/*.log run/ngrok_url.txt 2>/dev/null || true
    echo "   ✓ Cleaned run/ directory"
else
    echo "   ℹ️  No run directory"
fi
echo ""

# Clean pytest cache
echo "5. Cleaning pytest cache..."
rm -rf .pytest_cache tests/.pytest_cache tests/__pycache__ 2>/dev/null || true
echo "   ✓ Pytest cache removed"
echo ""

# Optimize database
echo "6. Optimizing database..."
if [ -f "bot.db" ]; then
    DB_SIZE_BEFORE=$(du -h bot.db | awk '{print $1}')
    sqlite3 bot.db "VACUUM;" 2>/dev/null || true
    sqlite3 bot.db "ANALYZE;" 2>/dev/null || true
    DB_SIZE_AFTER=$(du -h bot.db | awk '{print $1}')
    echo "   ✓ Database optimized ($DB_SIZE_BEFORE → $DB_SIZE_AFTER)"
else
    echo "   ℹ️  No bot.db found"
fi
echo ""

# Git cleanup
echo "7. Optimizing git repository..."
git gc --aggressive --prune=now > /dev/null 2>&1 || true
echo "   ✓ Git repository optimized"
echo ""

# Remove temporary files
echo "8. Removing temporary files..."
TEMP_COUNT=$(find . -type f \( -name "*.tmp" -o -name "*~" -o -name ".DS_Store" \) 2>/dev/null | wc -l)
find . -type f \( -name "*.tmp" -o -name "*~" -o -name ".DS_Store" \) -delete 2>/dev/null || true
echo "   ✓ Removed $TEMP_COUNT temporary files"
echo ""

# Summary
echo "=================================="
echo "✅ Optimization Complete!"
echo ""
echo "Current disk usage:"
du -sh . 2>/dev/null
echo ""
echo "Largest directories:"
du -sh */ 2>/dev/null | sort -h | tail -5
echo ""
echo "To start bot: ./start.sh --bot"
