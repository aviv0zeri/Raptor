"""
⚙️ Configuration Manager - The Cosmic Settings Controller
Where environment variables dance with hardcoded defaults
"""

import os
from typing import Dict, Any, Optional
try:
    from ..utils.log_module import CustomLogger
except ImportError:
    # Fallback for IDE compatibility
    class CustomLogger:
        def __init__(self, filename):
            pass
        def log(self, level, message):
            print(f"{level.upper()}: {message}")
        def info(self, message):
            print(f"INFO: {message}")
        def error(self, message):
            print(f"ERROR: {message}")
        def warning(self, message):
            print(f"WARNING: {message}")

# Initialize the cosmic logger
logger = CustomLogger("app.log")

class ConfigManager:
    """
    🎛️ The Grand Configuration Orchestrator
    Manages all settings with environment variable support and graceful fallbacks
    """
    
    def __init__(self):
        self.config = {}
        self._load_configuration()
    
    def _load_configuration(self):
        """🔧 Load configuration from environment variables with artistic defaults"""
        
        # Database Configuration
        self.config['database'] = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'dbname': os.getenv('DB_NAME', 'trading_bot'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password'),
        }
        
        # API Configuration
        self.config['api'] = {
            'binance_api_key': os.getenv('BINANCE_API_KEY', ''),
            'binance_secret_key': os.getenv('BINANCE_SECRET_KEY', ''),
            'bybit_api_key': os.getenv('BYBIT_API_KEY', ''),
            'bybit_secret_key': os.getenv('BYBIT_SECRET_KEY', ''),
            'request_timeout': int(os.getenv('REQUEST_TIMEOUT', '10')),
            'max_retries': int(os.getenv('MAX_RETRIES', '5')),
        }
        
        # Trading Configuration
        self.config['trading'] = {
            'default_quantity': float(os.getenv('DEFAULT_QUANTITY', '1.0')),
            'max_position_size': float(os.getenv('MAX_POSITION_SIZE', '100.0')),
            'risk_percentage': float(os.getenv('RISK_PERCENTAGE', '2.0')),
            'enable_paper_trading': os.getenv('ENABLE_PAPER_TRADING', 'true').lower() == 'true',
            'default_exchange': os.getenv('DEFAULT_EXCHANGE', 'binance'),
        }
        
        # Logging Configuration
        self.config['logging'] = {
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_file': os.getenv('LOG_FILE', 'app.log'),
            'enable_console_logging': os.getenv('ENABLE_CONSOLE_LOGGING', 'true').lower() == 'true',
            'max_log_size': int(os.getenv('MAX_LOG_SIZE', '10485760')),  # 10MB
        }
        
        # Performance Configuration
        self.config['performance'] = {
            'wallet_update_interval': int(os.getenv('WALLET_UPDATE_INTERVAL', '30')),  # seconds
            'price_update_interval': int(os.getenv('PRICE_UPDATE_INTERVAL', '5')),  # seconds
            'enable_caching': os.getenv('ENABLE_CACHING', 'true').lower() == 'true',
            'cache_ttl': int(os.getenv('CACHE_TTL', '300')),  # seconds
        }
        
        # Web Interface Configuration
        self.config['web'] = {
            'host': os.getenv('WEB_HOST', 'localhost'),
            'port': int(os.getenv('WEB_PORT', '5000')),
            'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true',
            'enable_cors': os.getenv('ENABLE_CORS', 'true').lower() == 'true',
        }
        
        logger.log('info', "🌟 Configuration loaded successfully")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        🔍 Retrieve a configuration value with graceful fallback
        """
        try:
            return self.config[section][key]
        except KeyError:
            logger.log('warning', f"Configuration key '{section}.{key}' not found, using default: {default}")
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        ✏️ Set a configuration value dynamically
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        logger.log('info', f"Configuration updated: {section}.{key} = {value}")
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        📋 Get an entire configuration section
        """
        return self.config.get(section, {})
    
    def validate_configuration(self) -> bool:
        """
        ✅ Validate critical configuration settings
        Returns True if configuration is valid, False otherwise
        """
        errors = []
        
        # Check API keys
        if not self.get('api', 'binance_api_key'):
            errors.append("BINANCE_API_KEY is required")
        
        if not self.get('api', 'binance_secret_key'):
            errors.append("BINANCE_SECRET_KEY is required")
        
        # Check database configuration
        if not self.get('database', 'dbname'):
            errors.append("DB_NAME is required")
        
        if errors:
            for error in errors:
                logger.log('error', f"Configuration validation failed: {error}")
            return False
        
        logger.log('info', "✅ Configuration validation passed")
        return True
    
    def print_configuration_summary(self) -> None:
        """
        📊 Display a beautiful summary of the current configuration
        """
        print("\n" + "="*60)
        print("🌟 CONFIGURATION SUMMARY")
        print("="*60)
        
        for section, settings in self.config.items():
            print(f"\n📁 {section.upper()}:")
            for key, value in settings.items():
                # Mask sensitive information
                if 'key' in key.lower() or 'password' in key.lower():
                    display_value = '*' * 8 if value else 'Not Set'
                else:
                    display_value = str(value)
                print(f"  {key}: {display_value}")
        
        print("\n" + "="*60)

# Global configuration instance
config_manager = ConfigManager()

def get_config(section: str, key: str, default: Any = None) -> Any:
    """
    🌟 Convenience function to get configuration values
    """
    return config_manager.get(section, key, default)

def set_config(section: str, key: str, value: Any) -> None:
    """
    🌟 Convenience function to set configuration values
    """
    config_manager.set(section, key, value)

def validate_config() -> bool:
    """
    🌟 Convenience function to validate configuration
    """
    return config_manager.validate_configuration()
