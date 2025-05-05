from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
import requests

def get_exchange_rates():
    """Get exchange rates from cache or API"""
    # Try to get from cache first
    rates = cache.get('exchange_rates')
    if rates:
        return rates

    # If not in cache, fetch from API
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        if response.status_code == 200:
            rates = response.json()['rates']
            # Cache for 1 hour
            cache.set('exchange_rates', rates, 3600)
            return rates
    except:
        # Fallback rates if API fails
        return {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73
        }

def convert_currency(amount, from_currency, to_currency):
    """Convert amount from one currency to another"""
    if from_currency == to_currency:
        return amount

    rates = get_exchange_rates()
    
    # Convert to USD first if not already USD
    if from_currency != 'USD':
        amount_in_usd = Decimal(str(amount)) / Decimal(str(rates[from_currency]))
    else:
        amount_in_usd = Decimal(str(amount))

    # Convert from USD to target currency
    if to_currency != 'USD':
        converted_amount = amount_in_usd * Decimal(str(rates[to_currency]))
    else:
        converted_amount = amount_in_usd

    return round(converted_amount, 2)

def format_currency(amount, currency):
    """Format amount with currency symbol"""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£'
    }
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}" 