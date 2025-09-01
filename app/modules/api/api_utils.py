"""
🔌 API Utilities - The Cosmic Connection Hub
=========================================

📁 File: /bot2025_centralized_api_integrated/Bot/tools/api/api_utils.py
🎯 Purpose: Centralized API utilities for exchange interactions
🔧 Function: Provides unified interface for Binance and Bybit APIs

🌟 Features:
- Unified API interface for multiple exchanges
- Automatic authentication and signature generation
- Rate limiting and request management
- Error handling and retry logic
- Response validation and parsing
- WebSocket connection management
- Real-time data streaming
- Order book management

🔄 Supported Operations:
- Market data retrieval (prices, volumes, order books)
- Account information (balances, positions)
- Order management (place, cancel, query)
- Trade history and analytics
- WebSocket streaming for real-time data
- Authentication and security

📊 Supported Exchanges:
- Binance (primary exchange)
- Bybit (secondary exchange)
- Extensible for additional exchanges

🔧 Configuration:
- API keys and secrets (from environment)
- Request timeouts and retries
- Rate limiting parameters
- WebSocket connection settings
- Error handling strategies

📋 Dependencies:
- python-binance (Binance API client)
- pybit (Bybit API client)
- requests (HTTP requests)
- websockets (WebSocket connections)
- hmac (signature generation)
- hashlib (cryptographic functions)
- time (timestamp generation)

🔗 Related Files:
- wrapper.py (API wrapper implementation)
- config/config_manager.py (configuration)
- utils/centralized_logger.py (logging)

🎯 API Endpoints:
- Market Data: /api/v3/ticker/price, /api/v3/klines
- Account: /api/v3/account, /api/v3/balance
- Orders: /api/v3/order, /api/v3/openOrders
- WebSocket: Real-time streaming endpoints

🛡️ Security Features:
- HMAC-SHA256 signature generation
- Request timestamp validation
- API key authentication
- IP whitelist support
- Rate limiting compliance
"""

import sys
import os
import time
import hmac
import hashlib
from urllib.parse import urlencode
from decimal import Decimal, ROUND_DOWN
from threading import Lock
try:
    import requests
except ImportError:
    # Fallback for IDE 
    # 
    # 
    # 
    # 
    # compatibility
    requests = None
try:
    from binance.client import BinanceAPIException
except ImportError:
    # Fallback for IDE compatibility
    BinanceAPIException = Exception
from .wrapper import make_binance_request
try:
    from ..utils.log_module import CustomLogger
except ImportError:
    # Fallback for IDE compatibility
    class CustomLogger:
        def __init__(self, filename):
            pass
        def info(self, msg):
            print(f"INFO: {msg}")
        def error(self, msg):
            print(f"ERROR: {msg}")
        def warning(self, msg):
            print(f"WARNING: {msg}")

# Initialize the cosmic logger
logger = CustomLogger("app.log")

# Global wallet cache with thread safety
wallet_data = {}
wallet_lock = Lock()

class APIError(Exception):
    """🌊 API Error - When the digital waves crash against our shores"""
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"APIError(code={self.code}): {self.message}"

class InvalidTradingPairError(Exception):
    """❌ Invalid Trading Pair - When symbols dance to different rhythms"""
    pass

class UnsupportedClientTypeError(Exception):
    """🚫 Unsupported Client - When the exchange speaks a different language"""
    pass

class TradingPairCheckError(Exception):
    """🔍 Trading Pair Check Failed - When validation meets chaos"""
    pass

