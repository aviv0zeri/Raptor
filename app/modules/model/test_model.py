import os
import time
import random
from datetime import datetime
import requests


def write_signal_csv(model_output_path: str, signal: int, quantity: int, coin_symbol: str) -> None:
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    signal_str = 'BUY' if signal == 1 else 'HOLD'
    with open(model_output_path, 'a') as f:
        f.write(f"{now_str}, {signal_str}, {quantity}, {coin_symbol}\n")


def post_webhook(url: str, signal: int, price: float, reasoning: str = "Test model signal") -> None:
    payload = {
        "type": "model_signal",
        "data": {
            "timestamp": datetime.now().isoformat(),
            "signal": 'BUY' if signal == 1 else 'HOLD',
            "confidence": round(random.uniform(0.6, 0.95), 4),
            "price": price,
            "reasoning": reasoning,
        },
        "timestamp": datetime.now().isoformat(),
    }
    try:
        requests.post(url, json=payload, timeout=3)
    except Exception:
        pass


def main():
    print('Starting TEST model (random BUY/HOLD)...')

    # Output CSV path identical to main.py convention
    model_output_path = os.path.join('..', 'model_output.csv')
    target_coin = 'CHZ/USDT'
    webhook_url = 'http://localhost:5001/webhook'

    # Ensure file exists; create header if needed
    if not os.path.exists(model_output_path):
        with open(model_output_path, 'w') as f:
            # No header to match your existing CSV lines format
            pass

    while True:
        signal = random.choice([0, 1])
        price = round(random.uniform(150, 250), 2)

        write_signal_csv(model_output_path, signal, 1, target_coin)
        post_webhook(webhook_url, signal, price)

        print(f"Emitted test signal: {'BUY' if signal == 1 else 'HOLD'} @ {price}")
        time.sleep(10)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
🧠 Simple Test Model for Raptor Trading Bot
===========================================

This is a simplified model that outputs trading signals to CSV every 1 minute
for testing the main bot strategy.

Output Format:
timestamp, signal, quantity, coin
2025-08-29 14:30:00, BUY, 1, CHZ/USDT
"""

import time
import schedule
import random
from datetime import datetime
import os

def update_model_output_file(signal, quantity, coin, model_output_path):
    """Write signal to CSV file"""
    with open(model_output_path, 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{timestamp}, {signal}, {quantity}, {coin}\n')
    print(f"📊 Model Signal: {timestamp}, {signal}, {quantity}, {coin}")

def perform_action():
    """Generate a random trading signal"""
    signals = ['BUY', 'HOLD', 'SELL']
    signal = random.choice(signals)
    quantity = random.randint(1, 10)
    coin = 'CHZ/USDT'
    
    # Write to CSV
    model_output_path = os.path.join('..', 'model_output.csv')
    update_model_output_file(signal, quantity, coin, model_output_path)

def main():
    print('🧠 Starting Simple Test Model...\n')
    print('📊 Will output signals every 1 minute to model_output.csv\n')
    
    # Create CSV file if it doesn't exist
    model_output_path = os.path.join('..', 'model_output.csv')
    if not os.path.exists(model_output_path):
        with open(model_output_path, 'w') as f:
            f.write('timestamp, signal, quantity, coin\n')
        print(f"✅ Created {model_output_path}")
    
    # Schedule the function to run every 1 minute
    schedule.every(1).minutes.do(perform_action)
    
    print("⏰ Model scheduled to run every 1 minute")
    print("🔄 Starting signal generation...\n")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
