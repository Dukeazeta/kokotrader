"""
Signal Stability & Multi-Timeframe Analysis
Prevents signal whipsaws and improves accuracy
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SignalHistory:
    """Track historical signals to prevent whipsaws"""
    symbol: str
    signal: str  # LONG, SHORT, HOLD
    strength: str
    confidence: float
    timestamp: datetime
    timeframe: str
    
    
class SignalStabilityManager:
    """
    Manages signal stability to prevent constant flipping
    """
    
    def __init__(self):
        # Store recent signals: {symbol: [SignalHistory]}
        self.signal_history: Dict[str, List[SignalHistory]] = {}
        self.max_history_per_symbol = 50
        
    def add_signal(self, symbol: str, signal: str, strength: str, confidence: float, timeframe: str):
        """Add a new signal to history"""
        if symbol not in self.signal_history:
            self.signal_history[symbol] = []
        
        signal_entry = SignalHistory(
            symbol=symbol,
            signal=signal,
            strength=strength,
            confidence=confidence,
            timestamp=datetime.now(),
            timeframe=timeframe
        )
        
        self.signal_history[symbol].append(signal_entry)
        
        # Keep only recent history
        if len(self.signal_history[symbol]) > self.max_history_per_symbol:
            self.signal_history[symbol] = self.signal_history[symbol][-self.max_history_per_symbol:]
    
    def get_recent_signals(self, symbol: str, minutes: int = 30) -> List[SignalHistory]:
        """Get signals from last N minutes"""
        if symbol not in self.signal_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            sig for sig in self.signal_history[symbol]
            if sig.timestamp >= cutoff_time
        ]
    
    def get_last_signal(self, symbol: str, timeframe: str) -> Optional[SignalHistory]:
        """Get the most recent signal for a symbol and timeframe"""
        if symbol not in self.signal_history:
            return None
        
        # Filter by timeframe and get most recent
        matching = [sig for sig in reversed(self.signal_history[symbol]) 
                   if sig.timeframe == timeframe]
        
        return matching[0] if matching else None
    
    def should_flip_signal(
        self, 
        symbol: str, 
        current_signal: str, 
        current_confidence: float,
        current_strength: str,
        timeframe: str,
        min_confidence_diff: float = 15,
        cooldown_minutes: int = 10
    ) -> Tuple[bool, str]:
        """
        Determine if we should flip the signal or keep previous one
        
        Returns: (should_flip, reason)
        """
        last_signal = self.get_last_signal(symbol, timeframe)
        
        # No history - allow first signal
        if not last_signal:
            return True, "First signal for this symbol"
        
        # Same signal - no flip needed
        if last_signal.signal == current_signal:
            return True, "Signal confirmed (same direction)"
        
        # Check cooldown period
        time_since_last = (datetime.now() - last_signal.timestamp).total_seconds() / 60
        if time_since_last < cooldown_minutes:
            return False, f"Cooldown period ({time_since_last:.1f} min < {cooldown_minutes} min)"
        
        # Require significant confidence increase to flip
        confidence_diff = current_confidence - last_signal.confidence
        if confidence_diff < min_confidence_diff:
            return False, f"Confidence increase insufficient ({confidence_diff:.1f}% < {min_confidence_diff}%)"
        
        # Check if current signal is STRONG (allow flip more easily for strong signals)
        if current_strength == "STRONG" and current_confidence >= 75:
            return True, f"Strong signal detected ({current_confidence}% confidence)"
        
        # Check if previous signal was WEAK (allow flip more easily)
        if last_signal.strength == "WEAK" and current_confidence >= 65:
            return True, f"Previous signal weak, new signal stronger"
        
        # Default: don't flip unless really confident
        if current_confidence >= 80 and current_strength in ["STRONG", "MODERATE"]:
            return True, f"High confidence signal ({current_confidence}%)"
        
        return False, "Signal flip requirements not met"
    
    def get_signal_consistency(self, symbol: str, minutes: int = 30) -> Dict[str, float]:
        """
        Calculate how consistent signals have been
        Returns: {LONG: %, SHORT: %, HOLD: %}
        """
        recent_signals = self.get_recent_signals(symbol, minutes)
        
        if not recent_signals:
            return {"LONG": 0, "SHORT": 0, "HOLD": 100}
        
        total = len(recent_signals)
        counts = {"LONG": 0, "SHORT": 0, "HOLD": 0}
        
        for sig in recent_signals:
            counts[sig.signal] = counts.get(sig.signal, 0) + 1
        
        return {
            signal: (count / total) * 100
            for signal, count in counts.items()
        }


class MultiTimeframeAnalyzer:
    """
    Analyze multiple timeframes to confirm signals
    Only trade when higher timeframe aligns with lower timeframe
    """
    
    # Timeframe hierarchy (lower to higher)
    TIMEFRAME_HIERARCHY = {
        '1m': 1,
        '5m': 2,
        '15m': 3,
        '30m': 4,
        '1h': 5,
        '4h': 6,
        '1d': 7
    }
    
    @classmethod
    def get_higher_timeframe(cls, timeframe: str) -> str:
        """Get the next higher timeframe"""
        current_rank = cls.TIMEFRAME_HIERARCHY.get(timeframe, 3)
        
        for tf, rank in cls.TIMEFRAME_HIERARCHY.items():
            if rank == current_rank + 1:
                return tf
        
        return '1h'  # Default
    
    @classmethod
    def get_confirmation_timeframes(cls, base_timeframe: str) -> List[str]:
        """
        Get timeframes that should be checked for confirmation
        Returns [current, higher1, higher2]
        """
        current_rank = cls.TIMEFRAME_HIERARCHY.get(base_timeframe, 3)
        
        timeframes = [base_timeframe]
        
        # Add 1-2 higher timeframes
        for tf, rank in sorted(cls.TIMEFRAME_HIERARCHY.items(), key=lambda x: x[1]):
            if rank > current_rank and len(timeframes) < 3:
                timeframes.append(tf)
        
        return timeframes
    
    @staticmethod
    def calculate_mtf_score(signals: Dict[str, Tuple[str, float, str]]) -> Tuple[str, float, str]:
        """
        Calculate multi-timeframe signal
        
        Args:
            signals: {timeframe: (signal, confidence, strength)}
            
        Returns:
            (final_signal, final_confidence, reason)
        """
        if not signals:
            return "HOLD", 30, "No signals available"
        
        # Weight timeframes: higher timeframes = more weight
        weights = {'1m': 1, '5m': 1.5, '15m': 2, '30m': 2.5, '1h': 3, '4h': 4, '1d': 5}
        
        scores = {"LONG": 0, "SHORT": 0, "HOLD": 0}
        total_weight = 0
        
        for tf, (signal, confidence, strength) in signals.items():
            weight = weights.get(tf, 2)
            
            # Confidence-weighted score
            score_contribution = (confidence / 100) * weight
            
            scores[signal] += score_contribution
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            for sig in scores:
                scores[sig] = (scores[sig] / total_weight) * 100
        
        # Determine final signal
        max_signal = max(scores, key=scores.get)
        max_score = scores[max_signal]
        
        # Check for alignment
        signal_list = [sig for sig, conf, str in signals.values()]
        unique_signals = set(signal_list)
        
        # All timeframes agree
        if len(unique_signals) == 1:
            reason = f"✅ All {len(signals)} timeframes aligned: {max_signal}"
            return max_signal, min(max_score, 95), reason
        
        # Majority agreement
        majority_count = signal_list.count(max_signal)
        if majority_count >= len(signal_list) * 0.66:  # 66% agreement
            reason = f"✅ {majority_count}/{len(signal_list)} timeframes agree: {max_signal}"
            return max_signal, min(max_score * 0.9, 85), reason
        
        # Conflicting signals
        reason = f"⚠️ Conflicting timeframes - {unique_signals}"
        return "HOLD", 40, reason
    
    @staticmethod
    def check_trend_alignment(
        lower_tf_trend: str,
        higher_tf_trend: str,
        signal: str
    ) -> Tuple[bool, str]:
        """
        Check if signal aligns with higher timeframe trend
        
        Returns: (is_aligned, reason)
        """
        # LONG signal should align with bullish higher timeframe
        if signal == "LONG":
            if higher_tf_trend in ["BULLISH", "NEUTRAL"]:
                return True, f"✅ LONG aligned with {higher_tf_trend} higher TF"
            else:
                return False, f"❌ LONG against {higher_tf_trend} higher TF"
        
        # SHORT signal should align with bearish higher timeframe
        elif signal == "SHORT":
            if higher_tf_trend in ["BEARISH", "NEUTRAL"]:
                return True, f"✅ SHORT aligned with {higher_tf_trend} higher TF"
            else:
                return False, f"❌ SHORT against {higher_tf_trend} higher TF"
        
        # HOLD is always safe
        return True, "HOLD - No trend conflict"

