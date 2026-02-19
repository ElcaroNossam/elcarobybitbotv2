#!/usr/bin/env python3
"""
Android Localization: Add missing Strings properties and replace hardcoded text.
Adds new properties to Strings interface + all 15 language objects.
Replaces static `text = "X"` with `text = strings.propertyName` in screen files.
"""
import re, os

BASE = "/Users/elcarosam/project/elcarobybitbotv2/android/EnlikoTrading/app/src/main/java/io/enliko/trading"
LOC_FILE = os.path.join(BASE, "util/Localization.kt")
SCREENS_DIR = os.path.join(BASE, "ui/screens")

# ═══════════════════════════════════════
# NEW PROPERTIES TO ADD
# Format: (propertyName, EN, RU, UK)
# Other 12 langs get EN fallback
# ═══════════════════════════════════════
NEW_PROPS = [
    # Settings / Risk / Strategy
    ("notificationCategories", "Notification Categories", "Категории уведомлений", "Категорії сповіщень"),
    ("preferences", "Preferences", "Предпочтения", "Налаштування"),
    ("selectExchange", "Select Exchange", "Выбрать биржу", "Обрати біржу"),
    ("walletInfoAutoDiscovered", "Wallet Info (Auto-Discovered)", "Кошелёк (автообнаружен)", "Гаманець (автознайдений)"),
    ("securityWarning", "Never share your API keys or private keys with anyone. Enable only required permissions.", "Никогда не делитесь API ключами. Включайте только необходимые разрешения.", "Ніколи не діліться API ключами. Вмикайте лише необхідні дозволи."),
    ("account", "Account", "Аккаунт", "Акаунт"),
    ("developer", "Developer", "Разработчик", "Розробник"),
    ("appearance", "Appearance", "Оформление", "Оформлення"),
    ("unlockAllFeatures", "Unlock all features", "Разблокировать все функции", "Розблокувати всі функції"),
    ("appVersion", "Enliko v1.0.0", "Enliko v1.0.0", "Enliko v1.0.0"),
    ("tapToLink", "Tap to link", "Нажмите для привязки", "Натисніть для прив'язки"),
    ("orderAndFilters", "Order & Filters", "Ордер и фильтры", "Ордер та фільтри"),
    ("filterByDirection", "Filter signals by direction", "Фильтровать по направлению", "Фільтрувати за напрямком"),
    ("orderType", "Order Type", "Тип ордера", "Тип ордеру"),
    ("zeroUnlimited", "0 = unlimited", "0 = без лимита", "0 = без ліміту"),
    ("coinsGroup", "Coins Group", "Группа монет", "Група монет"),
    ("breakEvenDesc", "Move SL to entry when profit reaches trigger", "Перенос SL на вход при достижении прибыли", "Перенос SL на вхід при досягненні прибутку"),
    ("step1", "Step 1", "Шаг 1", "Крок 1"),
    ("step2", "Step 2", "Шаг 2", "Крок 2"),
    ("dcaDesc", "Add to position when loss reaches trigger %", "Добор при достижении % убытка", "Добір при досягненні % збитку"),
    ("useAtrForSlTp", "Use ATR for SL/TP", "Использовать ATR для SL/TP", "Використовувати ATR для SL/TP"),
    ("dynamicLevelsVolatility", "Dynamic levels based on volatility", "Динамические уровни на основе волатильности", "Динамічні рівні на основі волатильності"),
    ("atrPeriods", "ATR Periods", "Периоды ATR", "Періоди ATR"),
    ("atrMultiplier", "ATR Multiplier", "Множитель ATR", "Множник ATR"),
    ("enableDca", "Enable DCA", "Включить DCA", "Увімкнути DCA"),
    ("dcaDollarCostAvg", "Dollar Cost Average on drawdown", "Усреднение при просадке", "Усереднення при просідці"),
    ("dcaLevel1Trigger", "DCA Level 1 Trigger", "DCA Уровень 1", "DCA Рівень 1"),
    ("dcaLevel2Trigger", "DCA Level 2 Trigger", "DCA Уровень 2", "DCA Рівень 2"),
    ("riskRewardAnalysis", "Risk/Reward Analysis", "Анализ риск/прибыль", "Аналіз ризик/прибуток"),
    ("rrRatio", "R:R Ratio", "Соотношение R:R", "Співвідношення R:R"),
    ("minWinRate", "Min Win Rate", "Мин. процент побед", "Мін. відсоток перемог"),
    ("currentLeverage", "Current Leverage", "Текущее плечо", "Поточне плече"),
    ("adjustLeverage", "Adjust Leverage", "Настроить плечо", "Налаштувати плече"),
    ("quickSelect", "Quick Select", "Быстрый выбор", "Швидкий вибір"),
    ("notConfigured", "Not Configured", "Не настроено", "Не налаштовано"),
    ("tradingMode", "Trading Mode", "Режим торговли", "Режим торгівлі"),
    ("networkSettings", "Network Settings", "Настройки сети", "Налаштування мережі"),
    ("testnetMode", "Testnet Mode", "Режим тестовой сети", "Режим тестової мережі"),
    ("useTestnet", "Use testnet for testing", "Тестовая сеть для проверки", "Тестова мережа для перевірки"),
    
    # Exchange features
    ("featureDemoReal", "Demo & Real accounts", "Демо и реал аккаунты", "Демо та реал акаунти"),
    ("featureLeverage100", "Up to 100x leverage", "Плечо до 100x", "Плече до 100x"),
    ("featureSpotFutures", "Spot & Futures trading", "Спот и фьючерсы", "Спот та ф'ючерси"),
    ("featureLowFees", "Low trading fees", "Низкие комиссии", "Низькі комісії"),
    ("featureDecentralized", "Decentralized trading", "Децентрализованная торговля", "Децентралізована торгівля"),
    ("featureNonCustodial", "Non-custodial", "Без хранения средств", "Без зберігання коштів"),
    ("featureLeverage50", "Up to 50x leverage", "Плечо до 50x", "Плече до 50x"),
    ("featureNoKyc", "No KYC required", "Без KYC", "Без KYC"),
    
    # HyperLiquid
    ("connectedWallet", "Connected Wallet", "Подключённый кошелёк", "Підключений гаманець"),
    ("topPerformingVaults", "Top Performing Vaults", "Лучшие хранилища", "Найкращі сховища"),
    ("totalPoints", "Total Points", "Всего очков", "Всього очків"),
    ("pointsBreakdown", "Points Breakdown", "Разбивка очков", "Розбивка очків"),
    
    # Trading
    ("symbol", "Symbol", "Символ", "Символ"),
    ("amount", "Amount", "Сумма", "Сума"),
    ("limitPrice", "Limit Price", "Лимитная цена", "Лімітна ціна"),
    ("tpSlLabel", "Take Profit / Stop Loss", "Тейк-профит / Стоп-лосс", "Тейк-профіт / Стоп-лосс"),
    ("quickPresets", "Quick presets", "Быстрые пресеты", "Швидкі пресети"),
    ("orderSummary", "Order Summary", "Итого по ордеру", "Підсумок ордеру"),
    ("confirmOrder", "Confirm Order", "Подтвердить ордер", "Підтвердити ордер"),
    ("orderSettings", "Order Settings", "Настройки ордера", "Налаштування ордеру"),
    ("quickActions", "Quick Actions", "Быстрые действия", "Швидкі дії"),
    
    # Portfolio / Positions
    ("noOpenPositions", "No Open Positions", "Нет открытых позиций", "Немає відкритих позицій"),
    ("positionsWillAppear", "Your open positions will appear here", "Ваши позиции появятся здесь", "Ваші позиції з'являться тут"),
    ("totalPnl", "Total PnL", "Общий PnL", "Загальний PnL"),
    ("pnlChartTitle", "PnL Chart", "График PnL", "Графік PnL"),
    ("performanceMetrics", "Performance Metrics", "Показатели", "Показники"),
    ("winLossDistribution", "Win/Loss Distribution", "Распределение побед/проигрышей", "Розподіл виграшів/програшів"),
    ("strategyBreakdown", "Strategy Breakdown", "По стратегиям", "По стратегіям"),
    ("topSymbols", "Top Symbols", "Топ символы", "Топ символи"),
    ("strategiesOverview", "Strategies Overview", "Обзор стратегий", "Огляд стратегій"),
    ("recentTrades", "Recent Trades", "Последние сделки", "Останні угоди"),
    ("totalFunding", "Total Funding", "Итого фандинг", "Всього фандинг"),
    ("currentPrice", "Current Price", "Текущая цена", "Поточна ціна"),
    ("lastPrice", "Last Price", "Последняя цена", "Остання ціна"),
    ("spread", "Spread", "Спред", "Спред"),
    ("markPrice", "Mark Price", "Цена маркировки", "Ціна маркування"),
    ("orderBook", "Order Book", "Книга ордеров", "Книга ордерів"),
    
    # Spot
    ("noOpenOrders", "No open orders", "Нет открытых ордеров", "Немає відкритих ордерів"),
    ("totalSpotValue", "Total Spot Value", "Спот баланс", "Спот баланс"),
    ("fearAndGreed", "Fear & Greed", "Страх и жадность", "Страх та жадність"),
    ("newsComingSoon", "News Coming Soon", "Новости скоро", "Новини скоро"),
    ("hideSmall", "Hide small", "Скрыть мелкие", "Сховати дрібні"),
    
    # Wallet
    ("connectedAddress", "Connected Address", "Подключённый адрес", "Підключена адреса"),
    
    # Stats
    ("quickStats", "Quick Stats", "Краткая статистика", "Коротка статистика"),
    
    # Misc
    ("waitingForConfirmation", "Waiting for confirmation...", "Ожидание подтверждения...", "Очікування підтвердження..."),
    ("longLabel", "LONG", "LONG", "LONG"),
    ("shortLabel", "SHORT", "SHORT", "SHORT"),
    ("copyTradingRisk", "⚠️ Copy trading involves risk. Past performance doesn't guarantee future results.", "⚠️ Копи-трейдинг связан с рисками. Прошлые результаты не гарантируют будущих.", "⚠️ Копі-трейдінг пов'язаний з ризиками. Минулі результати не гарантують майбутніх."),
    
    # Auth / Telegram
    ("addEmailLogin", "Add email login to your account for web and mobile access", "Добавьте email для входа через веб и мобильное приложение", "Додайте email для входу через веб та мобільний додаток"),
    ("linkEmailAccount", "Link Email Account", "Привязать Email", "Прив'язати Email"),
    ("loginViaTelegram", "Login via Telegram", "Войти через Telegram", "Увійти через Telegram"),
    ("enterTelegramUsername", "Enter your Telegram @username", "Введите @username в Telegram", "Введіть @username в Telegram"),
    ("openEnlikoBotInTelegram", "Open @EnlikoBot in Telegram\\nand approve the login request", "Откройте @EnlikoBot в Telegram\\nи подтвердите вход", "Відкрийте @EnlikoBot в Telegram\\nта підтвердіть вхід"),
    ("mustStartBotFirst", "You must have started @EnlikoBot first", "Сначала запустите @EnlikoBot", "Спочатку запустіть @EnlikoBot"),

    # Market orders desc
    ("marketOrdersDesc", "Market orders execute immediately at current price. Limit orders are placed with an offset for better entry.", "Рыночные ордера исполняются мгновенно. Лимитные размещаются со смещением.", "Ринкові ордери виконуються миттєво. Лімітні розміщуються зі зміщенням."),
    ("dcaAddsDesc", "DCA adds to your position when price moves against you by the specified percentage.", "DCA добирает позицию при движении цены против вас.", "DCA добирає позицію при русі ціни проти вас."),
    ("atrTrailingDesc", "ATR trailing stop adjusts your stop-loss based on market volatility for optimal risk management.", "ATR трейлинг стоп корректирует ваш стоп-лосс на основе волатильности.", "ATR трейлінг стоп коригує ваш стоп-лосс на основі волатильності."),
    ("exchangeEnableDesc", "Enable or disable trading on specific exchanges. Exchanges must be configured in API Keys first.", "Включить/выключить торговлю на конкретных биржах. Сначала настройте API ключи.", "Увімкнути/вимкнути торгівлю на конкретних біржах. Спочатку налаштуйте API ключі."),
    ("alertCreateDesc", "Create price alerts to get notified when your target is reached", "Создайте алерты цены для уведомления при достижении цели", "Створіть алерти ціни для сповіщення при досягненні цілі"),
    ("condition", "Condition", "Условие", "Умова"),
    ("targetPrice", "Target Price", "Целевая цена", "Цільова ціна"),
    ("distance", "Distance", "Расстояние", "Відстань"),
    ("tp", "TP", "TP", "TP"),
    ("sl", "SL", "SL", "SL"),
    ("qty", "Qty", "Кол-во", "Кільк."),
    ("total", "Total", "Итого", "Всього"),
    ("coin", "Coin", "Монета", "Монета"),
]

