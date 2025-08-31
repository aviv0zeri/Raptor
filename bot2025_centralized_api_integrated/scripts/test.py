import time
from Bot.ver_1.tools.bot_output_logger import log_to_stoploss, log_to_details

def main_logic():
    """Simulate task that logs messages to two separate loggers."""
    while True:
        # Log messages to the stoploss logger (no ID needed for stoploss)
        log_to_stoploss(f"Stoploss - Log entry at {time.strftime('%H:%M:%S')}", "dasdsas")
        time.sleep(2)  # Wait for 2 seconds before logging again

        # Log messages to the details logger with unique ID generated inside the function
        log_to_details(f"Details - Log entry at {time.strftime('%H:%M:%S')}")
        time.sleep(2)  # Wait for 2 seconds before logging again
