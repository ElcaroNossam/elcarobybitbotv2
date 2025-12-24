#!/bin/bash

# Quick Test Verification Script
# Runs essential tests to verify the test suite is working

echo "========================================="
echo "Backend Test Suite Verification"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}1. Checking Python version...${NC}"
python3 --version
echo ""

echo -e "${BLUE}2. Checking pytest installation...${NC}"
python3 -m pytest --version
echo ""

echo -e "${BLUE}3. Collecting all tests...${NC}"
TEST_COUNT=$(python3 -m pytest tests/ --co -q 2>&1 | grep -E "^[0-9]+ items?" | cut -d' ' -f1)
echo "Total tests found: $TEST_COUNT"
echo ""

echo -e "${BLUE}4. Running quick verification tests...${NC}"
python3 -m pytest tests/test_quick_verify.py -v
RESULT=$?
echo ""

if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Test infrastructure is working correctly!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run all tests:        ./run_tests.sh all"
    echo "  2. Run with coverage:    ./run_tests.sh coverage"
    echo "  3. Run specific tests:   ./run_tests.sh database"
    echo ""
    echo "Documentation:"
    echo "  - Full guide:            tests/README.md"
    echo "  - Test summary:          TESTING_SUMMARY.md"
    echo "  - Test examples:         tests/test_examples.py"
else
    echo -e "${RED}✗ Tests failed. Check the output above.${NC}"
    exit 1
fi
