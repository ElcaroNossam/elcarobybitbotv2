from django.db import models


class Symbol(models.Model):
    MARKET_TYPE_CHOICES = [
        ("spot", "Spot"),
        ("futures", "Futures"),
    ]
    
    symbol = models.CharField(max_length=20)  # BTCUSDT (not unique alone, unique with market_type)
    name = models.CharField(max_length=50, blank=True)
    market_type = models.CharField(
        max_length=10, choices=MARKET_TYPE_CHOICES, default="futures"
    )

    class Meta:
        unique_together = [["symbol", "market_type"]]
        indexes = [
            models.Index(fields=["market_type"], name="screener_sy_market__idx"),
        ]

    def __str__(self) -> str:
        return self.symbol


class ScreenerSnapshot(models.Model):
    symbol = models.ForeignKey(
        Symbol, on_delete=models.CASCADE, related_name="snapshots"
    )
    ts = models.DateTimeField(db_index=True)

    # Core price/open interest/funding
    price = models.DecimalField(max_digits=20, decimal_places=8)
    open_interest = models.FloatField(default=0.0)
    funding_rate = models.FloatField(default=0.0)

    # Price change (%)
    change_1m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    change_2m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    change_3m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    change_5m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    change_15m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    change_30m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    change_1h = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    change_4h = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    change_8h = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    change_1d = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)

    # OI change (%)
    oi_change_1m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    oi_change_2m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    oi_change_3m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    oi_change_5m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    oi_change_15m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    oi_change_30m = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    oi_change_1h = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    oi_change_4h = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    oi_change_8h = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    oi_change_1d = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)

    # Volatility
    volatility_1m = models.FloatField(default=0.0)
    volatility_2m = models.FloatField(default=0.0)
    volatility_3m = models.FloatField(default=0.0)
    volatility_5m = models.FloatField(default=0.0)
    volatility_15m = models.FloatField(default=0.0)
    volatility_30m = models.FloatField(default=0.0)
    volatility_1h = models.FloatField(default=0.0)
    volatility_4h = models.FloatField(default=0.0)
    volatility_8h = models.FloatField(default=0.0)
    volatility_1d = models.FloatField(default=0.0)

    # Ticks
    ticks_1m = models.IntegerField(default=0)
    ticks_2m = models.IntegerField(default=0)
    ticks_3m = models.IntegerField(default=0)
    ticks_5m = models.IntegerField(default=0)
    ticks_15m = models.IntegerField(default=0)
    ticks_30m = models.IntegerField(default=0)
    ticks_1h = models.IntegerField(default=0)
    ticks_4h = models.IntegerField(default=0)
    ticks_8h = models.IntegerField(default=0)
    ticks_1d = models.IntegerField(default=0)

    # Vdelta (volume-weighted price change in USDT)
    vdelta_1m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    vdelta_2m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    vdelta_3m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    vdelta_5m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    vdelta_15m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    vdelta_30m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    vdelta_1h = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    vdelta_4h = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    vdelta_8h = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    vdelta_1d = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)

    # Volume (in USDT)
    volume_1m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    volume_2m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    volume_3m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    volume_5m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    volume_15m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    volume_30m = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    volume_1h = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    volume_4h = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    volume_8h = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    volume_1d = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)

    class Meta:
        indexes = [
            models.Index(fields=["symbol", "-ts"]),
        ]

    def __str__(self) -> str:
        return f"{self.symbol.symbol} @ {self.ts}"


class Liquidation(models.Model):
    """
    Модель для хранения событий ликвидаций (force liquidation orders).
    Используется для:
    - История ликвидаций (графики, анализ)
    - Real-time поток через WebSocket (/ws/liquidations/)
    - REST API для запросов истории (/api/liquidations/)
    
    TTL: 24 часа (cleanup_old_liquidations management command)
    """
    SIDE_CHOICES = [
        ("BUY", "Buy (Long liquidated)"),   # Лонг ликвидирован → принудительная покупка
        ("SELL", "Sell (Short liquidated)"), # Шорт ликвидирован → принудительная продажа
    ]
    
    symbol = models.ForeignKey(
        Symbol, 
        on_delete=models.CASCADE, 
        related_name="liquidations",
        help_text="Символ (BTCUSDT, ETHUSDT, etc.)"
    )
    
    side = models.CharField(
        max_length=4, 
        choices=SIDE_CHOICES,
        help_text="BUY = long liquidated, SELL = short liquidated"
    )
    
    price = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        help_text="Цена ликвидации"
    )
    
    quantity = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        help_text="Размер ликвидации (в базовой валюте, например BTC)"
    )
    
    notional_value = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        default=0.0,
        help_text="Размер в USDT (quantity × price)"
    )
    
    timestamp = models.DateTimeField(
        db_index=True,
        help_text="Время ликвидации"
    )
    
    class Meta:
        indexes = [
            # Для быстрого поиска по символу и времени
            models.Index(fields=["symbol", "-timestamp"], name="liq_symbol_ts_idx"),
            # Для быстрого поиска последних ликвидаций
            models.Index(fields=["-timestamp"], name="liq_ts_idx"),
            # Для фильтрации по размеру (крупные ликвидации)
            models.Index(fields=["-notional_value"], name="liq_notional_idx"),
        ]
        ordering = ["-timestamp"]
    
    def __str__(self) -> str:
        return f"{self.symbol.symbol} {self.side} {self.quantity} @ {self.price} ({self.timestamp})"
    
    def save(self, *args, **kwargs):
        # Автоматически считаем notional value
        if not self.notional_value or self.notional_value == 0:
            self.notional_value = self.quantity * self.price
        super().save(*args, **kwargs)
