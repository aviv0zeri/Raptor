import requests
import uuid
import time
from datetime import datetime, timezone, timedelta

# Flask API URL for logging data for the first logger (Stoploss)
FLASK_API_STOPLOSS = "http://127.0.0.1:5000/log_data_stoploss"

# Flask API URL for logging data for the second logger (Details)
FLASK_API_DETAILS = "http://127.0.0.1:5000/log_data_details"

def log_to_stoploss(current_price, highest_limit):
    """Send a log message to the first logger in Flask via POST request."""
    try:
        # Get the current time in GMT+3
        israel_tz = timezone(timedelta(hours=3))
        timestamp = datetime.now(israel_tz).isoformat()  # Format as ISO 8601 string
        data = {"current_price": current_price, "highest_limit": highest_limit, "timestamp": timestamp}
        
        response = requests.post(FLASK_API_STOPLOSS, json=data)
        if response.status_code != 200:
            print(f"Failed to send log data to logger 1: {response.status_code}")
        else:
            return data
    except Exception as e:
        print(f"Error sending log data to logger 1: {e}")
        return None
    
def log_to_details(message):
    """Send a log message to the second logger in Flask via POST request."""
    try:
        log_id = str(uuid.uuid4())  # Generate a unique ID for this log entry
        data = {"id": log_id, "message": message}
        response = requests.post(FLASK_API_DETAILS, json=data)
        if response.status_code != 200:
            print(f"Failed to send log data to logger 2: {response.status_code}")
        else:
            # Return the generated ID and message for further use (if needed)
            return log_id, message
    except Exception as e:
        print(f"Error sending log data to logger 2: {e}")
        return None, None
