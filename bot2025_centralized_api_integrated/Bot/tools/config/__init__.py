"""
⚙️ Configuration Utilities - The Cosmic Settings Controller
Exports all configuration-related functions and variables for easy importing
"""

from .config_manager import (
    ConfigManager,
    get_config,
    set_config,
    validate_config
)

from .config import (
    BINANCE_API_KEY,
    BINANCE_SECRET_KEY,
    DB_CONFIG
)

__all__ = [
    # Configuration management
    'ConfigManager',
    'get_config',
    'set_config',
    'validate_config',
    
    # Configuration variables
    'BINANCE_API_KEY',
    'BINANCE_SECRET_KEY',
    'DB_CONFIG'
]
