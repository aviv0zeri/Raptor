"""
🔍 Enhanced Debugger - The Cosmic System Analyzer
==============================================

📁 File: /bot2025_centralized_api_integrated/scripts/enhanced_debugger.py
🎯 Purpose: Comprehensive 10-second system analysis and error detection
🔧 Function: Runs trading bot system and analyzes logs for issues

🌟 Features:
- 10-second precise timing analysis
- Comprehensive error pattern detection
- Warning and success indicator analysis
- Performance metrics collection
- Automatic log file generation
- JSON report creation with detailed analysis
- Real-time progress monitoring
- Graceful cleanup and process management

🔍 Analysis Capabilities:
- Webhook connectivity testing
- SSL/TLS warning detection
- Runtime warning identification
- Import and module error detection
- Database connection validation
- Service startup verification
- Performance benchmarking

📊 Output Files:
- logs/enhanced_debug_YYYYMMDD_HHMMSS.log - Raw debug log
- logs/enhanced_debug_report_YYYYMMDD_HHMMSS.json - Detailed JSON report

🔄 Usage:
    python scripts/enhanced_debugger.py
    ./run_debugger.sh (recommended)

📋 Dependencies:
- subprocess (process management)
- json (report generation)
- time (timing control)
- signal (interrupt handling)
- threading (background operations)
- pathlib (file operations)
- re (pattern matching)

🔗 Related Files:
- run_debugger.sh (bash wrapper)
- scripts/start_app.sh (system startup)
- webhook/webhook_server.py (webhook testing)
- logs/ (output directory)

🎯 Error Patterns Detected:
- Webhook HTTP errors (403, 500, etc.)
- SSL/TLS warnings
- Runtime warnings
- Import errors
- Connection errors
- Database errors
- API authentication errors
"""