# ═══════════════════════════════════════
# REPLACEMENT MAP: "Hardcoded" → (existingProperty OR newProperty)
# Maps the full `text = "X"` to `text = strings.Y`
# ═══════════════════════════════════════
REPLACEMENTS = {
    # Settings screens
    '"Notification Categories"': 'strings.notificationCategories',
    '"Preferences"': 'strings.preferences',
    '"Select Exchange"': 'strings.selectExchange',
    '"Account Type"': 'strings.accountType',
    '"Wallet Info (Auto-Discovered)"': 'strings.walletInfoAutoDiscovered',
    '"Never share your API keys or private keys with anyone. Enable only required permissions."': 'strings.securityWarning',
    '"Account"': 'strings.account',
    '"Trading"': 'strings.trading',
    '"Developer"': 'strings.developer',
    '"Appearance"': 'strings.appearance',
    '"Unlock all features"': 'strings.unlockAllFeatures',
    '"Enliko v1.0.0"': 'strings.appVersion',
    '"Tap to link"': 'strings.tapToLink',
    '"Not verified"': 'strings.notVerified',
    '"Order & Filters"': 'strings.orderAndFilters',
    '"Filter signals by direction"': 'strings.filterByDirection',
    '"Order Type"': 'strings.orderType',
    '"0 = unlimited"': 'strings.zeroUnlimited',
    '"Coins Group"': 'strings.coinsGroup',
    '"Move SL to entry when profit reaches trigger"': 'strings.breakEvenDesc',
    '"Step 1"': 'strings.step1',
    '"Step 2"': 'strings.step2',
    '"Add to position when loss reaches trigger %"': 'strings.dcaDesc',
    '"Use ATR for SL/TP"': 'strings.useAtrForSlTp',
    '"Dynamic levels based on volatility"': 'strings.dynamicLevelsVolatility',
    '"ATR Periods"': 'strings.atrPeriods',
    '"ATR Multiplier"': 'strings.atrMultiplier',
    '"Enable DCA"': 'strings.enableDca',
    '"Dollar Cost Average on drawdown"': 'strings.dcaDollarCostAvg',
    '"DCA Level 1 Trigger"': 'strings.dcaLevel1Trigger',
    '"DCA Level 2 Trigger"': 'strings.dcaLevel2Trigger',
    '"Risk/Reward Analysis"': 'strings.riskRewardAnalysis',
    '"R:R Ratio"': 'strings.rrRatio',
    '"Min Win Rate"': 'strings.minWinRate',
    '"Current Leverage"': 'strings.currentLeverage',
    '"Adjust Leverage"': 'strings.adjustLeverage',
    '"Quick Select"': 'strings.quickSelect',
    '"Not Configured"': 'strings.notConfigured',
    '"Trading Mode"': 'strings.tradingMode',
    '"Network Settings"': 'strings.networkSettings',
    '"Testnet Mode"': 'strings.testnetMode',
    '"Use testnet for testing"': 'strings.useTestnet',
    
    # Exchange features
    '"Demo & Real accounts"': 'strings.featureDemoReal',
    '"Up to 100x leverage"': 'strings.featureLeverage100',
    '"Spot & Futures trading"': 'strings.featureSpotFutures',
    '"Low trading fees"': 'strings.featureLowFees',
    '"Decentralized trading"': 'strings.featureDecentralized',
    '"Non-custodial"': 'strings.featureNonCustodial',
    '"Up to 50x leverage"': 'strings.featureLeverage50',
    '"No KYC required"': 'strings.featureNoKyc',
    
    # HyperLiquid
    '"Connected Wallet"': 'strings.connectedWallet',
    '"Top Performing Vaults"': 'strings.topPerformingVaults',
    '"Total Points"': 'strings.totalPoints',
    '"Points Breakdown"': 'strings.pointsBreakdown',
    
    # Trading
    '"Symbol"': 'strings.symbol',
    '"Amount"': 'strings.amount',
    '"Limit Price"': 'strings.limitPrice',
    '"Take Profit / Stop Loss"': 'strings.tpSlLabel',
    '"Quick presets"': 'strings.quickPresets',
    '"Order Summary"': 'strings.orderSummary',
    '"Confirm Order"': 'strings.confirmOrder',
    '"Order Settings"': 'strings.orderSettings',
    '"Leverage"': 'strings.leverage',
    '"Take Profit"': 'strings.takeProfit',
    '"Stop Loss"': 'strings.stopLoss',
    '"Buy"': 'strings.buy',
    '"Sell"': 'strings.sell',
    '"LONG"': 'strings.longLabel',
    '"SHORT"': 'strings.shortLabel',
    '"Cancel"': 'strings.cancel',
    '"Entry"': 'strings.entry',
    '"Price"': 'strings.price',
    
    # Portfolio / Positions / History
    '"Quick Actions"': 'strings.quickActions',
    '"No Open Positions"': 'strings.noOpenPositions',
    '"Your open positions will appear here"': 'strings.positionsWillAppear',
    '"Total PnL"': 'strings.totalPnl',
    '"PnL Chart"': 'strings.pnlChartTitle',
    '"Performance Metrics"': 'strings.performanceMetrics',
    '"Win/Loss Distribution"': 'strings.winLossDistribution',
    '"Strategy Breakdown"': 'strings.strategyBreakdown',
    '"Top Symbols"': 'strings.topSymbols',
    '"Strategies Overview"': 'strings.strategiesOverview',
    '"Recent Trades"': 'strings.recentTrades',
    '"Total Funding"': 'strings.totalFunding',
    '"Recent Activity"': 'strings.recentActivity',
    '"Total Balance"': 'strings.totalBalance',
    '"Current Price"': 'strings.currentPrice',
    '"Last Price"': 'strings.lastPrice',
    '"Spread"': 'strings.spread',
    '"Mark Price"': 'strings.markPrice',
    '"Order Book"': 'strings.orderBook',
    '"Assets"': 'strings.assets',
    '"Quick Stats"': 'strings.quickStats',
    
    # Spot
    '"No open orders"': 'strings.noOpenOrders',
    '"Total Spot Value"': 'strings.totalSpotValue',
    '"Fear & Greed"': 'strings.fearAndGreed',
    '"News Coming Soon"': 'strings.newsComingSoon',
    '"Hide small"': 'strings.hideSmall',
    '"Wallet"': 'strings.wallet',
    '"Total"': 'strings.total',
    '"TP"': 'strings.tp',
    '"SL"': 'strings.sl',
    '"Qty"': 'strings.qty',
    '"Coin"': 'strings.coin',
    
    # Longer descriptions
    '"Market orders execute immediately at current price. Limit orders are placed with an offset for better entry."': 'strings.marketOrdersDesc',
    '"DCA adds to your position when price moves against you by the specified percentage."': 'strings.dcaAddsDesc',
    '"ATR trailing stop adjusts your stop-loss based on market volatility for optimal risk management."': 'strings.atrTrailingDesc',
    '"Enable or disable trading on specific exchanges. Exchanges must be configured in API Keys first."': 'strings.exchangeEnableDesc',
    '"Create price alerts to get notified when your target is reached"': 'strings.alertCreateDesc',
    '"Condition"': 'strings.condition',
    '"Target Price"': 'strings.targetPrice',
    '"Distance"': 'strings.distance',
    '"Connected Address"': 'strings.connectedAddress',
    '"Waiting for confirmation..."': 'strings.waitingForConfirmation',
    
    # Auth
    '"Add email login to your account for web and mobile access"': 'strings.addEmailLogin',
    '"Link Email Account"': 'strings.linkEmailAccount',
    '"Login via Telegram"': 'strings.loginViaTelegram',
    '"Enter your Telegram @username"': 'strings.enterTelegramUsername',
    '"You must have started @EnlikoBot first"': 'strings.mustStartBotFirst',
}

