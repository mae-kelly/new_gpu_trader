#!/bin/bash
set -e

echo "🌌 INITIALIZING APEX CORE SYSTEMS..."

# Install Python dependencies
pip3 install --upgrade pip wheel setuptools
pip3 install fastapi uvicorn websockets aiohttp aioredis
pip3 install numpy pandas torch transformers
pip3 install web3 eth-account requests tweepy praw
pip3 install asyncio aiofiles orjson ujson
pip3 install textblob vadersentiment scikit-learn
pip3 install python-dotenv pydantic httpx nest-asyncio

# Start Redis for microsecond caching
if command -v redis-server &> /dev/null; then
    redis-server --daemonize yes --port 6379 --maxmemory 2gb --maxmemory-policy allkeys-lru
    echo "✅ Redis started"
else
    echo "⚠️ Redis not found - install with: brew install redis"
fi

echo "✅ APEX dependencies installed"
