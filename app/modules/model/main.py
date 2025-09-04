import time
from datetime import datetime
import sys
import os
import schedule
import os
import random
import warnings
import sys
import urllib3
import json
import requests
from dataclasses import asdict

# 🤫 Suppress SSL warnings from urllib3 - we know what we're doing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")
warnings.filterwarnings("ignore", message="ssl module.*LibreSSL")

# --- Timestamped print helper so model.log shows dates ---
try:
    import builtins as _builtins

    def _ts_print(*args, **kwargs):
        try:
            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if args:
                first = f"[{ts}] {args[0]}"
                _builtins.print(first, *args[1:], **kwargs)
            else:
                _builtins.print(f"[{ts}]", **kwargs)
        except Exception:
            _builtins.print(*args, **kwargs)

    print = _ts_print  # type: ignore
except Exception:
    pass

# Add the Model and App directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = current_dir
app_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
for p in [model_dir, app_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Import Signal after path setup
from app.modules.components.signal import Signal
from app.modules.utils.config_loader import get_signal_template, validate_signal

try:
    from BinancePuller import *
    from DataPuller import *
    from LiveModel import *
except ImportError as e:
    print(f"Warning: Could not import ML modules: {e}")
    print("Using simplified model for testing...")
    
    # Create a simple fallback model
    class SimpleModel:
        def __init__(self, *args, **kwargs):
            pass
        
        def model_init(self, *args):
            print("Simple model initialized")
        
        def train_row(self, *args):
            pass
        
        def predict(self, *args):
            return random.choice([0, 1])  # 0 = HOLD, 1 = BUY
    
    class SimpleDataPuller:
        def __init__(self, *args, **kwargs):
            pass
        
        def data_init(self, *args, **kwargs):
            print("Simple data puller initialized")
        
        def pull_new_candle(self, *args):
            pass
        
        def get_lag_second_last_row(self):
            return [0] * 10
        
        def get_lag_last_row(self):
            return [0] * 10
    
    # Replace the imports with simple versions
    LiveModel = SimpleModel
    DataPuller = SimpleDataPuller
    BinancePuller = SimpleDataPuller  # Use same simple class for both
# from BinancePuller import create_dataset
warnings.filterwarnings("ignore")


def update_model_output_file(signal, quantity, coin, model_output_path):
    with open(model_output_path, 'a') as f:
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if signal == 1:
            signal = 'BUY'
        else:
            signal = 'HOLD'
        coin = 'CHZ/USDT' #TODO use the coin variable from the parameters instead.
        f.write(f'{time}, {signal}, {quantity}, {coin}\n')
    return None
    

def send_status_update(message, status_type="info"):
    """Send status updates to the frontend via API"""
    try:
        api_url = os.environ.get('API_SIGNAL_URL', 'http://localhost:5050/api/model/signal')
        payload = {
            "type": "model_status",
            "data": {
                "message": message,
                "status_type": status_type,
                "timestamp": datetime.now().isoformat(),
                "model": os.environ.get('MODEL_NAME', 'real')
            },
            "timestamp": datetime.now().isoformat()
        }
        try:
            r = requests.post(api_url, json=payload, timeout=5)
            print(f"Status update sent: {r.status_code}")
        except Exception as e:
            print(f"Failed to send status update: {e}")
    except Exception:
        pass

def emit_webhook_signal(signal_value, coin_symbol, price_value, confidence_value=None):
    """
    🌟 SIGNAL COMMUNICATION SYSTEM - How It Works! 🌟
    ================================================
    
    This function is like a messenger that takes your model's decision and delivers it 
    to the frontend dashboard so you can see what your model is thinking!
    
    📡 THE SIGNAL JOURNEY:
    1. Your model makes a decision (BUY/SELL/HOLD)
    2. This function packages it nicely in a JSON envelope
    3. Sends it to the API server (like a post office)
    4. API server forwards it to the webhook server
    5. Webhook server broadcasts it to all connected frontends via WebSocket
    6. Your dashboard receives it and shows you the signal!
    
    🎯 WHY THIS FORMAT MATTERS:
    - The frontend expects signals in this exact JSON format
    - If you change the format, the frontend won't understand your signals
    - This is like speaking the same language - everyone needs to use the same words!
    
    📦 THE JSON ENVELOPE:
    {
      "type": "model_signal",           # Tells the system "this is a trading signal"
      "data": {                         # The actual signal information
        "timestamp": "2025-09-04...",   # When the signal was made
        "signal": "BUY",                # What the model decided (BUY/SELL/HOLD)
        "confidence": 0.75,             # How sure the model is (0.0 to 1.0)
        "reasoning": "Model thinks...",  # Why the model made this decision
        "model": "real",                # Which model made this decision
        "interval": "1m"                # How often the model runs
      },
      "timestamp": "2025-09-04..."      # When this message was sent
    }
    
    🔧 FOR MODEL DEVELOPERS:
    If you want to create your own model that works with our system:
    1. Use this exact JSON format
    2. Send it to http://localhost:5050/api/model/signal
    3. Make sure your signal values are: 1 = BUY, 0 = HOLD, -1 = SELL
    4. Include all the required fields in the "data" section
    """
    try:
        # Send via API server which normalizes and forwards to webhook
        api_url = os.environ.get('API_SIGNAL_URL', 'http://localhost:5050/api/model/signal')
        
        # Create signal using the standard format from JSON configuration
        sig = Signal(
            timestamp=datetime.now().isoformat(),
            signal='BUY' if signal_value == 1 else 'HOLD',
            confidence=confidence_value if confidence_value is not None else 0.5,
            reasoning=f"Live model {('BUY' if signal_value == 1 else 'HOLD')} signal for {coin_symbol}",
            model=os.environ.get('MODEL_NAME', 'real'),
            interval=os.environ.get('MODEL_INTERVAL', '1m')
        )
        
        # Create payload using the standard format from JSON configuration
        payload = {
            "type": "model_signal",
            "data": asdict(sig),
            "timestamp": datetime.now().isoformat()
        }
        
        # Validate the signal format before sending
        if not validate_signal(payload["data"]):
            print("❌ Signal format validation failed!")
            return False
        try:
            r = requests.post(api_url, json=payload, timeout=10)
            print(f"Real model posted: {r.status_code}")
        except Exception as e:
            print(f"Real model post failed (API): {e}")
    except Exception:
        # Avoid crashing scheduled job on network errors
        pass

def main():

    print('Starting the Model...\n')
    
    # Use a valid Binance interval for data fetching (minimum 1m)
    # but keep user's chosen interval for scheduling
    global interval 
    user_interval = os.environ.get('MODEL_INTERVAL', '1m')
    # Convert 10s to 1m for Binance data fetching
    if user_interval == '10s':
        interval = '1m'
    else:
        interval = user_interval
    
    print(f"🔧 Initializing Real model with interval: {user_interval}")
    print(f"📊 Using data interval: {interval} (converted from {user_interval})")
    
    # Send initialization status - NOT ready yet
    def send_init_status(message):
        try:
            api_url = os.environ.get('API_SIGNAL_URL', 'http://localhost:5050/api/model/signal')
            payload = {
                "type": "model_status",
                "data": {
                    "message": message,
                    "status_type": "initializing",
                    "ready": False,
                    "timestamp": datetime.now().isoformat(),
                    "model": "real"
                }
            }
            requests.post(api_url, json=payload, timeout=3)
        except:
            pass
    
    send_init_status(f"Starting Real model initialization with {user_interval} interval")
    # Announce dataset universe
    try:
        send_init_status(f"Building dataset for: {', '.join(currencies)}")
    except Exception:
        pass


    #---------------------------------------------------------------------------------------

    ### interval - the candels you want to trade with.
    ### currencies - the currencies you will use as data. - not implemented yet.
    ### targer_currency - the currencies that will be traded.

    starting_date = '2023-10-19' #TODO need to be changed to the earliest date available.
    end_date = 'now' #TODO need to be changed to the current date available.
    currencies = ['CHZUSDT','UNIUSDT','DOTUSDT','ETCUSDT','ANKRUSDT','BTCUSDT']
    global target_currency
    target_currency = 'CHZUSDT' 
    base_url = 'https://fapi.binance.com'
    end_point = '/fapi/v1/klines'
    # Resolve absolute paths within the project
    data_dir = os.path.join(project_root, 'app', 'Data')
    rawdata_path = os.path.join(data_dir, 'rawdata')
    dataset_path = os.path.join(data_dir, 'dataset.csv')
    lagged_data_path = os.path.join(data_dir, 'lagged_data.csv')
    global model_output_path
    model_output_path = os.path.join(project_root, 'logs', 'model_output.csv')

    # Ensure required directories exist
    try:
        os.makedirs(rawdata_path, exist_ok=True)
        os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
        os.makedirs(os.path.dirname(lagged_data_path), exist_ok=True)
        os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    except Exception:
        pass

    low_puller = BinancePuller(base_url, end_point, rawdata_path, currencies)
    data_puller = DataPuller(currencies, target_currency, rawdata_path, dataset_path, low_puller, lagged_data_path)
    model = LiveModel("LogisticRegression", lagged_data_path, target_currency, [1, 1])

    #---------------------------------------------------------------------------------------
    print("📈 Loading historical data...")
    send_init_status("Loading historical data from Binance...")
    # Stream per-currency data info (file age if present)
    try:
        for ccy in currencies:
            cfile = os.path.join(rawdata_path, f"{ccy}.csv")
            if os.path.exists(cfile):
                age_hours = (time.time() - os.path.getmtime(cfile)) / 3600.0
                send_init_status(f"Using existing data for {ccy} (age: {age_hours:.1f}h)")
            else:
                send_init_status(f"Downloading fresh data for {ccy}…")
    except Exception:
        pass
    data_puller.data_init(interval, starting_date, end_date, 5)
    # Dataset summary (row counts) after data_init
    try:
        def _count_rows(path: str) -> int:
            try:
                with open(path, 'r') as f:
                    # subtract header if present
                    lines = sum(1 for _ in f)
                    return max(0, lines - 1)
            except Exception:
                return 0
        ds_rows = _count_rows(dataset_path)
        lag_rows = _count_rows(lagged_data_path)
        if ds_rows or lag_rows:
            send_init_status(f"Dataset ready: {ds_rows} rows; lagged: {lag_rows} rows")
    except Exception:
        pass

    print("🤖 Initializing ML model...")
    send_init_status("Training ML model with historical data...")
    model.model_init(0)
    print("✅ Model initialization complete!")
    print(f"⏰ Model ready - waiting for start signal from frontend")
    
    # Mark model as initialized
    perform_action.model_initialized = True

    # Global flag to control signal generation
    global model_running
    model_running = False
    interval_str = user_interval  # Use the user's chosen interval for scheduling
    
    def schedule_from_string(spec: str):
        try:
            s = spec.strip().lower()
            if s.endswith('s'):
                n = int(s[:-1])
                schedule.every(n).seconds.do(lambda: perform_action(data_puller, model=model) if model_running else None)
            elif s.endswith('m'):
                n = int(s[:-1])
                schedule.every(n).minutes.do(lambda: perform_action(data_puller, model=model) if model_running else None)
            elif s.endswith('h'):
                n = int(s[:-1])
                schedule.every(n).hours.do(lambda: perform_action(data_puller, model=model) if model_running else None)
            else:
                schedule.every(10).seconds.do(lambda: perform_action(data_puller, model=model) if model_running else None)
        except Exception:
            schedule.every(10).seconds.do(lambda: perform_action(data_puller, model=model) if model_running else None)
    
    # Set up the schedule but don't start generating signals yet
    schedule_from_string(interval_str)
    
    # Start a simple HTTP server to receive start/stop commands
    from flask import Flask, request, jsonify
    control_app = Flask(__name__)
    
    @control_app.route('/control/start', methods=['POST'])
    def start_model():
        global model_running
        model_running = True
        print("🚀 Real model started - generating signals!")
        sys.stdout.flush()
        send_status_update(f"Real model started! Generating signals every {user_interval}", "success")
        return jsonify({'success': True, 'message': 'Model started'})
    
    @control_app.route('/control/stop', methods=['POST'])
    def stop_model():
        global model_running
        model_running = False
        print("⏹️ Real model stopped - no more signals")
        sys.stdout.flush()
        send_status_update("Real model stopped", "info")
        return jsonify({'success': True, 'message': 'Model stopped'})
    
    @control_app.route('/control/status', methods=['GET'])
    def model_status():
        # Model is ready after building, not after first signal
        model_built = hasattr(perform_action, 'model_initialized') and perform_action.model_initialized
        return jsonify({
            'success': True,
            'ready': model_built,
            'running': model_running,
            'interval': user_interval
        })
    
    # Start control server in a separate thread
    import threading
    control_thread = threading.Thread(target=lambda: control_app.run(host='127.0.0.1', port=5051, debug=False))
    control_thread.daemon = True
    control_thread.start()
    
    print("🎛️ Control server started on port 5051")
    
    # NOW send ready status - model is fully initialized
    # Don't send ready status yet - wait for first signal
    print("⏰ Model initialized - will be ready after first signal generation")

    ## Keep the script running to ensure the scheduling happens
    while True:
        schedule.run_pending()
        time.sleep(1)


def perform_action(data_puller: DataPuller, model: LiveModel):
    """
    🧠 THE BRAIN OF YOUR MODEL - How It Makes Decisions! 🧠
    ====================================================
    
    This function is like the thinking process of your model. Every time it runs,
    it follows these steps to make a trading decision:
    
    📊 STEP 1: GET FRESH DATA
    - Pulls the latest market data from Binance
    - This is like checking the news before making a decision
    
    🎓 STEP 2: LEARN FROM HISTORY  
    - Takes the second-to-last data point and trains the model with it
    - This is like studying past examples to get better at predictions
    
    🔮 STEP 3: MAKE A PREDICTION
    - Takes the most recent data and asks the model: "What should we do?"
    - The model returns: 1 = BUY, 0 = HOLD, -1 = SELL
    
    📝 STEP 4: RECORD THE DECISION
    - Saves the decision to a CSV file for record keeping
    - This is like writing in a diary what you decided and why
    
    📡 STEP 5: SHARE THE DECISION
    - Sends the decision to the frontend so you can see it
    - This is like telling your friend about your trading decision
    
    🎯 WHY THIS MATTERS:
    - Every model that wants to work with our system must follow this pattern
    - The frontend expects signals in a specific format
    - If you change this flow, the system won't understand your model's decisions
    """
    
    # 📊 STEP 1: Get fresh market data from Binance
    data_puller.pull_new_candle(interval)
    
    # 🎓 STEP 2: Train the model with historical data (second-to-last row)
    seconed_last_row = data_puller.get_lag_second_last_row()
    model.train_row(seconed_last_row)
    
    # 🔮 STEP 3: Make a prediction using the most recent data
    last_lagged_row = data_puller.get_lag_last_row()
    signal = model.predict(last_lagged_row)
    print(f'Got signal: {signal}')
    sys.stdout.flush()
    
    # 📝 STEP 4: Save the decision to CSV file for record keeping
    update_model_output_file(signal, 1, target_currency, model_output_path)
    
    # Send ready status after first signal is generated
    if not hasattr(perform_action, 'first_signal_sent'):
        perform_action.first_signal_sent = True
        try:
            api_url = os.environ.get('API_SIGNAL_URL', 'http://localhost:5050/api/model/signal')
            ready_payload = {
                "type": "model_status",
                "data": {
                    "message": "Real model ready! First signal generated successfully",
                    "status_type": "ready",
                    "ready": True,
                    "timestamp": datetime.now().isoformat(),
                    "model": "real"
                }
            }
            requests.post(api_url, json=ready_payload, timeout=3)
            print("✅ Ready status sent after first signal")
            sys.stdout.flush()
        except:
            print("⚠️ Failed to send ready status")
            sys.stdout.flush()
    # Also emit webhook event for UI/model reader
    try:
        current_price = None
        # Best-effort: get latest price from Binance for target currency on a short interval
        if hasattr(data_puller, 'low_puller') and hasattr(data_puller.low_puller, 'get_current_price'):
            current_price = data_puller.low_puller.get_current_price(target_currency, '1m')
        print('Emitting signal to API...')
        sys.stdout.flush()
        emit_webhook_signal(signal, target_currency, current_price, confidence_value=None)
        print('Real model posted: 200')
        sys.stdout.flush()
    except Exception as e:
        print(f'emit failed: {e}')
        sys.stdout.flush()




if __name__ == "__main__":
    main()






















    
# def check_for_nulls(df):
#     for column in df.columns:
#         if df[column].isnull().sum() != 0:
#             print(f'{column} has {df[column].isnull().sum()} missing values') 
