# Configuration Guide

This guide explains how to customize your Crypto Futures Signals Bot.

## Table of Contents
- [Backend Configuration](#backend-configuration)
- [Frontend Configuration](#frontend-configuration)
- [Trading Strategy Customization](#trading-strategy-customization)
- [Indicator Customization](#indicator-customization)
- [Exchange Configuration](#exchange-configuration)

---

## Backend Configuration

### Changing the Exchange

**File**: `backend/services/price_service.py`

```python
def __init__(self, exchange_id: str = "binance"):
    self.exchange_id = exchange_id
    self.exchange = getattr(ccxt, exchange_id)({
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',  # 'spot' for spot trading
        }
    })
```

Supported exchanges (via CCXT):
- `binance` - Binance Futures (default)
- `bybit` - Bybit Perpetual
- `okx` - OKX Futures
- `kraken` - Kraken Futures
- `kucoin` - KuCoin Futures

### Adjusting Signal Confidence Thresholds

**File**: `backend/services/signal_service.py`

Find the `_analyze_confluences` method and adjust scoring:

```python
# Current scoring
if rsi < 30:
    bullish_score += 2  # Change this value (0-3)
elif rsi < 40:
    bullish_score += 1  # Adjust threshold and score
```

### Customizing Stop Loss & Take Profit Levels

**File**: `backend/services/signal_service.py`

In the `_calculate_levels` method:

```python
# Adjust multipliers based on volatility
if volatility == "HIGH":
    sl_multiplier = 2.5      # Default: 2.5x ATR
    tp_multipliers = [2, 3.5, 5]  # TP1, TP2, TP3
elif volatility == "LOW":
    sl_multiplier = 1.5      # Default: 1.5x ATR
    tp_multipliers = [1.5, 2.5, 3.5]
else:  # MEDIUM
    sl_multiplier = 2        # Default: 2x ATR
    tp_multipliers = [2, 3, 4.5]
```

**More Conservative** (tighter stops):
```python
if volatility == "HIGH":
    sl_multiplier = 2.0
    tp_multipliers = [1.5, 2.5, 4]
```

**More Aggressive** (wider stops, bigger targets):
```python
if volatility == "HIGH":
    sl_multiplier = 3.0
    tp_multipliers = [3, 5, 7]
```

### Changing Position Size Recommendations

**File**: `backend/services/signal_service.py`

In the `_suggest_position_size` method:

```python
if confidence >= 80 and volatility in ["LOW", "MEDIUM"]:
    return "LARGE (3-5% of portfolio)"  # Adjust percentages
elif confidence >= 70:
    return "MEDIUM (2-3% of portfolio)"
elif confidence >= 60:
    return "SMALL (1-2% of portfolio)"
else:
    return "MINIMAL (0.5-1% of portfolio)"
```

---

## Frontend Configuration

### Changing API Endpoint

**File**: `frontend/src/services/api.js`

```javascript
const API_BASE_URL = 'http://localhost:8000'  // Change to your backend URL
const WS_URL = 'ws://localhost:8000/ws'       // Change to your WebSocket URL
```

For production deployment:
```javascript
const API_BASE_URL = 'https://your-domain.com/api'
const WS_URL = 'wss://your-domain.com/ws'
```

### Adding More Symbols

**File**: `frontend/src/components/SymbolSelector.jsx`

```javascript
const SYMBOLS = [
  'BTC/USDT', 
  'ETH/USDT', 
  'SOL/USDT', 
  'BNB/USDT', 
  'XRP/USDT', 
  'ADA/USDT',
  // Add more symbols
  'DOGE/USDT',
  'MATIC/USDT',
  'AVAX/USDT',
]
```

### Changing Available Timeframes

**File**: `frontend/src/components/SymbolSelector.jsx`

```javascript
const TIMEFRAMES = [
  '1m',   // 1 minute
  '5m',   // 5 minutes
  '15m',  // 15 minutes (default)
  '30m',  // 30 minutes
  '1h',   // 1 hour
  '4h',   // 4 hours
  '1d',   // 1 day
  // Add more timeframes
  '1w',   // 1 week
  '1M',   // 1 month
]
```

### Adjusting Auto-Refresh Interval

**File**: `frontend/src/App.jsx`

```javascript
// Auto refresh every 30 seconds (default)
useEffect(() => {
  const interval = setInterval(() => {
    loadData()
  }, 30000)  // Change to 60000 for 1 minute, 10000 for 10 seconds, etc.

  return () => clearInterval(interval)
}, [symbol, timeframe])
```

### Customizing Colors & Theme

**File**: `frontend/src/index.css`

```css
body {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  /* Change gradient colors */
}

/* Primary color (purple/blue) */
/* Find and replace #6366f1 with your color */
```

**File**: `frontend/src/App.css`

```css
.badge-long {
  background: rgba(34, 197, 94, 0.2);  /* Green for LONG */
  color: #4ade80;
}

.badge-short {
  background: rgba(239, 68, 68, 0.2);  /* Red for SHORT */
  color: #f87171;
}
```

---

## Trading Strategy Customization

### Adding a New Confluence

**File**: `backend/services/signal_service.py`

In the `_analyze_confluences` method, add your custom logic:

```python
def _analyze_confluences(self, indicators: Dict[str, float], trend: str):
    # ... existing confluences ...
    
    # 8. Custom: Price Action Pattern
    current_price = indicators.get('current_price', 0)
    ema_9 = indicators.get('ema_9', 0)
    ema_21 = indicators.get('ema_21', 0)
    
    # Example: Bullish engulfing at support
    if current_price > ema_9 and ema_9 > ema_21:
        confluences.append("Price broke above EMAs - Bullish breakout")
        bullish_score += 1.5
    
    # Your custom confluence here...
```

### Creating a Custom Indicator

**File**: `backend/services/indicators.py`

Add your calculation in the `calculate_all` method:

```python
@staticmethod
def calculate_all(df: pd.DataFrame) -> Dict[str, float]:
    indicators = {}
    
    # ... existing indicators ...
    
    # Custom: Ichimoku Cloud
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    indicators['tenkan_sen'] = ((high_9 + low_9) / 2).iloc[-1]
    
    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    indicators['kijun_sen'] = ((high_26 + low_26) / 2).iloc[-1]
    
    return indicators
```

### Trend Detection Customization

**File**: `backend/services/indicators.py`

Modify the `detect_trend` method:

```python
@staticmethod
def detect_trend(df: pd.DataFrame, indicators: Dict[str, float]) -> str:
    ema_9 = indicators.get('ema_9', 0)
    ema_21 = indicators.get('ema_21', 0)
    ema_50 = indicators.get('ema_50', 0)
    adx = indicators.get('adx', 0)
    
    # More strict trend requirement
    if adx > 30:  # Changed from 25 to 30
        if ema_9 > ema_21 > ema_50:
            return "BULLISH"
        elif ema_9 < ema_21 < ema_50:
            return "BEARISH"
    
    # Ranging if ADX is very low
    if adx < 15:  # Changed from 20 to 15
        return "RANGING"
    
    return "NEUTRAL"
```

---

## Indicator Customization

### Changing RSI Period

**File**: `backend/services/indicators.py`

```python
# Default: 14-period RSI
rsi = RSIIndicator(close=df['close'], window=14)

# Change to 9-period RSI (faster)
rsi = RSIIndicator(close=df['close'], window=9)

# Or 21-period RSI (slower)
rsi = RSIIndicator(close=df['close'], window=21)
```

### Adjusting EMA Periods

**File**: `backend/services/indicators.py`

```python
# Default EMAs
ema_9 = EMAIndicator(close=df['close'], window=9)
ema_21 = EMAIndicator(close=df['close'], window=21)
ema_50 = EMAIndicator(close=df['close'], window=50)

# Custom EMAs (example: 8, 13, 34 - Fibonacci numbers)
ema_8 = EMAIndicator(close=df['close'], window=8)
ema_13 = EMAIndicator(close=df['close'], window=13)
ema_34 = EMAIndicator(close=df['close'], window=34)
```

### Changing Bollinger Bands Settings

**File**: `backend/services/indicators.py`

```python
# Default: 20-period, 2 standard deviations
bb = BollingerBands(close=df['close'], window=20, window_dev=2)

# More sensitive: 10-period, 1.5 std dev
bb = BollingerBands(close=df['close'], window=10, window_dev=1.5)

# Less sensitive: 30-period, 2.5 std dev
bb = BollingerBands(close=df['close'], window=30, window_dev=2.5)
```

---

## Exchange Configuration

### Adding API Keys (for Private Data)

**File**: `backend/services/price_service.py`

```python
def __init__(self, exchange_id: str = "binance"):
    self.exchange = getattr(ccxt, exchange_id)({
        'apiKey': 'YOUR_API_KEY',        # Add your API key
        'secret': 'YOUR_SECRET_KEY',     # Add your secret key
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
        }
    })
```

**Security Note**: Store keys in environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

self.exchange = getattr(ccxt, exchange_id)({
    'apiKey': os.getenv('EXCHANGE_API_KEY'),
    'secret': os.getenv('EXCHANGE_SECRET_KEY'),
    'enableRateLimit': True,
})
```

Create `.env` file:
```env
EXCHANGE_API_KEY=your_key_here
EXCHANGE_SECRET_KEY=your_secret_here
```

### Using Testnet

**File**: `backend/services/price_service.py`

```python
self.exchange = getattr(ccxt, exchange_id)({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    },
    'urls': {
        'api': {
            'public': 'https://testnet.binance.vision/api',  # Testnet URL
            'private': 'https://testnet.binance.vision/api',
        }
    }
})
```

---

## Advanced Configuration

### Rate Limiting

Adjust CCXT rate limiting:

```python
self.exchange = getattr(ccxt, exchange_id)({
    'enableRateLimit': True,
    'rateLimit': 1200,  # Milliseconds between requests (default varies)
})
```

### Data Limit for Analysis

**File**: `backend/services/price_service.py`

```python
async def get_ohlcv_df(self, symbol: str, timeframe: str = "15m", limit: int = 200):
    # Change limit to fetch more/less historical data
    # More data = more accurate long-term indicators but slower
    # Less data = faster but less accurate
```

### WebSocket Update Frequency

**File**: `backend/main.py`

```python
while True:
    signal = await signal_service.generate_signal("BTC/USDT", "15m")
    await websocket.send_json({...})
    
    # Wait 30 seconds before next update
    await asyncio.sleep(30)  # Change to 10, 60, 120, etc.
```

---

## Quick Reference

| What to Change | File | Line/Section |
|----------------|------|--------------|
| Exchange | `backend/services/price_service.py` | `__init__` |
| Symbols | `frontend/src/components/SymbolSelector.jsx` | `SYMBOLS` array |
| Timeframes | `frontend/src/components/SymbolSelector.jsx` | `TIMEFRAMES` array |
| Stop Loss/TP | `backend/services/signal_service.py` | `_calculate_levels` |
| Confluences | `backend/services/signal_service.py` | `_analyze_confluences` |
| Indicators | `backend/services/indicators.py` | `calculate_all` |
| Colors | `frontend/src/index.css`, `frontend/src/App.css` | CSS variables |
| API URL | `frontend/src/services/api.js` | `API_BASE_URL` |
| Refresh Rate | `frontend/src/App.jsx` | `setInterval` |

---

**Need Help?** Check the main [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md)