# Additional replacements that use FeatureRow() pattern:
FEATURE_ROW_REPLACEMENTS = {
    'text = "Demo & Real accounts"': 'text = strings.featureDemoReal',
    'text = "Up to 100x leverage"': 'text = strings.featureLeverage100',
    'text = "Spot & Futures trading"': 'text = strings.featureSpotFutures',
    'text = "Low trading fees"': 'text = strings.featureLowFees',
    'text = "Decentralized trading"': 'text = strings.featureDecentralized',
    'text = "Non-custodial"': 'text = strings.featureNonCustodial',
    'text = "Up to 50x leverage"': 'text = strings.featureLeverage50',
    'text = "No KYC required"': 'text = strings.featureNoKyc',
}


def inject_interface_props(content):
    """Add new properties to the Strings interface."""
    # Find position before the operator fun get() line
    marker = "    /**\n     * Operator to access strings by key"
    if marker not in content:
        marker = "    operator fun get(key: String)"
    
    new_lines = "\n    // === GENERATED: Additional localized properties ===\n"
    for prop_name, en, ru, uk in NEW_PROPS:
        new_lines += f"    val {prop_name}: String\n"
    new_lines += "\n"
    
    content = content.replace(marker, new_lines + marker)
    return content


def inject_object_props(content, obj_name, obj_line, values_map):
    """Add override val properties to a language object, before its closing brace."""
    lines = content.split('\n')
    
    # Find the closing brace of this object (the next `}` at 4-space indent after obj_line)
    # Actually we need to find the `}` right before the next `object` or before `object Localization`
    insert_idx = None
    brace_depth = 0
    in_object = False
    for i in range(obj_line - 1, len(lines)):
        line = lines[i]
        if f'object {obj_name}' in line:
            in_object = True
            brace_depth = 0
        if in_object:
            brace_depth += line.count('{') - line.count('}')
            if brace_depth == 0 and in_object and '{' in lines[obj_line - 1]:
                insert_idx = i
                break
    
    if insert_idx is None:
        # Fallback: find the closing brace by looking for `    }` followed by empty/object line
        for i in range(obj_line, len(lines)):
            if lines[i].strip() == '}' and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line == '' or next_line.startswith('object ') or next_line.startswith('}'):
                    insert_idx = i
                    break
    
    if insert_idx is None:
        print(f"  WARN: Could not find closing brace for {obj_name}")
        return content
    
    # Build new lines
    new_lines = []
    new_lines.append("        ")
    new_lines.append("        // === GENERATED: Additional localized properties ===")
    for prop_name, value in values_map:
        escaped = value.replace('"', '\\"')
        new_lines.append(f'        override val {prop_name} = "{escaped}"')
    
    # Insert before the closing brace
    for j, nl in enumerate(new_lines):
        lines.insert(insert_idx + j, nl)
    
    return '\n'.join(lines)


