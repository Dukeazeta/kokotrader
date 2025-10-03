from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime

class SignalResponse(BaseModel):
    symbol: str
    timeframe: str
    timestamp: str
    current_price: float
    
    # Signal information
    signal: str  # "LONG", "SHORT", "HOLD", "CLOSE_LONG", "CLOSE_SHORT"
    strength: str  # "STRONG", "MODERATE", "WEAK"
    confidence: float  # 0-100
    
    # Entry and exit levels
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    
    # Risk management
    risk_reward_ratio: Optional[float] = None
    position_size_suggestion: Optional[str] = None
    
    # Technical indicators
    indicators: Dict[str, float]
    
    # Confluences (reasons for the signal)
    confluences: List[str]
    
    # Market context
    trend: str  # "BULLISH", "BEARISH", "NEUTRAL", "RANGING"
    volatility: str  # "HIGH", "MEDIUM", "LOW"
    
    # Multi-timeframe analysis (NEW)
    mtf_analysis: Optional[Dict[str, Any]] = None  # Multi-timeframe data
    signal_stability: Optional[str] = None  # Signal stability status
    previous_signal: Optional[str] = None  # Previous signal for comparison
    strategy_used: Optional[str] = None  # Strategy used: "TECHNICAL" or "SMC"

class PriceData(BaseModel):
    symbol: str
    price: float
    timestamp: str
    change_24h: Optional[float] = None
    volume_24h: Optional[float] = None

