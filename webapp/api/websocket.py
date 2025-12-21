"""
WebSocket API for Real-Time Trade Streaming
Enhanced with orderbook, trades feed, and advanced analytics
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Optional
import json
import asyncio
import aiohttp
from datetime import datetime

router = APIRouter()


# ============================================================
# BYBIT ORDERBOOK STREAMING
# ============================================================
class BybitOrderbookStream:
    """Stream orderbook data from Bybit WebSocket"""
    
    def __init__(self):
        self.ws = None
        self.orderbook: Dict[str, dict] = {}  # symbol -> {asks: [], bids: []}
        self.subscribers: Dict[str, Set[WebSocket]] = {}  # symbol -> websockets
        self.running = False
        self.task = None
    
    async def connect(self, symbol: str = "BTCUSDT"):
        """Connect to Bybit WebSocket"""
        if self.running:
            return
        
        self.running = True
        url = "wss://stream.bybit.com/v5/public/linear"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(url) as ws:
                    self.ws = ws
                    
                    # Subscribe to orderbook
                    await ws.send_json({
                        "op": "subscribe",
                        "args": [f"orderbook.50.{symbol}"]
                    })
                    
                    async for msg in ws:
                        if not self.running:
                            break
                        
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            await self._handle_message(data)
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break
        except Exception as e:
            print(f"Bybit WS error: {e}")
        finally:
            self.running = False
    
    async def _handle_message(self, data: dict):
        """Handle incoming orderbook message"""
        topic = data.get("topic", "")
        if "orderbook" not in topic:
            return
        
        symbol = topic.split(".")[-1]
        msg_data = data.get("data", {})
        msg_type = data.get("type", "snapshot")
        
        if msg_type == "snapshot":
            # Full orderbook snapshot
            self.orderbook[symbol] = {
                "asks": [[float(p), float(s)] for p, s in msg_data.get("a", [])],
                "bids": [[float(p), float(s)] for p, s in msg_data.get("b", [])],
                "timestamp": msg_data.get("ts", 0)
            }
        elif msg_type == "delta":
            # Incremental update
            if symbol in self.orderbook:
                self._apply_delta(symbol, msg_data)
        
        # Broadcast to subscribers
        await self._broadcast_orderbook(symbol)
    
    def _apply_delta(self, symbol: str, delta: dict):
        """Apply delta update to orderbook"""
        ob = self.orderbook.get(symbol)
        if not ob:
            return
        
        # Update asks
        for price, size in delta.get("a", []):
            price, size = float(price), float(size)
            if size == 0:
                ob["asks"] = [a for a in ob["asks"] if a[0] != price]
            else:
                found = False
                for i, (p, s) in enumerate(ob["asks"]):
                    if p == price:
                        ob["asks"][i][1] = size
                        found = True
                        break
                if not found:
                    ob["asks"].append([price, size])
        
        # Update bids
        for price, size in delta.get("b", []):
            price, size = float(price), float(size)
            if size == 0:
                ob["bids"] = [b for b in ob["bids"] if b[0] != price]
            else:
                found = False
                for i, (p, s) in enumerate(ob["bids"]):
                    if p == price:
                        ob["bids"][i][1] = size
                        found = True
                        break
                if not found:
                    ob["bids"].append([price, size])
        
        # Sort orderbook
        ob["asks"].sort(key=lambda x: x[0])
        ob["bids"].sort(key=lambda x: -x[0])
        ob["timestamp"] = delta.get("ts", ob.get("timestamp", 0))
    
    async def _broadcast_orderbook(self, symbol: str):
        """Send orderbook to all subscribers"""
        if symbol not in self.subscribers:
            return
        
        ob = self.orderbook.get(symbol, {})
        message = {
            "type": "orderbook",
            "symbol": symbol,
            "asks": ob.get("asks", [])[:25],  # Top 25 levels
            "bids": ob.get("bids", [])[:25],
            "timestamp": ob.get("timestamp", 0)
        }
        
        dead_connections = []
        for ws in self.subscribers[symbol]:
            try:
                await ws.send_json(message)
            except:
                dead_connections.append(ws)
        
        for ws in dead_connections:
            self.subscribers[symbol].discard(ws)
    
    def subscribe(self, symbol: str, ws: WebSocket):
        """Add subscriber for symbol"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = set()
        self.subscribers[symbol].add(ws)
    
    def unsubscribe(self, symbol: str, ws: WebSocket):
        """Remove subscriber"""
        if symbol in self.subscribers:
            self.subscribers[symbol].discard(ws)
    
    async def start(self, symbol: str = "BTCUSDT"):
        """Start streaming in background"""
        if not self.task or self.task.done():
            self.task = asyncio.create_task(self.connect(symbol))
    
    def stop(self):
        """Stop streaming"""
        self.running = False
        if self.task:
            self.task.cancel()


