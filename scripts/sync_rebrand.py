#!/usr/bin/env python3
"""
Sync Community Rebrand — Replace subscription/payment keys in all 13 languages.
Uses the safe approach: load as module, replace keys, write back preserving structure.
"""

import os
import re
import sys

TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "translations")

TARGET_LANGS = ["de", "es", "fr", "it", "uk", "ja", "zh", "ar", "he", "pl", "cs", "lt", "sq"]

# Per-language button translations  
LOCALIZED_BUTTONS = {
    "button_subscribe": {
        "de": "🤝 UNTERSTÜTZEN", "es": "🤝 APOYAR", "fr": "🤝 SOUTENIR",
        "it": "🤝 SOSTENERE", "uk": "🤝 ПІДТРИМАТИ", "ja": "🤝 サポート",
        "zh": "🤝 支持我们", "ar": "🤝 ادعمنا", "he": "🤝 תמכו בנו",
        "pl": "🤝 WSPIERAJ", "cs": "🤝 PODPOŘIT", "lt": "🤝 PALAIKYTI",
        "sq": "🤝 MBËSHTETJE",
    },
    "btn_premium": {
        "de": "🤝 Patron", "es": "🤝 Patrón", "fr": "🤝 Patron",
        "it": "🤝 Patrono", "uk": "🤝 Патрон", "ja": "🤝 パトロン",
        "zh": "🤝 赞助者", "ar": "🤝 داعم رئيسي", "he": "🤝 פטרון",
        "pl": "🤝 Patron", "cs": "🤝 Patron", "lt": "🤝 Globėjas",
        "sq": "🤝 Patron",
    },
    "btn_basic": {
        "de": "💚 Unterstützer", "es": "💚 Colaborador", "fr": "💚 Soutien",
        "it": "💚 Sostenitore", "uk": "💚 Помічник", "ja": "💚 サポーター",
        "zh": "💚 支持者", "ar": "💚 داعم", "he": "💚 תומך",
        "pl": "💚 Wspieracz", "cs": "💚 Podporovatel", "lt": "💚 Rėmėjas",
        "sq": "💚 Mbështetës",
    },
    "btn_trial": {
        "de": "🆓 Entdecker (Kostenlos)", "es": "🆓 Explorador (Gratis)",
        "fr": "🆓 Explorateur (Gratuit)", "it": "🆓 Esploratore (Gratis)",
        "uk": "🆓 Дослідник (Безкоштовно)", "ja": "🆓 お試し (無料)",
        "zh": "🆓 体验 (免费)", "ar": "🆓 استكشاف (مجاني)", "he": "🆓 חוקר (חינם)",
        "pl": "🆓 Odkrywca (Darmowy)", "cs": "🆓 Průzkumník (Zdarma)",
        "lt": "🆓 Tyrinėtojas (Nemokama)", "sq": "🆓 Eksplorues (Falas)",
    },
    "btn_enter_promo": {
        "de": "🎟 Einladungscode", "es": "🎟 Código de invitación",
        "fr": "🎟 Code d'invitation", "it": "🎟 Codice invito",
        "uk": "🎟 Код запрошення", "ja": "🎟 招待コード",
        "zh": "🎟 邀请码", "ar": "🎟 رمز الدعوة", "he": "🎟 קוד הזמנה",
        "pl": "🎟 Kod zaproszenia", "cs": "🎟 Kód pozvánky",
        "lt": "🎟 Kvietimo kodas", "sq": "🎟 Kodi ftesës",
    },
    "btn_my_subscription": {
        "de": "📋 Meine Mitgliedschaft", "es": "📋 Mi membresía",
        "fr": "📋 Mon adhésion", "it": "📋 La mia adesione",
        "uk": "📋 Моя участь", "ja": "📋 メンバーシップ",
        "zh": "📋 我的会员", "ar": "📋 عضويتي", "he": "📋 החברות שלי",
        "pl": "📋 Moje członkostwo", "cs": "📋 Mé členství",
        "lt": "📋 Mano narystė", "sq": "📋 Anëtarësia ime",
    },
}

