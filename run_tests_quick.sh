#!/bin/bash
# Quick Test Runner for Enliko Trading Platform

echo "🚀 Enliko Trading Platform - Test Suite Runner"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if in correct directory
if [ ! -f "bot.py" ]; then
    echo -e "${RED}Error: Must run from project root directory${NC}"
    exit 1
fi

# Function to run tests
run_tests() {
    local test_file=$1
    local description=$2
    
    echo -e "${YELLOW}Running: $description${NC}"
    python3 -m pytest "$test_file" -v --tb=short
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $description - PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ $description - FAILED${NC}"
        return 1
    fi
}

# Parse command line arguments
case "$1" in
    --all|-a)
        echo "📋 Running ALL tests (86 tests)..."
        echo ""
        run_tests "tests/test_advanced_features.py tests/test_services_full.py" "Complete Test Suite"
        ;;
    
    --basic|-b)
        echo "📋 Running BASIC tests (27 tests)..."
        echo ""
        run_tests "tests/test_advanced_features.py" "Basic Functionality Tests"
        ;;
    
    --full|-f)
        echo "📋 Running COMPREHENSIVE tests (59 tests)..."
        echo ""
        run_tests "tests/test_services_full.py" "Comprehensive Edge Case Tests"
        ;;
    
    --position|-p)
        echo "📋 Running POSITION CALCULATOR tests..."
        echo ""
        run_tests "tests/test_services_full.py::TestPositionCalculatorFull" "Position Calculator Tests"
        ;;
    
    --indicators|-i)
        echo "📋 Running INDICATORS tests..."
        echo ""
        run_tests "tests/test_services_full.py::TestAdvancedIndicatorsFull" "Advanced Indicators Tests"
        ;;
    
    --orderbook|-o)
        echo "📋 Running ORDERBOOK tests..."
        echo ""
        run_tests "tests/test_services_full.py::TestOrderbookAnalyzerFull" "Orderbook Analyzer Tests"
        ;;
    
    --risk|-r)
        echo "📋 Running RISK MANAGEMENT tests..."
        echo ""
        run_tests "tests/test_services_full.py::TestRiskManagementFull" "Risk Management Tests"
        ;;
    
    --timeframe|-t)
        echo "📋 Running MULTI-TIMEFRAME tests..."
        echo ""
        run_tests "tests/test_services_full.py::TestMultiTimeframeFull" "Multi-Timeframe Tests"
        ;;
    
    --strategy|-s)
        echo "📋 Running STRATEGY BUILDER tests..."
        echo ""
        run_tests "tests/test_services_full.py::TestStrategyBuilderFull" "Strategy Builder Tests"
        ;;
    
    --monte|-m)
        echo "📋 Running MONTE CARLO tests..."
        echo ""
        run_tests "tests/test_services_full.py::TestMonteCarloFull" "Monte Carlo Tests"
        ;;
    
    --walk|-w)
        echo "📋 Running WALK FORWARD tests..."
        echo ""
        run_tests "tests/test_services_full.py::TestWalkForwardFull" "Walk Forward Tests"
        ;;
    
    --integration|-n)
        echo "📋 Running INTEGRATION tests..."
        echo ""
        run_tests "tests/test_services_full.py::TestIntegrationComplex" "Integration Tests"
        ;;
    
    --stress|-x)
        echo "📋 Running STRESS tests..."
        echo ""
        run_tests "tests/test_services_full.py::TestStressTests" "Stress Tests"
        ;;
    
    --quick|-q)
        echo "⚡ Running QUICK test check (no output)..."
        echo ""
        python3 -m pytest tests/ -v --tb=no -q
        ;;
    
    --coverage|-c)
        echo "📊 Running tests with COVERAGE..."
        echo ""
        python3 -m pytest tests/ --cov=webapp/services --cov-report=html --cov-report=term
        echo ""
        echo -e "${GREEN}Coverage report generated at: htmlcov/index.html${NC}"
        ;;
    
    --help|-h|*)
        echo "Usage: ./run_tests_quick.sh [OPTION]"
        echo ""
        echo "Options:"
        echo "  -a, --all           Run all tests (86 tests) [default]"
        echo "  -b, --basic         Run basic tests only (27 tests)"
        echo "  -f, --full          Run comprehensive tests only (59 tests)"
        echo ""
        echo "Individual test categories:"
        echo "  -p, --position      Position Calculator tests (8 tests)"
        echo "  -i, --indicators    Advanced Indicators tests (7 tests)"
        echo "  -o, --orderbook     Orderbook Analyzer tests (6 tests)"
        echo "  -r, --risk          Risk Management tests (10 tests)"
        echo "  -t, --timeframe     Multi-Timeframe tests (4 tests)"
        echo "  -s, --strategy      Strategy Builder tests (4 tests)"
        echo "  -m, --monte         Monte Carlo tests (7 tests)"
        echo "  -w, --walk          Walk Forward tests (5 tests)"
        echo "  -n, --integration   Integration tests (3 tests)"
        echo "  -x, --stress        Stress tests (5 tests)"
        echo ""
        echo "Utility options:"
        echo "  -q, --quick         Quick test check (minimal output)"
        echo "  -c, --coverage      Run with coverage report"
        echo "  -h, --help          Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests_quick.sh --all          # Run all 86 tests"
        echo "  ./run_tests_quick.sh --position     # Run position calculator tests only"
        echo "  ./run_tests_quick.sh --stress       # Run stress tests only"
        echo "  ./run_tests_quick.sh --coverage     # Generate coverage report"
        echo ""
        ;;
esac

echo ""
echo "=============================================="
echo "✨ Test run complete!"
