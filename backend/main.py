from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import json
from datetime import datetime

from services.price_service import PriceService
from services.signal_service import SignalService
from models.signal import SignalResponse

app = FastAPI(title="Crypto Futures Signals Bot")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
price_service = PriceService()
signal_service = SignalService(price_service)

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
    """Get trading signal for a symbol"""
    signal = await signal_service.generate_signal(symbol.replace("-", "/"), timeframe)
    return signal

@app.get("/api/ohlcv/{symbol}")
async def get_ohlcv(symbol: str, timeframe: str = "15m", limit: int = 100):
    """Get OHLCV data for charting"""
    ohlcv = await price_service.get_ohlcv(symbol.replace("-", "/"), timeframe, limit)
    return {"data": ohlcv}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time signal updates"""
    await manager.connect(websocket)
    try:
        # Send initial data
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to signals stream"
        })
        
        # Keep sending updates
        while True:
            try:
                # Generate signal for BTC/USDT (can be customized)
                signal = await signal_service.generate_signal("BTC/USDT", "15m")
                
                await websocket.send_json({
                    "type": "signal_update",
                    "data": signal.dict(),
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
    uvicorn.run(app, host="0.0.0.0", port=8000)

