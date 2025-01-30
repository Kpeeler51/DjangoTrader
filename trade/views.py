from django.shortcuts import render
import yfinance as yf
import json
import logging

logger = logging.getLogger(__name__)

def home(request):
    symbol = request.GET.get('symbol', 'BTC')
    logger.debug(f"Fetching data for symbol: {symbol}")
    
    try:
        stock = yf.Ticker(symbol)
        history = stock.history(period="1mo")
        
        dates = history.index.strftime('%Y-%m-%d').tolist()
        prices = history['Close'].tolist()
        
        logger.debug(f"Fetched {len(dates)} data points")

        currency = stock.info.get('currency', 'Unknown')
        
        context = {
            'symbol': symbol,
            'dates': json.dumps(dates),
            'prices': json.dumps(prices),
            'currency': currency,
        }

        if request.user.is_authenticated:
            context['username'] = request.user.username
            if hasattr(request.user, 'profile'):
                context['balance'] = request.user.profile.balance
            else:
                context['balance'] = "Profile not found"
        else:
            context['username'] = "Anonymous"
            context['balance'] = "Not logged in"

    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        context = {
            'symbol': symbol,
            'error': 'Unable to fetch stock data',
        }
        
        if request.user.is_authenticated:
            context['username'] = request.user.username
            if hasattr(request.user, 'profile'):
                context['balance'] = request.user.profile.balance
            else:
                context['balance'] = "Profile not found"
        else:
            context['username'] = "Anonymous"
            context['balance'] = "Not logged in"
    
    return render(request, 'trade/home.html', context)