#!/bin/bash
# Error Alerting Script - sends detailed error reports to admin
# Runs every 5 minutes via cron

LOG_FILE="/home/ubuntu/project/elcarobybitbotv2/logs/error_alerts.log"
BOT_TOKEN=$(grep TELEGRAM_TOKEN /home/ubuntu/project/elcarobybitbotv2/.env | cut -d= -f2)
ADMIN_ID="511692487"

# Check for errors in last 5 minutes
ERRORS=$(journalctl -u elcaro-bot --since "5 minutes ago" 2>/dev/null | grep -iE "ERROR|CRITICAL" | tail -20)
ERROR_COUNT=$(echo "$ERRORS" | grep -c . 2>/dev/null | tr -d '\n' || echo 0)
# Make sure ERROR_COUNT is a number
ERROR_COUNT=${ERROR_COUNT:-0}
ERROR_COUNT=$(echo $ERROR_COUNT | tr -d ' \n')

# Only send alert if there are errors
if [ "$ERROR_COUNT" -gt 0 ] && [ -n "$ERRORS" ]; then
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    
    # Extract unique error patterns
    UNIQUE_ERRORS=$(echo "$ERRORS" | grep -oE "(API_KEY_INVALID|INSUFFICIENT|ORDER_FAILED|RATE_LIMIT|LEVERAGE|PositionIdx|balance|position|unauthorized|timeout)[A-Za-z_]*" | sort | uniq -c | sort -rn | head -5)
    
    # Extract affected user IDs
    USER_IDS=$(echo "$ERRORS" | grep -oE "user[_id]*[=: ]+[0-9]+" | grep -oE "[0-9]+" | sort -u | head -5 | tr '\n' ' ')
    
    # Get last error line (truncated)
    LAST_ERROR=$(echo "$ERRORS" | tail -1 | cut -c1-180)
    
    # Build message with HTML formatting
    MESSAGE="🚨 <b>Error Alert</b>
⏰ $TIMESTAMP
📊 <b>$ERROR_COUNT errors</b> in last 5 min

<b>Error Types:</b>
<code>$UNIQUE_ERRORS</code>

<b>Affected Users:</b> $USER_IDS

<b>Last Error:</b>
<code>$LAST_ERROR</code>"

    # Log the alert
    echo "$TIMESTAMP - $ERROR_COUNT errors detected" >> "$LOG_FILE"
    
    # Send Telegram notification with inline keyboard
    if [ -n "$BOT_TOKEN" ]; then
        KEYBOARD='{"inline_keyboard":[[{"text":"📋 View Logs","callback_data":"admin:errors_list:0"},{"text":"👥 By User","callback_data":"admin:errors_by_user"}],[{"text":"🔄 Refresh","callback_data":"admin:errors_menu"}]]}'
        
        curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
            -d "chat_id=$ADMIN_ID" \
            -d "parse_mode=HTML" \
            -d "text=$MESSAGE" \
            -d "reply_markup=$KEYBOARD" \
            > /dev/null 2>&1
    fi
fi
