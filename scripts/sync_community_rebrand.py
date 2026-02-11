#!/usr/bin/env python3
"""
Sync Community Rebrand to All 13 Non-EN/RU Language Files
=========================================================
Replaces commercial/marketing subscription keys with non-commercial community language.
Also adds any missing keys from EN as English fallback.

Languages: de, es, fr, it, uk, ja, zh, ar, he, pl, cs, lt, sq
"""

import os
import re
import sys

TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "translations")

# Target languages (EN and RU already done)
TARGET_LANGS = ["de", "es", "fr", "it", "uk", "ja", "zh", "ar", "he", "pl", "cs", "lt", "sq"]

# ============================================================
# Keys that need full replacement with localized non-commercial text
# Key → dict of {lang: new_value}
# For languages without specific translation, EN value is used
# ============================================================

# Common button replacements (short strings, translate per language)
BUTTON_REPLACEMENTS = {
    "button_subscribe": {
        "de": "'🤝 UNTERSTÜTZEN'",
        "es": "'🤝 APOYAR'",
        "fr": "'🤝 SOUTENIR'",
        "it": "'🤝 SOSTENERE'",
        "uk": "'🤝 ПІДТРИМАТИ'",
        "ja": "'🤝 サポート'",
        "zh": "'🤝 支持我们'",
        "ar": "'🤝 ادعمنا'",
        "he": "'🤝 תמכו בנו'",
        "pl": "'🤝 WSPIERAJ'",
        "cs": "'🤝 PODPOŘIT'",
        "lt": "'🤝 PALAIKYTI'",
        "sq": "'🤝 MBËSHTETJE'",
    },
    "btn_premium": {
        "de": "'🤝 Patron'",
        "es": "'🤝 Patrón'",
        "fr": "'🤝 Patron'",
        "it": "'🤝 Patrono'",
        "uk": "'🤝 Патрон'",
        "ja": "'🤝 パトロン'",
        "zh": "'🤝 赞助者'",
        "ar": "'🤝 داعم رئيسي'",
        "he": "'🤝 פטרון'",
        "pl": "'🤝 Patron'",
        "cs": "'🤝 Patron'",
        "lt": "'🤝 Globėjas'",
        "sq": "'🤝 Patron'",
    },
    "btn_basic": {
        "de": "'💚 Unterstützer'",
        "es": "'💚 Colaborador'",
        "fr": "'💚 Soutien'",
        "it": "'💚 Sostenitore'",
        "uk": "'💚 Помічник'",
        "ja": "'💚 サポーター'",
        "zh": "'💚 支持者'",
        "ar": "'💚 داعم'",
        "he": "'💚 תומך'",
        "pl": "'💚 Wspieracz'",
        "cs": "'💚 Podporovatel'",
        "lt": "'💚 Rėmėjas'",
        "sq": "'💚 Mbështetës'",
    },
    "btn_trial": {
        "de": "'🆓 Entdecker (Kostenlos)'",
        "es": "'🆓 Explorador (Gratis)'",
        "fr": "'🆓 Explorateur (Gratuit)'",
        "it": "'🆓 Esploratore (Gratis)'",
        "uk": "'🆓 Дослідник (Безкоштовно)'",
        "ja": "'🆓 お試し (無料)'",
        "zh": "'🆓 体验 (免费)'",
        "ar": "'🆓 استكشاف (مجاني)'",
        "he": "'🆓 חוקר (חינם)'",
        "pl": "'🆓 Odkrywca (Darmowy)'",
        "cs": "'🆓 Průzkumník (Zdarma)'",
        "lt": "'🆓 Tyrinėtojas (Nemokama)'",
        "sq": "'🆓 Eksplorues (Falas)'",
    },
    "btn_enter_promo": {
        "de": "'🎟 Einladungscode'",
        "es": "'🎟 Código de invitación'",
        "fr": "'🎟 Code d\\'invitation'",
        "it": "'🎟 Codice invito'",
        "uk": "'🎟 Код запрошення'",
        "ja": "'🎟 招待コード'",
        "zh": "'🎟 邀请码'",
        "ar": "'🎟 رمز الدعوة'",
        "he": "'🎟 קוד הזמנה'",
        "pl": "'🎟 Kod zaproszenia'",
        "cs": "'🎟 Kód pozvánky'",
        "lt": "'🎟 Kvietimo kodas'",
        "sq": "'🎟 Kodi ftesës'",
    },
    "btn_my_subscription": {
        "de": "'📋 Meine Mitgliedschaft'",
        "es": "'📋 Mi membresía'",
        "fr": "'📋 Mon adhésion'",
        "it": "'📋 La mia adesione'",
        "uk": "'📋 Моя участь'",
        "ja": "'📋 メンバーシップ'",
        "zh": "'📋 我的会员'",
        "ar": "'📋 عضويتي'",
        "he": "'📋 החברות שלי'",
        "pl": "'📋 Moje członkostwo'",
        "cs": "'📋 Mé členství'",
        "lt": "'📋 Mano narystė'",
        "sq": "'📋 Anëtarësia ime'",
    },
    "btn_pay_elc": {
        "_all": "'◈ ELC'",
    },
    "btn_verify_ton": {
        "de": "'✅ Beitrag prüfen'",
        "es": "'✅ Verificar contribución'",
        "fr": "'✅ Vérifier contribution'",
        "it": "'✅ Verifica contributo'",
        "uk": "'✅ Перевірити внесок'",
        "ja": "'✅ 確認する'",
        "zh": "'✅ 验证贡献'",
        "ar": "'✅ تحقق من المساهمة'",
        "he": "'✅ אמת תרומה'",
        "pl": "'✅ Zweryfikuj wpłatę'",
        "cs": "'✅ Ověřit příspěvek'",
        "lt": "'✅ Patikrinti įnašą'",
        "sq": "'✅ Verifiko kontributin'",
    },
}

