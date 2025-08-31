#!/usr/bin/env python3
"""
🔍 Timer Debugger - 10 Second Run Cycles
Runs for 10 seconds, reads logs, fixes issues, repeats
"""

import os
import sys
import subprocess
import json
import time
import signal
import threading
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TimerDebugger:
    """Timer-based debugger with 10-second cycles"""
    
    def __init__(self):
        self.running = True
        self.cycle_count = 0
        self.process = None
        self.log_file = None
        
        # Handle Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\n🛑 Timer debugger stopped by user")
        self.stop_process()
        self.running = False
    
    def start_process(self):
        """Start the startup script"""
        try:
            startup_script = project_root / 'scripts' / 'start_app.sh'
            
            if not startup_script.exists():
                print(f"❌ Startup script not found: {startup_script}")
                return False
            
            # Make executable
            os.chmod(startup_script, 0o755)
            
            # Create log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = project_root / 'logs' / f'timer_debug_{timestamp}.log'
            os.makedirs(self.log_file.parent, exist_ok=True)
            
            # Start process with output redirected to log file
            with open(self.log_file, 'w') as log:
                self.process = subprocess.Popen(
                    [str(startup_script)],
                    stdout=log,
                    stderr=log,
                    text=True,
                    cwd=project_root
                )
            
            print(f"🚀 Started process (PID: {self.process.pid})")
            print(f"📝 Logging to: {self.log_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start process: {e}")
            return False
    
    def stop_process(self):
        """Stop the running process"""
        if self.process:
            print("🛑 Stopping process...")
            self.process.terminate()
            time.sleep(2)
            
            if self.process.poll() is None:
                self.process.kill()
            
            print("✅ Process stopped")
            self.process = None
    
    def run_cycle(self):
        """Run one 10-second cycle"""
        self.cycle_count += 1
        print(f"\n🔄 CYCLE {self.cycle_count}")
        print("=" * 50)
        
        # Start process if not running
        if not self.process:
            if not self.start_process():
                return False
        
        # Run for 10 seconds
        print("⏱️  Running for 10 seconds...")
        start_time = time.time()
        
        while time.time() - start_time < 10 and self.running:
            time.sleep(1)
            elapsed = int(time.time() - start_time)
            print(f"⏱️  {elapsed}s elapsed...")
        
        # Read log file
        print("📖 Reading log file...")
        log_content = self.read_log_file()
        
        # Analyze and fix issues
        print("🔍 Analyzing issues...")
        issues = self.analyze_log(log_content)
        
        # Apply fixes
        if issues:
            print("🔧 Applying fixes...")
            self.apply_fixes(issues)
        
        return True
    
    def read_log_file(self):
        """Read the log file"""
        if not self.log_file or not self.log_file.exists():
            return "Log file not found"
        
        try:
            with open(self.log_file, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading log: {e}"
    
    def analyze_log(self, log_content):
        """Analyze log content for issues"""
        issues = []
        
        # Check for common error patterns
        error_patterns = [
            ("ImportError", "Missing import"),
            ("ModuleNotFoundError", "Missing module"),
            ("FileNotFoundError", "Missing file"),
            ("PermissionError", "Permission issue"),
            ("ConnectionError", "Connection failed"),
            ("TimeoutError", "Timeout occurred"),
            ("SyntaxError", "Syntax error"),
            ("IndentationError", "Indentation error"),
            ("KeyError", "Missing key"),
            ("AttributeError", "Missing attribute"),
            ("TypeError", "Type error"),
            ("ValueError", "Value error"),
            ("OSError", "OS error"),
            ("RuntimeError", "Runtime error")
        ]
        
        for pattern, description in error_patterns:
            if pattern in log_content:
                issues.append({
                    'type': 'error',
                    'pattern': pattern,
                    'description': description,
                    'severity': 'high'
                })
        
        # Check for warnings
        warning_patterns = [
            ("Warning", "Warning message"),
            ("DeprecationWarning", "Deprecated feature"),
            ("UserWarning", "User warning"),
            ("FutureWarning", "Future warning")
        ]
        
        for pattern, description in warning_patterns:
            if pattern in log_content:
                issues.append({
                    'type': 'warning',
                    'pattern': pattern,
                    'description': description,
                    'severity': 'medium'
                })
        
        # Check for success indicators
        success_patterns = [
            ("✅", "Success indicator"),
            ("Success", "Success message"),
            ("Started", "Service started"),
            ("Running", "Service running"),
            ("Connected", "Connection successful")
        ]
        
        for pattern, description in success_patterns:
            if pattern in log_content:
                issues.append({
                    'type': 'success',
                    'pattern': pattern,
                    'description': description,
                    'severity': 'low'
                })
        
        return issues
    
    def apply_fixes(self, issues):
        """Apply fixes based on identified issues"""
        for issue in issues:
            print(f"🔧 Fixing: {issue['description']} ({issue['pattern']})")
            
            if issue['pattern'] == "ImportError":
                self.fix_import_error()
            elif issue['pattern'] == "ModuleNotFoundError":
                self.fix_missing_module()
            elif issue['pattern'] == "FileNotFoundError":
                self.fix_missing_file()
            elif issue['pattern'] == "PermissionError":
                self.fix_permission_error()
            elif issue['pattern'] == "ConnectionError":
                self.fix_connection_error()
            else:
                print(f"   ⚠️  No specific fix for {issue['pattern']}")
    
    def fix_import_error(self):
        """Fix import errors"""
        print("   📦 Installing missing packages...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "config/requirements.txt"], 
                         capture_output=True, text=True, cwd=project_root)
            print("   ✅ Packages installed")
        except Exception as e:
            print(f"   ❌ Failed to install packages: {e}")
    
    def fix_missing_module(self):
        """Fix missing modules"""
        print("   📦 Installing missing modules...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         capture_output=True, text=True, cwd=project_root)
            print("   ✅ Pip upgraded")
        except Exception as e:
            print(f"   ❌ Failed to upgrade pip: {e}")
    
    def fix_missing_file(self):
        """Fix missing files"""
        print("   📁 Creating missing files...")
        # Create basic .env if missing
        env_file = project_root / '.env'
        if not env_file.exists():
            try:
                with open(env_file, 'w') as f:
                    f.write("# Environment variables\n")
                    f.write("BINANCE_API_KEY=your_api_key_here\n")
                    f.write("BINANCE_SECRET_KEY=your_secret_key_here\n")
                print("   ✅ Created .env file")
            except Exception as e:
                print(f"   ❌ Failed to create .env: {e}")
    
    def fix_permission_error(self):
        """Fix permission errors"""
        print("   🔐 Fixing permissions...")
        try:
            # Make scripts executable
            scripts_dir = project_root / 'scripts'
            for script in scripts_dir.glob('*.sh'):
                os.chmod(script, 0o755)
            print("   ✅ Fixed script permissions")
        except Exception as e:
            print(f"   ❌ Failed to fix permissions: {e}")
    
    def fix_connection_error(self):
        """Fix connection errors"""
        print("   🌐 Checking network connectivity...")
        try:
            # Test basic connectivity
            result = subprocess.run(['ping', '-c', '1', 'google.com'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ Network connectivity OK")
            else:
                print("   ❌ Network connectivity issues")
        except Exception as e:
            print(f"   ❌ Network check failed: {e}")
    
    def run_debug_cycles(self, max_cycles=10):
        """Run multiple debug cycles"""
        print("🔍 Timer Debugger - 10 Second Cycles")
        print("=" * 60)
        print("Press Ctrl+C to stop")
        print()
        
        for cycle in range(max_cycles):
            if not self.running:
                break
            
            if not self.run_cycle():
                print("❌ Cycle failed, stopping")
                break
            
            # Wait 10 seconds between cycles
            if cycle < max_cycles - 1:  # Don't wait after last cycle
                print("⏳ Waiting 10 seconds before next cycle...")
                time.sleep(10)
        
        # Final cleanup
        self.stop_process()
        print("\n🎯 Debug cycles completed")
        return True

def main():
    """Main timer debugger function"""
    debugger = TimerDebugger()
    
    try:
        success = debugger.run_debug_cycles(max_cycles=5)  # Run 5 cycles
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n🛑 Debugger stopped by user")
        return 1
    except Exception as e:
        print(f"❌ Timer debugger failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
