#!/bin/bash

# Redirect all output to startup log
exec > >(tee -a startup.log) 2>&1

# 🌟 Smart Trading Bot App Runner - The Cosmic Launcher
# ===================================================
# 
# 📁 File: /bot2025_centralized_api_integrated/run_app.sh
# 🎯 Purpose: Complete application launcher with frontend URL display
# 🔧 Function: Starts all components and displays frontend URLs
# 
# 🌟 Features:
# - Environment setup and validation
# - Port cleanup and management
# - Webhook server startup
# - React frontend startup
# - URL display and monitoring
# - Process management and cleanup
# 
# 🔄 Usage:
#     ./run_app.sh                    # Run complete app
#     ./run_app.sh frontend-only      # Run only frontend
#     ./run_app.sh backend-only       # Run only backend
# 
# 📋 Dependencies:
# - .env file with configuration
# - venv/ virtual environment
# - All required Python packages
# - Node.js and npm for frontend
# 
# 🔗 Related Files:
# - .env (environment configuration)
# - Bot/main.py (trading logic)
# - Model/main.py (ML model)
# - webhook/webhook_server.py (communication hub)
# - web/dashboard/ (React frontend)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root (parent directory of scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Function to print colored status
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_url() {
    echo -e "${PURPLE}🌐 $1${NC}"
}

# Clear logs model_output.csv
clear_model_output() {
    print_status "Clearing logs/model_output.csv"
    : > "$PROJECT_ROOT/logs/model_output.csv" 2>/dev/null || true
}

# Clear all log files
clear_all_logs() {
    print_status "Clearing all log files..."
    
    # Clear model logs
    : > "$PROJECT_ROOT/logs/model/real.log" 2>/dev/null || true
    : > "$PROJECT_ROOT/logs/model/test.log" 2>/dev/null || true
    : > "$PROJECT_ROOT/logs/model/old_model.log" 2>/dev/null || true
    
    # Clear bot logs
    : > "$PROJECT_ROOT/logs/bot/main.log" 2>/dev/null || true
    : > "$PROJECT_ROOT/logs/bot/test.log" 2>/dev/null || true
    
    # Clear API logs
    : > "$PROJECT_ROOT/logs/api/api_server.log" 2>/dev/null || true
    : > "$PROJECT_ROOT/logs/api/api_server.out" 2>/dev/null || true
    
    # Clear webhook logs
    : > "$PROJECT_ROOT/logs/webhook/webhook_server.log" 2>/dev/null || true
    : > "$PROJECT_ROOT/logs/webhook/webhook_app.log" 2>/dev/null || true
    
    # Clear frontend logs
    : > "$PROJECT_ROOT/logs/frontend/frontend_app.log" 2>/dev/null || true
    : > "$PROJECT_ROOT/logs/frontend/frontend_debug.log" 2>/dev/null || true
    
    # Clear startup log
    : > "$PROJECT_ROOT/startup.log" 2>/dev/null || true
    
    print_success "All log files cleared"
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$pids" ]; then
        print_warning "Killing processes on port $port (PIDs: $pids)"
        echo $pids | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        print_info "Port $port is free"
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$port" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "$service_name failed to start after $max_attempts attempts"
            return 1
        fi
        
        sleep 1
        attempt=$((attempt + 1))
    done
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "app/venv" ] && [ ! -d ".venv" ]; then
        print_error "Virtual environment not found. Please run setup first."
        exit 1
    fi
}

# Function to check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_error ".env file not found. Please copy env.example to .env and configure it."
        exit 1
    fi
}

# Function to check if Node.js is available
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
}

# Function to start backend services
start_backend() {
    print_status "Starting backend services..."
    
    # Load environment variables
    print_status "Loading environment variables from .env"
    source .env 2>/dev/null || true
    
    # Activate virtual environment
    print_status "Activating virtual environment"
    # Activate virtual environment (try app/venv first, then .venv)
    if [ -d "app/venv" ]; then
        source app/venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # Clear all log files before starting
    clear_all_logs
    
    # Clear model output file before starting
    clear_model_output

    # Create necessary directories
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p logs/webhook logs/api logs/frontend logs/model logs/bot logs/system
    mkdir -p Data/output
    mkdir -p Data/backup
    
    # Kill any existing processes on our ports
    print_status "Cleaning up existing processes..."
    kill_port 5001  # Webhook server
    kill_port 8767  # WebSocket
    kill_port 3000  # React frontend (alternative)
    kill_port 5173  # Vite dev server
    kill_port 5050  # API server
    
    # Start webhook server
    print_status "Starting webhook server on port 5001..."
    python3 app/modules/webhook/webhook_server.py > logs/webhook/server.log 2>&1 &
    WEBHOOK_PID=$!
    
    # Wait for webhook server
    if wait_for_service "Webhook Server" 5001; then
        print_success "Webhook server started successfully (PID: $WEBHOOK_PID)"
    else
        print_error "Failed to start webhook server"
        return 1
    fi
    
    # Test webhook server
    print_status "Testing webhook server..."
    if curl -s -X POST http://localhost:5001/webhook \
        -H "Content-Type: application/json" \
        -d '{"test": "data"}' >/dev/null 2>&1; then
        print_success "Webhook server test successful"
    else
        print_warning "Webhook server test failed, but continuing..."
    fi
    
    print_success "Backend services started successfully"
    return 0
}

