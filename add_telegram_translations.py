#!/usr/bin/env python3
"""Add Telegram 2FA translations to all languages in LocalizationManager.swift"""

import re

# Translations for Telegram 2FA Login by language
TELEGRAM_2FA_TRANSLATIONS = {
    # Ukrainian already added manually
    
    # German
    "de": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "Mit Telegram anmelden",
        "auth_telegram_login_subtitle": "Geben Sie Ihren Telegram-Benutzernamen ein, um eine Anmeldebestätigung zu erhalten",
        "auth_send_confirmation": "Bestätigung senden",
        "auth_telegram_hint": "Wir senden Ihnen eine Nachricht in Telegram zur Bestätigung",
        "auth_confirm_in_telegram": "In Telegram bestätigen",
        "auth_waiting_confirmation": "Warte auf Bestätigung",
        "auth_check_telegram": "Öffnen Sie Telegram und tippen Sie auf 'Anmeldung bestätigen'",
        "auth_expires_in_5_min": "Anfrage läuft in 5 Minuten ab",
        "auth_login_rejected": "Anmeldung abgelehnt",
        "auth_request_expired": "Anfrage abgelaufen. Bitte versuchen Sie es erneut.",
        "auth_unknown_error": "Unbekannter Fehler aufgetreten",
        "auth_telegram_option_hint": "Nutzen Sie Telegram, wenn Sie bereits ein Bot-Konto haben",
''',
    
    # Spanish
    "es": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "Iniciar sesión con Telegram",
        "auth_telegram_login_subtitle": "Ingrese su nombre de usuario de Telegram para recibir una confirmación de inicio de sesión",
        "auth_send_confirmation": "Enviar confirmación",
        "auth_telegram_hint": "Le enviaremos un mensaje en Telegram para confirmar",
        "auth_confirm_in_telegram": "Confirmar en Telegram",
        "auth_waiting_confirmation": "Esperando confirmación",
        "auth_check_telegram": "Abra Telegram y toque 'Confirmar inicio de sesión'",
        "auth_expires_in_5_min": "La solicitud expira en 5 minutos",
        "auth_login_rejected": "Inicio de sesión rechazado",
        "auth_request_expired": "Solicitud expirada. Por favor, inténtelo de nuevo.",
        "auth_unknown_error": "Error desconocido",
        "auth_telegram_option_hint": "Use Telegram si ya tiene una cuenta en el bot",
''',
    
    # French
    "fr": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "Se connecter avec Telegram",
        "auth_telegram_login_subtitle": "Entrez votre nom d'utilisateur Telegram pour recevoir une confirmation de connexion",
        "auth_send_confirmation": "Envoyer la confirmation",
        "auth_telegram_hint": "Nous vous enverrons un message sur Telegram pour confirmer",
        "auth_confirm_in_telegram": "Confirmer sur Telegram",
        "auth_waiting_confirmation": "En attente de confirmation",
        "auth_check_telegram": "Ouvrez Telegram et appuyez sur 'Confirmer la connexion'",
        "auth_expires_in_5_min": "La demande expire dans 5 minutes",
        "auth_login_rejected": "Connexion rejetée",
        "auth_request_expired": "Demande expirée. Veuillez réessayer.",
        "auth_unknown_error": "Erreur inconnue",
        "auth_telegram_option_hint": "Utilisez Telegram si vous avez déjà un compte bot",
''',
    
    # Italian
    "it": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "Accedi con Telegram",
        "auth_telegram_login_subtitle": "Inserisci il tuo username Telegram per ricevere una conferma di accesso",
        "auth_send_confirmation": "Invia conferma",
        "auth_telegram_hint": "Ti invieremo un messaggio su Telegram per confermare",
        "auth_confirm_in_telegram": "Conferma su Telegram",
        "auth_waiting_confirmation": "In attesa di conferma",
        "auth_check_telegram": "Apri Telegram e tocca 'Conferma accesso'",
        "auth_expires_in_5_min": "La richiesta scade tra 5 minuti",
        "auth_login_rejected": "Accesso rifiutato",
        "auth_request_expired": "Richiesta scaduta. Riprova.",
        "auth_unknown_error": "Errore sconosciuto",
        "auth_telegram_option_hint": "Usa Telegram se hai già un account bot",
''',
    
    # Japanese
    "ja": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "Telegramでログイン",
        "auth_telegram_login_subtitle": "Telegramユーザー名を入力してログイン確認を受け取ります",
        "auth_send_confirmation": "確認を送信",
        "auth_telegram_hint": "Telegramで確認メッセージをお送りします",
        "auth_confirm_in_telegram": "Telegramで確認",
        "auth_waiting_confirmation": "確認を待っています",
        "auth_check_telegram": "Telegramを開いて「ログインを確認」をタップしてください",
        "auth_expires_in_5_min": "リクエストは5分で期限切れになります",
        "auth_login_rejected": "ログインが拒否されました",
        "auth_request_expired": "リクエストが期限切れです。再試行してください。",
        "auth_unknown_error": "不明なエラー",
        "auth_telegram_option_hint": "すでにボットアカウントをお持ちの場合はTelegramを使用してください",
''',
    
    # Chinese
    "zh": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "使用Telegram登录",
        "auth_telegram_login_subtitle": "输入您的Telegram用户名以接收登录确认",
        "auth_send_confirmation": "发送确认",
        "auth_telegram_hint": "我们将通过Telegram向您发送消息进行确认",
        "auth_confirm_in_telegram": "在Telegram中确认",
        "auth_waiting_confirmation": "等待确认",
        "auth_check_telegram": "打开Telegram并点击"确认登录"",
        "auth_expires_in_5_min": "请求将在5分钟后过期",
        "auth_login_rejected": "登录被拒绝",
        "auth_request_expired": "请求已过期。请重试。",
        "auth_unknown_error": "未知错误",
        "auth_telegram_option_hint": "如果您已有机器人账户，请使用Telegram",
''',
    
    # Arabic
    "ar": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "تسجيل الدخول عبر تيليجرام",
        "auth_telegram_login_subtitle": "أدخل اسم المستخدم الخاص بك على تيليجرام لتلقي تأكيد تسجيل الدخول",
        "auth_send_confirmation": "إرسال التأكيد",
        "auth_telegram_hint": "سنرسل لك رسالة على تيليجرام للتأكيد",
        "auth_confirm_in_telegram": "التأكيد في تيليجرام",
        "auth_waiting_confirmation": "في انتظار التأكيد",
        "auth_check_telegram": "افتح تيليجرام واضغط على 'تأكيد تسجيل الدخول'",
        "auth_expires_in_5_min": "تنتهي صلاحية الطلب خلال 5 دقائق",
        "auth_login_rejected": "تم رفض تسجيل الدخول",
        "auth_request_expired": "انتهت صلاحية الطلب. يرجى المحاولة مرة أخرى.",
        "auth_unknown_error": "خطأ غير معروف",
        "auth_telegram_option_hint": "استخدم تيليجرام إذا كان لديك حساب في البوت",
''',
    
    # Hebrew
    "he": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "התחברות עם Telegram",
        "auth_telegram_login_subtitle": "הזן את שם המשתמש שלך ב-Telegram כדי לקבל אישור התחברות",
        "auth_send_confirmation": "שלח אישור",
        "auth_telegram_hint": "נשלח לך הודעה ב-Telegram לאישור",
        "auth_confirm_in_telegram": "אשר ב-Telegram",
        "auth_waiting_confirmation": "ממתין לאישור",
        "auth_check_telegram": "פתח את Telegram ולחץ על 'אשר התחברות'",
        "auth_expires_in_5_min": "הבקשה תפוג בעוד 5 דקות",
        "auth_login_rejected": "ההתחברות נדחתה",
        "auth_request_expired": "הבקשה פגה. נסה שוב.",
        "auth_unknown_error": "שגיאה לא ידועה",
        "auth_telegram_option_hint": "השתמש ב-Telegram אם יש לך כבר חשבון בבוט",
''',
    
    # Polish
    "pl": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "Zaloguj przez Telegram",
        "auth_telegram_login_subtitle": "Wprowadź swoją nazwę użytkownika Telegram, aby otrzymać potwierdzenie logowania",
        "auth_send_confirmation": "Wyślij potwierdzenie",
        "auth_telegram_hint": "Wyślemy Ci wiadomość w Telegramie do potwierdzenia",
        "auth_confirm_in_telegram": "Potwierdź w Telegramie",
        "auth_waiting_confirmation": "Oczekiwanie na potwierdzenie",
        "auth_check_telegram": "Otwórz Telegram i kliknij 'Potwierdź logowanie'",
        "auth_expires_in_5_min": "Żądanie wygasa za 5 minut",
        "auth_login_rejected": "Logowanie odrzucone",
        "auth_request_expired": "Żądanie wygasło. Spróbuj ponownie.",
        "auth_unknown_error": "Nieznany błąd",
        "auth_telegram_option_hint": "Użyj Telegrama, jeśli masz już konto w bocie",
''',
    
    # Czech
    "cs": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "Přihlásit se přes Telegram",
        "auth_telegram_login_subtitle": "Zadejte své uživatelské jméno Telegram pro přijetí potvrzení přihlášení",
        "auth_send_confirmation": "Odeslat potvrzení",
        "auth_telegram_hint": "Pošleme vám zprávu v Telegramu k potvrzení",
        "auth_confirm_in_telegram": "Potvrdit v Telegramu",
        "auth_waiting_confirmation": "Čekání na potvrzení",
        "auth_check_telegram": "Otevřete Telegram a klepněte na 'Potvrdit přihlášení'",
        "auth_expires_in_5_min": "Požadavek vyprší za 5 minut",
        "auth_login_rejected": "Přihlášení zamítnuto",
        "auth_request_expired": "Požadavek vypršel. Zkuste to znovu.",
        "auth_unknown_error": "Neznámá chyba",
        "auth_telegram_option_hint": "Použijte Telegram, pokud již máte účet v botovi",
''',
    
    # Lithuanian
    "lt": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "Prisijungti per Telegram",
        "auth_telegram_login_subtitle": "Įveskite savo Telegram vartotojo vardą, kad gautumėte prisijungimo patvirtinimą",
        "auth_send_confirmation": "Siųsti patvirtinimą",
        "auth_telegram_hint": "Telegram atsiųsime jums pranešimą patvirtinimui",
        "auth_confirm_in_telegram": "Patvirtinti Telegram",
        "auth_waiting_confirmation": "Laukiama patvirtinimo",
        "auth_check_telegram": "Atidarykite Telegram ir bakstelėkite 'Patvirtinti prisijungimą'",
        "auth_expires_in_5_min": "Užklausa baigia galioti po 5 minučių",
        "auth_login_rejected": "Prisijungimas atmestas",
        "auth_request_expired": "Užklausa pasibaigė. Bandykite dar kartą.",
        "auth_unknown_error": "Nežinoma klaida",
        "auth_telegram_option_hint": "Naudokite Telegram, jei jau turite paskyrą bote",
''',
    
    # Albanian
    "sq": '''
        // Telegram 2FA Login
        "auth_telegram_login_title": "Hyr me Telegram",
        "auth_telegram_login_subtitle": "Fut emrin tënd të përdoruesit në Telegram për të marrë konfirmimin e hyrjes",
        "auth_send_confirmation": "Dërgo konfirmimin",
        "auth_telegram_hint": "Do t'ju dërgojmë një mesazh në Telegram për konfirmim",
        "auth_confirm_in_telegram": "Konfirmo në Telegram",
        "auth_waiting_confirmation": "Duke pritur konfirmimin",
        "auth_check_telegram": "Hap Telegram dhe kliko 'Konfirmo hyrjen'",
        "auth_expires_in_5_min": "Kërkesa skadon për 5 minuta",
        "auth_login_rejected": "Hyrja u refuzua",
        "auth_request_expired": "Kërkesa skadoi. Provo përsëri.",
        "auth_unknown_error": "Gabim i panjohur",
        "auth_telegram_option_hint": "Përdor Telegram nëse ke tashmë llogari në bot",
''',
}

def add_translations():
    """Add Telegram 2FA translations to LocalizationManager.swift"""
    filepath = '/Users/elcarosam/project/elcarobybitbotv2/ios/EnlikoTrading/EnlikoTrading/Services/LocalizationManager.swift'
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find each language section and add translations
    # Pattern: after "auth_register_subtitle" line before the closing ] }
    
    for lang, translations in TELEGRAM_2FA_TRANSLATIONS.items():
        # Find the section for this language
        # We need to find a unique marker in each language section
        
        if lang == "de":
            # German - insert after "orders_empty": "Keine Orders",
            marker = '"orders_empty": "Keine Orders",'
            if marker in content and "auth_telegram_login_title" not in content.split(marker)[1].split("] }")[0]:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
        
        elif lang == "es":
            # Spanish - find a unique marker
            marker = '"error_field_required": "%@ es obligatorio.",'
            if marker in content:
                # Find the end of Spanish section before next static var
                content = content.replace(
                    marker,
                    marker + translations
                )
                print(f"Added translations for {lang}")
        
        elif lang == "fr":
            # French
            marker = '"error_field_required": "%@ est requis.",'
            if marker in content:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
        
        elif lang == "it":
            marker = '"error_field_required": "%@ è obbligatorio.",'
            if marker in content:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
        
        elif lang == "ja":
            marker = '"error_field_required": "%@は必須です。",'
            if marker in content:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
        
        elif lang == "zh":
            marker = '"error_field_required": "%@是必填项。",'
            if marker in content:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
        
        elif lang == "ar":
            marker = '"error_field_required": "%@ مطلوب.",'
            if marker in content:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
        
        elif lang == "he":
            marker = '"error_field_required": "%@ נדרש.",'
            if marker in content:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
        
        elif lang == "pl":
            marker = '"error_field_required": "%@ jest wymagane.",'
            if marker in content:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
        
        elif lang == "cs":
            marker = '"error_field_required": "%@ je vyžadováno.",'
            if marker in content:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
        
        elif lang == "lt":
            marker = '"error_field_required": "%@ yra privalomas.",'
            if marker in content:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
        
        elif lang == "sq":
            marker = '"error_field_required": "%@ është e detyrueshme.",'
            if marker in content:
                content = content.replace(marker, marker + translations)
                print(f"Added translations for {lang}")
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print("Done!")

if __name__ == "__main__":
    add_translations()
