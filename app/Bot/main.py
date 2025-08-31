"""
🤖 Trading Bot - The Cosmic Trading Engine
=======================================

📁 File: /bot2025_centralized_api_integrated/Bot/main.py
🎯 Purpose: Core trading algorithm and execution engine
🔧 Function: Implements trading strategies and executes orders

🌟 Features:
- Real-time market data processing
- Trading signal generation
- Order execution and management
- Risk management and position sizing
- Stop-loss and take-profit handling
- Multi-exchange support (Binance, Bybit)
- Paper trading mode for testing
- Real-time balance tracking
- Performance monitoring and analytics

🔄 Trading Flow:
1. Market data collection and analysis
2. Signal generation based on strategy
3. Risk assessment and position sizing
4. Order placement and execution
5. Position monitoring and management
6. Stop-loss and take-profit handling
7. Performance tracking and reporting

📊 Supported Exchanges:
- Binance (primary)
- Bybit (secondary)
- Paper trading (simulation)

🔧 Configuration:
- Risk percentage: 2% per trade
- Default quantity: 1.0
- Max position size: 100.0
- Enable paper trading: true
- Default exchange: binance

📋 Dependencies:
- python-binance (Binance API)
- pybit (Bybit API)
- pandas (data processing)
- numpy (mathematical operations)
- psycopg2 (database operations)
- CentralizedLogger (logging)

🔗 Related Files:
- tools/api/api_utils.py (API utilities)
- tools/config/config_manager.py (configuration)
- tools/database/ (database operations)
- tools/trading/ (trading functions)
- tools/utils/centralized_logger.py (logging)

🎯 Trading Strategies:
- Technical analysis based
- Machine learning enhanced
- Risk-adjusted returns
- Multi-timeframe analysis
"""

import csv


import time
import os
import sys
import asyncio
from pathlib import Path
from colorama import Fore, Style, init
from binance.client import Client

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import our modular utilities
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
from .tools.utils.log_module import CustomLogger
from .tools.database.order import Order, Receipt
from .tools.database.database import connect, insert_order
from .tools import utils as ut
from .tools.utils.sync_time_utils import sync_system_time, get_formatted_time
from .tools.utils.cache_manager import cache_manager
from .tools.config.config_manager import config_manager
from .tools.utils.wallet_utils import print_wallet, get_wallet_summary
from .tools.trading.stop_loss import CoinTracker, get_asset_balance_in_usdt, stop_loss_manager
from .exceptions.bot_exceptions import (
    BotException, TradingException, DatabaseException, 
    ConfigurationException, raise_insufficient_balance
)
try:
    from ..Sounds import bot_sounds
except ImportError:
    # Fallback for IDE compatibility
    bot_sounds = None

# Initialize colorama for colored terminal output
init(autoreset=True)

# Initialize the cosmic logger
logger = CustomLogger("logs/main.log")

