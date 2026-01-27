"""
ENLIKO Token Bot Commands

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
    """Show user's ENLIKO token balance."""
    user_id = update.effective_user.id
    t = ctx.t  # translations
    
    try:
        balance = db_elcaro.get_elc_balance(user_id)
        
        text = (
            f"{t.get('elc_balance_title')}\n\n"
            f"{t.get('elc_available')}: <b>{balance['available']:.2f} ELC</b>\n"
            f"{t.get('elc_staked')}: <b>{balance['staked']:.2f} ELC</b>\n"
            f"{t.get('elc_locked')}: <b>{balance['locked']:.2f} ELC</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"{t.get('elc_total')}: <b>{balance['total']:.2f} ELC</b>\n\n"
            f"{t.get('elc_value_usd', value=balance['total'])}"
        )
        
        keyboard = [
            [
                InlineKeyboardButton(t.get('btn_buy_elc'), callback_data="elc:buy"),
                InlineKeyboardButton(t.get('btn_elc_history'), callback_data="elc:history")
            ],
            [
                InlineKeyboardButton(t.get('btn_connect_wallet'), callback_data="elc:connect_wallet")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting ELC balance for {user_id}: {e}")
        await update.message.reply_text(
            t.get('elc_balance_error'),
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
        f"{t.get('elc_buy_title')}\n\n"
        f"{t.get('elc_current_price')}\n"
        f"{t.get('elc_platform_fee')}\n\n"
        f"{t.get('elc_purchase_hint')}\n\n"
        f"{t.get('elc_choose_amount')}"
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
        InlineKeyboardButton(t.get('elc_custom_amount'), callback_data="elc:buy:custom")
    ])
    keyboard.append([
        InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:balance")
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
            text = f"{t.get('elc_history_title')}\n\n{t.get('elc_no_transactions')}"
        else:
            text = f"{t.get('elc_history_title')}\n\n"
            
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
        
        keyboard = [[InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:balance")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error getting ELC history for {user_id}: {e}")
        await update.message.reply_text(
            t.get('elc_history_error'),
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
            f"{t.get('elc_wallet_connected_title')}\n\n"
            f"{t.get('elc_wallet_address')}: <code>{wallet['wallet_address'][:10]}...{wallet['wallet_address'][-8:]}</code>\n"
            f"{t.get('elc_wallet_type')}: <b>{wallet['wallet_type'].title()}</b>\n"
            f"{t.get('elc_wallet_chain')}: <b>{wallet['chain'].upper()}</b>\n"
            f"{t.get('elc_wallet_connected_at')}: {wallet['connected_at']}\n\n"
            f"{t.get('elc_wallet_hint')}"
        )
        
        keyboard = [
            [InlineKeyboardButton(t.get('btn_disconnect_wallet'), callback_data="elc:disconnect_wallet")],
            [InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:balance")]
        ]
    else:
        text = (
            f"{t.get('elc_connect_title')}\n\n"
            f"{t.get('elc_connect_desc')}\n\n"
            f"{t.get('elc_supported_wallets')}\n"
            f"{t.get('elc_wallet_metamask')}\n"
            f"{t.get('elc_wallet_wc')}\n"
            f"{t.get('elc_wallet_tonkeeper')}\n\n"
            f"{t.get('elc_keys_local')}"
        )
        
        keyboard = [
            [InlineKeyboardButton(t.get('btn_metamask'), callback_data="elc:connect:metamask")],
            [InlineKeyboardButton(t.get('btn_walletconnect'), callback_data="elc:connect:walletconnect")],
            [InlineKeyboardButton(t.get('btn_tonkeeper'), callback_data="elc:connect:tonkeeper")],
            [InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:balance")]
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
                f"{t.get('elc_balance_title')}\n\n"
                f"{t.get('elc_available')}: <b>{balance['available']:.2f} ELC</b>\n"
                f"{t.get('elc_staked')}: <b>{balance['staked']:.2f} ELC</b>\n"
                f"{t.get('elc_locked')}: <b>{balance['locked']:.2f} ELC</b>\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"{t.get('elc_total')}: <b>{balance['total']:.2f} ELC</b>\n\n"
                f"{t.get('elc_value_usd', value=balance['total'])}"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton(t.get('btn_buy_elc'), callback_data="elc:buy"),
                    InlineKeyboardButton(t.get('btn_elc_history'), callback_data="elc:history")
                ],
                [InlineKeyboardButton(t.get('btn_connect_wallet'), callback_data="elc:connect_wallet")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
        elif data == "elc:buy":
            # Show buy options
            text = (
                f"{t.get('elc_buy_title')}\n\n"
                f"{t.get('elc_current_price')}\n"
                f"{t.get('elc_platform_fee')}\n\n"
                f"{t.get('elc_purchase_hint')}\n\n"
                f"{t.get('elc_choose_amount')}"
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
            
            keyboard.append([InlineKeyboardButton(t.get('elc_custom_amount'), callback_data="elc:buy:custom")])
            keyboard.append([InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:balance")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
        elif data.startswith("elc:buy:"):
            # Process buy
            amount_str = data.split(":")[-1]
            
            if amount_str == "custom":
                text = (
                    f"{t.get('elc_custom_amount_title')}\n\n"
                    f"{t.get('elc_custom_prompt')}"
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
                    f"{t.get('elc_purchase_summary', amount=elc_amount)}\n\n"
                    f"{t.get('elc_cost', cost=usdt_amount)}\n"
                    f"{t.get('elc_fee_amount', fee=usdt_amount * 0.005)}\n\n"
                    f"{t.get('elc_payment_link')}\n"
                    f"<code>{payment_result['payment_link']}</code>\n\n"
                    f"{t.get('elc_payment_hint')}"
                )
                
                keyboard = [
                    [InlineKeyboardButton(t.get('btn_open_payment'), url=payment_result['payment_link'])],
                    [InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:buy")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
                
            except Exception as e:
                logger.error(f"Error creating payment: {e}")
                await query.edit_message_text(
                    t.get('elc_payment_error'),
                    parse_mode="HTML"
                )
        
        elif data == "elc:history":
            # Show transaction history
            transactions = db_elcaro.get_elc_transactions(user_id, limit=10)
            
            if not transactions:
                text = f"{t.get('elc_history_title')}\n\n{t.get('elc_no_transactions')}"
            else:
                text = f"{t.get('elc_history_title')}\n\n"
                
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
            
            keyboard = [[InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:balance")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
        elif data == "elc:connect_wallet":
            # Show wallet connection options
            wallet = db_elcaro.get_connected_wallet(user_id)
            
            if wallet:
                text = (
                    f"{t.get('elc_wallet_connected_title')}\n\n"
                    f"{t.get('elc_wallet_address')}: <code>{wallet['wallet_address'][:10]}...{wallet['wallet_address'][-8:]}</code>\n"
                    f"{t.get('elc_wallet_type')}: <b>{wallet['wallet_type'].title()}</b>\n"
                    f"{t.get('elc_wallet_chain')}: <b>{wallet['chain'].upper()}</b>\n"
                    f"{t.get('elc_wallet_connected_at')}: {wallet['connected_at']}\n\n"
                    f"{t.get('elc_wallet_hint')}"
                )
                
                keyboard = [
                    [InlineKeyboardButton(t.get('btn_disconnect_wallet'), callback_data="elc:disconnect_wallet")],
                    [InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:balance")]
                ]
            else:
                text = (
                    f"{t.get('elc_connect_title')}\n\n"
                    f"{t.get('elc_connect_desc')}\n\n"
                    f"{t.get('elc_supported_wallets')}\n"
                    f"{t.get('elc_wallet_metamask')}\n"
                    f"{t.get('elc_wallet_wc')}\n"
                    f"{t.get('elc_wallet_tonkeeper')}\n\n"
                    f"{t.get('elc_keys_local')}"
                )
                
                keyboard = [
                    [InlineKeyboardButton(t.get('btn_metamask'), callback_data="elc:connect:metamask")],
                    [InlineKeyboardButton(t.get('btn_walletconnect'), callback_data="elc:connect:walletconnect")],
                    [InlineKeyboardButton(t.get('btn_tonkeeper'), callback_data="elc:connect:tonkeeper")],
                    [InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:balance")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
        elif data.startswith("elc:connect:"):
            wallet_type = data.split(":")[-1]
            
            # Generate connection instructions
            webapp_url = os.getenv("WEBAPP_URL", "https://named-supplement-pending-cooking.trycloudflare.com")
            
            text = (
                f"{t.get('elc_connect_steps_title', wallet=wallet_type.title())}\n\n"
                f"{t.get('elc_connect_step1')}\n"
                f"{t.get('elc_connect_step2')}\n"
                f"{t.get('elc_connect_step3', wallet=wallet_type.title())}\n"
                f"{t.get('elc_connect_step4')}\n\n"
                f"{t.get('elc_connect_keys_hint')}"
            )
            
            keyboard = [
                [InlineKeyboardButton(t.get('btn_open_webapp'), url=f"{webapp_url}/terminal")],
                [InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:connect_wallet")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
        
        elif data == "elc:disconnect_wallet":
            # Disconnect wallet
            db_elcaro.disconnect_wallet(user_id)
            
            text = (
                f"{t.get('elc_disconnected_title')}\n\n"
                f"{t.get('elc_disconnected_msg')}\n\n"
                f"{t.get('elc_disconnected_hint')}"
            )
            
            keyboard = [[InlineKeyboardButton(t.get('btn_back', '« Back'), callback_data="elc:balance")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)
    
    except Exception as e:
        logger.error(f"Error in ELC callback handler: {e}")
        await query.edit_message_text(
            t.get('elc_error_generic'),
            parse_mode="HTML"
        )


# ------------------------------------------------------------------------------------
# Register Handlers (call from bot.py)
# ------------------------------------------------------------------------------------

def register_elc_handlers(app):
    """
    Register ENLIKO token handlers.
    
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
    
    logger.info("✅ ENLIKO token handlers registered")
