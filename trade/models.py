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
        return f"{self.trade_type} {self.quantity} {self.symbol} at ${self.price} by {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from accounts.models import Transaction
        amount = self.quantity * self.price
        if self.trade_type == 'SELL':
            amount = -amount
        Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='TRADE'
        )