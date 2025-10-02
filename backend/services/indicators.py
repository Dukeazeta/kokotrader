import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice
from typing import Dict

class TechnicalIndicators:
    """Calculate various technical indicators for trading signals"""
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Dict[str, float]:
        """Calculate all technical indicators and return as dictionary"""
        
        indicators = {}
        
        # Ensure we have enough data
        if len(df) < 50:
            return indicators
        
        try:
            # Moving Averages
            ema_9 = EMAIndicator(close=df['close'], window=9)
            ema_21 = EMAIndicator(close=df['close'], window=21)
            ema_50 = EMAIndicator(close=df['close'], window=50)
            ema_200 = EMAIndicator(close=df['close'], window=200) if len(df) >= 200 else None
            
            indicators['ema_9'] = ema_9.ema_indicator().iloc[-1]
            indicators['ema_21'] = ema_21.ema_indicator().iloc[-1]
            indicators['ema_50'] = ema_50.ema_indicator().iloc[-1]
            if ema_200:
                indicators['ema_200'] = ema_200.ema_indicator().iloc[-1]
            
            # RSI
            rsi = RSIIndicator(close=df['close'], window=14)
            indicators['rsi'] = rsi.rsi().iloc[-1]
            
            # MACD
            macd = MACD(close=df['close'])
            indicators['macd'] = macd.macd().iloc[-1]
            indicators['macd_signal'] = macd.macd_signal().iloc[-1]
            indicators['macd_diff'] = macd.macd_diff().iloc[-1]
            
            # Bollinger Bands
            bb = BollingerBands(close=df['close'], window=20, window_dev=2)
            indicators['bb_upper'] = bb.bollinger_hband().iloc[-1]
            indicators['bb_middle'] = bb.bollinger_mavg().iloc[-1]
            indicators['bb_lower'] = bb.bollinger_lband().iloc[-1]
            indicators['bb_width'] = bb.bollinger_wband().iloc[-1]
            
            # Stochastic
            stoch = StochasticOscillator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=14,
                smooth_window=3
            )
            indicators['stoch_k'] = stoch.stoch().iloc[-1]
            indicators['stoch_d'] = stoch.stoch_signal().iloc[-1]
            
            # ADX (Trend Strength)
            adx = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
            indicators['adx'] = adx.adx().iloc[-1]
            indicators['adx_pos'] = adx.adx_pos().iloc[-1]
            indicators['adx_neg'] = adx.adx_neg().iloc[-1]
            
            # ATR (Volatility)
            atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
            indicators['atr'] = atr.average_true_range().iloc[-1]
            
            # Current price
            indicators['current_price'] = df['close'].iloc[-1]
            
            # Price position relative to EMAs
            current_price = df['close'].iloc[-1]
            indicators['price_above_ema21'] = 1 if current_price > indicators['ema_21'] else 0
            indicators['price_above_ema50'] = 1 if current_price > indicators['ema_50'] else 0
            
            # Volume analysis
            indicators['volume'] = df['volume'].iloc[-1]
            indicators['avg_volume_20'] = df['volume'].tail(20).mean()
            indicators['volume_ratio'] = indicators['volume'] / indicators['avg_volume_20']
            
        except Exception as e:
            print(f"Error calculating indicators: {str(e)}")
        
        return indicators
    
    @staticmethod
    def detect_trend(df: pd.DataFrame, indicators: Dict[str, float]) -> str:
        """Detect overall market trend"""
        
        try:
            ema_9 = indicators.get('ema_9', 0)
            ema_21 = indicators.get('ema_21', 0)
            ema_50 = indicators.get('ema_50', 0)
            adx = indicators.get('adx', 0)
            
            # Strong trend if ADX > 25
            if adx > 25:
                if ema_9 > ema_21 > ema_50:
                    return "BULLISH"
                elif ema_9 < ema_21 < ema_50:
                    return "BEARISH"
            
            # Weak trend or ranging
            if adx < 20:
                return "RANGING"
            
            # Neutral trend
            return "NEUTRAL"
            
        except:
            return "NEUTRAL"
    
    @staticmethod
    def detect_volatility(indicators: Dict[str, float]) -> str:
        """Detect market volatility level"""
        
        try:
            bb_width = indicators.get('bb_width', 0)
            atr = indicators.get('atr', 0)
            current_price = indicators.get('current_price', 1)
            
            # ATR as percentage of price
            atr_pct = (atr / current_price) * 100
            
            if atr_pct > 3 or bb_width > 0.15:
                return "HIGH"
            elif atr_pct > 1.5 or bb_width > 0.08:
                return "MEDIUM"
            else:
                return "LOW"
                
        except:
            return "MEDIUM"

