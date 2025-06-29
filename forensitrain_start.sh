#!/usr/bin/env bash

set -e

echo "🚀 Starting ForensiTrain..."

# التحقق من المتطلبات
for cmd in python3 pip npm cmake; do
  if ! command -v $cmd &> /dev/null; then
    echo "❌ $cmd is not installed. Please install it first."
    exit 1
  fi
done

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# ---- Backend ----
cd "$SCRIPT_DIR/backend"

# إنشاء وتفعيل بيئة venv
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

# تحديث pip
pip install --upgrade pip

# تثبيت الحزم الأساسية المطلوبة لبناء dlib
echo "📦 Installing system dependencies for dlib..."
sudo apt update
sudo apt install -y build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev

# تثبيت dlib بدون دعم GUI (لحل مشاكل التوافق)
if ! pip show dlib &>/dev/null; then
    echo "📦 Installing dlib..."
    pip install dlib --config-settings=--define="DLIB_NO_GUI_SUPPORT=1"
fi

# تثبيت face_recognition_models يدويًا (مطلوب)
if ! pip show face_recognition_models &>/dev/null; then
    echo "📦 Installing face_recognition_models..."
    pip install git+https://github.com/ageitgey/face_recognition_models
fi

# تثبيت بقية المتطلبات
echo "📦 Installing backend requirements..."
pip install -r requirements.txt

# تحميل متغيرات .env إن وجدت
if [ -f .env ]; then
    echo "📦 Loading .env variables..."
    export $(grep -v '^#' .env | xargs) || true
fi

# تشغيل الـ backend
mkdir -p "$SCRIPT_DIR/logs"
echo "🚀 Starting backend on http://localhost:8000 ..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# ---- Frontend ----
cd "$SCRIPT_DIR/frontend"

# تثبيت حزم npm
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend packages..."
    npm install
fi

echo "🚀 Starting frontend on http://localhost:7000 ..."
npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# التعامل مع الإنهاء
trap 'echo -e "\n🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit 0' INT TERM

echo ""
echo "✅ ForensiTrain is running!"
echo "➜  Frontend: http://localhost:7000/"
echo "➜  Backend (docs): http://localhost:8000/docs"

wait $BACKEND_PID $FRONTEND_PID
