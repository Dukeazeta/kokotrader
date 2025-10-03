"""
Leverage Calculator for ICT Trading Signals
Calculates optimal leverage (5x-20x) based on confluence, confidence, and risk management
"""
from typing import Dict


class LeverageCalculator:
    """Calculate optimal leverage based on ICT confluence and risk management"""
    
    @staticmethod
    def calculate_leverage_suggestion(
        confluence_score: int,
        confidence: float,
        risk_reward_ratio: float,
        volatility: str,
        in_killzone: bool,
        stop_loss_distance_pct: float = 2.0
    ) -> Dict:
        """
        Calculate suggested leverage (5x-20x) based on:
        - Confluence count (more = higher leverage)
        - Confidence level
        - R:R ratio (better = higher leverage)
        - Volatility (lower = higher leverage safe)
        - Killzone (in killzone = boost)
        
        Returns:
        {
            "suggested_leverage": 15,  # 5x-20x
            "risk_level": "MODERATE",  # LOW/MODERATE/HIGH
            "position_size_1pct_risk": "2.5%",  # Of available margin
            "position_size_2pct_risk": "5%",
            "liquidation_warning": "Liquidation at $43,200 (-15.5%)",
            "max_loss_at_sl": "1% account"
        }
        """
        base_leverage = 5
        
        # Confluence boost (0-5x)
        if confluence_score >= 8:
            base_leverage += 5
        elif confluence_score >= 6:
            base_leverage += 3
        elif confluence_score >= 4:
            base_leverage += 1
        
        # Confidence boost (0-3x)
        if confidence > 80:
            base_leverage += 3
        elif confidence > 70:
            base_leverage += 2
        elif confidence > 60:
            base_leverage += 1
        
        # R:R boost (0-4x)
        if risk_reward_ratio > 5:
            base_leverage += 4
        elif risk_reward_ratio > 3:
            base_leverage += 2
        elif risk_reward_ratio > 2:
            base_leverage += 1
        
        # Killzone boost (+2x)
        if in_killzone:
            base_leverage += 2
        
        # Volatility adjustment
        if volatility == "HIGH":
            base_leverage = max(5, base_leverage - 3)
        elif volatility == "LOW":
            base_leverage = min(20, base_leverage + 1)
        
        suggested_leverage = min(max(base_leverage, 5), 20)  # Clamp to 5-20x
        
        # Determine risk level
        if suggested_leverage <= 8:
            risk_level = "LOW"
        elif suggested_leverage <= 14:
            risk_level = "MODERATE"
        else:
            risk_level = "HIGH"
        
        # Calculate position sizes
        # For 1% account risk: Position size = (Account Risk %) / (Stop Loss Distance % × Leverage)
        # Example: 1% risk / (2% SL × 10x leverage) = 5% of margin position size
        
        position_1pct = (1.0 / stop_loss_distance_pct) * suggested_leverage
        position_2pct = (2.0 / stop_loss_distance_pct) * suggested_leverage
        
        # Calculate liquidation distance (rough estimate)
        # Liquidation occurs when loss = 100% / leverage
        liquidation_pct = (100 / suggested_leverage)
        
        return {
            "suggested_leverage": suggested_leverage,
            "risk_level": risk_level,
            "position_size_1pct_risk": f"{position_1pct:.1f}%",
            "position_size_2pct_risk": f"{position_2pct:.1f}%",
            "liquidation_distance": f"{liquidation_pct:.1f}%",
            "max_loss_at_sl_1pct": "1.0% of account",
            "max_loss_at_sl_2pct": "2.0% of account",
            "recommendation": LeverageCalculator._get_leverage_recommendation(
                suggested_leverage, risk_level, confluence_score, in_killzone
            )
        }
    
    @staticmethod
    def _get_leverage_recommendation(
        leverage: int,
        risk_level: str,
        confluence: int,
        in_killzone: bool
    ) -> str:
        """Generate human-readable recommendation"""
        
        if leverage >= 18 and risk_level == "HIGH":
            return f"{leverage}x - Maximum leverage. High confluence setup in{'side' if in_killzone else ' outside'} killzone. Use tight stops."
        elif leverage >= 15:
            return f"{leverage}x - Aggressive leverage. Strong setup with {confluence} confluences. Consider scaling in."
        elif leverage >= 12:
            return f"{leverage}x - Moderate-high leverage. Good setup quality. Recommended for experienced traders."
        elif leverage >= 8:
            return f"{leverage}x - Balanced leverage. Solid setup. Good risk/reward ratio."
        else:
            return f"{leverage}x - Conservative leverage. Safe entry for capital preservation."