# Multi-line keys that need full replacement (same for all non-EN/RU languages → use EN text)
MULTILINE_EN_FALLBACK_KEYS = [
    "no_license",
    "no_license_trading",
    "license_required",
    "trial_demo_only",
    "basic_strategy_limit",
    "basic_bybit_only",
    "subscribe_menu_header",
    "subscribe_menu_info",
    "premium_title",
    "premium_desc",
    "basic_title",
    "basic_desc",
    "trial_title",
    "trial_desc",
    "trial_activate",
    "trial_already_used",
    "trial_activated",
    "payment_select_method",
    "payment_elc_title",
    "payment_elc_desc",
    "payment_ton_title",
    "payment_ton_desc",
    "payment_processing",
    "payment_success",
    "payment_failed",
    "my_subscription_header",
    "my_subscription_active",
    "my_subscription_none",
    "my_subscription_history",
    "subscription_expiring_soon",
    "promo_enter",
    "promo_success",
    "promo_invalid",
    "promo_expired",
    "promo_used",
    "promo_already_used",
    "admin_license_menu",
    "admin_btn_grant_license",
    "admin_btn_view_licenses",
    "admin_btn_create_promo",
    "admin_btn_view_promos",
    "admin_btn_expiring_soon",
    "admin_grant_select_type",
    "admin_grant_select_period",
    "admin_grant_enter_user",
    "admin_license_granted",
    "admin_license_extended",
    "admin_license_revoked",
    "admin_promo_created",
    "crypto_select_currency",
    "crypto_payment_invoice",
    "creating_payment",
    "payment_creation_failed",
    "payment_error",
    "crypto_payment_instructions",
    "crypto_payment_error",
    "crypto_payment_confirmed",
    "crypto_payment_confirming",
    "crypto_payment_expired",
    "crypto_payment_pending",
]

# EN values for multi-line keys (read from en.py at runtime)
EN_TEXTS = {}


def load_en_texts():
    """Load EN translation values."""
    en_path = os.path.join(TRANSLATIONS_DIR, "en.py")
    namespace = {}
    with open(en_path, "r", encoding="utf-8") as f:
        exec(f.read(), namespace)
    return namespace.get("TEXTS", {})


