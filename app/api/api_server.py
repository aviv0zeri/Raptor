"""
🌟 Cosmic Trading Bot API Server
Provides REST API endpoints for the React dashboard
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os
import subprocess
import threading
import time
import json
import psutil
from datetime import datetime
from dotenv import load_dotenv
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Load API documentation using the config loader
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modules.utils.config_loader import load_api_routes, validate_signal

def load_api_docs():
    """Load API documentation from data folder"""
    return load_api_routes()

# Index route - Main API page
@app.route('/')
def index():
    """Main API index page"""
    api_docs = load_api_docs()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Raptor Trading Bot API</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }}
            .header {{ color: #4CAF50; }}
            .route {{ background: #333; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .method {{ color: #FF9800; font-weight: bold; }}
            .path {{ color: #2196F3; }}
        </style>
    </head>
    <body>
        <h1 class="header">🚀 Raptor Trading Bot API</h1>
        <p>Welcome to the Raptor Trading Bot API server.</p>
        
        <h2>Available Routes:</h2>
        <div class="route">
            <span class="method">GET</span> <span class="path">/health</span> - Health check
        </div>
        <div class="route">
            <span class="method">GET</span> <span class="path">/api/model/status</span> - Model status
        </div>
        <div class="route">
            <span class="method">POST</span> <span class="path">/api/model/start</span> - Start model
        </div>
        <div class="route">
            <span class="method">POST</span> <span class="path">/api/model/stop</span> - Stop model
        </div>
        <div class="route">
            <span class="method">GET</span> <span class="path">/api/system/status</span> - System status
        </div>
        
        <p><strong>Status:</strong> API Server Running ✅</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </body>
    </html>
    """

# Health check route
@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Check if services are running
        services = {
            "api": "running",
            "webhook": "unknown",
            "model": "stopped",
            "bot": "unknown"
        }
        
        # Check webhook server
        try:
            response = requests.get('http://localhost:5001/api/status', timeout=2)
            if response.status_code == 200:
                services["webhook"] = "running"
        except:
            services["webhook"] = "stopped"
        
        # Check model status
        try:
            response = requests.get('http://127.0.0.1:5051/control/status', timeout=2)
            if response.status_code == 200:
                services["model"] = "running"
        except:
            services["model"] = "stopped"
        
        # Check bot status
        if bot_process and bot_process.poll() is None:
            services["bot"] = "running"
        else:
            services["bot"] = "stopped"
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": services,
            "uptime": "running"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 500

# Global state
bot_process = None
test_stack_process = None
bot_logs = []
system_status = {
    'overall': 'offline',
    'components': {
        'model': {'status': 'offline', 'lastUpdate': None, 'performance': 0},
        'main': {'status': 'offline', 'lastUpdate': None, 'performance': 0},
        'database': {'status': 'offline', 'lastUpdate': None, 'performance': 0},
        'api': {'status': 'offline', 'lastUpdate': None, 'performance': 0},
    },
    'resources': {
        'cpu': 0,
        'memory': 0,
        'disk': 0,
        'network': 0,
    }
}

model_process = None
current_model = {
    'name': None,
    'interval': None,
    'pid': None,
}

def log_message(message, level='info', source='api'):
    """Add message to bot logs"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'id': len(bot_logs) + 1,
        'timestamp': timestamp,
        'level': level,
        'message': message,
        'source': source,
        'details': f'API Server: {message}'
    }
    bot_logs.append(log_entry)
    if len(bot_logs) > 1000:  # Keep only last 1000 logs
        bot_logs.pop(0)

def kill_by_ports(ports):
    try:
        for port in ports:
            try:
                p = subprocess.check_output(['lsof', '-ti', f':{port}']).decode().strip().splitlines()
            except Exception:
                p = []
            for pid in p:
                try:
                    os.kill(int(pid), 9)
                except Exception:
                    pass
    except Exception:
        pass

def kill_test_services():
    """Kill known test services without touching this API server."""
    # Kill by common ports
    kill_by_ports([5001, 5173, 8767])
    # Kill by process names
    try:
        for name in ['webhook_server.py', 'test_model.py', 'test_main.py', 'vite']:
            try:
                subprocess.call(['pkill', '-f', name])
            except Exception:
                pass
    except Exception:
        pass

def get_system_metrics():
    """Get current system metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'disk': disk.percent,
            'network': 0  # Placeholder for network usage
        }
    except Exception as e:
        log_message(f"Error getting system metrics: {e}", 'error')
        return {'cpu': 0, 'memory': 0, 'disk': 0, 'network': 0}

