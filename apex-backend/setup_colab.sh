#!/bin/bash

pip install fastapi uvicorn websockets aiohttp aioredis pandas numpy asyncio web3 eth-account requests tweepy praw beautifulsoup4 textblob vadersentiment python-dotenv pydantic httpx ujson orjson python-multipart torch transformers sentence-transformers openai anthropic scikit-learn matplotlib plotly

pip install redis-py-cluster redis-sentinel

wget -q https://download.redis.io/redis-stable.tar.gz
tar xzf redis-stable.tar.gz
cd redis-stable
make
sudo make install
cd ..

redis-server --daemonize yes --port 6379 --maxmemory 1gb
