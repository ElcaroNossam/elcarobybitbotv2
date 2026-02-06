#!/usr/bin/env python3
"""Add missing auth strings to all language objects in Localization.kt"""

import re

file_path = "android/EnlikoTrading/app/src/main/java/io/enliko/trading/util/Localization.kt"

# New strings for each language
translations = {
    "German": {
        "confirmPassword": "Passwort bestätigen",
        "name": "Name",
        "passwordRequirements": "Min 8 Zeichen, Buchstaben und Zahlen",
        "passwordsDoNotMatch": "Passwörter stimmen nicht überein"
    },
    "Spanish": {
        "confirmPassword": "Confirmar contraseña",
        "name": "Nombre",
        "passwordRequirements": "Mín 8 caracteres, letras y números",
        "passwordsDoNotMatch": "Las contraseñas no coinciden"
    },
    "French": {
        "confirmPassword": "Confirmer le mot de passe",
        "name": "Nom",
        "passwordRequirements": "Min 8 caractères, lettres et chiffres",
        "passwordsDoNotMatch": "Les mots de passe ne correspondent pas"
    },
    "Italian": {
        "confirmPassword": "Conferma password",
        "name": "Nome",
        "passwordRequirements": "Min 8 caratteri, lettere e numeri",
        "passwordsDoNotMatch": "Le password non corrispondono"
    },
    "Japanese": {
        "confirmPassword": "パスワード確認",
        "name": "名前",
        "passwordRequirements": "8文字以上、英数字を含む",
        "passwordsDoNotMatch": "パスワードが一致しません"
    },
    "Chinese": {
        "confirmPassword": "确认密码",
        "name": "姓名",
        "passwordRequirements": "至少8个字符，包含字母和数字",
        "passwordsDoNotMatch": "密码不匹配"
    },
    "Arabic": {
        "confirmPassword": "تأكيد كلمة المرور",
        "name": "الاسم",
        "passwordRequirements": "8 أحرف على الأقل، أحرف وأرقام",
        "passwordsDoNotMatch": "كلمات المرور غير متطابقة"
    },
    "Hebrew": {
        "confirmPassword": "אשר סיסמה",
        "name": "שם",
        "passwordRequirements": "מינימום 8 תווים, אותיות ומספרים",
        "passwordsDoNotMatch": "הסיסמאות אינן תואמות"
    },
    "Polish": {
        "confirmPassword": "Potwierdź hasło",
        "name": "Imię",
        "passwordRequirements": "Min 8 znaków, litery i cyfry",
        "passwordsDoNotMatch": "Hasła nie pasują"
    },
    "Czech": {
        "confirmPassword": "Potvrďte heslo",
        "name": "Jméno",
        "passwordRequirements": "Min 8 znaků, písmena a čísla",
        "passwordsDoNotMatch": "Hesla se neshodují"
    },
    "Lithuanian": {
        "confirmPassword": "Patvirtinkite slaptažodį",
        "name": "Vardas",
        "passwordRequirements": "Min 8 simboliai, raidės ir skaičiai",
        "passwordsDoNotMatch": "Slaptažodžiai nesutampa"
    },
    "Albanian": {
        "confirmPassword": "Konfirmo fjalëkalimin",
        "name": "Emri",
        "passwordRequirements": "Min 8 karaktere, shkronja dhe numra",
        "passwordsDoNotMatch": "Fjalëkalimet nuk përputhen"
    }
}

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

for lang_name, strings in translations.items():
    # Find the pattern: override val password = "XXX"\n        override val forgotPassword
    pattern = rf'(object {lang_name} : Strings \{{.*?override val password = "([^"]+)")\n(        override val forgotPassword)'
    
    def replacement(m):
        prefix = m.group(1)
        forgot = m.group(3)
        new_lines = f'''
        override val confirmPassword = "{strings['confirmPassword']}"
        override val name = "{strings['name']}"
        override val passwordRequirements = "{strings['passwordRequirements']}"
        override val passwordsDoNotMatch = "{strings['passwordsDoNotMatch']}"
'''
        return f"{prefix}{new_lines}{forgot}"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    if new_content != content:
        print(f"Updated {lang_name}")
        content = new_content
    else:
        print(f"Pattern not found for {lang_name}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone!")
