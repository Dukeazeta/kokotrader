from datetime import datetime
from typing import List, Dict, Tuple
from models.signal import SignalResponse
from services.price_service import PriceService
from services.indicators import TechnicalIndicators

class SignalService:
    """Generate trading signals based on multiple confluences"""
    
    def __init__(self, price_service: PriceService):
        self.price_service = price_service
        self.indicators_calc = TechnicalIndicators()
    
    async def generate_signal(self, symbol: str, timeframe: str = "15m") -> SignalResponse:
        """Generate a complete trading signal with confluences"""
        
        # Fetch price data
        df = await self.price_service.get_ohlcv_df(symbol, timeframe, limit=200)
        current_price_data = await self.price_service.get_current_price(symbol)
        current_price = current_price_data['price']
        
        # Calculate indicators
        indicators = self.indicators_calc.calculate_all(df)
        
        # Detect trend and volatility
        trend = self.indicators_calc.detect_trend(df, indicators)
        volatility = self.indicators_calc.detect_volatility(indicators)
        
        # Analyze confluences
        signal, strength, confluences, confidence = self._analyze_confluences(indicators, trend)
        
        # Calculate entry, stop loss, and take profit levels
        entry_price, stop_loss, tp1, tp2, tp3, risk_reward = self._calculate_levels(
            signal, current_price, indicators, volatility
        )
        
        # Position size suggestion
        position_size = self._suggest_position_size(confidence, volatility)
        
        return SignalResponse(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.now().isoformat(),
            current_price=current_price,
            signal=signal,
            strength=strength,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            risk_reward_ratio=risk_reward,
            position_size_suggestion=position_size,
            indicators=indicators,
            confluences=confluences,
            trend=trend,
            volatility=volatility
        )
    
    def _analyze_confluences(self, indicators: Dict[str, float], trend: str) -> Tuple[str, str, List[str], float]:
        """Analyze multiple confluences to generate signal"""
        
        confluences = []
        bullish_score = 0
        bearish_score = 0
        
        # 1. RSI Analysis
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            confluences.append("RSI oversold (< 30) - Bullish reversal potential")
            bullish_score += 2
        elif rsi < 40:
            confluences.append("RSI approaching oversold - Potential buying opportunity")
            bullish_score += 1
        elif rsi > 70:
            confluences.append("RSI overbought (> 70) - Bearish reversal potential")
            bearish_score += 2
        elif rsi > 60:
            confluences.append("RSI approaching overbought - Potential selling opportunity")
            bearish_score += 1
        
        # 2. MACD Analysis
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        macd_diff = indicators.get('macd_diff', 0)
        
        if macd_diff > 0 and macd > macd_signal:
            confluences.append("MACD bullish crossover - Upward momentum")
            bullish_score += 2
        elif macd_diff < 0 and macd < macd_signal:
            confluences.append("MACD bearish crossover - Downward momentum")
            bearish_score += 2
        
        # 3. Moving Average Alignment
        ema_9 = indicators.get('ema_9', 0)
        ema_21 = indicators.get('ema_21', 0)
        ema_50 = indicators.get('ema_50', 0)
        current_price = indicators.get('current_price', 0)
        
        if ema_9 > ema_21 > ema_50:
            confluences.append("EMAs aligned bullish (9 > 21 > 50)")
            bullish_score += 2
        elif ema_9 < ema_21 < ema_50:
            confluences.append("EMAs aligned bearish (9 < 21 < 50)")
            bearish_score += 2
        
        if current_price > ema_21:
            confluences.append("Price above EMA 21 - Bullish context")
            bullish_score += 1
        else:
            confluences.append("Price below EMA 21 - Bearish context")
            bearish_score += 1
        
        # 4. Bollinger Bands
        bb_upper = indicators.get('bb_upper', 0)
        bb_lower = indicators.get('bb_lower', 0)
        bb_middle = indicators.get('bb_middle', 0)
        
        if current_price < bb_lower:
            confluences.append("Price below lower Bollinger Band - Oversold")
            bullish_score += 1
        elif current_price > bb_upper:
            confluences.append("Price above upper Bollinger Band - Overbought")
            bearish_score += 1
        
        # 5. Stochastic
        stoch_k = indicators.get('stoch_k', 50)
        stoch_d = indicators.get('stoch_d', 50)
        
        if stoch_k < 20 and stoch_k > stoch_d:
            confluences.append("Stochastic oversold with bullish crossover")
            bullish_score += 1
        elif stoch_k > 80 and stoch_k < stoch_d:
            confluences.append("Stochastic overbought with bearish crossover")
            bearish_score += 1
        
        # 6. ADX Trend Strength
        adx = indicators.get('adx', 0)
        if adx > 25:
            if trend == "BULLISH":
                confluences.append(f"Strong bullish trend (ADX: {adx:.1f})")
                bullish_score += 1
            elif trend == "BEARISH":
                confluences.append(f"Strong bearish trend (ADX: {adx:.1f})")
                bearish_score += 1
        else:
            confluences.append(f"Weak trend or ranging market (ADX: {adx:.1f})")
        
        # 7. Volume Analysis
        volume_ratio = indicators.get('volume_ratio', 1)
        if volume_ratio > 1.5:
            confluences.append("High volume confirmation (1.5x average)")
            bullish_score += 0.5 if bullish_score > bearish_score else 0
            bearish_score += 0.5 if bearish_score > bullish_score else 0
        
        # Determine signal
        total_score = bullish_score + bearish_score
        confidence = 0
        
        if total_score == 0:
            signal = "HOLD"
            strength = "WEAK"
            confidence = 30
        elif bullish_score > bearish_score:
            signal = "LONG"
            confidence = min((bullish_score / total_score) * 100, 95)
            
            if bullish_score >= 6:
                strength = "STRONG"
            elif bullish_score >= 4:
                strength = "MODERATE"
            else:
                strength = "WEAK"
        elif bearish_score > bullish_score:
            signal = "SHORT"
            confidence = min((bearish_score / total_score) * 100, 95)
            
            if bearish_score >= 6:
                strength = "STRONG"
            elif bearish_score >= 4:
                strength = "MODERATE"
            else:
                strength = "WEAK"
        else:
            signal = "HOLD"
            strength = "WEAK"
            confidence = 50
        
        return signal, strength, confluences, round(confidence, 2)
    
    def _calculate_levels(
        self,
        signal: str,
        current_price: float,
        indicators: Dict[str, float],
        volatility: str
    ) -> Tuple[float, float, float, float, float, float]:
        """Calculate entry, stop loss, and take profit levels"""
        
        if signal == "HOLD":
            return None, None, None, None, None, None
        
        atr = indicators.get('atr', current_price * 0.02)
        
        # Adjust multipliers based on volatility
        if volatility == "HIGH":
            sl_multiplier = 2.5
            tp_multipliers = [2, 3.5, 5]
        elif volatility == "LOW":
            sl_multiplier = 1.5
            tp_multipliers = [1.5, 2.5, 3.5]
        else:  # MEDIUM
            sl_multiplier = 2
            tp_multipliers = [2, 3, 4.5]
        
        if signal == "LONG":
            entry_price = current_price
            stop_loss = current_price - (atr * sl_multiplier)
            tp1 = current_price + (atr * tp_multipliers[0])
            tp2 = current_price + (atr * tp_multipliers[1])
            tp3 = current_price + (atr * tp_multipliers[2])
        else:  # SHORT
            entry_price = current_price
            stop_loss = current_price + (atr * sl_multiplier)
            tp1 = current_price - (atr * tp_multipliers[0])
            tp2 = current_price - (atr * tp_multipliers[1])
            tp3 = current_price - (atr * tp_multipliers[2])
        
        # Calculate risk-reward ratio
        risk = abs(entry_price - stop_loss)
        reward = abs(entry_price - tp1)
        risk_reward = round(reward / risk, 2) if risk > 0 else 0
        
        return (
            round(entry_price, 2),
            round(stop_loss, 2),
            round(tp1, 2),
            round(tp2, 2),
            round(tp3, 2),
            risk_reward
        )
    
    def _suggest_position_size(self, confidence: float, volatility: str) -> str:
        """Suggest position size based on confidence and volatility"""
        
        if confidence >= 80 and volatility in ["LOW", "MEDIUM"]:
            return "LARGE (3-5% of portfolio)"
        elif confidence >= 70:
            return "MEDIUM (2-3% of portfolio)"
        elif confidence >= 60:
            return "SMALL (1-2% of portfolio)"
        else:
            return "MINIMAL (0.5-1% of portfolio)"

