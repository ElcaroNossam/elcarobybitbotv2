from django.contrib import admin

from .models import ScreenerSnapshot, Symbol


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    list_display = ("symbol", "name", "market_type")
    search_fields = ("symbol", "name")
    list_filter = ("market_type",)


@admin.register(ScreenerSnapshot)
class ScreenerSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "symbol",
        "ts",
        "price",
        "change_15m",
        "volume_15m",
        "oi_change_15m",
        "funding_rate",
    )
    list_filter = ("symbol__market_type", "ts")
    search_fields = ("symbol__symbol",)
    date_hierarchy = "ts"
    list_select_related = ("symbol",)  # Оптимизация: избегаем N+1 запросов
    list_per_page = 50  # Ограничение для производительности
    readonly_fields = ("ts",)  # Временная метка обычно не редактируется
    
    def get_queryset(self, request):
        """Оптимизация запроса с select_related."""
        qs = super().get_queryset(request)
        return qs.select_related("symbol")


