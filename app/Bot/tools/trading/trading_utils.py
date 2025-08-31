"""
🎯 Trading Utilities - Where Strategy Meets Execution
The battlefield where buy/sell signals transform into real orders
"""

import time
import random
import datetime
from ..api.api_utils import (
    check_and_format_pair, precise_quantity_binance, 
    get_fiat_amount, InvalidTradingPairError, 
    UnsupportedClientTypeError, TradingPairCheckError
)
from ..database.database import insert_order
from ..database.order import Order, Receipt
from ..utils.log_module import CustomLogger
from ..api.wrapper import make_binance_request
from pybit.unified_trading import HTTP

# Initialize the cosmic logger
logger = CustomLogger("app.log")

def get_current_datetime():
    """⏰ Get the current moment in the cosmic timeline"""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_random_number(num):
    """
    🎲 Generate a random 7-digit number for order identification
    Each order gets its own unique cosmic signature
    """
    random_number = random.randint(1000000, 9999999)
    return str(random_number)

def binance_extra_error_descriptions(err):
    """
    🔍 Decode Binance's cryptic error messages into human wisdom
    Transforms exchange gibberish into actionable insights
    """
    error_explanations = {
        "PRICE_FILTER": "price is too high, too low, and/or not following the tick size rule for the symbol.",
        "PERCENT_PRICE": "price is X% too high or X% too low from the average weighted price over the last Y minutes.",
        "LOT_SIZE": "quantity is too high, too low, and/or not following the step size rule for the symbol.",
        "NOTIONAL": "price * quantity is too low to be a valid order for the symbol.",
        "ICEBERG_PARTS": "ICEBERG order would break into too many parts; icebergQty is too small.",
        "MARKET_LOT_SIZE": "MARKET order's quantity is too high, too low, and/or not following the step size rule for the symbol.",
        "MAX_POSITION": "The account's position has reached the maximum defined limit.",
        "MAX_NUM_ORDERS": "Account has too many open orders on the symbol.",
        "MAX_NUM_ALGO_ORDERS": "Account has too many open stop loss and/or take profit orders on the symbol.",
        "MAX_NUM_ICEBERG_ORDERS": "Account has too many open iceberg orders on the symbol.",
        "TRAILING_DELTA": "trailingDelta is not within the defined range of the filter for that order type.",
        "EXCHANGE_MAX_NUM_ORDERS": "Account has too many open orders on the exchange.",
        "EXCHANGE_MAX_NUM_ALGO_ORDERS": "Account has too many open stop loss and/or take profit orders on the exchange.",
        "EXCHANGE_MAX_NUM_ICEBERG_ORDERS": "Account has too many open iceberg orders on the exchange."
    }

    if "Filter failure" in err:
        for error_code, explanation in error_explanations.items():
            if error_code in err:
                logger.log('error', f"Explanation: {explanation}")

