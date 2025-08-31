#this is a blueprint for checking admin permissions on this program:
#TODO change this to a function with returned values, or maybe prints . use it for a purpose serving the program.

import os
import sys
import ctypes

def is_admin():
    """Check if the script is running with admin privileges."""
    try:
        # Check if the current process is running as Administrator
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False

if __name__ == "__main__":
    if is_admin():
        print("This script is running with Administrator privileges!")
    else:
        print("This script is NOT running with Administrator privileges. Please run as Administrator.")
        sys.exit(1)
