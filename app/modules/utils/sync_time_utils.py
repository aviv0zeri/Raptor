"""
🕐 Cross-Platform Time Synchronization Utilities
The cosmic timekeeper that works across all operating systems
"""

import os
import sys
import platform
import subprocess
import time
from .log_module import CustomLogger

# Initialize the cosmic logger
logger = CustomLogger("app.log")

class TimeSyncManager:
    """
    🌟 The Grand Time Synchronization Orchestrator
    Handles time synchronization across different operating systems
    """
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_admin = self._check_admin_privileges()
    
    def _check_admin_privileges(self):
        """
        🔐 Check if the script has administrative privileges
        """
        try:
            if self.os_type == "windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def sync_time_windows(self):
        """
        🪟 Synchronize time on Windows systems
        """
        try:
            logger.log('info', "Starting Windows time synchronization...")
            
            # Start Windows Time service
            subprocess.run(['net', 'start', 'w32time'], 
                         capture_output=True, text=True, check=True)
            
            # Query current status
            result = subprocess.run(['w32tm', '/query', '/status'], 
                                  capture_output=True, text=True)
            logger.log('info', f"Time service status: {result.stdout}")
            
            # Resync time
            subprocess.run(['w32tm', '/resync'], 
                         capture_output=True, text=True, check=True)
            
            logger.log('info', "Windows time synchronization completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.log('error', f"Windows time sync failed: {e}")
            return False
        except Exception as e:
            logger.log('error', f"Unexpected error in Windows time sync: {e}")
            return False
    
    def sync_time_linux(self):
        """
        🐧 Synchronize time on Linux systems
        """
        try:
            logger.log('info', "Starting Linux time synchronization...")
            
            # Try systemd-timesyncd first
            if self._check_command('timedatectl'):
                logger.log('info', "Using systemd-timesyncd for time synchronization")
                
                # Enable and start the service
                subprocess.run(['systemctl', 'enable', 'systemd-timesyncd'], 
                             capture_output=True, text=True)
                subprocess.run(['systemctl', 'start', 'systemd-timesyncd'], 
                             capture_output=True, text=True)
                
                # Force sync
                subprocess.run(['timedatectl', 'set-ntp', 'true'], 
                             capture_output=True, text=True, check=True)
                
                logger.log('info', "Linux time synchronization completed using systemd-timesyncd")
                return True
            
            # Try chrony
            elif self._check_command('chronyd'):
                logger.log('info', "Using chrony for time synchronization")
                
                subprocess.run(['systemctl', 'enable', 'chronyd'], 
                             capture_output=True, text=True)
                subprocess.run(['systemctl', 'start', 'chronyd'], 
                             capture_output=True, text=True)
                subprocess.run(['chronyc', '-a', 'makestep'], 
                             capture_output=True, text=True, check=True)
                
                logger.log('info', "Linux time synchronization completed using chrony")
                return True
            
            # Try ntpdate
            elif self._check_command('ntpdate'):
                logger.log('info', "Using ntpdate for time synchronization")
                
                subprocess.run(['ntpdate', '-s', 'pool.ntp.org'], 
                             capture_output=True, text=True, check=True)
                
                logger.log('info', "Linux time synchronization completed using ntpdate")
                return True
            
            else:
                logger.log('error', "No time synchronization service found on Linux")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.log('error', f"Linux time sync failed: {e}")
            return False
        except Exception as e:
            logger.log('error', f"Unexpected error in Linux time sync: {e}")
            return False
    
    def _check_command(self, command):
        """
        🔍 Check if a command is available on the system
        """
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def sync_time(self):
        """
        🌟 Main time synchronization method - works across all platforms
        """
        logger.log('info', f"Starting time synchronization on {self.os_type}")
        
        if not self.is_admin:
            logger.log('warning', "Administrative privileges not detected. Time sync may fail.")
        
        if self.os_type == "windows":
            return self.sync_time_windows()
        elif self.os_type == "linux":
            return self.sync_time_linux()
        else:
            logger.log('error', f"Unsupported operating system: {self.os_type}")
            return False
    
    def get_current_time(self):
        """
        🕐 Get the current system time in a formatted string
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    def get_time_offset(self):
        """
        ⏰ Get the time offset from NTP servers (if available)
        """
        try:
            if self.os_type == "windows":
                result = subprocess.run(['w32tm', '/query', '/status'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse the output to find time offset
                    for line in result.stdout.split('\n'):
                        if 'Time Offset' in line:
                            return line.strip()
            elif self.os_type == "linux":
                if self._check_command('chronyc'):
                    result = subprocess.run(['chronyc', 'tracking'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'System time' in line:
                                return line.strip()
            
            return "Time offset information not available"
            
        except Exception as e:
            logger.log('error', f"Error getting time offset: {e}")
            return "Error retrieving time offset"

# Global time sync manager instance
time_sync_manager = TimeSyncManager()

def sync_system_time():
    """
    🌟 Convenience function to sync system time
    """
    return time_sync_manager.sync_time()

def get_formatted_time():
    """
    🌟 Convenience function to get current formatted time
    """
    return time_sync_manager.get_current_time()

def get_time_sync_status():
    """
    🌟 Get the current time synchronization status
    """
    return {
        'os_type': time_sync_manager.os_type,
        'is_admin': time_sync_manager.is_admin,
        'current_time': time_sync_manager.get_current_time(),
        'time_offset': time_sync_manager.get_time_offset()
    }
