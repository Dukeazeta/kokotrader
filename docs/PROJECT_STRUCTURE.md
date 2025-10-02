# Project Structure

```
kokotrader/
├── backend/                          # Python FastAPI Backend
│   ├── models/                       # Data models
│   │   ├── __init__.py
│   │   └── signal.py                # Signal and price data models
│   │
│   ├── services/                     # Business logic
│   │   ├── __init__.py
│   │   ├── price_service.py         # CCXT price fetching service
│   │   ├── indicators.py            # Technical indicators calculations
│   │   └── signal_service.py        # Signal generation engine
│   │
│   ├── main.py                      # FastAPI app & WebSocket server
│   ├── requirements.txt             # Python dependencies
│   └── README.md                    # Backend documentation
│
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── Header.jsx          # Top navigation bar
│   │   │   ├── Header.css
│   │   │   ├── SymbolSelector.jsx  # Symbol & timeframe picker
│   │   │   ├── SymbolSelector.css
│   │   │   ├── SignalCard.jsx      # Main signal display
│   │   │   ├── SignalCard.css
│   │   │   ├── PriceChart.jsx      # Candlestick chart
│   │   │   ├── PriceChart.css
│   │   │   ├── IndicatorsPanel.jsx # Technical indicators grid
│   │   │   └── IndicatorsPanel.css
│   │   │
│   │   ├── services/                # API services
│   │   │   └── api.js              # HTTP & WebSocket client
│   │   │
│   │   ├── App.jsx                 # Main app component
│   │   ├── App.css                 # App styles
│   │   ├── main.jsx                # React entry point
│   │   └── index.css               # Global styles
│   │
│   ├── index.html                   # HTML template
│   ├── package.json                 # Node.js dependencies
│   ├── vite.config.js              # Vite configuration
│   └── README.md                    # Frontend documentation
│
├── start.sh                         # Quick start script (Unix)
├── start.bat                        # Quick start script (Windows)
├── README.md                        # Main documentation
├── QUICKSTART.md                    # Quick start guide
├── PROJECT_STRUCTURE.md             # This file
├── LICENSE                          # MIT License
└── .gitignore                       # Git ignore rules
```

## Architecture Overview

### Backend (Python)

**FastAPI Server** (`main.py`)
- RESTful API endpoints
- WebSocket server for real-time updates
- CORS middleware for frontend integration

**Services Layer**
1. **PriceService** - Fetches live prices from Binance via CCXT
2. **TechnicalIndicators** - Calculates 15+ technical indicators
3. **SignalService** - Analyzes confluences & generates signals

**Models Layer**
- `SignalResponse` - Complete signal with entry/exit levels
- `PriceData` - Current price information

### Frontend (React)

**Main App** (`App.jsx`)
- State management for symbols, timeframes, signals
- Data fetching and WebSocket connection
- Auto-refresh every 30 seconds

**Components**
1. **Header** - Navigation with live status indicator
2. **SymbolSelector** - Dropdown menus for symbol/timeframe
3. **SignalCard** - Main signal display with all trading info
4. **PriceChart** - Line chart with reference levels
5. **IndicatorsPanel** - Grid of technical indicators

**Services**
- `api.js` - Axios HTTP client & WebSocket connection

## Data Flow

```
┌─────────────┐
│   Binance   │
│  Futures    │
└──────┬──────┘
       │
       │ CCXT Library
       ▼
┌─────────────────┐
│  PriceService   │
│  (Fetch OHLCV)  │
└────────┬────────┘
         │
         ▼
┌────────────────────┐
│TechnicalIndicators │
│  (Calculate RSI,   │
│   MACD, EMAs...)   │
└─────────┬──────────┘
          │
          ▼
┌──────────────────┐
│  SignalService   │
│  (Analyze & Gen  │
│    Signal)       │
└────────┬─────────┘
         │
         │ REST API & WebSocket
         ▼
┌─────────────────┐
│  React Frontend │
│  (Dashboard UI) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│      User       │
└─────────────────┘
```

## Technical Stack

### Backend
- **FastAPI** - Modern Python web framework
- **CCXT** - Cryptocurrency exchange library
- **Pandas** - Data manipulation
- **TA** - Technical analysis indicators
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time communication

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool & dev server
- **Recharts** - Charting library
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Key Features Implementation

### 1. Signal Generation
**File**: `backend/services/signal_service.py`

Analyzes 7 confluences:
- RSI (oversold/overbought)
- MACD (momentum)
- EMA alignment (trend)
- Bollinger Bands (volatility)
- Stochastic (momentum confirmation)
- ADX (trend strength)
- Volume (confirmation)

Scoring system: 0-10.5 points → Confidence %

### 2. Risk Management
**File**: `backend/services/signal_service.py` → `_calculate_levels()`

- Stop loss based on ATR (Average True Range)
- 3 take profit levels with different R:R ratios
- Position sizing based on confidence & volatility
- Adjusts for HIGH/MEDIUM/LOW volatility

### 3. Real-time Updates
**Backend**: `backend/main.py` → WebSocket endpoint
**Frontend**: `frontend/src/services/api.js` → `connectWebSocket()`

- Server pushes updates every 30 seconds
- Frontend auto-refreshes data
- Live connection status indicator

### 4. Technical Indicators
**File**: `backend/services/indicators.py`

Calculates:
- Moving Averages: EMA 9, 21, 50, 200
- Momentum: RSI, MACD, Stochastic
- Trend: ADX, +DI, -DI
- Volatility: Bollinger Bands, ATR
- Volume: Ratio vs 20-period average

### 5. Chart Visualization
**File**: `frontend/src/components/PriceChart.jsx`

- Recharts LineChart with OHLCV data
- Reference lines for entry, SL, TP1
- Custom tooltip with price info
- Responsive design

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/price/{symbol}` | Current price |
| GET | `/api/signals/{symbol}` | Trading signal |
| GET | `/api/ohlcv/{symbol}` | Chart data |
| WS | `/ws` | Real-time updates |

## Environment Variables

Backend (`.env`):
```env
EXCHANGE=binance
SYMBOL=BTC/USDT
TIMEFRAME=15m
PORT=8000
```

Frontend (`vite.config.js`):
- API Proxy to backend
- Port 3000

## Extension Points

### Adding New Indicators
1. Add calculation in `backend/services/indicators.py`
2. Use in `signal_service.py` for confluences
3. Display in `frontend/src/components/IndicatorsPanel.jsx`

### Adding New Exchanges
1. Modify `backend/services/price_service.py`
2. Change exchange_id parameter
3. Ensure CCXT supports the exchange

### Adding New Symbols
1. Update `SYMBOLS` array in `frontend/src/components/SymbolSelector.jsx`
2. Ensure symbol exists on the exchange

### Customizing Strategies
1. Modify confluence logic in `backend/services/signal_service.py`
2. Adjust scoring weights
3. Add new confluence checks

## Performance Considerations

- **Caching**: Consider Redis for price caching
- **Rate Limiting**: CCXT handles exchange rate limits
- **WebSocket**: Single connection serves all clients
- **Frontend**: React memoization for heavy components

## Security Notes

- No API keys required (read-only public data)
- CORS configured for localhost only
- No user authentication (single-user bot)
- No database (stateless)

## Future Enhancements

- [ ] Multiple exchange support
- [ ] Custom strategy builder
- [ ] Backtesting module
- [ ] Alert notifications (email, Telegram)
- [ ] Portfolio tracking
- [ ] Trade execution integration
- [ ] Historical signal performance
- [ ] Machine learning signal optimization

