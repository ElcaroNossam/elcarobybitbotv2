#!/bin/bash
set -e

echo "========================================"
echo "  Enliko Auto-Login Quick Check"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current URL
if [ -f "run/ngrok_url.txt" ]; then
    URL=$(cat run/ngrok_url.txt)
else
    echo -e "${RED}❌ run/ngrok_url.txt not found${NC}"
    exit 1
fi

echo -e "${YELLOW}🔗 Testing URL: $URL${NC}"
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/health" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed (HTTP $HTTP_CODE)${NC}"
    exit 1
fi
echo ""

# Test 2: Dashboard accessible
echo "Test 2: Dashboard Access"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/dashboard" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Dashboard accessible${NC}"
else
    echo -e "${RED}❌ Dashboard not accessible (HTTP $HTTP_CODE)${NC}"
    exit 1
fi
echo ""

# Test 3: Dashboard with start parameter
TEST_USER_ID="511692487"
echo "Test 3: Dashboard with start parameter (user_id: $TEST_USER_ID)"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/dashboard?start=$TEST_USER_ID" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Dashboard with start param works${NC}"
else
    echo -e "${RED}❌ Dashboard with start param failed (HTTP $HTTP_CODE)${NC}"
    exit 1
fi
echo ""

# Test 4: Direct login API
echo "Test 4: Direct Login API"
RESPONSE=$(curl -s -X POST "$URL/api/auth/direct-login" \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": $TEST_USER_ID}" 2>/dev/null || echo "")

if echo "$RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Direct login API works${NC}"
    TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "   Token: ${TOKEN:0:20}..."
else
    echo -e "${RED}❌ Direct login API failed${NC}"
    echo "   Response: $RESPONSE"
    exit 1
fi
echo ""

# Test 5: Token validation
echo "Test 5: Token Validation (/api/auth/me)"
if [ -n "$TOKEN" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/api/auth/me" \
        -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Token validation works${NC}"
    else
        echo -e "${RED}❌ Token validation failed (HTTP $HTTP_CODE)${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Skipped (no token)${NC}"
fi
echo ""

# Test 6: Menu Button URL format
echo "Test 6: Menu Button URL Format"
MENU_URL="$URL/dashboard"
echo "   Expected format: https://[subdomain].trycloudflare.com/dashboard"
echo "   Actual URL: $MENU_URL"
if [[ "$MENU_URL" =~ ^https://.*\.trycloudflare\.com/dashboard$ ]]; then
    echo -e "${GREEN}✅ Menu Button URL format correct${NC}"
else
    echo -e "${YELLOW}⚠️  URL format unusual (might be local/custom)${NC}"
fi
echo ""

echo "========================================"
echo -e "${GREEN}✅ AUTO-LOGIN SYSTEM HEALTHY${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Restart Telegram app"
echo "2. Click Menu button (three lines)"
echo "3. Should auto-login to dashboard"
echo ""
