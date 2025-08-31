import logging

class CustomLogger:
    def __init__(self, log_file_name):
        self.log_file_name = log_file_name  # Store the log file name

        # Configure logging to log to a file
        logging.basicConfig(
            level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s [%(levelname)s]: %(message)s',  # Define the log message format
            datefmt='%Y-%m-%d %H:%M:%S',  # Define the date/time format
            filename=log_file_name,  # Specify the file to which logs should be written
            filemode='a'  # Use 'w' to overwrite the file or 'a' to append to an existing file
        )

        # Create a logger instance
        self.logger = logging.getLogger()

    def log(self, level, message):
        """Log the message at the specified level."""
        if level == 'debug':
            self.logger.debug(message)
        elif level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'critical':
            self.logger.critical(message)

    def read_last_log_entry(self):
        """Reads the last entry from the log file."""
        try:
            with open(self.log_file_name, 'r') as file:
                lines = file.readlines()
                if lines:
                    return lines[-1].strip()
                else:
                    return "Log file is empty."
        except FileNotFoundError:
            return "Log file not found."

    def read_log_entries_containing(self, keyword):
        """Reads log entries containing the specified keyword."""
        try:
            with open(self.log_file_name, 'r') as file:
                lines = file.readlines()
                filtered_lines = [line.strip() for line in lines if keyword in line]
                return filtered_lines
        except FileNotFoundError:
            return ["Log file not found."]

    def print_info_or_error_logs(self, log_type):
        """Prints logs of the specified type ('info' or 'error')."""
        if log_type.lower() == "error":
            error_logs = self.read_log_entries_containing('ERROR')
            if error_logs:
                for log in error_logs:
                    print("ERROR log entry:", log)
        elif log_type.lower() == "info":
            info_logs = self.read_log_entries_containing('INFO')
            if info_logs:
                for log in info_logs:
                    print("INFO log entry:", log)
        else:
            print("Invalid log type specified. Please use 'info' or 'error'.")
