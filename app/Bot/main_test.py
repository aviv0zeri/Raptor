"""
🌟 Test Main - The Cosmic Test Trading Engine
Clone of main.py that uses test interface for safe testing
"""

import os
import time
import asyncio
import multiprocessing
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import our modular utilities
from .tools.utils.centralized_logger import centralized_logger
from .tools.utils.sounds_interface import (
    play_order_executed, play_order_cancelled, play_error_alert,
    play_success_confirmation, play_warning_notification, play_trade_signal,
    play_system_start, play_system_stop, play_balance_update
)
from .tools.database.trading_models import OrderType, OrderStatus, TradeType
from .tools.trading.test_interface import test_interface, test_buy, test_sell, get_test_summary
from .tools.utils.cache_manager import cache_manager
from .tools.config.config_manager import config_manager
from .tools.utils.wallet_utils import print_wallet, get_wallet_summary
from .exceptions.bot_exceptions import (
    BotException, TradingException, DatabaseException, 
    ConfigurationException, raise_insufficient_balance
)

# Initialize colorama for colored terminal output
from colorama import Fore, Style, init
init(autoreset=True)

class TestTradingBot:
    """
    🌟 Test Trading Bot - Safe Testing Environment
    
    Features:
    - Uses test interface for paper trading
    - Simulates real trading conditions
    - Safe testing without real money
    - Full logging and monitoring
    """
    
    def __init__(self):
        self.is_running = False
        self.test_mode = True
        self.current_signal = None
        self.last_trade_time = None
        
        # Initialize components
        centralized_logger.info('test_bot', '🌟 Test trading bot initialized')
        play_system_start({'bot_type': 'test_bot'})
        
        # Test configuration
        self.test_config = {
            'min_trade_interval': 60,  # seconds
            'max_position_size': Decimal('100'),  # USDT
            'default_quantity': Decimal('10'),  # USDT
            'symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT']
        }
    
    def start(self):
        """Start the test trading bot"""
        try:
            self.is_running = True
            centralized_logger.info('test_bot', '🚀 Test trading bot started')
            play_system_start({'status': 'started'})
            
            # Start main trading loop
            self._run_trading_loop()
            
        except KeyboardInterrupt:
            centralized_logger.info('test_bot', '⏹️ Test trading bot stopped by user')
        except Exception as e:
            centralized_logger.error('test_bot', f'❌ Test trading bot error: {e}')
        finally:
            self.stop()
    
    def stop(self):
        """Stop the test trading bot"""
        self.is_running = False
        centralized_logger.info('test_bot', '🛑 Test trading bot stopped')
        play_system_stop({'status': 'stopped'})
    
    def _run_trading_loop(self):
        """Main trading loop for testing"""
        centralized_logger.info('test_bot', '🔄 Starting test trading loop')
        
        while self.is_running:
            try:
                # Get trading signal (simulated)
                signal = self._get_test_signal()
                
                if signal:
                    self._process_trade_signal(signal)
                
                # Update test balances display
                self._display_test_status()
                
                # Wait before next iteration
                time.sleep(10)  # 10 second intervals for testing
                
            except Exception as e:
                centralized_logger.error('test_bot', f'❌ Error in trading loop: {e}')
                time.sleep(5)
    
    def _get_test_signal(self) -> Optional[Dict[str, Any]]:
        """Get simulated trading signal"""
        import random
        
        # Simulate signal generation (50% chance of signal)
        if random.random() < 0.5:
            return None
        
        # Random symbol and action
        symbol = random.choice(self.test_config['symbols'])
        action = random.choice(['BUY', 'SELL'])
        
        # Get current price
        current_price = test_interface.get_current_price(symbol)
        if not current_price:
            return None
        
        # Calculate quantity based on max position size
        quantity = self.test_config['max_position_size'] / current_price
        
        signal = {
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'price': current_price,
            'confidence': random.uniform(0.6, 0.9),
            'timestamp': datetime.now()
        }
        
        centralized_logger.info('test_bot', f'📊 Test signal generated', {
            'symbol': symbol,
            'action': action,
            'quantity': float(quantity),
            'price': float(current_price),
            'confidence': signal['confidence']
        })
        
        # Play trade signal sound
        play_trade_signal({
            'symbol': symbol,
            'action': action,
            'confidence': signal['confidence']
        })
        
        return signal
    
    def _process_trade_signal(self, signal: Dict[str, Any]):
        """Process trading signal using test interface"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            quantity = signal['quantity']
            price = signal['price']
            
            # Check if enough time has passed since last trade
            if self.last_trade_time:
                time_since_last = (datetime.now() - self.last_trade_time).total_seconds()
                if time_since_last < self.test_config['min_trade_interval']:
                    centralized_logger.info('test_bot', f'⏰ Skipping trade - too soon since last trade')
                    return
            
            # Execute test order
            if action == 'BUY':
                order = test_buy(symbol, quantity, price)
                if order:
                    centralized_logger.info('test_bot', f'✅ Test buy order executed', {
                        'order_id': order.order_id,
                        'symbol': symbol,
                        'quantity': float(quantity),
                        'price': float(price)
                    })
                    play_order_executed({
                        'order_id': order.order_id,
                        'symbol': symbol,
                        'side': 'BUY',
                        'quantity': float(quantity),
                        'price': float(price)
                    })
                    self.last_trade_time = datetime.now()
                else:
                    centralized_logger.error('test_bot', f'❌ Test buy order failed')
                    play_error_alert({'error': 'buy_order_failed', 'symbol': symbol})
                    
            elif action == 'SELL':
                order = test_sell(symbol, quantity, price)
                if order:
                    centralized_logger.info('test_bot', f'✅ Test sell order executed', {
                        'order_id': order.order_id,
                        'symbol': symbol,
                        'quantity': float(quantity),
                        'price': float(price)
                    })
                    play_order_executed({
                        'order_id': order.order_id,
                        'symbol': symbol,
                        'side': 'SELL',
                        'quantity': float(quantity),
                        'price': float(price)
                    })
                    self.last_trade_time = datetime.now()
                else:
                    centralized_logger.error('test_bot', f'❌ Test sell order failed')
                    play_error_alert({'error': 'sell_order_failed', 'symbol': symbol})
            
        except Exception as e:
            centralized_logger.error('test_bot', f'❌ Error processing trade signal: {e}')
    
    def _display_test_status(self):
        """Display current test status"""
        try:
            summary = get_test_summary()
            
            print(f"\n{Fore.CYAN}=== TEST TRADING STATUS ==={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}📊 Orders: {summary['total_orders']} | Filled: {summary['filled_orders']} | Cancelled: {summary['cancelled_orders']}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}💰 Total Volume: ${summary['total_volume']:.2f}{Style.RESET_ALL}")
            
            print(f"\n{Fore.BLUE}=== TEST BALANCES ==={Style.RESET_ALL}")
            for asset, balance in summary['balances'].items():
                if balance > 0:
                    print(f"{Fore.WHITE}{asset}: {balance:.8f}{Style.RESET_ALL}")
            
            print(f"\n{Fore.MAGENTA}=== CURRENT PRICES ==={Style.RESET_ALL}")
            for symbol, price in summary['current_prices'].items():
                print(f"{Fore.WHITE}{symbol}: ${price:.2f}{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}========================{Style.RESET_ALL}\n")
            
        except Exception as e:
            centralized_logger.error('test_bot', f'❌ Error displaying status: {e}')
    
    def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        return {
            'is_running': self.is_running,
            'test_mode': self.test_mode,
            'current_signal': self.current_signal,
            'last_trade_time': self.last_trade_time.isoformat() if self.last_trade_time else None,
            'test_summary': get_test_summary()
        }

# Global test bot instance
test_bot = TestTradingBot()

def main():
    """Main function for test trading bot"""
    try:
        print(f"{Fore.CYAN}🌟 Starting Test Trading Bot{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️ This is a TEST environment - no real money will be used{Style.RESET_ALL}")
        
        # Start the test bot
        test_bot.start()
        
    except Exception as e:
        centralized_logger.critical('test_bot', f'🚨 Critical error in test bot: {e}')
        raise

if __name__ == "__main__":
    main()
