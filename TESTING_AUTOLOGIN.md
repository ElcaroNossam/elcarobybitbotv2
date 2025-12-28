# 🧪 Auto-Login Testing - Quick Guide

## 🚀 Quick Test (2 seconds)

```bash
./run_autologin_tests.sh
```

All 6 tests should pass ✅

---

## 📝 What Gets Tested

1. **Health Check** - API is up and running
2. **Dashboard Access** - Page loads correctly
3. **Dashboard with start param** - `?start=USER_ID` works
4. **Direct Login API** - Returns valid JWT token
5. **Token Validation** - Token works with `/api/auth/me`
6. **URL Format** - Menu Button URL is correct

---

## 🔍 Manual Testing

### Test on Server
```bash
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com \
  'cd /home/ubuntu/project/elcarobybitbotv2 && ./test_autologin.sh'
```

### Test Locally (if webapp running)
```bash
./test_autologin.sh
```

### Full Test Suite
```bash
python3 -m pytest tests/test_autologin.py -v
```

---

## 🎯 Test in Telegram

1. **Close Telegram completely** (don't just minimize)
2. **Open Telegram again**
3. **Open bot:** @elcaroprem_bot
4. **Click Menu button** (⋮ three horizontal lines at bottom right)
5. **Dashboard should open and auto-login** ✅

If it doesn't work:
- Send `/start` to bot first
- Wait 5 seconds
- Try Menu button again

---

## 🐛 Debugging Failed Tests

### Test 1 Failed (Health Check)
```bash
# Check if webapp is running
systemctl status elcaro-webapp

# Check webapp logs
journalctl -u elcaro-webapp -n 50
```

### Test 4 Failed (Direct Login API)
```bash
# Check API endpoint manually
curl -X POST https://[URL]/api/auth/direct-login \
  -H "Content-Type: application/json" \
  -d '{"user_id": 511692487}'

# Should return: {"access_token": "...", "user": {...}}
```

### Test 5 Failed (Token Validation)
```bash
# Get a token first
TOKEN=$(curl -s -X POST https://[URL]/api/auth/direct-login \
  -H "Content-Type: application/json" \
  -d '{"user_id": 511692487}' | jq -r '.access_token')

# Test /auth/me
curl -H "Authorization: Bearer $TOKEN" https://[URL]/api/auth/me
```

### User Not Found
```python
# Check if user exists in database
import db
user_id = 511692487
user = db.get_user_config(user_id)
print(user.get('username'), user.get('first_name'))

# If None, user needs to send /start to bot
```

---

## 📊 Expected Output

```
========================================
  ElCaro Auto-Login Quick Check
========================================

✅ Health check passed
✅ Dashboard accessible
✅ Dashboard with start param works
✅ Direct login API works
✅ Token validation works
✅ Menu Button URL format correct

========================================
✅ AUTO-LOGIN SYSTEM HEALTHY
========================================
```

---

## 🔄 Run After Every Deploy

```bash
# 1. Deploy changes
scp -i noet-dat.pem webapp/templates/dashboard.html ubuntu@SERVER:/path/

# 2. Restart webapp
ssh -i noet-dat.pem ubuntu@SERVER 'sudo systemctl restart elcaro-webapp'

# 3. Run tests
./run_autologin_tests.sh

# 4. If all pass ✅ - deployment successful!
```

---

## 📅 Automated Daily Tests

Add to crontab on server:
```bash
# Run auto-login tests daily at 2 AM
0 2 * * * cd /home/ubuntu/project/elcarobybitbotv2 && ./test_autologin.sh >> logs/autologin_daily.log 2>&1
```

Check logs:
```bash
tail -50 /home/ubuntu/project/elcarobybitbotv2/logs/autologin_daily.log
```

---

## 📱 Mobile Testing Checklist

- [ ] Open bot on mobile
- [ ] Click Menu button
- [ ] Dashboard loads
- [ ] Auto-login works
- [ ] Username appears in top right
- [ ] Can see balance/positions
- [ ] Can switch exchanges
- [ ] No errors in console

---

## 🆘 Get Help

If tests fail:
1. Check [AUTOLOGIN_FIXED.md](AUTOLOGIN_FIXED.md) for detailed docs
2. Run `./test_autologin.sh` for diagnosis
3. Check webapp logs: `journalctl -u elcaro-webapp -f`
4. Check bot logs: `journalctl -u elcaro-bot -f`

---

**Last Updated:** December 25, 2025  
**Status:** ✅ All tests passing  
**Current URL:** https://wheels-cabinet-theatre-trial.trycloudflare.com
