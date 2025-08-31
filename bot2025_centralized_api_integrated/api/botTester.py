import threading
import time
import requests  # For checking if Flask is up
import app  # Import the Flask app from app.py
import subprocess  # For running the bot processes (run.py)

# Function to start the Flask server
def start_flask():
    print("Starting Flask server...")
    app.app.run(debug=True, use_reloader=False)  # Calling the main function in app.py to run the Flask server

# Function to check if Flask server is up (by polling the /ready route)
def check_flask_ready():
    url = 'http://127.0.0.1:5000/ready'  # URL of the Flask app /ready route
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Flask server is up and running!")
                return True  # Return True when Flask is ready
        except requests.ConnectionError:
            # Wait for a short period before retrying
            time.sleep(1)

# Function to run run.py as a subprocess (running bot logic)
def run_bot_process():
    print("Starting bot processes (run.py)...")
    subprocess.run(["python", "run.py"])  # This will run the main() function from run.py

if __name__ == "__main__":
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    # Wait for Flask server to be ready (i.e., the /ready route is accessible)
    if check_flask_ready():  # Only if Flask is ready, we start the bot processes
        # Once Flask is ready, start the bot logic (run.py) in the background as a separate thread
        bot_thread = threading.Thread(target=run_bot_process)
        bot_thread.start()

    # Wait for Flask thread to finish (this will run indefinitely)
    flask_thread.join()
    bot_thread.join()  # Ensure the bot thread is also completed if it's not running indefinitely
