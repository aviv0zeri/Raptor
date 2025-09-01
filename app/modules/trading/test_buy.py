import asyncio
import sys
import os
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.modules.trading.trading_utils import make_order
from app.modules.utils.log_module import CustomLogger
from app.modules.database.database import connect
from app.modules.database.order import Receipt
from binance.client import Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

receipt = Receipt()
# Configuration constants
NOFIAT = "NOFIAT"  # Indicator for canceling purchase with fiat amount
USD_FIAT = "USDT"  # The base fiat currency for USD value
test_order = False  # Flag for test orders

# Initialize the Binance client
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

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

receipt = make_order(cur, conn, client, logger, "BTC", "USDT", 11, "BUY", "USDT", receipt, False)
print(receipt)