# Function to start API server
start_api_server() {
    print_status "Starting API server on port 5050..."

    # Activate virtual environment (try app/venv first, then .venv)
    if [ -d "app/venv" ]; then
        source app/venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi

    kill_port 5050
    python3 app/api/api_server.py > logs/api/server.log 2>&1 &
    API_PID=$!

    if wait_for_service "API Server" 5050; then
        print_success "API server started successfully (PID: $API_PID)"
    else
        print_error "Failed to start API server"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend..."
    
    # Resolve frontend directory (supports both web/dashboard and app/web/dashboard)
    FRONTEND_DIR=""
    LOG_REL=""
    if [ -d "app/web/dashboard" ]; then
        FRONTEND_DIR="app/web/dashboard"
        LOG_REL="../../../logs"
    elif [ -d "web/dashboard" ]; then
        FRONTEND_DIR="web/dashboard"
        LOG_REL="../../logs"
    else
        print_error "Frontend dashboard not found at app/web/dashboard or web/dashboard"
        return 1
    fi

    # Ensure Node is available
    if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
        print_error "Node.js or npm not installed. Please install Node.js."
        return 1
    fi
    
    # Check if package.json exists
    if [ ! -f "$FRONTEND_DIR/package.json" ]; then
        print_error "package.json not found in $FRONTEND_DIR"
        return 1
    fi
    
    # Kill any existing processes on frontend ports
    kill_port 3000  # React frontend (alternative)
    kill_port 5173  # Vite dev server
    
    # Start React development server
    print_status "Starting React development server in $FRONTEND_DIR..."
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists, if not install dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start the development server
    npm run dev > "$LOG_REL/frontend/app.log" 2>&1 &
    FRONTEND_PID=$!
    cd - >/dev/null 2>&1 || true
    
    # Wait for frontend to start (up to 30s)
    max_attempts=30
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if lsof -i:5173 >/dev/null 2>&1; then
            print_success "Frontend started successfully (PID: $FRONTEND_PID)"
            print_url "Frontend URL: http://localhost:5173"
            print_url "Frontend Debugger: Available in the floating panel"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done

    print_error "Failed to start frontend after $max_attempts seconds"
    return 1
}

# Function to start main bot
start_main_bot() {
    print_status "Starting main trading bot..."
    
    # Activate virtual environment
    # Activate virtual environment (try app/venv first, then .venv)
    if [ -d "app/venv" ]; then
        source app/venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # Start main bot in background
    python3 app/modules/bot/main.py > logs/bot/main.log 2>&1 &
    MAIN_BOT_PID=$!
    
    print_success "Main bot started successfully (PID: $MAIN_BOT_PID)"
    return 0
}

# Function to start model
start_model() {
    print_status "Starting ML model..."
    
    # Activate virtual environment
    # Activate virtual environment (try app/venv first, then .venv)
    if [ -d "app/venv" ]; then
        source app/venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # Start model in background
    python3 app/modules/model/main.py > logs/model/real.log 2>&1 &
    MODEL_PID=$!
    
    print_success "ML model started successfully (PID: $MODEL_PID)"
    return 0
}

