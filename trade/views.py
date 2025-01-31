from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import yfinance as yf
import json
import logging
from decimal import Decimal
from django.db import transaction
from .models import StockPosition, Trade
from accounts.views import get_user_balance

logger = logging.getLogger(__name__)

def get_current_price(symbol):
    try:
        if symbol == 'BTC':
            symbol = 'BTC-USD'
        stock = yf.Ticker(symbol)
        info = stock.info
        
        if 'regularMarketPrice' in info:
            return Decimal(str(info['regularMarketPrice']))
        elif 'regularMarketOpen' in info:
            return Decimal(str(info['regularMarketOpen']))
        else:
            available_keys = ', '.join(info.keys())
            raise ValueError(f"No suitable price key found in stock info. Available keys: {available_keys}")
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {str(e)}")
        raise ValueError(f"Unable to fetch current price for {symbol}. Error: {str(e)}")
    
def home(request):
    symbol = request.GET.get('symbol', 'BTC')
    logger.debug(f"Fetching data for symbol: {symbol}")
    
    try:
        stock = yf.Ticker(symbol)
        history = stock.history(period="1mo")
        
        dates = history.index.strftime('%Y-%m-%d').tolist()
        prices = history['Close'].tolist()
        
        logger.debug(f"Fetched {len(dates)} data points")

        currency = stock.info.get('currency', 'USD')
        current_price = get_current_price(symbol)
        
        context = {
            'symbol': symbol,
            'dates': json.dumps(dates),
            'prices': json.dumps(prices),
            'currency': currency,
            'current_price': current_price,
            'username': request.user.username if request.user.is_authenticated else "Anonymous",
            'balance': get_user_balance(request.user)
        }

    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        context = {
            'symbol': symbol,
            'error': f'Unable to fetch stock data: {str(e)}',
            'username': request.user.username if request.user.is_authenticated else "Anonymous",
            'balance': get_user_balance(request.user)
        }
    
    return render(request, 'trade/home.html', context)

@login_required
@transaction.atomic
def buy_stock(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        quantity = int(request.POST.get('quantity'))
        
        try:
            current_price = get_current_price(symbol)
            total_cost = quantity * current_price

            profile = request.user.profile
            if profile.balance < total_cost:
                messages.error(request, "Insufficient funds")
                return redirect('home')

            # Update user's balance
            profile.balance -= total_cost
            profile.save()

            # Update or create stock position
            position, created = StockPosition.objects.get_or_create(user=request.user, symbol=symbol)
            position.quantity += quantity
            position.save()

            # Create trade record
            Trade.objects.create(
                user=request.user,
                symbol=symbol,
                quantity=quantity,
                price=current_price,
                trade_type='BUY'
            )

            messages.success(request, f'Successfully bought {quantity} shares of {symbol} at ${current_price} per share')
        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            logger.error(f"Error buying stock: {str(e)}")
            messages.error(request, f"An error occurred while processing your request: {str(e)}")

    return redirect('home')

@login_required
@transaction.atomic
def sell_stock(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        quantity = int(request.POST.get('quantity'))
        
        try:
            current_price = get_current_price(symbol)
            total_value = quantity * current_price

            position = StockPosition.objects.get(user=request.user, symbol=symbol)
            if position.quantity < quantity:
                messages.error(request, "Insufficient stocks to sell")
                return redirect('portfolio')

            # Update user's balance
            profile = request.user.profile
            profile.balance += total_value
            profile.save()

            # Update stock position
            position.quantity -= quantity
            if position.quantity == 0:
                position.delete()
            else:
                position.save()

            # Create trade record
            Trade.objects.create(
                user=request.user,
                symbol=symbol,
                quantity=quantity,
                price=current_price,
                trade_type='SELL'
            )

            messages.success(request, f'Successfully sold {quantity} shares of {symbol} at ${current_price} per share')
        except StockPosition.DoesNotExist:
            messages.error(request, "You don't own this stock")
        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            logger.error(f"Error selling stock: {str(e)}")
            messages.error(request, "An error occurred while processing your request")

    return redirect('portfolio')

@login_required
def portfolio(request):
    positions = StockPosition.objects.filter(user=request.user)
    portfolio_value = Decimal('0.00')
    portfolio_data = []

    for position in positions:
        try:
            current_price = get_current_price(position.symbol)
            total_value = position.quantity * current_price
            portfolio_value += total_value
            portfolio_data.append({
                'symbol': position.symbol,
                'quantity': position.quantity,
                'current_price': current_price,
                'total_value': total_value,
            })
        except Exception as e:
            logger.error(f"Error fetching data for {position.symbol}: {str(e)}")

    context = {
        'portfolio': portfolio_data,
        'portfolio_value': portfolio_value,
        'balance': get_user_balance(request.user),
        'total_value': portfolio_value + get_user_balance(request.user),
    }
    return render(request, 'trade/portfolio.html', context)