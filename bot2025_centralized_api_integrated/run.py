"""
🚀 Smart Trading Bot Runner - The Cosmic Orchestrator
====================================================

📁 File: /bot2025_centralized_api_integrated/run.py
🎯 Purpose: Main entry point for the trading bot system
🔧 Function: Loads environment variables and orchestrates all components

🌟 Features:
- Environment variable management
- Directory structure validation
- Component orchestration
- Error handling and logging
- System health checks

🔄 Usage:
    python run.py                    # Run in parallel mode (default)
    python run.py sequential         # Run in sequential mode
    python run.py --help            # Show help information

📋 Dependencies:
- .env file with configuration
- venv/ virtual environment
- All required Python packages

🔗 Related Files:
- .env (environment configuration)
- Bot/main.py (trading logic)
- Model/main.py (ML model)
- webhook/webhook_server.py (communication hub)
"""

import os
import sys
import subprocess
import multiprocessing
import signal
import time
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """
    🌟 Load environment variables from .env file
    The cosmic configuration loader that sets up our trading environment
    """
    # Look for .env file in the current directory
    env_file = Path('.env')
    
    if env_file.exists():
        print("🌟 Loading environment variables from .env file...")
        load_dotenv(env_file)
        print("✅ Environment variables loaded successfully")
    else:
        print("⚠️ No .env file found. Please create one from env.example")
        print("💡 Copy env.example to .env and fill in your configuration")
        return False
    
    # Validate required environment variables
    required_vars = [
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY',
        'DB_HOST',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("💡 Please check your .env file and ensure all required variables are set")
        return False
    
    print("✅ All required environment variables are set")
    return True

def setup_directories():
    """
    📁 Create necessary directories if they don't exist
    The cosmic directory creator that ensures our file structure is ready
    """
    directories = [
        'logs',
        'data/output',
        'data/backup',
        'config',
        'scripts',
        'tests',
        'docs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure verified")

def run_model():
    """
    🧠 Run the machine learning model
    The cosmic brain that generates trading signals
    """
    try:
        print("🧠 Starting the Machine Learning Model...")
        model_path = Path('Model/main.py')
        
        if not model_path.exists():
            print("❌ Model/main.py not found")
            return False
        
        # Run the model
        result = subprocess.run([sys.executable, str(model_path)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Model started successfully")
            return True
        else:
            print(f"❌ Model failed to start: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting model: {e}")
        return False

def run_main():
    """
    🚀 Run the main trading bot
    The cosmic executor that processes trading signals
    """
    try:
        print("🚀 Starting the Main Trading Bot...")
        main_path = Path('Bot/main.py')
        
        if not main_path.exists():
            print("❌ Bot/main.py not found")
            return False
        
        # Run the main bot
        result = subprocess.run([sys.executable, str(main_path)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Main bot started successfully")
            return True
        else:
            print(f"❌ Main bot failed to start: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting main bot: {e}")
        return False

def run_web_dashboard():
    """
    🌐 Run the React web dashboard
    The cosmic interface that provides real-time monitoring
    """
    try:
        print("🌐 Starting the React Web Dashboard...")
        dashboard_path = Path('web/dashboard')
        
        if not dashboard_path.exists():
            print("⚠️ web/dashboard not found, skipping web dashboard")
            return False
        
        # Change to dashboard directory and start the React app
        result = subprocess.run(
            ['npm', 'run', 'dev'],
            cwd=dashboard_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ React dashboard started successfully")
            print("🌐 Access the dashboard at: http://localhost:5173")
            return True
        else:
            print(f"❌ React dashboard failed to start: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting React dashboard: {e}")
        return False

def run_sequential():
    """
    🔄 Run components sequentially (model first, then main)
    The sequential orchestrator for testing and development
    """
    print("🔄 Running components sequentially...")
    
    # Start model first
    if run_model():
        print("⏳ Waiting for model to generate initial signals...")
        time.sleep(10)  # Wait for model to generate some signals
        
        # Then start main bot
        if run_main():
            print("✅ Sequential execution completed successfully")
            return True
        else:
            print("❌ Main bot failed to start")
            return False
    else:
        print("❌ Model failed to start")
        return False

def run_parallel():
    """
    ⚡ Run components in parallel
    The parallel orchestrator for production use
    """
    print("⚡ Running components in parallel...")
    
    processes = []
    
    try:
        # Start model in background
        model_process = subprocess.Popen([sys.executable, 'Model/main.py'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        processes.append(('Model', model_process))
        print("🧠 Model started in background")
        
        # Wait a bit for model to initialize
        time.sleep(5)
        
        # Start main bot in background
        main_process = subprocess.Popen([sys.executable, 'Bot/main.py'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        processes.append(('Main Bot', main_process))
        print("🚀 Main bot started in background")
        
        # Start React web dashboard in background (optional)
        if Path('web/dashboard').exists():
            web_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd='web/dashboard',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append(('React Dashboard', web_process))
            print("🌐 React dashboard started in background")
            print("🌐 Access the dashboard at: http://localhost:5173")
        
        print("✅ All components started successfully")
        print("🔄 Monitoring processes... (Press Ctrl+C to stop)")
        
        # Monitor processes
        while True:
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name} process stopped unexpectedly")
                    return False
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all processes...")
        for name, process in processes:
            process.terminate()
            print(f"🛑 {name} stopped")
        return True
    except Exception as e:
        print(f"❌ Error in parallel execution: {e}")
        return False

def main():
    """
    🌟 The Grand Runner - Main orchestration function
    The cosmic conductor that orchestrates the entire trading system
    """
    print("🌟 Cosmic Trading Bot Runner")
    print("=" * 50)
    
    # Load environment variables
    if not load_environment():
        print("❌ Failed to load environment variables")
        return 1
    
    # Setup directories
    setup_directories()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = 'parallel'  # Default to parallel mode
    
    print(f"🎯 Running in {mode} mode")
    
    try:
        if mode == 'sequential':
            success = run_sequential()
        elif mode == 'parallel':
            success = run_parallel()
        elif mode == 'model':
            success = run_model()
        elif mode == 'main':
            success = run_main()
        elif mode == 'web':
            success = run_web_dashboard()
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Available modes: sequential, parallel, model, main, web")
            return 1
        
        if success:
            print("✅ Trading bot execution completed successfully")
            return 0
        else:
            print("❌ Trading bot execution failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Trading bot stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
