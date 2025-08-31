"""
🔧 General Utilities - The Cosmic Helper Functions
Exports all general utility functions for easy importing
"""

from .cache_manager import (
    CacheEntry,
    LRUCache,
    CacheManager,
    get_cached_value,
    set_cached_value,
    clear_cache
)

from .wallet_utils import (
    print_wallet,
    get_wallet_summary,
    get_asset_balance,
    get_top_assets_by_value,
    calculate_portfolio_allocation,
    print_portfolio_allocation,
    check_sufficient_balance,
    get_available_trading_balance
)

from ..api.api_utils import (
    update_wallet_data,
    get_non_zero_balances,
    get_asset_usd_value
)

from .sync_time_utils import (
    TimeSyncManager,
    sync_system_time,
    get_formatted_time,
    get_time_sync_status
)

from .log_module import (
    CustomLogger
)

from .centralized_logger import (
    CentralizedLogger,
    centralized_logger,
    log_debug,
    log_info,
    log_warning,
    log_error,
    log_critical
)

from .sounds_interface import (
    SoundsInterface,
    sounds_interface,
    SoundType,
    play_order_executed,
    play_order_cancelled,
    play_error_alert,
    play_success_confirmation,
    play_warning_notification,
    play_trade_signal,
    play_system_start,
    play_system_stop,
    play_balance_update,
    play_profit_alert,
    play_loss_alert
)

from .bot_output_logger import (
    log_to_details,
    log_to_stoploss
)

__all__ = [
    # Cache management
    'CacheEntry',
    'LRUCache',
    'CacheManager',
    'get_cached_value',
    'set_cached_value',
    'clear_cache',
    
    # Wallet utilities
    'print_wallet',
    'get_wallet_summary',
    'get_asset_balance',
    'get_top_assets_by_value',
    'calculate_portfolio_allocation',
    'print_portfolio_allocation',
    'check_sufficient_balance',
    'get_available_trading_balance',
    'update_wallet_data',
    'get_non_zero_balances',
    'get_asset_usd_value',
    
    # Time synchronization
    'TimeSyncManager',
    'sync_system_time',
    'get_formatted_time',
    'get_time_sync_status',
    
    # Logging
    'CustomLogger',
    'log_to_details',
    'log_to_stoploss',
    
    # Centralized logging
    'CentralizedLogger',
    'centralized_logger',
    'log_debug',
    'log_info',
    'log_warning',
    'log_error',
    'log_critical',
    
    # Sounds interface
    'SoundsInterface',
    'sounds_interface',
    'SoundType',
    'play_order_executed',
    'play_order_cancelled',
    'play_error_alert',
    'play_success_confirmation',
    'play_warning_notification',
    'play_trade_signal',
    'play_system_start',
    'play_system_stop',
    'play_balance_update',
    'play_profit_alert',
    'play_loss_alert'
]
