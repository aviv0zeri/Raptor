import time
import csv
import os
import asyncio
import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
from pybit.unified_trading import HTTP
from binance.client import Client
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

# Set up logging
logger = CustomLogger("app.log")

# Create the main window
root = tk.Tk()
root.title("Order Tester")  # Changed title to "Order Tester"

# Set dark theme colors
root.configure(bg='#3A3A3A')  # Slightly lighter background
text_color = '#FFFFFF'  # White text for contrast
log_box_bg = '#2E2E2E'  # Darker background for the log box

# Set window size
root.geometry("600x400")  # Increase window size

# Create a scrolled text box for logging messages
log_box = scrolledtext.ScrolledText(root, width=70, height=15, state='disabled', bg=log_box_bg, fg=text_color, font=('Helvetica', 10))
log_box.grid(row=4, column=0, columnspan=2)

def log_message(message):
    log_box.configure(state='normal')  # Allow editing
    log_box.insert(tk.END, message + "\n")  # Append message
    log_box.configure(state='disabled')  # Prevent editing
    log_box.yview(tk.END)  # Scroll to the end
    logger.log('info', message)  # Log message to the logger

class RedirectStdout:
    def __init__(self, log_func):
        self.log_func = log_func

    def write(self, message):
        if message.strip():  # Avoid logging empty messages
            self.log_func(message.strip())

    def flush(self):  # No-op for flush
        pass

# Redirect stdout to the log_message function
sys.stdout = RedirectStdout(log_message)

# Connect to Database
try:
    print("Attempting to connect to the database...")
    conn, db_name = connect()
    if conn is None:
        raise ConnectionError("Failed to connect to the database")
    else:
        print("Connection to the database was successful.")
except ConnectionError as e:
    print(f"ConnectionError: {str(e)}")
    logger.log('error', str(e))
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
    logger.log('error', str(e))
print("done\n")

# Create a cursor object for database operations
cur = conn.cursor()

# CSV file setup
order_number = 0
csv_file = 'bot_output.csv'

if not os.path.exists(csv_file):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Order Number", "Order Id", "Order Datetime", "Order Type", "Order Symbol", "Order Quantity", "Order Fees Amount", "Order Price", "Order Side", "Order Execution Time"])
else:
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) > 1:
            last_order_number = int(rows[-1][0])
            order_number = last_order_number

# Initialize the Binance client
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

# Initial wallet update
ut.update_wallet_data(client)

# Initialize a list to store execution times
execution_times = []

def display_wallet():
    wallet_info = ut.wallet_data  # Get the wallet data
    log_message("Wallet Information:")
    
    total_value = 0
    log_message(f"{'Coin':<10} {'Balance':<15} {'USD Value':<15}")  # Header
    log_message("-" * 40)  # Divider
    
    for coin, data in wallet_info.items():  # Format as needed
        balance = data['balance']
        usd_value = data['usd_value']
        total_value += usd_value
        log_message(f"{coin:<10} {balance:<15} ${usd_value:<15.2f}")

    log_message("-" * 40)  # Divider
    log_message(f"{'Total':<10} {'':<15} ${total_value:<15.2f}")  # Total value

# Make execute_order async for async functionality
async def execute_order(order_type):
    global order_number
    coin = coin_entry.get().strip().upper()
    base_coin = base_coin_entry.get().strip().upper()
    amount = amount_entry.get().strip()

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a numeric value for amount.")
        return

    # Record the start time of the order
    start_time = time.time()

    # Place the order
    receipt = await ut.make_order(cur, conn, client, logger, coin, base_coin, amount, order_type, "USDT", ord.Receipt(), False)

    # Record the end time of the order and calculate the execution time
    end_time = time.time()
    execution_time = end_time - start_time
    execution_times.append(execution_time)

    if receipt and receipt.type is not None:
        # Log and print the successful order information
        print("Exchange successful:")
        print(f"Symbol: {receipt.symbol}")
        print(f"Amount: {receipt.quantity}")
        print(f"Type: {receipt.type}")
        print(f"Side: {receipt.side}")
        print(f"Order ID: {receipt.order_id}")
        print(f"Execution Time: {execution_time:.2f} seconds")

        # Increment the order number
        order_number += 1
        # Append the order details to the CSV file
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                order_number,
                receipt.order_id,
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),  # Order Datetime
                receipt.type,
                receipt.symbol,
                receipt.quantity,
                receipt.fees_amount,
                receipt.price,
                receipt.side,
                execution_time
            ])
        
        # Update wallet data
        ut.update_wallet_data(client)
        display_wallet()  # Display wallet after a successful order
    else:
        messagebox.showerror("Order Error", "Failed to execute the order.")

# Create and place labels and entries with bold text
tk.Label(root, text="Coin:", bg='#3A3A3A', fg=text_color, font=('Helvetica', 12, 'bold')).grid(row=0, column=0)
coin_entry = tk.Entry(root)
coin_entry.grid(row=0, column=1)

tk.Label(root, text="Base Coin:", bg='#3A3A3A', fg=text_color, font=('Helvetica', 12, 'bold')).grid(row=1, column=0)
base_coin_entry = tk.Entry(root)
base_coin_entry.grid(row=1, column=1)

tk.Label(root, text="Amount:", bg='#3A3A3A', fg=text_color, font=('Helvetica', 12, 'bold')).grid(row=2, column=0)
amount_entry = tk.Entry(root)
amount_entry.grid(row=2, column=1)

# Create Buy and Sell buttons with bold text
buy_button = tk.Button(root, text="Buy", command=lambda: asyncio.create_task(execute_order('BUY')), font=('Helvetica', 12, 'bold'))
buy_button.grid(row=3, column=0)

sell_button = tk.Button(root, text="Sell", command=lambda: asyncio.create_task(execute_order('SELL')), font=('Helvetica', 12, 'bold'))
sell_button.grid(row=3, column=1)

# Display wallet on startup
display_wallet()

root.mainloop()
