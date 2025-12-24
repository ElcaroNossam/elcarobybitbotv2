"""
WebSocket endpoint for real-time market data streaming.

Similar to scan/api/consumers.py but using FastAPI WebSockets.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()

# Import workers after router creation to avoid circular imports
from webapp.realtime import (
    register_client, 
    unregister_client, 
    get_current_data,
    start_workers,
    _workers_running
)


@router.websocket("/realtime/{exchange}")
async def websocket_endpoint(
    websocket: WebSocket,
    exchange: str,
    symbols: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time market data.
    
    Args:
        exchange: 'bybit' or 'hyperliquid'
        symbols: Comma-separated list of symbols (optional)
    
    Example:
        ws://localhost:8765/ws/realtime/bybit?symbols=BTCUSDT,ETHUSDT
    """
    if exchange not in ['bybit', 'hyperliquid']:
        await websocket.close(code=1008, reason="Invalid exchange")
        return
    
    await websocket.accept()
    logger.info(f"✅ WebSocket client connected to {exchange}")
    
    # Parse symbols if provided
    symbol_list = symbols.split(',') if symbols else None
    
    # Register this client
    register_client(websocket, exchange)
    
    try:
        # Send initial snapshot
        initial_data = get_current_data(exchange)
        if initial_data:
            await websocket.send_json({
                'type': 'initial_data',
                'exchange': exchange,
                'data': list(initial_data.values()),
                'count': len(initial_data)
            })
        
        # Keep connection alive and handle pings
        while True:
            try:
                # Wait for messages from client (ping/pong)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                msg = json.loads(data)
                if msg.get('type') == 'ping':
                    await websocket.send_json({'type': 'pong'})
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({'type': 'ping'})
                except:
                    break
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.debug(f"Error receiving from client: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from {exchange}")
    except Exception as e:
        logger.error(f"WebSocket error for {exchange}: {e}", exc_info=True)
    finally:
        unregister_client(websocket, exchange)


@router.get("/realtime/status")
async def get_status():
    """Get status of real-time workers."""
    from webapp.realtime import _workers_running, _bybit_data, _hyperliquid_data, _active_connections
    
    return {
        'workers_running': _workers_running,
        'bybit_symbols': len(_bybit_data),
        'hyperliquid_symbols': len(_hyperliquid_data),
        'active_connections': {
            'bybit': len(_active_connections['bybit']),
            'hyperliquid': len(_active_connections['hyperliquid'])
        }
    }


@router.post("/realtime/start")
async def start_realtime_workers(
    bybit_symbols: Optional[list] = None,
    hl_symbols: Optional[list] = None
):
    """Start real-time data workers."""
    try:
        await start_workers(bybit_symbols, hl_symbols)
        return {'status': 'started', 'message': 'Real-time workers started successfully'}
    except Exception as e:
        logger.error(f"Failed to start workers: {e}", exc_info=True)
        return {'status': 'error', 'message': str(e)}
