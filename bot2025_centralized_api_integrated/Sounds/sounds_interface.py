"""
🎵 Sounds Interface - The Cosmic Audio Feedback System
==================================================

📁 File: /bot2025_centralized_api_integrated/Sounds/sounds_interface.py
🎯 Purpose: Cross-platform audio feedback system for trading events
🔧 Function: Provides audio notifications for trading events and system alerts

🌟 Features:
- Cross-platform audio support (Windows, macOS, Linux)
- Event-based sound triggers with configurable types
- Thread-safe audio playback
- Volume control and mute functionality
- Integration with centralized logger
- Automatic sound file generation
- Real-time audio feedback

🔄 Supported Sound Types:
- ORDER_EXECUTED: Order execution confirmation
- ORDER_CANCELLED: Order cancellation notification
- ERROR_ALERT: Error and critical issue alerts
- SUCCESS_CONFIRMATION: Success operation feedback
- WARNING_NOTIFICATION: Warning and caution alerts
- TRADE_SIGNAL: Trading signal notifications
- SYSTEM_START: System startup sound
- SYSTEM_STOP: System shutdown sound
- BALANCE_UPDATE: Balance change notifications
- PROFIT_ALERT: Profit achievement alerts
- LOSS_ALERT: Loss threshold alerts

🔧 Platform Support:
- Windows: PowerShell beep commands
- macOS: afplay with system sounds
- Linux: sox audio generation

📋 Dependencies:
- platform (system detection)
- subprocess (audio commands)
- threading (thread-safe playback)
- os (file operations)
- enum (sound type definitions)

🔗 Related Files:
- bot_sounds.py (legacy compatibility)
- Bot/tools/utils/centralized_logger.py (logging integration)
- web/dashboard/src/App.jsx (frontend sounds)

🎵 Audio Configuration:
- Volume: 0.0 to 1.0 (configurable)
- Duration: 0.1 to 2.0 seconds
- Frequency: 150Hz to 1200Hz
- Thread-safe playback
"""

import os
import platform
import subprocess
import threading
from typing import Optional, Dict, Any
from enum import Enum

# Import centralized logger if available
try:
    from Bot.tools.utils.centralized_logger import centralized_logger
except ImportError:
    # Fallback logger if centralized logger not available
    class FallbackLogger:
        def info(self, category, message, data=None):
            print(f"[{category.upper()}] ℹ️ {message}")
        def warning(self, category, message, data=None):
            print(f"[{category.upper()}] ⚠️ {message}")
        def error(self, category, message, data=None):
            print(f"[{category.upper()}] ❌ {message}")
    
    centralized_logger = FallbackLogger()

class SoundType(Enum):
    """Sound types for different events"""
    ORDER_EXECUTED = "order_executed"
    ORDER_CANCELLED = "order_cancelled"
    ERROR_ALERT = "error_alert"
    SUCCESS_CONFIRMATION = "success_confirmation"
    WARNING_NOTIFICATION = "warning_notification"
    TRADE_SIGNAL = "trade_signal"
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    BALANCE_UPDATE = "balance_update"
    PROFIT_ALERT = "profit_alert"
    LOSS_ALERT = "loss_alert"

