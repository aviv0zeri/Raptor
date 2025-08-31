#!/usr/bin/env python3
"""
🔍 Background Debugger - Continuous Process Monitoring
Starts processes in background and logs output continuously
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

class BackgroundDebugger:
    """Background debugger for continuous process monitoring"""
    
    def __init__(self):
        self.processes = {}
        self.log_files = {}
        self.running = True
        
        # Handle Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\n🛑 Stopping background processes...")
        self.stop_all_processes()
        self.running = False
    
    def start_background_process(self, name: str, command: list, log_file: str):
        """Start a process in background with continuous logging"""
        try:
            # Create log file
            log_path = project_root / 'logs' / log_file
            os.makedirs(log_path.parent, exist_ok=True)
            
            # Open log file for writing
            log_handle = open(log_path, 'w')
            
            # Write header
            log_handle.write(f"🔍 Background Process Log - {name}\n")
            log_handle.write(f"Started: {datetime.now().isoformat()}\n")
            log_handle.write(f"Command: {' '.join(command)}\n")
            log_handle.write("=" * 60 + "\n\n")
            log_handle.flush()
            
            # Start process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=project_root,
                bufsize=1,
                universal_newlines=True
            )
            
            # Store process info
            self.processes[name] = {
                'process': process,
                'command': command,
                'start_time': datetime.now(),
                'log_handle': log_handle,
                'log_file': str(log_path)
            }
            
            self.log_files[name] = str(log_path)
            
            print(f"🚀 Started {name} (PID: {process.pid})")
            print(f"📝 Logging to: {log_path}")
            
            # Start output monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_process_output,
                args=(name,),
                daemon=True
            )
            monitor_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return False
    
    def _monitor_process_output(self, name: str):
        """Monitor process output and write to log file"""
        try:
            process_info = self.processes[name]
            process = process_info['process']
            log_handle = process_info['log_handle']
            
            while self.running and process.poll() is None:
                # Read stdout
                stdout_line = process.stdout.readline()
                if stdout_line:
                    line = stdout_line.strip()
                    if line:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        log_handle.write(f"[{timestamp}] {line}\n")
                        log_handle.flush()
                
                # Read stderr
                stderr_line = process.stderr.readline()
                if stderr_line:
                    line = stderr_line.strip()
                    if line:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        log_handle.write(f"[{timestamp}] ERROR: {line}\n")
                        log_handle.flush()
                
                time.sleep(0.1)
            
            # Process finished
            if process.poll() is not None:
                log_handle.write(f"\n[{datetime.now().strftime('%H:%M:%S')}] Process finished (exit code: {process.returncode})\n")
                log_handle.flush()
                log_handle.close()
                
                print(f"✅ {name} finished (exit code: {process.returncode})")
            
        except Exception as e:
            print(f"❌ Error monitoring {name}: {e}")
    
    def stop_process(self, name: str):
        """Stop a specific process"""
        if name in self.processes:
            process_info = self.processes[name]
            process = process_info['process']
            log_handle = process_info['log_handle']
            
            print(f"🛑 Stopping {name}...")
            
            # Terminate process
            process.terminate()
            time.sleep(2)
            
            # Force kill if still running
            if process.poll() is None:
                process.kill()
            
            # Close log file
            log_handle.write(f"\n[{datetime.now().strftime('%H:%M:%S')}] Process stopped by user\n")
            log_handle.close()
            
            del self.processes[name]
            print(f"✅ {name} stopped")
    
    def stop_all_processes(self):
        """Stop all running processes"""
        for name in list(self.processes.keys()):
            self.stop_process(name)
    
    def get_process_status(self):
        """Get status of all processes"""
        status = {}
        for name, info in self.processes.items():
            process = info['process']
            status[name] = {
                'pid': process.pid,
                'running': process.poll() is None,
                'exit_code': process.returncode if process.poll() is not None else None,
                'start_time': info['start_time'].isoformat(),
                'log_file': info['log_file']
            }
        return status
    
    def read_log_tail(self, name: str, lines: int = 20):
        """Read last N lines from a process log"""
        if name not in self.log_files:
            return f"Process {name} not found"
        
        try:
            log_file = self.log_files[name]
            with open(log_file, 'r') as f:
                lines_list = f.readlines()
                return ''.join(lines_list[-lines:])
        except Exception as e:
            return f"Error reading log: {e}"

def main():
    """Main background debugger function"""
    debugger = BackgroundDebugger()
    
    print("🔍 Background Trading Bot Debugger")
    print("=" * 50)
    print("Press Ctrl+C to stop all processes")
    print()
    
    # Start the startup script in background
    startup_script = project_root / 'scripts' / 'start_app.sh'
    
    if startup_script.exists():
        # Make executable
        os.chmod(startup_script, 0o755)
        
        # Start in background
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f'background_startup_{timestamp}.log'
        
        success = debugger.start_background_process(
            "startup_script",
            [str(startup_script)],
            log_file
        )
        
        if success:
            print(f"\n🎯 Process started successfully!")
            print(f"📊 You can check the log file to see progress")
            print(f"📝 Log file: logs/{log_file}")
            print(f"\n💡 Use these commands to monitor:")
            print(f"   - Check status: python -c \"from scripts.background_debugger import BackgroundDebugger; d=BackgroundDebugger(); print(d.get_process_status())\"")
            print(f"   - Read log: python -c \"from scripts.background_debugger import BackgroundDebugger; d=BackgroundDebugger(); print(d.read_log_tail('startup_script'))\"")
            
            # Keep running until interrupted
            try:
                while debugger.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            return 0
        else:
            print("❌ Failed to start process")
            return 1
    else:
        print(f"❌ Startup script not found: {startup_script}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
