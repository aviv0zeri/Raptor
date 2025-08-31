from flask import Flask, render_template, jsonify, request
import uuid  # To generate unique IDs for each log entry

app = Flask(__name__)

# In-memory storage for two sets of logs
logs_stoploss = []
logs_details = []

@app.route('/')
def index():
    """Serve the HTML page with two log boxes."""
    return render_template('index.html')

@app.route('/get_logs_stoploss', methods=['GET'])
def get_logs_stoploss():
    """Return the stoploss log data."""
    return jsonify(logs_stoploss)

@app.route('/get_logs_details', methods=['GET'])
def get_logs_details():
    """Return the details log data."""
    return jsonify(logs_details)

@app.route('/log_data_stoploss', methods=['POST'])
def log_data_stoploss():
    """Receive and store log data for the stoploss logger."""
    data = request.get_json()
    timestamp = data.get('timestamp')
    current_price = data.get('current_price')
    highest_limit = data.get('highest_limit')
    
    if timestamp and current_price is not None and highest_limit is not None:
        # Store the log with timestamp, current_price, and highest_limit
        logs_stoploss.append({
            'timestamp': timestamp,
            'current_price': current_price,
            'highest_limit': highest_limit
        })
        return jsonify({'status': 'success', 'timestamp': timestamp, 'current_price': current_price, 'highest_limit': highest_limit}), 200
    
    return jsonify({'error': 'Invalid data'}), 400

@app.route('/log_data_details', methods=['POST'])
def log_data_details():
    """Receive and store log data for the second logger."""
    data = request.get_json()
    message = data.get('message')
    
    if message:
        log_id = str(uuid.uuid4())  # Generate a unique ID for this log entry
        logs_details.append({'id': log_id, 'message': message})  # Store the log message with an ID for details
        return jsonify({'status': 'success', 'id': log_id, 'message': message}), 200
    
    return jsonify({'error': 'Invalid message'}), 400

@app.route('/ready', methods=['GET'])
def ready():
    """A route to signal that Flask is ready."""
    return jsonify({"status": "Flask is ready"}), 200

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
