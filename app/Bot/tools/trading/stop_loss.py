"""
🛑 Stop Loss System - The Guardian of Digital Fortunes
Where protection mechanisms dance with market volatility
"""

import time
import threading
import platform
from urllib.parse import urlencode
from binance.client import Client
import hmac
import hashlib

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
from ..api.wrapper import make_binance_request
from ...exceptions.bot_exceptions import StopLossException, APIException, NetworkException
from ..utils.log_module import CustomLogger

# Initialize the cosmic logger
logger = CustomLogger("app.log")

# Initialize the Binance client globally
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

def get_asset_balance_in_usdt(asset):
    """
    💰 Fetch the available balance of the specified asset in USDT using the API wrapper
    The digital vault inspector that counts our cosmic wealth
    """
    try:
        # Fetch account details
        url_account = "https://api.binance.com/api/v3/account"
        headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
        params_account = {"timestamp": int(time.time() * 1000)}

        # Sign the request with cosmic precision
        query_string = urlencode(params_account)
        signature = hmac.new(BINANCE_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        params_account["signature"] = signature

        # Make the request using the wrapper
        response_account = make_binance_request("GET", url_account, headers=headers, params=params_account)
        
        # Check for valid response
        if not response_account or not hasattr(response_account, "json"):
            logger.log('error', "Invalid response for account details")
            raise APIException("Invalid response for account details", api_name="Binance")

        account_data = response_account.json()
        balance_info = next(
            (item for item in account_data.get("balances", []) if item["asset"] == asset), 
            None
        )

        if balance_info and "free" in balance_info:
            amount = float(balance_info["free"])
            if amount > 0:
                # Fetch the ticker price
                url_ticker = "https://api.binance.com/api/v3/ticker/price"
                params_ticker = {"symbol": f"{asset}USDT"}
                response_ticker = make_binance_request("GET", url_ticker, headers=headers, params=params_ticker)
                
                # Check for valid ticker response
                if not response_ticker or not hasattr(response_ticker, "json"):
                    logger.log('error', "Invalid response for ticker price")
                    raise APIException("Invalid response for ticker price", api_name="Binance")

                ticker_data = response_ticker.json()
                current_price = float(ticker_data.get("price", 0.0))
                total_value_in_usdt = amount * current_price
                return total_value_in_usdt
            else:
                return 0.0
        else:
            return 0.0
            
    except APIException:
        raise
    except Exception as e:
        logger.log('error', f"Error fetching balance for {asset}: {e}")
        raise NetworkException(f"Error fetching balance for {asset}", details={'asset': asset}) from e


class CoinTracker:
    """
    🎯 The Cosmic Price Tracker - Guardian of Stop Loss Mechanisms
    Monitors coin prices and triggers protective actions when needed
    """
    
    def __init__(self, initial_price, coin):
        self.current_price = initial_price
        self.fake_current_price = initial_price  # Separate field for fake coin price
        self.is_tracking = False
        self.thread = None
        self.coin = coin  # Store the coin symbol
        self.highest_current_price_limit = initial_price * 0.99994  # Track the highest 90% limit for the real coin
        self.fake_highest_current_price_limit = initial_price * 0.99994  # Track for fake coin
        self.fake_price_increase_count = 0  # Counter for fake coin increases
        self.stop_loss_triggered = False
        self.lock = threading.Lock()  # Thread safety for Linux compatibility

    def get_coin_value(self):
        """
        🌟 Fetch the current value of the specified coin in USDT
        The cosmic price oracle that reveals market truths
        """
        try:
            url = "https://api.binance.com/api/v3/ticker/price"
            params = {"symbol": f"{self.coin}USDT"}
            headers = {"X-MBX-APIKEY": BINANCE_API_KEY}

            # Make the request using the wrapper
            response = wrapper.make_binance_request("GET", url, headers=headers, params=params)

            # Check if the response is valid
            if not response or not hasattr(response, 'json'):
                logger.log('error', "Invalid response for ticker price")
                raise APIException("Invalid response for ticker price", api_name="Binance")

            # Extract price from the response
            ticker = response.json()
            self.current_price = float(ticker.get('price', 0.0))

        except APIException:
            raise
        except Exception as e:
            logger.log('error', f"Error fetching data: {e}")
            raise NetworkException(f"Error fetching coin value for {self.coin}", details={'coin': self.coin}) from e

    def update_value(self):
        """
        🔄 Update the current price and check stop loss conditions
        The heartbeat of the stop loss system
        """
        try:
            self.get_coin_value()
            
            with self.lock:
                # Update the highest limit if current price is higher
                if self.current_price > self.highest_current_price_limit:
                    self.highest_current_price_limit = self.current_price * 0.99994
                
                # Check if stop loss should be triggered
                if self.current_price < self.highest_current_price_limit:
                    self.stop_loss_triggered = True
                    logger.log('warning', f"Stop loss triggered for {self.coin} at price {self.current_price}")
                    
        except Exception as e:
            logger.log('error', f"Error updating value for {self.coin}: {e}")
            raise StopLossException(f"Failed to update value for {self.coin}", coin=self.coin, price=self.current_price) from e

    def start_tracking(self):
        """
        🚀 Start the cosmic price tracking thread
        Launches the guardian into the digital marketplace
        """
        if self.is_tracking:
            logger.log('warning', f"Already tracking {self.coin}")
            return
        
        self.is_tracking = True
        self.stop_loss_triggered = False
        
        # Create tracking thread with proper Linux compatibility
        self.thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.thread.start()
        
        logger.log('info', f"Started tracking {self.coin} with initial price: {self.current_price}")

    def stop_tracking(self):
        """
        🛑 Stop the cosmic price tracking thread
        Brings the guardian back from the digital battlefield
        """
        with self.lock:
            self.is_tracking = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)  # Wait up to 5 seconds for thread to finish
        
        logger.log('info', f"Stopped tracking {self.coin}")

    def _tracking_loop(self):
        """
        🔄 The main tracking loop - the guardian's eternal vigilance
        """
        logger.log('info', f"Tracking loop started for {self.coin}")
        
        while self.is_tracking:
            try:
                self.update_value()
                
                # Check if stop loss was triggered
                if self.stop_loss_triggered:
                    logger.log('warning', f"Stop loss condition met for {self.coin}")
                    break
                
                # Sleep with proper Linux compatibility
                time.sleep(1)
                
            except Exception as e:
                logger.log('error', f"Error in tracking loop for {self.coin}: {e}")
                # Continue tracking even if there's an error
                time.sleep(5)  # Wait longer on error
        
        logger.log('info', f"Tracking loop ended for {self.coin}")

    def get_status(self):
        """
        📊 Get the current status of the coin tracker
        """
        with self.lock:
            return {
                'coin': self.coin,
                'current_price': self.current_price,
                'highest_limit': self.highest_current_price_limit,
                'is_tracking': self.is_tracking,
                'stop_loss_triggered': self.stop_loss_triggered,
                'price_drop_percentage': ((self.highest_current_price_limit - self.current_price) / self.highest_current_price_limit) * 100 if self.highest_current_price_limit > 0 else 0
            }

    def __repr__(self):
        """
        🎭 String representation of the coin tracker
        """
        status = self.get_status()
        return (f"CoinTracker(coin='{self.coin}', "
                f"current_price={self.current_price:.8f}, "
                f"highest_limit={self.highest_current_price_limit:.8f}, "
                f"tracking={self.is_tracking}, "
                f"drop_percent={status['price_drop_percentage']:.2f}%)")


