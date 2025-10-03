from datetime import datetime
from typing import List, Dict, Tuple, Any
import numpy as np
from models.signal import SignalResponse, LimitOrderLevel, LeverageSuggestion
from services.price_service import PriceService
from services.indicators import TechnicalIndicators
from services.advanced_strategies import AdvancedStrategies
from services.signal_stability import SignalStabilityManager, MultiTimeframeAnalyzer
from services.smc_strategy import SMCStrategy
from services.leverage_calculator import LeverageCalculator


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


class ICTSignalService:
    """
    ICT-Only Signal Service
    Pure Inner Circle Trader / Smart Money Concepts approach
    """
    
    def __init__(self, price_service: PriceService):
        self.price_service = price_service
        self.indicators_calc = TechnicalIndicators()  # Still used for volatility/ATR
        self.advanced_strategies = AdvancedStrategies()  # For S/R levels
        self.smc_strategy = SMCStrategy()
        self.stability_manager = SignalStabilityManager()
        self.mtf_analyzer = MultiTimeframeAnalyzer()
    
    async def generate_signal(self, symbol: str, timeframe: str = "15m") -> SignalResponse:
        """
        Generate ICT-based trading signal with confirmation logic
        
        Only returns active signals when:
        1. Price is AT a key ICT level (OB, FVG, OTE, Breaker)
        2. Confirmation candle is present
        3. Multiple confluences align
        
        Otherwise returns SETUP_PENDING or AWAITING_CONFIRMATION
        """
        
        # Fetch price data
        df = await self.price_service.get_ohlcv_df(symbol, timeframe, limit=200)
        current_price_data = await self.price_service.get_current_price(symbol)
        current_price = current_price_data['price']
        
        # Calculate basic indicators (for volatility, ATR, trend context)
        indicators = self.indicators_calc.calculate_all(df)
        trend = self.indicators_calc.detect_trend(df, indicators)
        volatility = self.indicators_calc.detect_volatility(indicators)
        
        # Generate ICT analysis
        (signal, strength, confluences, confidence, key_levels, 
         killzone_data, ote_zones, limit_orders) = self.smc_strategy.generate_smc_signal(
            df, datetime.now()
        )
        
        # Check if price is AT a key level (not just near)
        at_level = self.smc_strategy.check_price_at_key_level(current_price, key_levels, tolerance_pct=0.3)
        
        setup_state = "ACTIVE"
        
        if not at_level and signal != "HOLD":
            # Price not at key level - show pending setup
            setup_state = "PENDING"
            signal_to_show = "SETUP_PENDING"
            
            # Sort key levels by confluence
            sorted_levels = sorted(key_levels, key=lambda x: x.get('confluence', 0), reverse=True)[:3]
            
            confluences.insert(0, f"⏸️ Setup pending - Price not at key level. Nearest: {sorted_levels[0]['type'] if sorted_levels else 'None'}")
            
            return await self._build_pending_response(
                symbol, timeframe, current_price, signal, strength, confluences,
                confidence, indicators, trend, volatility, sorted_levels,
                killzone_data, ote_zones, limit_orders
            )
        
        # Price is at level, check for confirmation
        if at_level and signal != "HOLD":
            confirmed = self.smc_strategy.wait_for_confirmation(df, signal, at_level)
            
            if not confirmed:
                setup_state = "AWAITING_CONFIRMATION"
                signal_to_show = "AWAITING_CONFIRMATION"
                
                confluences.insert(0, f"⏳ Price at {at_level['type']}, waiting for confirmation candle")
                
                return await self._build_awaiting_response(
                    symbol, timeframe, current_price, signal, strength, confluences,
                    confidence, indicators, trend, volatility, at_level,
                    killzone_data, ote_zones, limit_orders
                )
        
        # Signal is confirmed or HOLD - proceed with full signal generation
        confluences.insert(0, "🎯 Strategy: ICT / Smart Money Concepts")
        
        # Calculate entry, stop loss, and take profit levels
        support_levels, resistance_levels = self.advanced_strategies.detect_support_resistance(df, indicators)
        entry_price, stop_loss, tp1, tp2, tp3, risk_reward = self._calculate_levels(
            signal, current_price, indicators, volatility, support_levels, resistance_levels, ote_zones, key_levels
        )
        
        # Calculate stop loss distance for leverage calculation
        if stop_loss:
            sl_distance_pct = abs(current_price - stop_loss) / current_price * 100
        else:
            sl_distance_pct = 2.0  # Default 2%
        
        # Calculate dynamic leverage suggestion
        leverage_suggestion = None
        if signal != "HOLD":
            leverage_calc = LeverageCalculator.calculate_leverage_suggestion(
                confluence_score=len([c for c in confluences if '🟢' in c or '🔴' in c or '📈' in c or '📉' in c or '💥' in c or '🔄' in c or '🌊' in c or '⚡' in c]),
                confidence=confidence,
                risk_reward_ratio=risk_reward if risk_reward else 2.0,
                volatility=volatility,
                in_killzone=killzone_data.get('in_killzone', False),
                stop_loss_distance_pct=sl_distance_pct
            )
            leverage_suggestion = LeverageSuggestion(**leverage_calc)
        
        # Convert limit orders to proper model
        limit_order_models = []
        if limit_orders:
            for order in limit_orders[:3]:  # Top 3 only
                # Calculate SL/TP for each limit order
                if signal == "LONG":
                    order_sl = order['price'] * 0.98  # 2% below entry
                    order_tp = [
                        order['price'] * 1.02,
                        order['price'] * 1.04,
                        order['price'] * 1.06
                    ]
                else:
                    order_sl = order['price'] * 1.02  # 2% above entry
                    order_tp = [
                        order['price'] * 0.98,
                        order['price'] * 0.96,
                        order['price'] * 0.94
                    ]
                
                limit_order_models.append(LimitOrderLevel(
                    price=order['price'],
                    type=order['type'],
                    confluence=order['confluence'],
                    description=order['description'],
                    stop_loss=order_sl,
                    take_profit=order_tp,
                    risk_reward=(abs(order['price'] - order_tp[0]) / abs(order['price'] - order_sl)) if order_sl else None
                ))
        
        # MTF confirmation (simplified for ICT)
        mtf_analysis_data = None
        signal_stability_status = None
        previous_signal_value = None
        
        try:
            # Get multi-timeframe confirmation
            mtf_result = await self._get_mtf_confirmation(symbol, timeframe, signal, confidence, strength, trend)
            if mtf_result:
                mtf_analysis_data = mtf_result
                
                # Override signal with MTF analysis if significantly different
                if mtf_result.get('mtf_signal') and mtf_result.get('override', False):
                    original_signal = signal
                    signal = mtf_result['mtf_signal']
                    confidence = mtf_result['mtf_confidence']
                    strength = mtf_result.get('mtf_strength', strength)
                    confluences.insert(0, f"🔀 MTF Override: {original_signal} → {signal}")
            
            # Check signal stability
            last_signal = self.stability_manager.get_last_signal(symbol, timeframe)
            if last_signal:
                previous_signal_value = last_signal.signal
                
            should_flip, flip_reason = self.stability_manager.should_flip_signal(
                symbol, signal, confidence, strength, timeframe
            )
            
            if not should_flip and last_signal and last_signal.signal != signal:
                signal_stability_status = f"⚠️ Signal stability lock: {flip_reason}"
                confluences.insert(0, f"🔒 Keeping previous signal ({last_signal.signal}) - {flip_reason}")
                signal = last_signal.signal
            else:
                signal_stability_status = f"✅ Signal confirmed: {flip_reason}"
                confluences.insert(0, f"✅ {flip_reason}")
            
            # Add signal to history
            self.stability_manager.add_signal(symbol, signal, strength, confidence, timeframe)
            
        except Exception as e:
            print(f"MTF/Stability check error: {str(e)}")
        
        # Convert all numpy types to Python native types for Pydantic serialization
        indicators = convert_numpy_types(indicators)
        if ote_zones:
            ote_zones = convert_numpy_types(ote_zones)
        if killzone_data:
            killzone_data = convert_numpy_types(killzone_data)
        
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
            position_size_suggestion=self._suggest_position_size(confidence, volatility, leverage_suggestion),
            indicators=indicators,
            confluences=confluences,
            trend=trend,
            volatility=volatility,
            mtf_analysis=mtf_analysis_data,
            signal_stability=signal_stability_status,
            previous_signal=previous_signal_value,
            setup_state=setup_state,
            limit_orders=limit_order_models,
            leverage_suggestion=leverage_suggestion,
            killzone_active=killzone_data.get('in_killzone', False),
            killzone_name=killzone_data.get('killzone_name'),
            ote_data=ote_zones
        )
    
    async def _build_pending_response(
        self, symbol, timeframe, current_price, signal, strength, confluences, 
        confidence, indicators, trend, volatility, pending_levels, killzone_data, ote_zones, limit_orders
    ) -> SignalResponse:
        """Build response for SETUP_PENDING state"""
        
        # Convert all numpy types to Python native types for Pydantic serialization
        indicators = convert_numpy_types(indicators)
        if ote_zones:
            ote_zones = convert_numpy_types(ote_zones)
        if killzone_data:
            killzone_data = convert_numpy_types(killzone_data)
        if pending_levels:
            pending_levels = convert_numpy_types(pending_levels)
        
        return SignalResponse(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.now().isoformat(),
            current_price=current_price,
            signal="SETUP_PENDING",
            strength=strength,
            confidence=confidence,
            entry_price=None,
            stop_loss=None,
            take_profit_1=None,
            take_profit_2=None,
            take_profit_3=None,
            risk_reward_ratio=None,
            position_size_suggestion="Wait for price to reach key level",
            indicators=indicators,
            confluences=confluences,
            trend=trend,
            volatility=volatility,
            setup_state="PENDING",
            pending_levels=pending_levels,
            limit_orders=[LimitOrderLevel(**order) for order in limit_orders[:3]] if limit_orders else None,
            killzone_active=killzone_data.get('in_killzone', False),
            killzone_name=killzone_data.get('killzone_name'),
            ote_data=ote_zones
        )
    
    async def _build_awaiting_response(
        self, symbol, timeframe, current_price, signal, strength, confluences,
        confidence, indicators, trend, volatility, at_level, killzone_data, ote_zones, limit_orders
    ) -> SignalResponse:
        """Build response for AWAITING_CONFIRMATION state"""
        
        # Convert all numpy types to Python native types for Pydantic serialization
        indicators = convert_numpy_types(indicators)
        if ote_zones:
            ote_zones = convert_numpy_types(ote_zones)
        if killzone_data:
            killzone_data = convert_numpy_types(killzone_data)
        if at_level:
            at_level = convert_numpy_types(at_level)
        
        return SignalResponse(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.now().isoformat(),
            current_price=current_price,
            signal="AWAITING_CONFIRMATION",
            strength=strength,
            confidence=confidence,
            entry_price=at_level.get('price'),
            stop_loss=None,
            take_profit_1=None,
            take_profit_2=None,
            take_profit_3=None,
            risk_reward_ratio=None,
            position_size_suggestion="Wait for confirmation candle",
            indicators=indicators,
            confluences=confluences,
            trend=trend,
            volatility=volatility,
            setup_state="AWAITING_CONFIRMATION",
            pending_levels=[at_level],
            limit_orders=[LimitOrderLevel(**order) for order in limit_orders[:3]] if limit_orders else None,
            killzone_active=killzone_data.get('in_killzone', False),
            killzone_name=killzone_data.get('killzone_name'),
            ote_data=ote_zones
        )
    
    def _calculate_levels(
        self,
        signal: str,
        current_price: float,
        indicators: Dict[str, float],
        volatility: str,
        support_levels: List[float],
        resistance_levels: List[float],
        ote_zones: Dict,
        key_levels: List[Dict]
    ) -> Tuple[float, float, float, float, float, float]:
        """Calculate ICT-based entry, SL, and TP levels"""
        
        if signal == "HOLD" or signal in ["SETUP_PENDING", "AWAITING_CONFIRMATION"]:
            return None, None, None, None, None, None
        
        atr = indicators.get('atr', current_price * 0.02)
        
        # Use tighter stops for ICT
        if volatility == "HIGH":
            sl_multiplier = 2.0
            tp_multipliers = [2.5, 4, 6]
        elif volatility == "LOW":
            sl_multiplier = 1.2
            tp_multipliers = [2, 3, 4.5]
        else:
            sl_multiplier = 1.5
            tp_multipliers = [2.5, 3.5, 5]
        
        if signal == "LONG":
            entry_price = current_price
            
            # Try to use OTE or Order Block for entry
            if ote_zones and ote_zones.get('direction') == "BULLISH":
                entry_price = ote_zones.get('ote_0.705', current_price)
            
            # Place SL below nearest Order Block or support
            ob_levels = [lvl.get('low') for lvl in key_levels if lvl.get('type') == 'ORDER_BLOCK' and lvl.get('low', 0) < entry_price]
            if ob_levels:
                stop_loss = max(ob_levels) * 0.995  # Just below OB
            else:
                stop_loss = entry_price - (atr * sl_multiplier)
            
            # Target liquidity pools or resistance
            nearby_resistances = sorted([r for r in resistance_levels if r > entry_price])
            if len(nearby_resistances) >= 3:
                tp1, tp2, tp3 = nearby_resistances[:3]
            else:
                tp1 = entry_price + (atr * tp_multipliers[0])
                tp2 = entry_price + (atr * tp_multipliers[1])
                tp3 = entry_price + (atr * tp_multipliers[2])
                
        else:  # SHORT
            entry_price = current_price
            
            # Try to use OTE or Order Block for entry
            if ote_zones and ote_zones.get('direction') == "BEARISH":
                entry_price = ote_zones.get('ote_0.705', current_price)
            
            # Place SL above nearest Order Block or resistance
            ob_levels = [lvl.get('high') for lvl in key_levels if lvl.get('type') == 'ORDER_BLOCK' and lvl.get('high', float('inf')) > entry_price]
            if ob_levels:
                stop_loss = min(ob_levels) * 1.005  # Just above OB
            else:
                stop_loss = entry_price + (atr * sl_multiplier)
            
            # Target liquidity pools or support
            nearby_supports = sorted([s for s in support_levels if s < entry_price], reverse=True)
            if len(nearby_supports) >= 3:
                tp1, tp2, tp3 = nearby_supports[:3]
            else:
                tp1 = entry_price - (atr * tp_multipliers[0])
                tp2 = entry_price - (atr * tp_multipliers[1])
                tp3 = entry_price - (atr * tp_multipliers[2])
        
        # Calculate risk-reward
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
    
    def _suggest_position_size(self, confidence: float, volatility: str, leverage_sugg: LeverageSuggestion = None) -> str:
        """Suggest position size based on ICT setup quality"""
        
        if leverage_sugg:
            return f"{leverage_sugg.suggested_leverage}x leverage - {leverage_sugg.risk_level} risk ({leverage_sugg.position_size_1pct_risk} for 1% account risk)"
        
        # Fallback position sizing
        if confidence >= 85 and volatility in ["LOW", "MEDIUM"]:
            return "LARGE (3-5% of portfolio) - High confidence ICT setup"
        elif confidence >= 75:
            return "MEDIUM (2-3% of portfolio)"
        elif confidence >= 65:
            return "SMALL (1-2% of portfolio)"
        elif confidence >= 55:
            return "MINIMAL (0.5-1% of portfolio)"
        else:
            return "AVOID - Wait for better ICT setup"
    
    async def _get_mtf_confirmation(
        self, 
        symbol: str, 
        base_timeframe: str, 
        base_signal: str,
        base_confidence: float,
        base_strength: str,
        base_trend: str
    ) -> Dict:
        """Multi-timeframe confirmation using ICT analysis"""
        try:
            timeframes = self.mtf_analyzer.get_confirmation_timeframes(base_timeframe)
            mtf_signals = {}
            
            for tf in timeframes:
                try:
                    df = await self.price_service.get_ohlcv_df(symbol, tf, limit=200)
                    
                    # Use ICT analysis for MTF
                    (signal, strength, confluences, confidence, key_levels, 
                     killzone_data, ote_zones, limit_orders) = self.smc_strategy.generate_smc_signal(df)
                    
                    mtf_signals[tf] = (signal, confidence, strength)
                    
                except Exception as e:
                    print(f"Error analyzing timeframe {tf}: {str(e)}")
                    continue
            
            if len(mtf_signals) < 2:
                return None
            
            mtf_signal, mtf_confidence, mtf_reason = self.mtf_analyzer.calculate_mtf_score(mtf_signals)
            
            # Override logic
            should_override = False
            if mtf_signal == "HOLD" and base_signal != "HOLD" and mtf_confidence > 50:
                should_override = True
            elif mtf_signal != base_signal and mtf_signal != "HOLD" and mtf_confidence > 70:
                should_override = True
            
            return {
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
            
        except Exception as e:
            print(f"MTF confirmation error: {str(e)}")
            return None