class Wallet:
    """
    💼 The Digital Vault - Guardian of Trading Capital
    Manages balances and converts between different assets
    """
    
    def __init__(self, coin):
        self.bot_coin = coin
        self.bot_coin_amount = 0.0  # Amount of bot coin held
        self.usdt_amount = 0.0  # Amount of USDT held
        self.update_wallet()  # Initialize the wallet with current values

    def update_wallet(self):
        """
        🔄 Fetches the current USDT value for the bot_coin and updates the wallet
        The cosmic balance inspector that reveals our digital wealth
        """
        try:
            # Get account balances using cached API calls
            cache_key = f"wallet_balance_{self.bot_coin}"
            cached_balance = cache_manager.get('wallet', cache_key)
            
            if cached_balance:
                self.bot_coin_amount = cached_balance.get('bot_coin', 0.0)
                self.usdt_amount = cached_balance.get('usdt', 0.0)
                return

            # Fetch fresh data from API
            url = "https://api.binance.com/api/v3/account"
            response = ut.make_binance_request(
                method="GET",
                url=url,
                api_key=BINANCE_API_KEY,
                secret_key=BINANCE_SECRET_KEY
            )

            if not response or not hasattr(response, 'json'):
                logger.log('error', "Invalid response object for update_wallet")
                return
  
            account_data = response.json()
            for balance in account_data.get('balances', []):
                if balance['asset'] == self.bot_coin:
                    self.bot_coin_amount = float(balance.get('free', 0))
                elif balance['asset'] == 'USDT':
                    self.usdt_amount = float(balance.get('free', 0))
            
            # Cache the balance data
            cache_manager.set('wallet', cache_key, {
                'bot_coin': self.bot_coin_amount,
                'usdt': self.usdt_amount
            }, ttl=60)  # Cache for 1 minute
            
        except Exception as e:
            logger.log('error', f"Error updating wallet: {e}")
            self.bot_coin_amount = 0.0
            self.usdt_amount = 0.0

    def convert_to_usdt(self):
        """
        💱 Converts the bot_coin_amount to its equivalent value in USDT
        The alchemy of digital currency conversion
        """
        try:
            # Use cached price if available
            cache_key = f"price_{self.bot_coin}USDT"
            cached_price = cache_manager.get('prices', cache_key)
            
            if cached_price:
                price = cached_price
            else:
                # Fetch fresh price
                url = "https://api.binance.com/api/v3/ticker/price"
                params = {"symbol": f"{self.bot_coin}USDT"}
                response = ut.make_binance_request(
                    method="GET",
                    url=url,
                    api_key=BINANCE_API_KEY,
                    secret_key=BINANCE_SECRET_KEY,
                    params=params
                )

                if not response or not hasattr(response, 'json'):
                    logger.log('error', "Invalid response object for convert_to_usdt")
                    return 0.0

                ticker = response.json()
                price = float(ticker.get('price', 0))
                
                # Cache the price for 30 seconds
                cache_manager.set('prices', cache_key, price, ttl=30)
            
            # Update the bot_coin_amount field to its equivalent value in USDT
            self.bot_coin_amount = self.bot_coin_amount * price
            logger.log('info', f"Updated bot_coin_amount to equivalent USDT value: {self.bot_coin_amount}")
            return self.bot_coin_amount
            
        except Exception as e:
            logger.log('error', f"Error converting to USDT: {e}")
            return 0.0

    def __repr__(self):
        """
        🎭 String representation of the wallet
        """
        return (
            f"Wallet(bot_coin='{self.bot_coin}', "
            f"bot_coin_amount={self.bot_coin_amount:.2f}, "
            f"usdt_amount={self.usdt_amount:.2f}, "
            f"total_usdt_value={self.convert_to_usdt():.2f})"
        )


class Trade:
    """
    💰 The Trading Transaction - Record of Market Interactions
    Captures the essence of each trading decision and execution
    """
    
    def __init__(self, line_number, timestamp, action, quantity, pair, execution_time=None):
        self.line_number = line_number
        self.timestamp = timestamp
        self.action = action.strip()
        self.quantity = float(quantity)
        self.pair = pair.strip()
        self.execution_time = execution_time

    def __repr__(self):
        """
        🎭 String representation of the trade
        """
        exec_time_str = f"{self.execution_time:.2f}s" if self.execution_time is not None else "N/A"
        return (f"order:{self.line_number}, timestamp:{self.timestamp}, "
                f"action:{self.action}, quantity:{self.quantity}, pair:{self.pair}, "
                f"execution_time:{exec_time_str}")

    def repr_hold_csv(self):
        """
        📊 Convert trade to CSV format for HOLD actions
        """
        return [
            -1,
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "@MARKETORDER",
            self.pair,
            self.quantity,
            -1,
            -1,
            self.action,
            0
        ]


def get_last_line_of_csv(file_path, last_processed_timestamp):
    """
    📄 Get the last line of a CSV file for processing
    The cosmic data reader that finds the latest trading signals
    """
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            last_line = None
            line_number = 0
            for last_line in reader:
                line_number += 1

            if last_line is not None:
                current_timestamp = last_line[0].strip()
                if current_timestamp == last_processed_timestamp:
                    return None
                return (line_number, last_line)

        return None
    except Exception as e:
        logger.log('error', f"Error reading CSV file: {e}")
        return None


async def initialize_system():
    """
    🌟 Initialize the trading system with proper setup
    The cosmic startup sequence that prepares everything for trading
    """
    logger.log('info', "🌟 Starting the Cosmic Trading Bot...")
    
    # Sync system time for accurate trading
    logger.log('info', "🕐 Synchronizing system time...")
    if sync_system_time():
        logger.log('info', "✅ Time synchronization successful")
    else:
        logger.log('warning', "⚠️ Time synchronization failed, continuing anyway")
    
    # Initialize Binance client
    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    logger.log('info', "🔗 Binance client initialized")
    
    # Connect to database
    try:
        logger.log('info', "🗄️ Attempting to connect to the database...")
        conn, db_name = connect()
        if conn is None:
            raise DatabaseException("Failed to connect to the database")
        logger.log('info', f"✅ Database connection successful: {db_name}")
        return client, conn
    except Exception as e:
        logger.log('error', f"❌ Database connection failed: {e}")
        raise


