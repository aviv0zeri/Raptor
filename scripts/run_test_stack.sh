#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

log() { echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }
ok() { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err() { echo -e "${RED}❌ $1${NC}"; }

kill_port() {
  local port=$1
  local pids=$(lsof -ti:$port 2>/dev/null || true)
  if [ ! -z "$pids" ]; then
    warn "Killing processes on port $port (PIDs: $pids)"
    echo $pids | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
}

activate_venv() {
  if [ -d "app/venv" ]; then
    source app/venv/bin/activate
  elif [ -d ".venv" ]; then
    source .venv/bin/activate
  else
    err "Virtualenv not found (app/venv or .venv)"
    exit 1
  fi
}

start_webhook() {
  log "Starting webhook server (http://localhost:5001)"
  activate_venv
  mkdir -p logs
  python3 app/modules/webhook/webhook_server.py > logs/webhook_app.log 2>&1 &
  WEBHOOK_PID=$!
  sleep 2
  ok "Webhook PID: $WEBHOOK_PID"
}

start_api() {
  log "Starting Flask API server (http://localhost:5050)"
  activate_venv
  python3 app/api/api_server.py > logs/frontend_app.log 2>&1 &
  API_PID=$!
  sleep 2
  ok "API PID: $API_PID"
}

start_frontend() {
  log "Starting Vite dashboard (http://localhost:5173)"
  kill_port 5173
  pushd app/web/dashboard >/dev/null
  if [ ! -d node_modules ]; then
    log "Installing frontend dependencies"
    npm install
  fi
  npm run dev > ../../../logs/frontend_app.log 2>&1 &
  FRONTEND_PID=$!
  popd >/dev/null
  sleep 2
  ok "Frontend PID: $FRONTEND_PID"
}

start_test_model() {
  log "Starting Python test_model.py (JSON via API)"
  activate_venv
  python3 app/modules/model/test_model.py > logs/model_test.log 2>&1 &
  TEST_MODEL_PID=$!
  ok "Test model PID: $TEST_MODEL_PID"
}

start_test_bot() {
  log "Starting test trading bot (CSV consumer)"
  activate_venv
  python3 app/modules/test/test_main.py > logs/test_bot.log 2>&1 &
  TEST_BOT_PID=$!
  ok "Test bot PID: $TEST_BOT_PID"
}

main() {
  log "Running Test Stack from $PROJECT_ROOT"
  mkdir -p logs app/Data/rawdata Data/output Data/backup
  kill_port 5001
  kill_port 8767

  start_webhook
  start_api
  start_frontend
  start_test_model
  start_test_bot

  ok "All test services started"
  echo "WEBHOOK_PID=$WEBHOOK_PID" > logs/test_stack.pids
  echo "FRONTEND_PID=$FRONTEND_PID" >> logs/test_stack.pids
  echo "TEST_MODEL_PID=$TEST_MODEL_PID" >> logs/test_stack.pids
  echo "TEST_BOT_PID=$TEST_BOT_PID" >> logs/test_stack.pids
  echo "API_PID=$API_PID" >> logs/test_stack.pids

  log "Open http://localhost:5173/wall for SignalWall"
  # Try to auto-open Microsoft Edge to the Signal Wall
  if command -v open &> /dev/null; then
    open -a "Microsoft Edge" "http://localhost:5173/wall" 2>/dev/null || \
    open -a "Edge" "http://localhost:5173/wall" 2>/dev/null || \
    warn "Could not open Edge automatically. Please open http://localhost:5173/wall manually"
  fi
  log "Press Ctrl+C to stop"
  trap 'warn "Stopping..."; [ ! -z "$TEST_BOT_PID" ] && kill $TEST_BOT_PID 2>/dev/null || true; [ ! -z "$TEST_MODEL_PID" ] && kill $TEST_MODEL_PID 2>/dev/null || true; [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true; [ ! -z "$WEBHOOK_PID" ] && kill $WEBHOOK_PID 2>/dev/null || true; ok "Stopped"; exit 0' INT TERM
  while true; do sleep 10; done
}

main "$@"



