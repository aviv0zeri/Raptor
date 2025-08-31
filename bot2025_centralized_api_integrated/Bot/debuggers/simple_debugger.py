#!/usr/bin/env python3
"""
🔍 Simple Debugger - File-based Output Capture
Writes output to a file that can be read by AI tools
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_script_with_logging(script_path: str, log_file: str, timeout: int = 300):
    """Run script and log all output to file"""
    try:
        script_path = Path(script_path)
        if not script_path.exists():
            return {
                'success': False,
                'error': f"Script not found: {script_path}",
                'log_file': log_file
            }
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        # Create log file
        log_path = project_root / 'logs' / log_file
        os.makedirs(log_path.parent, exist_ok=True)
        
        # Start process with output redirected to log file
        start_time = time.time()
        
        with open(log_path, 'w') as log:
            # Write header
            log.write(f"🔍 Debug Log - {datetime.now().isoformat()}\n")
            log.write(f"Script: {script_path}\n")
            log.write("=" * 60 + "\n\n")
            log.flush()
            
            # Run the script
            process = subprocess.Popen(
                [str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=project_root
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                execution_time = time.time() - start_time
                exit_code = process.returncode
                
                # Write output to log
                if stdout:
                    log.write("📤 STDOUT:\n")
                    log.write(stdout)
                    log.write("\n")
                
                if stderr:
                    log.write("❌ STDERR:\n")
                    log.write(stderr)
                    log.write("\n")
                
                # Write summary
                log.write("=" * 60 + "\n")
                log.write(f"Exit Code: {exit_code}\n")
                log.write(f"Execution Time: {execution_time:.2f}s\n")
                log.write(f"Success: {exit_code == 0}\n")
                log.write(f"Completed: {datetime.now().isoformat()}\n")
                
                success = exit_code == 0
                
                return {
                    'success': success,
                    'script_path': str(script_path),
                    'log_file': str(log_path),
                    'exit_code': exit_code,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                log.write(f"⏰ TIMEOUT after {timeout} seconds\n")
                return {
                    'success': False,
                    'error': f"Timeout after {timeout}s",
                    'log_file': str(log_path)
                }
                
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'log_file': log_file
        }

def main():
    """Main debugger function"""
    print("🔍 Simple Trading Bot Debugger")
    print("=" * 50)
    
    # Generate log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f'debug_output_{timestamp}.log'
    
    # Run startup script
    startup_script = project_root / 'scripts' / 'start_app.sh'
    
    if startup_script.exists():
        print(f"🚀 Running: {startup_script.name}")
        print(f"📝 Output will be logged to: logs/{log_file}")
        print("⏳ Please wait...")
        
        result = run_script_with_logging(str(startup_script), log_file)
        
        # Save results summary
        summary_file = project_root / 'logs' / f'debug_summary_{timestamp}.json'
        with open(summary_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n📊 Results:")
        print(f"   Success: {result['success']}")
        print(f"   Log File: {result['log_file']}")
        print(f"   Summary: {summary_file}")
        
        return 0 if result['success'] else 1
    else:
        print(f"❌ Startup script not found: {startup_script}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
