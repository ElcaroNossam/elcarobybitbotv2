#!/bin/bash
# Проверка здоровья системы Noet-Dat на production сервере

set -e

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🏥 Noet-Dat System Health Check"
echo "================================"
echo ""

# 1. Gunicorn статус
echo "1️⃣  Gunicorn Service"
echo "-------------------"
if systemctl is-active --quiet noetdat-gunicorn; then
    echo -e "${GREEN}✅ Gunicorn is running${NC}"
    systemctl status noetdat-gunicorn --no-pager -l | grep -E "(Active|Main PID|Memory)" | head -3
else
    echo -e "${RED}❌ Gunicorn is not running${NC}"
    echo "   Run: sudo systemctl start noetdat-gunicorn"
fi
echo ""

# 2. Workers статус (проверяем логи)
echo "2️⃣  Binance Workers"
echo "-----------------"
worker_running=$(journalctl -u noetdat-gunicorn --since "1 minute ago" | grep -c "worker" || echo "0")
if [ "$worker_running" -gt 0 ]; then
    echo -e "${GREEN}✅ Workers active (${worker_running} log entries in last minute)${NC}"
    
    # Показываем последнее сообщение от каждого worker
    echo ""
    echo "Recent worker activity:"
    journalctl -u noetdat-gunicorn --since "30 seconds ago" --no-pager | grep -E "(Spot worker|Futures worker)" | tail -5
else
    echo -e "${YELLOW}⚠️  No recent worker activity${NC}"
fi
echo ""

# 3. PostgreSQL
echo "3️⃣  PostgreSQL Database"
echo "---------------------"
if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
    
    # Проверяем подключение
    if psql -U cryptouser -d cryptoscreener -c "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database connection OK${NC}"
        
        # Статистика данных
        snapshot_count=$(psql -U cryptouser -d cryptoscreener -t -c "SELECT COUNT(*) FROM screener_screenersnapshot" 2>/dev/null || echo "0")
        liquidation_count=$(psql -U cryptouser -d cryptoscreener -t -c "SELECT COUNT(*) FROM screener_liquidation" 2>/dev/null || echo "0")
        
        echo "   Snapshots: $(echo $snapshot_count | xargs) records"
        echo "   Liquidations: $(echo $liquidation_count | xargs) records"
    else
        echo -e "${RED}❌ Cannot connect to database${NC}"
    fi
else
    echo -e "${RED}❌ PostgreSQL is not running${NC}"
fi
echo ""

# 4. Redis
echo "4️⃣  Redis Cache/PubSub"
echo "--------------------"
if systemctl is-active --quiet redis 2>/dev/null || systemctl is-active --quiet redis-server 2>/dev/null; then
    echo -e "${GREEN}✅ Redis is running${NC}"
    
    # Проверяем ping
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis responding to PING${NC}"
        
        # Показываем статистику
        redis_info=$(redis-cli info stats 2>/dev/null | grep -E "total_connections_received|total_commands_processed" || echo "")
        if [ -n "$redis_info" ]; then
            echo "   $redis_info"
        fi
    else
        echo -e "${RED}❌ Redis not responding${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Redis status unknown${NC}"
fi
echo ""

# 5. API Endpoints
echo "5️⃣  API Endpoints"
echo "---------------"

# Screener API
screener_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/screener/latest/?market_type=spot 2>/dev/null || echo "000")
if [ "$screener_status" == "200" ]; then
    echo -e "${GREEN}✅ Screener API: HTTP $screener_status${NC}"
else
    echo -e "${RED}❌ Screener API: HTTP $screener_status${NC}"
fi

# Liquidations API
liq_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/liquidations/?limit=1 2>/dev/null || echo "000")
if [ "$liq_status" == "200" ]; then
    echo -e "${GREEN}✅ Liquidations API: HTTP $liq_status${NC}"
else
    echo -e "${YELLOW}⚠️  Liquidations API: HTTP $liq_status${NC}"
fi
echo ""

# 6. Disk Space
echo "6️⃣  Disk Space"
echo "------------"
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    echo -e "${GREEN}✅ Disk usage: ${disk_usage}%${NC}"
else
    echo -e "${YELLOW}⚠️  Disk usage: ${disk_usage}% (consider cleanup)${NC}"
fi
df -h / | tail -1
echo ""

# 7. Memory
echo "7️⃣  Memory Usage"
echo "--------------"
mem_usage=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}')
if [ "$mem_usage" -lt 90 ]; then
    echo -e "${GREEN}✅ Memory: ${mem_usage}%${NC}"
else
    echo -e "${YELLOW}⚠️  Memory: ${mem_usage}% (high usage)${NC}"
fi
free -h | grep -E "Mem|Swap"
echo ""

# 8. Recent Errors
echo "8️⃣  Recent Errors (last 5 minutes)"
echo "--------------------------------"
error_count=$(journalctl -u noetdat-gunicorn --since "5 minutes ago" --no-pager | grep -ciE "(error|exception|traceback)" || echo "0")
if [ "$error_count" -eq 0 ]; then
    echo -e "${GREEN}✅ No errors in last 5 minutes${NC}"
else
    echo -e "${YELLOW}⚠️  ${error_count} errors found${NC}"
    echo ""
    echo "Recent errors:"
    journalctl -u noetdat-gunicorn --since "5 minutes ago" --no-pager | grep -iE "(error|exception)" | tail -3
fi
echo ""

# 9. WebSocket Reconnects
echo "9️⃣  WebSocket Health"
echo "------------------"
reconnects=$(journalctl -u noetdat-gunicorn --since "10 minutes ago" --no-pager | grep -c "reconnecting" || echo "0")
if [ "$reconnects" -lt 10 ]; then
    echo -e "${GREEN}✅ WebSocket stable (${reconnects} reconnects in last 10 min)${NC}"
else
    echo -e "${YELLOW}⚠️  Frequent reconnects: ${reconnects} in last 10 minutes${NC}"
    echo "   (This is normal for long-running Binance connections)"
fi
echo ""

# 10. Cleanup Service
echo "🔟 Cleanup Service"
echo "----------------"
if systemctl is-active --quiet noetdat-cleanup.timer 2>/dev/null; then
    echo -e "${GREEN}✅ Cleanup timer is active${NC}"
    systemctl status noetdat-cleanup.timer --no-pager | grep -E "(Next|Last)" | head -2
else
    echo -e "${YELLOW}⚠️  Cleanup timer not running${NC}"
    echo "   Run: sudo systemctl start noetdat-cleanup.timer"
fi
echo ""

# Итог
echo "================================"
echo -e "${BLUE}📊 Summary${NC}"
echo ""

# Подсчет проблем
issues=0

if ! systemctl is-active --quiet noetdat-gunicorn; then
    issues=$((issues + 1))
fi

if ! systemctl is-active --quiet postgresql; then
    issues=$((issues + 1))
fi

if [ "$screener_status" != "200" ]; then
    issues=$((issues + 1))
fi

if [ "$disk_usage" -gt 90 ]; then
    issues=$((issues + 1))
fi

if [ "$mem_usage" -gt 95 ]; then
    issues=$((issues + 1))
fi

if [ $issues -eq 0 ]; then
    echo -e "${GREEN}✅ All systems operational!${NC}"
else
    echo -e "${YELLOW}⚠️  ${issues} issue(s) detected${NC}"
    echo "   Review the output above for details"
fi
echo ""
echo "Last check: $(date)"
