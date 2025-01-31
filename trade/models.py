from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class StockPosition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'symbol')

    def __str__(self):
        return f"{self.user.username}'s position in {self.symbol}: {self.quantity} shares"

class Trade(models.Model):
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)

    def __str__(self):
        return f"{self.get_trade_type_display()} {self.quantity} shares of {self.symbol} at ${self.price} by {self.user.username}"

    @property
    def total_value(self):
        return Decimal(self.quantity) * self.price
