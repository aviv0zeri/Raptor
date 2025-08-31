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
