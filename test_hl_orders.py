#!/usr/bin/env python3
"""
Test HyperLiquid Orders - Both Testnet and Mainnet
Minimal amounts for testing
"""
import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Disable debug logs from aiohttp/other libs
logging.getLogger('aiohttp').setLevel(logging.WARNING)


async def test_hl_full(uid: int = 511692487):
    """Full HyperLiquid test: balance, open, close"""
    import db
    from hl_adapter import HLAdapter
    from hyperliquid import get_size_decimals
    
    user = db.execute_one(
        '''SELECT hl_testnet_private_key, hl_mainnet_private_key, 
                  hl_testnet_wallet_address, hl_mainnet_wallet_address 
           FROM users WHERE user_id = %s''', 
        (uid,)
    )
    
    results = {}
    
    # ═══════════════════════════════════════════════════════════════
    # TEST 1: MAINNET
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("TEST 1: HYPERLIQUID MAINNET")
    print("="*60)
    
    # Use main_wallet_address for Unified Account / API Wallet architecture
    adapter = HLAdapter(
        private_key=user['hl_mainnet_private_key'],
        testnet=False,
        main_wallet_address=user.get('hl_mainnet_wallet_address')  # Main wallet for balance
    )
    
    try:
        await adapter.initialize()
        
        # 1a. Get Balance
        print("\n[1a] BALANCE:")
        bal = await adapter.get_balance(use_cache=False)
        if bal.get('success'):
            data = bal.get('data', {})
            equity = data.get('equity', 0)
            available = data.get('available', 0)
            is_unified = data.get('is_unified_account', False)
            print(f"  Equity: ${equity:.2f}")
            print(f"  Available: ${available:.2f}")
            print(f"  Unified Account: {is_unified}")
            results['mainnet_balance'] = equity
        else:
            print(f"  ERROR: {bal.get('error')}")
            return results
        
        # 1b. Check existing positions
        print("\n[1b] EXISTING POSITIONS:")
        pos = await adapter.fetch_positions()
        pos_list = pos.get('result', {}).get('list', [])
        print(f"  Count: {len(pos_list)}")
        for p in pos_list:
            print(f"    - {p['symbol']} {p['side']} size={p['size']} entry={p['entryPrice']}")
        
        # 1c. Get current ETH price
        print("\n[1c] ETH PRICE:")
        eth_price = await adapter._client.get_mid_price("ETH")
        print(f"  ETH mid price: ${eth_price:.2f}")
        
        # 1d. Open minimal position (0.01 ETH ~ $20 on mainnet)
        MIN_ETH_SIZE = 0.01  # ~$20 notional at $2000 ETH
        if equity >= 30:
            print(f"\n[1d] OPEN TEST POSITION ({MIN_ETH_SIZE} ETH LONG):")
            try:
                result = await adapter._client.market_open(
                    coin="ETH",
                    is_buy=True,
                    sz=MIN_ETH_SIZE,  # Minimal size ~$20
                    slippage=0.05  # 5% slippage for market order
                )
                print(f"  Result: {result}")
                order_ok = result.get('status') == 'ok'
                statuses = result.get('response', {}).get('data', {}).get('statuses', [])
                if statuses and 'filled' in statuses[0]:
                    print(f"  ✅ Order filled: {statuses[0]['filled']}")
                    results['mainnet_open'] = True
                elif statuses and 'error' in statuses[0]:
                    print(f"  ❌ Order error: {statuses[0]['error']}")
                    results['mainnet_open'] = False
                else:
                    results['mainnet_open'] = order_ok
                
                # Wait a moment
                await asyncio.sleep(2)
                
                # 1e. Check position again
                print("\n[1e] VERIFY POSITION:")
                pos2 = await adapter.fetch_positions()
                pos_list2 = pos2.get('result', {}).get('list', [])
                eth_pos = None
                for p in pos_list2:
                    if 'ETH' in p['symbol']:
                        eth_pos = p
                        print(f"  ✅ ETH Position: {p['side']} size={p['size']} entry={p['entryPrice']}")
                        break
                
                # 1f. Close position (use adapter.close_position which passes main_wallet_address)
                if eth_pos:
                    print("\n[1f] CLOSE POSITION:")
                    close_result = await adapter.close_position(
                        symbol="ETH",
                        qty=None  # Close all
                    )
                    print(f"  Result: {close_result}")
                    results['mainnet_close'] = close_result.get('retCode') == 0
                    
            except Exception as e:
                print(f"  ERROR: {e}")
                results['mainnet_open'] = False
        else:
            print(f"\n  ⚠️ Insufficient balance for mainnet test (need $3, have ${equity:.2f})")
    
    finally:
        await adapter.close()
    
    # ═══════════════════════════════════════════════════════════════
    # TEST 2: TESTNET
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("TEST 2: HYPERLIQUID TESTNET")
    print("="*60)
    
    adapter2 = HLAdapter(
        private_key=user['hl_testnet_private_key'],
        testnet=True,
        main_wallet_address=user.get('hl_testnet_wallet_address')  # Main wallet for balance
    )
    
    try:
        await adapter2.initialize()
        
        # 2a. Get Balance
        print("\n[2a] BALANCE:")
        bal2 = await adapter2.get_balance(use_cache=False)
        if bal2.get('success'):
            data = bal2.get('data', {})
            equity = data.get('equity', 0)
            available = data.get('available', 0)
            is_unified = data.get('is_unified_account', False)
            print(f"  Equity: ${equity:.2f}")
            print(f"  Available: ${available:.2f}")
            print(f"  Unified Account: {is_unified}")
            results['testnet_balance'] = equity
        else:
            print(f"  ERROR: {bal2.get('error')}")
            return results
        
        # 2b. Check existing positions
        print("\n[2b] EXISTING POSITIONS:")
        pos = await adapter2.fetch_positions()
        pos_list = pos.get('result', {}).get('list', [])
        print(f"  Count: {len(pos_list)}")
        for p in pos_list:
            print(f"    - {p['symbol']} {p['side']} size={p['size']} entry={p['entryPrice']}")
        
        # 2c. Get current ETH price
        print("\n[2c] ETH PRICE:")
        eth_price = await adapter2._client.get_mid_price("ETH")
        if eth_price:
            print(f"  ETH mid price: ${eth_price:.2f}")
        else:
            print("  Could not get ETH price on testnet")
        
        # 2d. Open minimal position if we have balance
        MIN_ETH_SIZE_TESTNET = 0.01
        if equity >= 30 and eth_price:
            print(f"\n[2d] OPEN TEST POSITION ({MIN_ETH_SIZE_TESTNET} ETH LONG):")
            try:
                result = await adapter2._client.market_open(
                    coin="ETH",
                    is_buy=True,
                    sz=MIN_ETH_SIZE_TESTNET,
                    slippage=0.05
                )
                print(f"  Result: {result}")
                order_ok = result.get('status') == 'ok'
                statuses = result.get('response', {}).get('data', {}).get('statuses', [])
                if statuses and 'filled' in statuses[0]:
                    print(f"  ✅ Order filled: {statuses[0]['filled']}")
                    results['testnet_open'] = True
                elif statuses and 'error' in statuses[0]:
                    print(f"  ❌ Order error: {statuses[0]['error']}")
                    results['testnet_open'] = False
                else:
                    results['testnet_open'] = order_ok
                
                await asyncio.sleep(2)
                
                # 2e. Close position (use adapter.close_position which passes main_wallet_address)
                print("\n[2e] CLOSE POSITION:")
                try:
                    close_result = await adapter2.close_position(
                        symbol="ETH",
                        qty=None  # Close all
                    )
                    print(f"  Result: {close_result}")
                    results['testnet_close'] = close_result.get('retCode') == 0
                except Exception as ce:
                    print(f"  Close error (may have no position): {ce}")
                    
            except Exception as e:
                print(f"  ERROR: {e}")
                results['testnet_open'] = False
        else:
            print(f"\n  ⚠️ Testnet: balance=${equity:.2f}, need faucet tokens")
            print("  Get testnet tokens at: https://app.hyperliquid-testnet.xyz/drip")
    
    finally:
        await adapter2.close()
    
    # ═══════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for k, v in results.items():
        status = "✅" if v else "❌" if v is False else f"${v:.2f}" if isinstance(v, float) else str(v)
        print(f"  {k}: {status}")
    
    return results


if __name__ == "__main__":
    uid = int(sys.argv[1]) if len(sys.argv) > 1 else 511692487
    asyncio.run(test_hl_full(uid))
