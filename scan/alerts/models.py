from django.db import models
from django.utils import timezone


class Alert(models.Model):
    """Market alert model for notifications."""
    
    ALERT_TYPES = [
        ('price', 'Price Alert'),
        ('volume', 'Volume Alert'),
        ('liquidation', 'Liquidation Alert'),
        ('volatility', 'Volatility Alert'),
    ]
    
    MARKET_TYPES = [
        ('spot', 'Spot'),
        ('futures', 'Futures'),
    ]
    
    symbol = models.CharField(max_length=20, db_index=True)
    market_type = models.CharField(max_length=10, choices=MARKET_TYPES, default='spot')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, db_index=True)
    condition = models.JSONField(default=dict)  # {operator: ">", value: 50000}
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['symbol', 'alert_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.symbol} - {self.alert_type}"


class AlertLog(models.Model):
    """Log of triggered alerts."""
    
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='logs')
    triggered_value = models.DecimalField(max_digits=20, decimal_places=8)
    triggered_at = models.DateTimeField(default=timezone.now, db_index=True)
    notified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['triggered_at']),
        ]
    
    def __str__(self):
        return f"Alert {self.alert.id} triggered at {self.triggered_at}"
