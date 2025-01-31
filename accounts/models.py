from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def deposit(self, amount):
        self.balance += amount
        self.save()
        Transaction.objects.create(user=self.user, amount=amount)

    def get_transactions(self):
        return Transaction.objects.filter(user=self.user).order_by('-timestamp')
    
    def reset_account(self):
       self.balance = Decimal('500.00')
       Transaction.objects.filter(user=self.user).delete()
       self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deposit of ${self.amount} by {self.user.username}"