def get_binance_symbols(client):
    """
    🌟 Fetch all available symbols from Binance's cosmic marketplace
    Returns a sorted list of all trading pairs available
    """
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        headers = {"X-MBX-APIKEY": client.API_KEY}
        params = {}

        # Add signature for authenticated requests
        if hasattr(client, 'API_SECRET') and client.API_SECRET:
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = 5000

            query_string = urlencode(params)
            signature = hmac.new(client.API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
            params["signature"] = signature

        response = make_binance_request("GET", url, headers=headers, params=params)
        exchange_info = response.json()
        symbols = []
        
        for symbol in exchange_info.get('symbols', []):
            symbols.append(symbol['symbol'].upper())

        return sorted(list(set(symbols)))

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTPError while fetching Binance symbols: {e}")
        return []
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching Binance symbols: {e}")
        return []

def check_and_format_pair(coin, base_coin, client_type, client):
    """
    🎭 Validate and format trading pairs for the cosmic dance of exchanges
    Ensures the pair exists and follows the exchange's rhythm
    """
    symbol = f'{coin.upper()}{base_coin.upper()}'
    
    try:
        if client_type.lower() == 'binance':
            url = "https://api.binance.com/api/v3/exchangeInfo"
            headers = {"X-MBX-APIKEY": client.API_KEY}
            response = make_binance_request("GET", url, headers=headers)

            exchange_info = response.json()
            symbols = [item['symbol'].upper() for item in exchange_info.get('symbols', [])]

            if symbol in symbols:
                return symbol
            else:
                raise InvalidTradingPairError(f"Invalid trading pair for Binance: {symbol}")

        elif client_type.lower() == 'bybit':
            url = "https://api.bybit.com/v5/market/tickers"
            params = {"category": "spot", "symbol": symbol}
            response = make_binance_request("GET", url, params=params)

            result = response.json()
            if 'result' in result and result['result']:
                return symbol
            else:
                raise InvalidTradingPairError(f"Invalid trading pair for Bybit: {symbol}")
        else:
            raise UnsupportedClientTypeError(f"Unsupported client type: {client_type}")

    except (InvalidTradingPairError, UnsupportedClientTypeError) as e:
        raise e
    except Exception as e:
        raise TradingPairCheckError(f"Error checking trading pair: {e}")

def precise_quantity_binance(symbol, quantity, client):
    """
    ⚖️ Calculate precise quantity that dances with Binance's LOT_SIZE rules
    Ensures our orders don't step on the exchange's toes
    """
    try:
        quantity = Decimal(quantity)
        url = "https://api.binance.com/api/v3/exchangeInfo"
        headers = {"X-MBX-APIKEY": client.API_KEY}
        response = make_binance_request("GET", url, headers=headers)

        exchange_info = response.json()
        info = next((item for item in exchange_info['symbols'] if item['symbol'] == symbol), None)

        if not info:
            raise ValueError(f"Symbol {symbol} not found in exchange information.")

        stepSize = None
        for x in info.get("filters", []):
            if x["filterType"] == "LOT_SIZE":
                stepSize = Decimal(x["stepSize"])
                break

        if stepSize is None:
            raise ValueError(f"LOT_SIZE filter not found for symbol {symbol}")

        precise_quantity = (quantity // stepSize) * stepSize
        if precise_quantity == Decimal(0):
            precise_quantity = Decimal('0')

        return float(precise_quantity)

    except ValueError as e:
        print(f"ValueError: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error in precise_quantity_binance: {str(e)}")
        raise

def get_fiat_currencies(client):
    """
    💰 Discover the fiat currencies that flow through Binance's marketplace
    Returns a list of unique fiat currencies available for trading
    """
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        headers = {"X-MBX-APIKEY": client.API_KEY}
        response = make_binance_request("GET", url, headers=headers)

        exchange_info = response.json()
        symbols = exchange_info.get('symbols', [])
        fiat_currencies = set()

        for symbol_info in symbols:
            quote_asset = symbol_info.get('quoteAsset', '')
            if quote_asset.isalpha() and len(quote_asset) in [3, 4]:
                fiat_currencies.add(quote_asset)

        return list(fiat_currencies)

    except Exception as e:
        print(f"Error fetching fiat currencies: {e}")
        return []

def convert_crypto_to_fiat(coin, fiat_coin, amount, client):
    """
    🔄 Transform crypto into fiat - the alchemy of digital currency conversion
    Converts cryptocurrency amount to its fiat equivalent
    """
    FIAT_CURRENCIES = [
        'RUB', 'AEUR', 'VAI', 'RON', 'DOGE', 'TRY', 'COP', 'UAH', 'BTC', 'USDC',
        'PAX', 'ETH', 'USDT', 'MXN', 'BKRW', 'DAI', 'BUSD', 'TUSD', 'NGN',
        'IDRT', 'JPY', 'GBP', 'DOT', 'UST', 'BVND', 'PLN', 'AUD', 'USDS', 'EUR',
        'BNB', 'ARS', 'TRX', 'BIDR', 'BRL', 'XRP', 'ZAR', 'CZK', 'USDP'
    ]
    
    if fiat_coin not in FIAT_CURRENCIES:
        raise Exception(f"Not a fiat currency: {fiat_coin}")
    
    symbol = f'{coin.upper()}{fiat_coin.upper()}'

    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        headers = {"X-MBX-APIKEY": client.API_KEY}
        response = make_binance_request("GET", url, headers=headers)
        
        ticker = response.json()
        price = float(ticker['price'])
        fiat_value = amount * price
        return fiat_value

    except Exception as e:
        print(f"Unexpected error: {e}")
        return -1

def get_fiat_amount(coin, fiat_coin, amount, client):
    """
    💸 Calculate how much crypto you need for a specific fiat amount
    The reverse alchemy of fiat to crypto conversion
    """
    FIAT_CURRENCIES = [
        'RUB', 'AEUR', 'VAI', 'RON', 'DOGE', 'TRY', 'COP', 'UAH', 'BTC', 'USDC',
        'PAX', 'ETH', 'USDT', 'MXN', 'BKRW', 'DAI', 'BUSD', 'TUSD', 'NGN',
        'IDRT', 'JPY', 'GBP', 'DOT', 'UST', 'BVND', 'PLN', 'AUD', 'USDS', 'EUR',
        'BNB', 'ARS', 'TRX', 'BIDR', 'BRL', 'XRP', 'ZAR', 'CZK', 'USDP'
    ]
    
    if fiat_coin not in FIAT_CURRENCIES:
        raise Exception(f"Not a fiat currency: {fiat_coin}")
    
    symbol = f'{coin.upper()}{fiat_coin.upper()}'

    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        headers = {"X-MBX-APIKEY": client.API_KEY}
        response = make_binance_request("GET", url, headers=headers)
        
        ticker = response.json()
        price = float(ticker['price'])
        equivalent_amount = amount / price
        return equivalent_amount

    except Exception as e:
        print(f"Unexpected error: {e}")
        return -1

def update_wallet_data(client):
    """🔄 Refresh the cosmic wallet cache with latest balance data"""
    global wallet_data
    with wallet_lock:
        wallet_data = get_non_zero_balances(client)

def get_non_zero_balances(client):
    """
    💼 Fetch all non-zero balances from the digital vault
    Returns a dictionary of assets with their balances and USD values
    """
    account = client.get_account()
    balances = account['balances']
    non_zero_balances = {}
    
    for balance in balances:
        asset = balance['asset']
        free = float(balance['free'])
        if free > 0:
            usd_value = get_asset_usd_value(asset, free, client)
            non_zero_balances[asset] = {'balance': free, 'usd_value': usd_value}
    
    return non_zero_balances

def get_asset_usd_value(asset, amount, client):
    """
    💵 Calculate the USD value of any asset in our cosmic portfolio
    """
    if asset == 'USDT':
        return amount
    else:
        symbol = f"{asset}USDT"
        try:
            ticker = client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            return amount * price
        except:
            return 0
