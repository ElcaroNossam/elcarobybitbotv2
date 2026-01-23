# Backend Testing Guide

Comprehensive test suite for Lyxen Trading Bot backend.

## Test Structure

```
tests/
├── __init__.py              # Test package init
├── conftest.py              # PyTest fixtures and configuration
├── pytest.ini               # PyTest settings
├── .coveragerc              # Coverage configuration
├── test_database.py         # Database layer tests
├── test_exchanges.py        # Exchange adapter tests
├── test_services.py         # Services layer tests
├── test_exchange_router.py  # Exchange routing tests
├── test_core.py             # Core infrastructure tests
├── test_webapp.py           # WebApp API tests
└── test_integration.py      # Integration & E2E tests
```

## Installation

### Install Test Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
```

Or add to `requirements.txt`:

```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
httpx>=0.24.0  # For FastAPI testing
```

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test Category

```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests
pytest tests/ -m integration

# API tests
pytest tests/ -m api

# Slow tests
pytest tests/ -m slow
```

### Run Specific Test File

```bash
pytest tests/test_database.py
pytest tests/test_exchanges.py
pytest tests/test_services.py
```

### Run Specific Test Class or Function

```bash
# Run specific class
pytest tests/test_database.py::TestUserManagement

# Run specific test
pytest tests/test_database.py::TestUserManagement::test_ensure_user_creates_new_user
```

### Verbose Output

```bash
pytest tests/ -v
```

### Show Print Statements

```bash
pytest tests/ -s
```

### Stop on First Failure

```bash
pytest tests/ -x
```

## Coverage Reports

### Generate Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html
```

This creates `htmlcov/index.html` with detailed coverage report.

### Terminal Coverage Report

```bash
pytest tests/ --cov=. --cov-report=term-missing
```

### Coverage for Specific Module

```bash
pytest tests/test_database.py --cov=db --cov-report=term
```

## Test Markers

Tests are organized with markers for easy filtering:

| Marker | Description |
|--------|-------------|
| `unit` | Unit tests for individual components |
| `integration` | Integration tests for component interactions |
| `e2e` | End-to-end workflow tests |
| `api` | WebApp API endpoint tests |
| `database` | Database-related tests |
| `exchange` | Exchange integration tests |
| `services` | Service layer tests |
| `core` | Core infrastructure tests |
| `slow` | Long-running tests |

### Run Multiple Markers

```bash
pytest tests/ -m "unit and database"
pytest tests/ -m "integration or e2e"
```

### Skip Markers

```bash
pytest tests/ -m "not slow"
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run tests
      run: pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Writing New Tests

### Test Template

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

class TestMyFeature:
    """Test description"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_my_async_function(self, test_user_id):
        """Test specific behavior"""
        # Arrange
        mock_client = AsyncMock()
        mock_client.get_balance.return_value = 10000.0
        
        # Act
        result = await mock_client.get_balance()
        
        # Assert
        assert result == 10000.0
    
    @pytest.mark.unit
    def test_my_sync_function(self):
        """Test specific behavior"""
        # Arrange
        value = 5
        
        # Act
        result = value * 2
        
        # Assert
        assert result == 10
```

### Available Fixtures

From `conftest.py`:

- `test_db` - Test database with schema
- `test_user_id` - Test user ID (123456789)
- `test_user_data` - Test user with credentials
- `mock_bybit_client` - Mocked Bybit client
- `mock_hyperliquid_client` - Mocked HyperLiquid client
- `mock_telegram_update` - Mocked Telegram update
- `mock_telegram_context` - Mocked Telegram context
- `sample_signal_data` - Sample trading signal
- `sample_position_data` - Sample position
- `test_client` - FastAPI test client
- `auth_headers` - JWT auth headers

## Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Database Layer | 95%+ |
| Exchange Adapters | 90%+ |
| Services Layer | 90%+ |
| Core Infrastructure | 85%+ |
| WebApp API | 85%+ |
| Integration Tests | 75%+ |

## Debugging Tests

### Run with PDB

```bash
pytest tests/ --pdb
```

Drops into debugger on failure.

### Show Local Variables on Failure

```bash
pytest tests/ -l
```

### Increase Verbosity

```bash
pytest tests/ -vv
```

### Show Test Durations

```bash
pytest tests/ --durations=10
```

## Mocking Best Practices

### Mock External APIs

```python
@patch('exchanges.bybit.BybitExchange.place_order')
async def test_order_placement(mock_order):
    mock_order.return_value = {"retCode": 0}
    # ... test code
```

### Mock Database Calls

```python
@patch('db.get_user_config')
def test_user_config(mock_get_config):
    mock_get_config.return_value = {"balance": 10000}
    # ... test code
```

### Mock Async Functions

```python
mock_func = AsyncMock(return_value={"status": "ok"})
result = await mock_func()
```

## Common Issues

### Issue: Tests failing with "No event loop"

**Solution:** Add `@pytest.mark.asyncio` decorator to async tests.

### Issue: Database locked

**Solution:** Ensure proper cleanup with fixtures and context managers.

### Issue: Import errors

**Solution:** Run tests from project root: `pytest tests/`

### Issue: Fixtures not found

**Solution:** Check `conftest.py` is in tests directory.

## Performance Testing

### Run Only Fast Tests

```bash
pytest tests/ -m "not slow"
```

### Profile Test Execution

```bash
pytest tests/ --profile
```

## Resources

- [PyTest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

**Last Updated:** December 23, 2025  
**Test Suite Version:** 2.0.0  
**Total Tests:** 150+
