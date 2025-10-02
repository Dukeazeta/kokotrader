"""
Advanced Trading Strategies
Enhanced confluences for higher accuracy trades
"""
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np


class AdvancedStrategies:
    """Advanced trading strategies with multiple confirmation layers"""
    
    @staticmethod
    def detect_support_resistance(df: pd.DataFrame, indicators: Dict[str, float]) -> Tuple[List[float], List[float]]:
        """
        Detect key support and resistance levels using multiple methods
        """
        support_levels = []
        resistance_levels = []
        
        if len(df) < 50:
            return support_levels, resistance_levels
        
        # Method 1: Recent swing highs/lows
        highs = df['high'].tail(50)
        lows = df['low'].tail(50)
        
        # Find local peaks and troughs
        for i in range(2, len(highs) - 2):
            # Resistance - local peak
            if highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i-2] and \
               highs.iloc[i] > highs.iloc[i+1] and highs.iloc[i] > highs.iloc[i+2]:
                resistance_levels.append(highs.iloc[i])
            
            # Support - local trough
            if lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i-2] and \
               lows.iloc[i] < lows.iloc[i+1] and lows.iloc[i] < lows.iloc[i+2]:
                support_levels.append(lows.iloc[i])
        
        # Method 2: EMA levels as dynamic S/R
        support_levels.append(indicators.get('ema_50', 0))
        resistance_levels.append(indicators.get('bb_upper', 0))
        support_levels.append(indicators.get('bb_lower', 0))
        
        # Remove duplicates and sort
        support_levels = sorted(list(set([s for s in support_levels if s > 0])))
        resistance_levels = sorted(list(set([r for r in resistance_levels if r > 0])))
        
        return support_levels, resistance_levels
    
    @staticmethod
    def detect_price_action_patterns(df: pd.DataFrame) -> Dict[str, bool]:
        """
        Detect candlestick patterns and price action
        """
        patterns = {
            'bullish_engulfing': False,
            'bearish_engulfing': False,
            'hammer': False,
            'shooting_star': False,
            'doji': False,
            'bullish_pin_bar': False,
            'bearish_pin_bar': False
        }
        
        if len(df) < 2:
            return patterns
        
        # Get last two candles
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Bullish Engulfing
        if prev['close'] < prev['open'] and curr['close'] > curr['open']:
            if curr['open'] < prev['close'] and curr['close'] > prev['open']:
                patterns['bullish_engulfing'] = True
        
        # Bearish Engulfing
        if prev['close'] > prev['open'] and curr['close'] < curr['open']:
            if curr['open'] > prev['close'] and curr['close'] < prev['open']:
                patterns['bearish_engulfing'] = True
        
        # Hammer (bullish reversal)
        body = abs(curr['close'] - curr['open'])
        lower_wick = min(curr['close'], curr['open']) - curr['low']
        upper_wick = curr['high'] - max(curr['close'], curr['open'])
        
        if lower_wick > 2 * body and upper_wick < body:
            patterns['hammer'] = True
        
        # Shooting Star (bearish reversal)
        if upper_wick > 2 * body and lower_wick < body:
            patterns['shooting_star'] = True
        
        # Doji (indecision)
        if body < (curr['high'] - curr['low']) * 0.1:
            patterns['doji'] = True
        
        # Bullish Pin Bar
        if lower_wick > 2 * body and curr['close'] > curr['open']:
            patterns['bullish_pin_bar'] = True
        
        # Bearish Pin Bar
        if upper_wick > 2 * body and curr['close'] < curr['open']:
            patterns['bearish_pin_bar'] = True
        
        return patterns
    
    @staticmethod
    def calculate_trend_strength(df: pd.DataFrame, indicators: Dict[str, float]) -> float:
        """
        Calculate trend strength score (0-100)
        """
        if len(df) < 50:
            return 50
        
        score = 50  # neutral
        
        # ADX contribution (0-30 points)
        adx = indicators.get('adx', 20)
        if adx > 50:
            score += 30
        elif adx > 25:
            score += 20
        elif adx > 20:
            score += 10
        
        # EMA alignment (0-20 points)
        ema_9 = indicators.get('ema_9', 0)
        ema_21 = indicators.get('ema_21', 0)
        ema_50 = indicators.get('ema_50', 0)
        
        if ema_9 > ema_21 > ema_50:
            score += 20  # Bullish
        elif ema_9 < ema_21 < ema_50:
            score += 20  # Bearish (strong trend, just downward)
        
        # Price momentum (0-20 points)
        recent_closes = df['close'].tail(10).values
        if len(recent_closes) >= 10:
            trend = np.polyfit(range(len(recent_closes)), recent_closes, 1)[0]
            if abs(trend) > df['close'].iloc[-1] * 0.001:  # Strong momentum
                score += 20
        
        # Volume confirmation (0-10 points)
        volume_ratio = indicators.get('volume_ratio', 1)
        if volume_ratio > 1.5:
            score += 10
        
        return min(100, max(0, score))
    
    @staticmethod
    def detect_divergence(df: pd.DataFrame, indicators: Dict[str, float]) -> Dict[str, bool]:
        """
        Detect RSI and MACD divergences
        """
        divergences = {
            'rsi_bullish': False,
            'rsi_bearish': False,
            'macd_bullish': False,
            'macd_bearish': False
        }
        
        if len(df) < 20:
            return divergences
        
        # This is a simplified version - full divergence detection requires storing indicator history
        # For now, we'll check if price and RSI are moving in opposite directions
        
        recent_prices = df['close'].tail(10).values
        if len(recent_prices) >= 10:
            price_trend = recent_prices[-1] - recent_prices[0]
            
            # If price is falling but RSI is not extremely oversold, might be bullish divergence
            rsi = indicators.get('rsi', 50)
            if price_trend < 0 and rsi > 35 and rsi < 50:
                divergences['rsi_bullish'] = True
            
            # If price is rising but RSI is not extremely overbought, might be bearish divergence
            if price_trend > 0 and rsi < 65 and rsi > 50:
                divergences['rsi_bearish'] = True
        
        return divergences
    
    @staticmethod
    def calculate_volatility_percentile(df: pd.DataFrame, indicators: Dict[str, float]) -> float:
        """
        Calculate current volatility as percentile of recent volatility
        """
        if len(df) < 20:
            return 50
        
        # Calculate ATR percentile
        atr = indicators.get('atr', 0)
        recent_ranges = (df['high'] - df['low']).tail(50)
        
        if len(recent_ranges) < 20 or atr == 0:
            return 50
        
        percentile = (recent_ranges < atr).sum() / len(recent_ranges) * 100
        return percentile
    
    @staticmethod
    def market_regime_detection(df: pd.DataFrame, indicators: Dict[str, float]) -> str:
        """
        Detect market regime: TRENDING_UP, TRENDING_DOWN, RANGING, VOLATILE
        """
        if len(df) < 50:
            return "UNKNOWN"
        
        adx = indicators.get('adx', 20)
        bb_width = indicators.get('bb_width', 0)
        ema_9 = indicators.get('ema_9', 0)
        ema_21 = indicators.get('ema_21', 0)
        ema_50 = indicators.get('ema_50', 0)
        
        # Trending market
        if adx > 25:
            if ema_9 > ema_21 > ema_50:
                return "TRENDING_UP"
            elif ema_9 < ema_21 < ema_50:
                return "TRENDING_DOWN"
        
        # Ranging market
        if adx < 20 and bb_width < 0.1:
            return "RANGING"
        
        # Volatile market
        if bb_width > 0.15:
            return "VOLATILE"
        
        return "TRANSITIONING"