class SoundsInterface:
    """
    🌟 Sounds Interface - Cross-Platform Audio Feedback System
    
    Features:
    - Cross-platform audio support
    - Event-based sound triggers
    - Configurable sound settings
    - Thread-safe audio playback
    - Integration with centralized logger
    - Automatic sound generation
    """
    
    def __init__(self, enabled: bool = True, volume: float = 0.5):
        self.enabled = enabled
        self.volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
        self.system = platform.system().lower()
        self.sound_threads: Dict[str, threading.Thread] = {}
        
        # Sound configurations (frequency, duration)
        self.sound_configs = {
            SoundType.ORDER_EXECUTED: (800, 0.3),      # High pitch, short
            SoundType.ORDER_CANCELLED: (400, 0.2),     # Low pitch, very short
            SoundType.ERROR_ALERT: (200, 0.5),         # Very low pitch, longer
            SoundType.SUCCESS_CONFIRMATION: (1000, 0.4), # Very high pitch
            SoundType.WARNING_NOTIFICATION: (600, 0.3),  # Medium pitch
            SoundType.TRADE_SIGNAL: (900, 0.2),        # High pitch, short
            SoundType.SYSTEM_START: (500, 1.0),        # Medium pitch, long
            SoundType.SYSTEM_STOP: (300, 0.8),         # Low pitch, long
            SoundType.BALANCE_UPDATE: (700, 0.2),      # Medium-high pitch
            SoundType.PROFIT_ALERT: (1200, 0.3),       # Very high pitch
            SoundType.LOSS_ALERT: (150, 0.6),          # Very low pitch, longer
        }
        
        centralized_logger.info('sounds', '🎵 Sounds interface initialized', {
            'enabled': enabled,
            'volume': volume,
            'system': self.system
        })
    
    def play_sound(self, sound_type: SoundType, data: Dict[str, Any] = None):
        """
        🌟 Play a sound for a specific event
        
        Args:
            sound_type: Type of sound to play
            data: Additional data for logging
        """
        if not self.enabled:
            return
        
        try:
            # Log the sound event
            centralized_logger.info('sounds', f'🎵 Playing sound: {sound_type.value}', data or {})
            
            # Play sound in a separate thread to avoid blocking
            thread = threading.Thread(
                target=self._play_sound_threaded,
                args=(sound_type,),
                daemon=True
            )
            thread.start()
            
            # Store thread reference
            self.sound_threads[sound_type.value] = thread
            
        except Exception as e:
            centralized_logger.error('sounds', f'❌ Error playing sound {sound_type.value}: {e}')
    
    def _play_sound_threaded(self, sound_type: SoundType):
        """Play sound in a separate thread"""
        try:
            frequency, duration = self.sound_configs.get(sound_type, (500, 0.3))
            
            if self.system == "darwin":  # macOS
                self._play_sound_macos(frequency, duration)
            elif self.system == "linux":
                self._play_sound_linux(frequency, duration)
            elif self.system == "windows":
                self._play_sound_windows(frequency, duration)
            else:
                # Fallback for unknown systems
                centralized_logger.warning('sounds', f'Unknown system: {self.system}, using fallback')
                self._play_sound_fallback(frequency, duration)
                
        except Exception as e:
            centralized_logger.error('sounds', f'❌ Error in sound playback: {e}')
    
    def _play_sound_macos(self, frequency: int, duration: float):
        """Play sound on macOS using afplay"""
        try:
            # Use system sound for better compatibility
            cmd = "afplay -n 1 /System/Library/Sounds/Tink.aiff"
            subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        except Exception as e:
            centralized_logger.warning('sounds', f'macOS sound failed: {e}')
    
    def _play_sound_linux(self, frequency: int, duration: float):
        """Play sound on Linux using sox or beep"""
        try:
            # Try sox first
            cmd = f"sox -n -r 44100 -c 1 - synth {duration} sine {frequency} vol {self.volume}"
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            
            if result.returncode != 0:
                # Fallback to beep command
                cmd = f"beep -f {frequency} -l {int(duration * 1000)}"
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                
        except Exception as e:
            centralized_logger.warning('sounds', f'Linux sound failed: {e}')
    
    def _play_sound_windows(self, frequency: int, duration: float):
        """Play sound on Windows using PowerShell"""
        try:
            cmd = f"powershell -Command \"[console]::beep({frequency}, {int(duration * 1000)})\""
            subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        except Exception as e:
            centralized_logger.warning('sounds', f'Windows sound failed: {e}')
    
    def _play_sound_fallback(self, frequency: int, duration: float):
        """Fallback sound method using print statements"""
        try:
            # Print a visual indicator since audio failed
            print(f"🔊 SOUND: {frequency}Hz for {duration}s")
        except Exception as e:
            centralized_logger.warning('sounds', f'Fallback sound failed: {e}')
    
    def set_volume(self, volume: float):
        """Set volume level (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        centralized_logger.info('sounds', f'🔊 Volume set to: {self.volume}')
    
    def enable(self):
        """Enable sound playback"""
        self.enabled = True
        centralized_logger.info('sounds', '🔊 Sounds enabled')
    
    def disable(self):
        """Disable sound playback"""
        self.enabled = False
        centralized_logger.info('sounds', '🔇 Sounds disabled')
    
    def get_status(self) -> Dict[str, Any]:
        """Get sounds interface status"""
        return {
            'enabled': self.enabled,
            'volume': self.volume,
            'system': self.system,
            'active_threads': len([t for t in self.sound_threads.values() if t.is_alive()])
        }

# Global sounds interface instance
sounds_interface = SoundsInterface()

# Convenience functions for easy access
def play_order_executed(order_data: Dict[str, Any] = None):
    """Play sound for order execution"""
    sounds_interface.play_sound(SoundType.ORDER_EXECUTED, order_data)

def play_order_cancelled(order_data: Dict[str, Any] = None):
    """Play sound for order cancellation"""
    sounds_interface.play_sound(SoundType.ORDER_CANCELLED, order_data)

def play_error_alert(error_data: Dict[str, Any] = None):
    """Play sound for error alerts"""
    sounds_interface.play_sound(SoundType.ERROR_ALERT, error_data)

def play_success_confirmation(success_data: Dict[str, Any] = None):
    """Play sound for success confirmations"""
    sounds_interface.play_sound(SoundType.SUCCESS_CONFIRMATION, success_data)

def play_warning_notification(warning_data: Dict[str, Any] = None):
    """Play sound for warning notifications"""
    sounds_interface.play_sound(SoundType.WARNING_NOTIFICATION, warning_data)

def play_trade_signal(signal_data: Dict[str, Any] = None):
    """Play sound for trade signals"""
    sounds_interface.play_sound(SoundType.TRADE_SIGNAL, signal_data)

def play_system_start(start_data: Dict[str, Any] = None):
    """Play sound for system startup"""
    sounds_interface.play_sound(SoundType.SYSTEM_START, start_data)

def play_system_stop(stop_data: Dict[str, Any] = None):
    """Play sound for system shutdown"""
    sounds_interface.play_sound(SoundType.SYSTEM_STOP, stop_data)

def play_balance_update(balance_data: Dict[str, Any] = None):
    """Play sound for balance updates"""
    sounds_interface.play_sound(SoundType.BALANCE_UPDATE, balance_data)

def play_profit_alert(profit_data: Dict[str, Any] = None):
    """Play sound for profit alerts"""
    sounds_interface.play_sound(SoundType.PROFIT_ALERT, profit_data)

def play_loss_alert(loss_data: Dict[str, Any] = None):
    """Play sound for loss alerts"""
    sounds_interface.play_sound(SoundType.LOSS_ALERT, loss_data)

# Legacy compatibility functions
def buy_sound():
    """Legacy function for buy sound (redirects to trade signal)"""
    play_trade_signal({'action': 'buy'})

def sell_sound():
    """Legacy function for sell sound (redirects to trade signal)"""
    play_trade_signal({'action': 'sell'})

if __name__ == "__main__":
    # Test all sounds
    print("🎵 Testing Sounds Interface")
    print("=" * 40)
    
    sounds_interface.enable()
    sounds_interface.set_volume(0.5)
    
    # Test each sound type
    for sound_type in SoundType:
        print(f"Testing: {sound_type.value}")
        sounds_interface.play_sound(sound_type)
        import time
        time.sleep(0.5)  # Wait between sounds
    
    print("✅ Sound testing complete!")
