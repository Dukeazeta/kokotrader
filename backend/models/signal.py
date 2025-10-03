from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime


class LimitOrderLevel(BaseModel):
    """Optimal limit order entry level with ICT confluence"""
    price: float
    type: str  # "ORDER_BLOCK", "FVG_MIDPOINT", "OTE_0.705", etc.
    confluence: int
    description: str
    stop_loss: Optional[float] = None
    take_profit: Optional[List[float]] = None
    risk_reward: Optional[float] = None


class LeverageSuggestion(BaseModel):
    """Dynamic leverage suggestion based on ICT setup quality"""
    suggested_leverage: int  # 5-20x
    risk_level: str  # LOW/MODERATE/HIGH
    position_size_1pct_risk: str
    position_size_2pct_risk: str
    liquidation_distance: str
    max_loss_at_sl_1pct: str
    max_loss_at_sl_2pct: str
    recommendation: str


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
    
    # Multi-timeframe analysis
    mtf_analysis: Optional[Dict[str, Any]] = None  # Multi-timeframe data
    signal_stability: Optional[str] = None  # Signal stability status
    previous_signal: Optional[str] = None  # Previous signal for comparison
    
    # ICT-specific fields (NEW)
    setup_state: Optional[str] = None  # "ACTIVE", "PENDING", "AWAITING_CONFIRMATION"
    pending_levels: Optional[List[Dict]] = None  # Nearby key levels if setup pending
    limit_orders: Optional[List[LimitOrderLevel]] = None  # Optimal limit entry levels
    leverage_suggestion: Optional[LeverageSuggestion] = None  # Dynamic leverage 5x-20x
    killzone_active: Optional[bool] = None  # Is current time in ICT killzone?
    killzone_name: Optional[str] = None  # London Open, NY AM, etc.
    ote_data: Optional[Dict[str, Any]] = None  # Optimal Trade Entry zones

class PriceData(BaseModel):
    symbol: str
    price: float
    timestamp: str
    change_24h: Optional[float] = None
    volume_24h: Optional[float] = None

