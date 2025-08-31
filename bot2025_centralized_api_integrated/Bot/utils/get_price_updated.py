import tkinter as tk
from binance.client import Client
import time

from tools.config import BINANCE_SECRET_KEY, BINANCE_API_KEY
from tools.api_utils import make_binance_request  # Import the new API wrapper

# Initialize Binance client
API_KEY = BINANCE_API_KEY
API_SECRET = BINANCE_SECRET_KEY
client = Client(API_KEY, API_SECRET)

def get_coin_value(coin):
    """Fetch the current value of the specified coin in USDT."""
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": f"{coin}USDT"}
        response = make_binance_request("GET", url, params=params)
        if response and 'price' in response.json():
            return float(response.json()['price'])
        else:
            print(f"Unexpected response format: {response}")
            return None
    except Exception as e:
        print(f"Error fetching {coin} value: {e}")
        return None


def update_value(coin):
    """Update the value in the GUI."""
    value = get_coin_value(coin)
    if value is not None:
        value_label.config(text=f"{coin} Value: {value:.9f} USDT")  # Show 9 decimal places
    else:
        value_label.config(text=f"Error fetching {coin} value.")
    root.after(1000, update_value, coin)  # Update every second

# GUI setup
root = tk.Tk()
root.title("Binance Coin Value Tracker")

coin_input = tk.Entry(root)
coin_input.pack(pady=10)
coin_input.insert(0, 'Enter coin symbol (e.g., BTC)')

value_label = tk.Label(root, text="", font=('Helvetica', 16))
value_label.pack(pady=20)

def start_tracking():
    coin = coin_input.get().strip().upper()
    update_value(coin)

start_button = tk.Button(root, text="Start Tracking", command=start_tracking)
start_button.pack(pady=10)

# Start the GUI main loop
root.mainloop()
