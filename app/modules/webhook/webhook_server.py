"""
🌟 Webhook Server - The Cosmic Communication Hub
===============================================

📁 File: /bot2025_centralized_api_integrated/webhook/webhook_server.py
🎯 Purpose: Real-time communication server for trading bot system
🔧 Function: Handles HTTP webhooks and WebSocket connections

🌟 Features:
- HTTP webhook endpoints for real-time notifications
- WebSocket server for live data streaming
- CORS support for cross-origin requests
- Event broadcasting to all connected clients
- Connection management and health monitoring
- Thread-safe event queuing and processing

🔄 API Endpoints:
- POST /webhook - Receive webhook notifications
- GET /api/events - Get recent events
- GET /api/status - Get server status
- WebSocket ws://localhost:8765 - Real-time streaming

🔧 Configuration:
- Host: localhost (configurable)
- Port: 5001 (changed from 5000 to avoid AirTunes conflict)
- WebSocket Port: 8765
- CORS: Enabled for localhost:3000, localhost:5173

📋 Dependencies:
- Flask (web framework)
- Flask-CORS (cross-origin support)
- websockets (WebSocket server)
- asyncio (async operations)

🔗 Related Files:
- Bot/ver_1/tools/utils/centralized_logger.py (webhook client)
- scripts/start_app.sh (startup script)
- .env (configuration)

🚨 Port Conflicts:
- Port 5000: Used by Apple AirTunes (avoided)
- Port 5001: Webhook server (current)
- Port 8765: WebSocket server
"""

import os
import json
import asyncio
import websockets
from datetime import datetime
from typing import Dict, Any, List, Set
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time

