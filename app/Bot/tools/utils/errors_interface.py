"""
🚨 Errors Interface - The Cosmic Error Management System
Comprehensive error handling for all bot components
"""

import os
import sys
import traceback
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass, asdict

from .centralized_logger import centralized_logger
from .sounds_interface import play_error_alert, play_warning_notification

class ErrorSeverity(Enum):
    """Error severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorCategory(Enum):
    """Error categories"""
    API = "API"
    DATABASE = "DATABASE"
    TRADING = "TRADING"
    NETWORK = "NETWORK"
    CONFIGURATION = "CONFIGURATION"
    AUTHENTICATION = "AUTHENTICATION"
    VALIDATION = "VALIDATION"
    SYSTEM = "SYSTEM"
    SOUNDS = "SOUNDS"
    LOGGING = "LOGGING"
    WEBHOOK = "WEBHOOK"
    WEBSOCKET = "WEBSOCKET"
    FRONTEND = "FRONTEND"
    SCRIPT = "SCRIPT"

@dataclass
class ErrorInfo:
    """Error information structure"""
    timestamp: str
    category: str
    severity: str
    message: str
    details: Dict[str, Any]
    stack_trace: str
    component: str
    user_action: Optional[str] = None
    resolved: bool = False
    resolution_time: Optional[str] = None

class ErrorsInterface:
    """
    🌟 Errors Interface - Comprehensive Error Management
    
    Features:
    - Centralized error handling
    - Error categorization and severity levels
    - Automatic error logging and notification
    - Error resolution tracking
    - Integration with sounds and logging
    - Error statistics and reporting
    """
    
    def __init__(self):
        self.errors: List[ErrorInfo] = []
        self.error_stats: Dict[str, int] = {}
        self.resolution_actions: Dict[str, str] = {}
        self.auto_resolve_patterns: Dict[str, str] = {}
        
        # Initialize error patterns
        self._init_error_patterns()
        
        # Initialize resolution actions
        self._init_resolution_actions()
        
        centralized_logger.info('errors', '🚨 Errors interface initialized')
    
    def _init_error_patterns(self):
        """Initialize common error patterns for auto-resolution"""
        self.auto_resolve_patterns = {
            # API Errors
            "API_KEY_INVALID": "Check API key configuration in .env file",
            "RATE_LIMIT_EXCEEDED": "Wait for rate limit reset or reduce request frequency",
            "NETWORK_TIMEOUT": "Check internet connection and retry",
            "INVALID_SYMBOL": "Verify trading pair symbol format",
            "INSUFFICIENT_BALANCE": "Check account balance and reduce order size",
            
            # Database Errors
            "CONNECTION_REFUSED": "Check PostgreSQL service status",
            "AUTHENTICATION_FAILED": "Verify database credentials in .env",
            "TABLE_NOT_FOUND": "Run database initialization script",
            "DUPLICATE_KEY": "Handle duplicate entry gracefully",
            
            # Trading Errors
            "ORDER_REJECTED": "Check order parameters and market conditions",
            "PRICE_FILTER": "Adjust price to meet exchange requirements",
            "LOT_SIZE": "Adjust quantity to meet minimum/maximum requirements",
            "NOTIONAL": "Increase order value to meet minimum notional",
            
            # System Errors
            "PERMISSION_DENIED": "Check file permissions and user access",
            "DISK_SPACE_FULL": "Free up disk space",
            "MEMORY_ERROR": "Restart application or increase system resources",
            
            # Configuration Errors
            "MISSING_ENV_VAR": "Add required environment variable to .env",
            "INVALID_CONFIG": "Check configuration file format",
            "PORT_IN_USE": "Change port or stop conflicting service",
        }
    
    def _init_resolution_actions(self):
        """Initialize resolution actions for different error types"""
        self.resolution_actions = {
            ErrorCategory.API: [
                "Check API key validity",
                "Verify API permissions",
                "Check rate limits",
                "Validate request parameters",
                "Test API connectivity"
            ],
            ErrorCategory.DATABASE: [
                "Check database service status",
                "Verify connection credentials",
                "Run database migrations",
                "Check disk space",
                "Restart database service"
            ],
            ErrorCategory.TRADING: [
                "Validate order parameters",
                "Check account balance",
                "Verify trading pair",
                "Check market status",
                "Review trading rules"
            ],
            ErrorCategory.NETWORK: [
                "Check internet connection",
                "Verify firewall settings",
                "Test DNS resolution",
                "Check proxy configuration",
                "Restart network service"
            ],
            ErrorCategory.CONFIGURATION: [
                "Review .env file",
                "Check configuration syntax",
                "Verify file permissions",
                "Validate environment variables",
                "Restart application"
            ],
            ErrorCategory.AUTHENTICATION: [
                "Verify API keys",
                "Check authentication tokens",
                "Validate credentials",
                "Refresh authentication",
                "Contact support"
            ],
            ErrorCategory.VALIDATION: [
                "Check input parameters",
                "Validate data format",
                "Review business rules",
                "Test edge cases",
                "Update validation logic"
            ],
            ErrorCategory.SYSTEM: [
                "Check system resources",
                "Review system logs",
                "Restart services",
                "Update system packages",
                "Contact system administrator"
            ],
            ErrorCategory.SOUNDS: [
                "Check audio system",
                "Verify sound permissions",
                "Test audio drivers",
                "Restart audio service",
                "Check volume settings"
            ],
            ErrorCategory.LOGGING: [
                "Check log file permissions",
                "Verify log directory",
                "Review log configuration",
                "Clear old log files",
                "Restart logging service"
            ],
            ErrorCategory.WEBHOOK: [
                "Check webhook URL",
                "Verify webhook authentication",
                "Test webhook connectivity",
                "Review webhook payload",
                "Check webhook rate limits"
            ],
            ErrorCategory.WEBSOCKET: [
                "Check WebSocket connection",
                "Verify WebSocket URL",
                "Test WebSocket authentication",
                "Review WebSocket events",
                "Restart WebSocket service"
            ],
            ErrorCategory.FRONTEND: [
                "Check browser console",
                "Verify API endpoints",
                "Test frontend connectivity",
                "Review JavaScript errors",
                "Clear browser cache"
            ],
            ErrorCategory.SCRIPT: [
                "Check script permissions",
                "Verify script syntax",
                "Test script execution",
                "Review script dependencies",
                "Update script version"
            ]
        }
    
    def log_error(self, category: ErrorCategory, severity: ErrorSeverity, message: str, 
                  details: Dict[str, Any] = None, component: str = "unknown", 
                  user_action: str = None, auto_resolve: bool = False):
        """
        🌟 Log an error with comprehensive information
        
        Args:
            category: Error category
            severity: Error severity level
            message: Error message
            details: Additional error details
            component: Component where error occurred
            user_action: Suggested user action
            auto_resolve: Whether to attempt auto-resolution
        """
        try:
            # Get stack trace
            stack_trace = traceback.format_exc()
            
            # Create error info
            error_info = ErrorInfo(
                timestamp=datetime.now().isoformat(),
                category=category.value,
                severity=severity.value,
                message=message,
                details=details or {},
                stack_trace=stack_trace,
                component=component,
                user_action=user_action
            )
            
            # Add to errors list
            self.errors.append(error_info)
            
            # Update statistics
            self._update_error_stats(category, severity)
            
            # Log to centralized logger
            log_message = f"🚨 {category.value} ERROR: {message}"
            if details:
                log_message += f" | Details: {json.dumps(details)}"
            
            if severity == ErrorSeverity.CRITICAL:
                centralized_logger.critical('errors', log_message, details)
                # Play critical error sound
                play_error_alert({'error_type': 'critical', 'category': category.value})
            elif severity == ErrorSeverity.ERROR:
                centralized_logger.error('errors', log_message, details)
                # Play error sound
                play_error_alert({'error_type': 'error', 'category': category.value})
            elif severity == ErrorSeverity.WARNING:
                centralized_logger.warning('errors', log_message, details)
                # Play warning sound
                play_warning_notification({'warning_type': 'error', 'category': category.value})
            else:
                centralized_logger.info('errors', log_message, details)
            
            # Attempt auto-resolution
            if auto_resolve:
                self._attempt_auto_resolution(error_info)
            
            # Check for error patterns
            self._check_error_patterns(error_info)
            
        except Exception as e:
            # Fallback logging if error interface fails
            print(f"❌ Error in error logging: {e}")
    
    def _update_error_stats(self, category: ErrorCategory, severity: ErrorSeverity):
        """Update error statistics"""
        category_key = f"{category.value}_{severity.value}"
        self.error_stats[category_key] = self.error_stats.get(category_key, 0) + 1
    
    def _attempt_auto_resolution(self, error_info: ErrorInfo):
        """Attempt to auto-resolve common errors"""
        try:
            # Check for known patterns
            for pattern, resolution in self.auto_resolve_patterns.items():
                if pattern.lower() in error_info.message.lower():
                    centralized_logger.info('errors', f"🔄 Auto-resolution attempted: {resolution}")
                    error_info.user_action = resolution
                    break
        except Exception as e:
            centralized_logger.warning('errors', f"Auto-resolution failed: {e}")
    
    def _check_error_patterns(self, error_info: ErrorInfo):
        """Check for error patterns and suggest actions"""
        try:
            # Check for repeated errors
            recent_errors = [e for e in self.errors[-10:] if e.category == error_info.category]
            if len(recent_errors) >= 3:
                centralized_logger.warning('errors', f"⚠️ Multiple {error_info.category} errors detected")
                play_warning_notification({'warning_type': 'repeated_errors', 'category': error_info.category})
        except Exception as e:
            centralized_logger.warning('errors', f"Error pattern check failed: {e}")
    
    def resolve_error(self, error_index: int, resolution: str = None):
        """Mark an error as resolved"""
        try:
            if 0 <= error_index < len(self.errors):
                error = self.errors[error_index]
                error.resolved = True
                error.resolution_time = datetime.now().isoformat()
                if resolution:
                    error.user_action = resolution
                
                centralized_logger.info('errors', f"✅ Error resolved: {error.message}")
        except Exception as e:
            centralized_logger.error('errors', f"Error resolution failed: {e}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        try:
            total_errors = len(self.errors)
            resolved_errors = len([e for e in self.errors if e.resolved])
            critical_errors = len([e for e in self.errors if e.severity == ErrorSeverity.CRITICAL.value])
            
            category_summary = {}
            for error in self.errors:
                category = error.category
                if category not in category_summary:
                    category_summary[category] = {'total': 0, 'resolved': 0, 'critical': 0}
                
                category_summary[category]['total'] += 1
                if error.resolved:
                    category_summary[category]['resolved'] += 1
                if error.severity == ErrorSeverity.CRITICAL.value:
                    category_summary[category]['critical'] += 1
            
            return {
                'total_errors': total_errors,
                'resolved_errors': resolved_errors,
                'unresolved_errors': total_errors - resolved_errors,
                'critical_errors': critical_errors,
                'resolution_rate': (resolved_errors / total_errors * 100) if total_errors > 0 else 0,
                'category_summary': category_summary,
                'error_stats': self.error_stats
            }
        except Exception as e:
            centralized_logger.error('errors', f"Error summary generation failed: {e}")
            return {}
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors"""
        try:
            recent_errors = self.errors[-limit:] if self.errors else []
            return [asdict(error) for error in recent_errors]
        except Exception as e:
            centralized_logger.error('errors', f"Recent errors retrieval failed: {e}")
            return []
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[Dict[str, Any]]:
        """Get errors by category"""
        try:
            category_errors = [e for e in self.errors if e.category == category.value]
            return [asdict(error) for error in category_errors]
        except Exception as e:
            centralized_logger.error('errors', f"Category errors retrieval failed: {e}")
            return []
    
    def get_critical_errors(self) -> List[Dict[str, Any]]:
        """Get critical errors"""
        try:
            critical_errors = [e for e in self.errors if e.severity == ErrorSeverity.CRITICAL.value]
            return [asdict(error) for error in critical_errors]
        except Exception as e:
            centralized_logger.error('errors', f"Critical errors retrieval failed: {e}")
            return []
    
    def clear_resolved_errors(self):
        """Clear resolved errors from memory"""
        try:
            original_count = len(self.errors)
            self.errors = [e for e in self.errors if not e.resolved]
            cleared_count = original_count - len(self.errors)
            
            if cleared_count > 0:
                centralized_logger.info('errors', f"🧹 Cleared {cleared_count} resolved errors")
        except Exception as e:
            centralized_logger.error('errors', f"Error clearing failed: {e}")
    
    def export_errors_report(self, filepath: str = None) -> str:
        """Export errors report to file"""
        try:
            if not filepath:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"logs/errors_report_{timestamp}.json"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'summary': self.get_error_summary(),
                'recent_errors': self.get_recent_errors(50),
                'critical_errors': self.get_critical_errors(),
                'error_stats': self.error_stats
            }
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            centralized_logger.info('errors', f"📊 Errors report exported to {filepath}")
            return filepath
        except Exception as e:
            centralized_logger.error('errors', f"Error report export failed: {e}")
            return None

