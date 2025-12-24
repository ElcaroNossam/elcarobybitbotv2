"""
ELCARO Token Bot Commands

Telegram bot commands for ELCARO (ELC) token:
- View balance
- Buy ELC with USDT on TON
- Connect cold wallet (MetaMask, WalletConnect)
- View transaction history
- Subscription payments with ELC
"""

import logging
from decimal import Decimal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

import db_elcaro
from ton_payment_gateway import ELCAROPaymentManager
from cold_wallet_trading import connect_metamask, get_wallet_info

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------
# ELC Balance Command
# ------------------------------------------------------------------------------------

async def cmd_elc_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show user's ELCARO token balance."""
    user_id = update.effective_user.id
    t = ctx.t  # translations
    
    try:
        balance = db_elcaro.get_elc_balance(user_id)
        
        text = (
            f"💰 <b>ELCARO Balance</b>\n\n"
            f"Available: <b>{balance['available']:.2f} ELC</b>\n"
            f"Staked: <b>{balance['staked']:.2f} ELC</b>\n"
            f"Locked: <b>{balance['locked']:.2f} ELC</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Total: <b>{balance['total']:.2f} ELC</b>\n\n"
            f"💵 Value: ~${balance['total']:.2f} USD"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🛒 Buy ELC", callback_data="elc:buy"),
                InlineKeyboardButton("📊 History", callback_data="elc:history")
            ],
            [
                InlineKeyboardButton("🔗 Connect Wallet", callback_data="elc:connect_wallet")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting ELC balance for {user_id}: {e}")
        await update.message.reply_text(
            "❌ Failed to get ELC balance. Please try again.",
            parse_mode="HTML"
        )


# ------------------------------------------------------------------------------------
# Buy ELC Command
# ------------------------------------------------------------------------------------

async def cmd_buy_elc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show ELC purchase options."""
    user_id = update.effective_user.id
    t = ctx.t
    
    text = (
        f"🛒 <b>Buy ELCARO (ELC)</b>\n\n"
        f"💵 Current Price: <b>$1.00 USD / ELC</b>\n"
        f"🔥 Platform Fee: <b>0.5%</b>\n\n"
        f"<i>Purchase ELC with USDT on TON Network</i>\n\n"
        f"Choose amount to buy:"
    )
    
    amounts = [100, 500, 1000, 5000, 10000]
    keyboard = []
    
    for amount in amounts:
        usdt_cost = amount * 1.005  # +0.5% fee
        keyboard.append([
            InlineKeyboardButton(
                f"🪙 {amount} ELC (~${usdt_cost:.2f} USDT)",
                callback_data=f"elc:buy:{amount}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("✏️ Custom Amount", callback_data="elc:buy:custom")
    ])
    keyboard.append([
        InlineKeyboardButton("« Back", callback_data="elc:balance")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


# ------------------------------------------------------------------------------------
# ELC Transaction History
# ------------------------------------------------------------------------------------

async def cmd_elc_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show user's ELC transaction history."""
    user_id = update.effective_user.id
    t = ctx.t
    
    try:
        transactions = db_elcaro.get_elc_transactions(user_id, limit=10)
        
        if not transactions:
            text = "📊 <b>Transaction History</b>\n\nNo transactions yet."
        else:
            text = "📊 <b>Transaction History</b>\n\n"
            
            for tx in transactions:
                amount_str = f"+{tx['amount']:.2f}" if tx['amount'] >= 0 else f"{tx['amount']:.2f}"
                emoji = "🟢" if tx['amount'] >= 0 else "🔴"
                
                # Transaction type emoji
                type_emoji_map = {
                    "purchase": "🛒",
                    "subscription": "📱",
                    "marketplace": "🏪",
                    "burn": "🔥",
                    "stake": "💎",
                    "unstake": "💰",
                    "withdraw": "📤"
                }
                type_emoji = type_emoji_map.get(tx['transaction_type'], "💸")
                
                text += (
                    f"{emoji} {type_emoji} <b>{amount_str} ELC</b>\n"
                    f"   {tx['description'] or tx['transaction_type']}\n"
                    f"   Balance: {tx['balance_after']:.2f} ELC\n"
                    f"   {tx['created_at']}\n\n"
                )
        
        keyboard = [[InlineKeyboardButton("« Back", callback_data="elc:balance")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting ELC history for {user_id}: {e}")
        await update.message.reply_text(
            "❌ Failed to get transaction history. Please try again.",
            parse_mode="HTML"
        )


# ------------------------------------------------------------------------------------
# Connect Cold Wallet
# ------------------------------------------------------------------------------------

async def cmd_connect_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show wallet connection options."""
    user_id = update.effective_user.id
    t = ctx.t
    
    # Check if already connected
    wallet = db_elcaro.get_connected_wallet(user_id)
    
    if wallet:
        text = (
            f"🔗 <b>Connected Wallet</b>\n\n"
            f"Address: <code>{wallet['wallet_address'][:10]}...{wallet['wallet_address'][-8:]}</code>\n"
            f"Type: <b>{wallet['wallet_type'].title()}</b>\n"
            f"Chain: <b>{wallet['chain'].upper()}</b>\n"
            f"Connected: {wallet['connected_at']}\n\n"
            f"<i>Use this wallet to trade on HyperLiquid without exposing private keys</i>"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔓 Disconnect", callback_data="elc:disconnect_wallet")],
            [InlineKeyboardButton("« Back", callback_data="elc:balance")]
        ]
    else:
        text = (
            f"🔗 <b>Connect Cold Wallet</b>\n\n"
            f"Trade on HyperLiquid without exposing your private keys!\n\n"
            f"Supported wallets:\n"
            f"• MetaMask (Ethereum, Polygon, BSC)\n"
            f"• WalletConnect (Multi-chain)\n"
            f"• Tonkeeper (TON Network)\n\n"
            f"<i>Your keys never leave your device - all orders are signed locally</i>"
        )
        
        keyboard = [
            [InlineKeyboardButton("🦊 MetaMask", callback_data="elc:connect:metamask")],
            [InlineKeyboardButton("🔗 WalletConnect", callback_data="elc:connect:walletconnect")],
            [InlineKeyboardButton("💎 Tonkeeper", callback_data="elc:connect:tonkeeper")],
            [InlineKeyboardButton("« Back", callback_data="elc:balance")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)


# ------------------------------------------------------------------------------------
# Callback Query Handlers
# ------------------------------------------------------------------------------------

async def elc_callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle ELCARO-related callback queries."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    t = ctx.t
    
    try:
        if data == "elc:balance":
            # Show balance
            balance = db_elcaro.get_elc_balance(user_id)
            
            text = (
                f"💰 <b>ELCARO Balance</b>\n\n"
                f"Available: <b>{balance['available']:.2f} ELC</b>\n"
                f"Staked: <b>{balance['staked']:.2f} ELC</b>\n"
                f"Locked: <b>{balance['locked']:.2f} ELC</b>\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"Total: <b>{balance['total']:.2f} ELC</b>\n\n"
                f"💵 Value: ~${balance['total']:.2f} USD"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("🛒 Buy ELC", callback_data="elc:buy"),
                    InlineKeyboardButton("📊 History", callback_data="elc:history")
                ],
                [InlineKeyboardButton("🔗 Connect Wallet", callback_data="elc:connect_wallet")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
        elif data == "elc:buy":
            # Show buy options
            text = (
                f"🛒 <b>Buy ELCARO (ELC)</b>\n\n"
                f"💵 Current Price: <b>$1.00 USD / ELC</b>\n"
                f"🔥 Platform Fee: <b>0.5%</b>\n\n"
                f"<i>Purchase ELC with USDT on TON Network</i>\n\n"
                f"Choose amount to buy:"
            )
            
            amounts = [100, 500, 1000, 5000, 10000]
            keyboard = []
            
            for amount in amounts:
                usdt_cost = amount * 1.005
                keyboard.append([
                    InlineKeyboardButton(
                        f"🪙 {amount} ELC (~${usdt_cost:.2f} USDT)",
                        callback_data=f"elc:buy:{amount}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("✏️ Custom Amount", callback_data="elc:buy:custom")])
            keyboard.append([InlineKeyboardButton("« Back", callback_data="elc:balance")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
        elif data.startswith("elc:buy:"):
            # Process buy
            amount_str = data.split(":")[-1]
            
            if amount_str == "custom":
                text = (
                    f"✏️ <b>Custom Amount</b>\n\n"
                    f"Reply with the amount of ELC you want to buy\n"
                    f"Example: <code>2500</code>\n\n"
                    f"Min: 100 ELC\n"
                    f"Max: 100,000 ELC"
                )
                await query.edit_message_text(text, parse_mode="HTML")
                ctx.user_data["awaiting_elc_amount"] = True
                return
            
            try:
                elc_amount = float(amount_str)
                usdt_amount = elc_amount * 1.005  # +0.5% fee
                
                # Create payment via payment manager
                payment_manager = ELCAROPaymentManager()
                payment_result = await payment_manager.create_subscription_payment(
                    user_id=user_id,
                    plan="custom",
                    duration="instant",
                    custom_elc_amount=elc_amount
                )
                
                text = (
                    f"🛒 <b>Purchase {elc_amount:.2f} ELC</b>\n\n"
                    f"Cost: <b>{usdt_amount:.2f} USDT</b>\n"
                    f"Platform Fee: <b>{usdt_amount * 0.005:.2f} USDT</b>\n\n"
                    f"Payment Link:\n"
                    f"<code>{payment_result['payment_link']}</code>\n\n"
                    f"<i>Send USDT to this address on TON Network</i>"
                )
                
                keyboard = [
                    [InlineKeyboardButton("🔗 Open Payment", url=payment_result['payment_link'])],
                    [InlineKeyboardButton("« Back", callback_data="elc:buy")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
                
            except Exception as e:
                logger.error(f"Error creating payment: {e}")
                await query.edit_message_text(
                    "❌ Failed to create payment. Please try again.",
                    parse_mode="HTML"
                )
        
        elif data == "elc:history":
            # Show transaction history
            transactions = db_elcaro.get_elc_transactions(user_id, limit=10)
            
            if not transactions:
                text = "📊 <b>Transaction History</b>\n\nNo transactions yet."
            else:
                text = "📊 <b>Transaction History</b>\n\n"
                
                for tx in transactions:
                    amount_str = f"+{tx['amount']:.2f}" if tx['amount'] >= 0 else f"{tx['amount']:.2f}"
                    emoji = "🟢" if tx['amount'] >= 0 else "🔴"
                    
                    type_emoji_map = {
                        "purchase": "🛒",
                        "subscription": "📱",
                        "marketplace": "🏪",
                        "burn": "🔥",
                        "stake": "💎",
                        "unstake": "💰",
                        "withdraw": "📤"
                    }
                    type_emoji = type_emoji_map.get(tx['transaction_type'], "💸")
                    
                    text += (
                        f"{emoji} {type_emoji} <b>{amount_str} ELC</b>\n"
                        f"   {tx['description'] or tx['transaction_type']}\n"
                        f"   Balance: {tx['balance_after']:.2f} ELC\n"
                        f"   {tx['created_at']}\n\n"
                    )
            
            keyboard = [[InlineKeyboardButton("« Back", callback_data="elc:balance")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
        elif data == "elc:connect_wallet":
            # Show wallet connection options
            wallet = db_elcaro.get_connected_wallet(user_id)
            
            if wallet:
                text = (
                    f"🔗 <b>Connected Wallet</b>\n\n"
                    f"Address: <code>{wallet['wallet_address'][:10]}...{wallet['wallet_address'][-8:]}</code>\n"
                    f"Type: <b>{wallet['wallet_type'].title()}</b>\n"
                    f"Chain: <b>{wallet['chain'].upper()}</b>\n"
                    f"Connected: {wallet['connected_at']}\n\n"
                    f"<i>Use this wallet to trade on HyperLiquid without exposing private keys</i>"
                )
                
                keyboard = [
                    [InlineKeyboardButton("🔓 Disconnect", callback_data="elc:disconnect_wallet")],
                    [InlineKeyboardButton("« Back", callback_data="elc:balance")]
                ]
            else:
                text = (
                    f"🔗 <b>Connect Cold Wallet</b>\n\n"
                    f"Trade on HyperLiquid without exposing your private keys!\n\n"
                    f"Supported wallets:\n"
                    f"• MetaMask (Ethereum, Polygon, BSC)\n"
                    f"• WalletConnect (Multi-chain)\n"
                    f"• Tonkeeper (TON Network)\n\n"
                    f"<i>Your keys never leave your device - all orders are signed locally</i>"
                )
                
                keyboard = [
                    [InlineKeyboardButton("🦊 MetaMask", callback_data="elc:connect:metamask")],
                    [InlineKeyboardButton("🔗 WalletConnect", callback_data="elc:connect:walletconnect")],
                    [InlineKeyboardButton("💎 Tonkeeper", callback_data="elc:connect:tonkeeper")],
                    [InlineKeyboardButton("« Back", callback_data="elc:balance")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
        elif data.startswith("elc:connect:"):
            wallet_type = data.split(":")[-1]
            
            # Generate connection instructions
            webapp_url = "https://kevin-longitude-night-pro.trycloudflare.com"  # Get from config
            
            text = (
                f"🔗 <b>Connect {wallet_type.title()}</b>\n\n"
                f"1. Open our WebApp\n"
                f"2. Click 'Connect Wallet'\n"
                f"3. Select {wallet_type.title()}\n"
                f"4. Approve connection in wallet\n\n"
                f"<i>Your private keys stay in your wallet - we only get your public address</i>"
            )
            
            keyboard = [
                [InlineKeyboardButton("🌐 Open WebApp", url=f"{webapp_url}/terminal")],
                [InlineKeyboardButton("« Back", callback_data="elc:connect_wallet")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
        elif data == "elc:disconnect_wallet":
            # Disconnect wallet
            db_elcaro.disconnect_wallet(user_id)
            
            text = (
                f"🔓 <b>Wallet Disconnected</b>\n\n"
                f"Your wallet has been successfully disconnected.\n\n"
                f"<i>You can reconnect anytime to resume cold wallet trading</i>"
            )
            
            keyboard = [[InlineKeyboardButton("« Back", callback_data="elc:balance")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
    
    except Exception as e:
        logger.error(f"Error in ELC callback handler: {e}")
        await query.edit_message_text(
            "❌ An error occurred. Please try again.",
            parse_mode="HTML"
        )


# ------------------------------------------------------------------------------------
# Register Handlers (call from bot.py)
# ------------------------------------------------------------------------------------

def register_elc_handlers(app):
    """
    Register ELCARO token handlers.
    
    Call this from bot.py:
        from elcaro_bot_commands import register_elc_handlers
        register_elc_handlers(app)
    """
    app.add_handler(CommandHandler("elc", cmd_elc_balance))
    app.add_handler(CommandHandler("buy_elc", cmd_buy_elc))
    app.add_handler(CommandHandler("elc_history", cmd_elc_history))
    app.add_handler(CommandHandler("connect_wallet", cmd_connect_wallet))
    
    # Callback query handler for all elc: callbacks
    app.add_handler(CallbackQueryHandler(elc_callback_handler, pattern="^elc:"))
    
    logger.info("✅ ELCARO token handlers registered")
