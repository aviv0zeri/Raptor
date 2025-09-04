#!/usr/bin/env python3
"""
🦖 RAPTOR TRADING BOT - TEST MAIN
=================================

This implements the original CSV-based trading strategy from the commented code.
It reads model_output.csv and executes trades based on BUY/HOLD signals.

Strategy:
1. Monitor model_output.csv for new signals
2. Process BUY/HOLD signals
3. Execute trades with stop-loss management
4. Log all actions to bot_output_auto.csv
"""

import csv
import time
import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class FakeWallet:
    """Fake wallet for testing - simulates real wallet behavior"""
    
    def __init__(self, coin):
        self.bot_coin = coin
        self.bot_coin_amount = 0.0  # Amount of bot coin held
        self.usdt_amount = 1000.0   # Start with 1000 USDT
        self.chz_price = 0.05       # Simulated CHZ price
        
    def update_wallet(self):
        """Simulate wallet update"""
        # Simulate price fluctuations
        price_change = (time.time() % 60) / 60  # Price changes over time
        self.chz_price = 0.05 + (price_change - 0.5) * 0.01  # ±0.5 cent variation
        print(f"💰 Wallet updated - CHZ Price: ${self.chz_price:.4f}")
        
    def convert_to_usdt(self):
        """Convert bot coin to USDT value"""
        return self.bot_coin_amount * self.chz_price

class Trade:
    """Trade object representing a trading signal"""
    
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
        """Format for CSV output when HOLD"""
        return [
            -1,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "@MARKETORDER",
            self.pair,
            self.quantity,
            -1,
            -1,
            self.action,
            0
        ]

class FakeStopLossTracker:
    """Fake stop loss tracker for testing"""
    
    def __init__(self, initial_price, coin):
        self.initial_price = initial_price
        self.current_price = initial_price
        self.coin = coin
        self.current_price_limit = initial_price * 0.98  # 2% stop loss
        self.is_tracking = False
        
    def start_tracking(self):
        """Start stop loss monitoring"""
        self.is_tracking = True
        print(f"🛑 Stop loss initiated at ${self.initial_price:.4f}, limit: ${self.current_price_limit:.4f}")
        
    def stop_tracking(self):
        """Stop monitoring"""
        self.is_tracking = False
        print("🛑 Stop loss tracking stopped")
        
    def update_price(self):
        """Simulate price update"""
        # Simulate price movement
        price_change = (time.time() % 30) / 30  # Price changes every 30 seconds
        self.current_price = self.initial_price + (price_change - 0.5) * 0.02  # ±1% variation
        return self.current_price

def get_last_line_of_csv(file_path, last_processed_timestamp):
    """Get the last line from CSV if it's new"""
    try:
        if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
            return None
            
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
        print(f"Error reading CSV: {e}")
        return None

async def simulate_order_execution(coin, base_coin, amount, side, test_order=True):
    """Simulate order execution"""
    if test_order:
        # Simulate order execution time
        await asyncio.sleep(0.1)
        
        # Create fake receipt
        class FakeReceipt:
            def __init__(self):
                self.order_id = f"TEST_{int(time.time())}"
                self.type = "MARKET"
                self.symbol = f"{coin}{base_coin}"
                self.quantity = amount
                self.fees_amount = amount * 0.001  # 0.1% fee
                self.price = 0.05 if coin == "CHZ" else 45000  # Simulated price
                self.side = side
                self.execution_time = 0.1
                
        return FakeReceipt()
    else:
        # Real order execution would go here
        pass

