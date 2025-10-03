from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import json
import os
from datetime import datetime

from services.price_service import PriceService
from services.signal_service_ict import ICTSignalService
from models.signal import SignalResponse

app = FastAPI(title="Crypto Futures Signals Bot")

# CORS middleware for React frontend

# Allow both localhost and production URLs
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# Add production frontend URL if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)
    # Also allow https version
    if frontend_url.startswith("http://"):
        allowed_origins.append(frontend_url.replace("http://", "https://"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
price_service = PriceService()
signal_service = ICTSignalService(price_service)  # ICT-Only signal service

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Crypto Futures Signals Bot API", "status": "running"}

@app.get("/api/price/{symbol}")
async def get_current_price(symbol: str):
    """Get current price for a symbol"""
    price_data = await price_service.get_current_price(symbol.replace("-", "/"))
    return price_data

@app.get("/api/signals/{symbol}", response_model=SignalResponse)
async def get_signal(symbol: str, timeframe: str = "15m"):
    """
    Get ICT trading signal for a symbol
    
    Args:
        symbol: Trading pair (use - instead of /, e.g., BTC-USDT)
        timeframe: Candlestick timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
    """
    signal = await signal_service.generate_signal(symbol.replace("-", "/"), timeframe)
    return signal

@app.get("/api/signals/multi/{symbols}")
async def get_multi_signals(symbols: str, timeframe: str = "15m"):
    """Get trading signals for multiple symbols (comma-separated)"""
    symbol_list = [s.strip().replace("-", "/") for s in symbols.split(",")]
    signals = []
    
    for symbol in symbol_list:
        try:
            signal = await signal_service.generate_signal(symbol, timeframe)
            signals.append(signal.model_dump())
        except Exception as e:
            signals.append({
                "symbol": symbol,
                "error": str(e),
                "timeframe": timeframe
            })
    
    return {"signals": signals, "count": len(signals)}

@app.get("/api/ohlcv/{symbol}")
async def get_ohlcv(symbol: str, timeframe: str = "15m", limit: int = 100):
    """Get OHLCV data for charting"""
    ohlcv = await price_service.get_ohlcv(symbol.replace("-", "/"), timeframe, limit)
    return {"data": ohlcv}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time ICT signal updates"""
    await manager.connect(websocket)
    try:
        # Send initial data
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to ICT signals stream"
        })
        
        # Keep sending updates
        while True:
            try:
                # Read query params for symbol/timeframe
                params = websocket.query_params
                symbol = params.get("symbol", "BTC/USDT")
                timeframe = params.get("timeframe", "15m")

                # Generate ICT signal
                signal = await signal_service.generate_signal(symbol, timeframe)
                
                await websocket.send_json({
                    "type": "signal_update",
                    "data": signal.model_dump(),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Wait 30 seconds before next update
                await asyncio.sleep(30)
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                await asyncio.sleep(30)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable for production, default to 8000 for local dev
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

