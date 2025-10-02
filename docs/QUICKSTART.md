# Quick Start Guide

Get your Crypto Futures Signals Bot up and running in 5 minutes! 🚀

## Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ Node.js 16 or higher installed
- ✅ Internet connection for fetching live crypto prices

## Quick Start (Automated)

### Windows
Simply double-click `start.bat` or run:
```cmd
start.bat
```

### Mac/Linux
Make the script executable and run:
```bash
chmod +x start.sh
./start.sh
```

That's it! The bot will:
1. Install all dependencies
2. Start the backend server on port 8000
3. Start the frontend on port 3000
4. Open your browser automatically

## Manual Setup

If you prefer to start services manually:

### Step 1: Start the Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
python main.py
```

The backend API will be available at `http://localhost:8000`

### Step 2: Start the Frontend

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## First Use

1. **Open your browser** and navigate to `http://localhost:3000`

2. **Select a trading pair** (default: BTC/USDT)

3. **Select a timeframe** (default: 15m)

4. **View your signal**:
   - Signal type (LONG/SHORT/HOLD)
   - Confidence score
   - Entry price
   - Stop loss
   - Take profit levels (TP1, TP2, TP3)
   - Multiple confluences

5. **Monitor real-time updates** - The bot updates every 30 seconds

## Understanding the Dashboard

### Signal Card (Left Panel)
- **Signal Type**: LONG (buy), SHORT (sell), or HOLD (wait)
- **Strength**: STRONG, MODERATE, or WEAK
- **Confidence**: Percentage score (0-100%)
- **Entry Price**: Suggested entry point
- **Stop Loss**: Risk management level
- **Take Profits**: Three target levels
- **Confluences**: Reasons supporting the signal

### Price Chart (Right Panel)
- Real-time price candlestick chart
- Entry, stop loss, and TP1 levels marked
- Hover for detailed price information

### Indicators Panel (Bottom)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- ADX (Average Directional Index)
- EMAs (Exponential Moving Averages)
- Bollinger Bands
- Stochastic Oscillator
- ATR (Average True Range)
- Volume Analysis

## Changing Symbols

Click the **Symbol** dropdown to choose from:
- BTC/USDT (Bitcoin)
- ETH/USDT (Ethereum)
- SOL/USDT (Solana)
- BNB/USDT (Binance Coin)
- XRP/USDT (Ripple)
- ADA/USDT (Cardano)

## Changing Timeframes

Click the **Timeframe** dropdown to choose from:
- 1m (1 minute) - Very short-term
- 5m (5 minutes) - Short-term
- 15m (15 minutes) - Default, good for day trading
- 30m (30 minutes) - Medium-term
- 1h (1 hour) - Swing trading
- 4h (4 hours) - Position trading
- 1d (1 day) - Long-term

## Using the Signals

⚠️ **Important**: These signals are for educational purposes only. Always:

1. **Do Your Own Research (DYOR)**
2. **Never invest more than you can afford to lose**
3. **Use proper position sizing** (suggested in the signal)
4. **Always set stop losses**
5. **Take profits at multiple levels**
6. **Consider the confidence score** (>70% is generally more reliable)
7. **Check multiple timeframes for confirmation**

### Example Trading Strategy

1. **Wait for HIGH confidence signal** (>75%)
2. **Check confluences** - Look for 4+ positive indicators
3. **Verify trend direction** - Is it BULLISH or BEARISH?
4. **Enter at suggested entry price**
5. **Set stop loss immediately**
6. **Take 50% profit at TP1**
7. **Move stop loss to break-even**
8. **Take 30% profit at TP2**
9. **Let remaining 20% run to TP3**

## Troubleshooting

### Backend won't start
- Check if Python is installed: `python --version`
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use

### Frontend won't start
- Check if Node.js is installed: `node --version`
- Ensure all dependencies are installed: `npm install`
- Check if port 3000 is already in use
- Try clearing cache: `rm -rf node_modules && npm install`

### No data showing
- Ensure backend is running (`http://localhost:8000` should show a response)
- Check browser console for errors (F12)
- Verify internet connection (needed for live price data)

### WebSocket not connecting
- Backend must be running first
- Check for firewall blocking WebSocket connections
- Look for "Live" indicator in the top-right (green = connected)

## Next Steps

- ✅ Test different symbols and timeframes
- ✅ Learn to interpret the confluences
- ✅ Practice with paper trading first
- ✅ Customize indicators (see backend/services/indicators.py)
- ✅ Add more exchanges (modify backend/services/price_service.py)

## Getting Help

- Check the main [README.md](README.md) for detailed documentation
- Review backend docs: [backend/README.md](backend/README.md)
- Review frontend docs: [frontend/README.md](frontend/README.md)
- Open an issue on GitHub for bugs or questions

## Advanced Configuration

### Change the exchange
Edit `backend/services/price_service.py`:
```python
self.exchange = getattr(ccxt, "bybit")({  # Change to your exchange
    'enableRateLimit': True,
})
```

### Adjust indicator periods
Edit `backend/services/indicators.py` to customize EMAs, RSI periods, etc.

### Modify signal thresholds
Edit `backend/services/signal_service.py` to adjust confidence calculations

---

**Happy Trading! 📈**

Remember: This bot is a tool to assist your trading decisions, not replace them. Always use proper risk management!

