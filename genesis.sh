#!/bin/bash
set -e

echo "🌌 INITIALIZING APEX CORE SYSTEMS..."
echo "===================================="

# Check if we're on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "📦 Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install Python and Node.js via Homebrew
    echo "📦 Installing Python and Node.js..."
    brew install python@3.11 node redis || echo "Some packages may already be installed"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux"
    
    # Update package manager
    sudo apt update
    
    # Install Python, Node.js, and Redis
    echo "📦 Installing Python, Node.js, and Redis..."
    sudo apt install -y python3.11 python3-pip nodejs npm redis-server
fi

echo ""
echo "🐍 Installing Python dependencies..."

# Upgrade pip first
python3 -m pip install --upgrade pip wheel setuptools

# Core web framework dependencies
python3 -m pip install fastapi uvicorn websockets aiohttp aioredis

# Data processing and ML
python3 -m pip install numpy pandas torch transformers

# Blockchain and crypto
python3 -m pip install web3 eth-account requests

# Social media APIs
python3 -m pip install tweepy praw beautifulsoup4

# Text processing and sentiment analysis
python3 -m pip install textblob vadersentiment scikit-learn

# Utility libraries
python3 -m pip install asyncio aiofiles orjson ujson python-dotenv pydantic httpx nest-asyncio

echo ""
echo "🔴 Starting Redis server..."
if command -v redis-server &> /dev/null; then
    # Start Redis in the background
    redis-server --daemonize yes --port 6379 --maxmemory 2gb --maxmemory-policy allkeys-lru
    sleep 2
    
    # Test Redis connection
    if redis-cli ping | grep -q "PONG"; then
        echo "✅ Redis started successfully"
    else
        echo "⚠️ Redis may not be running properly"
    fi
else
    echo "⚠️ Redis not found. Install with:"
    echo "   macOS: brew install redis"
    echo "   Linux: sudo apt install redis-server"
fi

echo ""
echo "📦 Installing frontend dependencies..."
cd frontend

# Install Node.js dependencies
if [ -f "package.json" ]; then
    npm install --silent
    echo "✅ Frontend dependencies installed"
else
    echo "❌ package.json not found in frontend directory"
fi

cd ..

echo ""
echo "✅ APEX DEPENDENCIES INSTALLATION COMPLETE!"
echo "==========================================="
echo ""
echo "🎯 What was installed:"
echo "   • Python 3.11+ with FastAPI, WebSockets, ML libraries"
echo "   • Node.js with Next.js and React"
echo "   • Redis for ultra-fast caching"
echo "   • Crypto and blockchain libraries"
echo "   • Social media APIs for sentiment analysis"
echo ""
echo "🚀 Next step: ./test_apex.sh"
