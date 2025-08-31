#!/usr/bin/env python3
"""
🌟 Cosmic Trading Bot - Dashboard Test Script
Starts both the API server and React dashboard for testing
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_api_server():
    """Start the Flask API server"""
    print("🚀 Starting API Server...")
    
    try:
        # Start API server in background
        api_process = subprocess.Popen(
            [sys.executable, '../api/api_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ API Server started (PID: {})".format(api_process.pid))
        print("🌐 API available at: http://localhost:5000")
        
        return api_process
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_react_dashboard():
    """Start the React dashboard"""
    print("🌐 Starting React Dashboard...")
    
    dashboard_path = Path('web/dashboard')
    if not dashboard_path.exists():
        print("❌ React dashboard not found at web/dashboard")
        return None
    
    try:
        # Start React dashboard in background
        dashboard_process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=dashboard_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ React Dashboard started (PID: {})".format(dashboard_process.pid))
        print("📊 Dashboard available at: http://localhost:5173")
        
        return dashboard_process
        
    except Exception as e:
        print(f"❌ Failed to start React dashboard: {e}")
        return None

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("⚠️  No .env file found!")
        print("💡 Please create .env file from env.example:")
        print("   cp env.example .env")
        print("   nano .env")
        return False
    
    # Check if web/dashboard exists
    if not Path('web/dashboard').exists():
        print("❌ React dashboard not found!")
        print("💡 Please run: cd web && npx create-vite@latest dashboard --template react")
        return False
    
    # Check if node_modules exists
    if not Path('web/dashboard/node_modules').exists():
        print("⚠️  Node modules not installed!")
        print("💡 Please run: cd web/dashboard && npm install")
        return False
    
    print("✅ All dependencies are ready!")
    return True

def main():
    """Main function"""
    print("🌟 Cosmic Trading Bot - Dashboard Test")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please fix the issues above and try again.")
        return 1
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        return 1
    
    # Wait a bit for API server to start
    print("⏳ Waiting for API server to initialize...")
    time.sleep(3)
    
    # Start React dashboard
    dashboard_process = start_react_dashboard()
    if not dashboard_process:
        api_process.terminate()
        return 1
    
    print("\n🎉 Both services started successfully!")
    print("=" * 50)
    print("📊 React Dashboard: http://localhost:5173")
    print("🌐 API Server: http://localhost:5000")
    print("=" * 50)
    print("💡 Testing Instructions:")
    print("1. Open http://localhost:5173 in your browser")
    print("2. Click 'Test Connections' to verify API keys")
    print("3. Check your balance and system status")
    print("4. Try starting/stopping the bot")
    print("5. View real-time logs in the Logs Viewer")
    print("=" * 50)
    print("🛑 Press Ctrl+C to stop both services")
    
    try:
        # Keep running and monitor processes
        while True:
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API Server stopped unexpectedly")
                break
            
            if dashboard_process.poll() is not None:
                print("❌ React Dashboard stopped unexpectedly")
                break
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        
        # Stop API server
        if api_process:
            api_process.terminate()
            print("🛑 API Server stopped")
        
        # Stop React dashboard
        if dashboard_process:
            dashboard_process.terminate()
            print("🛑 React Dashboard stopped")
        
        print("✅ All services stopped")
        return 0
    
    return 0

if __name__ == "__main__":
    exit(main())
