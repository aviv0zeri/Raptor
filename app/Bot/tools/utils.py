"""
🌟 Main Utilities Module - The Cosmic Compatibility Layer
Maintains backward compatibility while using the new organized structure
"""

# Import from organized subfolders
from .api import (
    get_binance_symbols,
    check_and_format_pair,
    precise_quantity_binance,
    get_fiat_currencies,
    convert_crypto_to_fiat,
    get_fiat_amount,
    update_wallet_data,
    get_non_zero_balances,
    get_asset_usd_value,
    make_binance_request,
    APIError,
    InvalidTradingPairError,
    UnsupportedClientTypeError,
    TradingPairCheckError,
    NotFiatCurrencyException,
    BinanceTimeoutError
)

from .database import (
    connect,
    create_table,
    insert_order,
    get_all_orders,
    get_order_by_id,
    delete_all_orders,
    delete_order_by_id,
    Order,
    Receipt,
    Product,
    ProductManager,
    product_manager
)

from .trading import (
    make_order,
    get_current_datetime,
    get_random_number,
    binance_extra_error_descriptions,
    precise_quantity_bybit,
    test_buy_function
)

from .config import (
    ConfigManager,
    get_config,
    set_config,
    validate_config,
    BINANCE_API_KEY,
    BINANCE_SECRET_KEY,
    DB_CONFIG
)

from .utils import (
    CacheEntry,
    LRUCache,
    CacheManager,
    get_cached_value,
    set_cached_value,
    clear_cache,
    print_wallet,
    get_wallet_summary,
    get_asset_balance,
    get_top_assets_by_value,
    calculate_portfolio_allocation,
    print_portfolio_allocation,
    check_sufficient_balance,
    get_available_trading_balance,
    TimeSyncManager,
    sync_system_time,
    get_formatted_time,
    get_time_sync_status,
    CustomLogger,
    log_to_details,
    log_to_stoploss
)

# Legacy compatibility aliases
make_order_legacy = make_order

# Export all functions for backward compatibility
__all__ = [
    # API functions
    'get_binance_symbols',
    'check_and_format_pair',
    'precise_quantity_binance',
    'get_fiat_currencies',
    'convert_crypto_to_fiat',
    'get_fiat_amount',
    'update_wallet_data',
    'get_non_zero_balances',
    'get_asset_usd_value',
    'make_binance_request',
    
    # Database functions
    'connect',
    'create_table',
    'insert_order',
    'get_all_orders',
    'get_order_by_id',
    'delete_all_orders',
    'delete_order_by_id',
    
    # Trading functions
    'make_order',
    'make_order_legacy',  # Legacy alias
    'get_current_datetime',
    'get_random_number',
    'binance_extra_error_descriptions',
    'precise_quantity_bybit',
    'test_buy_function',
    
    # Configuration functions
    'ConfigManager',
    'get_config',
    'set_config',
    'validate_config',
    
    # Utility functions
    'CacheEntry',
    'LRUCache',
    'CacheManager',
    'get_cached_value',
    'set_cached_value',
    'clear_cache',
    'print_wallet',
    'get_wallet_summary',
    'get_asset_balance',
    'get_top_assets_by_value',
    'calculate_portfolio_allocation',
    'print_portfolio_allocation',
    'check_sufficient_balance',
    'get_available_trading_balance',
    'TimeSyncManager',
    'sync_system_time',
    'get_formatted_time',
    'get_time_sync_status',
    'CustomLogger',
    'log_to_details',
    'log_to_stoploss',
    
    # Classes
    'Order',
    'Receipt',
    'Product',
    'ProductManager',
    'product_manager',
    
    # Configuration variables
    'BINANCE_API_KEY',
    'BINANCE_SECRET_KEY',
    'DB_CONFIG',
    
    # Exceptions
    'APIError',
    'InvalidTradingPairError',
    'UnsupportedClientTypeError',
    'TradingPairCheckError',
    'NotFiatCurrencyException',
    'BinanceTimeoutError'
]