def test_binance_connection():
    """Test Binance API connection"""
    try:
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET_KEY')
        
        if not api_key or not secret_key:
            return False, "API keys not configured"
        
        client = Client(api_key, secret_key)
        
        # Test connection by getting account info
        account = client.get_account()
        return True, "Connection successful"
        
    except BinanceAPIException as e:
        return False, f"Binance API error: {e.message}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def get_binance_balance():
    """Get Binance account balance"""
    try:
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET_KEY')
        
        if not api_key or not secret_key:
            return None
        
        client = Client(api_key, secret_key)
        account = client.get_account()
        
        # Get USDT balance
        usdt_balance = 0
        total_balance_usdt = 0
        
        for balance in account['balances']:
            if balance['asset'] == 'USDT':
                usdt_balance = float(balance['free'])
            elif float(balance['free']) > 0:
                # Convert other assets to USDT (simplified)
                try:
                    ticker = client.get_symbol_ticker(symbol=f"{balance['asset']}USDT")
                    asset_value = float(balance['free']) * float(ticker['price'])
                    total_balance_usdt += asset_value
                except:
                    pass
        
        total_balance_usdt += usdt_balance
        
        return {
            'usdt_balance': usdt_balance,
            'total_balance_usdt': total_balance_usdt,
            'balances': account['balances']
        }
        
    except Exception as e:
        log_message(f"Error getting balance: {e}", 'error')
        return None

