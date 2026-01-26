# 📧 Email Setup для Lyxen Trading Platform

## Что уже готово (сделано мной):

✅ **Email Auth API** - `/api/auth/email/*`
- Регистрация с email + password (`/register`)
- Верификация через 6-значный код (`/verify`)
- Логин (`/login`)
- Сброс пароля (`/forgot-password`, `/reset-password`)
- Проверка доступности email (`/check-email/{email}`)
- Гостевой доступ (`/guest`)

✅ **Красивые HTML шаблоны** для писем:
- Verification code с брендингом Lyxen
- Password reset с безопасными инструкциями

✅ **Redis + Memory fallback** для кодов верификации
- Работает в multi-worker режиме

✅ **Безопасность:**
- PBKDF2-SHA256 хеширование паролей
- JWT токены (7 дней)
- Rate limiting (в планах)

---

## 🔧 Что нужно настроить тебе:

### Вариант 1: Gmail (Быстрый старт)

1. **Включи 2FA в Gmail:**
   - Перейди: https://myaccount.google.com/security
   - Включи "2-Step Verification"

2. **Создай App Password:**
   - Перейди: https://myaccount.google.com/apppasswords
   - Выбери "Mail" и "Other (Custom name)" → "Lyxen"
   - Скопируй 16-символьный пароль

3. **Обнови .env на сервере:**
   ```bash
   ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com
   nano /home/ubuntu/project/elcarobybitbotv2/.env
   ```
   
   Замени:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=твой-gmail@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App Password!
   SMTP_FROM=твой-gmail@gmail.com
   SMTP_USE_TLS=true
   ```

4. **Перезапусти сервис:**
   ```bash
   sudo systemctl restart elcaro-bot
   ```

---

### Вариант 2: Resend.com (Рекомендую для продакшена)

**Преимущества:**
- 3000 писем/месяц бесплатно
- Красивые аналитики
- Верифицированный домен = лучше deliverability
- Нет проблем с Gmail rate limits

1. **Регистрация:** https://resend.com

2. **Добавь домен:**
   - Dashboard → Domains → Add Domain
   - Добавь DNS записи (DKIM, SPF, DMARC)
   - Дождись верификации (~5 мин)

3. **Получи API key:**
   - Dashboard → API Keys → Create API Key
   
4. **Обнови .env:**
   ```
   SMTP_HOST=smtp.resend.com
   SMTP_PORT=465
   SMTP_USER=resend
   SMTP_PASSWORD=re_xxxxxxxxxxxx  # API Key
   SMTP_FROM=noreply@lyxen.io     # Твой верифицированный домен!
   SMTP_USE_TLS=false             # Используем SSL на 465
   ```

---

### Вариант 3: SendGrid (Enterprise)

1. **Регистрация:** https://sendgrid.com

2. **Создай API Key:**
   - Settings → API Keys → Create API Key
   - Full Access

3. **Обнови .env:**
   ```
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USER=apikey
   SMTP_PASSWORD=SG.xxxxxxxxxxxx
   SMTP_FROM=noreply@lyxen.io
   SMTP_USE_TLS=true
   ```

---

## 📱 iOS Email Login

Email login в iOS уже работает! Файлы:
- `ios/LyxenTrading/Views/Auth/LoginView.swift` - UI
- `ios/LyxenTrading/Services/AuthManager.swift` - API calls

---

## 🧪 Тестирование

После настройки SMTP, протестируй:

```bash
# На сервере
curl -X POST https://bills-send-prostores-relate.trycloudflare.com/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test1234", "name": "Test User"}'
```

Должен вернуть:
```json
{"success": true, "message": "Verification code sent to your email", "email": "test@example.com"}
```

И на email придёт код!

---

## 🔒 DNS записи для лучшей доставки (опционально)

Добавь в DNS твоего домена:

```
# SPF (разрешает Gmail/Resend отправлять от твоего имени)
TXT @ "v=spf1 include:_spf.google.com include:amazonses.com ~all"

# DMARC (политика аутентификации)  
TXT _dmarc "v=DMARC1; p=none; rua=mailto:admin@lyxen.io"
```

---

## 📊 Endpoints Reference

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/auth/email/register` | POST | Регистрация (отправляет код) |
| `/api/auth/email/verify` | POST | Подтверждение email |
| `/api/auth/email/login` | POST | Вход |
| `/api/auth/email/forgot-password` | POST | Запрос сброса пароля |
| `/api/auth/email/reset-password` | POST | Сброс пароля с кодом |
| `/api/auth/email/guest` | POST | Гостевой токен |
| `/api/auth/email/check-email/{email}` | GET | Проверка доступности |

---

*Последнее обновление: 26 января 2026*