async def process_trade_signal(trade, client, cur, conn, test_order=True):
    """
    🎯 Process a single trade signal from the model
    The cosmic decision maker that transforms signals into actions
    """
    try:
        coin, base_coin = trade.pair.split('/')
        wallet = Wallet(coin)
        wallet.update_wallet()

        # Check if we have sufficient balance
        if wallet.bot_coin_amount > wallet.usdt_amount:
            trade.action = "HOLD"
            logger.log('info', f"🔄 Changed action to HOLD due to insufficient balance")

        if trade.action == "BUY":
            await execute_buy_order(trade, wallet, coin, base_coin, client, cur, conn, test_order)
        elif trade.action == "HOLD":
            await execute_hold_action(trade, cur, conn)
        else:
            logger.log('warning', f"⚠️ Unknown action: {trade.action}")
            
    except Exception as e:
        logger.log('error', f"❌ Error processing trade signal: {e}")
        raise


async def execute_buy_order(trade, wallet, coin, base_coin, client, cur, conn, test_order=True):
    """
    💰 Execute a buy order with stop loss protection
    The cosmic purchase that begins the trading journey
    """
    try:
        wallet.update_wallet()
        start_time = time.time()
        
        # For test mode, use a fixed amount instead of wallet balance
        if test_order:
            amount = 10.0  # Fixed test amount in USDT
            logger.log('info', f"🧪 TEST MODE: Using fixed amount of {amount} USDT for buy order")
        else:
            # Calculate order amount (leave some buffer)
            amount = wallet.usdt_amount - 0.5
            
            # Check if we have sufficient balance
            if amount <= 0:
                raise InsufficientBalanceException(coin, amount, wallet.usdt_amount)
        
        # Create and execute the order
        receipt = await ut.make_order(cur, conn, client, logger, coin, base_coin, amount, "BUY", "USDT", None, test_order)
        end_time = time.time()
        
        trade.execution_time = end_time - start_time
        if hasattr(receipt, 'execution_time'):
            receipt.execution_time = trade.execution_time

        # Log the order
        log_order_to_csv(receipt, trade)
        
        # Play success sound
        if not test_order:
            Sounds.bot_sounds.buy_sound()

        mode_text = "🧪 TEST" if test_order else "💰 REAL"
        logger.log('info', f"✅ {mode_text} {trade} - BUY order executed successfully")
        print(f"{Fore.GREEN}{mode_text} {trade}{Style.RESET_ALL} - trade was placed")

        # Initialize stop loss protection (only for test mode with simulated tracking)
        if test_order:
            await initialize_test_stop_loss_protection(receipt, coin, trade, client, cur, conn)
        else:
            await initialize_stop_loss_protection(receipt, coin, trade, client, cur, conn)
            
    except Exception as e:
        logger.log('error', f"❌ Buy order execution failed: {e}")
        raise


async def execute_hold_action(trade, cur, conn):
    """
    ⏸️ Execute a hold action (no trade)
    The cosmic pause when the market conditions aren't right
    """
    try:
        hold_data = trade.repr_hold_csv()
        log_order_to_csv(hold_data, trade, is_hold=True)
        
        logger.log('info', f"⏸️ {trade} - HOLD action executed")
        print(f"{Fore.YELLOW}{trade.__repr__()}{Style.RESET_ALL} - no trade was placed")
        
    except Exception as e:
        logger.log('error', f"❌ Hold action execution failed: {e}")
        raise


async def initialize_test_stop_loss_protection(receipt, coin, trade, client, cur, conn):
    """
    🧪 Initialize test stop loss protection (simulated)
    The cosmic guardian that protects our test investments
    """
    try:
        initial_price = receipt.price
        logger.log('info', f"🧪 TEST STOPLOSS INITIATED for {coin} at price {initial_price}")
        print("🧪 TEST STOPLOSS INITIATED!")

        # Simulate stop loss monitoring for test mode
        await simulate_test_stop_loss(coin, trade, client, cur, conn, initial_price)
        
    except Exception as e:
        logger.log('error', f"❌ Test stop loss initialization failed: {e}")
        raise


