from django.contrib import admin
from .models import Alert, AlertLog


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'market_type', 'alert_type', 'is_active', 'created_at', 'triggered_at']
    list_filter = ['market_type', 'alert_type', 'is_active']
    search_fields = ['symbol', 'message']
    date_hierarchy = 'created_at'


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ['alert', 'triggered_value', 'triggered_at', 'notified']
    list_filter = ['notified', 'triggered_at']
    date_hierarchy = 'triggered_at'