@app.route('/api/model/signal', methods=['POST'])
def receive_model_signal():
    """Accept model signal JSON and forward to webhook broadcast."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON provided'}), 400
        
        # Validate signal format using JSON configuration
        signal_data = data.get('data') or data
        if data.get('type') == 'model_signal' and not validate_signal(signal_data):
            return jsonify({'success': False, 'message': 'Invalid signal format'}), 400
        
        # Normalize payload to { type: 'model_signal' or 'model_status', data: {...}, timestamp }
        payload = {
            'type': data.get('type', 'model_signal'),
            'data': signal_data,
            'timestamp': datetime.now().isoformat()
        }
        log_message(f"/api/model/signal received: {payload['data'].get('signal','?')}", 'info')
        print(f"/api/model/signal received → {payload['data']}")
        # Forward to local webhook HTTP endpoint for queueing/broadcast
        try:
            r = requests.post('http://localhost:5001/webhook', json=payload, timeout=2)
            ok = r.status_code == 200
        except Exception:
            ok = False
        return jsonify({'success': ok})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get overall system status"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/connection/test', methods=['POST'])
def test_connection():
    """Test API connections"""
    try:
        data = request.get_json()
        connection_type = data.get('type', 'binance')
        
        if connection_type == 'binance':
            success, message = test_binance_connection()
            log_message(f"Binance connection test: {message}", 'info' if success else 'error')
            
            return jsonify({
                'success': success,
                'message': message,
                'type': connection_type
            })
        
        elif connection_type == 'database':
            # Test database connection
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=os.getenv('DB_PORT', 5432),
                    database=os.getenv('DB_NAME', 'trading_bot'),
                    user=os.getenv('DB_USER', 'postgres'),
                    password=os.getenv('DB_PASSWORD', '')
                )
                conn.close()
                log_message("Database connection test: Success", 'info')
                return jsonify({
                    'success': True,
                    'message': 'Database connection successful',
                    'type': connection_type
                })
            except Exception as e:
                log_message(f"Database connection test: Failed - {e}", 'error')
                return jsonify({
                    'success': False,
                    'message': f'Database connection failed: {str(e)}',
                    'type': connection_type
                })
        
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown connection type: {connection_type}',
                'type': connection_type
            })
            
    except Exception as e:
        log_message(f"Connection test error: {e}", 'error')
        return jsonify({
            'success': False,
            'message': f'Test failed: {str(e)}'
        }), 500

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Get account balance"""
    try:
        balance = get_binance_balance()
        if balance:
            log_message(f"Balance retrieved: {balance['total_balance_usdt']:.2f} USDT", 'info')
            return jsonify(balance)
        else:
            return jsonify({
                'error': 'Failed to get balance',
                'usdt_balance': 0,
                'total_balance_usdt': 0
            }), 400
            
    except Exception as e:
        log_message(f"Balance error: {e}", 'error')
        return jsonify({
            'error': str(e),
            'usdt_balance': 0,
            'total_balance_usdt': 0
        }), 500

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    global bot_process
    
    try:
        if bot_process and bot_process.poll() is None:
            return jsonify({
                'success': False,
                'message': 'Bot is already running'
            })
        
        # Start the bot using run.py
        bot_process = subprocess.Popen(
            ['python', 'run.py', 'parallel'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        log_message("Bot started successfully", 'success')
        
        # Start monitoring thread
        threading.Thread(target=monitor_bot_process, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': 'Bot started successfully',
            'pid': bot_process.pid
        })
        
    except Exception as e:
        log_message(f"Failed to start bot: {e}", 'error')
        return jsonify({
            'success': False,
            'message': f'Failed to start bot: {str(e)}'
        }), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot_process
    
    try:
        if bot_process and bot_process.poll() is None:
            bot_process.terminate()
            bot_process.wait(timeout=10)
            log_message("Bot stopped successfully", 'info')
            return jsonify({
                'success': True,
                'message': 'Bot stopped successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Bot is not running'
            })
            
    except Exception as e:
        log_message(f"Failed to stop bot: {e}", 'error')
        return jsonify({
            'success': False,
            'message': f'Failed to stop bot: {str(e)}'
        }), 500

@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    """Get bot status"""
    global bot_process
    
    if bot_process and bot_process.poll() is None:
        status = 'running'
    else:
        status = 'stopped'
    
    return jsonify({
        'status': status,
        'pid': bot_process.pid if bot_process else None,
        'uptime': get_bot_uptime()
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get bot logs"""
    try:
        # Get logs from file if available
        log_file = 'logs/main.log'
        file_logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()[-100:]  # Last 100 lines
                for i, line in enumerate(lines):
                    if line.strip():
                        file_logs.append({
                            'id': len(bot_logs) + i + 1,
                            'timestamp': datetime.now().isoformat(),
                            'level': 'info',
                            'message': line.strip(),
                            'source': 'main',
                            'details': line.strip()
                        })
        
        # Combine file logs with API logs
        all_logs = bot_logs + file_logs
        all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify(all_logs[:100])  # Return last 100 logs
        
    except Exception as e:
        return jsonify([])

@app.route('/api/system/metrics', methods=['GET'])
def get_system_metrics_api():
    """Get system metrics"""
    try:
        metrics = get_system_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'cpu': 0,
            'memory': 0,
            'disk': 0,
            'network': 0
        }), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status_api():
    """Get detailed system status"""
    try:
        # Update system metrics
        system_status['resources'] = get_system_metrics()
        
        # Update component status based on running processes
        update_component_status()
        
        return jsonify(system_status)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'overall': 'error',
            'components': {},
            'resources': {}
        }), 500

def update_component_status():
    """Update component status based on running processes"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                if 'app/modules/model/main.py' in cmdline or 'Model/main.py' in cmdline:
                    system_status['components']['model']['status'] = 'online'
                    system_status['components']['model']['lastUpdate'] = datetime.now()
                    system_status['components']['model']['performance'] = 85
                
                elif 'app/modules/bot/main.py' in cmdline or 'Bot/ver_1/main.py' in cmdline:
                    system_status['components']['main']['status'] = 'online'
                    system_status['components']['main']['lastUpdate'] = datetime.now()
                    system_status['components']['main']['performance'] = 90
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Check if any components are online
        online_components = sum(1 for comp in system_status['components'].values() 
                              if comp['status'] == 'online')
        
        if online_components > 0:
            system_status['overall'] = 'online'
        else:
            system_status['overall'] = 'offline'
            
    except Exception as e:
        log_message(f"Error updating component status: {e}", 'error')

def monitor_bot_process():
    """Monitor bot process and update logs"""
    global bot_process
    
    while bot_process and bot_process.poll() is None:
        try:
            # Read output from bot process
            output = bot_process.stdout.readline()
            if output:
                log_message(output.strip(), 'info', 'bot')
            
            time.sleep(0.1)
        except Exception as e:
            log_message(f"Error monitoring bot: {e}", 'error')
            break
    
    if bot_process:
        log_message("Bot process ended", 'info')


@app.route('/api/test-stack/start', methods=['POST'])
def start_test_stack():
    """Start webhook, frontend, test model, and test bot together."""
    global test_stack_process
    try:
        if test_stack_process and test_stack_process.poll() is None:
            return jsonify({'success': False, 'message': 'Test stack already running', 'pid': test_stack_process.pid})

        # Ensure a clean slate
        kill_test_services()

        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'run_test_stack.sh'))
        cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        # Start script detached and log to file
        logs_dir = os.path.join(cwd, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        log_file = open(os.path.join(logs_dir, 'test_stack.out'), 'a')
        test_stack_process = subprocess.Popen(
            ['bash', script_path],
            cwd=cwd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

        log_message("Test stack started", 'info')
        return jsonify({'success': True, 'pid': test_stack_process.pid})
    except Exception as e:
        log_message(f"Failed to start test stack: {e}", 'error')
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/test-stack/stop', methods=['POST'])
def stop_test_stack():
    """Stop test stack services using recorded PIDs and free ports."""
    global test_stack_process
    try:
        pids_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'test_stack.pids'))
        killed = []
        if os.path.exists(pids_file):
            with open(pids_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        _, val = line.strip().split('=', 1)
                        try:
                            pid = int(val)
                            try:
                                os.kill(pid, 9)
                                killed.append(pid)
                            except Exception:
                                pass
                        except ValueError:
                            pass

        # Also attempt to kill by common ports and known services
        kill_test_services()

        # Stop wrapper script process
        if test_stack_process and test_stack_process.poll() is None:
            try:
                test_stack_process.terminate()
                test_stack_process.wait(timeout=5)
            except Exception:
                try:
                    test_stack_process.kill()
                except Exception:
                    pass
        test_stack_process = None

        log_message(f"Test stack stopped; killed PIDs: {killed}", 'info')
        return jsonify({'success': True, 'killed': killed})
    except Exception as e:
        log_message(f"Failed to stop test stack: {e}", 'error')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/test-stack/status', methods=['GET'])
def test_stack_status():
    """Report whether the test stack appears to be running based on ports."""
    try:
        def is_listening(port: int) -> bool:
            try:
                out = subprocess.check_output(['lsof', '-ti', f':{port}']).decode().strip()
                return len(out.splitlines()) > 0
            except Exception:
                return False
        status = {
            'webhook': is_listening(5001),
            'frontend': is_listening(5173),
            'websocket': is_listening(8767)
        }
        overall = any(status.values())
        return jsonify({'success': True, 'running': overall, 'ports': status})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/model/start', methods=['POST'])
def start_model():
    global model_process, current_model
    try:
        body = request.get_json(force=True) or {}
        model_name = (body.get('model') or 'real').lower()
        interval = body.get('interval') or '2h'
        if model_process and model_process.poll() is None:
            return jsonify({'success': False, 'message': 'Model already running', 'current': current_model}), 400
        # Map model to script
        if model_name in ['real', 'live', 'zigz', 'zigz model', 'zigz_model']:
            # Start Real model with selected interval
            script = 'app/modules/model/main.py'
            env = os.environ.copy()
            env['MODEL_NAME'] = model_name
            env['MODEL_INTERVAL'] = str(interval)
            # Launch detached
            model_process = subprocess.Popen(['python3', script], env=env, 
                                           stdout=open('logs/model/real.log', 'w'), 
                                           stderr=subprocess.STDOUT)
            current_model = {'name': model_name, 'interval': interval, 'pid': model_process.pid}
            system_status['components']['model']['status'] = 'online'
            return jsonify({'success': True, 'message': 'Real model started building', 'current': current_model})
        elif model_name in ['test', 'random']:
            script = 'app/modules/model/test_model.py'
            env = os.environ.copy()
            env['MODEL_NAME'] = model_name
            env['MODEL_INTERVAL'] = str(interval)
            # Launch detached
            model_process = subprocess.Popen(['python3', script], env=env)
            current_model = {'name': model_name, 'interval': interval, 'pid': model_process.pid}
            system_status['components']['model']['status'] = 'online'
            return jsonify({'success': True, 'pid': model_process.pid, 'current': current_model})
        else:
            return jsonify({'success': False, 'message': f'Unknown model: {model_name}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/model/stop', methods=['POST'])
def stop_model():
    global model_process, current_model
    try:
        # Check if we're stopping a Real model (via control server)
        if current_model and current_model.get('name') in ['real', 'live', 'zigz', 'zigz model', 'zigz_model']:
            try:
                response = requests.post('http://127.0.0.1:5051/control/stop', timeout=5)
                if response.status_code == 200:
                    current_model = {'name': None, 'interval': None, 'pid': None}
                    system_status['components']['model']['status'] = 'offline'
                    return jsonify({'success': True, 'message': 'Real model stopped'})
                else:
                    return jsonify({'success': False, 'message': 'Failed to stop Real model'}), 500
            except requests.exceptions.RequestException:
                return jsonify({'success': False, 'message': 'Real model control server not responding'}), 500
        else:
            # Stop Test model or other processes
            if model_process and model_process.poll() is None:
                model_process.terminate()
                try:
                    model_process.wait(timeout=10)
                except Exception:
                    model_process.kill()
            model_process = None
            current_model = {'name': None, 'interval': None, 'pid': None}
            system_status['components']['model']['status'] = 'offline'
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/model/status', methods=['GET'])
def model_status():
    running = model_process is not None and model_process.poll() is None
    
    # Check Real model readiness via control server (if running)
    real_model_ready = False
    real_model_running = False
    if running and current_model.get('name') in ['real', 'live', 'zigz', 'zigz model', 'zigz_model']:
        try:
            response = requests.get('http://127.0.0.1:5051/control/status', timeout=2)
            if response.status_code == 200:
                data = response.json()
                real_model_ready = data.get('ready', False)
                real_model_running = data.get('running', False)
        except requests.exceptions.RequestException:
            pass
    
    return jsonify({
        'running': running, 
        'current': current_model,
        'real_model_ready': real_model_ready,
        'real_model_running': real_model_running
    })

if __name__ == '__main__':
    log_message("API Server started", 'info')
    print("🌟 Cosmic Trading Bot API Server")
    print("🌐 API available at: http://localhost:5050")
    print("📊 React Dashboard should connect to: http://localhost:5173")
    # Run in production mode to avoid dev server restarts that cause timeouts
    app.run(host='0.0.0.0', port=5050, debug=False, use_reloader=False, threaded=True)