class StopLossManager:
    """
    🛡️ The Grand Stop Loss Manager - Orchestrator of Protection
    Manages multiple coin trackers and coordinates stop loss actions
    """
    
    def __init__(self):
        self.trackers = {}
        self.lock = threading.Lock()
        self.logger = CustomLogger("stoploss.log")
    
    def add_tracker(self, coin: str, initial_price: float) -> CoinTracker:
        """
        ➕ Add a new coin tracker to the protection system
        """
        with self.lock:
            if coin in self.trackers:
                self.logger.log('warning', f"Tracker for {coin} already exists")
                return self.trackers[coin]
            
            tracker = CoinTracker(initial_price, coin)
            self.trackers[coin] = tracker
            self.logger.log('info', f"Added tracker for {coin} with initial price {initial_price}")
            return tracker
    
    def remove_tracker(self, coin: str):
        """
        ➖ Remove a coin tracker from the protection system
        """
        with self.lock:
            if coin in self.trackers:
                tracker = self.trackers[coin]
                tracker.stop_tracking()
                del self.trackers[coin]
                self.logger.log('info', f"Removed tracker for {coin}")
    
    def get_tracker(self, coin: str) -> CoinTracker:
        """
        🔍 Get a specific coin tracker
        """
        with self.lock:
            return self.trackers.get(coin)
    
    def get_all_status(self):
        """
        📊 Get status of all active trackers
        """
        with self.lock:
            return {coin: tracker.get_status() for coin, tracker in self.trackers.items()}
    
    def stop_all_trackers(self):
        """
        🛑 Stop all active trackers
        """
        with self.lock:
            for tracker in self.trackers.values():
                tracker.stop_tracking()
            self.trackers.clear()
            self.logger.log('info', "Stopped all trackers")

# Global stop loss manager instance
stop_loss_manager = StopLossManager()
