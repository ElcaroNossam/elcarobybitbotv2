#!/bin/bash
# Quick Test Autologin - Run on server after deploy

echo "════════════════════════════════════════════════════════════"
echo "  Running Auto-Login Tests on Server"
echo "════════════════════════════════════════════════════════════"

ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com \
  'cd /home/ubuntu/project/elcarobybitbotv2 && ./test_autologin.sh'

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ALL TESTS PASSED - Auto-login is working!"
    echo ""
    echo "You can now:"
    echo "  1. Close Telegram completely"
    echo "  2. Open Telegram again"
    echo "  3. Click Menu button (⋮) in bot"
    echo "  4. Dashboard will auto-login ✅"
else
    echo ""
    echo "❌ TESTS FAILED - Check output above"
fi
