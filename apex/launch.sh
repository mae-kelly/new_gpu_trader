#!/bin/bash

echo "🚀 LAUNCHING APEX"
echo "================="

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Kill existing processes
pkill -f "python.*api_server.py" 2>/dev/null
pkill -f "npm.*dev" 2>/dev/null
sleep 2

echo "📡 Starting backend..."
cd core
python3 api_server.py &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend..."
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ Backend ready"
        break
    fi
    sleep 1
done

echo "🌐 Starting frontend..."
cd frontend

# Install if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing..."
    npm install --silent
fi

npm run dev &
FRONTEND_PID=$!
cd ..

echo "⏳ Waiting for frontend..."
sleep 5

echo ""
echo "🎉 APEX LAUNCHED!"
echo "================="
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 API: http://localhost:8000"
echo ""
echo "⚡ Press Ctrl+C to stop"

# Auto-open browser
if command -v open > /dev/null 2>&1; then
    sleep 2
    open http://localhost:3000
fi

cleanup() {
    echo "🛑 Stopping APEX..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM
wait
