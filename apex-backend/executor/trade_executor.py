import asyncio
import aioredis
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from web3 import Web3
import os

@dataclass
class Position:
    token_address: str
    symbol: str
    entry_price: float
    current_price: float
    amount_usd: float
    entry_time: float
    stop_loss: float
    take_profit: float
    pnl_percent: float
    pnl_usd: float
    status: str

@dataclass
class Trade:
    token_address: str
    action: str
    amount_usd: float
    price: float
    timestamp: float
    tx_hash: str
    status: str

class TradeExecutor:
    def __init__(self):
        self.redis = None
        self.w3 = None
        self.account = None
        self.positions = {}
        self.trade_history = []
        self.balance = 10.0
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'current_balance': 10.0
        }
        
        self.risk_params = {
            'max_position_size': 0.3,
            'stop_loss_pct': 0.25,
            'take_profit_pct': 2.0,
            'max_positions': 3,
            'max_holding_time': 1800
        }
        
    async def init(self):
        try:
            self.redis = aioredis.from_url("redis://localhost:6379")
            await self.redis.ping()
        except:
            pass
            
        rpc_url = os.getenv('RPC_URL', 'https://rpc.ankr.com/polygon')
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        private_key = os.getenv('PRIVATE_KEY')
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            
        asyncio.create_task(self.execution_loop())
        asyncio.create_task(self.position_monitor())
        
    async def execution_loop(self):
        while True:
            try:
                if self.redis:
                    prediction_keys = await self.redis.keys("prediction:*")
                    
                    for key in prediction_keys:
                        prediction_data = await self.redis.get(key)
                        if prediction_data:
                            prediction = json.loads(prediction_data)
                            
                            if prediction['action'] == 'BUY':
                                await self.evaluate_buy_signal(prediction)
                                
                await asyncio.sleep(1)
                
            except Exception as e:
                await asyncio.sleep(5)
                
    async def evaluate_buy_signal(self, prediction):
        try:
            token_address = prediction['token_address']
            
            if token_address in self.positions:
                return
                
            if len(self.positions) >= self.risk_params['max_positions']:
                return
                
            if prediction['confidence'] < 0.8:
                return
                
            if prediction['expected_return'] < 0.2:
                return
                
            if prediction['risk_score'] > 0.4:
                return
                
            position_size = self.calculate_position_size(prediction)
            if position_size < 1.0:
                return
                
            safety_check = await self.verify_token_safety(token_address)
            if not safety_check:
                return
                
            await self.execute_buy(prediction, position_size)
            
        except Exception as e:
            pass
            
    def calculate_position_size(self, prediction):
        base_size = self.balance * self.risk_params['max_position_size']
        
        confidence_mult = prediction['confidence']
        return_mult = min(prediction['expected_return'], 2.0)
        risk_div = max(prediction['risk_score'], 0.1)
        
        position_size = (base_size * confidence_mult * return_mult) / risk_div
        return min(position_size, base_size)
        
    async def verify_token_safety(self, token_address):
        try:
            honeypot_url = f"https://api.honeypot.is/v2/IsHoneypot?address={token_address}"
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(honeypot_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return not data.get('IsHoneypot', True)
            return False
        except:
            return False
            
    async def execute_buy(self, prediction, amount_usd):
        try:
            token_address = prediction['token_address']
            entry_price = prediction['entry_price']
            
            tx_hash = await self.simulate_buy_transaction(token_address, amount_usd, entry_price)
            
            if tx_hash:
                position = Position(
                    token_address=token_address,
                    symbol=f"TOKEN_{token_address[:6]}",
                    entry_price=entry_price,
                    current_price=entry_price,
                    amount_usd=amount_usd,
                    entry_time=time.time(),
                    stop_loss=entry_price * (1 - self.risk_params['stop_loss_pct']),
                    take_profit=entry_price * (1 + self.risk_params['take_profit_pct']),
                    pnl_percent=0.0,
                    pnl_usd=0.0,
                    status='OPEN'
                )
                
                self.positions[token_address] = position
                self.balance -= amount_usd
                self.performance['current_balance'] = self.balance
                
                trade = Trade(
                    token_address=token_address,
                    action='BUY',
                    amount_usd=amount_usd,
                    price=entry_price,
                    timestamp=time.time(),
                    tx_hash=tx_hash,
                    status='EXECUTED'
                )
                
                self.trade_history.append(trade)
                self.performance['total_trades'] += 1
                
                if self.redis:
                    await self.redis.setex(
                        f"position:{token_address}",
                        3600,
                        json.dumps(asdict(position))
                    )
                    
                print(f"✅ BUY: {position.symbol} at ${entry_price} (${amount_usd})")
                
        except Exception as e:
            print(f"❌ Buy execution failed: {e}")
            
    async def simulate_buy_transaction(self, token_address, amount_usd, price):
        await asyncio.sleep(0.1)
        return f"0x{''.join([f'{i:02x}' for i in range(32)])}"
        
    async def position_monitor(self):
        while True:
            try:
                for token_address, position in list(self.positions.items()):
                    await self.update_position_price(position)
                    
                    should_exit, reason = self.should_exit_position(position)
                    if should_exit:
                        await self.execute_sell(position, reason)
                        
                await asyncio.sleep(5)
                
            except Exception as e:
                await asyncio.sleep(10)
                
    async def update_position_price(self, position):
        try:
            if self.redis:
                token_data = await self.redis.get(f"token:{position.token_address}")
                if token_data:
                    token = json.loads(token_data)
                    current_price = token['price']
                    
                    position.current_price = current_price
                    position.pnl_percent = ((current_price - position.entry_price) / position.entry_price) * 100
                    position.pnl_usd = position.amount_usd * (position.pnl_percent / 100)
                    
        except Exception as e:
            pass
            
    def should_exit_position(self, position):
        if position.current_price <= position.stop_loss:
            return True, "STOP_LOSS"
            
        if position.current_price >= position.take_profit:
            return True, "TAKE_PROFIT"
            
        holding_time = time.time() - position.entry_time
        if holding_time > self.risk_params['max_holding_time']:
            return True, "TIME_LIMIT"
            
        return False, "HOLDING"
        
    async def execute_sell(self, position, reason):
        try:
            tx_hash = await self.simulate_sell_transaction(
                position.token_address, 
                position.amount_usd, 
                position.current_price
            )
            
            if tx_hash:
                exit_amount = position.amount_usd + position.pnl_usd
                self.balance += exit_amount
                self.performance['current_balance'] = self.balance
                
                self.performance['total_pnl'] += position.pnl_usd
                
                if position.pnl_usd > 0:
                    self.performance['winning_trades'] += 1
                    
                self.performance['best_trade'] = max(self.performance['best_trade'], position.pnl_usd)
                self.performance['worst_trade'] = min(self.performance['worst_trade'], position.pnl_usd)
                
                trade = Trade(
                    token_address=position.token_address,
                    action='SELL',
                    amount_usd=exit_amount,
                    price=position.current_price,
                    timestamp=time.time(),
                    tx_hash=tx_hash,
                    status='EXECUTED'
                )
                
                self.trade_history.append(trade)
                position.status = 'CLOSED'
                
                print(f"✅ SELL: {position.symbol} at ${position.current_price} "
                      f"({position.pnl_percent:+.1f}% / ${position.pnl_usd:+.2f}) - {reason}")
                
                del self.positions[position.token_address]
                
                if self.redis:
                    await self.redis.delete(f"position:{position.token_address}")
                    
        except Exception as e:
            print(f"❌ Sell execution failed: {e}")
            
    async def simulate_sell_transaction(self, token_address, amount_usd, price):
        await asyncio.sleep(0.1)
        return f"0x{''.join([f'{i:02x}' for i in range(32)])}"
        
    async def get_positions(self):
        return list(self.positions.values())
        
    async def get_performance(self):
        total_trades = self.performance['total_trades']
        win_rate = (self.performance['winning_trades'] / total_trades * 100) if total_trades > 0 else 0
        
        return {
            **self.performance,
            'win_rate': win_rate,
            'positions_count': len(self.positions),
            'available_balance': self.balance
        }

executor = TradeExecutor()
