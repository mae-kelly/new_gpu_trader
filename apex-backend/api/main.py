from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanner.hyperscan import scanner
from brain.ai_predictor import predictor
from executor.trade_executor import executor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
                
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup():
    await scanner.init()
    await predictor.init()
    await executor.init()
    asyncio.create_task(broadcast_loop())

async def broadcast_loop():
    while True:
        try:
            buy_signals = await get_buy_signals()
            sell_signals = await get_sell_signals()
            stats = await get_system_stats()
            
            message = {
                'type': 'update',
                'timestamp': time.time(),
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'stats': stats
            }
            
            await manager.broadcast(message)
            await asyncio.sleep(0.5)
            
        except Exception as e:
            await asyncio.sleep(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/buy-signals")
async def api_buy_signals():
    return await get_buy_signals()

@app.get("/api/sell-signals") 
async def api_sell_signals():
    return await get_sell_signals()

@app.get("/api/stats")
async def api_stats():
    return await get_system_stats()

@app.get("/api/performance")
async def api_performance():
    return await executor.get_performance()

async def get_buy_signals():
    try:
        predictions = await predictor.get_top_predictions(20)
        signals = []
        
        for pred in predictions:
            signals.append({
                'address': pred.token_address,
                'symbol': f"TOKEN_{pred.token_address[:6]}",
                'current_price': pred.entry_price,
                'predicted_return': pred.expected_return,
                'confidence': pred.confidence,
                'urgency': min(int(pred.confidence * 10), 10),
                'risk_score': pred.risk_score,
                'social_score': pred.social_score,
                'technical_score': pred.technical_score,
                'whale_score': pred.whale_score,
                'target_price': pred.target_price,
                'time_horizon': pred.time_horizon
            })
            
        return signals
    except Exception as e:
        return []

async def get_sell_signals():
    try:
        positions = await executor.get_positions()
        signals = []
        
        for pos in positions:
            signals.append({
                'address': pos.token_address,
                'symbol': pos.symbol,
                'entry_price': pos.entry_price,
                'current_price': pos.current_price,
                'pnl_percent': pos.pnl_percent,
                'pnl_usd': pos.pnl_usd,
                'amount_usd': pos.amount_usd,
                'holding_time': int(time.time() - pos.entry_time),
                'stop_loss': pos.stop_loss,
                'take_profit': pos.take_profit,
                'status': pos.status
            })
            
        return signals
    except Exception as e:
        return []

async def get_system_stats():
    try:
        scanner_stats = await scanner.get_stats()
        performance = await executor.get_performance()
        
        return {
            'tokens_scanned': scanner_stats.get('tokens_scanned', 0),
            'scan_rate': scanner_stats.get('scan_rate', 0),
            'active_opportunities': scanner_stats.get('active_opportunities', 0),
            'current_balance': performance.get('current_balance', 10.0),
            'total_pnl': performance.get('total_pnl', 0.0),
            'win_rate': performance.get('win_rate', 0.0),
            'total_trades': performance.get('total_trades', 0),
            'uptime': scanner_stats.get('uptime_seconds', 0)
        }
    except Exception as e:
        return {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
