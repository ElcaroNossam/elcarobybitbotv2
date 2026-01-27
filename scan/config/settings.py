import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: SECRET_KEY must be set in production
_secret_key = os.getenv("DJANGO_SECRET_KEY")
if not _secret_key:
    import warnings
    if os.getenv("DJANGO_DEBUG", "False") != "True":
        raise RuntimeError("DJANGO_SECRET_KEY must be set in production environment")
    # Only use fallback in development
    warnings.warn("DJANGO_SECRET_KEY not set - using insecure development key!", RuntimeWarning)
    _secret_key = "INSECURE-DEV-KEY-DO-NOT-USE-IN-PRODUCTION"
SECRET_KEY = _secret_key

# SECURITY: Default DEBUG to False for production safety
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

# Parse ALLOWED_HOSTS from environment variable (comma-separated)
allowed_hosts_str = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1],elcaro.online,www.elcaro.online")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(",") if host.strip()]

# CSRF trusted origins for POST requests (required for Django 4.0+)
CSRF_TRUSTED_ORIGINS = [
    "https://elcaro.online",
    "https://www.elcaro.online",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Проверяем наличие debug_toolbar ДО определения INSTALLED_APPS
_DEBUG_TOOLBAR_AVAILABLE = False
if DEBUG:
    try:
        import debug_toolbar
        _DEBUG_TOOLBAR_AVAILABLE = True
    except ImportError:
        pass  # Debug toolbar не установлен, пропускаем

# Базовый список приложений
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",
    "accounts",
    "screener",
    "api",
    "alerts",
]

# Django Debug Toolbar для мониторинга производительности (только в DEBUG режиме и если установлен)
# Добавляем в начало списка, чтобы Django загрузил его до других приложений
if _DEBUG_TOOLBAR_AVAILABLE:
    INSTALLED_APPS.insert(0, "debug_toolbar")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",  # Сжатие ответов (10x уменьшение размера JSON)
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # Локализация (базовый)
    "config.middleware.ForceLanguageMiddleware",  # Принудительное определение языка из URL/cookie
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.CSPMiddleware",  # Custom CSP middleware for TradingView
]

# Django Debug Toolbar middleware (только в DEBUG режиме и если установлен)
if _DEBUG_TOOLBAR_AVAILABLE:
    # Добавляем middleware в начало списка (должен быть после SecurityMiddleware)
    MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")

# Content Security Policy is now handled by CSPMiddleware
# This allows unsafe-eval for TradingView widget which requires it

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "cryptoscreener"),
        "USER": os.getenv("DB_USER", "cryptouser"),
        "PASSWORD": os.getenv("DB_PASSWORD", "cryptopass"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        # Оптимизация подключений для высокой нагрузки (16GB RAM, 8 cores)
        "CONN_MAX_AGE": 600,  # Переиспользуем подключения 10 минут (вместо создания новых)
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"  # 30 секунд таймаут для запросов
        },
    }
}

# Cache configuration for API performance optimization
# Используем Redis для кеширования (если доступен), иначе LocMemCache
try:
    import django_redis
    # Используем django-redis если доступен (более функциональный)
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",  # Используем БД 1 для кеша (0 для channels)
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                "IGNORE_EXCEPTIONS": True,  # Не падаем если Redis недоступен
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 100,  # Увеличено для высокой нагрузки (16GB RAM)
                    "retry_on_timeout": True,
                },
            },
            "KEY_PREFIX": "screener",
            "TIMEOUT": 300,  # 5 минут по умолчанию
        }
    }
except ImportError:
    # Fallback на встроенный Django Redis backend (без django-redis)
    try:
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379/1",  # Используем БД 1 для кеша (0 для channels)
                "KEY_PREFIX": "screener",
                "TIMEOUT": 300,  # 5 минут по умолчанию
            }
        }
    except Exception:
        # Fallback на LocMemCache если Redis недоступен
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "unique-screener-cache",
                "OPTIONS": {
                    "MAX_ENTRIES": 10000,  # Увеличено для множества пользователей (16GB RAM позволяет)
                }
            }
        }

# Channels configuration for WebSocket
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "capacity": 1000000,  # Увеличено до 1M для множества пользователей (16GB RAM позволяет)
            "expiry": 60,  # Увеличено до 60 секунд для обработки множества соединений
            "group_expiry": 86400,  # 24 часа для групп
            "symmetric_encryption_keys": [],  # Отключаем шифрование для производительности
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True
USE_L10N = True

USE_TZ = True

# Поддерживаемые языки
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
    ('es', 'Español'),
    ('he', 'עברית'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Language settings
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60  # 1 year
LANGUAGE_COOKIE_HTTPONLY = False  # Allow JavaScript to read it
LANGUAGE_COOKIE_SAMESITE = 'Lax'
LANGUAGE_COOKIE_SECURE = False  # Set to True if using HTTPS only
LANGUAGE_COOKIE_PATH = '/'  # Cookie available for entire site

# Django Debug Toolbar configuration (только в DEBUG режиме и если установлен)
if _DEBUG_TOOLBAR_AVAILABLE:
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]
    
    # Настройки для Debug Toolbar
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
        "SHOW_COLLAPSED": True,
        "HIDE_DJANGO_SQL": False,
    }

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:profile"
LOGOUT_REDIRECT_URL = "screener:list"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
SERVER_EMAIL = DEFAULT_FROM_EMAIL


