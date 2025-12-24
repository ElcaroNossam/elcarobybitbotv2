#!/bin/bash

# Backend Test Runner Script
# Provides convenient commands for running tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_color() {
    color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Show usage
show_usage() {
    cat << EOF
Backend Test Runner

Usage: $0 [command]

Commands:
    all             Run all tests
    unit            Run unit tests only
    integration     Run integration tests only
    api             Run API tests only
    database        Run database tests
    exchanges       Run exchange tests
    services        Run services tests
    core            Run core infrastructure tests
    webapp          Run webapp tests
    
    coverage        Run all tests with coverage report
    fast            Run tests excluding slow ones
    
    watch           Run tests in watch mode (re-run on file changes)
    
    install         Install test dependencies
    clean           Clean test cache and coverage data
    
Examples:
    $0 all          # Run all tests
    $0 unit         # Run only unit tests
    $0 coverage     # Run with coverage report

EOF
}

# Install test dependencies
install_deps() {
    print_color "$BLUE" "Installing test dependencies..."
    pip install pytest pytest-asyncio pytest-cov pytest-mock httpx fastapi uvicorn
    print_color "$GREEN" "✓ Dependencies installed"
}

# Clean test artifacts
clean() {
    print_color "$BLUE" "Cleaning test artifacts..."
    rm -rf .pytest_cache __pycache__ tests/__pycache__
    rm -rf htmlcov .coverage
    rm -rf tests/.pytest_cache tests/__pycache__
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    print_color "$GREEN" "✓ Cleaned"
}

# Run all tests
run_all() {
    print_color "$BLUE" "Running all tests..."
    pytest tests/ -v
}

# Run unit tests
run_unit() {
    print_color "$BLUE" "Running unit tests..."
    pytest tests/ -m unit -v
}

# Run integration tests
run_integration() {
    print_color "$BLUE" "Running integration tests..."
    pytest tests/ -m integration -v
}

# Run API tests
run_api() {
    print_color "$BLUE" "Running API tests..."
    pytest tests/ -m api -v
}

# Run database tests
run_database() {
    print_color "$BLUE" "Running database tests..."
    pytest tests/test_database.py -v
}

# Run exchange tests
run_exchanges() {
    print_color "$BLUE" "Running exchange tests..."
    pytest tests/test_exchanges.py -v
}

# Run services tests
run_services() {
    print_color "$BLUE" "Running services tests..."
    pytest tests/test_services.py -v
}

# Run core tests
run_core() {
    print_color "$BLUE" "Running core infrastructure tests..."
    pytest tests/test_core.py -v
}

# Run webapp tests
run_webapp() {
    print_color "$BLUE" "Running webapp tests..."
    pytest tests/test_webapp.py -v
}

# Run with coverage
run_coverage() {
    print_color "$BLUE" "Running tests with coverage..."
    pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
    print_color "$GREEN" "✓ Coverage report generated: htmlcov/index.html"
}

# Run fast tests (exclude slow)
run_fast() {
    print_color "$BLUE" "Running fast tests..."
    pytest tests/ -m "not slow" -v
}

# Watch mode (requires pytest-watch)
run_watch() {
    print_color "$BLUE" "Running tests in watch mode..."
    if command -v ptw &> /dev/null; then
        ptw tests/
    else
        print_color "$YELLOW" "pytest-watch not installed. Install with: pip install pytest-watch"
        print_color "$BLUE" "Falling back to single run..."
        pytest tests/ -v
    fi
}

# Main command handler
case "${1:-all}" in
    all)
        run_all
        ;;
    unit)
        run_unit
        ;;
    integration)
        run_integration
        ;;
    api)
        run_api
        ;;
    database)
        run_database
        ;;
    exchanges)
        run_exchanges
        ;;
    services)
        run_services
        ;;
    core)
        run_core
        ;;
    webapp)
        run_webapp
        ;;
    coverage)
        run_coverage
        ;;
    fast)
        run_fast
        ;;
    watch)
        run_watch
        ;;
    install)
        install_deps
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_color "$RED" "Unknown command: $1"
        echo
        show_usage
        exit 1
        ;;
esac

print_color "$GREEN" "✓ Done"
