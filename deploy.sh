#!/bin/bash
# Lyxen Bot Deploy Script
# Usage: ./deploy.sh [message]

set -e

SERVER="ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com"
KEY="noet-dat.pem"
REMOTE_PATH="/home/ubuntu/project/elcarobybitbotv2"
BRANCH="bugfixes-critical-dec24"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}=== Lyxen Bot Deploy ===${NC}"

# Check for changes
if ! git diff --quiet; then
    echo -e "${YELLOW}📦 Staging changes...${NC}"
    git add -A
    
    # Commit message
    if [ -n "$1" ]; then
        MSG="$1"
    else
        MSG="Update $(date +%Y-%m-%d\ %H:%M)"
    fi
    
    echo -e "${YELLOW}💾 Committing: $MSG${NC}"
    git commit -m "$MSG"
else
    echo -e "${GREEN}✓ No local changes${NC}"
fi

# Push to GitHub
echo -e "${YELLOW}🚀 Pushing to GitHub...${NC}"
git push origin $BRANCH

# Deploy to server
echo -e "${YELLOW}📡 Deploying to server...${NC}"
ssh -i $KEY $SERVER "cd $REMOTE_PATH && git fetch origin && git reset --hard origin/$BRANCH"

# Restart bot
echo -e "${YELLOW}🔄 Restarting bot...${NC}"
ssh -i $KEY $SERVER "sudo systemctl restart elcaro-bot && sleep 2 && sudo systemctl status elcaro-bot --no-pager | head -10"

echo -e "${GREEN}✅ Deploy complete!${NC}"
echo -e "${GREEN}Log: ssh -i $KEY $SERVER 'journalctl -u elcaro-bot -f'${NC}"
