#!/bin/bash

echo "🧪 TESTING APEX SYSTEM"
echo "======================"

# Test Python
if python3 --version > /dev/null 2>&1; then
    echo "✅ Python 3 installed"
else
    echo "❌ Python 3 missing"
fi

# Test Node
if node --version > /dev/null 2>&1; then
    echo "✅ Node.js installed"
else
    echo "❌ Node.js missing"
fi

# Test Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis running"
else
    echo "❌ Redis not running"
fi

# Test files
if [ -f "core/api_server.py" ]; then
    echo "✅ API server exists"
else
    echo "❌ API server missing"
fi

if [ -f "engines/hyperscanner.py" ]; then
    echo "✅ HyperScanner exists"
else
    echo "❌ HyperScanner missing"
fi

if [ -f "frontend/package.json" ]; then
    echo "✅ Frontend exists"
else
    echo "❌ Frontend missing"
fi

echo ""
echo "🚀 Ready to launch: ./launch.sh"