async def main():
    """Main trading bot function"""
    print('🦖 Starting Raptor Test Bot...\n')
    
    # Configuration
    # Write all test CSVs under logs/, and use test-specific filenames
    csv_file = os.path.join('..', '..', '..', 'logs', 'bot_output_auto_test.csv')
    model_file = os.path.join('..', '..', '..', 'logs', 'model_output_test.csv')
    stoploss_file = os.path.join("logs", "stoploss.txt")
    
    # Initialize files
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Order Id", "Order Datetime", "Order Type", "Order Symbol", 
                "Order Quantity", "Order Fees Amount", "Order Price", 
                "Order Side", "Order Execution Time"
            ])
        print(f"✅ Created {csv_file}")
    
    # Initialize variables
    order_number = 0
    USD_FIAT = "USDT"
    test_order = True  # Use test orders for safety
    receipt = None
    last_processed_timestamp = None
    waiting_for_signals_printed = False
    
    print("🔄 Starting CSV monitoring loop...\n")
    
    while True:
        # Check if model file exists and has data
        if not os.path.exists(model_file) or os.stat(model_file).st_size == 0:
            if not waiting_for_signals_printed:
                print("⏳ Waiting for model signals...\n")
                waiting_for_signals_printed = True
            await asyncio.sleep(1)
            continue

        # Process the last line if the file is not empty
        result = get_last_line_of_csv(model_file, last_processed_timestamp)
        if result is None:
            await asyncio.sleep(1)
            continue
            
        line_number, last_line = result
        last_processed_timestamp = last_line[0].strip()
        
        # Create trade object
        trade = Trade(line_number, *last_line)
        coin, base_coin = trade.pair.split('/')
        
        # Initialize wallet
        wallet = FakeWallet(coin)
        wallet.update_wallet()
        
        print(f"📊 Processing signal: {trade}")
        
        # Check if we should force HOLD (if we have more bot coin than USDT)
        if wallet.bot_coin_amount > wallet.usdt_amount:
            trade.action = "HOLD"
            print(f"⚠️  Forcing HOLD - bot coin amount ({wallet.bot_coin_amount}) > USDT amount ({wallet.usdt_amount})")

        if trade.action == "BUY":
            print(f"🟢 Executing BUY order...")
            wallet.update_wallet()
            
            # Check if we have enough USDT
            if wallet.usdt_amount < 10:
                print(f"❌ Insufficient USDT balance: ${wallet.usdt_amount}")
                continue
                
            start_time = time.time()
            amount = wallet.usdt_amount - 0.5  # Leave 0.5 USDT for fees
            
            # Execute order
            receipt = await simulate_order_execution(coin, base_coin, amount, "BUY", test_order)
            end_time = time.time()
            trade.execution_time = end_time - start_time
            receipt.execution_time = trade.execution_time

            # Log to CSV
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    receipt.order_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    receipt.type,
                    receipt.symbol,
                    receipt.quantity,
                    receipt.fees_amount,
                    receipt.price,
                    receipt.side,
                    receipt.execution_time
                ])
            order_number += 1
            
            print(f"✅ BUY order executed: {receipt.symbol} at ${receipt.price:.4f}")
            print(f"🔊 Playing buy sound...")

            # Initialize stop loss tracking
            initial_price = receipt.price
            tracker = FakeStopLossTracker(initial_price, coin)
            print("🛑 STOPLOSS INITIATED!")

            tracker.start_tracking()

            # Stop loss monitoring loop
            while tracker.is_tracking:
                current_price = tracker.update_price()
                
                # Log to stop loss file
                with open(stoploss_file, 'a') as sf:
                    sf.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {coin} - Current price: {current_price:.9f} USDT, Highest Limit: {tracker.current_price_limit:.9f} USDT\n")
                    coin_value_in_usdt = wallet.convert_to_usdt()
                    sf.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Available {coin} balance in USDT: {coin_value_in_usdt:.2f} USDT\n")

                # Check if stop loss triggered
                if current_price < tracker.current_price_limit:
                    tracker.stop_tracking()
                    print(f"🛑 STOPLOSS TRIGGERED! Price: ${current_price:.4f} < Limit: ${tracker.current_price_limit:.4f}")
                    
                    # Execute SELL order
                    wallet.update_wallet()
                    start_time = time.time()
                    amount = wallet.bot_coin_amount - 0.5  # Leave some for fees
                    
                    receipt = await simulate_order_execution(coin, base_coin, amount, "SELL", test_order)
                    end_time = time.time()      
                    trade.execution_time = end_time - start_time
                    receipt.execution_time = trade.execution_time                            
                    
                    print(f"🔊 Playing sell sound...")
                    print(f"🛑 STOPLOSS: SOLD ALL {coin}")
                    
                    # Log stop loss
                    with open(stoploss_file, 'a') as sf:
                        sf.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - STOPLOSS: SOLD ALL {coin}\n")

                    # Log to CSV
                    with open(csv_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            receipt.order_id,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            receipt.type,
                            receipt.symbol,
                            receipt.quantity,
                            receipt.fees_amount,
                            receipt.price,
                            receipt.side,
                            receipt.execution_time
                        ])
                    order_number += 1
                    break

                await asyncio.sleep(1)

        elif trade.action == "HOLD":
            print(f"🟡 Processing HOLD signal...")
            hold_data = trade.repr_hold_csv()
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(hold_data)
            print(f"🟡 {trade.__repr__()} - no trade was placed.\n")
            order_number = line_number - 1
            
        elif trade.action == "SELL":
            print(f"🔴 Processing SELL signal...")
            # Similar to BUY but reverse logic
            wallet.update_wallet()
            start_time = time.time()
            amount = wallet.bot_coin_amount - 0.5
            
            receipt = await simulate_order_execution(coin, base_coin, amount, "SELL", test_order)
            end_time = time.time()
            trade.execution_time = end_time - start_time
            receipt.execution_time = trade.execution_time

            # Log to CSV
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    receipt.order_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    receipt.type,
                    receipt.symbol,
                    receipt.quantity,
                    receipt.fees_amount,
                    receipt.price,
                    receipt.side,
                    receipt.execution_time
                ])
            order_number += 1
            
            print(f"✅ SELL order executed: {receipt.symbol} at ${receipt.price:.4f}")
            print(f"🔊 Playing sell sound...")

if __name__ == "__main__":
    asyncio.run(main())
