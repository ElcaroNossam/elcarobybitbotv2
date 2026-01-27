"""
App Branding Configuration
Centralized app name management for easy rebranding via ENV variable
"""
import os
from typing import Optional

# Get app name from environment, default to Enliko
_APP_NAME: str = os.getenv("APP_NAME", "Enliko")

# Derived names
_APP_DISPLAY_NAME: str = f"{_APP_NAME} Trading"
_APP_TERMINAL_NAME: str = f"{_APP_NAME} Trading Terminal"
_APP_BOT_NAME: str = f"{_APP_NAME} Trading Bot"
_APP_BUNDLE_PREFIX: str = f"io.{_APP_NAME.lower()}"


def get_app_name() -> str:
    """Get the base app name (e.g., 'Enliko')"""
    return _APP_NAME


def get_display_name() -> str:
    """Get the display name (e.g., 'Enliko Trading')"""
    return _APP_DISPLAY_NAME


def get_terminal_name() -> str:
    """Get the terminal name (e.g., 'Enliko Trading Terminal')"""
    return _APP_TERMINAL_NAME


def get_bot_name() -> str:
    """Get the bot name (e.g., 'Enliko Trading Bot')"""
    return _APP_BOT_NAME


def get_bundle_prefix() -> str:
    """Get the bundle prefix (e.g., 'io.enliko')"""
    return _APP_BUNDLE_PREFIX


def format_text(text: str, app_name: Optional[str] = None) -> str:
    """
    Replace {APP_NAME} placeholder in text with actual app name.
    Also handles legacy 'Enliko' replacements if app_name is different.
    
    Args:
        text: Text with {APP_NAME} placeholder or hardcoded 'Enliko'
        app_name: Override app name (optional)
    
    Returns:
        Text with app name substituted
    """
    name = app_name or _APP_NAME
    
    # Replace placeholders
    result = text.replace("{APP_NAME}", name)
    result = result.replace("{app_name}", name.lower())
    result = result.replace("{APP_DISPLAY_NAME}", f"{name} Trading")
    result = result.replace("{APP_TERMINAL_NAME}", f"{name} Trading Terminal")
    
    return result


def get_branding_info() -> dict:
    """Get all branding information as a dictionary"""
    return {
        "name": _APP_NAME,
        "display_name": _APP_DISPLAY_NAME,
        "terminal_name": _APP_TERMINAL_NAME,
        "bot_name": _APP_BOT_NAME,
        "bundle_prefix": _APP_BUNDLE_PREFIX,
    }


# Convenience exports
APP_NAME = _APP_NAME
APP_DISPLAY_NAME = _APP_DISPLAY_NAME
APP_TERMINAL_NAME = _APP_TERMINAL_NAME
APP_BOT_NAME = _APP_BOT_NAME
APP_BUNDLE_PREFIX = _APP_BUNDLE_PREFIX
