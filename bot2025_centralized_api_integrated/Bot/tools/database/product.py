"""
🏪 Product Class - The Cosmic Trading Instrument
Represents trading products/instruments with comprehensive metadata
"""

from datetime import datetime
from typing import Optional, Dict, Any

class Product:
    """
    🏪 The Cosmic Trading Product - Complete representation of trading instruments
    Contains all metadata needed for intelligent trading decisions
    """
    
    def __init__(self, 
                 symbol: str,
                 base_asset: str,
                 quote_asset: str,
                 exchange: str = "binance",
                 status: str = "TRADING",
                 price_precision: int = 8,
                 quantity_precision: int = 8,
                 min_price: float = 0.0,
                 max_price: float = float('inf'),
                 min_quantity: float = 0.0,
                 max_quantity: float = float('inf'),
                 step_size: float = 0.00000001,
                 tick_size: float = 0.00000001,
                 min_notional: float = 0.0,
                 max_notional: float = float('inf'),
                 is_spot: bool = True,
                 is_margin: bool = False,
                 is_futures: bool = False,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        """
        🌟 Initialize a new trading product with cosmic precision
        
        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            base_asset: Base asset (e.g., "BTC")
            quote_asset: Quote asset (e.g., "USDT")
            exchange: Exchange name (default: "binance")
            status: Trading status (default: "TRADING")
            price_precision: Price decimal precision
            quantity_precision: Quantity decimal precision
            min_price: Minimum allowed price
            max_price: Maximum allowed price
            min_quantity: Minimum allowed quantity
            max_quantity: Maximum allowed quantity
            step_size: Minimum quantity step size
            tick_size: Minimum price tick size
            min_notional: Minimum order value
            max_notional: Maximum order value
            is_spot: Is spot trading enabled
            is_margin: Is margin trading enabled
            is_futures: Is futures trading enabled
            created_at: Product creation timestamp
            updated_at: Last update timestamp
        """
        self.symbol = symbol.upper()
        self.base_asset = base_asset.upper()
        self.quote_asset = quote_asset.upper()
        self.exchange = exchange.lower()
        self.status = status.upper()
        self.price_precision = price_precision
        self.quantity_precision = quantity_precision
        self.min_price = min_price
        self.max_price = max_price
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.step_size = step_size
        self.tick_size = tick_size
        self.min_notional = min_notional
        self.max_notional = max_notional
        self.is_spot = is_spot
        self.is_margin = is_margin
        self.is_futures = is_futures
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
        # Additional metadata
        self.current_price: Optional[float] = None
        self.volume_24h: Optional[float] = None
        self.price_change_24h: Optional[float] = None
        self.price_change_percent_24h: Optional[float] = None
        self.high_24h: Optional[float] = None
        self.low_24h: Optional[float] = None
        
    def is_trading(self) -> bool:
        """
        🔍 Check if the product is currently trading
        """
        return self.status == "TRADING"
    
    def is_valid_price(self, price: float) -> bool:
        """
        ✅ Validate if a price is within allowed range
        """
        return self.min_price <= price <= self.max_price
    
    def is_valid_quantity(self, quantity: float) -> bool:
        """
        ✅ Validate if a quantity is within allowed range
        """
        return self.min_quantity <= quantity <= self.max_quantity
    
    def is_valid_notional(self, notional: float) -> bool:
        """
        ✅ Validate if order value is within allowed range
        """
        return self.min_notional <= notional <= self.max_notional
    
    def format_price(self, price: float) -> str:
        """
        🎯 Format price according to precision rules
        """
        return f"{price:.{self.price_precision}f}"
    
    def format_quantity(self, quantity: float) -> str:
        """
        🎯 Format quantity according to precision rules
        """
        return f"{quantity:.{self.quantity_precision}f}"
    
    def get_precise_quantity(self, quantity: float) -> float:
        """
        ⚖️ Get precise quantity according to step size rules
        """
        import math
        step_precision = int(round(-math.log10(self.step_size)))
        return round(quantity, step_precision)
    
    def get_precise_price(self, price: float) -> float:
        """
        ⚖️ Get precise price according to tick size rules
        """
        import math
        tick_precision = int(round(-math.log10(self.tick_size)))
        return round(price, tick_precision)
    
    def update_market_data(self, 
                          current_price: Optional[float] = None,
                          volume_24h: Optional[float] = None,
                          price_change_24h: Optional[float] = None,
                          price_change_percent_24h: Optional[float] = None,
                          high_24h: Optional[float] = None,
                          low_24h: Optional[float] = None):
        """
        📊 Update market data for the product
        """
        if current_price is not None:
            self.current_price = current_price
        if volume_24h is not None:
            self.volume_24h = volume_24h
        if price_change_24h is not None:
            self.price_change_24h = price_change_24h
        if price_change_percent_24h is not None:
            self.price_change_percent_24h = price_change_percent_24h
        if high_24h is not None:
            self.high_24h = high_24h
        if low_24h is not None:
            self.low_24h = low_24h
        
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        📋 Convert product to dictionary for serialization
        """
        return {
            'symbol': self.symbol,
            'base_asset': self.base_asset,
            'quote_asset': self.quote_asset,
            'exchange': self.exchange,
            'status': self.status,
            'price_precision': self.price_precision,
            'quantity_precision': self.quantity_precision,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'min_quantity': self.min_quantity,
            'max_quantity': self.max_quantity,
            'step_size': self.step_size,
            'tick_size': self.tick_size,
            'min_notional': self.min_notional,
            'max_notional': self.max_notional,
            'is_spot': self.is_spot,
            'is_margin': self.is_margin,
            'is_futures': self.is_futures,
            'current_price': self.current_price,
            'volume_24h': self.volume_24h,
            'price_change_24h': self.price_change_24h,
            'price_change_percent_24h': self.price_change_percent_24h,
            'high_24h': self.high_24h,
            'low_24h': self.low_24h,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """
        🔄 Create product from dictionary
        """
        # Parse datetime strings
        created_at = None
        updated_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            updated_at = datetime.fromisoformat(data['updated_at'])
        
        return cls(
            symbol=data['symbol'],
            base_asset=data['base_asset'],
            quote_asset=data['quote_asset'],
            exchange=data.get('exchange', 'binance'),
            status=data.get('status', 'TRADING'),
            price_precision=data.get('price_precision', 8),
            quantity_precision=data.get('quantity_precision', 8),
            min_price=data.get('min_price', 0.0),
            max_price=data.get('max_price', float('inf')),
            min_quantity=data.get('min_quantity', 0.0),
            max_quantity=data.get('max_quantity', float('inf')),
            step_size=data.get('step_size', 0.00000001),
            tick_size=data.get('tick_size', 0.00000001),
            min_notional=data.get('min_notional', 0.0),
            max_notional=data.get('max_notional', float('inf')),
            is_spot=data.get('is_spot', True),
            is_margin=data.get('is_margin', False),
            is_futures=data.get('is_futures', False),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def __repr__(self) -> str:
        """
        🎭 String representation of the product
        """
        return (f"Product(symbol='{self.symbol}', "
                f"base_asset='{self.base_asset}', "
                f"quote_asset='{self.quote_asset}', "
                f"exchange='{self.exchange}', "
                f"status='{self.status}', "
                f"current_price={self.current_price})")
    
    def __str__(self) -> str:
        """
        📝 Human-readable string representation
        """
        return f"{self.symbol} ({self.base_asset}/{self.quote_asset}) on {self.exchange}"


class ProductManager:
    """
    🏪 Product Manager - The Cosmic Product Registry
    Manages all trading products with intelligent caching and validation
    """
    
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.by_exchange: Dict[str, Dict[str, Product]] = {}
        self.by_base_asset: Dict[str, Dict[str, Product]] = {}
        self.by_quote_asset: Dict[str, Dict[str, Product]] = {}
    
    def add_product(self, product: Product) -> None:
        """
        ➕ Add a product to the registry
        """
        self.products[product.symbol] = product
        
        # Index by exchange
        if product.exchange not in self.by_exchange:
            self.by_exchange[product.exchange] = {}
        self.by_exchange[product.exchange][product.symbol] = product
        
        # Index by base asset
        if product.base_asset not in self.by_base_asset:
            self.by_base_asset[product.base_asset] = {}
        self.by_base_asset[product.base_asset][product.symbol] = product
        
        # Index by quote asset
        if product.quote_asset not in self.by_quote_asset:
            self.by_quote_asset[product.quote_asset] = {}
        self.by_quote_asset[product.quote_asset][product.symbol] = product
    
    def get_product(self, symbol: str) -> Optional[Product]:
        """
        🔍 Get product by symbol
        """
        return self.products.get(symbol.upper())
    
    def get_products_by_exchange(self, exchange: str) -> Dict[str, Product]:
        """
        🔍 Get all products for a specific exchange
        """
        return self.by_exchange.get(exchange.lower(), {})
    
    def get_products_by_base_asset(self, base_asset: str) -> Dict[str, Product]:
        """
        🔍 Get all products for a specific base asset
        """
        return self.by_base_asset.get(base_asset.upper(), {})
    
    def get_products_by_quote_asset(self, quote_asset: str) -> Dict[str, Product]:
        """
        🔍 Get all products for a specific quote asset
        """
        return self.by_quote_asset.get(quote_asset.upper(), {})
    
    def get_trading_products(self) -> Dict[str, Product]:
        """
        🔍 Get all products that are currently trading
        """
        return {symbol: product for symbol, product in self.products.items() 
                if product.is_trading()}
    
    def validate_order(self, symbol: str, price: float, quantity: float) -> bool:
        """
        ✅ Validate order parameters for a product
        """
        product = self.get_product(symbol)
        if not product:
            return False
        
        notional = price * quantity
        return (product.is_valid_price(price) and 
                product.is_valid_quantity(quantity) and 
                product.is_valid_notional(notional))
    
    def get_all_products(self) -> Dict[str, Product]:
        """
        📋 Get all products
        """
        return self.products.copy()
    
    def clear(self) -> None:
        """
        🗑️ Clear all products
        """
        self.products.clear()
        self.by_exchange.clear()
        self.by_base_asset.clear()
        self.by_quote_asset.clear()


# Global product manager instance
product_manager = ProductManager()
