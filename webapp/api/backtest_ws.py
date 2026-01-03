"""
Backtest WebSocket API - Real-time progress updates
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

# Active backtest sessions
active_backtests: Dict[str, dict] = {}
active_connections: Dict[str, Set[WebSocket]] = {}


@router.websocket("/ws/backtest/{backtest_id}")
async def backtest_websocket(websocket: WebSocket, backtest_id: str):
    """WebSocket endpoint for real-time backtest progress updates"""
    await websocket.accept()
    
    # Add to active connections
    if backtest_id not in active_connections:
        active_connections[backtest_id] = set()
    active_connections[backtest_id].add(websocket)
    
    logger.info(f"Backtest WebSocket connected: {backtest_id}")
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "backtest_id": backtest_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and listen for commands
        while True:
            try:
                message = await websocket.receive_json()
                msg_type = message.get('type')
                
                if msg_type == 'cancel':
                    # Cancel backtest
                    if backtest_id in active_backtests:
                        active_backtests[backtest_id]['cancelled'] = True
                        await broadcast_to_backtest(backtest_id, {
                            "type": "cancelled",
                            "message": "Backtest cancelled by user",
                            "timestamp": datetime.now().isoformat()
                        })
                
                elif msg_type == 'ping':
                    # Keep-alive ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    finally:
        # Remove from active connections
        if backtest_id in active_connections:
            active_connections[backtest_id].discard(websocket)
            if len(active_connections[backtest_id]) == 0:
                del active_connections[backtest_id]
        
        logger.info(f"Backtest WebSocket disconnected: {backtest_id}")


async def broadcast_to_backtest(backtest_id: str, message: dict):
    """Broadcast message to all clients subscribed to this backtest"""
    if backtest_id not in active_connections:
        return
    
    disconnected = set()
    for ws in active_connections[backtest_id]:
        try:
            await ws.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to WebSocket: {e}")
            disconnected.add(ws)
    
    # Remove disconnected clients
    for ws in disconnected:
        active_connections[backtest_id].discard(ws)


async def send_progress(backtest_id: str, progress: float, stage: str, details: dict = None):
    """Send progress update to all connected clients"""
    message = {
        "type": "progress",
        "progress": progress,
        "stage": stage,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        message.update(details)
    
    await broadcast_to_backtest(backtest_id, message)


async def send_result(backtest_id: str, results: dict):
    """Send final backtest results"""
    message = {
        "type": "completed",
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    await broadcast_to_backtest(backtest_id, message)


async def send_error(backtest_id: str, error: str):
    """Send error message"""
    message = {
        "type": "error",
        "error": error,
        "timestamp": datetime.now().isoformat()
    }
    
    await broadcast_to_backtest(backtest_id, message)


def create_backtest_session(config: dict) -> str:
    """Create a new backtest session and return ID"""
    backtest_id = str(uuid.uuid4())
    active_backtests[backtest_id] = {
        "config": config,
        "status": "pending",
        "progress": 0,
        "cancelled": False,
        "started_at": datetime.now().isoformat()
    }
    return backtest_id


def is_backtest_cancelled(backtest_id: str) -> bool:
    """Check if backtest was cancelled"""
    if backtest_id not in active_backtests:
        return False
    return active_backtests[backtest_id].get('cancelled', False)


async def cleanup_backtest_session(backtest_id: str):
    """Clean up backtest session after completion"""
    if backtest_id in active_backtests:
        del active_backtests[backtest_id]
    
    if backtest_id in active_connections:
        # Close all connections - collect tasks to await them
        close_tasks = []
        for ws in active_connections[backtest_id]:
            try:
                close_tasks.append(ws.close())
            except Exception:
                pass
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        del active_connections[backtest_id]