def replace_in_screens(directory):
    """Replace hardcoded text = "X" with text = strings.Y in all .kt screen files."""
    total = 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            if not f.endswith('.kt'):
                continue
            filepath = os.path.join(root, f)
            with open(filepath, 'r') as fh:
                content = fh.read()
            
            original = content
            count = 0
            
            # Check if file has `val strings = LocalStrings.current` or similar
            has_strings = 'strings' in content and 'LocalStrings' in content
            
            # Replace each pattern
            for old_str, new_str in REPLACEMENTS.items():
                pattern = f'text = {old_str}'
                replacement = f'text = {new_str}'
                
                if pattern in content:
                    # Only replace exact text = "X" patterns (not inside interpolation)
                    occurrences = content.count(pattern)
                    content = content.replace(pattern, replacement)
                    count += occurrences
            
            # Also handle FeatureRow patterns
            for old_str, new_str in FEATURE_ROW_REPLACEMENTS.items():
                if old_str in content:
                    occurrences = content.count(old_str)
                    content = content.replace(old_str, new_str)
                    count += occurrences
            
            if count > 0:
                # Ensure file has `val strings = LocalStrings.current`
                if not has_strings:
                    # Add strings variable at the top of the first @Composable function
                    # Find pattern: `@Composable\nfun ScreenName(`
                    composable_match = re.search(r'(@Composable\s*\nfun \w+\([^)]*\)\s*\{)', content)
                    if composable_match:
                        insert_after = composable_match.group(1)
                        content = content.replace(
                            insert_after,
                            insert_after + '\n    val strings = LocalStrings.current',
                            1
                        )
                        print(f"  + Added `val strings = LocalStrings.current` to {f}")
                
                with open(filepath, 'w') as fh:
                    fh.write(content)
                print(f"  OK: {f} — {count} replacements")
                total += count
    
    return total


