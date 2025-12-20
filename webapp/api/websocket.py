"""
WebSocket API for Real-Time Trade Streaming
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for trade streaming"""
    
    def __init__(self):
        # user_id -> list of websocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # All connected clients for broadcast
        self.all_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, user_id: int = None):
        """Accept and store connection"""
        await websocket.accept()
        self.all_connections.add(websocket)
        
        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to ElCaro Trade Stream",
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket, user_id: int = None):
        """Remove connection"""
        self.all_connections.discard(websocket)
        
        if user_id and user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass
    
    async def broadcast(self, message: dict):
        """Broadcast to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.all_connections.discard(conn)
    
    async def broadcast_trade(self, trade: dict, user_id: int = None):
        """Broadcast trade notification"""
        message = {
            "type": "trade",
            "data": trade,
            "timestamp": datetime.now().isoformat()
        }
        
        if user_id:
            await self.send_to_user(user_id, message)
        else:
            await self.broadcast(message)
    
    async def broadcast_signal(self, signal: dict):
        """Broadcast new signal"""
        message = {
            "type": "signal",
            "data": signal,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)
    
    async def broadcast_position_update(self, position: dict, user_id: int):
        """Send position update to user"""
        message = {
            "type": "position_update",
            "data": position,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_user(user_id, message)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/trades/{user_id}")
async def websocket_trades(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for user-specific trade streaming"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive and listen for messages
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30)
                
                # Handle client messages
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.get("type") == "subscribe":
                    # User wants to subscribe to specific symbols
                    await websocket.send_json({
                        "type": "subscribed",
                        "symbols": data.get("symbols", [])
                    })
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        manager.disconnect(websocket, user_id)


@router.websocket("/signals")
async def websocket_signals(websocket: WebSocket):
    """WebSocket endpoint for public signal streaming"""
    await manager.connect(websocket)
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30)
                
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


# Helper functions to be called from bot.py

async def notify_trade_opened(user_id: int, trade_data: dict):
    """Notify user that trade was opened"""
    trade_data["action"] = "open"
    await manager.broadcast_trade(trade_data, user_id)


async def notify_trade_closed(user_id: int, trade_data: dict):
    """Notify user that trade was closed"""
    trade_data["action"] = "close"
    await manager.broadcast_trade(trade_data, user_id)


async def notify_new_signal(signal_data: dict):
    """Broadcast new trading signal"""
    await manager.broadcast_signal(signal_data)


async def notify_position_update(user_id: int, position_data: dict):
    """Notify user of position update (PnL change)"""
    await manager.broadcast_position_update(position_data, user_id)
