# ElCaro Trading Platform v2.1.0

**Multi-exchange async trading bot + WebApp + Real-time Screener**

Supported Exchanges: Bybit, HyperLiquid  
Markets: Futures, Spot  
Features: Telegram Bot, Web Terminal, Live Screener, AI Agent, Backtesting

---

## 🌐 Production Server Info (Updated Dec 24, 2025)

**AWS EC2 Server (eu-central-1)**
- **Host:** `ec2-3-66-84-33.eu-central-1.compute.amazonaws.com`
- **User:** `ubuntu`
- **SSH Key:** `noet-dat.pem` (в корне проекта)
- **Bot Path:** `/home/ubuntu/project/elcarobybitbotv2/`
- **Systemd Service:** `elcaro-bot.service` (enabled, auto-restart)
- **Cloudflare Tunnel:** 🆓 Автоматически создается при каждом запуске!
- **Current URL:** Обновляется в `/run/ngrok_url.txt` и `.env`

**Server Resources:**
- Disk: 16GB (21% used - 13GB free)
- Memory: 1.9GB + 1GB swap
- Auto-cleanup: Daily at 3 AM UTC (cron)

**SSH Connect:**
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com
```

---

## 🚀 Quick Start (Updated Dec 24, 2025)

### Local Development

```bash
# 1. Clone and setup
cd bybit_demo/
cp .env.example .env
nano .env  # Add TELEGRAM_TOKEN and SIGNAL_CHANNEL_IDS

# 2. Install dependencies
./start.sh --install

# 3. Start all services (daemon mode)
./start.sh --daemon
# or simply
./start.sh --restart
```

**Services Started:**
- ✅ Telegram Bot (PID tracked)
- ✅ WebApp on port 8765 (with health checks)
- ✅ Real-time Screener (WebSocket updates every 3s)
- ✅ Cloudflare Tunnel (auto-generated public URL)

---

## 📋 Commands (start.sh v2.1.0)

| Command | Description |
|---------|-------------|
| `./start.sh --daemon` | Start all services in background |
| `./start.sh --restart` | Restart all services |
| `./start.sh --status` | Show service status |
| `./start.sh --stop` | Stop all services |
| `./start.sh --bot` | Start only Telegram bot |
| `./start.sh --webapp` | Start only WebApp |
| `./start.sh --install` | Install/update dependencies |
| `./start.sh --clean` | Clean caches and temp files |
| `./start.sh --help` | Show all options |

### Examples

```bash
# Start everything
./start.sh --restart

# Check if running
./start.sh --status

# View logs
tail -f logs/bot.log
tail -f logs/webapp.log

# Stop everything
./start.sh --stop

# Development mode (hot reload)
./start.sh  # foreground mode with --reload
```

---

## 🌐 Access Points

After `./start.sh --daemon`:

| Service | URL | Description |
|---------|-----|-------------|
| **WebApp** | http://localhost:8765 | Main dashboard |
| **Terminal** | http://localhost:8765/terminal | Trading terminal |
| **Screener** | http://localhost:8765/screener | Real-time market data |
| **API Docs** | http://localhost:8765/api/docs | Swagger UI |
| **Health** | http://localhost:8765/health | Health check endpoint |
| **Tunnel** | https://xxx.trycloudflare.com | Public URL (auto) |

---

## 🖥️ Server Setup (Production)

**Path:** `/home/ubuntu/project/elcarobybitbotv2`

### SSH Connection
```bash
ssh -i rita.pem ubuntu@46.62.211.0
cd /home/ubuntu/project/elcarobybitbotv2
```

### Deploy Changes
```bash
# Pull latest changes
git pull origin main

# Restart services
./start.sh --restart

# Check status
./start.sh --status

# View logs
journalctl -u elcaro-bot -f --no-pager
```

### Systemd (Autostart)

```bash
# Install service
sudo cp bybit-bot.service /etc/systemd/system/elcaro-bot.service
sudo systemctl daemon-reload
sudo systemctl enable elcaro-bot
sudo systemctl start elcaro-bot

# Commands
sudo systemctl status elcaro-bot
sudo systemctl stop elcaro-bot
sudo systemctl restart elcaro-bot
journalctl -u elcaro-bot -f  # View logs
```

### Logs

```bash
tail -f bot.log           # View logs
tail -100 bot.log         # Last 100 lines
```

## Files

| File | Description |
|------|-------------|
| `bot.py` | Main bot logic |
| `db.py` | SQLite database |
| `coin_params.py` | Trading parameters |
| `translations/` | Multi-language support |
| `.env` | Configuration (secrets) |
| `start.sh` | Startup script |
| `bot.log` | Log file |
| `bot.db` | Database |

## Requirements

- Python 3.10+
- Ubuntu 22.04+ (server)