# Keys that get EN fallback value (same for all languages) 
EN_FALLBACK_SIMPLE = {
    "btn_pay_elc": "◈ ELC",
    "premium_title": "🤝 *Patron Membership*",
    "basic_title": "💚 *Supporter Membership*",
    "trial_title": "🆓 *Explorer Access — 14 Days*",
    "trial_activate": "🆓 Start Exploring",
    "premium_1m": "🤝 1 Month — {price} ELC",
    "premium_3m": "🤝 3 Months — {price} ELC",
    "premium_6m": "🤝 6 Months — {price} ELC",
    "premium_12m": "🤝 12 Months — {price} ELC",
    "basic_1m": "💚 1 Month — {price} ELC",
    "payment_processing": "⏳ ...",
    "btn_check_again": "🔄 Check",
}


def replace_single_line_key(content, key, new_value):
    """Replace a single-line 'key': 'old value', with new value."""
    escaped_key = re.escape(key)
    pattern = rf"    '{escaped_key}':\s*('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"),?\s*\n"
    
    match = re.search(pattern, content)
    if match:
        escaped_val = new_value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        replacement = f"    '{key}': '{escaped_val}',\n"
        new_content = content[:match.start()] + replacement + content[match.end():]
        return new_content, True
    return content, False


def replace_multiline_key(content, key, new_text):
    """
    Replace a multi-line key value (triple-quoted or parenthesized).
    Returns (new_content, was_replaced).
    """
    escaped_key = re.escape(key)

    # Try triple-quoted strings first: 'key': '''...''',
    pattern_triple = rf"(    '{escaped_key}':\s*)('''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\")(,?\s*\n)"
    match = re.search(pattern_triple, content)
    if match:
        # Always use escaped \n in single-quoted strings for safety
        escaped_val = new_text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        replacement = f"    '{key}': '{escaped_val}',\n"
        new_content = content[:match.start()] + replacement + content[match.end():]
        return new_content, True

    # Try parenthesized strings: 'key': (\n '...' \n '...' \n),
    pattern_paren = rf"    '{escaped_key}':\s*\([\s\S]*?\),?\n"
    match = re.search(pattern_paren, content)
    if match:
        escaped_val = new_text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        replacement = f"    '{key}': '{escaped_val}',\n"
        new_content = content[:match.start()] + replacement + content[match.end():]
        return new_content, True
    
    return content, False


