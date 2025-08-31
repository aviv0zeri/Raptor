"""
🌊 API Utilities - The Cosmic Marketplace Connectors
Exports all API-related functions for easy importing
"""

from .api_utils import (
    get_binance_symbols,
    check_and_format_pair,
    precise_quantity_binance,
    get_fiat_currencies,
    convert_crypto_to_fiat,
    get_fiat_amount,
    update_wallet_data,
    get_non_zero_balances,
    get_asset_usd_value,
    APIError,
    InvalidTradingPairError,
    UnsupportedClientTypeError,
    TradingPairCheckError,
    NotFiatCurrencyException
)

from .wrapper import (
    make_binance_request,
    BinanceTimeoutError
)

__all__ = [
    # API utilities
    'get_binance_symbols',
    'check_and_format_pair',
    'precise_quantity_binance',
    'get_fiat_currencies',
    'convert_crypto_to_fiat',
    'get_fiat_amount',
    'update_wallet_data',
    'get_non_zero_balances',
    'get_asset_usd_value',
    
    # Exceptions
    'APIError',
    'InvalidTradingPairError',
    'UnsupportedClientTypeError',
    'TradingPairCheckError',
    'NotFiatCurrencyException',
    
    # Wrapper functions
    'make_binance_request',
    'BinanceTimeoutError'
]
