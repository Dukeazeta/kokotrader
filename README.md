# Crypto Perpetual Futures Signals Bot

A comprehensive cryptocurrency perpetual futures trading signals bot with Python backend and React frontend. Get real-time trading signals with multiple technical indicators, confluences, and risk management.

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

### Trading Signals
- **LONG/SHORT/HOLD Signals** with confidence scores (0-100%)
- **Multiple Confluences** combining 7+ technical indicators
- **Automatic Entry/Exit Levels** with stop loss and 3 take profit targets
- **Risk Management** with position sizing suggestions
- **Real-time Updates** via WebSocket (every 30 seconds)

### Technical Analysis
- **Trend Indicators**: EMA (9, 21, 50, 200), MACD, ADX
- **Momentum**: RSI, Stochastic Oscillator
- **Volatility**: Bollinger Bands, ATR
- **Volume Analysis**: Volume ratio and confirmation
- **Market Context**: Trend detection (Bullish/Bearish/Neutral/Ranging)

### User Interface
- 📊 **Interactive Price Charts** with candlestick visualization
- 📈 **Technical Indicators Panel** with real-time values
- 🎯 **Signal Dashboard** with clear entry/exit recommendations
- 📱 **Responsive Design** for desktop and mobile
- 🌙 **Modern Dark Theme** with beautiful gradients

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## 🛠️ Installation

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 🎯 Usage

1. **Select Symbol**: Choose from BTC/USDT, ETH/USDT, SOL/USDT, etc.
2. **Select Timeframe**: Choose from 1m, 5m, 15m, 30m, 1h, 4h, 1d
3. **View Signal**: Check the trading signal, confidence, and confluences
4. **Entry/Exit Levels**: Use the provided stop loss and take profit levels
5. **Monitor Indicators**: Review technical indicators for confirmation

### Example Signal Output

```
Signal: LONG
Strength: STRONG
Confidence: 87.5%

Entry Price: $42,500
Stop Loss: $42,100
Take Profit 1: $43,200
Take Profit 2: $43,800
Take Profit 3: $44,500

Risk/Reward: 1:2.5
Position Size: MEDIUM (2-3% of portfolio)

Confluences:
- RSI oversold (< 30) - Bullish reversal potential
- MACD bullish crossover - Upward momentum
- EMAs aligned bullish (9 > 21 > 50)
- Price above EMA 21 - Bullish context
- Strong bullish trend (ADX: 32.5)
```

## 🔌 API Endpoints

- `GET /` - Health check
- `GET /api/price/{symbol}` - Get current price
- `GET /api/signals/{symbol}?timeframe=15m` - Get trading signal
- `GET /api/ohlcv/{symbol}?timeframe=15m&limit=100` - Get chart data
- `WS /ws` - WebSocket for real-time updates

## 📊 Supported Exchanges

Currently supports Binance Futures. Can be extended to:
- Bybit
- OKX
- Kraken
- And any exchange supported by CCXT

## 📈 Supported Symbols

Any perpetual futures pair available on Binance:
- BTC/USDT
- ETH/USDT
- SOL/USDT
- BNB/USDT
- XRP/USDT
- ADA/USDT
- And 100+ more

## ⚙️ Configuration

### Backend Configuration
Edit `backend/.env`:
```env
EXCHANGE=binance
SYMBOL=BTC/USDT
TIMEFRAME=15m
PORT=8000
```

### Frontend Configuration
Edit `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000'
const WS_URL = 'ws://localhost:8000/ws'
```

## 🧪 Signal Confidence Calculation

The bot uses a scoring system based on multiple confluences:

1. **RSI** (0-2 points): Oversold/overbought conditions
2. **MACD** (0-2 points): Crossovers and momentum
3. **EMA Alignment** (0-3 points): Moving average structure
4. **Bollinger Bands** (0-1 point): Price extremes
5. **Stochastic** (0-1 point): Momentum confirmation
6. **ADX** (0-1 point): Trend strength
7. **Volume** (0-0.5 points): Move confirmation

**Total possible score**: 10.5 points
**Confidence %**: (score / total_possible) × 100

## 📚 Documentation

Complete documentation is available in the [docs](docs/) directory:

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **[Features Overview](docs/FEATURES.md)** - Complete list of current features
- **[Configuration Guide](docs/CONFIGURATION.md)** - Customize the bot to your needs
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Architecture and data flow
- **[Development Roadmap](docs/ROADMAP.md)** - Future features and improvements

Also check component-specific documentation:
- [Backend Documentation](backend/README.md) - API and backend services
- [Frontend Documentation](frontend/README.md) - UI components and React app

## ⚠️ Risk Disclaimer

**This bot is for educational and informational purposes only.**

- Trading cryptocurrencies involves substantial risk of loss
- Past performance does not guarantee future results
- Never invest more than you can afford to lose
- Always do your own research (DYOR)
- Use proper risk management and position sizing
- The signals are not financial advice

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- CCXT library for exchange connectivity
- TA library for technical indicators
- FastAPI for the backend framework
- React and Recharts for the frontend

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the documentation in the [docs](docs/) directory
- Review backend docs: [backend/README.md](backend/README.md)
- Review frontend docs: [frontend/README.md](frontend/README.md)

---

**Happy Trading! 📈🚀**

*Remember: Always trade responsibly and manage your risk.*

