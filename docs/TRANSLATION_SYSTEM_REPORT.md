# Translation System Analysis Report
## Enliko Trading Platform - Cross-Platform Localization Audit
**Date:** 5 February 2026  
**Platforms:** Telegram Bot, WebApp, iOS App, Android App

---

## Executive Summary

| Platform | Languages | Keys | Status | Issues |
|----------|-----------|------|--------|--------|
| **Bot** (reference) | 15 | 783 (EN) | ⚠️ | 14 languages missing 85 keys each |
| **iOS** | 15 | ~300+ | ✅ | Different key naming convention |
| **Android** | 15 | ~90 interface props | ✅ | Type-safe approach, minimal keys |
| **WebApp** | 15 | ~100 | ✅ | Separate JS file, basic keys |

### Key Findings

1. **85 translation keys missing** in 14 bot languages (all except EN and RU)
2. **Different key naming conventions** between platforms
3. **Language sync works correctly** via `/api/users/language` endpoint
4. **Database stores `lang` field** in PostgreSQL `users` table

---

## 1. Bot Translations Analysis

### File Structure
```
translations/
├── en.py    # 783 keys (REFERENCE)
├── ru.py    # 783 keys ✅ COMPLETE
├── uk.py    # 698 keys ❌ -85 missing
├── de.py    # 698 keys ❌ -85 missing
├── es.py    # 698 keys ❌ -85 missing
├── fr.py    # 698 keys ❌ -85 missing
├── it.py    # 698 keys ❌ -85 missing
├── ja.py    # 698 keys ❌ -85 missing
├── zh.py    # 698 keys ❌ -85 missing
├── ar.py    # 698 keys ❌ -85 missing
├── he.py    # 698 keys ❌ -85 missing
├── pl.py    # 698 keys ❌ -85 missing
├── cs.py    # 698 keys ❌ -85 missing
├── lt.py    # 698 keys ❌ -85 missing
└── sq.py    # 698 keys ❌ -85 missing
```

### Complete List of 85 Missing Keys

These keys exist in `en.py` and `ru.py` but are missing in all other 14 languages:

#### App Login (Unified Auth) - 5 keys
- `app_login_approved`
- `app_login_error`
- `app_login_expired`
- `app_login_prompt`
- `app_login_rejected`

#### UI Buttons - 15 keys
- `btn_check_payment`
- `btn_copy_address`
- `btn_new_currency`
- `btn_retry`
- `button_coins`
- `button_elcaro`
- `button_fibonacci`
- `button_indicators`
- `button_limit_only`
- `button_scalper`
- `button_scryptomera`
- `button_spot`
- `button_support`
- `button_toggle_oi`
- `button_toggle_rsi_bb`
- `button_update_tpsl`

#### Crypto Payments - 10 keys
- `checking_payment`
- `creating_payment`
- `crypto_creating_invoice`
- `crypto_payment_confirmed`
- `crypto_payment_confirming`
- `crypto_payment_error`
- `crypto_payment_expired`
- `crypto_payment_instructions`
- `crypto_payment_invoice`
- `crypto_payment_pending`
- `crypto_select_currency`

#### Spot Trading - 35 keys
- `spot_advanced_header`
- `spot_auto_rebalance`
- `spot_btn_buy`
- `spot_btn_holdings`
- `spot_btn_rebalance`
- `spot_btn_sell`
- `spot_btn_settings`
- `spot_dca_crash_boost`
- `spot_dca_dip_buy`
- `spot_dca_fear_greed`
- `spot_dca_fixed`
- `spot_dca_momentum`
- `spot_dca_rsi`
- `spot_dca_strategy_header`
- `spot_dca_strategy_select`
- `spot_dca_value_avg`
- `spot_limit_dca`
- `spot_performance_current`
- `spot_performance_header`
- `spot_performance_holdings`
- `spot_performance_invested`
- `spot_performance_pnl`
- `spot_portfolio_ai`
- `spot_portfolio_blue_chip`
- `spot_portfolio_btc`
- `spot_portfolio_custom`
- `spot_portfolio_defi`
- `spot_portfolio_eth_btc`
- `spot_portfolio_gaming`
- `spot_portfolio_header`
- `spot_portfolio_infra`
- `spot_portfolio_l1`
- `spot_portfolio_layer2`
- `spot_portfolio_meme`
- `spot_portfolio_rwa`
- `spot_portfolio_select`
- `spot_profit_lock`
- `spot_tp_aggressive`
- `spot_tp_balanced`
- `spot_tp_conservative`
- `spot_tp_header`
- `spot_tp_moonbag`
- `spot_tp_profile_select`
- `spot_trailing_tp`

