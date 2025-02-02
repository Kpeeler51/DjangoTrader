from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import DepositForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            request.user.profile.deposit(amount)
            return redirect('balance')
    else:
        form = DepositForm()
    
    context = {
        'form': form,
        'balance': request.user.profile.balance
    }
    return render(request, 'accounts/deposit.html', context)

@login_required
def account_balance(request):
    transactions = request.user.profile.get_transactions()
    context = {
        'balance': request.user.profile.balance,
        'transactions': transactions
    }
    return render(request, 'accounts/balance.html', context)

def get_user_balance(user):
    if user.is_authenticated:
        if hasattr(user, 'profile'):
            return user.profile.balance
        else:
            return "Profile not found"
    else:
        return "Not logged in"
    
@login_required
def reset_account(request):
    if request.method == 'POST':
        request.user.profile.reset_account()
    return redirect('balance')