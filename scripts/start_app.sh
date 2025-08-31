#!/bin/bash

# 🌟 Trading Bot Startup Script
# Starts all components: webhook server, test bot, and React frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
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
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Function to kill process on port
kill_port() {
    local port=$1
    if check_port $port; then
        print_warning "Killing process on port $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Main startup function
main() {
    print_status "🌟 Starting Trading Bot Application"
    print_status "====================================="
    
    # Check if we're in the right directory
    if [ ! -f "run.py" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Load environment variables
    if [ -f ".env" ]; then
        print_status "Loading environment variables from .env"
        export $(cat .env | grep -v '^#' | xargs)
    else
        print_warning "No .env file found, using defaults"
    fi
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        print_status "Activating virtual environment"
        source venv/bin/activate
    else
        print_warning "No virtual environment found"
    fi
    
    # Kill any existing processes on our ports
    print_status "Cleaning up existing processes..."
    kill_port 5001  # Webhook server
    kill_port 8765  # WebSocket
    kill_port 3000  # React frontend
    
    # Create necessary directories
    print_status "Creating necessary directories..."
    mkdir -p logs/categories
    mkdir -p data/output
    mkdir -p data/backup
    
    # Start webhook server in background
    print_status "Starting webhook server..."
    python webhook/webhook_server.py &
    WEBHOOK_PID=$!
    
    # Wait for webhook server
    if wait_for_service "Webhook Server" 5001; then
        print_success "Webhook server started successfully (PID: $WEBHOOK_PID)"
    else
        print_error "Failed to start webhook server"
        exit 1
    fi
    
    # Start test bot in background
    print_status "Starting test trading bot..."
    python -c "
import sys
sys.path.append('.')
from Bot.ver_1.main_test import test_bot
test_bot.start()
" &
    TEST_BOT_PID=$!
    
    print_success "Test bot started successfully (PID: $TEST_BOT_PID)"
    
    # Start React frontend
    print_status "Starting React frontend..."
    cd web/dashboard
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing React dependencies..."
        npm install
    fi
    
    # Start React development server
    npm run dev &
    REACT_PID=$!
    cd ../..
    
    # Wait for React frontend
    if wait_for_service "React Frontend" 3000; then
        print_success "React frontend started successfully (PID: $REACT_PID)"
    else
        print_error "Failed to start React frontend"
        exit 1
    fi
    
    # Save PIDs to file for cleanup
    echo "$WEBHOOK_PID $TEST_BOT_PID $REACT_PID" > .running_pids
    
    print_success "🎉 All services started successfully!"
    print_status "====================================="
    print_status "🌐 React Frontend: http://localhost:3000"
    print_status "🔗 Webhook Server: http://localhost:5000"
    print_status "📡 WebSocket: ws://localhost:8765"
    print_status "📊 Test Bot: Running in background"
    print_status ""
    print_warning "Press Ctrl+C to stop all services"
    
    # Function to cleanup on exit
    cleanup() {
        print_status "Shutting down services..."
        
        # Kill all background processes
        if [ -f ".running_pids" ]; then
            for pid in $(cat .running_pids); do
                if kill -0 $pid 2>/dev/null; then
                    print_status "Killing process $pid"
                    kill $pid
                fi
            done
            rm -f .running_pids
        fi
        
        # Kill processes on our ports
        kill_port 5000
        kill_port 8765
        kill_port 3000
        
        print_success "All services stopped"
        exit 0
    }
    
    # Set up signal handlers
    trap cleanup SIGINT SIGTERM
    
    # Keep script running
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"