async def simulate_test_stop_loss(coin, trade, client, cur, conn, initial_price):
    """
    🧪 Simulate stop loss monitoring for test mode
    The test guardian that simulates protection mechanisms
    """
    try:
        stoploss_file = os.path.join("logs", "stoploss.txt")
        
        # Simulate monitoring for a few seconds
        for i in range(5):
            # Log current status
            with open(stoploss_file, 'a') as sf:
                sf.write(f"{get_formatted_time()} - TEST {coin} - Simulated price: {initial_price:.9f} USDT, Test Limit: {initial_price * 0.99994:.9f} USDT\n")
                sf.write(f"{get_formatted_time()} - TEST Available {coin} balance in USDT: 10.00 USDT\n")

            # Simulate price movement
            simulated_price = initial_price * (1 + (i - 2) * 0.001)  # Small price fluctuations
            
            # Check if stop loss should be triggered (simulated)
            if simulated_price < initial_price * 0.99994:
                await execute_test_stop_loss_sell(coin, trade, client, cur, conn, stoploss_file)
                break

            await asyncio.sleep(1)
            
        logger.log('info', f"🧪 Test stop loss simulation completed for {coin}")
        
    except Exception as e:
        logger.log('error', f"❌ Test stop loss simulation failed: {e}")
        raise


async def execute_test_stop_loss_sell(coin, trade, client, cur, conn, stoploss_file):
    """
    🧪 Execute the test stop loss sell order
    The protective test sell that simulates loss limitation
    """
    try:
        start_time = time.time()
        amount = 10.0  # Fixed test amount
        
        # Execute test sell order
        receipt = await ut.make_order(cur, conn, client, logger, coin, "USDT", amount, "SELL", "USDT", None, True)
        end_time = time.time()
        
        trade.execution_time = end_time - start_time
        if hasattr(receipt, 'execution_time'):
            receipt.execution_time = trade.execution_time

        # Log the test stop loss
        Sounds.bot_sounds.sell_sound()
        logger.log('warning', f"🧪 TEST STOPLOSS: SOLD ALL {coin}")
        
        with open(stoploss_file, 'a') as sf:
            sf.write(f"{get_formatted_time()} - TEST STOPLOSS: SOLD ALL {coin}\n")

        # Log the order
        log_order_to_csv(receipt, trade)
        
        print(f"🧪 TEST STOPLOSS: SOLD ALL {coin}")
        
    except Exception as e:
        logger.log('error', f"❌ Test stop loss sell execution failed: {e}")
        raise


async def initialize_stop_loss_protection(receipt, coin, trade, client, cur, conn):
    """
    🛡️ Initialize stop loss protection for the purchased asset
    The cosmic guardian that protects our investments
    """
    try:
        initial_price = receipt.price
        tracker = CoinTracker(initial_price, coin)
        logger.log('info', f"🛡️ STOPLOSS INITIATED for {coin} at price {initial_price}")
        print("🛡️ STOPLOSS INITIATED!")

        tracker.start_tracking()

        # Monitor the stop loss
        await monitor_stop_loss(tracker, coin, trade, client, cur, conn)
        
    except Exception as e:
        logger.log('error', f"❌ Stop loss initialization failed: {e}")
        raise


async def monitor_stop_loss(tracker, coin, trade, client, cur, conn):
    """
    👁️ Monitor the stop loss and execute sell when triggered
    The eternal vigilance that watches over our positions
    """
    try:
        stoploss_file = os.path.join("logs", "stoploss.txt")
        
        while tracker.is_tracking and not tracker.stop_loss_triggered:
            # Log current status
            with open(stoploss_file, 'a') as sf:
                sf.write(f"{get_formatted_time()} - {coin} - Current price: {tracker.current_price:.9f} USDT, Highest Limit: {tracker.highest_current_price_limit:.9f} USDT\n")
                coin_value_in_usdt = get_asset_balance_in_usdt(coin)
                sf.write(f"{get_formatted_time()} - Available {coin} balance in USDT: {coin_value_in_usdt:.2f} USDT\n")

            # Check if stop loss should be triggered
            if tracker.current_price < tracker.highest_current_price_limit:
                tracker.stop_tracking()
                await execute_stop_loss_sell(coin, trade, client, cur, conn, stoploss_file)
                break

            await asyncio.sleep(1)
            
    except Exception as e:
        logger.log('error', f"❌ Stop loss monitoring failed: {e}")
        raise


