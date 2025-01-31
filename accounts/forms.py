from django import forms
from django.core.validators import MinValueValidator

class DepositForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        label="Deposit Amount ($)"
    )