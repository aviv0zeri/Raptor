#!/usr/bin/env python3
"""
🔍 Debugger - The Cosmic System Diagnostics Tool
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

def run_bash_script(script_path: str, timeout: int = 300):
    """Run bash script and capture output"""
    try:
        script_path = Path(script_path)
        if not script_path.exists():
            return {
                'success': False,
                'error': f"Script not found: {script_path}",
                'stdout': '',
                'stderr': '',
                'exit_code': -1
            }
        
        print(f"🚀 Running: {script_path}")
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        # Run script
        start_time = time.time()
        process = subprocess.Popen(
            [str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root  # Run from project root
        )
        
        stdout, stderr = process.communicate(timeout=timeout)
        execution_time = time.time() - start_time
        exit_code = process.returncode
        
        success = exit_code == 0
        
        result = {
            'success': success,
            'script_path': str(script_path),
            'stdout': stdout,
            'stderr': stderr,
            'exit_code': exit_code,
            'execution_time': execution_time
        }
        
        if success:
            print(f"✅ Success ({execution_time:.2f}s)")
        else:
            print(f"❌ Failed (exit code: {exit_code})")
            if stderr:
                print(f"Error: {stderr}")
        
        return result
        
    except subprocess.TimeoutExpired:
        process.kill()
        return {
            'success': False,
            'error': f"Timeout after {timeout}s",
            'stdout': '',
            'stderr': '',
            'exit_code': -1
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'stdout': '',
            'stderr': '',
            'exit_code': -1
        }

def main():
    """Main debugger function"""
    print("🔍 Trading Bot Debugger")
    print("=" * 50)
    
    # Run startup script
    startup_script = project_root / 'scripts' / 'start_app.sh'
    
    if startup_script.exists():
        result = run_bash_script(str(startup_script))
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = project_root / 'logs' / f'debug_report_{timestamp}.json'
        
        os.makedirs(report_path.parent, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n📊 Report saved to: {report_path}")
        
        return 0 if result['success'] else 1
    else:
        print(f"❌ Startup script not found: {startup_script}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
