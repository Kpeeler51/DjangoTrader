# import processes used in models.
from accounts.models import Transaction
from django.db import models
from django.contrib.auth.models import User

# Model to represent users' stock positions.
class StockPosition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    quantity = models.IntegerField(default=0)

    class Meta:
        # Ensure each user can only have one position for each stock.
        unique_together = ('user', 'symbol')

    def __str__(self):
        return f"{self.user.username}'s position in {self.symbol}: {self.quantity} shares"
# Model to represent trade transactions.
class Trade(models.Model):
    # Define possible trade types.
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    # Arguments for trade details.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)

    def __str__(self):
        return f"{self.trade_type} {self.quantity} {self.symbol} at ${self.price} by {self.user.username}"

# Model to represent account transactions.
    def save(self, *args, **kwargs):
        # saves the trade transaction.
        super().save(*args, **kwargs)
        #  Calculates the transaction.
        amount = self.quantity * self.price
        # If stock is sold, update the stock position.
        if self.trade_type == 'SELL':
            amount = -amount
            # Creates a transaction record for the sale.
        Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='TRADE'
        )