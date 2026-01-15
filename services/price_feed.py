"""
WebSocket Price Feed Service
============================
Real-time price updates from exchanges via WebSocket.
Broadcasts to Redis for all workers to consume.

Features:
- Multi-exchange support (Bybit, HyperLiquid)
- Automatic reconnection
- Price caching in Redis
- Pub/sub broadcasting
"""

import asyncio
import websockets
import json
import logging
import os
import signal
from typing import Dict, Set, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class PriceFeedService:
    """
    WebSocket price feed aggregator.
    
    Connects to exchange WebSockets and broadcasts prices to Redis.
    """
    
    def __init__(self):
        self.redis = None
        self.subscribed_symbols: Set[str] = set()
        self.prices: Dict[str, float] = {}
        self.running = False
        self._ws_bybit = None
        self._ws_hl = None
        self._reconnect_delay = 5
    
    async def start(self):
        """Start the price feed service"""
        logger.info("🚀 Starting Price Feed Service")
        
        # Connect to Redis
        from core.redis_client import get_redis
        self.redis = await get_redis()
        
        if not self.redis._connected:
            logger.error("❌ Redis not connected, cannot start price feed")
            return
        
        self.running = True
        
        # Get initial symbols to subscribe
        await self._refresh_symbols()
        
        # Start WebSocket connections
        await asyncio.gather(
            self._run_bybit_ws(),
            self._run_hl_ws(),
            self._symbol_refresh_loop(),
            return_exceptions=True
        )
    
    async def stop(self):
        """Stop the price feed service"""
        logger.info("🛑 Stopping Price Feed Service")
        self.running = False
        
        if self._ws_bybit:
            await self._ws_bybit.close()
        if self._ws_hl:
            await self._ws_hl.close()
    
    async def _refresh_symbols(self):
        """Refresh list of symbols to subscribe"""
        try:
            # Get symbols from active positions
            from core.db_async import get_all_active_symbols
            symbols = await get_all_active_symbols()
            
            # Add common symbols that are always needed
            common = {"BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"}
            symbols = set(symbols) | common
            
            new_symbols = symbols - self.subscribed_symbols
            if new_symbols:
                logger.info(f"📊 New symbols to subscribe: {new_symbols}")
                self.subscribed_symbols = symbols
                
                # Resubscribe if WebSocket is connected
                if self._ws_bybit:
                    await self._subscribe_bybit(new_symbols)
                    
        except Exception as e:
            logger.error(f"Failed to refresh symbols: {e}")
    
    async def _symbol_refresh_loop(self):
        """Periodically refresh symbol subscriptions"""
        while self.running:
            await asyncio.sleep(60)  # Check every minute
            await self._refresh_symbols()
    
    # ═══════════════════════════════════════════════════════════════
    # BYBIT WEBSOCKET
    # ═══════════════════════════════════════════════════════════════
    
    async def _run_bybit_ws(self):
        """Run Bybit WebSocket connection with auto-reconnect"""
        while self.running:
            try:
                await self._connect_bybit_ws()
            except Exception as e:
                logger.error(f"Bybit WS error: {e}")
            
            if self.running:
                logger.info(f"Reconnecting Bybit WS in {self._reconnect_delay}s...")
                await asyncio.sleep(self._reconnect_delay)
    
    async def _connect_bybit_ws(self):
        """Connect to Bybit WebSocket"""
        uri = "wss://stream.bybit.com/v5/public/linear"
        
        logger.info(f"📡 Connecting to Bybit WS: {uri}")
        
        async with websockets.connect(
            uri,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=5
        ) as ws:
            self._ws_bybit = ws
            logger.info("✅ Bybit WS connected")
            
            # Subscribe to tickers
            await self._subscribe_bybit(self.subscribed_symbols)
            
            # Listen for messages
            async for message in ws:
                await self._handle_bybit_message(message)
    
    async def _subscribe_bybit(self, symbols: Set[str]):
        """Subscribe to Bybit tickers"""
        if not self._ws_bybit or not symbols:
            return
        
        subscribe_msg = {
            "op": "subscribe",
            "args": [f"tickers.{s}" for s in symbols]
        }
        
        await self._ws_bybit.send(json.dumps(subscribe_msg))
        logger.info(f"📩 Subscribed to {len(symbols)} Bybit tickers")
    
    async def _handle_bybit_message(self, message: str):
        """Handle Bybit WebSocket message"""
        try:
            data = json.loads(message)
            
            # Check for ticker update
            topic = data.get("topic", "")
            if topic.startswith("tickers."):
                symbol = topic.replace("tickers.", "")
                ticker_data = data.get("data", {})
                
                price = ticker_data.get("lastPrice")
                if price:
                    await self._update_price(symbol, float(price), "bybit")
                    
        except Exception as e:
            logger.error(f"Error handling Bybit message: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # HYPERLIQUID WEBSOCKET
    # ═══════════════════════════════════════════════════════════════
    
    async def _run_hl_ws(self):
        """Run HyperLiquid WebSocket connection with auto-reconnect"""
        while self.running:
            try:
                await self._connect_hl_ws()
            except Exception as e:
                logger.error(f"HyperLiquid WS error: {e}")
            
            if self.running:
                logger.info(f"Reconnecting HyperLiquid WS in {self._reconnect_delay}s...")
                await asyncio.sleep(self._reconnect_delay)
    
    async def _connect_hl_ws(self):
        """Connect to HyperLiquid WebSocket"""
        uri = "wss://api.hyperliquid.xyz/ws"
        
        logger.info(f"📡 Connecting to HyperLiquid WS: {uri}")
        
        async with websockets.connect(
            uri,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=5
        ) as ws:
            self._ws_hl = ws
            logger.info("✅ HyperLiquid WS connected")
            
            # Subscribe to all mids (prices)
            subscribe_msg = {
                "method": "subscribe",
                "subscription": {"type": "allMids"}
            }
            await ws.send(json.dumps(subscribe_msg))
            
            # Listen for messages
            async for message in ws:
                await self._handle_hl_message(message)
    
    async def _handle_hl_message(self, message: str):
        """Handle HyperLiquid WebSocket message"""
        try:
            data = json.loads(message)
            
            if data.get("channel") == "allMids":
                mids = data.get("data", {}).get("mids", {})
                
                for symbol, price in mids.items():
                    # Convert HL symbol to standard format
                    std_symbol = f"{symbol}USDT" if not symbol.endswith("USDT") else symbol
                    await self._update_price(std_symbol, float(price), "hyperliquid")
                    
        except Exception as e:
            logger.error(f"Error handling HyperLiquid message: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # PRICE UPDATES
    # ═══════════════════════════════════════════════════════════════
    
    async def _update_price(self, symbol: str, price: float, source: str):
        """Update price in Redis and broadcast"""
        if price <= 0:
            return
        
        # Update local cache
        old_price = self.prices.get(symbol)
        self.prices[symbol] = price
        
        # Update Redis
        await self.redis.set_price(symbol, price)
        
        # Broadcast significant changes (>0.1% move)
        if old_price:
            change_pct = abs(price - old_price) / old_price * 100
            if change_pct > 0.1:
                await self.redis.publish_price_update(symbol, price)
    
    async def get_health(self) -> Dict:
        """Get service health status"""
        return {
            "running": self.running,
            "symbols_count": len(self.subscribed_symbols),
            "prices_cached": len(self.prices),
            "bybit_connected": self._ws_bybit is not None and self._ws_bybit.open,
            "hl_connected": self._ws_hl is not None and self._ws_hl.open,
            "timestamp": datetime.utcnow().isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

async def main():
    """Main entry point"""
    service = PriceFeedService()
    
    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    
    def shutdown_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(service.stop())
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, shutdown_handler)
    
    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
