"""
Smart Money Concepts (SMC) Strategy
Institutional trading approach focusing on market structure, order blocks, and liquidity
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class SMCStrategy:
    """
    Smart Money Concepts trading strategy
    Focuses on institutional order flow and market structure
    """
    
    @staticmethod
    def detect_market_structure(df: pd.DataFrame) -> Dict[str, any]:
        """
        Detect market structure (Higher Highs/Lows or Lower Highs/Lows)
        """
        if len(df) < 20:
            return {"trend": "RANGING", "structure": "UNCLEAR"}
        
        highs = df['high'].tail(20).values
        lows = df['low'].tail(20).values
        
        # Find swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(highs) - 2):
            # Swing high
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                swing_highs.append((i, highs[i]))
            
            # Swing low
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                swing_lows.append((i, lows[i]))
        
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return {"trend": "RANGING", "structure": "INSUFFICIENT_DATA"}
        
        # Check for Higher Highs and Higher Lows (bullish structure)
        recent_highs = [h[1] for h in swing_highs[-2:]]
        recent_lows = [l[1] for l in swing_lows[-2:]]
        
        higher_highs = recent_highs[-1] > recent_highs[-2]
        higher_lows = recent_lows[-1] > recent_lows[-2]
        
        lower_highs = recent_highs[-1] < recent_highs[-2]
        lower_lows = recent_lows[-1] < recent_lows[-2]
        
        if higher_highs and higher_lows:
            return {
                "trend": "BULLISH",
                "structure": "HH_HL",
                "last_high": recent_highs[-1],
                "last_low": recent_lows[-1]
            }
        elif lower_highs and lower_lows:
            return {
                "trend": "BEARISH",
                "structure": "LH_LL",
                "last_high": recent_highs[-1],
                "last_low": recent_lows[-1]
            }
        else:
            return {
                "trend": "RANGING",
                "structure": "MIXED",
                "last_high": recent_highs[-1],
                "last_low": recent_lows[-1]
            }
    
    @staticmethod
    def detect_order_blocks(df: pd.DataFrame, structure: Dict) -> Dict[str, List[Dict]]:
        """
        Detect bullish and bearish order blocks
        Order Block = Last opposite candle before significant move
        """
        if len(df) < 10:
            return {"bullish_ob": [], "bearish_ob": []}
        
        bullish_obs = []
        bearish_obs = []
        
        # Look for order blocks in recent candles
        for i in range(3, len(df) - 1):
            curr = df.iloc[i]
            next_candle = df.iloc[i + 1]
            
            # Bearish Order Block (before bullish move)
            # Last red candle before strong green candle
            if curr['close'] < curr['open'] and next_candle['close'] > next_candle['open']:
                move_size = next_candle['close'] - next_candle['open']
                body_size = curr['open'] - curr['close']
                
                # Strong bullish move after bearish candle
                if move_size > body_size * 2:
                    bearish_obs.append({
                        'index': i,
                        'high': curr['high'],
                        'low': curr['low'],
                        'open': curr['open'],
                        'close': curr['close'],
                        'strength': min(move_size / body_size, 10)
                    })
            
            # Bullish Order Block (before bearish move)
            # Last green candle before strong red candle
            if curr['close'] > curr['open'] and next_candle['close'] < next_candle['open']:
                move_size = next_candle['open'] - next_candle['close']
                body_size = curr['close'] - curr['open']
                
                # Strong bearish move after bullish candle
                if move_size > body_size * 2:
                    bullish_obs.append({
                        'index': i,
                        'high': curr['high'],
                        'low': curr['low'],
                        'open': curr['open'],
                        'close': curr['close'],
                        'strength': min(move_size / body_size, 10)
                    })
        
        # Keep only most recent and strongest
        bullish_obs = sorted(bullish_obs, key=lambda x: (x['index'], x['strength']), reverse=True)[:3]
        bearish_obs = sorted(bearish_obs, key=lambda x: (x['index'], x['strength']), reverse=True)[:3]
        
        return {"bullish_ob": bullish_obs, "bearish_ob": bearish_obs}
    
    @staticmethod
    def detect_fair_value_gaps(df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Detect Fair Value Gaps (FVG) - price imbalances
        Bullish FVG: Gap between candle[i-1].high and candle[i+1].low
        Bearish FVG: Gap between candle[i-1].low and candle[i+1].high
        """
        if len(df) < 3:
            return {"bullish_fvg": [], "bearish_fvg": []}
        
        bullish_fvgs = []
        bearish_fvgs = []
        
        for i in range(1, len(df) - 1):
            prev = df.iloc[i - 1]
            curr = df.iloc[i]
            next_candle = df.iloc[i + 1]
            
            # Bullish FVG (gap up)
            if prev['high'] < next_candle['low']:
                gap_size = next_candle['low'] - prev['high']
                bullish_fvgs.append({
                    'index': i,
                    'top': next_candle['low'],
                    'bottom': prev['high'],
                    'size': gap_size,
                    'filled': False
                })
            
            # Bearish FVG (gap down)
            if prev['low'] > next_candle['high']:
                gap_size = prev['low'] - next_candle['high']
                bearish_fvgs.append({
                    'index': i,
                    'top': prev['low'],
                    'bottom': next_candle['high'],
                    'size': gap_size,
                    'filled': False
                })
        
        # Keep only unfilled gaps (price hasn't returned)
        current_price = df['close'].iloc[-1]
        
        bullish_fvgs = [
            fvg for fvg in bullish_fvgs 
            if current_price < fvg['top']  # Not filled yet
        ][-5:]  # Keep last 5
        
        bearish_fvgs = [
            fvg for fvg in bearish_fvgs 
            if current_price > fvg['bottom']  # Not filled yet
        ][-5:]  # Keep last 5
        
        return {"bullish_fvg": bullish_fvgs, "bearish_fvg": bearish_fvgs}
    
    @staticmethod
    def detect_break_of_structure(df: pd.DataFrame, structure: Dict) -> Dict[str, bool]:
        """
        Detect Break of Structure (BOS) - confirms trend continuation
        """
        if len(df) < 10 or structure['structure'] == "UNCLEAR":
            return {"bullish_bos": False, "bearish_bos": False}
        
        recent_candles = df.tail(5)
        current_price = df['close'].iloc[-1]
        
        bullish_bos = False
        bearish_bos = False
        
        if structure['structure'] == "HH_HL":
            # In bullish structure, BOS = break above previous high
            if 'last_high' in structure and current_price > structure['last_high']:
                bullish_bos = True
        
        elif structure['structure'] == "LH_LL":
            # In bearish structure, BOS = break below previous low
            if 'last_low' in structure and current_price < structure['last_low']:
                bearish_bos = True
        
        return {"bullish_bos": bullish_bos, "bearish_bos": bearish_bos}
    
    @staticmethod
    def detect_change_of_character(df: pd.DataFrame, structure: Dict) -> Dict[str, bool]:
        """
        Detect Change of Character (ChoCh) - potential trend reversal
        """
        if len(df) < 10 or structure['structure'] == "UNCLEAR":
            return {"bullish_choch": False, "bearish_choch": False}
        
        current_price = df['close'].iloc[-1]
        
        bullish_choch = False
        bearish_choch = False
        
        # ChoCh in bearish structure (break above previous lower high)
        if structure['structure'] == "LH_LL":
            if 'last_high' in structure and current_price > structure['last_high']:
                bullish_choch = True
        
        # ChoCh in bullish structure (break below previous higher low)
        elif structure['structure'] == "HH_HL":
            if 'last_low' in structure and current_price < structure['last_low']:
                bearish_choch = True
        
        return {"bullish_choch": bullish_choch, "bearish_choch": bearish_choch}
    
    @staticmethod
    def calculate_premium_discount_zones(df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate premium and discount zones
        Based on recent swing high and low
        """
        if len(df) < 20:
            return {}
        
        recent_data = df.tail(50)
        swing_high = recent_data['high'].max()
        swing_low = recent_data['low'].min()
        
        range_size = swing_high - swing_low
        equilibrium = (swing_high + swing_low) / 2
        
        # Premium zone = upper 50% (equilibrium to swing high)
        # Discount zone = lower 50% (swing low to equilibrium)
        
        premium_start = equilibrium
        premium_end = swing_high
        discount_start = swing_low
        discount_end = equilibrium
        
        current_price = df['close'].iloc[-1]
        
        # Determine if price is in premium or discount
        if current_price > equilibrium:
            zone = "PREMIUM"
            distance_pct = ((current_price - equilibrium) / (swing_high - equilibrium)) * 100
        else:
            zone = "DISCOUNT"
            distance_pct = ((equilibrium - current_price) / (equilibrium - swing_low)) * 100
        
        return {
            "swing_high": swing_high,
            "swing_low": swing_low,
            "equilibrium": equilibrium,
            "premium_zone": [premium_start, premium_end],
            "discount_zone": [discount_start, discount_end],
            "current_zone": zone,
            "zone_depth_pct": distance_pct
        }
    
    @staticmethod
    def detect_liquidity_zones(df: pd.DataFrame) -> Dict[str, List[float]]:
        """
        Detect liquidity zones (equal highs/lows where stops cluster)
        """
        if len(df) < 20:
            return {"buy_side_liquidity": [], "sell_side_liquidity": []}
        
        recent_data = df.tail(50)
        
        # Buy-side liquidity = equal highs (stop losses for shorts)
        highs = recent_data['high'].values
        equal_highs = []
        
        for i in range(len(highs) - 5):
            # Find clusters of similar highs
            cluster = highs[i:i+5]
            if np.std(cluster) < np.mean(cluster) * 0.002:  # Within 0.2%
                equal_highs.append(np.mean(cluster))
        
        # Sell-side liquidity = equal lows (stop losses for longs)
        lows = recent_data['low'].values
        equal_lows = []
        
        for i in range(len(lows) - 5):
            cluster = lows[i:i+5]
            if np.std(cluster) < np.mean(cluster) * 0.002:
                equal_lows.append(np.mean(cluster))
        
        # Remove duplicates and keep unique levels
        buy_side_liquidity = list(set([round(h, 2) for h in equal_highs]))[-3:]
        sell_side_liquidity = list(set([round(l, 2) for l in equal_lows]))[-3:]
        
        return {
            "buy_side_liquidity": sorted(buy_side_liquidity, reverse=True),
            "sell_side_liquidity": sorted(sell_side_liquidity)
        }
    
    @staticmethod
    def generate_smc_signal(df: pd.DataFrame) -> Tuple[str, str, List[str], float]:
        """
        Generate trading signal based on SMC concepts
        
        Returns: (signal, strength, confluences, confidence)
        """
        if len(df) < 20:
            return "HOLD", "WEAK", ["Insufficient data for SMC analysis"], 30
        
        confluences = []
        bullish_score = 0
        bearish_score = 0
        
        # 1. Market Structure
        structure = SMCStrategy.detect_market_structure(df)
        confluences.append(f"📊 Market Structure: {structure['structure']}")
        
        if structure['trend'] == "BULLISH":
            bullish_score += 2
        elif structure['trend'] == "BEARISH":
            bearish_score += 2
        
        # 2. Order Blocks
        order_blocks = SMCStrategy.detect_order_blocks(df, structure)
        current_price = df['close'].iloc[-1]
        
        # Check if price near bullish OB
        for ob in order_blocks['bullish_ob']:
            if ob['low'] <= current_price <= ob['high']:
                confluences.append(f"🟢 Price at Bullish Order Block (Strength: {ob['strength']:.1f})")
                bullish_score += 2.5
                break
        
        # Check if price near bearish OB
        for ob in order_blocks['bearish_ob']:
            if ob['low'] <= current_price <= ob['high']:
                confluences.append(f"🔴 Price at Bearish Order Block (Strength: {ob['strength']:.1f})")
                bearish_score += 2.5
                break
        
        # 3. Fair Value Gaps
        fvgs = SMCStrategy.detect_fair_value_gaps(df)
        
        # Bullish FVG below price (potential support)
        for fvg in fvgs['bullish_fvg']:
            if current_price >= fvg['bottom'] and current_price <= fvg['top'] * 1.02:
                confluences.append(f"📈 Bullish FVG nearby (${fvg['bottom']:.2f}-${fvg['top']:.2f})")
                bullish_score += 1.5
                break
        
        # Bearish FVG above price (potential resistance)
        for fvg in fvgs['bearish_fvg']:
            if current_price <= fvg['top'] and current_price >= fvg['bottom'] * 0.98:
                confluences.append(f"📉 Bearish FVG nearby (${fvg['bottom']:.2f}-${fvg['top']:.2f})")
                bearish_score += 1.5
                break
        
        # 4. Break of Structure
        bos = SMCStrategy.detect_break_of_structure(df, structure)
        if bos['bullish_bos']:
            confluences.append("💥 Bullish Break of Structure - Trend continuation confirmed")
            bullish_score += 3
        if bos['bearish_bos']:
            confluences.append("💥 Bearish Break of Structure - Trend continuation confirmed")
            bearish_score += 3
        
        # 5. Change of Character
        choch = SMCStrategy.detect_change_of_character(df, structure)
        if choch['bullish_choch']:
            confluences.append("🔄 Bullish Change of Character - Potential reversal")
            bullish_score += 2.5
        if choch['bearish_choch']:
            confluences.append("🔄 Bearish Change of Character - Potential reversal")
            bearish_score += 2.5
        
        # 6. Premium/Discount Zones
        zones = SMCStrategy.calculate_premium_discount_zones(df)
        if zones:
            zone_info = f"{zones['current_zone']} ({zones['zone_depth_pct']:.1f}% depth)"
            confluences.append(f"💰 Price in {zone_info}")
            
            # Buy in discount, sell in premium
            if zones['current_zone'] == "DISCOUNT" and zones['zone_depth_pct'] > 50:
                confluences.append("✅ Deep discount zone - Favorable for LONG")
                bullish_score += 1.5
            elif zones['current_zone'] == "PREMIUM" and zones['zone_depth_pct'] > 50:
                confluences.append("✅ Deep premium zone - Favorable for SHORT")
                bearish_score += 1.5
        
        # 7. Liquidity Zones
        liquidity = SMCStrategy.detect_liquidity_zones(df)
        if liquidity['buy_side_liquidity']:
            confluences.append(f"💧 Buy-side liquidity: ${liquidity['buy_side_liquidity'][0]:,.2f}")
        if liquidity['sell_side_liquidity']:
            confluences.append(f"💧 Sell-side liquidity: ${liquidity['sell_side_liquidity'][0]:,.2f}")
        
        # Determine final signal
        total_score = bullish_score + bearish_score
        
        if total_score == 0:
            return "HOLD", "WEAK", confluences, 30
        
        if bullish_score > bearish_score:
            confidence = min((bullish_score / total_score) * 100, 95)
            if bullish_score >= 6:
                strength = "STRONG"
            elif bullish_score >= 4:
                strength = "MODERATE"
            else:
                strength = "WEAK"
            return "LONG", strength, confluences, round(confidence, 2)
        
        elif bearish_score > bullish_score:
            confidence = min((bearish_score / total_score) * 100, 95)
            if bearish_score >= 6:
                strength = "STRONG"
            elif bearish_score >= 4:
                strength = "MODERATE"
            else:
                strength = "WEAK"
            return "SHORT", strength, confluences, round(confidence, 2)
        
        else:
            return "HOLD", "WEAK", confluences, 50

