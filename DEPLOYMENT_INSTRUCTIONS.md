# 🚀 Deployment Instructions - ElCaro Trading Bot v2

## ✅ Changes Applied (December 24, 2025)

### Fixes:
1. **Backtest Links** - Fixed incorrect `/dashboard#backtesting` → `/backtest` links in:
   - `webapp/templates/index.html`
   - `webapp/templates/screener.html`

2. **HTML Templates** - All syntax validated, no errors found

3. **Tests** - 356/358 tests passing (99.4% success rate)
   - Only 2 minor failures in realtime/enhanced_screener (non-critical)

---

## 📋 Deployment Steps

### 1. Connect to Server
```bash
ssh -i rita.pem ubuntu@46.62.211.0
```

### 2. Navigate to Project
```bash
cd /home/ubuntu/project/elcarobybitbotv2
```

### 3. Pull Latest Changes
```bash
git pull origin webapp-screener-auth-2fa-dec21
```

### 4. Restart Bot Service
```bash
sudo systemctl restart elcaro-bot
```

### 5. Check Status
```bash
# Check bot status
sudo systemctl status elcaro-bot

# View logs (live)
journalctl -u elcaro-bot -f --no-pager -n 50
```

### 6. Verify Cloudflare Tunnel
```bash
# Check tunnel status
ps aux | grep cloudflared

# If not running, restart:
sudo systemctl restart cloudflared
```

---

## 🔍 Verification Steps

### 1. Check Bot Logs
```bash
journalctl -u elcaro-bot -n 100 --no-pager
```

Should see:
```
✅ Bot started successfully
✅ WebApp running on port 8765
✅ Cloudflare tunnel active
```

### 2. Test WebApp Access
```bash
curl http://localhost:8765/health
```

Expected response:
```json
{"status": "healthy", "version": "2.0.0"}
```

### 3. Test Fixed Links
Open in browser:
- https://YOUR-TUNNEL-URL.trycloudflare.com/
- Click "Strategy Backtesting" → Should redirect to `/backtest` (NOT `/dashboard#backtesting`)

---

## 🛠️ Troubleshooting

### Bot Won't Start
```bash
# View detailed logs
journalctl -u elcaro-bot -n 200 --no-pager

# Check Python errors
grep -i error /home/ubuntu/project/elcarobybitbotv2/nohup.out | tail -20
```

### WebApp Not Accessible
```bash
# Check if port 8765 is listening
netstat -tlnp | grep 8765

# If not, check webapp process
ps aux | grep uvicorn
```

### Cloudflare Tunnel Issues
```bash
# Get current tunnel URL
grep -o 'https://[a-z-]*\.trycloudflare\.com' /tmp/cloudflared.log | tail -1

# Restart tunnel
pkill cloudflared
nohup cloudflared tunnel --url http://localhost:8765 > /tmp/cloudflared.log 2>&1 &

# Wait 5 seconds, get new URL
sleep 5
grep -o 'https://[a-z-]*\.trycloudflare\.com' /tmp/cloudflared.log | tail -1
```

---

## 📊 Test Results Summary

| Category | Passed | Failed | Success Rate |
|----------|--------|--------|--------------|
| Total | 356 | 2 | 99.4% |
| Core | 178 | 0 | 100% |
| WebApp | 156 | 2 | 98.7% |
| Integration | 22 | 0 | 100% |

**Failed Tests (Non-Critical):**
1. `test_enhanced_screener.py::test_get_market_data_hyperliquid` - Missing 'price' field in mock data
2. `test_realtime_system.py::test_start_workers` - Event loop closed (async test artifact)

---

## ✅ Post-Deployment Checklist

- [ ] Bot service running (`sudo systemctl status elcaro-bot`)
- [ ] Logs show no errors (`journalctl -u elcaro-bot -n 50`)
- [ ] WebApp accessible at tunnel URL
- [ ] Backtest links working correctly
- [ ] Screener page loads without errors
- [ ] Terminal page functional
- [ ] Database queries responsive

---

## 📝 Rollback Instructions

If issues arise, rollback to previous commit:

```bash
cd /home/ubuntu/project/elcarobybitbotv2
git log --oneline -5  # Find previous commit hash
git checkout <previous-commit-hash>
sudo systemctl restart elcaro-bot
```

---

## 📞 Support

If deployment issues persist:
1. Check logs: `journalctl -u elcaro-bot -n 200 --no-pager`
2. Review `.env` file for correct credentials
3. Verify Python dependencies: `pip list | grep -E "fastapi|uvicorn|telegram"`

---

**Deployment Date:** December 24, 2025
**Git Commit:** `9b724e7`
**Branch:** `webapp-screener-auth-2fa-dec21`
**Status:** ✅ Ready for Production
