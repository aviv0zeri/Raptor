"""
Ported Trading Bot Main from app/Bot/main.py to app/modules/bot/main.py
Updated imports to new app.modules.* structure
"""

import csv
import time
import os
import sys
import asyncio
from pathlib import Path
from colorama import Fore, Style, init
from binance.client import Client

# Ensure project root on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv()

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

from app.modules.utils.log_module import CustomLogger
from app.modules.database.order import Order, Receipt
from app.modules.database.database import connect, insert_order
from app.modules.tools import utils as ut
from app.modules.utils.sync_time_utils import sync_system_time, get_formatted_time
from app.modules.utils.cache_manager import cache_manager
from app.modules.config.config_manager import config_manager
from app.modules.utils.wallet_utils import print_wallet, get_wallet_summary
from app.modules.trading.stop_loss import CoinTracker, get_asset_balance_in_usdt, stop_loss_manager
from app.modules.exceptions.bot_exceptions import (
    BotException, TradingException, DatabaseException,
    ConfigurationException, raise_insufficient_balance
)

try:
    from app.Sounds import bot_sounds
except Exception:
    bot_sounds = None

init(autoreset=True)
logger = CustomLogger("logs/main.log")


class Wallet:
    def __init__(self, coin):
        self.bot_coin = coin
        self.bot_coin_amount = 0.0
        self.usdt_amount = 0.0
        self.update_wallet()

    def update_wallet(self):
        try:
            cache_key = f"wallet_balance_{self.bot_coin}"
            cached_balance = cache_manager.get('wallet', cache_key)
            if cached_balance:
                self.bot_coin_amount = cached_balance.get('bot_coin', 0.0)
                self.usdt_amount = cached_balance.get('usdt', 0.0)
                return

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

            cache_manager.set('wallet', cache_key, {
                'bot_coin': self.bot_coin_amount,
                'usdt': self.usdt_amount
            }, ttl=60)
        except Exception as e:
            logger.log('error', f"Error updating wallet: {e}")
            self.bot_coin_amount = 0.0
            self.usdt_amount = 0.0

    def convert_to_usdt(self):
        try:
            cache_key = f"price_{self.bot_coin}USDT"
            cached_price = cache_manager.get('prices', cache_key)
            if cached_price:
                price = cached_price
            else:
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
                cache_manager.set('prices', cache_key, price, ttl=30)

            self.bot_coin_amount = self.bot_coin_amount * price
            logger.log('info', f"Updated bot_coin_amount to equivalent USDT value: {self.bot_coin_amount}")
            return self.bot_coin_amount
        except Exception as e:
            logger.log('error', f"Error converting to USDT: {e}")
            return 0.0

    def __repr__(self):
        return (
            f"Wallet(bot_coin='{self.bot_coin}', "
            f"bot_coin_amount={self.bot_coin_amount:.2f}, "
            f"usdt_amount={self.usdt_amount:.2f}, "
            f"total_usdt_value={self.convert_to_usdt():.2f})"
        )


class Trade:
    def __init__(self, line_number, timestamp, action, quantity, pair, execution_time=None):
        self.line_number = line_number
        self.timestamp = timestamp
        self.action = action.strip()
        self.quantity = float(quantity)
        self.pair = pair.strip()
        self.execution_time = execution_time

    def __repr__(self):
        exec_time_str = f"{self.execution_time:.2f}s" if self.execution_time is not None else "N/A"
        return (f"order:{self.line_number}, timestamp:{self.timestamp}, "
                f"action:{self.action}, quantity:{self.quantity}, pair:{self.pair}, "
                f"execution_time:{exec_time_str}")

    def repr_hold_csv(self):
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
    logger.log('info', "🌟 Starting the Cosmic Trading Bot...")
    logger.log('info', "🕐 Synchronizing system time...")
    if sync_system_time():
        logger.log('info', "✅ Time synchronization successful")
    else:
        logger.log('warning', "⚠️ Time synchronization failed, continuing anyway")
    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    logger.log('info', "🔗 Binance client initialized")
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
    try:
        coin, base_coin = trade.pair.split('/')
        wallet = Wallet(coin)
        wallet.update_wallet()
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
    try:
        wallet.update_wallet()
        start_time = time.time()
        if test_order:
            amount = 10.0
            logger.log('info', f"🧪 TEST MODE: Using fixed amount of {amount} USDT for buy order")
        else:
            amount = wallet.usdt_amount - 0.5
            if amount <= 0:
                raise raise_insufficient_balance(coin, amount, wallet.usdt_amount)
        receipt = await ut.make_order(cur, conn, client, logger, coin, base_coin, amount, "BUY", "USDT", None, test_order)
        end_time = time.time()
        trade.execution_time = end_time - start_time
        if hasattr(receipt, 'execution_time'):
            receipt.execution_time = trade.execution_time
        log_order_to_csv(receipt, trade)
        if not test_order and bot_sounds:
            bot_sounds.buy_sound()
        mode_text = "🧪 TEST" if test_order else "💰 REAL"
        logger.log('info', f"✅ {mode_text} {trade} - BUY order executed successfully")
        print(f"{Fore.GREEN}{mode_text} {trade}{Style.RESET_ALL} - trade was placed")
        if test_order:
            await initialize_test_stop_loss_protection(receipt, coin, trade, client, cur, conn)
        else:
            await initialize_stop_loss_protection(receipt, coin, trade, client, cur, conn)
    except Exception as e:
        logger.log('error', f"❌ Buy order execution failed: {e}")
        raise


