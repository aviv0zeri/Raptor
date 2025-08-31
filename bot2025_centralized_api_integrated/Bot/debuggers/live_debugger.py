#!/usr/bin/env python3
"""
🔍 Live Debugger - Real-time System Diagnostics
Streams output live so you can see what's happening
"""

import os
import sys
import subprocess
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from queue import Queue
import signal

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class LiveDebugger:
    """Live debugger with real-time output streaming"""
    
    def __init__(self):
        self.output_queue = Queue()
        self.running = True
        
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\n🛑 Debugger stopped by user")
        self.running = False
    
    def _stream_output(self, process, prefix=""):
        """Stream output from process in real-time"""
        try:
            while self.running and process.poll() is None:
                # Read stdout
                stdout_line = process.stdout.readline()
                if stdout_line:
                    line = stdout_line.strip()
                    if line:
                        print(f"{prefix}📤 {line}")
                        self.output_queue.put(('stdout', line))
                
                # Read stderr
                stderr_line = process.stderr.readline()
                if stderr_line:
                    line = stderr_line.strip()
                    if line:
                        print(f"{prefix}❌ {line}")
                        self.output_queue.put(('stderr', line))
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
        except Exception as e:
            print(f"❌ Error streaming output: {e}")
    
    def run_bash_script_live(self, script_path: str, timeout: int = 300):
        """Run bash script with live output streaming"""
        try:
            script_path = Path(script_path)
            if not script_path.exists():
                print(f"❌ Script not found: {script_path}")
                return {
                    'success': False,
                    'error': f"Script not found: {script_path}",
                    'output': []
                }
            
            print(f"🚀 Starting live execution: {script_path}")
            print("=" * 60)
            
            # Make executable
            os.chmod(script_path, 0o755)
            
            # Start process
            start_time = time.time()
            process = subprocess.Popen(
                [str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,
                cwd=project_root
            )
            
            # Start output streaming in separate thread
            stream_thread = threading.Thread(
                target=self._stream_output,
                args=(process, ""),
                daemon=True
            )
            stream_thread.start()
            
            # Wait for completion or timeout
            try:
                exit_code = process.wait(timeout=timeout)
                execution_time = time.time() - start_time
                success = exit_code == 0
                
                # Get any remaining output
                remaining_stdout, remaining_stderr = process.communicate()
                
                if remaining_stdout:
                    print(f"📤 {remaining_stdout}")
                if remaining_stderr:
                    print(f"❌ {remaining_stderr}")
                
                print("=" * 60)
                if success:
                    print(f"✅ Script completed successfully in {execution_time:.2f}s")
                else:
                    print(f"❌ Script failed with exit code {exit_code}")
                
                # Collect all output from queue
                output = []
                while not self.output_queue.empty():
                    output.append(self.output_queue.get())
                
                return {
                    'success': success,
                    'script_path': str(script_path),
                    'exit_code': exit_code,
                    'execution_time': execution_time,
                    'output': output,
                    'timestamp': datetime.now().isoformat()
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⏰ Script execution timed out after {timeout} seconds")
                return {
                    'success': False,
                    'error': f"Timeout after {timeout}s",
                    'output': []
                }
                
        except Exception as e:
            print(f"❌ Failed to run script: {e}")
            return {
                'success': False,
                'error': str(e),
                'output': []
            }
    
    def check_system_status(self):
        """Check basic system status"""
        print("🔍 Checking system status...")
        
        # Check if we're in the right directory
        if not (project_root / 'run.py').exists():
            print("❌ Not in project root directory")
            return False
        
        # Check key files
        key_files = [
            '.env',
            'scripts/start_app.sh',
            'Bot/main.py',
            'web/dashboard/package.json'
        ]
        
        missing_files = []
        for file_path in key_files:
            if not (project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
            return False
        
        print("✅ Project structure looks good")
        return True
    
    def run_live_debug(self):
        """Run comprehensive live debug"""
        print("🔍 Live Trading Bot Debugger")
        print("=" * 60)
        print("Press Ctrl+C to stop at any time")
        print()
        
        # Check system status first
        if not self.check_system_status():
            return False
        
        # Run startup script with live output
        startup_script = project_root / 'scripts' / 'start_app.sh'
        
        if startup_script.exists():
            print(f"🎯 Running startup script: {startup_script.name}")
            print()
            
            result = self.run_bash_script_live(str(startup_script))
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = project_root / 'logs' / f'live_debug_report_{timestamp}.json'
            
            os.makedirs(report_path.parent, exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"\n📊 Live debug report saved to: {report_path}")
            
            return result['success']
        else:
            print(f"❌ Startup script not found: {startup_script}")
            return False

def main():
    """Main live debugger function"""
    debugger = LiveDebugger()
    
    try:
        success = debugger.run_live_debug()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n🛑 Debugger stopped by user")
        return 1
    except Exception as e:
        print(f"❌ Live debugger failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
