# APEX: $10 → $1000 Ultra-Aggressive Trading System

Production-ready backend for Google Colab deployment.

## Quick Start

1. Upload all files to Google Colab
2. Run setup: `!bash setup_colab.sh`
3. Set environment variables in the notebook
4. Run `main.ipynb` cells sequentially

## Components

- **HyperScanner**: Real-time token discovery across multiple DEXs
- **AI Predictor**: Social sentiment + whale tracking + technical analysis
- **Trade Executor**: Automated position management with risk controls
- **API Server**: WebSocket + REST endpoints for frontend

## Features

- Scans 1000+ tokens per second across 5+ chains
- AI-driven social sentiment analysis
- Whale wallet tracking and copy trading
- Automated risk management
- Real-time performance monitoring

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials.

## API Endpoints

- `ws://localhost:8000/ws` - WebSocket for real-time updates
- `GET /api/buy-signals` - Current buy opportunities
- `GET /api/sell-signals` - Active positions to sell
- `GET /api/stats` - System performance stats
- `GET /api/performance` - Trading performance metrics
