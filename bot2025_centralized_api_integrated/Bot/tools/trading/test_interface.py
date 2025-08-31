"""
🌟 Test Trading Interface - The Cosmic Paper Trading Engine
Local test interface for buy/sell operations without API calls
"""

import os
import json
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.centralized_logger import centralized_logger
from ..database.trading_models import Order, Trade, Balance, OrderType, OrderStatus, TradeType, trading_db

@dataclass
class TestBalance:
    """Test balance for paper trading"""
    asset: str
    free: Decimal
    locked: Decimal
    total: Decimal

@dataclass
class TestOrder:
    """Test order for paper trading"""
    order_id: str
    symbol: str
    side: OrderType
    quantity: Decimal
    price: Decimal
    status: OrderStatus
    created_at: datetime
    filled_at: Optional[datetime] = None
    filled_quantity: Decimal = Decimal('0')
    avg_price: Decimal = Decimal('0')

class TestTradingInterface:
    """
    🌟 Test Trading Interface with Local Balance Management
    
    Features:
    - Local test balance management
    - Paper trading simulation
    - Order execution simulation
    - Real-time price simulation
    - Database integration
    """
    
    def __init__(self):
        self.test_balances: Dict[str, TestBalance] = {}
        self.test_orders: Dict[str, TestOrder] = {}
        self.current_prices: Dict[str, Decimal] = {}
        
        # Initialize test balances
        self._init_test_balances()
        
        # Initialize current prices
        self._init_current_prices()
        
        centralized_logger.info('test_interface', '🌟 Test trading interface initialized')
    
    def _init_test_balances(self):
        """Initialize test balances with default values"""
        default_balances = {
            'USDT': TestBalance('USDT', Decimal('10000'), Decimal('0'), Decimal('10000')),
            'BTC': TestBalance('BTC', Decimal('0'), Decimal('0'), Decimal('0')),
            'ETH': TestBalance('ETH', Decimal('0'), Decimal('0'), Decimal('0')),
            'ADA': TestBalance('ADA', Decimal('0'), Decimal('0'), Decimal('0')),
            'DOT': TestBalance('DOT', Decimal('0'), Decimal('0'), Decimal('0'))
        }
        
        self.test_balances = default_balances
        centralized_logger.info('test_interface', '💰 Test balances initialized', {
            'balances': {asset: float(bal.total) for asset, bal in default_balances.items()}
        })
    
    def _init_current_prices(self):
        """Initialize current prices for common pairs"""
        self.current_prices = {
            'BTCUSDT': Decimal('45000'),
            'ETHUSDT': Decimal('3000'),
            'ADAUSDT': Decimal('0.5'),
            'DOTUSDT': Decimal('20')
        }
        centralized_logger.info('test_interface', '📊 Current prices initialized', {
            'prices': {symbol: float(price) for symbol, price in self.current_prices.items()}
        })
    
    def get_balance(self, asset: str) -> Optional[TestBalance]:
        """Get test balance for an asset"""
        return self.test_balances.get(asset)
    
    def get_all_balances(self) -> Dict[str, TestBalance]:
        """Get all test balances"""
        return self.test_balances.copy()
    
    def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current price for a symbol"""
        return self.current_prices.get(symbol)
    
    def update_price(self, symbol: str, new_price: Decimal):
        """Update current price for a symbol"""
        self.current_prices[symbol] = new_price
        centralized_logger.info('test_interface', f'📈 Price updated for {symbol}', {
            'symbol': symbol,
            'new_price': float(new_price)
        })
    
    def _simulate_price_movement(self, symbol: str):
        """Simulate price movement for more realistic trading"""
        import random
        
        current_price = self.current_prices.get(symbol, Decimal('100'))
        
        # Simulate small random price movement (±2%)
        movement_percent = random.uniform(-0.02, 0.02)
        new_price = current_price * (1 + Decimal(str(movement_percent)))
        
        self.update_price(symbol, new_price)
        return new_price
    
    def place_order(self, symbol: str, side: OrderType, quantity: Decimal, 
                   price: Optional[Decimal] = None) -> Optional[TestOrder]:
        """
        🌟 Place a test order
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side (BUY/SELL)
            quantity: Order quantity
            price: Order price (if None, uses current market price)
        
        Returns:
            TestOrder if successful, None if failed
        """
        try:
            # Generate order ID
            order_id = f"test_{uuid.uuid4().hex[:8]}"
            
            # Get current price if not provided
            if price is None:
                price = self.get_current_price(symbol)
                if price is None:
                    centralized_logger.error('test_interface', f'❌ No price available for {symbol}')
                    return None
            
            # Check balance for the order
            if side == OrderType.BUY:
                # Check USDT balance for buy orders
                usdt_balance = self.get_balance('USDT')
                required_usdt = quantity * price
                
                if usdt_balance.free < required_usdt:
                    centralized_logger.error('test_interface', f'❌ Insufficient USDT balance for buy order', {
                        'required': float(required_usdt),
                        'available': float(usdt_balance.free)
                    })
                    return None
                
                # Lock USDT
                usdt_balance.locked += required_usdt
                usdt_balance.free -= required_usdt
                
            elif side == OrderType.SELL:
                # Check asset balance for sell orders
                base_asset = symbol.replace('USDT', '')
                asset_balance = self.get_balance(base_asset)
                
                if asset_balance.free < quantity:
                    centralized_logger.error('test_interface', f'❌ Insufficient {base_asset} balance for sell order', {
                        'required': float(quantity),
                        'available': float(asset_balance.free)
                    })
                    return None
                
                # Lock asset
                asset_balance.locked += quantity
                asset_balance.free -= quantity
            
            # Create test order
            test_order = TestOrder(
                order_id=order_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                status=OrderStatus.PENDING,
                created_at=datetime.now()
            )
            
            # Store order
            self.test_orders[order_id] = test_order
            
            # Log order placement
            centralized_logger.info('test_interface', f'📝 Test order placed', {
                'order_id': order_id,
                'symbol': symbol,
                'side': side.value,
                'quantity': float(quantity),
                'price': float(price)
            })
            
            # Simulate order execution (immediate fill for simplicity)
            self._execute_order(test_order)
            
            return test_order
            
        except Exception as e:
            centralized_logger.error('test_interface', f'❌ Error placing test order: {e}')
            return None
    
    def _execute_order(self, test_order: TestOrder):
        """Execute a test order"""
        try:
            # Simulate price movement
            new_price = self._simulate_price_movement(test_order.symbol)
            
            # Execute at the order price (or current price if market order)
            execution_price = test_order.price
            
            # Update order status
            test_order.status = OrderStatus.FILLED
            test_order.filled_at = datetime.now()
            test_order.filled_quantity = test_order.quantity
            test_order.avg_price = execution_price
            
            # Update balances
            if test_order.side == OrderType.BUY:
                # Buy order: spend USDT, receive asset
                usdt_balance = self.get_balance('USDT')
                base_asset = test_order.symbol.replace('USDT', '')
                asset_balance = self.get_balance(base_asset)
                
                # Unlock USDT and spend it
                usdt_balance.locked -= test_order.quantity * execution_price
                usdt_balance.total -= test_order.quantity * execution_price
                
                # Receive asset
                asset_balance.free += test_order.quantity
                asset_balance.total += test_order.quantity
                
            elif test_order.side == OrderType.SELL:
                # Sell order: spend asset, receive USDT
                base_asset = test_order.symbol.replace('USDT', '')
                asset_balance = self.get_balance(base_asset)
                usdt_balance = self.get_balance('USDT')
                
                # Unlock asset and spend it
                asset_balance.locked -= test_order.quantity
                asset_balance.total -= test_order.quantity
                
                # Receive USDT
                usdt_balance.free += test_order.quantity * execution_price
                usdt_balance.total += test_order.quantity * execution_price
            
            # Log execution
            centralized_logger.info('test_interface', f'✅ Test order executed', {
                'order_id': test_order.order_id,
                'symbol': test_order.symbol,
                'side': test_order.side.value,
                'quantity': float(test_order.quantity),
                'execution_price': float(execution_price)
            })
            
            # Save to database
            self._save_order_to_db(test_order)
            
        except Exception as e:
            centralized_logger.error('test_interface', f'❌ Error executing test order: {e}')
    
    def _save_order_to_db(self, test_order: TestOrder):
        """Save test order to database"""
        try:
            # Create database order
            db_order = Order(
                id=0,  # Will be set by database
                order_id=test_order.order_id,
                symbol=test_order.symbol,
                side=test_order.side,
                quantity=test_order.quantity,
                price=test_order.price,
                status=test_order.status,
                trade_type=TradeType.TEST,
                created_at=test_order.created_at
            )
            
            # Insert into database
            order_id = trading_db.insert_order(db_order)
            
            if order_id:
                centralized_logger.info('test_interface', f'💾 Test order saved to database', {
                    'order_id': test_order.order_id,
                    'db_id': order_id
                })
            
        except Exception as e:
            centralized_logger.error('test_interface', f'❌ Error saving order to database: {e}')
    
    def get_order(self, order_id: str) -> Optional[TestOrder]:
        """Get test order by ID"""
        return self.test_orders.get(order_id)
    
    def get_all_orders(self) -> List[TestOrder]:
        """Get all test orders"""
        return list(self.test_orders.values())
    
    def get_orders_by_symbol(self, symbol: str) -> List[TestOrder]:
        """Get test orders for a specific symbol"""
        return [order for order in self.test_orders.values() if order.symbol == symbol]
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel a test order"""
        test_order = self.test_orders.get(order_id)
        if not test_order:
            centralized_logger.error('test_interface', f'❌ Order not found: {order_id}')
            return False
        
        if test_order.status != OrderStatus.PENDING:
            centralized_logger.error('test_interface', f'❌ Cannot cancel non-pending order: {order_id}')
            return False
        
        # Update order status
        test_order.status = OrderStatus.CANCELLED
        
        # Unlock balances
        if test_order.side == OrderType.BUY:
            usdt_balance = self.get_balance('USDT')
            usdt_balance.free += test_order.quantity * test_order.price
            usdt_balance.locked -= test_order.quantity * test_order.price
        elif test_order.side == OrderType.SELL:
            base_asset = test_order.symbol.replace('USDT', '')
            asset_balance = self.get_balance(base_asset)
            asset_balance.free += test_order.quantity
            asset_balance.locked -= test_order.quantity
        
        centralized_logger.info('test_interface', f'❌ Test order cancelled', {
            'order_id': order_id,
            'symbol': test_order.symbol
        })
        
        return True
    
    def get_trading_summary(self) -> Dict[str, Any]:
        """Get trading summary"""
        total_orders = len(self.test_orders)
        filled_orders = len([o for o in self.test_orders.values() if o.status == OrderStatus.FILLED])
        cancelled_orders = len([o for o in self.test_orders.values() if o.status == OrderStatus.CANCELLED])
        
        total_volume = sum(o.quantity * o.price for o in self.test_orders.values() if o.status == OrderStatus.FILLED)
        
        return {
            'total_orders': total_orders,
            'filled_orders': filled_orders,
            'cancelled_orders': cancelled_orders,
            'total_volume': float(total_volume),
            'balances': {asset: float(bal.total) for asset, bal in self.test_balances.items()},
            'current_prices': {symbol: float(price) for symbol, price in self.current_prices.items()}
        }

# Global test interface instance
test_interface = TestTradingInterface()

# Convenience functions
def test_buy(symbol: str, quantity: Decimal, price: Optional[Decimal] = None) -> Optional[TestOrder]:
    """Place a test buy order"""
    return test_interface.place_order(symbol, OrderType.BUY, quantity, price)

def test_sell(symbol: str, quantity: Decimal, price: Optional[Decimal] = None) -> Optional[TestOrder]:
    """Place a test sell order"""
    return test_interface.place_order(symbol, OrderType.SELL, quantity, price)

def get_test_balance(asset: str) -> Optional[TestBalance]:
    """Get test balance for an asset"""
    return test_interface.get_balance(asset)

def get_test_summary() -> Dict[str, Any]:
    """Get test trading summary"""
    return test_interface.get_trading_summary()
