"""
🚨 Bot Exceptions - The Cosmic Error Handling System
Where chaos meets order and errors become meaningful insights
"""

class BotException(Exception):
    """
    🌟 Base exception class for all bot-related errors
    The foundation of our cosmic error handling system
    """
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self):
        """
        📊 Convert exception to dictionary for logging
        """
        return {
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'exception_type': self.__class__.__name__
        }

class APIException(BotException):
    """
    🌊 API-related exceptions - When the digital waves crash
    """
    
    def __init__(self, message: str, api_name: str = None, status_code: int = None, **kwargs):
        self.api_name = api_name
        self.status_code = status_code
        super().__init__(message, error_code="API_ERROR", details={
            'api_name': api_name,
            'status_code': status_code,
            **kwargs
        })

class BinanceAPIException(APIException):
    """
    🪙 Binance-specific API exceptions
    """
    
    def __init__(self, message: str, status_code: int = None, **kwargs):
        super().__init__(message, api_name="Binance", status_code=status_code, **kwargs)

class BybitAPIException(APIException):
    """
    🐉 Bybit-specific API exceptions
    """
    
    def __init__(self, message: str, status_code: int = None, **kwargs):
        super().__init__(message, api_name="Bybit", status_code=status_code, **kwargs)

class TradingException(BotException):
    """
    💰 Trading-related exceptions - When the market gods are angry
    """
    
    def __init__(self, message: str, order_id: str = None, symbol: str = None, **kwargs):
        self.order_id = order_id
        self.symbol = symbol
        super().__init__(message, error_code="TRADING_ERROR", details={
            'order_id': order_id,
            'symbol': symbol,
            **kwargs
        })

class InsufficientBalanceException(TradingException):
    """
    💸 When the digital vault is empty
    """
    
    def __init__(self, asset: str, required_amount: float, available_amount: float, **kwargs):
        message = f"Insufficient balance for {asset}. Required: {required_amount}, Available: {available_amount}"
        super().__init__(message, error_code="INSUFFICIENT_BALANCE", details={
            'asset': asset,
            'required_amount': required_amount,
            'available_amount': available_amount,
            **kwargs
        })

class InvalidOrderException(TradingException):
    """
    ❌ When orders don't follow the cosmic rules
    """
    
    def __init__(self, message: str, order_type: str = None, **kwargs):
        super().__init__(message, error_code="INVALID_ORDER", details={
            'order_type': order_type,
            **kwargs
        })

class OrderExecutionException(TradingException):
    """
    ⚡ When order execution fails in the digital battlefield
    """
    
    def __init__(self, message: str, execution_time: float = None, **kwargs):
        super().__init__(message, error_code="ORDER_EXECUTION_ERROR", details={
            'execution_time': execution_time,
            **kwargs
        })

class DatabaseException(BotException):
    """
    🗄️ Database-related exceptions - When the data temple crumbles
    """
    
    def __init__(self, message: str, operation: str = None, table: str = None, **kwargs):
        self.operation = operation
        self.table = table
        super().__init__(message, error_code="DATABASE_ERROR", details={
            'operation': operation,
            'table': table,
            **kwargs
        })

class ConfigurationException(BotException):
    """
    ⚙️ Configuration-related exceptions - When settings go haywire
    """
    
    def __init__(self, message: str, config_key: str = None, config_value: str = None, **kwargs):
        self.config_key = config_key
        self.config_value = config_value
        super().__init__(message, error_code="CONFIG_ERROR", details={
            'config_key': config_key,
            'config_value': config_value,
            **kwargs
        })

class ValidationException(BotException):
    """
    ✅ Validation-related exceptions - When data doesn't meet cosmic standards
    """
    
    def __init__(self, message: str, field: str = None, value: str = None, **kwargs):
        self.field = field
        self.value = value
        super().__init__(message, error_code="VALIDATION_ERROR", details={
            'field': field,
            'value': value,
            **kwargs
        })

class InvalidTradingPairException(ValidationException):
    """
    🎭 When trading pairs don't dance to the right rhythm
    """
    
    def __init__(self, pair: str, exchange: str = None, **kwargs):
        message = f"Invalid trading pair: {pair}"
        if exchange:
            message += f" for exchange: {exchange}"
        super().__init__(message, field="trading_pair", value=pair, details={
            'exchange': exchange,
            **kwargs
        })

class NotFiatCurrencyException(ValidationException):
    """
    💱 When someone tries to use non-fiat as fiat
    """
    
    def __init__(self, currency: str, **kwargs):
        message = f"Not a fiat currency: {currency}"
        super().__init__(message, field="currency", value=currency, **kwargs)

class TimeSyncException(BotException):
    """
    🕐 Time synchronization exceptions - When the cosmic clock is wrong
    """
    
    def __init__(self, message: str, os_type: str = None, **kwargs):
        self.os_type = os_type
        super().__init__(message, error_code="TIME_SYNC_ERROR", details={
            'os_type': os_type,
            **kwargs
        })

class NetworkException(BotException):
    """
    🌐 Network-related exceptions - When the digital highways are blocked
    """
    
    def __init__(self, message: str, url: str = None, timeout: int = None, **kwargs):
        self.url = url
        self.timeout = timeout
        super().__init__(message, error_code="NETWORK_ERROR", details={
            'url': url,
            'timeout': timeout,
            **kwargs
        })

class CacheException(BotException):
    """
    💾 Cache-related exceptions - When the memory palace fails
    """
    
    def __init__(self, message: str, cache_name: str = None, key: str = None, **kwargs):
        self.cache_name = cache_name
        self.key = key
        super().__init__(message, error_code="CACHE_ERROR", details={
            'cache_name': cache_name,
            'key': key,
            **kwargs
        })

class StopLossException(BotException):
    """
    🛑 Stop-loss related exceptions - When protection mechanisms fail
    """
    
    def __init__(self, message: str, coin: str = None, price: float = None, **kwargs):
        self.coin = coin
        self.price = price
        super().__init__(message, error_code="STOPLOSS_ERROR", details={
            'coin': coin,
            'price': price,
            **kwargs
        })

class ModelException(BotException):
    """
    🧠 Model-related exceptions - When the AI brain malfunctions
    """
    
    def __init__(self, message: str, model_name: str = None, prediction: str = None, **kwargs):
        self.model_name = model_name
        self.prediction = prediction
        super().__init__(message, error_code="MODEL_ERROR", details={
            'model_name': model_name,
            'prediction': prediction,
            **kwargs
        })

# Convenience functions for common error scenarios
def raise_insufficient_balance(asset: str, required: float, available: float):
    """
    🌟 Convenience function to raise insufficient balance exception
    """
    raise InsufficientBalanceException(asset, required, available)

def raise_invalid_trading_pair(pair: str, exchange: str = None):
    """
    🌟 Convenience function to raise invalid trading pair exception
    """
    raise InvalidTradingPairException(pair, exchange)

def raise_api_error(message: str, api_name: str = "Unknown", status_code: int = None):
    """
    🌟 Convenience function to raise API exception
    """
    if api_name.lower() == "binance":
        raise BinanceAPIException(message, status_code)
    elif api_name.lower() == "bybit":
        raise BybitAPIException(message, status_code)
    else:
        raise APIException(message, api_name, status_code)

def raise_config_error(message: str, key: str = None, value: str = None):
    """
    🌟 Convenience function to raise configuration exception
    """
    raise ConfigurationException(message, key, value)

def raise_validation_error(message: str, field: str = None, value: str = None):
    """
    🌟 Convenience function to raise validation exception
    """
    raise ValidationException(message, field, value)