def load_lang_file(lang):
    """Load a language file as raw text."""
    path = os.path.join(TRANSLATIONS_DIR, f"{lang}.py")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_lang_file(lang, content):
    """Save a language file."""
    path = os.path.join(TRANSLATIONS_DIR, f"{lang}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def replace_key_value(content, key, new_value_str):
    """
    Replace a key's value in a Python dict string.
    Handles both single-line and multi-line (triple-quoted) values.
    """
    # Pattern: 'key': <value>,  where value can be single/triple quoted or parenthesized
    # We need to find the key and replace everything until the next key or closing brace
    
    # Find the key position
    patterns = [
        rf"(    '{re.escape(key)}':\s*)",   # 'key':
        rf'(    "{re.escape(key)}":\s*)',   # "key":
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            start = match.start()
            prefix = match.group(1)
            after_key = content[match.end():]
            
            # Find the end of the value - look for next key at same indent level
            # or closing brace
            depth = 0
            in_string = False
            string_char = None
            triple = False
            i = 0
            found_end = False
            
            while i < len(after_key):
                c = after_key[i]
                
                if not in_string:
                    if after_key[i:i+3] in ("'''", '"""'):
                        in_string = True
                        string_char = after_key[i:i+3]
                        triple = True
                        i += 3
                        continue
                    elif c in ("'", '"') and (i == 0 or after_key[i-1] != '\\'):
                        in_string = True
                        string_char = c
                        triple = False
                        i += 1
                        continue
                    elif c == '(':
                        depth += 1
                    elif c == ')':
                        depth -= 1
                    elif c == '\n' and depth == 0:
                        # Check if next non-space content is a new key or comment or close brace
                        rest = after_key[i+1:]
                        stripped = rest.lstrip()
                        if (stripped.startswith("'") or stripped.startswith('"') or
                            stripped.startswith('#') or stripped.startswith('}') or
                            stripped.startswith('\n')):
                            # Found end of value
                            found_end = True
                            end_pos = i + 1
                            break
                else:
                    if triple:
                        if after_key[i:i+3] == string_char:
                            in_string = False
                            i += 3
                            continue
                    else:
                        if c == string_char and (i == 0 or after_key[i-1] != '\\'):
                            in_string = False
                
                i += 1
            
            if not found_end:
                end_pos = len(after_key)
            
            # Build replacement
            old_value = after_key[:end_pos]
            new_content = content[:start] + prefix + new_value_str + "\n" + content[match.end() + end_pos:]
            return new_content
    
    return content


def format_value_for_py(value):
    """Format a Python value for insertion into source code."""
    if isinstance(value, str):
        # Check if it contains newlines
        if '\n' in value:
            # Use triple quotes with parentheses for multi-line
            escaped = value.replace("\\", "\\\\").replace("'", "\\'")
            lines = escaped.split('\n')
            parts = []
            for line in lines:
                parts.append(f"        '{line}\\n'")
            # Last line without \n
            if parts:
                parts[-1] = parts[-1].replace("\\n'", "'")
            return "(\n" + "\n".join(parts) + "\n    ),"
        else:
            escaped = value.replace("\\", "\\\\").replace("'", "\\'")
            return f"'{escaped}',"
    return repr(value) + ","


def process_language(lang, en_texts):
    """Process a single language file."""
    content = load_lang_file(lang)
    changes = 0
    
    # 1. Replace button strings
    for key, lang_values in BUTTON_REPLACEMENTS.items():
        if "_all" in lang_values:
            new_val = lang_values["_all"]
        elif lang in lang_values:
            new_val = lang_values[lang]
        else:
            # Use EN value
            en_val = en_texts.get(key, "")
            new_val = repr(en_val)
        
        # Find and replace the key value  
        pattern = rf"(    '{re.escape(key)}':\s*)([^\n]*?)(\s*,?\s*\n)"
        match = re.search(pattern, content)
        if match:
            old_line = match.group(0)
            new_line = f"    '{key}': {new_val},\n"
            if old_line.strip() != new_line.strip():
                content = content.replace(old_line, new_line)
                changes += 1
    
    # 2. Replace multi-line subscription/payment keys with EN values
    for key in MULTILINE_EN_FALLBACK_KEYS:
        en_val = en_texts.get(key)
        if en_val is None:
            continue
        
        # Check if key exists in file
        if f"'{key}'" in content or f'"{key}"' in content:
            new_val_str = format_value_for_py(en_val)
            result = replace_key_value(content, key, new_val_str)
            if result != content:
                content = result
                changes += 1
    
    # 3. Replace simple single-line keys from the subscription section  
    simple_replacements = {
        "premium_1m": en_texts.get("premium_1m", "🤝 1 Month — {price} ELC"),
        "premium_3m": en_texts.get("premium_3m", "🤝 3 Months — {price} ELC"),
        "premium_6m": en_texts.get("premium_6m", "🤝 6 Months — {price} ELC"),
        "premium_12m": en_texts.get("premium_12m", "🤝 12 Months — {price} ELC"),
        "basic_1m": en_texts.get("basic_1m", "💚 1 Month — {price} ELC"),
    }
    
    for key, en_val in simple_replacements.items():
        pattern = rf"(    '{re.escape(key)}':\s*)([^\n]*?)(\s*\n)"
        match = re.search(pattern, content)
        if match:
            escaped = en_val.replace("'", "\\'")
            new_line = f"    '{key}': '{escaped}',\n"
            content = content[:match.start()] + new_line + content[match.end():]
            changes += 1
    
    if changes > 0:
        save_lang_file(lang, content)
    
    return changes


def main():
    print("=" * 60)
    print("  Enliko Community Rebrand - Translation Sync")
    print("=" * 60)
    print()
    
    # Load EN reference
    print("Loading EN reference translations...")
    en_texts = load_en_texts()
    print(f"  EN has {len(en_texts)} keys")
    print()
    
    total_changes = 0
    
    for lang in TARGET_LANGS:
        lang_path = os.path.join(TRANSLATIONS_DIR, f"{lang}.py")
        if not os.path.exists(lang_path):
            print(f"  ⚠️  {lang}.py not found, skipping")
            continue
        
        try:
            changes = process_language(lang, en_texts)
            total_changes += changes
            emoji = "✅" if changes > 0 else "⏭️ "
            print(f"  {emoji} {lang}.py — {changes} keys updated")
        except Exception as e:
            print(f"  ❌ {lang}.py — ERROR: {e}")
    
    print()
    print(f"Total: {total_changes} changes across {len(TARGET_LANGS)} languages")
    print()
    print("Done! Review changes with: git diff translations/")


if __name__ == "__main__":
    main()
