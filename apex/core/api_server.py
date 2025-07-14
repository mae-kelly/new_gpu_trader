from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import random

app = FastAPI(title="APEX Trading System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple storage
buy_signals = []
performance_data = {
    'system': {'tokens_scanned': 0, 'scan_rate': 1200},
    'trading': {'current_balance': 10.0, 'total_pnl': 0.0, 'win_rate': 0.0, 'total_trades': 0, 'active_positions': 0}
}

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
    print("🚀 APEX API Server Starting...")
    asyncio.create_task(simulation_loop())

async def simulation_loop():
    global buy_signals, performance_data
    
    while True:
        try:
            # Generate signals
            if random.random() < 0.3:
                signal = {
                    'address': f"0x{random.randint(100000, 999999):06x}" + "0" * 34,
                    'symbol': f"TOKEN{random.randint(1, 999)}",
                    'type': random.choice(['NEW_LISTING', 'MOMENTUM_BREAK', 'SOCIAL_PUMP']),
                    'confidence': random.uniform(0.85, 0.98),
                    'expected_return': random.uniform(0.3, 1.5),
                    'urgency': random.randint(6, 10),
                    'current_price': random.uniform(0.000001, 0.1),
                    'age_seconds': random.randint(5, 120),
                    'social_score': random.uniform(0.4, 0.9),
                    'whale_activity': random.uniform(0.3, 0.8)
                }
                buy_signals.append(signal)
                buy_signals = buy_signals[-8:]  # Keep last 8
                
                print(f"🎯 Signal: {signal['symbol']} ({signal['confidence']:.1%})")
            
            # Update performance
            performance_data['system']['tokens_scanned'] += random.randint(50, 200)
            performance_data['system']['scan_rate'] = random.randint(800, 1500)
            
            # Broadcast
            message = {
                'type': 'update',
                'timestamp': time.time(),
                'buy_signals': buy_signals,
                'sell_signals': [],
                'performance': performance_data
            }
            
            await manager.broadcast(message)
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)

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
    return buy_signals

@app.get("/api/sell-signals")
async def api_sell_signals():
    return []

@app.get("/api/performance")
async def api_performance():
    return performance_data

@app.get("/")
async def root():
    return {"status": "APEX Online", "signals": len(buy_signals)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
