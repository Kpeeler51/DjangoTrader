from django.shortcuts import render
import yfinance as yf
import json
import logging
from accounts.views import get_user_balance

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
            'username': request.user.username if request.user.is_authenticated else "Anonymous",
            'balance': get_user_balance(request.user)
        }

    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        context = {
            'symbol': symbol,
            'error': 'Unable to fetch stock data',
            'username': request.user.username if request.user.is_authenticated else "Anonymous",
            'balance': get_user_balance(request.user)
        }
    
    return render(request, 'trade/home.html', context)