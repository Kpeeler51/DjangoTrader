from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import yfinance as yf
import json
import logging
from decimal import Decimal
from django.db import transaction
from .models import StockPosition
from accounts.views import get_user_balance
from accounts.models import Transaction
from django.urls import reverse
from django.middleware.csrf import get_token
from django.http import JsonResponse

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
    symbol = request.GET.get('symbol', 'BTC-USD')
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
            'username': request.user.username if request.user.is_authenticated else None,
            'csrf_token': get_token(request),
        }

        if request.user.is_authenticated:
            positions = StockPosition.objects.filter(user=request.user)
            portfolio_value = Decimal('0.00')
            portfolio_data = []

            for position in positions:
                try:
                    position_current_price = get_current_price(position.symbol)
                    total_value = position.quantity * position_current_price
                    portfolio_value += total_value
                    portfolio_data.append({
                        'symbol': position.symbol,
                        'quantity': position.quantity,
                        'current_price': position_current_price,
                        'total_value': total_value,
                    })
                except Exception as e:
                    logger.error(f"Error fetching data for {position.symbol}: {str(e)}")

            user_balance = get_user_balance(request.user)
            
            context.update({
                'balance': user_balance,
                'portfolio': portfolio_data,
                'portfolio_value': portfolio_value,
                'total_value': portfolio_value + user_balance,
                'buy_url': reverse('buy_stock'),
                'sell_url': reverse('sell_stock'),
            })

    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        context = {
            'symbol': symbol,
            'error': f'Unable to fetch stock data: {str(e)}',
            'username': request.user.username if request.user.is_authenticated else None,
        }
        if request.user.is_authenticated:
            context['balance'] = get_user_balance(request.user)
    
    return render(request, 'trade/home.html', context)

@login_required
@transaction.atomic
def buy_stock(request):
    symbol = request.POST.get('symbol')
    quantity = int(request.POST.get('quantity'))
    
    try:
        current_price = get_current_price(symbol)
        total_cost = quantity * current_price

        profile = request.user.profile
        if profile.balance < total_cost:
            return JsonResponse({'success': False, 'error': "Insufficient funds"})

        # Update user's balance
        profile.balance -= total_cost
        profile.save()

        # Update or create stock position
        position, created = StockPosition.objects.get_or_create(
            user=request.user,
            symbol=symbol,
            defaults={'quantity': quantity}
        )
        if not created:
            position.quantity += quantity
            position.save()

        # Create transaction record
        Transaction.objects.create(
            user=request.user,
            amount=total_cost,
            transaction_type='STOCK_BUY',
            symbol=symbol,
            quantity=quantity,
            price=current_price
        )

        # Fetch updated portfolio data
        portfolio_data = get_portfolio_data(request.user)
        portfolio_value = sum(position['total_value'] for position in portfolio_data)
        total_value = portfolio_value + profile.balance

        return JsonResponse({
            'success': True,
            'message': f'Successfully bought {quantity} shares of {symbol} at ${current_price} per share',
            'portfolio': portfolio_data,
            'portfolio_value': portfolio_value,
            'total_value': total_value,
            'balance': profile.balance
        })
    except ValueError as ve:
        return JsonResponse({'success': False, 'error': str(ve)})
    except Exception as e:
        logger.error(f"Error buying stock: {str(e)}")
        return JsonResponse({'success': False, 'error': f"An error occurred while processing your request: {str(e)}"})

@login_required
@transaction.atomic
def sell_stock(request):
    symbol = request.POST.get('symbol')
    quantity = int(request.POST.get('quantity'))
    
    try:
        current_price = get_current_price(symbol)
        total_value = quantity * current_price

        position = StockPosition.objects.get(user=request.user, symbol=symbol)
        if position.quantity < quantity:
            return JsonResponse({'success': False, 'error': "Insufficient stocks to sell"})

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

        # Create transaction record
        Transaction.objects.create(
            user=request.user,
            amount=total_value,
            transaction_type='STOCK_SELL',
            symbol=symbol,
            quantity=quantity,
            price=current_price
        )

        # Fetch updated portfolio data
        portfolio_data = get_portfolio_data(request.user)
        portfolio_value = sum(position['total_value'] for position in portfolio_data)
        total_value = portfolio_value + profile.balance

        return JsonResponse({
            'success': True,
            'message': f'Successfully sold {quantity} shares of {symbol} at ${current_price} per share',
            'portfolio': portfolio_data,
            'portfolio_value': portfolio_value,
            'total_value': total_value,
            'balance': profile.balance
        })
    except StockPosition.DoesNotExist:
        return JsonResponse({'success': False, 'error': "You don't own this stock"})
    except ValueError as ve:
        return JsonResponse({'success': False, 'error': str(ve)})
    except Exception as e:
        logger.error(f"Error selling stock: {str(e)}")
        return JsonResponse({'success': False, 'error': "An error occurred while processing your request"})
    

def get_portfolio_data(user):
    positions = StockPosition.objects.filter(user=user)
    portfolio_data = []
    for position in positions:
        try:
            current_price = get_current_price(position.symbol)
            total_value = position.quantity * current_price
            portfolio_data.append({
                'symbol': position.symbol,
                'quantity': position.quantity,
                'current_price': current_price,
                'total_value': total_value,
            })
        except Exception as e:
            logger.error(f"Error fetching data for {position.symbol}: {str(e)}")
    return portfolio_data