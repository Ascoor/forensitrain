#!/usr/bin/env bash

# Simple diagnostic script to verify that the FastAPI backend is running
# and attempt to start it automatically if needed.

set -e

BACKEND_PORT=8000
BACKEND_URL="http://localhost:$BACKEND_PORT/docs"

echo "🔍 Checking ForensiTrain Environment..."
echo "🧪 Checking if backend is running on port $BACKEND_PORT..."

if nc -z localhost "$BACKEND_PORT"; then
    echo "✅ Backend is running on port $BACKEND_PORT."
else
    echo "❌ Backend is not running. Trying to start backend..."
    cd "$(dirname "$0")/backend" || exit 1
    # Activate or create virtual environment
    if [ -d venv ]; then
        source venv/bin/activate
    else
        python3 -m venv venv
        source venv/bin/activate
    fi
    pip install -r requirements.txt

    echo "🚀 Starting Backend with Uvicorn..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload \
        > ../logs/backend.log 2>&1 &

    sleep 3

    if nc -z localhost "$BACKEND_PORT"; then
        echo "✅ Backend started successfully."
    else
        echo "❌ Failed to start backend. Check logs at logs/backend.log"
        exit 1
    fi
fi

echo "📡 You can now retry your request to: $BACKEND_URL"
