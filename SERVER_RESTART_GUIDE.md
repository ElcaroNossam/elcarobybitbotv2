# 🔄 Server Restart Guide - ElCaro Bot

**Quick fix for "Internal Server Error" or WebApp not accessible**

---

## 🚨 Problem: Bot shows "Internal Server Error"

**Причина:** Cloudflare tunnel URL изменился после перезапуска

---

## ✅ Quick Fix (5 минут)

### 1. Проверить текущий статус
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com "
sudo systemctl status elcaro-bot --no-pager && 
ps aux | grep cloudflared | grep -v grep
"
```

### 2. Получить новый URL туннеля
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com "
tail -100 /tmp/cloudflared.log | grep -o 'https://[a-z-]*\.trycloudflare\.com' | tail -1
"
```
**Пример output:** `https://mountain-stats-retrieved-frontier.trycloudflare.com`

### 3. Обновить URL в конфигурации
```bash
# Замените NEW_URL на URL из шага 2
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com "
cd /home/ubuntu/project/elcarobybitbotv2 && 
echo 'NEW_URL' > run/ngrok_url.txt && 
sed -i 's|WEBAPP_URL=.*|WEBAPP_URL=NEW_URL|' .env && 
sudo systemctl restart elcaro-bot && 
echo '✅ Done'
"
```

### 4. Проверить что работает
```bash
curl -s https://YOUR-URL.trycloudflare.com/health
```
**Ожидаемый output:** `{"status":"healthy",...}`

---

## 🔧 Full Restart (если Quick Fix не помог)

### Полный перезапуск всех сервисов:
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com "
cd /home/ubuntu/project/elcarobybitbotv2 && 
sudo systemctl stop elcaro-bot && 
sleep 3 && 
sudo pkill -9 cloudflared && 
sleep 2 && 
sudo systemctl start elcaro-bot && 
sleep 20 && 
tail -50 /tmp/cloudflared.log | grep -o 'https://[a-z-]*\.trycloudflare\.com' | tail -1
"
```

Затем выполнить шаг 3 (обновить URL).

---

## 📋 Автоматический скрипт

Создайте на сервере:
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com "cat > /home/ubuntu/update_tunnel_url.sh << 'EOF'
#!/bin/bash
# Update Cloudflare Tunnel URL after bot restart

cd /home/ubuntu/project/elcarobybitbotv2

# Get new URL from cloudflared logs
NEW_URL=\$(tail -100 /tmp/cloudflared.log | grep -o 'https://[a-z-]*\.trycloudflare\.com' | tail -1)

if [ -z \"\$NEW_URL\" ]; then
    echo '❌ Error: Could not find tunnel URL in logs'
    exit 1
fi

echo \"📡 New tunnel URL: \$NEW_URL\"

# Update files
echo \"\$NEW_URL\" > run/ngrok_url.txt
sed -i \"s|WEBAPP_URL=.*|WEBAPP_URL=\$NEW_URL|\" .env

echo '✅ Updated run/ngrok_url.txt and .env'

# Restart bot to apply changes
sudo systemctl restart elcaro-bot
echo '🔄 Bot restarted with new URL'

sleep 5

# Test
if curl -s \"\$NEW_URL/health\" | grep -q 'healthy'; then
    echo '✅ WebApp is accessible!'
else
    echo '⚠️ WebApp check failed - may need a few more seconds'
fi
EOF
chmod +x /home/ubuntu/update_tunnel_url.sh
echo '✅ Script created at /home/ubuntu/update_tunnel_url.sh'
"
```

### Использование:
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com "
/home/ubuntu/update_tunnel_url.sh
"
```

---

## 🔍 Диагностика

### Проверить статус бота
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com "
sudo systemctl status elcaro-bot
"
```

### Проверить логи бота
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com "
journalctl -u elcaro-bot -n 50 --no-pager
"
```

### Проверить логи cloudflared
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com "
tail -50 /tmp/cloudflared.log
"
```

### Проверить процессы
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com "
ps aux | grep -E '(python.*bot|cloudflared|uvicorn)' | grep -v grep
"
```

---

## 📝 Текущая конфигурация (Dec 25, 2025)

**Сервер:** ec2-3-66-84-33.eu-central-1.compute.amazonaws.com  
**User:** ubuntu  
**SSH Key:** noet-dat.pem  
**Bot Path:** /home/ubuntu/project/elcarobybitbotv2  
**Service:** elcaro-bot.service  

**WebApp URL (актуальный):**
```
https://mountain-stats-retrieved-frontier.trycloudflare.com
```

**Health Check:**
```bash
curl https://mountain-stats-retrieved-frontier.trycloudflare.com/health
```

---

## ⚠️ Важные заметки

1. **Cloudflare Tunnel URL меняется** при каждом перезапуске cloudflared процесса
2. После перезапуска бота **обязательно обновить URL** в `.env` и `run/ngrok_url.txt`
3. Бот автоматически установит Menu Button с новым URL при старте
4. WebApp (uvicorn) работает на порту 8765 локально
5. Cloudflare tunnel направляет трафик на localhost:8765

---

*Last updated: December 25, 2025*  
*Current tunnel: https://mountain-stats-retrieved-frontier.trycloudflare.com*
