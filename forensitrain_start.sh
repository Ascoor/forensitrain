#!/usr/bin/env bash

set -e

echo "🚀 Starting ForensiTrain..."

# --------🔍 تحقق من الأدوات المطلوبة ----------
PYTHON_BIN=${PYTHON_BIN:-python3.12}

REQUIRED_CMDS=("$PYTHON_BIN" pip npm cmake)
for cmd in "${REQUIRED_CMDS[@]}"; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "❌ Missing required command: $cmd"
    exit 1
  fi
done

# --------📦 إنشاء بيئة Python افتراضية --------
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR/backend"

if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  "$PYTHON_BIN" -m venv venv
fi

source venv/bin/activate

# --------🔁 تحديث pip وتثبيت المتطلبات --------
echo "📦 Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing system dependencies for dlib..."
sudo apt update
sudo apt install -y build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev

if ! pip show dlib &>/dev/null; then
  echo "📦 Installing dlib (no GUI)..."
  pip install dlib --config-settings=--define="DLIB_NO_GUI_SUPPORT=1"
fi

if ! pip show face_recognition_models &>/dev/null; then
  echo "📦 Installing face_recognition_models..."
  pip install git+https://github.com/ageitgey/face_recognition_models
fi

echo "📦 Installing backend requirements..."
pip install -r requirements.txt

if [ -f .env ]; then
  echo "📦 Loading environment variables from .env..."
  export $(grep -v '^#' .env | xargs) || true
fi

# --------🚀 تشغيل الـ Backend --------
mkdir -p "$SCRIPT_DIR/logs"
echo "🚀 Starting backend at http://localhost:8000 ..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
BACKEND_PID=$!

# --------🧩 تشغيل الـ Frontend --------
cd "$SCRIPT_DIR/frontend"

if [ ! -d "node_modules" ]; then
  echo "📦 Installing frontend packages..."
  npm install
fi

echo "🚀 Starting frontend at http://localhost:7000 ..."
npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!

cd "$SCRIPT_DIR"

# --------🛑 التعامل مع إيقاف السكريبت --------
trap 'echo -e "\n🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit 0' INT TERM

echo ""
echo "✅ ForensiTrain is running successfully!"
echo "🌐 Frontend: http://localhost:7000"
echo "🛠️  Backend API (Docs): http://localhost:8000/docs"

wait $BACKEND_PID $FRONTEND_PID
