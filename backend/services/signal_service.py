from datetime import datetime
from typing import List, Dict, Tuple, Any
import numpy as np
from models.signal import SignalResponse
from services.price_service import PriceService
from services.indicators import TechnicalIndicators
from services.advanced_strategies import AdvancedStrategies
from services.signal_stability import SignalStabilityManager, MultiTimeframeAnalyzer
from services.smc_strategy import SMCStrategy

def convert_numpy_types(obj: Any) -> Any:
    """
    Recursively convert numpy types to Python native types for JSON serialization.
    Handles numpy.bool_, numpy.int64, numpy.float64, etc.
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

class SignalService:
    """Generate trading signals based on multiple confluences"""
    
    def __init__(self, price_service: PriceService):
        self.price_service = price_service
        self.indicators_calc = TechnicalIndicators()
        self.advanced_strategies = AdvancedStrategies()
        self.smc_strategy = SMCStrategy()
        self.stability_manager = SignalStabilityManager()
        self.mtf_analyzer = MultiTimeframeAnalyzer()
    
    async def generate_signal(self, symbol: str, timeframe: str = "15m", strategy: str = "TECHNICAL") -> SignalResponse:
        """
        Generate a complete trading signal with advanced confluences
        
        Args:
            symbol: Trading pair (e.g., BTC/USDT)
            timeframe: Candlestick timeframe (e.g., 15m, 1h)
            strategy: "TECHNICAL" (indicators) or "SMC" (Smart Money Concepts)
        """
        
        # Fetch price data
        df = await self.price_service.get_ohlcv_df(symbol, timeframe, limit=200)
        current_price_data = await self.price_service.get_current_price(symbol)
        current_price = current_price_data['price']
        
        # Calculate indicators (always needed for fallback data)
        indicators = self.indicators_calc.calculate_all(df)
        
        # Detect trend and volatility
        trend = self.indicators_calc.detect_trend(df, indicators)
        volatility = self.indicators_calc.detect_volatility(indicators)
        
        # Strategy-specific signal generation
        if strategy == "SMC":
            # Use Smart Money Concepts
            signal, strength, confluences, confidence = self.smc_strategy.generate_smc_signal(df)
            confluences.insert(0, "🎯 Strategy: Smart Money Concepts (SMC)")
            
            # Still get support/resistance for levels calculation
            support_levels, resistance_levels = self.advanced_strategies.detect_support_resistance(df, indicators)
            trend_strength = 70 if signal != "HOLD" else 50  # Simplified for SMC
            
        else:  # Default to TECHNICAL strategy
            # Advanced technical analysis
            market_regime = self.advanced_strategies.market_regime_detection(df, indicators)
            price_patterns = self.advanced_strategies.detect_price_action_patterns(df)
            divergences = self.advanced_strategies.detect_divergence(df, indicators)
            trend_strength = self.advanced_strategies.calculate_trend_strength(df, indicators)
            support_levels, resistance_levels = self.advanced_strategies.detect_support_resistance(df, indicators)
            
            # Analyze confluences with advanced features
            signal, strength, confluences, confidence = self._analyze_confluences(
                indicators, trend, price_patterns, divergences, market_regime, trend_strength
            )
            confluences.insert(0, "📊 Strategy: Technical Analysis")
        
        # Calculate entry, stop loss, and take profit levels using S/R
        entry_price, stop_loss, tp1, tp2, tp3, risk_reward = self._calculate_levels(
            signal, current_price, indicators, volatility, support_levels, resistance_levels
        )
        
        # Position size suggestion
        position_size = self._suggest_position_size(confidence, volatility, trend_strength)
        
        # NEW: Check signal stability and multi-timeframe alignment
        mtf_analysis_data = None
        signal_stability_status = None
        previous_signal_value = None
        
        try:
            # Get multi-timeframe confirmation
            mtf_result = await self._get_mtf_confirmation(symbol, timeframe, signal, confidence, strength, trend, strategy)
            if mtf_result:
                mtf_analysis_data = mtf_result
                
                # Override signal with MTF analysis if significantly different
                if mtf_result.get('mtf_signal') and mtf_result.get('override', False):
                    original_signal = signal
                    signal = mtf_result['mtf_signal']
                    confidence = mtf_result['mtf_confidence']
                    strength = mtf_result.get('mtf_strength', strength)
                    confluences.insert(0, f"🔀 MTF Override: {original_signal} → {signal} (Reason: {mtf_result.get('mtf_reason', 'Multi-timeframe conflict')})")
            
            # Check signal stability (prevent whipsaws)
            last_signal = self.stability_manager.get_last_signal(symbol, timeframe)
            if last_signal:
                previous_signal_value = last_signal.signal
                
            should_flip, flip_reason = self.stability_manager.should_flip_signal(
                symbol, signal, confidence, strength, timeframe
            )
            
            if not should_flip and last_signal:
                # Keep previous signal
                signal_stability_status = f"⚠️ Signal stability lock: {flip_reason}"
                confluences.insert(0, f"🔒 Keeping previous signal ({last_signal.signal}) - {flip_reason}")
                signal = last_signal.signal
                # Use previous levels too
                entry_price = last_signal_entry if 'last_signal_entry' in locals() else entry_price
            else:
                signal_stability_status = f"✅ Signal confirmed: {flip_reason}"
                confluences.insert(0, f"✅ {flip_reason}")
            
            # Add signal to history
            self.stability_manager.add_signal(symbol, signal, strength, confidence, timeframe)
            
        except Exception as e:
            print(f"MTF/Stability check error: {str(e)}")
        
        # Convert all numpy types to Python native types for Pydantic serialization
        indicators = convert_numpy_types(indicators)
        if mtf_analysis_data:
            mtf_analysis_data = convert_numpy_types(mtf_analysis_data)
        
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
            volatility=volatility,
            mtf_analysis=mtf_analysis_data,
            signal_stability=signal_stability_status,
            previous_signal=previous_signal_value,
            strategy_used=strategy
        )
    
    def _analyze_confluences(
        self, 
        indicators: Dict[str, float], 
        trend: str,
        price_patterns: Dict[str, bool] = None,
        divergences: Dict[str, bool] = None,
        market_regime: str = None,
        trend_strength: float = 50
    ) -> Tuple[str, str, List[str], float]:
        """Analyze multiple confluences to generate signal with enhanced accuracy"""
        
        confluences = []
        bullish_score = 0
        bearish_score = 0
        
        if price_patterns is None:
            price_patterns = {}
        if divergences is None:
            divergences = {}
        
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
        
        # 8. Price Action Patterns (NEW)
        if price_patterns.get('bullish_engulfing'):
            confluences.append("✨ Bullish Engulfing Pattern - Strong reversal signal")
            bullish_score += 2.5
        if price_patterns.get('bearish_engulfing'):
            confluences.append("✨ Bearish Engulfing Pattern - Strong reversal signal")
            bearish_score += 2.5
        if price_patterns.get('hammer'):
            confluences.append("🔨 Hammer Pattern - Bullish reversal")
            bullish_score += 1.5
        if price_patterns.get('shooting_star'):
            confluences.append("⭐ Shooting Star Pattern - Bearish reversal")
            bearish_score += 1.5
        if price_patterns.get('bullish_pin_bar'):
            confluences.append("📌 Bullish Pin Bar - Rejection of lower prices")
            bullish_score += 1
        if price_patterns.get('bearish_pin_bar'):
            confluences.append("📌 Bearish Pin Bar - Rejection of higher prices")
            bearish_score += 1
        
        # 9. Divergence Detection (NEW)
        if divergences.get('rsi_bullish'):
            confluences.append("📈 RSI Bullish Divergence - Hidden buying pressure")
            bullish_score += 2
        if divergences.get('rsi_bearish'):
            confluences.append("📉 RSI Bearish Divergence - Hidden selling pressure")
            bearish_score += 2
        if divergences.get('macd_bullish'):
            confluences.append("📈 MACD Bullish Divergence - Momentum shift")
            bullish_score += 1.5
        if divergences.get('macd_bearish'):
            confluences.append("📉 MACD Bearish Divergence - Momentum shift")
            bearish_score += 1.5
        
        # 10. Market Regime Filter (NEW)
        if market_regime:
            confluences.append(f"🌐 Market Regime: {market_regime}")
            # Boost score if signal aligns with market regime
            if market_regime == "TRENDING_UP" and bullish_score > bearish_score:
                bullish_score += 1.5
            elif market_regime == "TRENDING_DOWN" and bearish_score > bullish_score:
                bearish_score += 1.5
            elif market_regime == "RANGING":
                # Reduce both scores in ranging market (less reliable)
                confluences.append("⚠️ Ranging market - Reduce position size")
                bullish_score *= 0.7
                bearish_score *= 0.7
        
        # 11. Trend Strength Bonus (NEW)
        if trend_strength > 70:
            confluences.append(f"💪 Strong Trend (Strength: {trend_strength:.0f}/100)")
            if bullish_score > bearish_score:
                bullish_score += 1
            else:
                bearish_score += 1
        elif trend_strength < 40:
            confluences.append(f"⚠️ Weak Trend (Strength: {trend_strength:.0f}/100) - Lower confidence")
        
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
        volatility: str,
        support_levels: List[float] = None,
        resistance_levels: List[float] = None
    ) -> Tuple[float, float, float, float, float, float]:
        """Calculate entry, stop loss, and take profit levels using S/R"""
        
        if signal == "HOLD":
            return None, None, None, None, None, None
        
        if support_levels is None:
            support_levels = []
        if resistance_levels is None:
            resistance_levels = []
        
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
            
            # Find nearest support for stop loss
            nearby_supports = [s for s in support_levels if s < current_price and s > current_price * 0.95]
            if nearby_supports:
                # Place SL just below nearest support
                stop_loss = max(nearby_supports) * 0.998
            else:
                stop_loss = current_price - (atr * sl_multiplier)
            
            # Find resistance levels for take profits
            nearby_resistances = sorted([r for r in resistance_levels if r > current_price])
            if len(nearby_resistances) >= 3:
                tp1 = nearby_resistances[0]
                tp2 = nearby_resistances[1]
                tp3 = nearby_resistances[2]
            else:
                tp1 = current_price + (atr * tp_multipliers[0])
                tp2 = current_price + (atr * tp_multipliers[1])
                tp3 = current_price + (atr * tp_multipliers[2])
                
        else:  # SHORT
            entry_price = current_price
            
            # Find nearest resistance for stop loss
            nearby_resistances = [r for r in resistance_levels if r > current_price and r < current_price * 1.05]
            if nearby_resistances:
                # Place SL just above nearest resistance
                stop_loss = min(nearby_resistances) * 1.002
            else:
                stop_loss = current_price + (atr * sl_multiplier)
            
            # Find support levels for take profits
            nearby_supports = sorted([s for s in support_levels if s < current_price], reverse=True)
            if len(nearby_supports) >= 3:
                tp1 = nearby_supports[0]
                tp2 = nearby_supports[1]
                tp3 = nearby_supports[2]
            else:
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
    
    def _suggest_position_size(self, confidence: float, volatility: str, trend_strength: float = 50) -> str:
        """Suggest position size based on confidence, volatility, and trend strength"""
        
        # Base position size on confidence
        if confidence >= 85 and volatility in ["LOW", "MEDIUM"] and trend_strength > 70:
            return "LARGE (3-5% of portfolio) - High confidence + Strong trend"
        elif confidence >= 80 and volatility in ["LOW", "MEDIUM"]:
            return "LARGE (3-4% of portfolio)"
        elif confidence >= 70 and trend_strength > 60:
            return "MEDIUM (2-3% of portfolio)"
        elif confidence >= 70:
            return "MEDIUM (1.5-2.5% of portfolio)"
        elif confidence >= 60:
            return "SMALL (1-2% of portfolio)"
        elif confidence >= 50:
            return "MINIMAL (0.5-1% of portfolio)"
        else:
            return "AVOID - Confidence too low"
    
    async def _get_mtf_confirmation(
        self, 
        symbol: str, 
        base_timeframe: str, 
        base_signal: str,
        base_confidence: float,
        base_strength: str,
        base_trend: str,
        strategy: str = "TECHNICAL"
    ) -> Dict:
        """
        Get multi-timeframe confirmation for the signal
        Analyzes higher timeframes to confirm or reject the signal
        """
        try:
            # Get confirmation timeframes (current + 1-2 higher)
            timeframes = self.mtf_analyzer.get_confirmation_timeframes(base_timeframe)
            
            # Analyze each timeframe
            mtf_signals = {}
            
            for tf in timeframes:
                try:
                    # Fetch data for this timeframe
                    df = await self.price_service.get_ohlcv_df(symbol, tf, limit=200)
                    indicators = self.indicators_calc.calculate_all(df)
                    trend = self.indicators_calc.detect_trend(df, indicators)
                    volatility = self.indicators_calc.detect_volatility(indicators)
                    
                    # Use selected strategy for analysis
                    if strategy == "SMC":
                        signal, strength, confluences, confidence = self.smc_strategy.generate_smc_signal(df)
                    else:
                        # Quick signal analysis for this timeframe (technical)
                        price_patterns = self.advanced_strategies.detect_price_action_patterns(df)
                        divergences = self.advanced_strategies.detect_divergence(df, indicators)
                        market_regime = self.advanced_strategies.market_regime_detection(df, indicators)
                        trend_strength = self.advanced_strategies.calculate_trend_strength(df, indicators)
                        
                        signal, strength, confluences, confidence = self._analyze_confluences(
                            indicators, trend, price_patterns, divergences, market_regime, trend_strength
                        )
                    
                    mtf_signals[tf] = (signal, confidence, strength)
                    
                except Exception as e:
                    print(f"Error analyzing timeframe {tf}: {str(e)}")
                    continue
            
            # Calculate multi-timeframe score
            if len(mtf_signals) < 2:
                return None  # Not enough data
            
            mtf_signal, mtf_confidence, mtf_reason = self.mtf_analyzer.calculate_mtf_score(mtf_signals)
            
            # Check if we should override the base signal
            should_override = False
            
            # Override if MTF says HOLD but base says trade
            if mtf_signal == "HOLD" and base_signal != "HOLD" and mtf_confidence > 50:
                should_override = True
            
            # Override if MTF has opposite signal with high confidence
            elif mtf_signal != base_signal and mtf_signal != "HOLD" and mtf_confidence > 70:
                should_override = True
            
            # Build MTF analysis data
            mtf_data = {
                'timeframes_analyzed': list(mtf_signals.keys()),
                'mtf_signal': mtf_signal,
                'mtf_confidence': mtf_confidence,
                'mtf_reason': mtf_reason,
                'override': should_override,
                'signals_by_timeframe': {
                    tf: {'signal': sig, 'confidence': conf, 'strength': str}
                    for tf, (sig, conf, str) in mtf_signals.items()
                },
                'alignment_score': mtf_confidence
            }
            
            # Convert any numpy types to Python native types
            mtf_data = convert_numpy_types(mtf_data)
            
            # Check higher timeframe trend alignment
            if len(timeframes) >= 2:
                higher_tf = timeframes[1]
                if higher_tf in mtf_signals:
                    df_higher = await self.price_service.get_ohlcv_df(symbol, higher_tf, limit=100)
                    indicators_higher = self.indicators_calc.calculate_all(df_higher)
                    trend_higher = self.indicators_calc.detect_trend(df_higher, indicators_higher)
                    
                    is_aligned, alignment_reason = self.mtf_analyzer.check_trend_alignment(
                        base_trend, trend_higher, base_signal
                    )
                    
                    mtf_data['trend_alignment'] = {
                        'is_aligned': is_aligned,
                        'reason': alignment_reason,
                        'higher_tf': higher_tf,
                        'higher_tf_trend': trend_higher
                    }
            
            return mtf_data
            
        except Exception as e:
            print(f"MTF confirmation error: {str(e)}")
            return None

