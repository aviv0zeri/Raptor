"""
🎵 Bot Sounds - Legacy Compatibility Layer
=======================================

📁 File: /bot2025_centralized_api_integrated/Sounds/bot_sounds.py
🎯 Purpose: Legacy compatibility layer for sound functions
🔧 Function: Provides backward compatibility for old sound calls

🌟 Features:
- Legacy function compatibility
- Redirects to new cross-platform sounds interface
- Maintains old function signatures
- No winsound dependency

🔄 Migration:
- Old: winsound.Beep() calls
- New: Cross-platform sounds interface
- Backward compatible function names

📋 Dependencies:
- Sounds.sounds_interface (new cross-platform interface)

🔗 Related Files:
- Sounds/sounds_interface.py (main sounds interface)
- Bot/tools/utils/centralized_logger.py (logging)

⚠️  DEPRECATED: Use Sounds.sounds_interface directly for new code
"""

# Import the new sounds interface
from .sounds_interface import (
    play_trade_signal,
    play_order_executed,
    play_order_cancelled,
    play_error_alert,
    play_success_confirmation,
    play_warning_notification,
    play_system_start,
    play_system_stop,
    play_balance_update,
    play_profit_alert,
    play_loss_alert
)

def buy_sound():
    """
    🎵 Play a sound for a BUY action (Legacy function)
    
    This function is maintained for backward compatibility.
    For new code, use: from Sounds.sounds_interface import play_trade_signal
    """
    play_trade_signal({'action': 'buy', 'legacy': True})

def sell_sound():
    """
    🎵 Play a sound for a SELL action (Legacy function)
    
    This function is maintained for backward compatibility.
    For new code, use: from Sounds.sounds_interface import play_trade_signal
    """
    play_trade_signal({'action': 'sell', 'legacy': True})

# Additional legacy functions for completeness
def order_executed_sound():
    """Legacy function for order execution sound"""
    play_order_executed({'legacy': True})

def order_cancelled_sound():
    """Legacy function for order cancellation sound"""
    play_order_cancelled({'legacy': True})

def error_sound():
    """Legacy function for error sound"""
    play_error_alert({'legacy': True})

def success_sound():
    """Legacy function for success sound"""
    play_success_confirmation({'legacy': True})

def warning_sound():
    """Legacy function for warning sound"""
    play_warning_notification({'legacy': True})

def system_start_sound():
    """Legacy function for system start sound"""
    play_system_start({'legacy': True})

def system_stop_sound():
    """Legacy function for system stop sound"""
    play_system_stop({'legacy': True})

# Example usage and testing
if __name__ == "__main__":
    print("🎵 Testing Legacy Bot Sounds")
    print("=" * 40)
    
    print("Playing BUY sound...")
    buy_sound()
    
    import time
    time.sleep(0.5)
    
    print("Playing SELL sound...")
    sell_sound()
    
    time.sleep(0.5)
    
    print("Playing order executed sound...")
    order_executed_sound()
    
    time.sleep(0.5)
    
    print("Playing error sound...")
    error_sound()
    
    print("✅ Legacy sound testing complete!")
    print("💡 For new code, use the Sounds.sounds_interface directly")