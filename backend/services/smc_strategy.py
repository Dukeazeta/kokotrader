"""
Smart Money Concepts (SMC) Strategy
Institutional trading approach focusing on market structure, order blocks, and liquidity
Enhanced with ICT concepts: Killzones, OTE, Liquidity Sweeps, Breaker Blocks
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pytz


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
    def is_in_killzone(timestamp: datetime = None) -> Dict:
        """
        Check if current time is in ICT Killzone
        - London Open: 02:00-05:00 EST (high probability)
        - New York AM: 08:00-11:00 EST (highest probability)
        - London Close: 10:00-12:00 EST (medium probability)
        """
        if timestamp is None:
            timestamp = datetime.now(pytz.UTC)
        
        # Convert to EST
        est = pytz.timezone('US/Eastern')
        est_time = timestamp.astimezone(est)
        hour = est_time.hour
        
        if 2 <= hour < 5:
            return {
                "in_killzone": True,
                "killzone_name": "London Open",
                "probability_multiplier": 1.3,
                "description": "High probability setup window"
            }
        elif 8 <= hour < 11:
            return {
                "in_killzone": True,
                "killzone_name": "New York AM",
                "probability_multiplier": 1.5,
                "description": "Highest probability setup window"
            }
        elif 10 <= hour < 12:
            return {
                "in_killzone": True,
                "killzone_name": "London Close",
                "probability_multiplier": 1.2,
                "description": "Medium probability setup window"
            }
        else:
            return {
                "in_killzone": False,
                "killzone_name": None,
                "probability_multiplier": 1.0,
                "description": "Outside killzone - lower probability"
            }
    
    @staticmethod
    def calculate_ote_zones(df: pd.DataFrame, structure: Dict) -> Dict:
        """
        Calculate Optimal Trade Entry zones (0.62, 0.705, 0.79 Fibonacci)
        Based on recent impulse move (swing high to swing low)
        """
        if len(df) < 20 or structure.get('structure') == "UNCLEAR":
            return {}
        
        # Find last significant impulse move
        recent_data = df.tail(50)
        swing_high = recent_data['high'].max()
        swing_low = recent_data['low'].min()
        
        # Find where these swings occurred
        high_idx = recent_data['high'].idxmax()
        low_idx = recent_data['low'].idxmin()
        
        # Determine direction of last impulse
        if high_idx > low_idx:
            # Bullish impulse (from low to high)
            impulse_start = swing_low
            impulse_end = swing_high
            direction = "BULLISH"
        else:
            # Bearish impulse (from high to low)
            impulse_start = swing_high
            impulse_end = swing_low
            direction = "BEARISH"
        
        impulse_range = abs(impulse_end - impulse_start)
        
        # Calculate Fibonacci retracement levels (OTE zones)
        if direction == "BULLISH":
            # For bullish, we want retracements from high back down
            ote_62 = impulse_end - (impulse_range * 0.62)
            ote_705 = impulse_end - (impulse_range * 0.705)
            ote_79 = impulse_end - (impulse_range * 0.79)
        else:
            # For bearish, we want retracements from low back up
            ote_62 = impulse_end + (impulse_range * 0.62)
            ote_705 = impulse_end + (impulse_range * 0.705)
            ote_79 = impulse_end + (impulse_range * 0.79)
        
        current_price = df['close'].iloc[-1]
        
        # Check if price is in OTE zone
        if direction == "BULLISH":
            in_ote = ote_79 <= current_price <= ote_62
        else:
            in_ote = ote_62 <= current_price <= ote_79
        
        return {
            "direction": direction,
            "ote_0.62": round(ote_62, 2),
            "ote_0.705": round(ote_705, 2),
            "ote_0.79": round(ote_79, 2),
            "in_ote_zone": in_ote,
            "optimal_entry": round(ote_705, 2),  # 0.705 is the "golden pocket"
            "impulse_high": swing_high,
            "impulse_low": swing_low
        }
    
    @staticmethod
    def detect_liquidity_sweeps(df: pd.DataFrame, liquidity_zones: Dict) -> Dict:
        """
        Detect when price sweeps liquidity (takes stops) then reverses
        - Price wicks above/below equal highs/lows
        - Then closes back inside range (rejection)
        """
        if len(df) < 5:
            return {"bullish_sweep": False, "bearish_sweep": False}
        
        recent_candles = df.tail(3)
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        bullish_sweep = False
        bearish_sweep = False
        swept_level = None
        
        # Check for bullish sweep (sweep sell-side liquidity then reverse up)
        # Price wicks below support/equal lows then closes higher
        sell_side_liquidity = liquidity_zones.get('sell_side_liquidity', [])
        
        for level in sell_side_liquidity:
            # Check if last candle wicked below level but closed above it
            if last_candle['low'] < level < last_candle['close']:
                # Confirm it's a rejection (close in upper 60% of candle)
                candle_range = last_candle['high'] - last_candle['low']
                close_position = (last_candle['close'] - last_candle['low']) / candle_range if candle_range > 0 else 0
                
                if close_position > 0.6:
                    bullish_sweep = True
                    swept_level = level
                    break
        
        # Check for bearish sweep (sweep buy-side liquidity then reverse down)
        # Price wicks above resistance/equal highs then closes lower
        buy_side_liquidity = liquidity_zones.get('buy_side_liquidity', [])
        
        for level in buy_side_liquidity:
            # Check if last candle wicked above level but closed below it
            if last_candle['high'] > level > last_candle['close']:
                # Confirm it's a rejection (close in lower 60% of candle)
                candle_range = last_candle['high'] - last_candle['low']
                close_position = (last_candle['close'] - last_candle['low']) / candle_range if candle_range > 0 else 0
                
                if close_position < 0.4:
                    bearish_sweep = True
                    swept_level = level
                    break
        
        return {
            "bullish_sweep": bullish_sweep,
            "bearish_sweep": bearish_sweep,
            "swept_level": swept_level
        }
    
    @staticmethod
    def detect_breaker_blocks(df: pd.DataFrame, order_blocks: Dict, structure: Dict) -> Dict:
        """
        Breaker Block = Failed Order Block that becomes opposite signal
        When price breaks through OB without respect, it becomes a Breaker
        """
        if len(df) < 10:
            return {"bullish_breaker": [], "bearish_breaker": []}
        
        current_price = df['close'].iloc[-1]
        recent_high = df.tail(5)['high'].max()
        recent_low = df.tail(5)['low'].min()
        
        bullish_breakers = []
        bearish_breakers = []
        
        # Check bullish OBs that got broken (become bearish breakers)
        for ob in order_blocks.get('bullish_ob', []):
            # If price broke significantly below a bullish OB, it becomes a bearish breaker
            if current_price < ob['low'] * 0.995:
                bearish_breakers.append({
                    'high': ob['high'],
                    'low': ob['low'],
                    'strength': ob['strength'] * 0.8,  # Breakers slightly less reliable
                    'type': 'FAILED_BULLISH_OB'
                })
        
        # Check bearish OBs that got broken (become bullish breakers)
        for ob in order_blocks.get('bearish_ob', []):
            # If price broke significantly above a bearish OB, it becomes a bullish breaker
            if current_price > ob['high'] * 1.005:
                bullish_breakers.append({
                    'high': ob['high'],
                    'low': ob['low'],
                    'strength': ob['strength'] * 0.8,
                    'type': 'FAILED_BEARISH_OB'
                })
        
        return {
            "bullish_breaker": bullish_breakers[:2],  # Keep top 2
            "bearish_breaker": bearish_breakers[:2]
        }
    
    @staticmethod
    def check_price_at_key_level(
        current_price: float, 
        key_levels: List[Dict], 
        tolerance_pct: float = 0.3
    ) -> Optional[Dict]:
        """
        Check if current price is AT (not just near) a key ICT level
        
        key_levels = [
            {"type": "ORDER_BLOCK", "price": 45000, "high": 45100, "low": 44900, "confluence": 5},
            {"type": "FVG_50", "price": 44500, "confluence": 3},
            {"type": "OTE_0.705", "price": 44200, "confluence": 4},
            ...
        ]
        
        Returns the key level dict if price is within tolerance, else None
        """
        for level in key_levels:
            level_price = level.get('price', 0)
            level_high = level.get('high', level_price)
            level_low = level.get('low', level_price)
            
            # Calculate tolerance
            tolerance = level_price * (tolerance_pct / 100)
            
            # Check if price is within tolerance of the level
            if level_low - tolerance <= current_price <= level_high + tolerance:
                return level
        
        return None
    
    @staticmethod
    def wait_for_confirmation(df: pd.DataFrame, signal_direction: str, key_level: Dict) -> bool:
        """
        Wait for confirmation candle before triggering signal:
        - For LONG: Bullish candle close above key level OR bullish rejection wick
        - For SHORT: Bearish candle close below key level OR bearish rejection wick
        - Check last 1-2 candles
        
        Returns True if confirmed, False if waiting
        """
        if len(df) < 2:
            return False
        
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        level_price = key_level.get('price', 0)
        level_high = key_level.get('high', level_price)
        level_low = key_level.get('low', level_price)
        
        if signal_direction == "LONG":
            # Check for bullish confirmation
            # 1. Bullish candle (close > open)
            is_bullish_candle = last_candle['close'] > last_candle['open']
            
            # 2. Close above key level
            closes_above = last_candle['close'] > level_low
            
            # 3. OR bullish rejection wick (long lower wick, close in upper half)
            candle_range = last_candle['high'] - last_candle['low']
            lower_wick = last_candle['open'] - last_candle['low'] if last_candle['close'] > last_candle['open'] else last_candle['close'] - last_candle['low']
            close_position = (last_candle['close'] - last_candle['low']) / candle_range if candle_range > 0 else 0
            
            has_rejection_wick = lower_wick > candle_range * 0.4 and close_position > 0.6
            
            return (is_bullish_candle and closes_above) or has_rejection_wick
            
        elif signal_direction == "SHORT":
            # Check for bearish confirmation
            # 1. Bearish candle (close < open)
            is_bearish_candle = last_candle['close'] < last_candle['open']
            
            # 2. Close below key level
            closes_below = last_candle['close'] < level_high
            
            # 3. OR bearish rejection wick (long upper wick, close in lower half)
            candle_range = last_candle['high'] - last_candle['low']
            upper_wick = last_candle['high'] - last_candle['open'] if last_candle['close'] < last_candle['open'] else last_candle['high'] - last_candle['close']
            close_position = (last_candle['close'] - last_candle['low']) / candle_range if candle_range > 0 else 0
            
            has_rejection_wick = upper_wick > candle_range * 0.4 and close_position < 0.4
            
            return (is_bearish_candle and closes_below) or has_rejection_wick
        
        return False
    
    @staticmethod
    def calculate_limit_orders(
        signal: str,
        current_price: float,
        order_blocks: Dict,
        fvgs: Dict,
        ote_zones: Dict,
        zones: Dict,
        breakers: Dict
    ) -> List[Dict]:
        """
        Calculate optimal limit order entry levels with confluence ranking
        
        Returns list of entry levels sorted by confluence (best first)
        """
        limit_levels = []
        
        if signal == "LONG":
            # Order Block lows (demand zones)
            for ob in order_blocks.get('bullish_ob', [])[:3]:
                if ob['low'] < current_price:
                    confluence = 3  # Base confluence
                    confluence += min(int(ob['strength']), 3)  # Add strength
                    
                    limit_levels.append({
                        "price": ob['low'],
                        "type": "ORDER_BLOCK_LOW",
                        "confluence": confluence,
                        "description": f"Bullish Order Block (Strength: {ob['strength']:.1f})"
                    })
            
            # FVG midpoints
            for fvg in fvgs.get('bullish_fvg', [])[:2]:
                if fvg['bottom'] < current_price:
                    midpoint = (fvg['top'] + fvg['bottom']) / 2
                    confluence = 2
                    
                    limit_levels.append({
                        "price": midpoint,
                        "type": "FVG_MIDPOINT",
                        "confluence": confluence,
                        "description": f"FVG 50% Fill (${fvg['bottom']:.2f}-${fvg['top']:.2f})"
                    })
            
            # OTE levels
            if ote_zones and ote_zones.get('direction') == "BULLISH":
                for fib_level in ['ote_0.62', 'ote_0.705', 'ote_0.79']:
                    price = ote_zones.get(fib_level)
                    if price and price < current_price:
                        confluence = 4 if '705' in fib_level else 3
                        
                        limit_levels.append({
                            "price": price,
                            "type": f"OTE_{fib_level.split('_')[1]}",
                            "confluence": confluence,
                            "description": f"Optimal Trade Entry {fib_level.split('_')[1]}"
                        })
            
            # Discount zone levels
            if zones and zones.get('current_zone') == "DISCOUNT":
                equilibrium = zones.get('equilibrium')
                if equilibrium and equilibrium < current_price:
                    limit_levels.append({
                        "price": equilibrium,
                        "type": "EQUILIBRIUM",
                        "confluence": 2,
                        "description": "50% Equilibrium Level"
                    })
            
            # Breaker blocks
            for breaker in breakers.get('bullish_breaker', []):
                if breaker['low'] < current_price:
                    limit_levels.append({
                        "price": breaker['low'],
                        "type": "BREAKER_BLOCK",
                        "confluence": 3,
                        "description": "Bullish Breaker Block"
                    })
        
        elif signal == "SHORT":
            # Order Block highs (supply zones)
            for ob in order_blocks.get('bearish_ob', [])[:3]:
                if ob['high'] > current_price:
                    confluence = 3
                    confluence += min(int(ob['strength']), 3)
                    
                    limit_levels.append({
                        "price": ob['high'],
                        "type": "ORDER_BLOCK_HIGH",
                        "confluence": confluence,
                        "description": f"Bearish Order Block (Strength: {ob['strength']:.1f})"
                    })
            
            # FVG midpoints
            for fvg in fvgs.get('bearish_fvg', [])[:2]:
                if fvg['top'] > current_price:
                    midpoint = (fvg['top'] + fvg['bottom']) / 2
                    confluence = 2
                    
                    limit_levels.append({
                        "price": midpoint,
                        "type": "FVG_MIDPOINT",
                        "confluence": confluence,
                        "description": f"FVG 50% Fill (${fvg['bottom']:.2f}-${fvg['top']:.2f})"
                    })
            
            # OTE levels
            if ote_zones and ote_zones.get('direction') == "BEARISH":
                for fib_level in ['ote_0.62', 'ote_0.705', 'ote_0.79']:
                    price = ote_zones.get(fib_level)
                    if price and price > current_price:
                        confluence = 4 if '705' in fib_level else 3
                        
                        limit_levels.append({
                            "price": price,
                            "type": f"OTE_{fib_level.split('_')[1]}",
                            "confluence": confluence,
                            "description": f"Optimal Trade Entry {fib_level.split('_')[1]}"
                        })
            
            # Premium zone levels
            if zones and zones.get('current_zone') == "PREMIUM":
                equilibrium = zones.get('equilibrium')
                if equilibrium and equilibrium > current_price:
                    limit_levels.append({
                        "price": equilibrium,
                        "type": "EQUILIBRIUM",
                        "confluence": 2,
                        "description": "50% Equilibrium Level"
                    })
            
            # Breaker blocks
            for breaker in breakers.get('bearish_breaker', []):
                if breaker['high'] > current_price:
                    limit_levels.append({
                        "price": breaker['high'],
                        "type": "BREAKER_BLOCK",
                        "confluence": 3,
                        "description": "Bearish Breaker Block"
                    })
        
        # Sort by confluence (highest first) and return top 5
        limit_levels.sort(key=lambda x: x['confluence'], reverse=True)
        return limit_levels[:5]
    
    @staticmethod
    def generate_smc_signal(df: pd.DataFrame, current_time: datetime = None) -> Tuple:
        """
        Enhanced ICT signal generation with:
        1. Killzone timing
        2. Liquidity sweeps
        3. OTE entries
        4. Breaker blocks
        5. Multi-level confluence scoring
        
        Returns: (signal, strength, confluences, confidence, key_levels, killzone_data, ote_zones, limit_orders)
        """
        if len(df) < 20:
            return "HOLD", "WEAK", ["Insufficient data for ICT analysis"], 30, [], {}, {}, []
        
        if current_time is None:
            current_time = datetime.now(pytz.UTC)
        
        confluences = []
        bullish_score = 0
        bearish_score = 0
        key_levels = []  # Track all key levels for confirmation
        
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
                key_levels.append({
                    "type": "ORDER_BLOCK",
                    "price": ob['low'],
                    "high": ob['high'],
                    "low": ob['low'],
                    "confluence": min(int(ob['strength']) + 3, 6)
                })
                break
        
        # Check if price near bearish OB
        for ob in order_blocks['bearish_ob']:
            if ob['low'] <= current_price <= ob['high']:
                confluences.append(f"🔴 Price at Bearish Order Block (Strength: {ob['strength']:.1f})")
                bearish_score += 2.5
                key_levels.append({
                    "type": "ORDER_BLOCK",
                    "price": ob['high'],
                    "high": ob['high'],
                    "low": ob['low'],
                    "confluence": min(int(ob['strength']) + 3, 6)
                })
                break
        
        # 3. Fair Value Gaps
        fvgs = SMCStrategy.detect_fair_value_gaps(df)
        
        # Bullish FVG below price (potential support)
        for fvg in fvgs['bullish_fvg']:
            if current_price >= fvg['bottom'] and current_price <= fvg['top'] * 1.02:
                confluences.append(f"📈 Bullish FVG nearby (${fvg['bottom']:.2f}-${fvg['top']:.2f})")
                bullish_score += 1.5
                midpoint = (fvg['top'] + fvg['bottom']) / 2
                key_levels.append({
                    "type": "FVG_MIDPOINT",
                    "price": midpoint,
                    "high": fvg['top'],
                    "low": fvg['bottom'],
                    "confluence": 3
                })
                break
        
        # Bearish FVG above price (potential resistance)
        for fvg in fvgs['bearish_fvg']:
            if current_price <= fvg['top'] and current_price >= fvg['bottom'] * 0.98:
                confluences.append(f"📉 Bearish FVG nearby (${fvg['bottom']:.2f}-${fvg['top']:.2f})")
                bearish_score += 1.5
                midpoint = (fvg['top'] + fvg['bottom']) / 2
                key_levels.append({
                    "type": "FVG_MIDPOINT",
                    "price": midpoint,
                    "high": fvg['top'],
                    "low": fvg['bottom'],
                    "confluence": 3
                })
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
        
        # 8. Killzone Check (NEW)
        killzone_data = SMCStrategy.is_in_killzone(current_time)
        if killzone_data['in_killzone']:
            confluences.append(f"⏰ {killzone_data['killzone_name']} Killzone - {killzone_data['description']}")
            # Boost scores in killzone
            if bullish_score > bearish_score:
                bullish_score *= killzone_data['probability_multiplier']
            elif bearish_score > bullish_score:
                bearish_score *= killzone_data['probability_multiplier']
        
        # 9. OTE Zones (NEW)
        ote_zones = SMCStrategy.calculate_ote_zones(df, structure)
        if ote_zones and ote_zones.get('in_ote_zone'):
            confluences.append(f"🎯 Price in OTE Zone ({ote_zones['direction']}) - Optimal entry range")
            if ote_zones['direction'] == "BULLISH":
                bullish_score += 2
                # Add OTE levels to key levels
                key_levels.append({
                    "type": "OTE_0.705",
                    "price": ote_zones['ote_0.705'],
                    "confluence": 4,
                    "description": "Optimal Trade Entry (Golden Pocket)"
                })
            else:
                bearish_score += 2
                key_levels.append({
                    "type": "OTE_0.705",
                    "price": ote_zones['ote_0.705'],
                    "confluence": 4,
                    "description": "Optimal Trade Entry (Golden Pocket)"
                })
        
        # 10. Liquidity Sweeps (NEW)
        sweeps = SMCStrategy.detect_liquidity_sweeps(df, liquidity)
        if sweeps['bullish_sweep']:
            confluences.append(f"🌊 Bullish Liquidity Sweep @ ${sweeps['swept_level']:,.2f} - Stops taken, reversal likely")
            bullish_score += 3
        if sweeps['bearish_sweep']:
            confluences.append(f"🌊 Bearish Liquidity Sweep @ ${sweeps['swept_level']:,.2f} - Stops taken, reversal likely")
            bearish_score += 3
        
        # 11. Breaker Blocks (NEW)
        breakers = SMCStrategy.detect_breaker_blocks(df, order_blocks, structure)
        current_price = df['close'].iloc[-1]
        
        for breaker in breakers['bullish_breaker']:
            if breaker['low'] <= current_price <= breaker['high']:
                confluences.append(f"⚡ Price at Bullish Breaker Block - Failed resistance becomes support")
                bullish_score += 2
                key_levels.append({
                    "type": "BREAKER_BLOCK",
                    "price": breaker['low'],
                    "high": breaker['high'],
                    "low": breaker['low'],
                    "confluence": 3
                })
        
        for breaker in breakers['bearish_breaker']:
            if breaker['low'] <= current_price <= breaker['high']:
                confluences.append(f"⚡ Price at Bearish Breaker Block - Failed support becomes resistance")
                bearish_score += 2
                key_levels.append({
                    "type": "BREAKER_BLOCK",
                    "price": breaker['high'],
                    "high": breaker['high'],
                    "low": breaker['low'],
                    "confluence": 3
                })
        
        # Determine final signal
        total_score = bullish_score + bearish_score
        
        if total_score == 0:
            return "HOLD", "WEAK", confluences, 30, key_levels, killzone_data, ote_zones, []
        
        if bullish_score > bearish_score:
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
        
        # Calculate limit orders for best entry points
        zones = SMCStrategy.calculate_premium_discount_zones(df)
        limit_orders = SMCStrategy.calculate_limit_orders(
            signal, current_price, order_blocks, fvgs, ote_zones, zones, breakers
        )
        
        return signal, strength, confluences, round(confidence, 2), key_levels, killzone_data, ote_zones, limit_orders