import os
import sys
import subprocess
import json
import time
import signal
import threading
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class EnhancedDebugger:
    """Enhanced debugger with comprehensive 10-second analysis"""
    
    def __init__(self):
        self.running = True
        self.process = None
        self.log_file = None
        self.start_time = None
        self.end_time = None
        
        # Analysis results
        self.errors = []
        self.warnings = []
        self.successes = []
        self.performance_metrics = {}
        
        # Handle Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\n🛑 Debugger stopped by user")
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
            self.log_file = project_root / 'logs' / f'enhanced_debug_{timestamp}.log'
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
    
    def run_10_second_analysis(self):
        """Run exactly 10 seconds of analysis"""
        print("🔍 Enhanced Debugger - 10 Second Analysis")
        print("=" * 60)
        
        # Start process if not running
        if not self.process:
            if not self.start_process():
                return False
        
        # Record start time
        self.start_time = time.time()
        print("⏱️  Running for exactly 10 seconds...")
        
        # Run for exactly 10 seconds
        while time.time() - self.start_time < 10 and self.running:
            elapsed = time.time() - self.start_time
            if int(elapsed) % 2 == 0:  # Update every 2 seconds
                print(f"⏱️  {int(elapsed)}s elapsed...")
            time.sleep(0.1)
        
        # Record end time
        self.end_time = time.time()
        actual_duration = self.end_time - self.start_time
        
        print(f"✅ Analysis completed in {actual_duration:.1f}s")
        
        # Analyze log file
        print("📖 Reading and analyzing log file...")
        log_content = self.read_log_file()
        
        # Perform comprehensive analysis
        self.analyze_log_comprehensive(log_content)
        
        # Generate report
        self.generate_report()
        
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
    
    def analyze_log_comprehensive(self, log_content: str):
        """Comprehensive log analysis"""
        
        # Error patterns
        error_patterns = [
            (r'⚠️ Webhook failed: (\d+)', 'Webhook HTTP Error'),
            (r'RuntimeWarning: (.+)', 'Runtime Warning'),
            (r'NotOpenSSLWarning: (.+)', 'SSL/TLS Warning'),
            (r'ImportError: (.+)', 'Import Error'),
            (r'ModuleNotFoundError: (.+)', 'Module Not Found'),
            (r'FileNotFoundError: (.+)', 'File Not Found'),
            (r'PermissionError: (.+)', 'Permission Error'),
            (r'ConnectionError: (.+)', 'Connection Error'),
            (r'TimeoutError: (.+)', 'Timeout Error'),
            (r'SyntaxError: (.+)', 'Syntax Error'),
            (r'IndentationError: (.+)', 'Indentation Error'),
            (r'KeyError: (.+)', 'Key Error'),
            (r'AttributeError: (.+)', 'Attribute Error'),
            (r'TypeError: (.+)', 'Type Error'),
            (r'ValueError: (.+)', 'Value Error'),
            (r'OSError: (.+)', 'OS Error'),
            (r'RequestException: (.+)', 'Request Exception'),
            (r'401 Client Error: Unauthorized', 'API Authentication Error'),
            (r'403 Client Error: Forbidden', 'API Authorization Error'),
            (r'404 Client Error: Not Found', 'API Endpoint Not Found'),
            (r'500 Server Error', 'Server Error'),
        ]
        
        # Warning patterns
        warning_patterns = [
            (r'Warning: (.+)', 'General Warning'),
            (r'DeprecationWarning: (.+)', 'Deprecation Warning'),
            (r'UserWarning: (.+)', 'User Warning'),
            (r'FutureWarning: (.+)', 'Future Warning'),
        ]
        
        # Success patterns
        success_patterns = [
            (r'✅ (.+)', 'Success Indicator'),
            (r'Success: (.+)', 'Success Message'),
            (r'Started', 'Service Started'),
            (r'Running', 'Service Running'),
            (r'Connected', 'Connection Successful'),
            (r'Database connection established', 'Database Connected'),
            (r'Trading tables created successfully', 'Database Tables Created'),
        ]
        
        # Performance patterns
        performance_patterns = [
            (r'ready in (\d+) ms', 'React Startup Time'),
            (r'Execution Time: ([\d.]+)s', 'Script Execution Time'),
            (r'Total runtime: ([\d.]+) seconds', 'Bot Runtime'),
        ]
        
        # Analyze errors
        for pattern, description in error_patterns:
            matches = re.findall(pattern, log_content)
            for match in matches:
                self.errors.append({
                    'type': description,
                    'details': match,
                    'severity': 'high'
                })
        
        # Analyze warnings
        for pattern, description in warning_patterns:
            matches = re.findall(pattern, log_content)
            for match in matches:
                self.warnings.append({
                    'type': description,
                    'details': match,
                    'severity': 'medium'
                })
        
        # Analyze successes
        for pattern, description in success_patterns:
            matches = re.findall(pattern, log_content)
            for match in matches:
                self.successes.append({
                    'type': description,
                    'details': match,
                    'severity': 'low'
                })
        
        # Analyze performance
        for pattern, description in performance_patterns:
            matches = re.findall(pattern, log_content)
            for match in matches:
                self.performance_metrics[description] = match
    
    def generate_report(self):
        """Generate comprehensive debug report"""
        print("\n" + "=" * 60)
        print("🔍 ENHANCED DEBUGGER ANALYSIS REPORT")
        print("=" * 60)
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   Duration: {self.end_time - self.start_time:.1f} seconds")
        print(f"   Errors Found: {len(self.errors)}")
        print(f"   Warnings Found: {len(self.warnings)}")
        print(f"   Success Indicators: {len(self.successes)}")
        
        # Critical Issues
        if self.errors:
            print(f"\n🚨 CRITICAL ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:5], 1):  # Show top 5
                print(f"   {i}. {error['type']}: {error['details'][:100]}...")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more errors")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings[:3], 1):  # Show top 3
                print(f"   {i}. {warning['type']}: {warning['details'][:100]}...")
            if len(self.warnings) > 3:
                print(f"   ... and {len(self.warnings) - 3} more warnings")
        
        # Success Indicators
        if self.successes:
            print(f"\n✅ SUCCESS INDICATORS ({len(self.successes)}):")
            for i, success in enumerate(self.successes[:5], 1):  # Show top 5
                print(f"   {i}. {success['type']}: {success['details'][:100]}...")
        
        # Performance Metrics
        if self.performance_metrics:
            print(f"\n⚡ PERFORMANCE METRICS:")
            for metric, value in self.performance_metrics.items():
                print(f"   {metric}: {value}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        webhook_errors = [e for e in self.errors if 'Webhook' in e['type']]
        if webhook_errors:
            print("   🔧 Fix webhook 403 errors by updating CORS configuration")
        
        ssl_warnings = [w for w in self.warnings if 'SSL' in w['type']]
        if ssl_warnings:
            print("   🔧 Update urllib3 to version 1.26.18 to fix SSL warnings")
        
        runtime_warnings = [w for w in self.warnings if 'Runtime' in w['type']]
        if runtime_warnings:
            print("   🔧 Fix async/await issues in webhook server")
        
        if not self.errors and not self.warnings:
            print("   ✅ System appears to be running smoothly!")
        
        # Save detailed report
        self.save_detailed_report()
        
        # Update debugger_info.md with latest results
        self.update_debugger_info()
        
        print(f"\n📄 Detailed report saved to: logs/enhanced_debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    def save_detailed_report(self):
        """Save detailed report to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = project_root / 'logs' / f'enhanced_debug_report_{timestamp}.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': self.end_time - self.start_time if self.end_time else 0,
            'log_file': str(self.log_file) if self.log_file else None,
            'errors': self.errors,
            'warnings': self.warnings,
            'successes': self.successes,
            'performance_metrics': self.performance_metrics,
            'summary': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'total_successes': len(self.successes),
                'critical_issues': len([e for e in self.errors if e['severity'] == 'high']),
                'system_status': 'healthy' if not self.errors else 'issues_detected'
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    def update_debugger_info(self):
        """Update debugger_info.md with latest analysis results"""
        debugger_info_file = project_root / 'Bot' / 'debuggers' / 'debugger_info.md'
        
        # Read current debugger_info.md
        current_content = ""
        if debugger_info_file.exists():
            with open(debugger_info_file, 'r') as f:
                current_content = f.read()
        
        # Generate new status section
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration = self.end_time - self.start_time if self.end_time else 0
        
        # Determine system status
        if not self.errors and not self.warnings:
            status = "🟢 HEALTHY"
            status_description = "System running smoothly with no issues detected"
        elif len(self.errors) == 0 and len(self.warnings) > 0:
            status = "🟡 WARNINGS"
            status_description = f"System running with {len(self.warnings)} warnings"
        else:
            status = "🔴 ISSUES"
            status_description = f"System has {len(self.errors)} errors and {len(self.warnings)} warnings"
        
        # Create new status section
        new_status_section = f"""
## 📊 Latest Debugger Status

**Last Run**: {timestamp}  
**Duration**: {duration:.1f} seconds  
**Status**: {status}  
**Description**: {status_description}

### 📈 Quick Stats
- **Errors**: {len(self.errors)}
- **Warnings**: {len(self.warnings)}
- **Success Indicators**: {len(self.successes)}
- **Performance Metrics**: {len(self.performance_metrics)}

### 🚨 Critical Issues
"""
        
        if self.errors:
            for i, error in enumerate(self.errors[:3], 1):
                new_status_section += f"{i}. **{error['type']}**: {error['details'][:100]}...\n"
        else:
            new_status_section += "✅ No critical issues detected\n"
        
        new_status_section += "\n### ⚠️ Warnings\n"
        
        if self.warnings:
            for i, warning in enumerate(self.warnings[:3], 1):
                new_status_section += f"{i}. **{warning['type']}**: {warning['details'][:100]}...\n"
        else:
            new_status_section += "✅ No warnings detected\n"
        
        new_status_section += "\n### ✅ Success Indicators\n"
        
        if self.successes:
            for i, success in enumerate(self.successes[:3], 1):
                new_status_section += f"{i}. **{success['type']}**: {success['details'][:100]}...\n"
        else:
            new_status_section += "ℹ️ No success indicators in this run\n"
        
        # Update the file content
        if "## 📊 Latest Debugger Status" in current_content:
            # Replace existing status section
            lines = current_content.split('\n')
            start_idx = None
            end_idx = None
            
            for i, line in enumerate(lines):
                if line.strip() == "## 📊 Latest Debugger Status":
                    start_idx = i
                elif start_idx and line.startswith("## ") and i > start_idx:
                    end_idx = i
                    break
            
            if start_idx is not None:
                if end_idx is not None:
                    lines = lines[:start_idx] + new_status_section.strip().split('\n') + lines[end_idx:]
                else:
                    lines = lines[:start_idx] + new_status_section.strip().split('\n')
                
                updated_content = '\n'.join(lines)
            else:
                updated_content = current_content + new_status_section
        else:
            # Add new status section at the end
            updated_content = current_content + new_status_section
        
        # Write updated content
        with open(debugger_info_file, 'w') as f:
            f.write(updated_content)
        
        print(f"📝 Updated debugger_info.md with latest analysis results")

def main():
    """Main enhanced debugger function"""
    debugger = EnhancedDebugger()
    
    try:
        success = debugger.run_10_second_analysis()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n🛑 Debugger stopped by user")
        return 1
    except Exception as e:
        print(f"❌ Enhanced debugger failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
