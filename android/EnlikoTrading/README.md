# Lyxen Trading - Android App

Full-featured Android trading application for Lyxen platform with real-time WebSocket updates, 15 language support, and cross-platform sync with iOS and Telegram bot.

## Features

- 📊 **Portfolio Dashboard** - Real-time balance, equity, PnL tracking
- 📈 **Trading** - One-tap Long/Short with configurable SL/TP
- 📡 **Signals** - Live trading signals with filtering
- 🔍 **Market Screener** - Crypto screener with volume and OI data
- 🤖 **AI Assistant** - AI-powered trading insights
- 📜 **Trade History** - Complete trade log with statistics
- ⚙️ **Settings** - Language, exchange, theme configuration
- 🔄 **Real-time Sync** - WebSocket updates for positions and prices
- 🌍 **15 Languages** - EN, RU, UK, DE, ES, FR, IT, JA, ZH, AR, HE, PL, CS, LT, SQ
- 🌙 **Dark/Light Theme** - Full Material 3 theming

## Tech Stack

- **Language**: Kotlin 2.1.0
- **UI**: Jetpack Compose + Material 3
- **Architecture**: MVVM + Clean Architecture
- **DI**: Hilt 2.53.1
- **Networking**: Retrofit 2.11.0 + OkHttp 4.12.0
- **WebSocket**: OkHttp WebSocket
- **Storage**: DataStore Preferences
- **Async**: Kotlin Coroutines + Flow
- **Images**: Coil 2.7.0

## Project Structure

```
app/src/main/java/io/enliko/trading/
├── LyxenApplication.kt          # Hilt Application
├── MainActivity.kt              # Entry point
├── data/
│   ├── api/
│   │   └── LyxenApi.kt          # Retrofit API interface
│   ├── models/
│   │   └── Models.kt            # Data classes
│   ├── repository/
│   │   └── PreferencesRepository.kt
│   └── websocket/
│       └── WebSocketService.kt  # Real-time updates
├── di/
│   └── NetworkModule.kt         # Hilt DI module
├── ui/
│   ├── components/
│   │   └── CommonComponents.kt
│   ├── navigation/
│   │   └── Navigation.kt
│   ├── screens/
│   │   ├── ai/
│   │   ├── auth/
│   │   ├── history/
│   │   ├── main/
│   │   ├── market/
│   │   ├── portfolio/
│   │   ├── settings/
│   │   ├── signals/
│   │   └── trading/
│   └── theme/
│       ├── Color.kt
│       ├── Theme.kt
│       └── Type.kt
└── util/
    └── Localization.kt          # 15-language support
```

## Building

### Prerequisites

- Android Studio Hedgehog (2023.1.1) or later
- JDK 17
- Android SDK 35

### Debug Build

```bash
cd android/LyxenTrading
./gradlew assembleDebug
```

APK will be at: `app/build/outputs/apk/debug/app-debug.apk`

### Release Build

1. Create keystore:
```bash
keytool -genkey -v -keystore enliko-release.keystore -alias enliko -keyalg RSA -keysize 2048 -validity 10000
```

2. Add to `local.properties`:
```properties
RELEASE_STORE_FILE=enliko-release.keystore
RELEASE_STORE_PASSWORD=your_password
RELEASE_KEY_ALIAS=enliko
RELEASE_KEY_PASSWORD=your_password
```

3. Build release:
```bash
./gradlew assembleRelease
# or for AAB (Play Store)
./gradlew bundleRelease
```

## Configuration

### API Endpoint

The API URL is configured in `app/build.gradle.kts`:

```kotlin
buildConfigField("String", "BASE_URL", "\"https://your-api-url.com/api\"")
```

For production, update the Cloudflare tunnel URL.

### WebSocket

WebSocket URL is in `WebSocketService.kt`:

```kotlin
private const val WS_URL = "wss://your-api-url.com/ws"
```

## Localization

To add translations, edit `util/Localization.kt`:

```kotlin
object Russian : Strings {
    override val portfolio = "Портфель"
    // ... add translations
}
```

## Cross-Platform Sync

The app syncs with iOS and Telegram bot via:

1. **REST API**: Settings, preferences, trades
2. **WebSocket**: Real-time positions, balance, signals
3. **Activity Log**: Tracked in `user_activity_log` table

## Permissions

- `INTERNET` - API and WebSocket communication

## License

Proprietary - Lyxen Trading Platform
