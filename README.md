# Elcaro Bybit Trading Bot v2

Async Telegram trading bot for Bybit cryptocurrency futures.

## Server Setup

**Path:** `/home/ubuntu/project/elcarobybitbotv2`

### Quick Start

```bash
# 1. Go to project folder
cd /home/ubuntu/project/elcarobybitbotv2

# 2. Create .env file
cp .env.example .env
nano .env  # Fill in TELEGRAM_TOKEN and SIGNAL_CHANNEL_IDS

# 3. Install and run
./start.sh --install -b
```

### Commands

```bash
./start.sh                # Run in foreground
./start.sh -b             # Run in background
./start.sh --install -b   # Install deps + run
./start.sh --status       # Check status
./start.sh --stop         # Stop bot
./start.sh --restart      # Restart bot
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
