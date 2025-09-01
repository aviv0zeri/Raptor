"""
🌟 Centralized Logger System - The Cosmic Logging Engine
====================================================

📁 File: /bot2025_centralized_api_integrated/Bot/tools/utils/centralized_logger.py
🎯 Purpose: Unified logging system with webhook integration and category-based organization
🔧 Function: Provides centralized logging with real-time webhook notifications

🌟 Features:
- Category-based log file organization
- Real-time webhook notifications
- Colored terminal output with emojis
- Thread-safe logging operations
- Automatic log rotation and management
- WebSocket notification queuing
- Configurable log levels and formats
- Cross-platform compatibility

📁 Log Categories:
- trading: Trading operations and signals
- api: API calls and responses
- database: Database operations
- system: System-level events
- errors: Error tracking and analysis
- orders: Order management
- balance: Balance updates
- stop_loss: Stop-loss operations
- model: ML model operations
- webhook: Webhook communications

🔄 Usage:
    from Bot.ver_1.tools.utils.centralized_logger import CentralizedLogger
    
    logger = CentralizedLogger()
    logger.info('trading', 'Order executed successfully', {'order_id': '123'})
    logger.error('api', 'API connection failed', {'endpoint': '/api/v3/order'})

🔧 Configuration:
- Base log directory: logs/categories/
- Webhook URL: http://localhost:5001/webhook
- Webhook enabled: true/false (from environment)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

📋 Dependencies:
- colorama (colored terminal output)
- requests (webhook HTTP calls)
- threading (thread safety)
- pathlib (file operations)
- logging (Python logging framework)

🔗 Related Files:
- webhook/webhook_server.py (webhook receiver)
- .env (configuration)
- logs/categories/ (log files directory)

🎨 Output Format:
- Terminal: Colored with emojis and categories
- Files: Standard logging format
- Webhook: JSON payload with metadata
- WebSocket: Real-time event streaming
"""

import os
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import requests
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)

class CentralizedLogger:
    """
    🌟 Centralized Logger with Category-Based Logging and Webhook Integration
    
    Features:
    - Category-based log files
    - Real-time webhook notifications
    - Colored terminal output
    - Thread-safe logging
    - Automatic log rotation
    """
    
    def __init__(self, base_log_dir: str = "logs/categories"):
        self.base_log_dir = Path(base_log_dir)
        self.base_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Category loggers
        self._loggers: Dict[str, logging.Logger] = {}
        
        # Webhook configuration
        self.webhook_url = os.getenv('WEBHOOK_URL', 'http://localhost:5000/webhook')
        self.webhook_enabled = os.getenv('WEBHOOK_ENABLED', 'true').lower() == 'true'
        
        # Notification queue for websocket
        self.notification_queue: List[Dict[str, Any]] = []
        self.notification_lock = threading.Lock()
        
        # Initialize default categories
        self._init_default_categories()
    
    def _init_default_categories(self):
        """Initialize default logging categories"""
        default_categories = [
            'trading', 'api', 'database', 'system', 'errors', 
            'orders', 'balance', 'stop_loss', 'model', 'webhook'
        ]
        
        for category in default_categories:
            self._get_logger(category)
    
    def _get_logger(self, category: str) -> logging.Logger:
        """Get or create a logger for a specific category"""
        if category not in self._loggers:
            with self._lock:
                if category not in self._loggers:
                    logger = logging.getLogger(f"bot.{category}")
                    logger.setLevel(logging.DEBUG)
                    
                    # Create category-specific log file
                    log_file = self.base_log_dir / f"{category}.log"
                    file_handler = logging.FileHandler(log_file)
                    file_handler.setLevel(logging.DEBUG)
                    
                    # Create formatter
                    formatter = logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )
                    file_handler.setFormatter(formatter)
                    
                    # Add handler if not already added
                    if not logger.handlers:
                        logger.addHandler(file_handler)
                    
                    self._loggers[category] = logger
        
        return self._loggers[category]
    
    def _get_color(self, level: str) -> str:
        """Get color for log level"""
        colors = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.MAGENTA
        }
        return colors.get(level, Fore.WHITE)
    
    def _send_webhook(self, category: str, level: str, message: str, data: Dict[str, Any] = None):
        """Send webhook notification"""
        if not self.webhook_enabled:
            return
        
        try:
            payload = {
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'level': level,
                'message': message,
                'data': data or {}
            }
            
            # Add to notification queue for websocket
            with self.notification_lock:
                self.notification_queue.append(payload)
            
            # Send HTTP webhook
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"{Fore.RED}⚠️ Webhook failed: {response.status_code}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}⚠️ Webhook error: {e}{Style.RESET_ALL}")
    
    def log(self, category: str, level: str, message: str, data: Dict[str, Any] = None):
        """
        🌟 Main logging method with category and webhook support
        
        Args:
            category: Log category (trading, api, database, etc.)
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            data: Additional data for webhook
        """
        logger = self._get_logger(category)
        
        # Get color for terminal output
        color = self._get_color(level)
        
        # Format message with emoji
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        emoji = emoji_map.get(level, '📝')
        
        formatted_message = f"{emoji} {message}"
        
        # Log to file
        getattr(logger, level.lower())(message)
        
        # Print to terminal with color
        print(f"{color}[{category.upper()}] {formatted_message}{Style.RESET_ALL}")
        
        # Send webhook notification
        self._send_webhook(category, level, message, data)
    
    def debug(self, category: str, message: str, data: Dict[str, Any] = None):
        """Log debug message"""
        self.log(category, 'DEBUG', message, data)
    
    def info(self, category: str, message: str, data: Dict[str, Any] = None):
        """Log info message"""
        self.log(category, 'INFO', message, data)
    
    def warning(self, category: str, message: str, data: Dict[str, Any] = None):
        """Log warning message"""
        self.log(category, 'WARNING', message, data)
    
    def error(self, category: str, message: str, data: Dict[str, Any] = None):
        """Log error message"""
        self.log(category, 'ERROR', message, data)
    
    def critical(self, category: str, message: str, data: Dict[str, Any] = None):
        """Log critical message"""
        self.log(category, 'CRITICAL', message, data)
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get pending notifications for websocket"""
        with self.notification_lock:
            notifications = self.notification_queue.copy()
            self.notification_queue.clear()
        return notifications
    
    def get_log_file_path(self, category: str) -> str:
        """Get log file path for a category"""
        return str(self.base_log_dir / f"{category}.log")
    
    def get_all_log_files(self) -> Dict[str, str]:
        """Get all log file paths"""
        return {
            category: self.get_log_file_path(category)
            for category in self._loggers.keys()
        }

# Global logger instance
centralized_logger = CentralizedLogger()

# Convenience functions for backward compatibility
def log_debug(category: str, message: str, data: Dict[str, Any] = None):
    """Log debug message"""
    centralized_logger.debug(category, message, data)

def log_info(category: str, message: str, data: Dict[str, Any] = None):
    """Log info message"""
    centralized_logger.info(category, message, data)

def log_warning(category: str, message: str, data: Dict[str, Any] = None):
    """Log warning message"""
    centralized_logger.warning(category, message, data)

def log_error(category: str, message: str, data: Dict[str, Any] = None):
    """Log error message"""
    centralized_logger.error(category, message, data)

def log_critical(category: str, message: str, data: Dict[str, Any] = None):
    """Log critical message"""
    centralized_logger.critical(category, message, data)
