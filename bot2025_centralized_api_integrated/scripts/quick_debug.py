#!/usr/bin/env python3
"""
🔍 Quick Debugger - Limited Time Execution
Runs scripts for a short time to see what happens
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

def quick_test_script(script_path: str, timeout: int = 30):
    """Run script for a limited time to see what happens"""
    try:
        script_path = Path(script_path)
        if not script_path.exists():
            return {
                'success': False,
                'error': f"Script not found: {script_path}",
                'output': [],
                'partial_output': True
            }
        
        print(f"🚀 Quick test: {script_path.name}")
        print(f"⏱️  Timeout: {timeout} seconds")
        print("=" * 50)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        # Start process
        start_time = time.time()
        process = subprocess.Popen(
            [str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root
        )
        
        output_lines = []
        
        try:
            # Wait for timeout
            stdout, stderr = process.communicate(timeout=timeout)
            execution_time = time.time() - start_time
            
            # Process output
            if stdout:
                output_lines.extend(stdout.split('\n'))
            if stderr:
                output_lines.extend([f"ERROR: {line}" for line in stderr.split('\n') if line])
            
            success = process.returncode == 0
            partial_output = False  # Got full output
            
        except subprocess.TimeoutExpired:
            # Kill process and get partial output
            process.kill()
            stdout, stderr = process.communicate()
            execution_time = time.time() - start_time
            
            if stdout:
                output_lines.extend(stdout.split('\n'))
            if stderr:
                output_lines.extend([f"ERROR: {line}" for line in stderr.split('\n') if line])
            
            success = False
            partial_output = True
        
        # Filter out empty lines
        output_lines = [line for line in output_lines if line.strip()]
        
        result = {
            'success': success,
            'script_path': str(script_path),
            'execution_time': execution_time,
            'timeout': timeout,
            'partial_output': partial_output,
            'output_lines': output_lines,
            'exit_code': process.returncode,
            'timestamp': datetime.now().isoformat()
        }
        
        # Print results
        print(f"⏱️  Execution time: {execution_time:.2f}s")
        print(f"📊 Exit code: {process.returncode}")
        print(f"📝 Output lines: {len(output_lines)}")
        print(f"🔄 Partial output: {partial_output}")
        
        if output_lines:
            print("\n📤 Last 10 lines of output:")
            print("-" * 30)
            for line in output_lines[-10:]:
                print(line)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'output_lines': [],
            'partial_output': False
        }

def main():
    """Main quick debug function"""
    print("🔍 Quick Trading Bot Debugger")
    print("=" * 50)
    
    # Test startup script for 30 seconds
    startup_script = project_root / 'scripts' / 'start_app.sh'
    
    if startup_script.exists():
        result = quick_test_script(str(startup_script), timeout=30)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = project_root / 'logs' / f'quick_debug_{timestamp}.json'
        
        os.makedirs(report_path.parent, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n📊 Quick debug report saved to: {report_path}")
        
        # Analysis
        print("\n🔍 Analysis:")
        if result['partial_output']:
            print("⚠️  Script was still running when timeout occurred")
            print("💡 This suggests the script starts successfully but runs continuously")
        elif result['success']:
            print("✅ Script completed successfully")
        else:
            print("❌ Script failed or encountered errors")
        
        return 0 if result['success'] else 1
    else:
        print(f"❌ Startup script not found: {startup_script}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
