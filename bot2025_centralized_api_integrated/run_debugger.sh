#!/bin/bash

# 🌟 Enhanced Debugger Runner - The Cosmic System Analyzer
# Runs the debugger with automatic port cleanup and setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print functions
print_status() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ ! -z "$pids" ]; then
        print_warning "Killing processes on port $port (PIDs: $pids)"
        echo $pids | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        print_status "Port $port is free"
    fi
}

# Function to check if a port is free
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is free
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if check_port $port; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Main debugger function
run_debugger() {
    print_header "🔍 Enhanced Debugger - The Cosmic System Analyzer"
    print_header "=================================================="
    
    # Check if we're in the right directory
    if [ ! -f "run.py" ]; then
        print_error "Please run this script from the project root directory"
        print_error "Current directory: $(pwd)"
        print_error "Expected files: run.py, webhook/, scripts/"
        exit 1
    fi
    
    print_success "Running from project root: $(pwd)"
    
    # Load environment variables
    if [ -f ".env" ]; then
        print_status "Loading environment variables from .env"
        export $(cat .env | grep -v '^#' | xargs)
    else
        print_warning "No .env file found, using defaults"
        # Create basic .env if missing
        if [ -f "config/env.example" ]; then
            print_status "Creating .env from env.example"
            cp config/env.example .env
        fi
    fi
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        print_status "Activating virtual environment"
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_warning "No virtual environment found"
        print_status "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        print_status "Installing dependencies..."
        pip install -r config/requirements.txt
        print_success "Virtual environment created and dependencies installed"
    fi
    
    # Kill any existing processes on our ports
    print_status "Cleaning up existing processes..."
    kill_port 5000  # Old webhook port
    kill_port 5001  # New webhook port
    kill_port 8765  # WebSocket
    kill_port 3000  # React frontend
    kill_port 5173  # Vite dev server
    kill_port 5174  # Vite dev server
    kill_port 5175  # Vite dev server
    
    # Create necessary directories
    print_status "Creating necessary directories..."
    mkdir -p logs/categories
    mkdir -p data/output
    mkdir -p data/backup
    
    # Update environment variables for new port
    print_status "Updating configuration for port 5001..."
    sed -i '' 's/WEB_PORT=5000/WEB_PORT=5001/g' .env 2>/dev/null || true
    sed -i '' 's|WEBHOOK_URL=http://localhost:5000/webhook|WEBHOOK_URL=http://localhost:5001/webhook|g' .env 2>/dev/null || true
    
    # Start webhook server in background
    print_status "Starting webhook server on port 5001..."
    python3 webhook/webhook_server.py > logs/webhook_debug.log 2>&1 &
    WEBHOOK_PID=$!
    
    # Wait for webhook server
    if wait_for_service "Webhook Server" 5001; then
        print_success "Webhook server started successfully (PID: $WEBHOOK_PID)"
    else
        print_error "Failed to start webhook server"
        exit 1
    fi
    
    # Test webhook server
    print_status "Testing webhook server..."
    sleep 2
    if curl -s -X POST http://localhost:5001/webhook -H "Content-Type: application/json" -d '{"test": "debugger"}' > /dev/null 2>&1; then
        print_success "Webhook server test successful"
    else
        print_warning "Webhook server test failed, but continuing..."
    fi
    
    # Run the enhanced debugger
    print_header "🚀 Starting Enhanced Debugger Analysis"
    print_status "Running 10-second comprehensive analysis..."
    
    # Run the debugger
    python3 Bot/debuggers/enhanced_debugger.py
    
    # Get the debugger exit code
    DEBUGGER_EXIT_CODE=$?
    
    # Cleanup
    print_status "Cleaning up processes..."
    kill $WEBHOOK_PID 2>/dev/null || true
    
    # Show results
    print_header "📊 Debugger Analysis Complete"
    
    if [ $DEBUGGER_EXIT_CODE -eq 0 ]; then
        print_success "Debugger completed successfully!"
        
        # Show latest report
        LATEST_REPORT=$(ls -t logs/enhanced_debug_report_*.json 2>/dev/null | head -1)
        if [ ! -z "$LATEST_REPORT" ]; then
            print_status "Latest report: $LATEST_REPORT"
            
            # Extract summary from JSON
            if command -v jq >/dev/null 2>&1; then
                print_header "📋 Summary:"
                jq -r '.summary | "System Status: \(.system_status)\nTotal Errors: \(.total_errors)\nTotal Warnings: \(.total_warnings)\nCritical Issues: \(.critical_issues)"' "$LATEST_REPORT" 2>/dev/null || true
            fi
        fi
    else
        print_error "Debugger failed with exit code: $DEBUGGER_EXIT_CODE"
    fi
    
    print_header "🎯 Debugger Session Complete"
    print_status "Check logs/ directory for detailed reports"
    print_status "Check logs/enhanced_debug_*.log for raw logs"
    
    return $DEBUGGER_EXIT_CODE
}

# Handle Ctrl+C gracefully
cleanup() {
    print_warning "Received interrupt signal, cleaning up..."
    # Kill background processes
    jobs -p | xargs kill 2>/dev/null || true
    print_status "Cleanup complete"
    exit 1
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    # Check if Python is available
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -d "scripts" ] || [ ! -d "webhook" ]; then
        print_error "Please run this script from the project root directory"
        print_error "Expected directories: scripts/, webhook/"
        exit 1
    fi
    
    # Run the debugger
    run_debugger
    
    exit $?
}

# Run main function
main "$@"