async def execute_hold_action(trade, cur, conn):
    try:
        hold_data = trade.repr_hold_csv()
        log_order_to_csv(hold_data, trade, is_hold=True)
        logger.log('info', f"⏸️ {trade} - HOLD action executed")
        print(f"{Fore.YELLOW}{trade.__repr__()}{Style.RESET_ALL} - no trade was placed")
    except Exception as e:
        logger.log('error', f"❌ Hold action execution failed: {e}")
        raise


async def initialize_test_stop_loss_protection(receipt, coin, trade, client, cur, conn):
    try:
        initial_price = receipt.price
        logger.log('info', f"🧪 TEST STOPLOSS INITIATED for {coin} at price {initial_price}")
        print("🧪 TEST STOPLOSS INITIATED!")
        await simulate_test_stop_loss(coin, trade, client, cur, conn, initial_price)
    except Exception as e:
        logger.log('error', f"❌ Test stop loss initialization failed: {e}")
        raise


async def simulate_test_stop_loss(coin, trade, client, cur, conn, initial_price):
    try:
        stoploss_file = os.path.join("logs", "stoploss.txt")
        for i in range(5):
            with open(stoploss_file, 'a') as sf:
                sf.write(f"{get_formatted_time()} - TEST {coin} - Simulated price: {initial_price:.9f} USDT, Test Limit: {initial_price * 0.99994:.9f} USDT\n")
                sf.write(f"{get_formatted_time()} - TEST Available {coin} balance in USDT: 10.00 USDT\n")
            simulated_price = initial_price * (1 + (i - 2) * 0.001)
            if simulated_price < initial_price * 0.99994:
                await execute_test_stop_loss_sell(coin, trade, client, cur, conn, stoploss_file)
                break
            await asyncio.sleep(1)
        logger.log('info', f"🧪 Test stop loss simulation completed for {coin}")
    except Exception as e:
        logger.log('error', f"❌ Test stop loss simulation failed: {e}")
        raise


async def execute_test_stop_loss_sell(coin, trade, client, cur, conn, stoploss_file):
    try:
        start_time = time.time()
        amount = 10.0
        receipt = await ut.make_order(cur, conn, client, logger, coin, "USDT", amount, "SELL", "USDT", None, True)
        end_time = time.time()
        trade.execution_time = end_time - start_time
        if hasattr(receipt, 'execution_time'):
            receipt.execution_time = trade.execution_time
        if bot_sounds:
            bot_sounds.sell_sound()
        logger.log('warning', f"🧪 TEST STOPLOSS: SOLD ALL {coin}")
        with open(stoploss_file, 'a') as sf:
            sf.write(f"{get_formatted_time()} - TEST STOPLOSS: SOLD ALL {coin}\n")
        log_order_to_csv(receipt, trade)
        print(f"🧪 TEST STOPLOSS: SOLD ALL {coin}")
    except Exception as e:
        logger.log('error', f"❌ Test stop loss sell execution failed: {e}")
        raise


async def initialize_stop_loss_protection(receipt, coin, trade, client, cur, conn):
    try:
        initial_price = receipt.price
        tracker = CoinTracker(initial_price, coin)
        logger.log('info', f"🛡️ STOPLOSS INITIATED for {coin} at price {initial_price}")
        print("🛡️ STOPLOSS INITIATED!")
        tracker.start_tracking()
        await monitor_stop_loss(tracker, coin, trade, client, cur, conn)
    except Exception as e:
        logger.log('error', f"❌ Stop loss initialization failed: {e}")
        raise