#### Other - 10 keys
- `atr_disabled_restored`
- `basic_bybit_only`
- `global_settings_removed`
- `invalid_plan`
- `license_granted_notification`
- `main_menu_hint`
- `partial_tp_notification`
- `payment_creation_failed`
- `payment_error`

---

## 2. Key Naming Convention Comparison

### Bot (Python) - snake_case with underscores
```python
TEXTS = {
    'button_portfolio': '💼 Portfolio',
    'balance_title': '💰 *Account Balance*',
    'position_card': '...',
    'btn_back': '« Back',
}
```

### iOS (Swift) - snake_case in dictionary keys
```swift
static let englishTranslations: [String: String] = [
    "nav_portfolio": "Portfolio",
    "portfolio_title": "Portfolio",
    "positions_title": "Positions",
    "common_back": "Back",
]
```

### Android (Kotlin) - camelCase properties in interface
```kotlin
interface Strings {
    val portfolio: String        // Not "nav_portfolio"
    val positions: String        // Not "positions_title"
    val back: String            // Not "common_back"
}
```

### WebApp (JavaScript) - snake_case
```javascript
const translations = {
    en: {
        nav_home: "Home",
        nav_terminal: "Terminal",
        loading: "Loading...",
    }
}
```

### Key Differences Summary

| Category | Bot | iOS | Android | WebApp |
|----------|-----|-----|---------|--------|
| Format | snake_case | snake_case | camelCase | snake_case |
| Portfolio | `button_portfolio` | `nav_portfolio` | `portfolio` | `nav_home` |
| Back button | `btn_back`, `button_back` | `common_back` | `back` | N/A |
| Loading | `loader` | `common_loading` | `loading` | `loading` |

**Issue:** No shared translation key standard across platforms. Each platform has its own naming convention.

---

## 3. Language Preference Sync Architecture

### Database Schema
```sql
-- PostgreSQL users table
users (
    user_id BIGINT PRIMARY KEY,
    lang TEXT DEFAULT 'en',  -- Language preference
    ...
)
```

### Current User Distribution
```
ru: 4 users
en: 2 users
uk: 1 user
```

### API Endpoint: `/api/users/language`

