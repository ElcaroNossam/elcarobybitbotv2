"""
Exchange UI Module - Keyboards and display functions for multi-exchange support
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def get_exchange_selector_keyboard(current_mode: str = "bybit", hl_configured: bool = False) -> InlineKeyboardMarkup:
    """Get inline keyboard for exchange mode selection."""
    buttons = []
    
    # Bybit button
    bybit_check = "✅ " if current_mode in ("bybit", "both") else ""
    buttons.append([InlineKeyboardButton(f"{bybit_check}🟠 Bybit", callback_data="exch:select:bybit")])
    
    # HyperLiquid button (only if configured)
    if hl_configured:
        hl_check = "✅ " if current_mode in ("hyperliquid", "both") else ""
        buttons.append([InlineKeyboardButton(f"{hl_check}🟢 HyperLiquid", callback_data="exch:select:hyperliquid")])
        
        # Both button
        both_check = "✅ " if current_mode == "both" else ""
        buttons.append([InlineKeyboardButton(f"{both_check}🔄 Обе биржи", callback_data="exch:select:both")])
    else:
        buttons.append([InlineKeyboardButton("➕ Подключить HyperLiquid", callback_data="hl:mainnet")])
    
    return InlineKeyboardMarkup(buttons)


def get_main_menu_keyboard_by_exchange(
    exchange_mode: str,
    t: dict,
    bybit_mode: str = "demo",
    hl_testnet: bool = False,
) -> ReplyKeyboardMarkup:
    """Get main menu keyboard adapted to exchange mode."""
    
    # Common buttons for all modes
    settings_btn = t.get("button_settings", "⚙️ Settings")
    stats_btn = t.get("button_stats", "📊 Statistics")
    
    if exchange_mode == "bybit":
        # Bybit-only keyboard
        mode_emoji = "🧪" if bybit_mode == "demo" else "💰"
        keyboard = [
            [t.get("button_balance", "💰 Balance"), t.get("button_positions", "📊 Positions")],
            [t.get("button_orders", "📋 Orders"), t.get("button_manual_order", "✍️ Manual Order")],
            [settings_btn, stats_btn],
            [f"🟠 Bybit {mode_emoji}", t.get("button_exchange", "🔄 Exchange")],
        ]
    elif exchange_mode == "hyperliquid":
        # HyperLiquid-only keyboard
        mode_emoji = "🧪" if hl_testnet else "🌐"
        keyboard = [
            [t.get("button_balance", "💰 Balance"), t.get("button_positions", "📊 Positions")],
            [t.get("button_orders", "�� Orders"), t.get("button_manual_order", "✍️ Manual Order")],
            [settings_btn, stats_btn],
            [f"🟢 HyperLiquid {mode_emoji}", t.get("button_exchange", "🔄 Exchange")],
        ]
    else:  # both
        # Dual exchange keyboard with separate sections
        bb_emoji = "🧪" if bybit_mode == "demo" else "💰"
        hl_emoji = "🧪" if hl_testnet else "🌐"
        keyboard = [
            # Bybit section
            [f"🟠 BB: Balance {bb_emoji}", f"🟠 BB: Positions"],
            # HyperLiquid section
            [f"🟢 HL: Balance {hl_emoji}", f"🟢 HL: Positions"],
            # Common
            [t.get("button_manual_order", "✍️ Manual Order"), t.get("button_orders", "📋 All Orders")],
            [settings_btn, stats_btn],
            [f"🔄 Both Exchanges", t.get("button_exchange", "🔄 Switch")],
        ]
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_exchange_status_text(status: dict, t: dict) -> str:
    """Generate status text for both exchanges."""
    mode = status["exchange_mode"]
    bb = status["bybit"]
    hl = status["hyperliquid"]
    
    # Mode labels
    mode_labels = {
        "bybit": "🟠 Только Bybit",
        "hyperliquid": "🟢 Только HyperLiquid",
        "both": "🔄 Обе биржи",
    }
    
    lines = [
        f"*🔀 Режим торговли:* {mode_labels.get(mode, mode)}",
        "",
        "*🟠 Bybit:*",
    ]
    
    # Bybit status
    if bb["demo_configured"] or bb["real_configured"]:
        bb_mode = "Demo" if bb["trading_mode"] == "demo" else "Real"
        demo_status = "✅" if bb["demo_configured"] else "❌"
        real_status = "✅" if bb["real_configured"] else "❌"
        active = "🟢 Active" if bb["active"] else "⚪ Inactive"
        lines.extend([
            f"   Demo API: {demo_status} | Real API: {real_status}",
            f"   Mode: {bb_mode} | Status: {active}",
        ])
    else:
        lines.append("   ❌ Не настроен")
    
    lines.extend(["", "*🟢 HyperLiquid:*"])
    
    # HyperLiquid status
    if hl["configured"]:
        network = "🧪 Testnet" if hl["testnet"] else "🌐 Mainnet"
        addr = hl["address"][:8] + "..." + hl["address"][-6:] if hl["address"] else "N/A"
        active = "🟢 Active" if hl["active"] else "⚪ Inactive"
        lines.extend([
            f"   Wallet: `{addr}`",
            f"   Network: {network} | Status: {active}",
        ])
    else:
        lines.append("   ❌ Не подключен")
    
    return "\n".join(lines)


def get_api_settings_keyboard_with_hl(
    t: dict,
    bybit_demo: bool,
    bybit_real: bool,
    hl_configured: bool,
    bybit_mode: str,
    hl_testnet: bool,
) -> InlineKeyboardMarkup:
    """Get API settings keyboard with both Bybit and HyperLiquid options."""
    buttons = []
    
    # Bybit section header
    buttons.append([InlineKeyboardButton("━━━ 🟠 Bybit ━━━", callback_data="api:noop")])
    
    # Bybit Demo
    demo_status = "✅" if bybit_demo else "❌"
    buttons.append([
        InlineKeyboardButton(f"Demo API {demo_status}", callback_data="api:demo"),
        InlineKeyboardButton("🗑", callback_data="api:delete:demo") if bybit_demo else InlineKeyboardButton(" ", callback_data="api:noop"),
    ])
    
    # Bybit Real
    real_status = "✅" if bybit_real else "❌"
    buttons.append([
        InlineKeyboardButton(f"Real API {real_status}", callback_data="api:real"),
        InlineKeyboardButton("🗑", callback_data="api:delete:real") if bybit_real else InlineKeyboardButton(" ", callback_data="api:noop"),
    ])
    
    # Bybit mode toggle (demo/real)
    if bybit_demo and bybit_real:
        current = "Demo 🧪" if bybit_mode == "demo" else "Real 💰"
        buttons.append([InlineKeyboardButton(f"Trading: {current}", callback_data="api:toggle_mode")])
    
    # HyperLiquid section header
    buttons.append([InlineKeyboardButton("━━━ 🟢 HyperLiquid ━━━", callback_data="api:noop")])
    
    if hl_configured:
        # HL configured - show options
        network = "Testnet 🧪" if hl_testnet else "Mainnet 🌐"
        buttons.append([
            InlineKeyboardButton(f"Network: {network}", callback_data="hl:network"),
            InlineKeyboardButton("🗑", callback_data="hl:disconnect"),
        ])
    else:
        # Not configured - add button
        buttons.append([InlineKeyboardButton("➕ Connect Wallet", callback_data="hl:mainnet")])
    
    # Back button
    buttons.append([InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="api:back")])
    
    return InlineKeyboardMarkup(buttons)


def get_balance_text_dual(
    bybit_balance: dict,
    hl_balance: dict,
    exchange_mode: str,
    bybit_mode: str,
    hl_testnet: bool,
) -> str:
    """Generate combined balance text for both exchanges."""
    lines = []
    
    total_equity = 0.0
    total_available = 0.0
    total_pnl = 0.0
    
    if exchange_mode in ("bybit", "both"):
        bb_equity = float(bybit_balance.get("equity", 0))
        bb_available = float(bybit_balance.get("available", 0))
        bb_pnl = float(bybit_balance.get("unrealized_pnl", 0))
        
        bb_mode = "🧪 Demo" if bybit_mode == "demo" else "💰 Real"
        bb_pnl_emoji = "🟢" if bb_pnl >= 0 else "🔴"
        
        lines.extend([
            f"*🟠 Bybit* ({bb_mode})",
            f"   💎 Equity: ${bb_equity:,.2f}",
            f"   💵 Available: ${bb_available:,.2f}",
            f"   {bb_pnl_emoji} PnL: ${bb_pnl:+,.2f}",
            "",
        ])
        
        total_equity += bb_equity
        total_available += bb_available
        total_pnl += bb_pnl
    
    if exchange_mode in ("hyperliquid", "both"):
        hl_equity = float(hl_balance.get("equity", 0))
        hl_available = float(hl_balance.get("available", 0))
        hl_pnl = float(hl_balance.get("unrealized_pnl", 0))
        
        hl_mode = "🧪 Testnet" if hl_testnet else "�� Mainnet"
        hl_pnl_emoji = "🟢" if hl_pnl >= 0 else "🔴"
        
        lines.extend([
            f"*🟢 HyperLiquid* ({hl_mode})",
            f"   💎 Equity: ${hl_equity:,.2f}",
            f"   💵 Available: ${hl_available:,.2f}",
            f"   {hl_pnl_emoji} PnL: ${hl_pnl:+,.2f}",
            "",
        ])
        
        total_equity += hl_equity
        total_available += hl_available
        total_pnl += hl_pnl
    
    # Total if both exchanges
    if exchange_mode == "both":
        total_pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
        lines.extend([
            "━━━━━━━━━━━━━━━",
            "*📊 Total*",
            f"   💎 Equity: ${total_equity:,.2f}",
            f"   💵 Available: ${total_available:,.2f}",
            f"   {total_pnl_emoji} PnL: ${total_pnl:+,.2f}",
        ])
    
    return "\n".join(lines)


def get_positions_text_dual(
    bybit_positions: list,
    hl_positions: list,
    exchange_mode: str,
    t: dict,
) -> str:
    """Generate combined positions text for both exchanges."""
    lines = []
    total_pnl = 0.0
    position_count = 0
    
    if exchange_mode in ("bybit", "both") and bybit_positions:
        lines.append("*🟠 Bybit Positions:*\n")
        for pos in bybit_positions[:5]:
            symbol = pos.get("symbol", "?")
            side = pos.get("side", "?")
            size = float(pos.get("size", 0))
            pnl = float(pos.get("unrealisedPnl", 0))
            leverage = pos.get("leverage", "?")
            
            side_emoji = "🟢" if side == "Buy" else "🔴"
            pnl_emoji = "+" if pnl >= 0 else ""
            
            lines.append(f"{side_emoji} *{symbol}* {leverage}x | {pnl_emoji}${pnl:.2f}")
            total_pnl += pnl
            position_count += 1
        
        if len(bybit_positions) > 5:
            lines.append(f"   _...and {len(bybit_positions) - 5} more_")
        lines.append("")
    
    if exchange_mode in ("hyperliquid", "both") and hl_positions:
        lines.append("*🟢 HyperLiquid Positions:*\n")
        for pos in hl_positions[:5]:
            symbol = pos.get("symbol", "?")
            side = pos.get("side", "?")
            pnl = float(pos.get("unrealized_pnl", 0))
            leverage = pos.get("leverage", "?")
            
            side_emoji = "🟢" if side == "Buy" else "🔴"
            pnl_emoji = "+" if pnl >= 0 else ""
            
            lines.append(f"{side_emoji} *{symbol}* {leverage}x | {pnl_emoji}${pnl:.2f}")
            total_pnl += pnl
            position_count += 1
        
        if len(hl_positions) > 5:
            lines.append(f"   _...and {len(hl_positions) - 5} more_")
        lines.append("")
    
    if position_count == 0:
        return t.get("no_positions", "📭 No open positions")
    
    # Total summary
    if exchange_mode == "both":
        pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
        lines.extend([
            "━━━━━━━━━━━━━━━",
            f"*Total:* {position_count} positions | {pnl_emoji} ${total_pnl:+,.2f}",
        ])
    
    return "\n".join(lines)
