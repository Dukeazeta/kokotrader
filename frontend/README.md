# Crypto Futures Signals Bot - Frontend

Modern React frontend for the Crypto Futures Signals Bot.

## Features

- **Real-time Signal Display**: Live trading signals with confidence scores
- **Interactive Price Charts**: Candlestick charts with technical indicators
- **Multiple Symbols**: Support for BTC, ETH, SOL, and more
- **Multiple Timeframes**: 1m, 5m, 15m, 30m, 1h, 4h, 1d
- **WebSocket Support**: Real-time updates every 30 seconds
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Beautiful dark theme with gradient accents

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Components

- **Header**: Top navigation with status indicators
- **SymbolSelector**: Choose trading pair and timeframe
- **SignalCard**: Main trading signal display with entry/exit levels
- **PriceChart**: Candlestick chart visualization
- **IndicatorsPanel**: Grid of technical indicators

## Configuration

The API endpoint can be configured in `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000'
const WS_URL = 'ws://localhost:8000/ws'
```

## Tech Stack

- React 18
- Vite (build tool)
- Recharts (charting library)
- Axios (HTTP client)
- Lucide React (icons)


