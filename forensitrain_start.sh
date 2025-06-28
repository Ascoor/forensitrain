#!/usr/bin/env bash

set -e

echo "🚀 Starting ForensiTrain..."

# Check prerequisites
command -v python >/dev/null 2>&1 || { echo "Python is not installed" >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is not installed" >&2; exit 1; }

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# ---- Backend ----
cd "$SCRIPT_DIR/backend"
if [ ! -d "venv" ]; then
    python -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs) || true
fi
pip install -r requirements.txt
mkdir -p "$SCRIPT_DIR/logs"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# ---- Frontend ----
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

trap 'echo "\nStopping..."; kill $BACKEND_PID $FRONTEND_PID; exit 0' INT

wait $BACKEND_PID $FRONTEND_PID

