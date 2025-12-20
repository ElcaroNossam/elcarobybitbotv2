"""
Minimal Telegram bot that responds to /start and shows the chat id.

This bot does NOT need Django models; it's only used so that users can
discover their chat id and paste it into the alert form on the site.

Run from the project root:

    TELEGRAM_BOT_TOKEN=... python scripts/telegram_bot.py
"""

import asyncio
import os
import signal
import sys

# Fix for systemd event loop issues
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    # nest_asyncio not installed, will use manual event loop handling
    pass

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - show chat ID and website link."""
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return
    
    # Create inline keyboard with website link
    keyboard = [
        [InlineKeyboardButton("🌐 Открыть скринер", url="https://elcaro.online")],
        [InlineKeyboardButton("⚙️ Настроить алерты", url="https://elcaro.online/alerts/")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        f"👋 Привет, {update.effective_user.first_name or ''}!\n\n"
        f"🆔 Твой Telegram chat_id: <code>{chat_id}</code>\n\n"
        "📋 <b>Инструкция:</b>\n"
        "1️⃣ Скопируй chat_id выше\n"
        "2️⃣ Нажми кнопку <b>\"Настроить алерты\"</b> ниже\n"
        "3️⃣ Вставь chat_id в форму создания алерта\n"
        "4️⃣ Выбери метрику и установи порог\n\n"
        "✅ Теперь ты будешь получать уведомления, когда условия сработают!\n\n"
        "💡 <b>Как использовать свой токен бота:</b>\n"
        "Если у тебя есть свой бот, укажи его токен в поле <b>\"Telegram Bot Token\"</b> "
        "при создании алерта. Если поле пустое, используется дефолтный бот."
    )
    await update.message.reply_html(text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - show available commands."""
    text = (
        "📚 <b>Доступные команды:</b>\n\n"
        "/start - Показать chat_id и инструкцию\n"
        "/help - Показать это сообщение\n"
        "/chatid - Показать только chat_id\n"
        "/website - Ссылка на скринер\n"
        "/alerts - Ссылка на настройку алертов\n\n"
        "💬 Вопросы? Пиши @elcaro_support"
    )
    await update.message.reply_html(text)


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /chatid command - show only chat ID."""
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return
    text = f"🆔 Твой chat_id: <code>{chat_id}</code>"
    await update.message.reply_html(text)


async def website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /website command - show website link."""
    keyboard = [[InlineKeyboardButton("🌐 Открыть скринер", url="https://elcaro.online")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🌐 <b>NoetDat Crypto Screener</b>\n\nОтслеживай рынок в реальном времени!"
    await update.message.reply_html(text, reply_markup=reply_markup)


async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /alerts command - show alerts setup link."""
    keyboard = [[InlineKeyboardButton("⚙️ Настроить алерты", url="https://elcaro.online/alerts/")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "⚙️ <b>Настройка алертов</b>\n\n"
        "Создай персональные уведомления по метрикам:\n"
        "• 📈 Изменение цены\n"
        "• 💰 Объём торгов\n"
        "• 🔥 Open Interest\n"
        "• ⚡ Volume Delta\n"
        "• 📊 Волатильность\n"
        "И многое другое!"
    )
    await update.message.reply_html(text, reply_markup=reply_markup)


async def main() -> None:
    """Main async function that sets up and runs the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN env var is required")

    app = Application.builder().token(token).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("chatid", chatid))
    app.add_handler(CommandHandler("website", website))
    app.add_handler(CommandHandler("alerts", alerts_command))

    print("Telegram bot is running. Press Ctrl+C to stop.")
    print("Available commands: /start, /help, /chatid, /website, /alerts")
    
    # Initialize and start polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    # Wait forever (until signal received)
    stop_event = asyncio.Event()
    
    def handle_signal(sig):
        print(f"\nReceived signal {sig}, stopping...")
        stop_event.set()
    
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
    
    await stop_event.wait()
    
    # Graceful shutdown
    await app.updater.stop()
    await app.stop()
    await app.shutdown()
    print("Bot stopped gracefully.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


