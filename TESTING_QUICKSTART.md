# 🧪 Backend Testing - Quick Start Guide

## ⚡ Quick Commands

```bash
# 1. Verify tests work
./verify_tests.sh

# 2. Run all tests
./run_tests.sh all

# 3. Run with coverage report
./run_tests.sh coverage

# 4. View coverage
open htmlcov/index.html  # или xdg-open на Linux
```

## 📊 Test Statistics

- **Total Tests:** 173+
- **Test Files:** 9
- **Lines of Code:** 3,500+
- **Documentation:** 1,400+ lines
- **Status:** ✅ All systems operational

## 🎯 Run Specific Tests

```bash
./run_tests.sh database    # Database layer tests
./run_tests.sh exchanges   # Exchange adapter tests
./run_tests.sh services    # Services layer tests
./run_tests.sh webapp      # WebApp API tests
./run_tests.sh core        # Core infrastructure tests
```

## 📁 Test Structure

```
tests/
├── test_database.py         (25+ tests)
├── test_exchanges.py        (35+ tests)
├── test_services.py         (30+ tests)
├── test_exchange_router.py  (15+ tests)
├── test_core.py             (25+ tests)
├── test_webapp.py           (30+ tests)
├── test_integration.py      (15+ tests)
└── test_examples.py         (20+ tests)
```

## 📚 Documentation

- **Full Guide:** [tests/README.md](tests/README.md)
- **Summary:** [TESTING_SUMMARY.md](TESTING_SUMMARY.md)
- **Completion Report:** [TESTS_COMPLETED.md](TESTS_COMPLETED.md)
- **Examples:** [tests/test_examples.py](tests/test_examples.py)

## 🔧 Installation

If pytest is not installed:

```bash
pip install pytest pytest-asyncio pytest-cov
# or
./run_tests.sh install
```

## ✅ Verification

Run quick verification to ensure everything works:

```bash
./verify_tests.sh
```

Expected output:
```
✓ Python 3.10.12 detected
✓ pytest 9.0.2 installed
✓ 173 tests collected
✓ 4/4 quick tests passed
```

## 🎓 First Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify tests work
./verify_tests.sh

# 3. Run all tests
./run_tests.sh all

# 4. Check coverage
./run_tests.sh coverage
```

## 💡 Tips

- Use `./run_tests.sh fast` to skip slow tests
- Use `./run_tests.sh unit` for quick feedback
- Use `./run_tests.sh integration` for workflow tests
- Check `tests/README.md` for detailed documentation

## 🚨 Troubleshooting

**Tests not found?**
```bash
./run_tests.sh clean
./run_tests.sh all
```

**Import errors?**
```bash
# Run from project root
cd /path/to/bybit_demo
./run_tests.sh all
```

---

**Status:** ✅ Ready to use  
**Last Updated:** December 23, 2025
