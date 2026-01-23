"""
Keyboard Helpers - Centralized keyboard button factory

Eliminates duplicate InlineKeyboardButton patterns across bot.py
Provides consistent styling and translation support
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional, Callable, Any


# ═══════════════════════════════════════════════════════════════════════════════
# COMMON BUTTONS
# ═══════════════════════════════════════════════════════════════════════════════

def btn_back(t: Any, callback_data: str = "back", icon: str = "⬅️") -> InlineKeyboardButton:
    """
    Create a standardized Back button.
    
    Args:
        t: Translation dict/object with get() method
        callback_data: Callback data string
        icon: Emoji icon (default: ⬅️)
    
    Returns:
        InlineKeyboardButton
    """
    label = t.get('btn_back', f'{icon} Back') if hasattr(t, 'get') else f'{icon} Back'
    return InlineKeyboardButton(label, callback_data=callback_data)


def btn_close(t: Any, callback_data: str = "close") -> InlineKeyboardButton:
    """Create a Close button."""
    label = t.get('btn_close', '❌ Close') if hasattr(t, 'get') else '❌ Close'
    return InlineKeyboardButton(label, callback_data=callback_data)


def btn_cancel(t: Any, callback_data: str = "cancel") -> InlineKeyboardButton:
    """Create a Cancel button."""
    label = t.get('btn_cancel', '❌ Cancel') if hasattr(t, 'get') else '❌ Cancel'
    return InlineKeyboardButton(label, callback_data=callback_data)


def btn_confirm(t: Any, callback_data: str = "confirm") -> InlineKeyboardButton:
    """Create a Confirm button."""
    label = t.get('btn_confirm', '✅ Confirm') if hasattr(t, 'get') else '✅ Confirm'
    return InlineKeyboardButton(label, callback_data=callback_data)


def btn_refresh(t: Any, callback_data: str = "refresh") -> InlineKeyboardButton:
    """Create a Refresh button."""
    label = t.get('btn_refresh', '🔄 Refresh') if hasattr(t, 'get') else '🔄 Refresh'
    return InlineKeyboardButton(label, callback_data=callback_data)


def btn_settings(t: Any, callback_data: str = "settings") -> InlineKeyboardButton:
    """Create a Settings button."""
    label = t.get('btn_settings', '⚙️ Settings') if hasattr(t, 'get') else '⚙️ Settings'
    return InlineKeyboardButton(label, callback_data=callback_data)


def btn_delete(t: Any, callback_data: str = "delete") -> InlineKeyboardButton:
    """Create a Delete button."""
    label = t.get('btn_delete', '🗑️ Delete') if hasattr(t, 'get') else '🗑️ Delete'
    return InlineKeyboardButton(label, callback_data=callback_data)


def btn_yes(t: Any, callback_data: str = "yes") -> InlineKeyboardButton:
    """Create a Yes button."""
    label = t.get('btn_yes', '✅ Yes') if hasattr(t, 'get') else '✅ Yes'
    return InlineKeyboardButton(label, callback_data=callback_data)


def btn_no(t: Any, callback_data: str = "no") -> InlineKeyboardButton:
    """Create a No button."""
    label = t.get('btn_no', '❌ No') if hasattr(t, 'get') else '❌ No'
    return InlineKeyboardButton(label, callback_data=callback_data)


# ═══════════════════════════════════════════════════════════════════════════════
# NAVIGATION BUTTONS
# ═══════════════════════════════════════════════════════════════════════════════

def btn_prev(t: Any, callback_data: str, disabled: bool = False) -> InlineKeyboardButton:
    """Create a Previous page button."""
    label = t.get('btn_prev', '◀️ Prev') if hasattr(t, 'get') else '◀️ Prev'
    if disabled:
        return InlineKeyboardButton("⬛", callback_data="noop")
    return InlineKeyboardButton(label, callback_data=callback_data)


def btn_next(t: Any, callback_data: str, disabled: bool = False) -> InlineKeyboardButton:
    """Create a Next page button."""
    label = t.get('btn_next', 'Next ▶️') if hasattr(t, 'get') else 'Next ▶️'
    if disabled:
        return InlineKeyboardButton("⬛", callback_data="noop")
    return InlineKeyboardButton(label, callback_data=callback_data)


def btn_page_info(page: int, total: int) -> InlineKeyboardButton:
    """Create a page info button (non-clickable)."""
    return InlineKeyboardButton(f"{page}/{total}", callback_data="noop")


# ═══════════════════════════════════════════════════════════════════════════════
# TOGGLE BUTTONS
# ═══════════════════════════════════════════════════════════════════════════════

def btn_toggle(
    t: Any,
    label: str,
    callback_data: str,
    is_on: bool,
    on_icon: str = "✅",
    off_icon: str = "❌"
) -> InlineKeyboardButton:
    """
    Create a toggle button with on/off state.
    
    Args:
        t: Translation dict/object
        label: Button label (translation key or text)
        callback_data: Callback data
        is_on: Current state
        on_icon: Icon when enabled
        off_icon: Icon when disabled
    """
    text = t.get(label, label) if hasattr(t, 'get') else label
    icon = on_icon if is_on else off_icon
    return InlineKeyboardButton(f"{icon} {text}", callback_data=callback_data)


def btn_radio(
    label: str,
    callback_data: str,
    is_selected: bool,
    selected_icon: str = "🔘",
    unselected_icon: str = "⚪"
) -> InlineKeyboardButton:
    """Create a radio button."""
    icon = selected_icon if is_selected else unselected_icon
    return InlineKeyboardButton(f"{icon} {label}", callback_data=callback_data)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION HEADERS
# ═══════════════════════════════════════════════════════════════════════════════

def btn_section(label: str, icon: str = "══") -> InlineKeyboardButton:
    """
    Create a section header (non-clickable).
    
    Args:
        label: Section label
        icon: Delimiter icon
    """
    return InlineKeyboardButton(f"{icon} {label} {icon}", callback_data="noop")


def btn_divider() -> InlineKeyboardButton:
    """Create a visual divider."""
    return InlineKeyboardButton("━━━━━━━━━━━━━━━━", callback_data="noop")


# ═══════════════════════════════════════════════════════════════════════════════
# KEYBOARD BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

def build_keyboard(
    buttons: List[List[InlineKeyboardButton]],
    back_button: Optional[InlineKeyboardButton] = None,
    close_button: Optional[InlineKeyboardButton] = None
) -> InlineKeyboardMarkup:
    """
    Build keyboard with optional back/close buttons.
    
    Args:
        buttons: 2D list of buttons
        back_button: Optional back button to add at bottom
        close_button: Optional close button to add at bottom
    
    Returns:
        InlineKeyboardMarkup
    """
    kb = list(buttons)  # Copy to avoid mutation
    
    if back_button and close_button:
        kb.append([back_button, close_button])
    elif back_button:
        kb.append([back_button])
    elif close_button:
        kb.append([close_button])
    
    return InlineKeyboardMarkup(kb)


def build_paginated_keyboard(
    items: List[InlineKeyboardButton],
    page: int,
    per_page: int,
    page_callback_prefix: str,
    t: Any,
    back_callback: Optional[str] = None,
    columns: int = 2
) -> InlineKeyboardMarkup:
    """
    Build a paginated keyboard.
    
    Args:
        items: List of buttons to paginate
        page: Current page (1-indexed)
        per_page: Items per page
        page_callback_prefix: Prefix for page navigation callbacks
        t: Translation dict
        back_callback: Optional callback for back button
        columns: Number of columns per row
    
    Returns:
        InlineKeyboardMarkup
    """
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_items = items[start_idx:end_idx]
    
    # Build rows
    rows = []
    for i in range(0, len(page_items), columns):
        row = page_items[i:i + columns]
        rows.append(row)
    
    # Navigation row
    if total_pages > 1:
        nav_row = [
            btn_prev(t, f"{page_callback_prefix}:{page - 1}", disabled=(page <= 1)),
            btn_page_info(page, total_pages),
            btn_next(t, f"{page_callback_prefix}:{page + 1}", disabled=(page >= total_pages)),
        ]
        rows.append(nav_row)
    
    # Back button
    if back_callback:
        rows.append([btn_back(t, back_callback)])
    
    return InlineKeyboardMarkup(rows)


def build_confirm_dialog(
    t: Any,
    confirm_callback: str,
    cancel_callback: str,
    message_buttons: Optional[List[InlineKeyboardButton]] = None
) -> InlineKeyboardMarkup:
    """
    Build a confirmation dialog keyboard.
    
    Args:
        t: Translation dict
        confirm_callback: Callback for confirm button
        cancel_callback: Callback for cancel button
        message_buttons: Optional additional buttons above confirm/cancel
    
    Returns:
        InlineKeyboardMarkup
    """
    rows = []
    
    if message_buttons:
        rows.append(message_buttons)
    
    rows.append([
        btn_confirm(t, confirm_callback),
        btn_cancel(t, cancel_callback)
    ])
    
    return InlineKeyboardMarkup(rows)


def build_yes_no_dialog(
    t: Any,
    yes_callback: str,
    no_callback: str
) -> InlineKeyboardMarkup:
    """Build a Yes/No dialog keyboard."""
    return InlineKeyboardMarkup([
        [btn_yes(t, yes_callback), btn_no(t, no_callback)]
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY SPECIFIC HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def build_strategy_toggle_row(
    t: Any,
    strategy: str,
    is_enabled: bool,
    callback_prefix: str = "strat"
) -> List[InlineKeyboardButton]:
    """Build a strategy toggle button row."""
    icons = {
        'elcaro': '🔥',
        'alpha': '🔷',
        'apex': '⚡',
        'btc': '₿',
        'funding': '💰',
        'spot': '🪙'
    }
    icon = icons.get(strategy.lower(), '📊')
    status = "✅" if is_enabled else "❌"
    
    return [
        InlineKeyboardButton(
            f"{icon} {strategy.title()} {status}",
            callback_data=f"{callback_prefix}:toggle:{strategy}"
        )
    ]


def build_exchange_selector(
    t: Any,
    current_mode: str,
    callback_prefix: str = "exch"
) -> InlineKeyboardMarkup:
    """Build exchange mode selector keyboard."""
    modes = [
        ('bybit', t.get('exch_mode_bybit_only', '🟠 Bybit Only')),
        ('hl', t.get('exch_mode_hl_only', '🟢 HyperLiquid Only')),
        ('both', t.get('exch_mode_both', '🔄 Both Exchanges')),
    ]
    
    rows = []
    for mode, label in modes:
        icon = "✅ " if mode == current_mode else ""
        rows.append([
            InlineKeyboardButton(f"{icon}{label}", callback_data=f"{callback_prefix}:mode:{mode}")
        ])
    
    return InlineKeyboardMarkup(rows)


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def chunk_buttons(buttons: List[InlineKeyboardButton], columns: int = 2) -> List[List[InlineKeyboardButton]]:
    """
    Split buttons into rows with specified number of columns.
    
    Args:
        buttons: Flat list of buttons
        columns: Number of buttons per row
    
    Returns:
        2D list of buttons
    """
    return [buttons[i:i + columns] for i in range(0, len(buttons), columns)]


def make_url_button(label: str, url: str) -> InlineKeyboardButton:
    """Create a URL button."""
    return InlineKeyboardButton(label, url=url)


def make_webapp_button(label: str, url: str) -> InlineKeyboardButton:
    """Create a WebApp button."""
    from telegram import WebAppInfo
    return InlineKeyboardButton(label, web_app=WebAppInfo(url=url))
