import psycopg2  # Used for interacting with PostgreSQL databases
from ..config.config_manager import get_config  # Use centralized config manager
from .order import Order  # Adjust the import path to match your directory structure
from ..utils.log_module import CustomLogger  # Adjust the import path to match your directory structure

# Initialize a logger for logging errors and information
logger = CustomLogger("app.log")

# Function to connect to the PostgreSQL database
def connect():
    try:
        # Build DB params from config manager
        db_params = {
            'host': get_config('database', 'host', 'localhost'),
            'port': get_config('database', 'port', 5432),
            'dbname': get_config('database', 'dbname', 'trading_bot'),
            'user': get_config('database', 'user', 'postgres'),
            'password': get_config('database', 'password', 'password'),
        }
        # Establish a database connection using the config parameters
        conn = psycopg2.connect(**db_params)
        # Retrieve the database name from the configuration
        db_name = db_params.get('dbname', 'Unknown Database')
        return conn, db_name  # Return the connection object and database name
    except Exception as e:
        logger.log('error', f"Error: Unable to connect to the database. {e}")
        return None, None  # Return None if connection fails

# Function to create a database table (if it doesn't exist)
def create_table(cursor):
    try:
        # SQL query to create a table named 'orders' with specified columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id VARCHAR(20) PRIMARY KEY,
                order_datetime TIMESTAMP,
                exchange VARCHAR(255),
                symbol VARCHAR(255),
                side VARCHAR(10),
                quantity DECIMAL(30, 10),
                price DECIMAL(30, 10),
                fees_amount DECIMAL(30, 10),
                fees_coin VARCHAR(20),
                is_test VARCHAR(255)
            )
        """)
        logger.log('info', "Database table is created/verified")
        return True  # Return True if table creation succeeds
    except Exception as e:
        logger.log('error', f"Error: Unable to create table. {e}")
        return False  # Return False if an error occurs during table creation

# Function to insert an order into the database
def insert_order(cursor, order):
    try:
        # SQL INSERT query with the new columns (fees and is_test)
        sql_query = """
            INSERT INTO orders (order_id, order_datetime, exchange, symbol, side, quantity, price, fees_amount, fees_coin, is_test)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Values to be inserted from the 'order' object
        values = (order.order_id, order.order_datetime, order.exchange, order.symbol, order.side, order.quantity, order.price, order.fees_amount, order.fees_coin, order.is_test)
        cursor.execute(sql_query, values)
        logger.log('info', "Order inserted into the database successfully")
        return True  # Return True if the insertion succeeds
    except Exception as e:
        logger.log('error', f"Error: Unable to insert order. {e}")
        return False  # Return False if an error occurs during insertion

# Function to retrieve all orders from the database
def get_all_orders(cursor):
    try:
        cursor.execute("SELECT * FROM orders")
        rows = cursor.fetchall()
        orders = []
        for row in rows:
            # Create an Order object and populate it with data from the database
            order = Order()
            order.order_id = row[0]
            order.order_datetime = row[1]
            order.exchange = row[2]
            order.symbol = row[3]
            order.side = row[4]
            order.quantity = row[5]
            order.price = row[6]
            order.fees_amount = row[7]
            order.fees_coin = row[8]
            order.is_test = row[9]
            orders.append(order)  # Append the order to the list
        return orders  # Return a list of Order objects
    except Exception as e:
        logger.log('error', f"Error: Unable to fetch orders. {e}")
        return []  # Return an empty list if an error occurs

# Function to retrieve an order by its ID from the database
def get_order_by_id(cursor, order_id):
    try:
        cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        row = cursor.fetchone()
        if row:
            # Create an Order object and populate it with data from the database
            order = Order()
            order.order_id = row[0]
            order.order_datetime = row[1]
            order.exchange = row[2]
            order.symbol = row[3]
            order.side = row[4]
            order.quantity = row[5]
            order.price = row[6]
            order.fees_amount = row[7]
            order.fees_coin = row[8]
            order.is_test = row[9]
            return order  # Return the Order object
        else:
            logger.log('info', "Order not found.")
            return None  # Return None if the order is not found
    except Exception as e:
        logger.log('error', f"Error: Unable to get order. {e}")
        return None  # Return None if an error occurs

# Function to delete all records from the 'orders' table
def delete_all_orders(cursor):
    try:
        cursor.execute("DELETE FROM orders")
        logger.log('info', "All the records are deleted")
        return True  # Return True if deletion succeeds
    except Exception as e:
        logger.log('error', f"Error: Unable to delete all orders. {e}")
        return False  # Return False if an error occurs during deletion

# Function to delete an order by its ID from the database
def delete_order_by_id(cursor, order_id):
    try:
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        logger.log('info', f"Order {order_id} is deleted from the database")
        return True  # Return True if deletion succeeds
    except Exception as e:
        logger.log('error', f"Error: Unable to delete order. {e}")
        return False  # Return False if an error occurs during deletion