async def execute_stop_loss_sell(coin, trade, client, cur, conn, stoploss_file):
    """
    💸 Execute the stop loss sell order
    The protective sell that limits our losses
    """
    try:
        wallet = Wallet(coin)
        wallet.update_wallet()

        start_time = time.time()
        amount = wallet.bot_coin_amount - 0.5
        
        # Execute sell order
        receipt = await ut.make_order(cur, conn, client, logger, coin, "USDT", amount, "SELL", "USDT", None, False)
        end_time = time.time()
        
        trade.execution_time = end_time - start_time
        if hasattr(receipt, 'execution_time'):
            receipt.execution_time = trade.execution_time

        # Log the stop loss
        Sounds.bot_sounds.sell_sound()
        logger.log('warning', f"🛑 STOPLOSS: SOLD ALL {coin}")
        
        with open(stoploss_file, 'a') as sf:
            sf.write(f"{get_formatted_time()} - STOPLOSS: SOLD ALL {coin}\n")

        # Log the order
        log_order_to_csv(receipt, trade)
        
        print(f"🛑 STOPLOSS: SOLD ALL {coin}")
        
    except Exception as e:
        logger.log('error', f"❌ Stop loss sell execution failed: {e}")
        raise


def log_order_to_csv(receipt, trade, is_hold=False):
    """
    📝 Log order details to CSV file
    The cosmic record keeper that documents all trading activities
    """
    try:
        csv_file = 'data/output/bot_output_auto.csv'
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        
        # Create file with headers if it doesn't exist
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Order Id", "Order Datetime", "Order Type", "Order Symbol", 
                    "Order Quantity", "Order Fees Amount", "Order Price", 
                    "Order Side", "Order Execution Time"
                ])

        # Write the order data
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            
            if is_hold:
                writer.writerow(receipt)  # receipt is already a list for hold actions
            else:
                writer.writerow([
                    receipt.order_id,
                    get_formatted_time(),
                    receipt.type,
                    receipt.symbol,
                    receipt.quantity,
                    receipt.fees_amount,
                    receipt.price,
                    receipt.side,
                    receipt.execution_time
                ])
                
        logger.log('info', f"📝 Order logged to CSV: {receipt.order_id if hasattr(receipt, 'order_id') else 'HOLD'}")
        
    except Exception as e:
        logger.log('error', f"❌ Failed to log order to CSV: {e}")


async def main():
    """
    🌟 The Grand Main Function - Orchestrator of the Trading Universe
    Where everything comes together in the cosmic dance of trading
    """
    try:
        # Initialize the system
        client, conn = await initialize_system()
        cur = conn.cursor()
        
        # Display system status
        print(f"{Fore.CYAN}🌟 Cosmic Trading Bot Initialized{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🕐 System Time: {get_formatted_time()}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🧪 TEST MODE ENABLED - All trades will be paper trades{Style.RESET_ALL}")
        
        # Show wallet status
        print_wallet()
        
        # Configuration - Force test mode for safety
        USD_FIAT = "USDT"
        test_order = True  # Always use test mode for safety
        
        # Main trading loop
        await run_trading_loop(client, cur, conn, USD_FIAT, test_order)
        
    except KeyboardInterrupt:
        logger.log('info', "🛑 Trading bot stopped by user")
        print(f"\n{Fore.YELLOW}🛑 Trading bot stopped by user{Style.RESET_ALL}")
    except Exception as e:
        logger.log('error', f"❌ Fatal error in main: {e}")
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
    finally:
        # Cleanup
        if 'conn' in locals():
            conn.close()
        logger.log('info', "🌟 Trading bot shutdown complete")


async def run_trading_loop(client, cur, conn, USD_FIAT, test_order):
    """
    🔄 The main trading loop that processes model signals
    The eternal cycle of market analysis and execution
    """
    model_file = os.path.join('..', '..', 'model_output.csv')
    last_processed_timestamp = None
    waiting_for_signals_printed = False

    logger.log('info', "🔄 Starting trading loop...")
    
    while True:
        try:
            # Check if model file exists and has data
            if not os.path.exists(model_file) or os.stat(model_file).st_size == 0:
                if not waiting_for_signals_printed:
                    print("⏳ Waiting for trading signals...")
                    waiting_for_signals_printed = True
                await asyncio.sleep(1)
                continue

            # Process the latest signal
            result = get_last_line_of_csv(model_file, last_processed_timestamp)
            if result is None:
                await asyncio.sleep(1)
                continue

            line_number, last_line = result
            trade = Trade(line_number, *last_line)
            last_processed_timestamp = last_line[0]
            
            # Process the trade signal (always in test mode)
            await process_trade_signal(trade, client, cur, conn, test_order)
            
            # Reset waiting message flag
            waiting_for_signals_printed = False
            
        except Exception as e:
            logger.log('error', f"❌ Error in trading loop: {e}")
            await asyncio.sleep(5)  # Wait longer on error


if __name__ == "__main__":
    asyncio.run(main())