class WebhookServer:
    """
    🌟 Webhook Server with WebSocket Support
    
    Features:
    - HTTP webhook endpoints
    - WebSocket real-time notifications
    - Event broadcasting
    - Connection management
    """
    
    def __init__(self, host: str = 'localhost', port: int = 5001):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        
        # Configure CORS properly
        CORS(self.app, resources={
            r"/*": {
                "origins": ["http://localhost:3000", "http://localhost:5173", "*"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
            }
        })
        
        # WebSocket connections
        self.websocket_connections: Set[websockets.WebSocketServerProtocol] = set()
        self.websocket_lock = threading.Lock()
        self.websocket_loop = None
        
        # Event queue
        self.event_queue: List[Dict[str, Any]] = []
        self.event_lock = threading.Lock()
        
        # Setup routes
        self._setup_routes()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/webhook', methods=['POST', 'OPTIONS'])
        def webhook_endpoint():
            """Handle incoming webhook notifications"""
            # Handle preflight requests
            if request.method == 'OPTIONS':
                response = jsonify({'status': 'ok'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
                return response
            
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Add timestamp if not present
                if 'timestamp' not in data:
                    data['timestamp'] = datetime.now().isoformat()
                
                # Add to event queue for broadcasting
                with self.event_lock:
                    self.event_queue.append(data)
                
                response = jsonify({'status': 'success', 'message': 'Webhook received'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
                
            except Exception as e:
                response = jsonify({'error': str(e)})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 500
        
        @self.app.route('/api/events', methods=['GET'])
        def get_events():
            """Get recent events"""
            try:
                with self.event_lock:
                    events = self.event_queue.copy()
                    self.event_queue.clear()
                
                response = jsonify({'events': events})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
                
            except Exception as e:
                response = jsonify({'error': str(e)})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 500
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get server status"""
            try:
                with self.websocket_lock:
                    connection_count = len(self.websocket_connections)
                
                response = jsonify({
                    'status': 'running',
                    'timestamp': datetime.now().isoformat(),
                    'websocket_connections': connection_count,
                    'pending_events': len(self.event_queue)
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
                
            except Exception as e:
                response = jsonify({'error': str(e)})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 500
    
    def _start_background_tasks(self):
        """Start background tasks"""
        # Start WebSocket server in background
        self.websocket_thread = threading.Thread(
            target=self._run_websocket_server_sync,
            daemon=True
        )
        self.websocket_thread.start()
        
        # Start event broadcaster in background
        self.broadcast_thread = threading.Thread(
            target=self._broadcast_events,
            daemon=True
        )
        self.broadcast_thread.start()
    
    def _run_websocket_server_sync(self):
        """Run WebSocket server in sync mode to avoid async issues"""
        try:
            print("🔄 Starting WebSocket server...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.websocket_loop = loop
            print("✅ WebSocket event loop created")
            loop.run_until_complete(self._run_websocket_server())
        except Exception as e:
            print(f"❌ WebSocket server error: {e}")
            import traceback
            traceback.print_exc()
    
    async def _websocket_handler(self, websocket, path=None):
        """Handle WebSocket connections"""
        try:
            # Add connection
            with self.websocket_lock:
                self.websocket_connections.add(websocket)
            
            print(f"🌟 WebSocket connected: {websocket.remote_address}")
            
            # Keep connection alive and handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    # Handle incoming messages if needed
                    print(f"📨 WebSocket message: {data}")
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON from WebSocket: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 WebSocket disconnected: {websocket.remote_address}")
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
        finally:
            # Remove connection
            with self.websocket_lock:
                self.websocket_connections.discard(websocket)
    
    async def _run_websocket_server(self):
        """Run WebSocket server"""
        try:
            print(f"🔄 Creating WebSocket server on {self.host}:8767...")
            server = await websockets.serve(self._websocket_handler, self.host, 8767)
            print(f"🌟 WebSocket server started on ws://{self.host}:8767")
            await asyncio.Future()  # Run forever
        except Exception as e:
            print(f"❌ WebSocket server error: {e}")
            import traceback
            traceback.print_exc()
    
    def _broadcast_events(self):
        """Broadcast events to WebSocket connections.
        If there are no active WebSocket connections, keep events in the queue so
        that HTTP polling via /api/events can retrieve them.
        """
        while True:
            try:
                # Check current connections
                with self.websocket_lock:
                    connections = list(self.websocket_connections)

                # Only drain the queue when there are active WS clients
                if connections:
                    with self.event_lock:
                        events = self.event_queue.copy()
                        self.event_queue.clear()
                else:
                    events = []

                # Broadcast to all connections
                for event in events:
                    message = json.dumps(event)
                    for websocket in connections:
                        try:
                            loop = self.websocket_loop
                            if loop and loop.is_running():
                                future = asyncio.run_coroutine_threadsafe(
                                    websocket.send(message), loop
                                )
                                future.result(timeout=1)
                            else:
                                # Fallback: try sending synchronously
                                asyncio.run(websocket.send(message))
                        except Exception as e:
                            print(f"❌ Failed to send to WebSocket: {e}")
                            with self.websocket_lock:
                                self.websocket_connections.discard(websocket)

                time.sleep(0.1)  # Small delay to prevent busy waiting

            except Exception as e:
                print(f"❌ Broadcast error: {e}")
                time.sleep(1)
    
    def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast an event to all connected clients"""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        with self.event_lock:
            self.event_queue.append(event)
    
    def run(self, debug: bool = False):
        """Run the webhook server"""
        print(f"🌟 Starting webhook server on http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug)

# Global webhook server instance
webhook_server = WebhookServer()

def broadcast_trading_event(event_type: str, data: Dict[str, Any]):
    """Broadcast trading event"""
    webhook_server.broadcast_event(event_type, data)

def broadcast_log_event(category: str, level: str, message: str, data: Dict[str, Any] = None):
    """Broadcast log event"""
    webhook_server.broadcast_event('log', {
        'category': category,
        'level': level,
        'message': message,
        'data': data or {}
    })

if __name__ == '__main__':
    # Run without Flask debug/reloader to avoid double-starting background
    # threads and WebSocket bind conflicts on port 8767.
    webhook_server.run(debug=False)
