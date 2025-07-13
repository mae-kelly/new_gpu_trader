import asyncio
import aiohttp
import aioredis
import json
import time
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import re
from textblob import TextBlob

@dataclass
class Prediction:
    token_address: str
    action: str
    confidence: float
    expected_return: float
    time_horizon: int
    risk_score: float
    entry_price: float
    target_price: float
    stop_loss: float
    social_score: float
    technical_score: float
    whale_score: float
    timestamp: float

class AIPredictor:
    def __init__(self):
        self.redis = None
        self.sessions = {}
        self.whale_wallets = {
            '0x742d35Cc6aB8C4532': 0.78,
            '0x8ba1f109551bD432803012645Hac136c': 0.82,
            '0x267be1C1D684F78cb4F6a176C4911b741E4Ffdc0': 0.71,
            '0x40ec5B33f54e0E8A33A975908C5BA1c14e5BbbDf': 0.85
        }
        self.predictions = {}
        
    async def init(self):
        try:
            self.redis = aioredis.from_url("redis://localhost:6379")
            await self.redis.ping()
        except:
            pass
            
        timeout = aiohttp.ClientTimeout(total=3)
        self.sessions['social'] = aiohttp.ClientSession(timeout=timeout)
        self.sessions['whale'] = aiohttp.ClientSession(timeout=timeout)
        
        asyncio.create_task(self.social_monitor())
        asyncio.create_task(self.whale_monitor())
        asyncio.create_task(self.prediction_loop())
        
    async def social_monitor(self):
        while True:
            try:
                await self.scan_twitter()
                await self.scan_reddit()
                await asyncio.sleep(30)
            except Exception as e:
                await asyncio.sleep(60)
                
    async def scan_twitter(self):
        try:
            search_terms = ['crypto', 'memecoin', 'gem', 'moonshot', 'pump']
            for term in search_terms:
                await self.process_twitter_data(term)
        except Exception as e:
            pass
            
    async def process_twitter_data(self, term):
        try:
            url = f"https://api.twitter.com/2/tweets/search/recent?query={term} crypto&max_results=100"
            headers = {'Authorization': 'Bearer YOUR_TWITTER_BEARER_TOKEN'}
            
            async with self.sessions['social'].get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for tweet in data.get('data', []):
                        await self.analyze_tweet(tweet)
        except Exception as e:
            pass
            
    async def analyze_tweet(self, tweet):
        try:
            text = tweet.get('text', '')
            tokens = self.extract_tokens(text)
            sentiment = self.analyze_sentiment(text)
            
            for token in tokens:
                await self.update_social_score(token, sentiment, 'twitter')
        except Exception as e:
            pass
            
    async def scan_reddit(self):
        try:
            subreddits = ['CryptoMoonShots', 'cryptocurrency', 'defi', 'ethtrader']
            for subreddit in subreddits:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=50"
                
                async with self.sessions['social'].get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        posts = data.get('data', {}).get('children', [])
                        for post in posts:
                            await self.analyze_reddit_post(post['data'])
        except Exception as e:
            pass
            
    async def analyze_reddit_post(self, post):
        try:
            title = post.get('title', '')
            score = post.get('score', 0)
            
            tokens = self.extract_tokens(title)
            sentiment = self.analyze_sentiment(title)
            
            weighted_sentiment = sentiment * min(score / 100, 5)
            
            for token in tokens:
                await self.update_social_score(token, weighted_sentiment, 'reddit')
        except Exception as e:
            pass
            
    def extract_tokens(self, text):
        pattern = r'\$([A-Z]{3,10})'
        matches = re.findall(pattern, text.upper())
        return matches
        
    def analyze_sentiment(self, text):
        try:
            blob = TextBlob(text)
            sentiment = (blob.sentiment.polarity + 1) / 2
            
            positive_words = ['moon', 'rocket', 'gem', 'pump', 'bullish', 'hodl', 'diamond', 'ape']
            negative_words = ['dump', 'crash', 'bearish', 'sell', 'exit', 'rug', 'scam']
            
            text_lower = text.lower()
            for word in positive_words:
                if word in text_lower:
                    sentiment = min(sentiment + 0.15, 1.0)
                    
            for word in negative_words:
                if word in text_lower:
                    sentiment = max(sentiment - 0.15, 0.0)
                    
            return sentiment
        except:
            return 0.5
            
    async def update_social_score(self, token, sentiment, source):
        try:
            if self.redis:
                key = f"social:{token}"
                existing = await self.redis.get(key)
                
                if existing:
                    data = json.loads(existing)
                else:
                    data = {
                        'twitter_sentiment': 0.5,
                        'reddit_sentiment': 0.5,
                        'mention_count': 0,
                        'last_updated': time.time()
                    }
                
                data[f'{source}_sentiment'] = sentiment
                data['mention_count'] += 1
                data['last_updated'] = time.time()
                
                overall = data['twitter_sentiment'] * 0.6 + data['reddit_sentiment'] * 0.4
                data['overall_sentiment'] = overall
                
                await self.redis.setex(key, 1800, json.dumps(data))
        except Exception as e:
            pass
            
    async def whale_monitor(self):
        while True:
            try:
                for wallet in self.whale_wallets:
                    await self.track_whale_wallet(wallet)
                await asyncio.sleep(60)
            except Exception as e:
                await asyncio.sleep(120)
                
    async def track_whale_wallet(self, wallet):
        try:
            url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet}&sort=desc&page=1&offset=10"
            
            async with self.sessions['whale'].get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for tx in data.get('result', []):
                        await self.analyze_whale_tx(tx, wallet)
        except Exception as e:
            pass
            
    async def analyze_whale_tx(self, tx, wallet):
        try:
            value = int(tx.get('value', 0))
            if value > 1000000000000000000:
                to_address = tx.get('to', '').lower()
                
                whale_score = self.whale_wallets.get(wallet, 0.5)
                
                if self.redis:
                    await self.redis.setex(
                        f"whale:{to_address}",
                        3600,
                        json.dumps({
                            'whale_wallet': wallet,
                            'success_rate': whale_score,
                            'transaction_value': value,
                            'timestamp': time.time()
                        })
                    )
        except Exception as e:
            pass
            
    async def prediction_loop(self):
        while True:
            try:
                if self.redis:
                    keys = await self.redis.keys("token:*")
                    for key in keys:
                        token_data = await self.redis.get(key)
                        if token_data:
                            token = json.loads(token_data)
                            prediction = await self.generate_prediction(token)
                            if prediction:
                                await self.cache_prediction(prediction)
                                
                await asyncio.sleep(5)
            except Exception as e:
                await asyncio.sleep(10)
                
    async def generate_prediction(self, token):
        try:
            address = token['address']
            
            social_data = await self.get_social_data(address)
            whale_data = await self.get_whale_data(address)
            technical_score = self.calc_technical_score(token)
            
            social_score = social_data.get('overall_sentiment', 0.5)
            whale_score = whale_data.get('success_rate', 0.5) if whale_data else 0.5
            
            combined_confidence = (
                technical_score * 0.4 +
                social_score * 0.3 +
                whale_score * 0.3
            )
            
            if combined_confidence < 0.7:
                return None
                
            entry_price = token['price']
            expected_return = token['expected_return']
            
            target_price = entry_price * (1 + expected_return)
            stop_loss = entry_price * 0.8
            
            risk_score = 1 - combined_confidence
            time_horizon = min(int(3600 / token['urgency']), 3600)
            
            action = 'BUY' if combined_confidence > 0.75 else 'HOLD'
            
            return Prediction(
                token_address=address,
                action=action,
                confidence=combined_confidence,
                expected_return=expected_return,
                time_horizon=time_horizon,
                risk_score=risk_score,
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                social_score=social_score,
                technical_score=technical_score,
                whale_score=whale_score,
                timestamp=time.time()
            )
            
        except Exception as e:
            return None
            
    async def get_social_data(self, address):
        try:
            if self.redis:
                data = await self.redis.get(f"social:{address}")
                return json.loads(data) if data else {}
            return {}
        except:
            return {}
            
    async def get_whale_data(self, address):
        try:
            if self.redis:
                data = await self.redis.get(f"whale:{address}")
                return json.loads(data) if data else None
            return None
        except:
            return None
            
    def calc_technical_score(self, token):
        try:
            momentum = token.get('momentum', 0)
            confidence = token.get('confidence', 0)
            urgency = token.get('urgency', 0) / 10
            
            volume_score = min(token.get('volume_1h', 0) / 50000, 1.0)
            liquidity_score = min(token.get('liquidity', 0) / 100000, 1.0)
            
            return (momentum * 0.3 + confidence * 0.3 + urgency * 0.2 + 
                   volume_score * 0.1 + liquidity_score * 0.1)
        except:
            return 0.5
            
    async def cache_prediction(self, prediction):
        try:
            self.predictions[prediction.token_address] = prediction
            
            if self.redis:
                await self.redis.setex(
                    f"prediction:{prediction.token_address}",
                    600,
                    json.dumps(asdict(prediction))
                )
        except Exception as e:
            pass
            
    async def get_top_predictions(self, limit=10):
        predictions = list(self.predictions.values())
        predictions.sort(
            key=lambda x: x.confidence * x.expected_return,
            reverse=True
        )
        return [p for p in predictions[:limit] if p.action == 'BUY']

predictor = AIPredictor()