# Function to display URLs and status
display_status() {
    echo ""
    echo "🌟 ========================================="
    echo "🌟 SMART TRADING BOT - APPLICATION STATUS"
    echo "🌟 ========================================="
    echo ""
    
    # Check webhook server
    if lsof -i:5001 >/dev/null 2>&1; then
        print_success "Webhook Server: Running on port 5001"
        print_url "Webhook URL: http://localhost:5001/webhook"
    else
        print_error "Webhook Server: Not running"
    fi
    
    # Check API server
    if lsof -i:5050 >/dev/null 2>&1; then
        print_success "API Server: Running on port 5050"
        print_url "API URL: http://localhost:5050"
    else
        print_warning "API Server: Not running"
    fi
    
    # Check frontend
    if lsof -i:5173 >/dev/null 2>&1; then
        print_success "Frontend: Running on port 5173"
        print_url "🌐 Frontend URL: http://localhost:5173"
        print_url "🔍 Frontend Debugger: Available in floating panel"
        
        # Open Edge browser automatically to API index
        print_status "Opening Edge browser to API index..."
        if command -v open &> /dev/null; then
            open -a "Microsoft Edge" "http://localhost:5050" 2>/dev/null || \
            open -a "Edge" "http://localhost:5050" 2>/dev/null || \
            print_warning "Could not open Edge automatically. Please open http://localhost:5050 manually"
        else
            print_warning "Could not open Edge automatically. Please open http://localhost:5050 manually"
        fi
    else
        print_error "Frontend: Not running"
    fi
    
    # Check main bot
    if [ ! -z "$MAIN_BOT_PID" ] && kill -0 $MAIN_BOT_PID 2>/dev/null; then
        print_success "Main Bot: Running (PID: $MAIN_BOT_PID)"
    else
        print_warning "Main Bot: Not running"
    fi
    
    # Check model
    if [ ! -z "$MODEL_PID" ] && kill -0 $MODEL_PID 2>/dev/null; then
        print_success "ML Model: Running (PID: $MODEL_PID)"
    else
        print_warning "ML Model: Not running"
    fi
    
    echo ""
    echo "🎯 Quick Access:"
    print_url "Frontend Dashboard: http://localhost:5173"
    print_url "Webhook Endpoint: http://localhost:5001/webhook"
    print_url "WebSocket: ws://localhost:8767"
    echo ""
    echo "📊 Monitoring:"
    print_info "Logs: logs/ directory"
    print_info "Frontend Log: logs/frontend_app.log"
    print_info "Webhook Log: logs/webhook_app.log"
    print_info "Main Bot Log: logs/bot/main.log"
    print_info "Model Log: logs/model/real.log"
    echo ""
    echo "🛑 To stop all services: Press Ctrl+C"
    echo ""
}

# Function to cleanup on exit
cleanup() {
    echo ""
    print_status "Cleaning up processes..."
    
    # Kill background processes
    if [ ! -z "$WEBHOOK_PID" ]; then
        kill $WEBHOOK_PID 2>/dev/null || true
        print_info "Webhook server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_info "Frontend stopped"
    fi
    
    if [ ! -z "$MAIN_BOT_PID" ]; then
        kill $MAIN_BOT_PID 2>/dev/null || true
        print_info "Main bot stopped"
    fi
    
    if [ ! -z "$MODEL_PID" ]; then
        kill $MODEL_PID 2>/dev/null || true
        print_info "ML model stopped"
    fi
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
        print_info "API server stopped"
    fi
    
    print_success "Cleanup completed"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main execution
main() {
    echo "🌟 Smart Trading Bot App Runner"
    echo "=================================================="
    print_status "Running from project root: $PROJECT_ROOT"
    
    # Check prerequisites
    check_venv
    check_env
    check_node
    
    # Parse command line arguments
    MODE=${1:-"full"}
    
    case $MODE in
        "frontend-only")
            print_info "Running in frontend-only mode"
            start_frontend
            ;;
        "backend-only")
            print_info "Running in backend-only mode"
            start_backend
            start_api_server
            start_main_bot
            # Model starts only when user presses Start button with selected interval
            ;;
        "test-stack")
            print_info "Running test stack (webhook + frontend + test model + test bot)"
            start_backend
            start_frontend
            start_api_server
            # Start test model
            print_status "Starting test model..."
            if [ -d "app/venv" ]; then
                source app/venv/bin/activate
            elif [ -d ".venv" ]; then
                source .venv/bin/activate
            fi
            python3 app/modules/model/test_model.py > logs/model/test.log 2>&1 &
            TEST_MODEL_PID=$!
            print_success "Test model started (PID: $TEST_MODEL_PID)"
            # Start test bot
            print_status "Starting test bot..."
            python3 app/modules/test/test_main.py > logs/test_bot.log 2>&1 &
            TEST_BOT_PID=$!
            print_success "Test bot started (PID: $TEST_BOT_PID)"
            ;;
        "full"|*)
            print_info "Running in full mode"
            start_backend
            start_frontend
            start_api_server
            start_main_bot
            # Model starts only when user presses Start button with selected interval
            ;;
    esac
    
    # Display status
    display_status
    
    # Keep the script running
    print_status "All services started. Press Ctrl+C to stop."
    while true; do
        sleep 10
    done
}

# Run main function
main "$@"