async def make_order(cur, conn, client, logger, coin, base_coin, quantity, side, fiat, receipt, test_order):
    """
    🚀 The Grand Order Execution - Where Dreams Become Reality
    Creates and executes orders on the chosen exchange with cosmic precision
    """
    
    # Determine the exchange type from client properties
    if hasattr(client, "WEBSITE_URL") and "binance" in client.WEBSITE_URL.lower():
        exchange = "binance"
    elif hasattr(client, "domain") and "bybit" in client.domain.lower():
        exchange = "bybit"
    else:
        exchange = "NOEXCHANGE"
    
    # Validate and format the trading pair
    try:
        symbol = check_and_format_pair(coin, base_coin, exchange, client)
    except (InvalidTradingPairError, UnsupportedClientTypeError, TradingPairCheckError) as e:
        receipt.error = str(e)
        return receipt
    
    # Convert to fiat amount if specified
    if fiat != "NOFIAT":
        quantity = get_fiat_amount(coin, fiat, quantity, client)

    # Execute on Binance
    if exchange.lower() == "binance":
        try:
            order = Order()
            order.order_datetime = get_current_datetime()
            order.exchange = "binance"
            order.symbol = symbol
            order.side = side
            
            if test_order:
                # 🧪 Paper Trading - Practice without consequences
                start_time = time.perf_counter()
                url = "https://api.binance.com/api/v3/order/test"
                params = {
                    "symbol": symbol,
                    "side": side,
                    "type": "MARKET",
                    "quantity": precise_quantity_binance(symbol, quantity, client),
                    "timestamp": int(time.time() * 1000) + 5000,
                }
                order_res = make_binance_request(
                    "POST", url, api_key=client.API_KEY, secret_key=client.API_SECRET, params=params
                )
                execution_time = time.perf_counter() - start_time

                # Create test order record
                order.order_id = get_random_number(20)
                order.quantity = quantity
                url = f"https://api.binance.com/api/v3/ticker/price"
                params = {"symbol": symbol}
                response = make_binance_request("GET", url, api_key=client.API_KEY, secret_key=client.API_SECRET, params=params)
                order.price = float(response.json()["price"])
                order.fees_amount = -1
                order.fees_coin = "NA"
                order.is_test = "true"
                
                logger.log('info', "Binance market paper trade test order successfully placed:")
                logger.log('info', order_res)
                insert_order(cur, order)
                conn.commit()

                # Create receipt for test order
                receipt = Receipt()
                receipt.order_id = order.order_id
                receipt.time = execution_time
                receipt.side = side
                receipt.exchange = order.exchange
                receipt.order_datetime = order.order_datetime
                receipt.quantity = order.quantity
                receipt.side = order.side
                receipt.symbol = symbol
                receipt.type = "@PaperTrade"
                receipt.fees_amount = order.fees_amount
                receipt.fees_coin = order.fees_coin
                receipt.price = order.price
                return receipt
                  
            else:
                # 💰 Real Trading - Where fortunes are made and lost
                start_time = time.perf_counter()
                url = "https://api.binance.com/api/v3/order"
                params = {
                    "symbol": symbol,
                    "side": side,
                    "type": "MARKET",
                    "quantity": precise_quantity_binance(symbol, quantity, client),
                    "timestamp": int(time.time() * 1000),
                }
                order_res = make_binance_request(
                    "POST", url, api_key=client.API_KEY, secret_key=client.API_SECRET, params=params
                )
                execution_time = time.perf_counter() - start_time

                # Create real order record
                order.order_id = str(order_res.json()["orderId"])
                order.quantity = float(order_res.json()["executedQty"])
                order.price = float(order_res.json()["fills"][0]["price"])
                order.fees_amount = float(order_res.json()["fills"][0]["commission"])
                order.fees_coin = order_res.json()["fills"][0]["commissionAsset"]
                order.is_test = "false"
                
                logger.log('info', "Binance market order successfully placed:")
                logger.log('info', order_res)
                insert_order(cur, order)
                conn.commit()

                # Create receipt for real order
                receipt = Receipt()
                receipt.order_id = order.order_id
                receipt.time = execution_time
                receipt.side = side
                receipt.exchange = order.exchange
                receipt.order_datetime = order.order_datetime
                receipt.quantity = order.quantity
                receipt.side = order.side
                receipt.symbol = order.symbol
                receipt.type = "@MarketOrder"
                receipt.fees_amount = order.fees_amount
                receipt.fees_coin = order.fees_coin
                receipt.price = order.price
                return receipt

        except Exception as e:
            logger.log('error', "Binance error: " + str(e))
            binance_extra_error_descriptions(str(e))
            receipt = Receipt()
            receipt.type = None
            receipt.error = str(e)
            return receipt
        
    elif exchange.lower() == "bybit":
        # 🐉 Bybit Integration - The Dragon Exchange
        try:
            if side.lower() == "buy":
                ticker = session.get_tickers(category="spot", symbol=symbol)
                last_price = float(ticker["result"]["list"][0]["lastPrice"])
                qty = str(round(quantity * last_price, 9))
            else:
                qty = str(precise_quantity_bybit(symbol, quantity))
                
            order_res = session.place_order(category="spot", symbol=symbol, side=side, orderType="Market", qty=qty)
            logger.log('info', "Bybit market order successfully placed:")
            order_id = order_res["result"]["orderId"]
            executed_order = session.get_order_history(category="spot", orderId=order_id)
            logger.log('info', executed_order)
            
            # Create order record
            order = Order()
            order.order_id = order_id
            order.order_datetime = get_current_datetime()
            order.exchange = "bybit"
            order.symbol = executed_order["result"]["list"][0]["symbol"]
            order.side = executed_order["result"]["list"][0]["side"]
            
            if side.lower() == "buy":
                order.quantity = quantity
            else:
                order.quantity = float(executed_order["result"]["list"][0]["qty"])
                
            order.price = float(executed_order["result"]["list"][0]["avgPrice"])
            order.fees_amount = -1
            order.fees_coin = "NA"
            order.is_test = "false"
            insert_order(cur, order)
            conn.commit()
            return True
            
        except Exception as e:
            logger.log('error', "Bybit error: " + str(e))
            return "bybit return value - finish checking code. - return the str(e) - for errors"
    else:
        logger.log('error', exchange + " exchange is not configured to this function. Only binance and bybit")

def precise_quantity_bybit(coin, quantity):
    """
    ⚖️ Calculate precise quantity for Bybit's trading rules
    Ensures orders dance to Bybit's rhythm
    """
    instrument_info = session.get_instruments_info(category="spot", symbol=coin)
    base_precision = float(instrument_info["result"]["list"][0]["lotSizeFilter"]["basePrecision"])
    print("base_precision: " + str(base_precision))
    truncate_num = math.log10(1 / base_precision)
    quantity = math.floor((quantity) * 10 ** truncate_num) / 10 ** truncate_num
    print("valid_quantity: " + str(quantity))
    return quantity