# Global orderbook stream
orderbook_stream = BybitOrderbookStream()


# ============================================================
# RECENT TRADES STREAMING
# ============================================================
class TradesStream:
    """Stream recent trades from Bybit"""
    
    def __init__(self):
        self.recent_trades: Dict[str, List[dict]] = {}  # symbol -> trades list
        self.subscribers: Dict[str, Set[WebSocket]] = {}
        self.running = False
        self.task = None
    
    async def connect(self, symbol: str = "BTCUSDT"):
        """Connect to Bybit WebSocket for trades"""
        if self.running:
            return
        
        self.running = True
        url = "wss://stream.bybit.com/v5/public/linear"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(url) as ws:
                    await ws.send_json({
                        "op": "subscribe",
                        "args": [f"publicTrade.{symbol}"]
                    })
                    
                    async for msg in ws:
                        if not self.running:
                            break
                        
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            await self._handle_message(data)
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
        except Exception as e:
            print(f"Trades stream error: {e}")
        finally:
            self.running = False
    
    async def _handle_message(self, data: dict):
        """Handle incoming trade messages"""
        topic = data.get("topic", "")
        if "publicTrade" not in topic:
            return
        
        symbol = topic.split(".")[-1]
        trades = data.get("data", [])
        
        if symbol not in self.recent_trades:
            self.recent_trades[symbol] = []
        
        for trade in trades:
            self.recent_trades[symbol].insert(0, {
                "price": float(trade.get("p", 0)),
                "size": float(trade.get("v", 0)),
                "side": trade.get("S", "Buy"),
                "time": trade.get("T", 0),
                "is_buyer_maker": trade.get("BM", False)
            })
        
        # Keep only last 100 trades
        self.recent_trades[symbol] = self.recent_trades[symbol][:100]
        
        # Broadcast to subscribers
        await self._broadcast_trades(symbol, trades)
    
    async def _broadcast_trades(self, symbol: str, trades: list):
        """Send trades to subscribers"""
        if symbol not in self.subscribers:
            return
        
        message = {
            "type": "trades",
            "symbol": symbol,
            "trades": [{
                "price": float(t.get("p", 0)),
                "size": float(t.get("v", 0)),
                "side": t.get("S", "Buy"),
                "time": t.get("T", 0)
            } for t in trades]
        }
        
        dead = []
        for ws in self.subscribers[symbol]:
            try:
                await ws.send_json(message)
            except:
                dead.append(ws)
        
        for ws in dead:
            self.subscribers[symbol].discard(ws)
    
    def subscribe(self, symbol: str, ws: WebSocket):
        if symbol not in self.subscribers:
            self.subscribers[symbol] = set()
        self.subscribers[symbol].add(ws)
    
    def unsubscribe(self, symbol: str, ws: WebSocket):
        if symbol in self.subscribers:
            self.subscribers[symbol].discard(ws)
    
    async def start(self, symbol: str = "BTCUSDT"):
        if not self.task or self.task.done():
            self.task = asyncio.create_task(self.connect(symbol))
    
    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()


# Global trades stream
trades_stream = TradesStream()


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

