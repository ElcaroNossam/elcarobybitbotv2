"""
User Guide PDF Generator for Bybit Trading Bot
"""
import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Try to register a font with Cyrillic support
FONT_NAME = "Helvetica"
try:
    # Try DejaVu font (common on Linux)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont('DejaVuSans', path))
            FONT_NAME = "DejaVuSans"
            break
except Exception:
    pass


def generate_user_guide_pdf(lang: str = "en") -> BytesIO:
    """
    Generate a PDF user guide for the trading bot.
    Returns BytesIO buffer with PDF content.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName=FONT_NAME,
        fontSize=24,
        spaceAfter=12,
        textColor=colors.HexColor('#1a1a2e'),
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontName=FONT_NAME,
        fontSize=16,
        spaceAfter=8,
        spaceBefore=16,
        textColor=colors.HexColor('#16213e'),
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading2'],
        fontName=FONT_NAME,
        fontSize=13,
        spaceAfter=6,
        spaceBefore=10,
        textColor=colors.HexColor('#0f3460'),
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        spaceAfter=6,
        leading=14,
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        leftIndent=15,
        spaceAfter=4,
        leading=13,
    )
    
    tip_style = ParagraphStyle(
        'TipStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        leftIndent=10,
        rightIndent=10,
        spaceAfter=8,
        spaceBefore=8,
        backColor=colors.HexColor('#e8f4f8'),
        borderColor=colors.HexColor('#3498db'),
        borderWidth=1,
        borderPadding=8,
        leading=13,
    )
    
    warning_style = ParagraphStyle(
        'WarningStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        leftIndent=10,
        rightIndent=10,
        spaceAfter=8,
        spaceBefore=8,
        backColor=colors.HexColor('#fff3cd'),
        borderColor=colors.HexColor('#ffc107'),
        borderWidth=1,
        borderPadding=8,
        leading=13,
    )
    
    # Content based on language
    if lang == "ru":
        content = _get_russian_content()
    elif lang == "uk":
        content = _get_ukrainian_content()
    else:
        content = _get_english_content()
    
    # Build document
    story = []
    
    # Title
    story.append(Paragraph(content["title"], title_style))
    story.append(Spacer(1, 10*mm))
    
    # Introduction
    story.append(Paragraph(content["intro"], body_style))
    story.append(Spacer(1, 5*mm))
    
    # Quick Start
    story.append(Paragraph(content["quick_start_title"], heading_style))
    for step in content["quick_start_steps"]:
        story.append(Paragraph(f"• {step}", bullet_style))
    story.append(Spacer(1, 3*mm))
    
    # API Setup
    story.append(Paragraph(content["api_title"], heading_style))
    story.append(Paragraph(content["api_intro"], body_style))
    for step in content["api_steps"]:
        story.append(Paragraph(f"• {step}", bullet_style))
    story.append(Paragraph(content["api_warning"], warning_style))
    story.append(Spacer(1, 3*mm))
    
    # Strategies Section
    story.append(Paragraph(content["strategies_title"], heading_style))
    story.append(Paragraph(content["strategies_intro"], body_style))
    
    for strat in content["strategies"]:
        story.append(Paragraph(strat["name"], subheading_style))
        story.append(Paragraph(strat["description"], body_style))
        
        if strat.get("params"):
            story.append(Paragraph(content["params_label"], body_style))
            for param in strat["params"]:
                story.append(Paragraph(f"• {param}", bullet_style))
        
        if strat.get("tip"):
            story.append(Paragraph(f"💡 {strat['tip']}", tip_style))
        
        story.append(Spacer(1, 2*mm))
    
    # Trading Modes
    story.append(Paragraph(content["modes_title"], heading_style))
    story.append(Paragraph(content["modes_intro"], body_style))
    
    modes_data = content["modes_table"]
    modes_table = Table(modes_data, colWidths=[35*mm, 120*mm])
    modes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(modes_table)
    story.append(Spacer(1, 5*mm))
    
    # DCA Section
    story.append(Paragraph(content["dca_title"], heading_style))
    story.append(Paragraph(content["dca_description"], body_style))
    for item in content["dca_params"]:
        story.append(Paragraph(f"• {item}", bullet_style))
    story.append(Paragraph(content["dca_tip"], tip_style))
    story.append(Spacer(1, 3*mm))
    
    # Spot Trading Section
    story.append(Paragraph(content["spot_title"], heading_style))
    story.append(Paragraph(content["spot_intro"], body_style))
    
    for feature in content["spot_features"]:
        story.append(Paragraph(feature["name"], subheading_style))
        story.append(Paragraph(feature["description"], body_style))
        if feature.get("items"):
            for item in feature["items"]:
                story.append(Paragraph(f"• {item}", bullet_style))
        if feature.get("tip"):
            story.append(Paragraph(f"💡 {feature['tip']}", tip_style))
        story.append(Spacer(1, 2*mm))
    
    # Risk Management
    story.append(Paragraph(content["risk_title"], heading_style))
    for tip in content["risk_tips"]:
        story.append(Paragraph(f"• {tip}", bullet_style))
    story.append(Paragraph(content["risk_warning"], warning_style))
    story.append(Spacer(1, 3*mm))
    
    # Commands
    story.append(Paragraph(content["commands_title"], heading_style))
    cmd_data = content["commands_table"]
    cmd_table = Table(cmd_data, colWidths=[40*mm, 115*mm])
    cmd_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(cmd_table)
    story.append(Spacer(1, 5*mm))
    
    # Support
    story.append(Paragraph(content["support_title"], heading_style))
    story.append(Paragraph(content["support_text"], body_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def _get_english_content():
    return {
        "title": "Bybit Trading Bot - User Guide",
        "intro": "Welcome to the Bybit Trading Bot! This guide will help you set up and configure the bot for automated cryptocurrency futures trading.",
        
        "quick_start_title": "Quick Start",
        "quick_start_steps": [
            "Set up your Bybit API keys (Demo or Real account)",
            "Choose and enable strategies you want to use",
            "Configure entry size, stop-loss, and take-profit for each strategy",
            "Select trading mode (Demo/Real/Both) per strategy",
            "Start receiving and executing trading signals automatically",
        ],
        
        "api_title": "API Setup",
        "api_intro": "To use the bot, you need to create API keys on Bybit:",
        "api_steps": [
            "Go to Bybit.com → Account → API Management",
            "Create new API key with 'Contract Trading' permission",
            "For Demo: Use api-demo.bybit.com to create demo account first",
            "Copy API Key and Secret to the bot via /api command",
            "You can set up both Demo and Real API keys",
        ],
        "api_warning": "⚠️ NEVER share your API keys! The bot stores them securely but you should use IP restrictions on Bybit for extra security.",
        
        "strategies_title": "Trading Strategies",
        "strategies_intro": "The bot supports 5 different trading strategies. Each can be configured independently:",
        "params_label": "Parameters:",
        
        "strategies": [
            {
                "name": "📊 OI (Open Interest)",
                "description": "Trades based on significant changes in Open Interest. When large players enter positions, OI changes rapidly, signaling potential moves.",
                "params": [
                    "Entry %: Position size as % of balance",
                    "SL %: Stop-loss percentage",
                    "TP %: Take-profit percentage",
                    "Coins Group: ALL / TOP / VOLATILE",
                ],
                "tip": "Best for catching momentum moves. Use smaller position sizes due to higher volatility.",
            },
            {
                "name": "📈 RSI + Bollinger Bands",
                "description": "Combines RSI oversold/overbought levels with Bollinger Band touches for mean-reversion entries.",
                "params": [
                    "Entry %: Position size as % of balance",
                    "SL %: Stop-loss percentage",
                    "TP %: Take-profit percentage",
                ],
                "tip": "Works best in ranging markets. Consider disabling during strong trends.",
            },
            {
                "name": "🔮 Scryptomera",
                "description": "Follows signals from Scryptomera channel. Supports separate settings for Long and Short positions.",
                "params": [
                    "Direction: Long only / Short only / Both",
                    "Long Entry/SL/TP: Settings for long positions",
                    "Short Entry/SL/TP: Settings for short positions",
                ],
                "tip": "You can set different risk parameters for longs vs shorts based on market bias.",
            },
            {
                "name": "⚡ Scalper",
                "description": "High-frequency scalping strategy for quick profits on small moves. Uses tight stops and targets.",
                "params": [
                    "Entry %: Usually smaller (0.5-2%)",
                    "SL %: Tight stop-loss (0.5-1.5%)",
                    "TP %: Quick take-profit (1-3%)",
                ],
                "tip": "Requires low-latency execution. Best on high-volume pairs. Consider higher leverage.",
            },
            {
                "name": "🔥 Elcaro",
                "description": "Premium signal strategy with pre-calculated parameters. Uses signal-provided SL/TP levels.",
                "params": [
                    "Entry %: Position size (signal may override)",
                    "Other params: Usually taken from signal",
                ],
                "tip": "Trust the signal parameters. This strategy is optimized for the specific setup in each signal.",
            },
        ],
        
        "modes_title": "Trading Modes",
        "modes_intro": "Each strategy can operate in different modes:",
        "modes_table": [
            ["Mode", "Description"],
            ["Global", "Uses your global account trading mode setting"],
            ["Demo", "Trades only on Demo account (safe testing)"],
            ["Real", "Trades only on Real account (live money)"],
            ["Both", "Trades on both Demo and Real simultaneously"],
        ],
        
        "dca_title": "DCA (Dollar Cost Averaging)",
        "dca_description": "DCA allows adding to positions when price moves against you:",
        "dca_params": [
            "DCA Enabled: Toggle ON/OFF in DCA Settings",
            "Leg 1: First add at -X% (default 10%)",
            "Leg 2: Second add at -Y% (default 25%)",
        ],
        "dca_tip": "💡 DCA increases position size and risk. Use with caution and proper risk management. Disabled by default.",
        
        "spot_title": "Professional Spot Trading",
        "spot_intro": "The bot includes advanced spot trading features for long-term portfolio building with automated DCA strategies:",
        "spot_features": [
            {
                "name": "📁 Portfolio Presets",
                "description": "Pre-configured portfolio allocations for different investment strategies:",
                "items": [
                    "Blue Chips: BTC 50%, ETH 30%, BNB 10%, SOL 10%",
                    "DeFi: UNI, AAVE, MKR, LINK, SNX",
                    "Layer 2: MATIC, ARB, OP, IMX",
                    "Meme: DOGE, SHIB, PEPE, FLOKI",
                    "Gaming: AXS, SAND, MANA, GALA",
                    "AI & Web3: FET, RNDR, GRT, OCEAN",
                    "Custom: Choose your own coins",
                ],
                "tip": "Blue Chips is recommended for beginners - lower risk with established coins.",
            },
            {
                "name": "🎯 Smart DCA Strategies",
                "description": "Intelligent buying strategies that adapt to market conditions:",
                "items": [
                    "Fixed DCA: Buy same amount at regular intervals",
                    "Value Averaging: Buy more when price drops, less when rises",
                    "Fear & Greed: Buy 2x during extreme fear, 0.5x during greed",
                    "Dip Buying: Only buy when price drops 5%+ from 7-day high",
                ],
                "tip": "Fear & Greed strategy is great for accumulating during market panics!",
            },
            {
                "name": "🔄 Auto DCA",
                "description": "Automatic periodic buying based on your schedule:",
                "items": [
                    "Daily: Buy every 24 hours",
                    "Weekly: Buy every 7 days",
                    "Monthly: Buy every 30 days",
                    "Manual: Buy only when you click 'Buy Now'",
                ],
            },
            {
                "name": "🎯 Auto Take Profit",
                "description": "Automatically sell portions of holdings when targets are reached:",
                "items": [
                    "Level 1: At +20% gain, sell 25%",
                    "Level 2: At +50% gain, sell 25%",
                    "Level 3: At +100% gain, sell 25%",
                    "Level 4: At +200% gain, sell remaining 25%",
                ],
                "tip": "TP levels are customizable. This helps lock in profits automatically!",
            },
            {
                "name": "⚖️ Auto Rebalance",
                "description": "Get notified when your portfolio drifts from target allocation. Keeps your portfolio balanced according to your chosen preset.",
            },
            {
                "name": "📊 Analytics",
                "description": "Track your spot portfolio performance including total invested, current value, PnL, and Fear & Greed Index.",
            },
        ],
        
        "risk_title": "Risk Management Tips",
        "risk_tips": [
            "Start with Demo account to test strategies",
            "Never risk more than 1-2% per trade",
            "Use different position sizes for different strategies",
            "Monitor your positions regularly via /positions",
            "Set up Telegram notifications for trade alerts",
            "Review statistics weekly via /stats",
        ],
        "risk_warning": "⚠️ Trading involves significant risk. Past performance doesn't guarantee future results. Only trade with money you can afford to lose.",
        
        "commands_title": "Main Commands",
        "commands_table": [
            ["Command", "Description"],
            ["/start", "Start bot and show main menu"],
            ["/balance", "Check USDT balance"],
            ["/positions", "View open positions"],
            ["/orders", "View pending orders"],
            ["/stats", "Trading statistics"],
            ["/api", "Configure API keys"],
            ["/config", "Bot settings"],
            ["/strategies", "Strategy settings"],
            ["/language", "Change language"],
        ],
        
        "support_title": "Support",
        "support_text": "If you have questions or issues, contact the bot administrator. Happy trading! 🚀",
    }


def _get_russian_content():
    return {
        "title": "Bybit Trading Bot - Руководство",
        "intro": "Добро пожаловать в Bybit Trading Bot! Это руководство поможет вам настроить бота для автоматической торговли криптовалютными фьючерсами.",
        
        "quick_start_title": "Быстрый старт",
        "quick_start_steps": [
            "Настройте API ключи Bybit (Demo или Real аккаунт)",
            "Выберите и включите нужные стратегии",
            "Настройте размер входа, стоп-лосс и тейк-профит для каждой стратегии",
            "Выберите режим торговли (Demo/Real/Both) для каждой стратегии",
            "Начните автоматически получать и исполнять торговые сигналы",
        ],
        
        "api_title": "Настройка API",
        "api_intro": "Для работы бота нужно создать API ключи на Bybit:",
        "api_steps": [
            "Перейдите на Bybit.com → Аккаунт → API Management",
            "Создайте новый API ключ с правами 'Contract Trading'",
            "Для Demo: сначала создайте демо-аккаунт на api-demo.bybit.com",
            "Скопируйте API Key и Secret в бота через команду /api",
            "Можно настроить оба типа ключей: Demo и Real",
        ],
        "api_warning": "⚠️ НИКОГДА не передавайте свои API ключи! Бот хранит их безопасно, но используйте IP-ограничения на Bybit для дополнительной защиты.",
        
        "strategies_title": "Торговые стратегии",
        "strategies_intro": "Бот поддерживает 5 различных стратегий. Каждая настраивается независимо:",
        "params_label": "Параметры:",
        
        "strategies": [
            {
                "name": "📊 OI (Open Interest)",
                "description": "Торгует на основе значительных изменений открытого интереса. Когда крупные игроки входят в позиции, OI быстро меняется, сигнализируя о потенциальных движениях.",
                "params": [
                    "Entry %: Размер позиции в % от баланса",
                    "SL %: Стоп-лосс в процентах",
                    "TP %: Тейк-профит в процентах",
                    "Coins Group: ALL / TOP / VOLATILE",
                ],
                "tip": "Лучше всего для ловли импульсных движений. Используйте меньшие размеры позиций из-за высокой волатильности.",
            },
            {
                "name": "📈 RSI + Bollinger Bands",
                "description": "Комбинирует уровни перекупленности/перепроданности RSI с касаниями полос Боллинджера для входов на возврат к среднему.",
                "params": [
                    "Entry %: Размер позиции в % от баланса",
                    "SL %: Стоп-лосс в процентах",
                    "TP %: Тейк-профит в процентах",
                ],
                "tip": "Лучше работает на боковых рынках. Отключайте во время сильных трендов.",
            },
            {
                "name": "🔮 Scryptomera",
                "description": "Следует сигналам канала Scryptomera. Поддерживает отдельные настройки для Long и Short позиций.",
                "params": [
                    "Direction: Только Long / Только Short / Оба",
                    "Long Entry/SL/TP: Настройки для лонгов",
                    "Short Entry/SL/TP: Настройки для шортов",
                ],
                "tip": "Можно установить разные параметры риска для лонгов и шортов в зависимости от рыночного тренда.",
            },
            {
                "name": "⚡ Scalper",
                "description": "Высокочастотная скальпинг-стратегия для быстрой прибыли на малых движениях. Использует узкие стопы и цели.",
                "params": [
                    "Entry %: Обычно меньше (0.5-2%)",
                    "SL %: Узкий стоп-лосс (0.5-1.5%)",
                    "TP %: Быстрый тейк-профит (1-3%)",
                ],
                "tip": "Требует быстрого исполнения. Лучше на высоколиквидных парах. Можно использовать большее плечо.",
            },
            {
                "name": "🔥 Elcaro",
                "description": "Премиум стратегия с заранее рассчитанными параметрами. Использует уровни SL/TP из сигнала.",
                "params": [
                    "Entry %: Размер позиции (сигнал может переопределить)",
                    "Остальные параметры: Обычно берутся из сигнала",
                ],
                "tip": "Доверяйте параметрам сигнала. Эта стратегия оптимизирована под конкретный сетап каждого сигнала.",
            },
        ],
        
        "modes_title": "Режимы торговли",
        "modes_intro": "Каждая стратегия может работать в разных режимах:",
        "modes_table": [
            ["Режим", "Описание"],
            ["Global", "Использует глобальные настройки аккаунта"],
            ["Demo", "Торгует только на Demo (безопасное тестирование)"],
            ["Real", "Торгует только на Real (реальные деньги)"],
            ["Both", "Торгует на Demo и Real одновременно"],
        ],
        
        "dca_title": "DCA (Усреднение позиции)",
        "dca_description": "DCA позволяет добирать позицию когда цена идёт против вас:",
        "dca_params": [
            "DCA Enabled: Вкл/Выкл в настройках DCA",
            "Leg 1: Первый добор при -X% (по умолчанию 10%)",
            "Leg 2: Второй добор при -Y% (по умолчанию 25%)",
        ],
        "dca_tip": "💡 DCA увеличивает размер позиции и риск. Используйте осторожно с правильным управлением рисками. По умолчанию выключен.",
        
        "spot_title": "Профессиональный Spot Trading",
        "spot_intro": "Бот включает продвинутые функции спот-торговли для долгосрочного построения портфеля с автоматизированными DCA стратегиями:",
        "spot_features": [
            {
                "name": "📁 Портфельные пресеты",
                "description": "Готовые распределения портфеля для разных инвестиционных стратегий:",
                "items": [
                    "Blue Chips: BTC 50%, ETH 30%, BNB 10%, SOL 10%",
                    "DeFi: UNI, AAVE, MKR, LINK, SNX",
                    "Layer 2: MATIC, ARB, OP, IMX",
                    "Meme: DOGE, SHIB, PEPE, FLOKI",
                    "Gaming: AXS, SAND, MANA, GALA",
                    "AI & Web3: FET, RNDR, GRT, OCEAN",
                    "Custom: Выберите свои монеты",
                ],
                "tip": "Blue Chips рекомендуется для начинающих - меньший риск с проверенными монетами.",
            },
            {
                "name": "🎯 Умные DCA стратегии",
                "description": "Интеллектуальные стратегии покупки, адаптирующиеся к рыночным условиям:",
                "items": [
                    "Fixed DCA: Покупка одинаковой суммы через равные интервалы",
                    "Value Averaging: Покупать больше когда цена падает, меньше когда растёт",
                    "Fear & Greed: Покупка 2x при экстремальном страхе, 0.5x при жадности",
                    "Dip Buying: Покупка только при падении на 5%+ от 7-дневного максимума",
                ],
                "tip": "Стратегия Fear & Greed отлично подходит для накопления во время паники на рынке!",
            },
            {
                "name": "🔄 Авто DCA",
                "description": "Автоматическая периодическая покупка по вашему расписанию:",
                "items": [
                    "Daily: Покупка каждые 24 часа",
                    "Weekly: Покупка каждые 7 дней",
                    "Monthly: Покупка каждые 30 дней",
                    "Manual: Покупка только по кнопке 'Buy Now'",
                ],
            },
            {
                "name": "🎯 Авто Take Profit",
                "description": "Автоматическая продажа частей холдингов при достижении целей:",
                "items": [
                    "Уровень 1: При +20% прибыли, продать 25%",
                    "Уровень 2: При +50% прибыли, продать 25%",
                    "Уровень 3: При +100% прибыли, продать 25%",
                    "Уровень 4: При +200% прибыли, продать оставшиеся 25%",
                ],
                "tip": "Уровни TP настраиваются. Это помогает фиксировать прибыль автоматически!",
            },
            {
                "name": "⚖️ Авто Ребалансировка",
                "description": "Получайте уведомления когда ваш портфель отклоняется от целевого распределения. Поддерживает баланс портфеля согласно выбранному пресету.",
            },
            {
                "name": "📊 Аналитика",
                "description": "Отслеживайте эффективность спот-портфеля: всего инвестировано, текущая стоимость, PnL, и индекс Fear & Greed.",
            },
        ],
        
        "risk_title": "Управление рисками",
        "risk_tips": [
            "Начните с Demo аккаунта для тестирования стратегий",
            "Не рискуйте более 1-2% на сделку",
            "Используйте разные размеры позиций для разных стратегий",
            "Регулярно проверяйте позиции через /positions",
            "Настройте уведомления Telegram для оповещений о сделках",
            "Еженедельно просматривайте статистику через /stats",
        ],
        "risk_warning": "⚠️ Торговля связана со значительными рисками. Прошлые результаты не гарантируют будущих. Торгуйте только теми деньгами, которые готовы потерять.",
        
        "commands_title": "Основные команды",
        "commands_table": [
            ["Команда", "Описание"],
            ["/start", "Запуск бота и главное меню"],
            ["/balance", "Проверить баланс USDT"],
            ["/positions", "Открытые позиции"],
            ["/orders", "Отложенные ордера"],
            ["/stats", "Статистика торговли"],
            ["/api", "Настройка API ключей"],
            ["/config", "Настройки бота"],
            ["/strategies", "Настройки стратегий"],
            ["/language", "Сменить язык"],
        ],
        
        "support_title": "Поддержка",
        "support_text": "Если есть вопросы или проблемы, свяжитесь с администратором бота. Удачной торговли! 🚀",
    }


def _get_ukrainian_content():
    return {
        "title": "Bybit Trading Bot - Посібник",
        "intro": "Ласкаво просимо до Bybit Trading Bot! Цей посібник допоможе вам налаштувати бота для автоматичної торгівлі криптовалютними ф'ючерсами.",
        
        "quick_start_title": "Швидкий старт",
        "quick_start_steps": [
            "Налаштуйте API ключі Bybit (Demo або Real акаунт)",
            "Оберіть та увімкніть потрібні стратегії",
            "Налаштуйте розмір входу, стоп-лос та тейк-профіт для кожної стратегії",
            "Оберіть режим торгівлі (Demo/Real/Both) для кожної стратегії",
            "Почніть автоматично отримувати та виконувати торгові сигнали",
        ],
        
        "api_title": "Налаштування API",
        "api_intro": "Для роботи бота потрібно створити API ключі на Bybit:",
        "api_steps": [
            "Перейдіть на Bybit.com → Акаунт → API Management",
            "Створіть новий API ключ з правами 'Contract Trading'",
            "Для Demo: спочатку створіть демо-акаунт на api-demo.bybit.com",
            "Скопіюйте API Key і Secret в бота через команду /api",
            "Можна налаштувати обидва типи ключів: Demo і Real",
        ],
        "api_warning": "⚠️ НІКОЛИ не передавайте свої API ключі! Бот зберігає їх безпечно, але використовуйте IP-обмеження на Bybit для додаткового захисту.",
        
        "strategies_title": "Торгові стратегії",
        "strategies_intro": "Бот підтримує 5 різних стратегій. Кожна налаштовується незалежно:",
        "params_label": "Параметри:",
        
        "strategies": [
            {
                "name": "📊 OI (Open Interest)",
                "description": "Торгує на основі значних змін відкритого інтересу. Коли великі гравці входять в позиції, OI швидко змінюється, сигналізуючи про потенційні рухи.",
                "params": [
                    "Entry %: Розмір позиції в % від балансу",
                    "SL %: Стоп-лос в відсотках",
                    "TP %: Тейк-профіт в відсотках",
                    "Coins Group: ALL / TOP / VOLATILE",
                ],
                "tip": "Найкраще для ловлі імпульсних рухів. Використовуйте менші розміри позицій через високу волатильність.",
            },
            {
                "name": "📈 RSI + Bollinger Bands",
                "description": "Комбінує рівні перекупленості/перепроданості RSI з дотиками смуг Боллінджера для входів на повернення до середнього.",
                "params": [
                    "Entry %: Розмір позиції в % від балансу",
                    "SL %: Стоп-лос в відсотках",
                    "TP %: Тейк-профіт в відсотках",
                ],
                "tip": "Краще працює на бокових ринках. Вимикайте під час сильних трендів.",
            },
            {
                "name": "🔮 Scryptomera",
                "description": "Слідує сигналам каналу Scryptomera. Підтримує окремі налаштування для Long і Short позицій.",
                "params": [
                    "Direction: Тільки Long / Тільки Short / Обидва",
                    "Long Entry/SL/TP: Налаштування для лонгів",
                    "Short Entry/SL/TP: Налаштування для шортів",
                ],
                "tip": "Можна встановити різні параметри ризику для лонгів і шортів залежно від ринкового тренду.",
            },
            {
                "name": "⚡ Scalper",
                "description": "Високочастотна скальпінг-стратегія для швидкого прибутку на малих рухах. Використовує вузькі стопи та цілі.",
                "params": [
                    "Entry %: Зазвичай менше (0.5-2%)",
                    "SL %: Вузький стоп-лос (0.5-1.5%)",
                    "TP %: Швидкий тейк-профіт (1-3%)",
                ],
                "tip": "Потребує швидкого виконання. Краще на високоліквідних парах. Можна використовувати більше плече.",
            },
            {
                "name": "🔥 Elcaro",
                "description": "Преміум стратегія з заздалегідь розрахованими параметрами. Використовує рівні SL/TP з сигналу.",
                "params": [
                    "Entry %: Розмір позиції (сигнал може перевизначити)",
                    "Інші параметри: Зазвичай беруться з сигналу",
                ],
                "tip": "Довіряйте параметрам сигналу. Ця стратегія оптимізована під конкретний сетап кожного сигналу.",
            },
        ],
        
        "modes_title": "Режими торгівлі",
        "modes_intro": "Кожна стратегія може працювати в різних режимах:",
        "modes_table": [
            ["Режим", "Опис"],
            ["Global", "Використовує глобальні налаштування акаунта"],
            ["Demo", "Торгує тільки на Demo (безпечне тестування)"],
            ["Real", "Торгує тільки на Real (реальні гроші)"],
            ["Both", "Торгує на Demo і Real одночасно"],
        ],
        
        "dca_title": "DCA (Усереднення позиції)",
        "dca_description": "DCA дозволяє добирати позицію коли ціна йде проти вас:",
        "dca_params": [
            "DCA Enabled: Увімк/Вимк в налаштуваннях DCA",
            "Leg 1: Перший добір при -X% (за замовчуванням 10%)",
            "Leg 2: Другий добір при -Y% (за замовчуванням 25%)",
        ],
        "dca_tip": "💡 DCA збільшує розмір позиції та ризик. Використовуйте обережно з правильним управлінням ризиками. За замовчуванням вимкнено.",
        
        "spot_title": "Професійний Spot Trading",
        "spot_intro": "Бот включає продвинуті функції спот-торгівлі для довгострокового побудови портфеля з автоматизованими DCA стратегіями:",
        "spot_features": [
            {
                "name": "📁 Портфельні пресети",
                "description": "Готові розподіли портфеля для різних інвестиційних стратегій:",
                "items": [
                    "Blue Chips: BTC 50%, ETH 30%, BNB 10%, SOL 10%",
                    "DeFi: UNI, AAVE, MKR, LINK, SNX",
                    "Layer 2: MATIC, ARB, OP, IMX",
                    "Meme: DOGE, SHIB, PEPE, FLOKI",
                    "Gaming: AXS, SAND, MANA, GALA",
                    "AI & Web3: FET, RNDR, GRT, OCEAN",
                    "Custom: Оберіть свої монети",
                ],
                "tip": "Blue Chips рекомендується для початківців - менший ризик з перевіреними монетами.",
            },
            {
                "name": "🎯 Розумні DCA стратегії",
                "description": "Інтелектуальні стратегії купівлі, що адаптуються до ринкових умов:",
                "items": [
                    "Fixed DCA: Купівля однакової суми через рівні інтервали",
                    "Value Averaging: Купувати більше коли ціна падає, менше коли росте",
                    "Fear & Greed: Купівля 2x при екстремальному страху, 0.5x при жадібності",
                    "Dip Buying: Купівля тільки при падінні на 5%+ від 7-денного максимуму",
                ],
                "tip": "Стратегія Fear & Greed чудово підходить для накопичення під час паніки на ринку!",
            },
            {
                "name": "🔄 Авто DCA",
                "description": "Автоматична періодична купівля за вашим розкладом:",
                "items": [
                    "Daily: Купівля кожні 24 години",
                    "Weekly: Купівля кожні 7 днів",
                    "Monthly: Купівля кожні 30 днів",
                    "Manual: Купівля тільки по кнопці 'Buy Now'",
                ],
            },
            {
                "name": "🎯 Авто Take Profit",
                "description": "Автоматичний продаж частин холдингів при досягненні цілей:",
                "items": [
                    "Рівень 1: При +20% прибутку, продати 25%",
                    "Рівень 2: При +50% прибутку, продати 25%",
                    "Рівень 3: При +100% прибутку, продати 25%",
                    "Рівень 4: При +200% прибутку, продати решту 25%",
                ],
                "tip": "Рівні TP налаштовуються. Це допомагає фіксувати прибуток автоматично!",
            },
            {
                "name": "⚖️ Авто Ребалансування",
                "description": "Отримуйте сповіщення коли ваш портфель відхиляється від цільового розподілу. Підтримує баланс портфеля згідно обраного пресету.",
            },
            {
                "name": "📊 Аналітика",
                "description": "Відстежуйте ефективність спот-портфеля: всього інвестовано, поточна вартість, PnL, та індекс Fear & Greed.",
            },
        ],
        
        "risk_title": "Управління ризиками",
        "risk_tips": [
            "Почніть з Demo акаунта для тестування стратегій",
            "Не ризикуйте більше 1-2% на угоду",
            "Використовуйте різні розміри позицій для різних стратегій",
            "Регулярно перевіряйте позиції через /positions",
            "Налаштуйте сповіщення Telegram для оповіщень про угоди",
            "Щотижня переглядайте статистику через /stats",
        ],
        "risk_warning": "⚠️ Торгівля пов'язана зі значними ризиками. Минулі результати не гарантують майбутніх. Торгуйте тільки тими грошима, які готові втратити.",
        
        "commands_title": "Основні команди",
        "commands_table": [
            ["Команда", "Опис"],
            ["/start", "Запуск бота та головне меню"],
            ["/balance", "Перевірити баланс USDT"],
            ["/positions", "Відкриті позиції"],
            ["/orders", "Відкладені ордери"],
            ["/stats", "Статистика торгівлі"],
            ["/api", "Налаштування API ключів"],
            ["/config", "Налаштування бота"],
            ["/strategies", "Налаштування стратегій"],
            ["/language", "Змінити мову"],
        ],
        
        "support_title": "Підтримка",
        "support_text": "Якщо є питання або проблеми, зв'яжіться з адміністратором бота. Успішної торгівлі! 🚀",
    }


# Cache for generated PDFs (lang -> BytesIO)
_pdf_cache = {}

def get_user_guide_pdf(lang: str = "en") -> BytesIO:
    """Get cached PDF or generate new one."""
    # Normalize language
    if lang in ("ru",):
        lang = "ru"
    elif lang in ("uk", "ua"):
        lang = "uk"
    else:
        lang = "en"
    
    if lang not in _pdf_cache:
        _pdf_cache[lang] = generate_user_guide_pdf(lang)
    
    # Return a copy of the buffer
    buffer = BytesIO(_pdf_cache[lang].getvalue())
    return buffer
