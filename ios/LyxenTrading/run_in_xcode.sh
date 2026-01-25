#!/bin/bash
# LyxenTrading - Quick run script
# This script opens the project in Xcode ready to run

set -e

echo "🚀 LyxenTrading iOS App Launcher"
echo "================================"

# Kill any hanging simctl processes
killall simctl 2>/dev/null || true
killall Simulator 2>/dev/null || true
sleep 2

# Clean derived data for fresh build
echo "🧹 Cleaning old builds..."
rm -rf ~/Library/Developer/Xcode/DerivedData/LyxenTrading-* 2>/dev/null || true

# Open project in Xcode
echo "🔧 Opening project in Xcode..."
open -a Xcode "$(dirname "$0")/LyxenTrading.xcodeproj"

sleep 3

# Start simulator
echo "📱 Starting simulator..."
open -a Simulator

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ Ready! Now in Xcode:                                   ║"
echo "║                                                            ║"
echo "║  1. Select a simulator from the dropdown (top center)     ║"
echo "║     Recommended: iPhone 16 Pro or iPhone 17 Pro Max       ║"
echo "║                                                            ║"
echo "║  2. Press Cmd+R to Build & Run                            ║"
echo "║                                                            ║"
echo "║  ⚠️  Note: xcrun simctl has a bug in Xcode 26.2 beta      ║"
echo "║     Running from Xcode GUI works correctly                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