# Live analysis sessions: user_id -> {"symbol": str, "strategies": list, "running": bool, "task": Task}
analysis_sessions: Dict[int, dict] = {}


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


@router.websocket("/terminal/{user_id}")
async def websocket_terminal(websocket: WebSocket, user_id: int):
    """WebSocket for terminal - live data, analysis, and auto-trading"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30)
                msg_type = data.get("type")
                
                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    
                elif msg_type == "start_analysis":
                    # Start live analysis for symbol
                    symbol = data.get("symbol", "BTCUSDT")
                    strategies = data.get("strategies", ["elcaro", "wyckoff", "scalper"])
                    auto_trade = data.get("auto_trade", False)
                    
                    # Stop existing session
                    if user_id in analysis_sessions and analysis_sessions[user_id].get("task"):
                        analysis_sessions[user_id]["running"] = False
                        analysis_sessions[user_id]["task"].cancel()
                    
                    # Start new session
                    analysis_sessions[user_id] = {
                        "symbol": symbol,
                        "strategies": strategies,
                        "auto_trade": auto_trade,
                        "running": True,
                        "task": None
                    }
                    
                    task = asyncio.create_task(
                        run_live_analysis(user_id, websocket, symbol, strategies, auto_trade, data)
                    )
                    analysis_sessions[user_id]["task"] = task
                    
                    await websocket.send_json({
                        "type": "analysis_started",
                        "symbol": symbol,
                        "strategies": strategies,
                        "auto_trade": auto_trade
                    })
                    
                elif msg_type == "stop_analysis":
                    if user_id in analysis_sessions:
                        analysis_sessions[user_id]["running"] = False
                        if analysis_sessions[user_id].get("task"):
                            analysis_sessions[user_id]["task"].cancel()
                        del analysis_sessions[user_id]
                    await websocket.send_json({"type": "analysis_stopped"})
                    
                elif msg_type == "get_price":
                    # Get current price for symbol
                    symbol = data.get("symbol", "BTCUSDT")
                    price_data = await fetch_current_price(symbol)
                    await websocket.send_json({
                        "type": "price_update",
                        "data": price_data
                    })
                    
            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break
                    
    except WebSocketDisconnect:
        if user_id in analysis_sessions:
            analysis_sessions[user_id]["running"] = False
        manager.disconnect(websocket, user_id)
    except Exception:
        if user_id in analysis_sessions:
            analysis_sessions[user_id]["running"] = False
        manager.disconnect(websocket)


async def run_live_analysis(
    user_id: int, 
    websocket: WebSocket, 
    symbol: str, 
    strategies: List[str],
    auto_trade: bool,
    config: dict
):
    """Run live market analysis and send signals"""
    import random  # For demo purposes
    
    exchange = config.get("exchange", "bybit")
    account_type = config.get("account_type", "demo")
    leverage = config.get("leverage", 10)
    size = config.get("size", 0.001)
    
    signal_count = 0
    
    try:
        while analysis_sessions.get(user_id, {}).get("running", False):
            # Fetch current market data
            price_data = await fetch_current_price(symbol)
            
            await websocket.send_json({
                "type": "price_update",
                "data": price_data
            })
            
            # Run analysis (simplified - in production would use real analyzers)
            for strategy in strategies:
                analysis_result = await analyze_with_strategy(symbol, strategy, price_data)
                
                if analysis_result:
                    signal_count += 1
                    signal = {
                        "id": signal_count,
                        "symbol": symbol,
                        "strategy": strategy,
                        "side": analysis_result["side"],
                        "entry_price": price_data.get("price", 0),
                        "confidence": analysis_result.get("confidence", 0.7),
                        "reason": analysis_result.get("reason", "Signal detected"),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_json({
                        "type": "signal",
                        "data": signal
                    })
                    
                    # Auto-trade if enabled
                    if auto_trade and analysis_result.get("confidence", 0) >= 0.75:
                        trade_result = await execute_auto_trade(
                            user_id, symbol, analysis_result["side"], 
                            exchange, account_type, leverage, size
                        )
                        await websocket.send_json({
                            "type": "auto_trade",
                            "data": trade_result
                        })
            
            # Wait before next analysis cycle
            await asyncio.sleep(5)  # Check every 5 seconds
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


async def fetch_current_price(symbol: str) -> dict:
    """Fetch current price from Bybit public API"""
    import aiohttp
    
    try:
        url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                if data.get("retCode") == 0:
                    ticker = data.get("result", {}).get("list", [{}])[0]
                    return {
                        "symbol": symbol,
                        "price": float(ticker.get("lastPrice", 0)),
                        "change24h": float(ticker.get("price24hPcnt", 0)) * 100,
                        "high24h": float(ticker.get("highPrice24h", 0)),
                        "low24h": float(ticker.get("lowPrice24h", 0)),
                        "volume24h": float(ticker.get("turnover24h", 0)),
                        "fundingRate": float(ticker.get("fundingRate", 0)) * 100
                    }
    except Exception as e:
        print(f"Price fetch error: {e}")
    
    return {"symbol": symbol, "price": 0, "change24h": 0}


async def analyze_with_strategy(symbol: str, strategy: str, price_data: dict) -> dict:
    """Analyze market with specific strategy (simplified demo)"""
    import random
    
    # In production, this would use actual strategy analyzers
    # For now, return random signals for demonstration
    
    # Only generate signal 5% of the time to simulate real trading
    if random.random() > 0.05:
        return None
    
    side = "Buy" if random.random() > 0.5 else "Sell"
    confidence = random.uniform(0.6, 0.95)
    
    reasons = {
        "elcaro": ["RSI oversold + BB touch", "Volume spike detected", "Trend reversal pattern"],
        "wyckoff": ["Accumulation phase complete", "Spring detected", "SOS confirmed"],
        "scalper": ["Quick momentum shift", "Micro-pullback entry", "Tick imbalance"],
        "scryptomera": ["Multi-timeframe confluence", "Key level break", "Smart money divergence"]
    }
    
    return {
        "side": side,
        "confidence": confidence,
        "reason": random.choice(reasons.get(strategy, ["Signal detected"]))
    }


async def execute_auto_trade(
    user_id: int,
    symbol: str,
    side: str,
    exchange: str,
    account_type: str,
    leverage: int,
    size: float
) -> dict:
    """Execute auto-trade based on signal"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from webapp.api.trading import PlaceOrderRequest, place_order
    
    try:
        req = PlaceOrderRequest(
            symbol=symbol,
            side=side.lower(),
            order_type="market",
            size=size,
            leverage=leverage,
            exchange=exchange,
            account_type=account_type
        )
        
        # Create mock user for request
        user = {"user_id": user_id}
        result = await place_order(req, user)
        
        return {
            "success": result.get("success", False),
            "order_id": result.get("order_id"),
            "symbol": symbol,
            "side": side,
            "size": size,
            "message": result.get("message") or result.get("error")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "symbol": symbol,
            "side": side
        }


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


# ============================================================
# LIVE BACKTEST WEBSOCKET
# ============================================================
@router.websocket("/backtest-live")
async def backtest_live_websocket(websocket: WebSocket):
    """WebSocket for live backtest streaming with real-time analysis visualization"""
    await websocket.accept()
    
    try:
        from webapp.api.backtest import live_manager
        
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")
            
            if msg_type == "start_live":
                # Start live backtest session
                config = {
                    "strategy": message.get("strategy", "elcaro"),
                    "symbol": message.get("symbol", "BTCUSDT"),
                    "timeframe": message.get("timeframe", "1h"),
                    "params": message.get("params", {}),
                    "initial_balance": message.get("initial_balance", 10000),
                    "days": message.get("days", 30)
                }
                
                # Run in background
                await live_manager.start_session(websocket, config)
                
            elif msg_type == "stop_live":
                # Stop current session
                await live_manager.stop_session(websocket)
                
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
    finally:
        try:
            from webapp.api.backtest import live_manager
            await live_manager.stop_session(websocket)
        except:
            pass

