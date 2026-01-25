"""
WebSocket endpoint for real-time market data streaming.

Similar to scan/api/consumers.py but using FastAPI WebSockets.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException
from typing import Optional
import logging
import json
import asyncio

from webapp.api.auth import get_current_user_optional, get_current_user

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
                except Exception as e:
                    logger.debug(f"Failed to send ping: {e}")
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
    hl_symbols: Optional[list] = None,
    current_user: dict = Depends(get_current_user)
):
    """Start real-time data workers. Requires authentication."""
    # Only admins can start workers
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        await start_workers(bybit_symbols, hl_symbols)
        return {'status': 'started', 'message': 'Real-time workers started successfully'}
    except Exception as e:
        logger.error(f"Failed to start workers: {e}", exc_info=True)
        return {'status': 'error', 'message': str(e)}


# ============================================================
# iOS MOBILE APP WEBSOCKET ENDPOINT
# ============================================================
# iOS uses /ws/market endpoint with specific message format:
# Subscribe: {"action": "subscribe", "channel": "ticker", "symbol": "BTCUSDT"}
# Response: {"type": "ticker", "symbol": "...", "price": ..., "change_24h": ...}

import aiohttp

async def fetch_ticker_data(symbol: str) -> Optional[dict]:
    """Fetch ticker data for a symbol from Bybit API."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("retCode") == 0:
                        result = data.get("result", {}).get("list", [])
                        if result:
                            t = result[0]
                            return {
                                "type": "ticker",
                                "symbol": t.get("symbol", symbol),
                                "price": float(t.get("lastPrice", 0)),
                                "change_24h": float(t.get("price24hPcnt", 0)) * 100,
                                "volume_24h": float(t.get("volume24h", 0)),
                                "high_24h": float(t.get("highPrice24h", 0)),
                                "low_24h": float(t.get("lowPrice24h", 0))
                            }
    except Exception as e:
        logger.debug(f"Failed to fetch ticker for {symbol}: {e}")
    return None


@router.websocket("/market")
async def websocket_market_ios(websocket: WebSocket):
    """
    WebSocket endpoint for iOS mobile app real-time market data.
    
    iOS sends:
        {"action": "subscribe", "channel": "ticker", "symbol": "BTCUSDT"}
        {"action": "unsubscribe", "channel": "ticker", "symbol": "BTCUSDT"}
    
    Server sends:
        {"type": "ticker", "symbol": "BTCUSDT", "price": 42000.5, "change_24h": 2.5, ...}
    """
    await websocket.accept()
    logger.info("✅ iOS client connected to /ws/market")
    
    # Track subscribed symbols for this connection
    subscribed_symbols: set = set()
    running = True
    
    async def stream_tickers():
        """Background task to stream ticker updates."""
        nonlocal running
        while running:
            try:
                for symbol in list(subscribed_symbols):
                    if not running:
                        break
                    ticker = await fetch_ticker_data(symbol)
                    if ticker:
                        try:
                            await websocket.send_json(ticker)
                        except Exception:
                            running = False
                            break
                await asyncio.sleep(1)  # Update every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Ticker stream error: {e}")
                await asyncio.sleep(2)
    
    # Start ticker streaming task
    ticker_task = asyncio.create_task(stream_tickers())
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30)
                
                action = data.get("action")
                channel = data.get("channel")
                symbol = data.get("symbol", "BTCUSDT")
                msg_type = data.get("type")
                
                # Handle ping/pong
                if msg_type == "ping" or action == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue
                
                # Handle subscription
                if action == "subscribe" and channel == "ticker":
                    subscribed_symbols.add(symbol)
                    # Send immediate ticker update
                    ticker = await fetch_ticker_data(symbol)
                    if ticker:
                        await websocket.send_json(ticker)
                    await websocket.send_json({
                        "type": "subscribed",
                        "channel": "ticker",
                        "symbol": symbol
                    })
                    logger.debug(f"iOS subscribed to {symbol}")
                
                elif action == "unsubscribe" and channel == "ticker":
                    subscribed_symbols.discard(symbol)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "channel": "ticker",
                        "symbol": symbol
                    })
                    logger.debug(f"iOS unsubscribed from {symbol}")
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        logger.info("iOS client disconnected from /ws/market")
    except Exception as e:
        logger.error(f"iOS WebSocket error: {e}")
    finally:
        running = False
        ticker_task.cancel()
        try:
            await ticker_task
        except asyncio.CancelledError:
            pass
