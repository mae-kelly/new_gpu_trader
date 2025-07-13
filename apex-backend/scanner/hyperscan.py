import asyncio
import aiohttp
import aioredis
import json
import time
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

@dataclass
class Token:
    address: str
    symbol: str
    price: float
    change_1h: float
    change_5m: float
    volume_1h: float
    liquidity: float
    market_cap: float
    momentum: float
    confidence: float
    opportunity_type: str
    urgency: int
    detected_at: float
    expected_return: float

class HyperScanner:
    def __init__(self):
        self.redis = None
        self.sessions = {}
        self.opportunities = {}
        self.stats = {'scanned': 0, 'found': 0, 'start': time.time()}
        
    async def init(self):
        try:
            self.redis = aioredis.from_url("redis://localhost:6379")
            await self.redis.ping()
        except:
            pass
            
        timeout = aiohttp.ClientTimeout(total=2)
        connector = aiohttp.TCPConnector(limit=100, keepalive_timeout=30)
        
        self.sessions['dex'] = aiohttp.ClientSession(connector=connector, timeout=timeout)
        self.sessions['tools'] = aiohttp.ClientSession(connector=connector, timeout=timeout)
        self.sessions['gecko'] = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        asyncio.create_task(self.scan_dexscreener())
        asyncio.create_task(self.scan_dextools())
        asyncio.create_task(self.scan_geckoterminal())
        asyncio.create_task(self.cleanup_loop())
        
    async def scan_dexscreener(self):
        chains = ['ethereum', 'bsc', 'polygon', 'arbitrum', 'base', 'solana']
        while True:
            try:
                for chain in chains:
                    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}"
                    async with self.sessions['dex'].get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            await self.process_dexscreener(data, chain)
                await asyncio.sleep(0.1)
            except Exception as e:
                await asyncio.sleep(1)
                
    async def scan_dextools(self):
        chains = ['ether', 'bsc', 'polygon']
        while True:
            try:
                for chain in chains:
                    url = f"https://api.dextools.io/v1/pairs/{chain}"
                    async with self.sessions['tools'].get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            await self.process_dextools(data, chain)
                await asyncio.sleep(0.2)
            except Exception as e:
                await asyncio.sleep(2)
                
    async def scan_geckoterminal(self):
        networks = ['eth', 'bsc', 'polygon_pos', 'arbitrum_one']
        while True:
            try:
                for network in networks:
                    url = f"https://api.geckoterminal.com/api/v2/networks/{network}/trending_pools"
                    async with self.sessions['gecko'].get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            await self.process_geckoterminal(data, network)
                await asyncio.sleep(0.5)
            except Exception as e:
                await asyncio.sleep(3)
                
    async def process_dexscreener(self, data, chain):
        if 'pairs' not in data:
            return
            
        current_time = time.time()
        for pair in data['pairs']:
            try:
                base_token = pair.get('baseToken', {})
                address = base_token.get('address', '').lower()
                if not address:
                    continue
                    
                price = float(pair.get('priceUsd', 0))
                if price <= 0:
                    continue
                    
                change_1h = float(pair.get('priceChange', {}).get('h1', 0))
                volume_1h = float(pair.get('volume', {}).get('h1', 0))
                liquidity = float(pair.get('liquidity', {}).get('usd', 0))
                market_cap = float(pair.get('marketCap', 0))
                
                pair_created = pair.get('pairCreatedAt', 0)
                is_new = pair_created and (current_time - pair_created/1000) < 3600
                
                change_5m = self.estimate_5m_change(change_1h, volume_1h)
                momentum = self.calc_momentum(change_1h, change_5m, volume_1h, liquidity)
                
                if is_new and volume_1h > 5000 and liquidity > 10000:
                    token = self.create_new_listing_token(pair, momentum, current_time)
                    if token:
                        await self.cache_token(token)
                        
                elif change_5m > 15 and volume_1h > 10000 and liquidity > 25000:
                    token = self.create_momentum_token(pair, momentum, change_5m, current_time)
                    if token:
                        await self.cache_token(token)
                        
                self.stats['scanned'] += 1
                
            except Exception as e:
                continue
                
    async def process_dextools(self, data, chain):
        if 'data' not in data:
            return
            
        current_time = time.time()
        for item in data['data']:
            try:
                address = item.get('id', '').lower()
                if not address:
                    continue
                    
                price = float(item.get('price', 0))
                change_1h = float(item.get('variation1h', 0))
                volume = float(item.get('volume', 0))
                liquidity = float(item.get('liquidity', 0))
                
                if change_1h > 20 and volume > 15000:
                    momentum = min((change_1h / 50) * (volume / 50000), 1.0)
                    confidence = min(momentum * 0.8 + (liquidity / 100000) * 0.2, 0.95)
                    
                    if confidence > 0.7:
                        token = Token(
                            address=address,
                            symbol=item.get('symbol', 'UNKNOWN'),
                            price=price,
                            change_1h=change_1h,
                            change_5m=change_1h / 12,
                            volume_1h=volume,
                            liquidity=liquidity,
                            market_cap=float(item.get('mcap', 0)),
                            momentum=momentum,
                            confidence=confidence,
                            opportunity_type='DEXTOOLS_MOMENTUM',
                            urgency=min(int(momentum * 10), 10),
                            detected_at=current_time,
                            expected_return=min(change_1h / 20, 2.0)
                        )
                        await self.cache_token(token)
                        
            except Exception as e:
                continue
                
    async def process_geckoterminal(self, data, network):
        if 'data' not in data:
            return
            
        current_time = time.time()
        for pool in data['data']:
            try:
                attrs = pool.get('attributes', {})
                base_token = attrs.get('base_token_price_usd')
                if not base_token:
                    continue
                    
                address = pool.get('relationships', {}).get('base_token', {}).get('data', {}).get('id', '').lower()
                if not address:
                    continue
                    
                price_change_24h = float(attrs.get('price_change_percentage', {}).get('h24', 0))
                volume_24h = float(attrs.get('volume_usd', {}).get('h24', 0))
                
                if abs(price_change_24h) > 30 and volume_24h > 20000:
                    momentum = min(abs(price_change_24h) / 100, 1.0)
                    confidence = min(momentum * 0.7 + (volume_24h / 100000) * 0.3, 0.9)
                    
                    if confidence > 0.75:
                        token = Token(
                            address=address,
                            symbol=attrs.get('name', 'UNKNOWN'),
                            price=float(base_token),
                            change_1h=price_change_24h / 24,
                            change_5m=price_change_24h / 288,
                            volume_1h=volume_24h / 24,
                            liquidity=float(attrs.get('reserve_in_usd', 0)),
                            market_cap=0,
                            momentum=momentum,
                            confidence=confidence,
                            opportunity_type='GECKO_TRENDING',
                            urgency=min(int(momentum * 10), 10),
                            detected_at=current_time,
                            expected_return=min(abs(price_change_24h) / 50, 1.5)
                        )
                        await self.cache_token(token)
                        
            except Exception as e:
                continue
                
    def estimate_5m_change(self, change_1h, volume_1h):
        if change_1h == 0:
            return 0
        volume_factor = min(volume_1h / 10000, 3.0)
        return change_1h * volume_factor / 12
        
    def calc_momentum(self, change_1h, change_5m, volume_1h, liquidity):
        price_momentum = abs(change_5m) / 20
        volume_momentum = min(volume_1h / 50000, 1.0)
        liquidity_factor = min(liquidity / 100000, 1.0)
        return min(price_momentum * 0.5 + volume_momentum * 0.3 + liquidity_factor * 0.2, 1.0)
        
    def create_new_listing_token(self, pair, momentum, timestamp):
        base_token = pair.get('baseToken', {})
        address = base_token.get('address', '').lower()
        
        volume_1h = float(pair.get('volume', {}).get('h1', 0))
        liquidity = float(pair.get('liquidity', {}).get('usd', 0))
        
        confidence = min(momentum * 0.7 + (liquidity / 100000) * 0.3, 0.95)
        expected_return = min(volume_1h / liquidity, 5.0) if liquidity > 0 else 0
        
        return Token(
            address=address,
            symbol=base_token.get('symbol', 'UNKNOWN'),
            price=float(pair.get('priceUsd', 0)),
            change_1h=float(pair.get('priceChange', {}).get('h1', 0)),
            change_5m=0,
            volume_1h=volume_1h,
            liquidity=liquidity,
            market_cap=float(pair.get('marketCap', 0)),
            momentum=momentum,
            confidence=confidence,
            opportunity_type='NEW_LISTING',
            urgency=min(int(confidence * 10), 10),
            detected_at=timestamp,
            expected_return=expected_return
        )
        
    def create_momentum_token(self, pair, momentum, change_5m, timestamp):
        base_token = pair.get('baseToken', {})
        address = base_token.get('address', '').lower()
        
        liquidity = float(pair.get('liquidity', {}).get('usd', 0))
        confidence = min(momentum * 0.8 + (liquidity / 200000) * 0.2, 0.9)
        expected_return = min(change_5m / 10, 3.0)
        
        return Token(
            address=address,
            symbol=base_token.get('symbol', 'UNKNOWN'),
            price=float(pair.get('priceUsd', 0)),
            change_1h=float(pair.get('priceChange', {}).get('h1', 0)),
            change_5m=change_5m,
            volume_1h=float(pair.get('volume', {}).get('h1', 0)),
            liquidity=liquidity,
            market_cap=float(pair.get('marketCap', 0)),
            momentum=momentum,
            confidence=confidence,
            opportunity_type='MOMENTUM_BREAK',
            urgency=min(int(momentum * 10), 10),
            detected_at=timestamp,
            expected_return=expected_return
        )
        
    async def cache_token(self, token):
        try:
            self.opportunities[token.address] = token
            self.stats['found'] += 1
            
            if self.redis:
                await self.redis.setex(
                    f"token:{token.address}",
                    300,
                    json.dumps(asdict(token))
                )
                
            print(f"🎯 {token.opportunity_type}: {token.symbol} ({token.confidence:.2f} confidence)")
            
        except Exception as e:
            pass
            
    async def cleanup_loop(self):
        while True:
            try:
                current_time = time.time()
                expired = []
                
                for address, token in self.opportunities.items():
                    if current_time - token.detected_at > 900:
                        expired.append(address)
                        
                for address in expired:
                    del self.opportunities[address]
                    if self.redis:
                        await self.redis.delete(f"token:{address}")
                        
                await asyncio.sleep(60)
                
            except Exception as e:
                await asyncio.sleep(30)
                
    async def get_top_opportunities(self, limit=20):
        opportunities = list(self.opportunities.values())
        opportunities.sort(
            key=lambda x: x.confidence * x.expected_return * (x.urgency / 10),
            reverse=True
        )
        return opportunities[:limit]
        
    async def get_stats(self):
        uptime = time.time() - self.stats['start']
        return {
            'tokens_scanned': self.stats['scanned'],
            'opportunities_found': self.stats['found'],
            'active_opportunities': len(self.opportunities),
            'scan_rate': self.stats['scanned'] / uptime if uptime > 0 else 0,
            'uptime_seconds': uptime
        }

scanner = HyperScanner()