# Global errors interface instance
errors_interface = ErrorsInterface()

# Convenience functions for different error categories
def log_api_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log API-related error"""
    errors_interface.log_error(ErrorCategory.API, severity, message, details, "api")

def log_database_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log database-related error"""
    errors_interface.log_error(ErrorCategory.DATABASE, severity, message, details, "database")

def log_trading_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log trading-related error"""
    errors_interface.log_error(ErrorCategory.TRADING, severity, message, details, "trading")

def log_network_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log network-related error"""
    errors_interface.log_error(ErrorCategory.NETWORK, severity, message, details, "network")

def log_config_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log configuration-related error"""
    errors_interface.log_error(ErrorCategory.CONFIGURATION, severity, message, details, "config")

def log_auth_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log authentication-related error"""
    errors_interface.log_error(ErrorCategory.AUTHENTICATION, severity, message, details, "auth")

def log_validation_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log validation-related error"""
    errors_interface.log_error(ErrorCategory.VALIDATION, severity, message, details, "validation")

def log_system_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log system-related error"""
    errors_interface.log_error(ErrorCategory.SYSTEM, severity, message, details, "system")

def log_sounds_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log sounds-related error"""
    errors_interface.log_error(ErrorCategory.SOUNDS, severity, message, details, "sounds")

def log_logging_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log logging-related error"""
    errors_interface.log_error(ErrorCategory.LOGGING, severity, message, details, "logging")

def log_webhook_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log webhook-related error"""
    errors_interface.log_error(ErrorCategory.WEBHOOK, severity, message, details, "webhook")

def log_websocket_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log WebSocket-related error"""
    errors_interface.log_error(ErrorCategory.WEBSOCKET, severity, message, details, "websocket")

def log_frontend_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log frontend-related error"""
    errors_interface.log_error(ErrorCategory.FRONTEND, severity, message, details, "frontend")

def log_script_error(message: str, details: Dict[str, Any] = None, severity: ErrorSeverity = ErrorSeverity.ERROR):
    """Log script-related error"""
    errors_interface.log_error(ErrorCategory.SCRIPT, severity, message, details, "script")