def main():
    print("=== Android Localization Script ===\n")
    
    # Read file
    with open(LOC_FILE, 'r') as f:
        content = f.read()
    
    # 1. Inject interface properties
    print("1. Adding interface properties...")
    content = inject_interface_props(content)
    
    # 2. Find all language object positions (re-scan after injection)
    LANG_OBJECTS = [
        ("English", "EN"),
        ("Russian", "RU"),
        ("Ukrainian", "UK"),
        ("German", "DE"),
        ("Spanish", "ES"),
        ("French", "FR"),
        ("Italian", "IT"),
        ("Japanese", "JA"),
        ("Chinese", "ZH"),
        ("Arabic", "AR"),
        ("Hebrew", "HE"),
        ("Polish", "PL"),
        ("Czech", "CS"),
        ("Lithuanian", "LT"),
        ("Albanian", "SQ"),
    ]
    
    print("2. Adding properties to language objects...")
    
    for lang_name, lang_code in LANG_OBJECTS:
        # Build values for this language
        values = []
        for prop_name, en, ru, uk in NEW_PROPS:
            if lang_code == "EN":
                values.append((prop_name, en))
            elif lang_code == "RU":
                values.append((prop_name, ru))
            elif lang_code == "UK":
                values.append((prop_name, uk))
            else:
                values.append((prop_name, en))  # English fallback
        
        # Find object line
        pattern = f'object {lang_name} : Strings {{'
        lines = content.split('\n')
        obj_line = None
        for i, line in enumerate(lines):
            if pattern in line:
                obj_line = i + 1  # 1-indexed
                break
        
        if obj_line:
            content = inject_object_props(content, lang_name, obj_line, values)
            print(f"  OK: {lang_name} ({lang_code}) — {len(values)} properties")
        else:
            print(f"  WARN: Could not find object {lang_name}")
    
    # Write updated Localization.kt
    with open(LOC_FILE, 'w') as f:
        f.write(content)
    print(f"\n  Written: {LOC_FILE}")
    
    # 3. Replace hardcoded strings in screen files
    print("\n3. Replacing hardcoded strings in screens...")
    total = replace_in_screens(SCREENS_DIR)
    print(f"\n  Total replacements: {total}")
    
    print("\n=== Done! ===")


if __name__ == '__main__':
    main()
