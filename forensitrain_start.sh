#!/usr/bin/env bash

set -e

echo "🚀 Starting ForensiTrain..."

# التحقق من وجود المتطلبات الأساسية
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is not installed"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is not installed"; exit 1; }

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# ---- Backend ----
cd "$SCRIPT_DIR/backend"

# إنشاء البيئة الافتراضية إذا لم تكن موجودة
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# تفعيل البيئة الافتراضية
source venv/bin/activate

# تحميل متغيرات البيئة
if [ -f .env ]; then
    echo "📦 Loading .env variables..."
    export $(grep -v '^#' .env | xargs) || true
fi

# التأكد من وجود uvicorn داخل البيئة
if ! pip show uvicorn >/dev/null 2>&1; then
    echo "📦 Installing uvicorn..."
    pip install --break-system-packages uvicorn
fi

# تثبيت المتطلبات
echo "📦 Installing Python dependencies..."
pip install --break-system-packages -r requirements.txt

# تشغيل الخادم
mkdir -p "$SCRIPT_DIR/logs"
echo "🚀 Starting backend on http://localhost:8000 ..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# ---- Frontend ----
cd "$SCRIPT_DIR/frontend"

# تثبيت حزم npm إذا لم تكن موجودة
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend packages..."
    npm install
fi

echo "🚀 Starting frontend on http://localhost:7000 ..."
npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# التعامل مع Ctrl+C لإيقاف الخدمات بشكل سليم
trap 'echo -e "\n🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit 0' INT TERM

wait $BACKEND_PID $FRONTEND_PID
echo "✅ ForensiTrain is running successfully!"
echo "🌐 Access the frontend at http://localhost:7000"