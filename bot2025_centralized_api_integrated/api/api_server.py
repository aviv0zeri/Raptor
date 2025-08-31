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

# Global state
bot_process = None
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
                
                if 'Model/main.py' in cmdline:
                    system_status['components']['model']['status'] = 'online'
                    system_status['components']['model']['lastUpdate'] = datetime.now()
                    system_status['components']['model']['performance'] = 85
                
                elif 'Bot/ver_1/main.py' in cmdline:
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

if __name__ == '__main__':
    log_message("API Server started", 'info')
    print("🌟 Cosmic Trading Bot API Server")
    print("🌐 API available at: http://localhost:5000")
    print("📊 React Dashboard should connect to: http://localhost:5173")
    app.run(host='0.0.0.0', port=5000, debug=True)