def process_language(lang):
    """Process a single language file."""
    filepath = os.path.join(TRANSLATIONS_DIR, f"{lang}.py")
    if not os.path.exists(filepath):
        return 0, "file not found"
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    changes = 0
    
    # 1. Replace localized button keys
    for key, lang_map in LOCALIZED_BUTTONS.items():
        if lang in lang_map:
            new_content, replaced = replace_single_line_key(content, key, lang_map[lang])
            if replaced:
                content = new_content
                changes += 1
    
    # 2. Replace simple EN-fallback keys
    for key, en_val in EN_FALLBACK_SIMPLE.items():
        new_content, replaced = replace_single_line_key(content, key, en_val)
        if replaced:
            content = new_content
            changes += 1
    
    # 3. Replace critical multi-line subscription marketing text with clean EN versions
    multiline_replacements = {
        "subscribe_menu_header": (
            "🤝 *Support Enliko*\n\n"
            "Your voluntary contribution helps maintain\n"
            "free open-source community tools.\n\n"
            "Choose your support level:"
        ),
        "subscribe_menu_info": "_Select your support level:_",
        "no_license": (
            "🤝 *Community Membership*\n\n"
            "Support our open-source project to access\n"
            "additional community resources.\n\n"
            "👉 /subscribe — Support the project"
        ),
        "no_license_trading": (
            "🤝 *Community Resource*\n\n"
            "This resource is available to community supporters.\n\n"
            "👉 /subscribe — Support the project"
        ),
        "license_required": (
            "🔒 *Supporter Resource*\n\n"
            "This resource requires {required} membership.\n\n"
            "👉 /subscribe — Support the project"
        ),
        "trial_demo_only": (
            "⚠️ *Explorer Access*\n\n"
            "Explorer access is limited to demo environment.\n\n"
            "👉 /subscribe — Become a supporter"
        ),
        "basic_strategy_limit": (
            "⚠️ *Community Tier*\n\n"
            "Available templates: {strategies}\n\n"
            "👉 /subscribe — Upgrade your support"
        ),
        "premium_desc": (
            "*Thank you for supporting our community!*\n\n"
            "As a patron, you receive access to:\n"
            "✅ All community analysis templates\n"
            "✅ Demo & live environments\n"
            "✅ Priority community support\n"
            "✅ ATR risk management tools\n"
            "✅ DCA configuration tools\n"
            "✅ Early access to updates\n\n"
            "⚠️ _Educational tools only. Not financial advice._"
        ),
        "basic_desc": (
            "*Thank you for your support!*\n\n"
            "✅ Demo + live environments\n"
            "✅ Templates: OI, RSI+BB\n"
            "✅ Bybit integration\n"
            "✅ ATR risk management tools\n\n"
            "⚠️ _Educational tools only. Not financial advice._"
        ),
        "trial_desc": (
            "*Explore our community tools:*\n\n"
            "✅ Full demo environment\n"
            "✅ All analysis templates\n"
            "✅ 14 days access\n"
            "✅ No contribution required\n\n"
            "⚠️ _Educational tools only. Not financial advice._"
        ),
        "trial_already_used": "⚠️ Explorer access already used. Consider supporting the project.",
        "trial_activated": (
            "🎉 *Explorer Access Activated!*\n\n"
            "⏰ 14 days of full demo access.\n\n"
            "⚠️ _Educational tools only. Not financial advice._"
        ),
        "payment_select_method": "🤝 *How would you like to contribute?*",
        "payment_success": "🎉 Thank you for your support!\n\n{plan} access activated until {expires}.",
        "payment_failed": "❌ Contribution failed: {error}",
        "my_subscription_header": "📋 *My Membership*",
        "my_subscription_none": "❌ No active membership.\n\nUse /subscribe to support the project.",
        "admin_license_menu": "🤝 *Membership Management*",
        "admin_btn_grant_license": "🎁 Grant Access",
        "admin_btn_view_licenses": "📋 View Members",
        "admin_btn_create_promo": "🎟 Create Invite",
        "admin_btn_view_promos": "📋 View Invites",
        "promo_enter": "🎟 Enter your invite code:",
        "promo_success": "🎉 Invite code applied!\n\n{plan} access for {days} days.",
        "promo_invalid": "❌ Invalid invite code.",
        "promo_expired": "❌ This invite code has expired.",
        "promo_used": "❌ This invite code has already been used.",
        "promo_already_used": "❌ You have already used this invite code.",
    }
    
    for key, new_text in multiline_replacements.items():
        # Try multi-line first, then single-line
        new_content, replaced = replace_multiline_key(content, key, new_text)
        if replaced:
            content = new_content
            changes += 1
        else:
            new_content, replaced = replace_single_line_key(content, key, new_text)
            if replaced:
                content = new_content
                changes += 1
    
    # Save if changed
    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    
    return changes, "ok"


def main():
    print("=" * 60)
    print("  Enliko Community Rebrand — 13 Languages Sync")
    print("=" * 60)
    print()
    
    total = 0
    for lang in TARGET_LANGS:
        try:
            changes, status = process_language(lang)
            total += changes
            if status == "ok":
                emoji = "✅" if changes > 0 else "⏭️ "
                print(f"  {emoji} {lang}.py — {changes} keys updated")
            else:
                print(f"  ⚠️  {lang}.py — {status}")
        except Exception as e:
            print(f"  ❌ {lang}.py — ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nTotal: {total} changes across {len(TARGET_LANGS)} languages")
    print("\nReview: git diff translations/")


if __name__ == "__main__":
    main()
