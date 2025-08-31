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
from colorama import Fore, Style, init
import time  # Import time for tracking execution duration
import csv
import pandas as pd
import os
import asyncio

input("\nPress Enter to Start")

# Initialize colorama for colored terminal output
init(autoreset=True)

# Set up logging
logger = CustomLogger("app.log")

# Connect to Database
try:
    print("Attempting to connect to the database...")
    
    conn, db_name = connect()  # Get the connection object and database name
    if conn is None:
        raise ConnectionError("Failed to connect to the database")
    else:
        print(f"{Fore.YELLOW}\nConnection to the database was successful.\n{Style.RESET_ALL}")
        # ut.beep('success')
except ConnectionError as e:
    print(f"{Fore.RED}ConnectionError: {str(e)}{Style.RESET_ALL}")
    logger.log('error', str(e))
    # # ut.beep('fail')    exit(1)
except Exception as e:
    print(f"{Fore.RED}An unexpected error occurred: {str(e)}{Style.RESET_ALL}")
    logger.log('error', str(e))
    # # ut.beep('fail')    exit(1)
print("done\n")

# Create a cursor object for database operations
cur = conn.cursor()

# CSV file setup
order_number = 0  # Initialize order number
csv_file = 'bot_output.csv'
csv_initialized = False

# Initialize CSV file with headers if it does not exist
if not os.path.exists(csv_file):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Order Number", "Order Id", "Order Datetime", "Order Type", "Order Symbol", "Order Quantity", "Order Fees Amount", "Order Price", "Order Side", "Order Execution Time"])
else:
    # Read the last order number from the existing CSV file
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) > 1:  # Check if there's more than just the header
            last_order_number = int(rows[-1][0])  # Get the last order number
            order_number = last_order_number    # Increment it for the next order

# Configuration constants
NOFIAT = "NOFIAT"  # Indicator for canceling purchase with fiat amount
USD_FIAT = "USDT"  # The base fiat currency for USD value
test_order = False  # Flag for test orders

# Initialize the Binance client
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

# Initial wallet update
ut.update_wallet_data(client)

# Startup beep
# ut.beep('startup')

print(f"{Fore.GREEN}ALGOTRADE 2024 -\n NO PAPER TRADING IN THIS VERSION{Style.RESET_ALL}")

# Print wallet information at the start
ut.print_wallet()
print("")

# Initialize a list to store execution times
execution_times = []

async def main():
    global order_number  # Allow access to the order_number variable
    receipt = Receipt()  # Initialize receipt object for storing order details

    while True:
        # Prompt for test or real order
        test_input = input("Enter T for test order or R for real order: ").strip().lower()
        # ut.beep('alert')

        if test_input in ('t', 'test'):
            test_order = True
        elif test_input in ('r', 'real'):
            test_order = False
        else:
            # ut.beep('fail')            print(f"{Fore.RED}Invalid input. Please enter T or R.{Style.RESET_ALL}")
            continue

        # Prompt for buy or sell action
        side_input = input("Enter your action(B for buy S for sell): ").strip().lower()
        # ut.beep('alert')

        if side_input in ('s', 'sell'):
            side = 'SELL'
        elif side_input in ('b', 'buy'):
            side = 'BUY'
        else:
            # ut.beep('fail')            print(f"{Fore.RED}Invalid input. Please enter a valid action.{Style.RESET_ALL}")
            continue

        # Prompt for coin and base coin
        coin = input("\nEnter Coin: ").strip().upper()
        # ut.beep('alert')
        base_coin = input("\nEnter Base Coin: ").strip().upper()
        # ut.beep('alert')

        # Prompt for amount and handle conversion
        try:
            amount = float(input("\nEnter Amount: ").strip())
            # ut.beep('alert')
        except ValueError:
            # ut.beep('fail')            print(f"{Fore.RED}Invalid amount. Please enter a numeric value.{Style.RESET_ALL}")
            continue

        # Print debug information before making the order
        print("")
        print(f"\n{Fore.MAGENTA}Debug Info:{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Action: {side}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Coin: {coin}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Base Coin: {base_coin}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Amount: {amount}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}USD_FIAT: {USD_FIAT}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Test Order: {test_order}{Style.RESET_ALL}\n")

        # Record the start time of the order
        start_time = time.time()

        # Place the order
        receipt = await ut.make_order(cur, conn, client, logger, coin, base_coin, amount, side, USD_FIAT, receipt, test_order)

        # Record the end time of the order and calculate the execution time
        end_time = time.time()
        execution_time = end_time - start_time

        # Add the execution time to the list
        execution_times.append(execution_time)

        # Calculate the average execution time
        average_execution_time = sum(execution_times) / len(execution_times)

        # Print the receipt or error details
        if receipt and receipt.type is not None:
            side_color = Fore.BLUE
            # ut.beep('success')
            print("")
            print(f"{Fore.MAGENTA}Exchange successful:{Style.RESET_ALL}")
            print(f"{Fore.BLUE}Symbol: {receipt.symbol}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}Amount: {receipt.quantity}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}Type: {receipt.type}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}Side: {receipt.side}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}Order ID: {receipt.order_id}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}Execution Time: {execution_time:.2f} seconds{Style.RESET_ALL}")

            # Print average execution time
            print(f"\n{Fore.LIGHTCYAN_EX}Average Execution Time: {average_execution_time:.2f} seconds{Style.RESET_ALL}")

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
        else:
            # ut.beep('fail')            print("")
            print(f"{Fore.RED}{receipt.error}{Style.RESET_ALL}")

        # Update wallet data and print wallet information again after the transaction
        ut.update_wallet_data(client)
        ut.print_wallet()
        print("\n")

if __name__ == "__main__":
    asyncio.run(main())