async def monitor_stop_loss(tracker, coin, trade, client, cur, conn):
    try:
        stoploss_file = os.path.join("logs", "stoploss.txt")
        while tracker.is_tracking and not tracker.stop_loss_triggered:
            with open(stoploss_file, 'a') as sf:
                sf.write(f"{get_formatted_time()} - {coin} - Current price: {tracker.current_price:.9f} USDT, Highest Limit: {tracker.highest_current_price_limit:.9f} USDT\n")
                coin_value_in_usdt = get_asset_balance_in_usdt(coin)
                sf.write(f"{get_formatted_time()} - Available {coin} balance in USDT: {coin_value_in_usdt:.2f} USDT\n")
            if tracker.current_price < tracker.highest_current_price_limit:
                tracker.stop_tracking()
                await execute_stop_loss_sell(coin, trade, client, cur, conn, stoploss_file)
                break
            await asyncio.sleep(1)
    except Exception as e:
        logger.log('error', f"❌ Stop loss monitoring failed: {e}")
        raise


async def execute_stop_loss_sell(coin, trade, client, cur, conn, stoploss_file):
    try:
        wallet = Wallet(coin)
        wallet.update_wallet()
        start_time = time.time()
        amount = wallet.bot_coin_amount - 0.5
        receipt = await ut.make_order(cur, conn, client, logger, coin, "USDT", amount, "SELL", "USDT", None, False)
        end_time = time.time()
        trade.execution_time = end_time - start_time
        if hasattr(receipt, 'execution_time'):
            receipt.execution_time = trade.execution_time
        if bot_sounds:
            bot_sounds.sell_sound()
        logger.log('warning', f"🛑 STOPLOSS: SOLD ALL {coin}")
        with open(stoploss_file, 'a') as sf:
            sf.write(f"{get_formatted_time()} - STOPLOSS: SOLD ALL {coin}\n")
        log_order_to_csv(receipt, trade)
        print(f"🛑 STOPLOSS: SOLD ALL {coin}")
    except Exception as e:
        logger.log('error', f"❌ Stop loss sell execution failed: {e}")
        raise


def log_order_to_csv(receipt, trade, is_hold=False):
    try:
        csv_file = 'data/output/bot_output_auto.csv'
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Order Id", "Order Datetime", "Order Type", "Order Symbol",
                    "Order Quantity", "Order Fees Amount", "Order Price",
                    "Order Side", "Order Execution Time"
                ])
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if is_hold:
                writer.writerow(receipt)
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
    try:
        client, conn = await initialize_system()
        cur = conn.cursor()
        print(f"{Fore.CYAN}🌟 Cosmic Trading Bot Initialized{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🕐 System Time: {get_formatted_time()}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🧪 TEST MODE ENABLED - All trades will be paper trades{Style.RESET_ALL}")
        print_wallet()
        USD_FIAT = "USDT"
        test_order = True
        await run_trading_loop(client, cur, conn, USD_FIAT, test_order)
    except KeyboardInterrupt:
        logger.log('info', "🛑 Trading bot stopped by user")
        print(f"\n{Fore.YELLOW}🛑 Trading bot stopped by user{Style.RESET_ALL}")
    except Exception as e:
        logger.log('error', f"❌ Fatal error in main: {e}")
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
    finally:
        if 'conn' in locals():
            conn.close()
        logger.log('info', "🌟 Trading bot shutdown complete")


async def run_trading_loop(client, cur, conn, USD_FIAT, test_order):
    model_file = os.path.join('..', '..', 'model_output.csv')
    last_processed_timestamp = None
    waiting_for_signals_printed = False
    logger.log('info', "🔄 Starting trading loop...")
    while True:
        try:
            if not os.path.exists(model_file) or os.stat(model_file).st_size == 0:
                if not waiting_for_signals_printed:
                    print("⏳ Waiting for trading signals...")
                    waiting_for_signals_printed = True
                await asyncio.sleep(1)
                continue
            result = get_last_line_of_csv(model_file, last_processed_timestamp)
            if result is None:
                await asyncio.sleep(1)
                continue
            line_number, last_line = result
            trade = Trade(line_number, *last_line)
            last_processed_timestamp = last_line[0]
            await process_trade_signal(trade, client, cur, conn, test_order)
            waiting_for_signals_printed = False
        except Exception as e:
            logger.log('error', f"❌ Error in trading loop: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())



