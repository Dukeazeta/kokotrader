# Crypto Futures Signals Bot - Backend

Python backend service for generating crypto perpetual futures trading signals.

## Features

- **Live Price Fetching**: Real-time price data from Binance futures
- **Technical Indicators**: RSI, MACD, EMAs, Bollinger Bands, Stochastic, ADX, ATR
- **Signal Generation**: LONG/SHORT/HOLD signals with confidence scores
- **Multi-Confluence Analysis**: Combines multiple indicators for reliable signals
- **Risk Management**: Automatic stop loss and take profit calculations
- **WebSocket Support**: Real-time signal updates
- **REST API**: Easy integration with frontend

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Health check
- `GET /api/price/{symbol}` - Get current price
- `GET /api/signals/{symbol}?timeframe=15m` - Get trading signal
- `GET /api/ohlcv/{symbol}?timeframe=15m&limit=100` - Get OHLCV data for charts
- `WS /ws` - WebSocket for real-time updates

## Trading Signals

The bot generates signals based on:

1. **RSI**: Oversold/overbought conditions
2. **MACD**: Momentum and trend direction
3. **EMAs**: Moving average alignments (9, 21, 50, 200)
4. **Bollinger Bands**: Volatility and price extremes
5. **Stochastic**: Momentum oscillator
6. **ADX**: Trend strength
7. **Volume**: Confirmation of moves

Each signal includes:
- Signal type (LONG/SHORT/HOLD)
- Strength (STRONG/MODERATE/WEAK)
- Confidence score (0-100)
- Entry price
- Stop loss
- Take profit levels (TP1, TP2, TP3)
- Risk/reward ratio
- Position size suggestion

## Supported Symbols

Any symbol available on Binance Futures, e.g.:
- BTC/USDT
- ETH/USDT
- SOL/USDT
- etc.

## Timeframes

Supported timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d