**Location:** [webapp/api/users.py#L506-L541](webapp/api/users.py#L506-L541)

```python
@router.post("/language")
async def change_language(
    data: LanguageChange,
    user: dict = Depends(get_current_user)
):
    """Change user language across all platforms."""
    user_id = user["user_id"]
    
    valid_langs = ["en", "ru", "uk", "de", "fr", "es", "it", 
                   "pl", "zh", "ja", "ar", "he", "cs", "lt", "sq"]
    
    if data.language not in valid_langs:
        raise HTTPException(400, f"Invalid language")
    
    # Save to database
    db.set_user_field(user_id, "lang", data.language)
    
    # Sync to other platforms via sync_service
    await sync_service.sync_settings_change(...)
    
    return {"success": True, "language": data.language}
```

### Sync Flow

```
┌─────────────────┐         ┌─────────────────┐
│   iOS App       │────────▶│   POST          │
│ LocalizationMgr │         │ /users/language │
└─────────────────┘         └────────┬────────┘
                                     │
┌─────────────────┐                  │
│ Android App     │──────────────────┤
│ setLanguage()   │                  │
└─────────────────┘                  ▼
                            ┌─────────────────┐
┌─────────────────┐         │  PostgreSQL     │
│   WebApp        │────────▶│  users.lang     │
│ translations.js │         └────────┬────────┘
└─────────────────┘                  │
                                     ▼
┌─────────────────┐         ┌─────────────────┐
│  Telegram Bot   │◀────────│ sync_service    │
│  translations/  │         │ (WebSocket)     │
└─────────────────┘         └─────────────────┘
```

### iOS Language Loading
```swift
// AppState.swift - syncFromServer()
if let serverLang = serverSettings.lang,
   let appLanguage = AppLanguage(rawValue: serverLang) {
    if LocalizationManager.shared.currentLanguage != appLanguage {
        LocalizationManager.shared.setLanguageWithoutSync(appLanguage)
    }
}
```

### Android Language Loading
```kotlin
// EnlikoApi.kt
@PUT("/api/users/language")
suspend fun setLanguage(
    @Body request: Map<String, String>
): Response<Unit>
```

**Status:** ✅ Language sync is correctly implemented

---

## 4. Platform-Specific Issues

### iOS
- ✅ 15 languages supported
- ✅ RTL support for Arabic and Hebrew
- ✅ Syncs with server on login
- ✅ Uses `setLanguageWithoutSync()` to prevent sync loops
- ⚠️ Different key naming than bot (e.g., `nav_portfolio` vs `button_portfolio`)

### Android
- ✅ 15 languages supported
- ✅ RTL support via `isRtl` flag
- ✅ Type-safe approach with interface
- ⚠️ Minimal key set (~90 properties)
- ⚠️ camelCase naming differs from other platforms

### WebApp
- ✅ 15 languages supported
- ✅ Syncs via `/api/users/language`
- ⚠️ Small key set (~100 keys)
- ⚠️ Separate from bot translations

### Telegram Bot
- ✅ 15 languages supported (reference)
- ❌ 14 languages missing 85 keys
- ✅ Most comprehensive key set (783 keys)

---

## 5. Fix Plan

### Phase 1: Bot Translation Sync (PRIORITY: HIGH)
**Effort:** 2-3 hours

1. **Create sync script** to add missing 85 keys to all 14 languages
2. **Source:** Use English values as placeholders or machine-translate
3. **Files to update:** uk.py, de.py, es.py, fr.py, it.py, ja.py, zh.py, ar.py, he.py, pl.py, cs.py, lt.py, sq.py

### Phase 2: Key Naming Standardization (PRIORITY: MEDIUM)
**Effort:** 4-6 hours

1. **Create shared key map** between platforms
2. **Document naming convention** for each platform
3. **Build bridge functions** for cross-platform lookups

### Phase 3: Unified Translation Management (PRIORITY: LOW)
**Effort:** 1-2 days

1. **Create centralized translation source** (JSON or YAML)
2. **Generate platform-specific files** from source:
   - Python dict for bot
   - Swift dictionary for iOS
   - Kotlin object for Android
   - JavaScript object for WebApp
3. **Add CI check** for translation coverage

### Phase 4: Real-time Sync (OPTIONAL)
**Effort:** 3-4 hours

1. **Push translation updates** via WebSocket
2. **Hot reload** translations without app restart

---

## 6. Quick Fix Commands

### Add Missing Keys to Bot Translations

```python
# Run this script to add EN values as placeholders
missing_keys = [
    'app_login_approved', 'app_login_error', 'app_login_expired',
    'app_login_prompt', 'app_login_rejected', 'atr_disabled_restored',
    # ... (full list above)
]

# Read EN values and append to each language file
```

### Verify Sync is Working

```bash
# Test language change via API
curl -X POST https://enliko.com/api/users/language \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"language": "de"}'

# Check database
ssh server "psql -c \"SELECT lang FROM users WHERE user_id=123\""
```

---

## Appendix: Key Category Distribution (EN)

| Category | Count | Description |
|----------|-------|-------------|
| admin | 86 | Admin panel texts |
| spot | 65 | Spot trading |
| button | 44 | Button labels |
| stats | 43 | Statistics |
| btn | 39 | Short button labels |
| prompt | 29 | Input prompts |
| wallet | 24 | Wallet texts |
| error | 17 | Error messages |
| param | 14 | Parameter labels |
| payment | 14 | Payment texts |
| balance | 14 | Balance display |
| dca | 13 | DCA settings |
| api | 13 | API settings |
| grid | 12 | Grid trading |
| fibonacci | 10 | Fibonacci strategy |
| rsi | 10 | RSI strategy |
| elcaro | 10 | Elcaro strategy |

---

**Report generated by:** GitHub Copilot  
**Last updated:** 5 February 2026
