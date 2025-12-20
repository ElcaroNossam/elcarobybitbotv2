from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from config.views import set_language_custom, robots_txt, test_liquidations
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/setlang/", set_language_custom, name="set_language"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("test-liquidations/", test_liquidations, name="test_liquidations"),  # Test page
]

# Django Debug Toolbar URLs (только в DEBUG режиме и если установлен)
# Проверяем через settings, чтобы избежать повторного импорта
if settings.DEBUG:
    try:
        # Проверяем, что debug_toolbar в INSTALLED_APPS
        if 'debug_toolbar' in settings.INSTALLED_APPS:
            import debug_toolbar
            urlpatterns.insert(0, path("__debug__/", include(debug_toolbar.urls)))
    except (ImportError, AttributeError):
        pass  # Debug toolbar не установлен или не в INSTALLED_APPS

urlpatterns += i18n_patterns(
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("api/", include(("api.urls", "api"), namespace="api")),
    path("alerts/", include(("alerts.urls", "alerts"), namespace="alerts")),
    path("", include(("screener.urls", "screener"), namespace="screener")),
    prefix_default_language=False,
)


