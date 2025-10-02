import ccxt
import pandas as pd
from datetime import datetime
from typing import List, Dict
import asyncio

class PriceService:
    def __init__(self, exchange_id: str = "binance"):
        self.exchange_id = exchange_id
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # Use perpetual futures
            }
        })
    
    async def get_current_price(self, symbol: str) -> Dict:
        """Fetch current price for a symbol"""
        try:
            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
            return {
                "symbol": symbol,
                "price": ticker['last'],
                "timestamp": datetime.now().isoformat(),
                "change_24h": ticker.get('percentage'),
                "volume_24h": ticker.get('quoteVolume'),
                "high_24h": ticker.get('high'),
                "low_24h": ticker.get('low'),
            }
        except Exception as e:
            raise Exception(f"Error fetching price: {str(e)}")
    
    async def get_ohlcv(self, symbol: str, timeframe: str = "15m", limit: int = 100) -> List:
        """Fetch OHLCV (candlestick) data"""
        try:
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv, 
                symbol, 
                timeframe, 
                limit=limit
            )
            
            # Convert to more readable format
            formatted_data = []
            for candle in ohlcv:
                formatted_data.append({
                    "timestamp": candle[0],
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5]
                })
            
            return formatted_data
        except Exception as e:
            raise Exception(f"Error fetching OHLCV: {str(e)}")
    
    async def get_ohlcv_df(self, symbol: str, timeframe: str = "15m", limit: int = 200) -> pd.DataFrame:
        """Fetch OHLCV data as pandas DataFrame for technical analysis"""
        try:
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv,
                symbol,
                timeframe,
                limit=limit
            )
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        except Exception as e:
            raise Exception(f"Error fetching OHLCV DataFrame: {str(e)}")

