#!/usr/bin/env python3
"""Test HL testnet trading functions for user 511692487."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test():
    from db import (
        get_hl_credentials, get_exchange_type, get_trading_mode,
        get_execution_targets, get_active_account_types
    )
    from hl_adapter import HLAdapter

    uid = 511692487

    # 1. User settings
    exchange = get_exchange_type(uid)
    mode = get_trading_mode(uid)
    print(f"1. exchange_type={exchange}, trading_mode={mode}")

    # 2. Credentials
    hl_creds = get_hl_credentials(uid)
    has_testnet = bool(hl_creds.get("hl_testnet_private_key"))
    has_mainnet = bool(hl_creds.get("hl_mainnet_private_key"))
    print(f"2. has_testnet_key={has_testnet}, has_mainnet_key={has_mainnet}")

    # 3. Active account types
    acc_types = get_active_account_types(uid)
    print(f"3. get_active_account_types={acc_types}")

    # 4. Execution targets per strategy
    for strat in ["oi", "scryptomera", "scalper", "manual", "fibonacci", "rsi_bb"]:
        targets = get_execution_targets(uid, strat)
        target_str = [(t["exchange"], t["account_type"]) for t in targets]
        print(f"4. targets({strat})={target_str}")

    # 5. get_user_targets from exchange_router
    try:
        from exchange_router import get_user_targets
        user_targets = get_user_targets(uid)
        print(f"5. get_user_targets={[(t.exchange, t.env, t.account_type, t.label) for t in user_targets]}")
    except Exception as e:
        print(f"5. get_user_targets ERROR: {e}")

    # 6. Connect to testnet
    private_key = hl_creds.get("hl_testnet_private_key")
    if not private_key:
        print("6. NO testnet key!")
        return

    adapter = HLAdapter(private_key=private_key, testnet=True)
    await adapter.initialize()
    print(f"6. main_wallet={adapter.main_wallet_address}")
    print(f"   api_wallet={adapter._client.address}")

    # 7. Balance
    balance = await adapter.get_balance()
    print(f"7. balance={balance}")

    # 8. Positions
    positions = await adapter.get_positions()
    pos_list = positions if positions else []
    print(f"8. testnet positions count={len(pos_list)}")
    for p in pos_list[:5]:
        coin = p.get("coin", "?")
        sz = p.get("szi", p.get("size", "?"))
        entry = p.get("entryPx", "?")
        uPnl = p.get("unrealizedPnl", "?")
        print(f"   {coin}: size={sz}, entry={entry}, uPnl={uPnl}")

    # 9. Open orders
    try:
        orders = await adapter.fetch_open_orders()
        order_list = orders.get("orders", []) if isinstance(orders, dict) else []
        print(f"9. open orders count={len(order_list)}")
    except Exception as e:
        print(f"9. get_open_orders ERROR: {e}")

    # 10. Test market data (get mid price for BTC)
    try:
        all_mids = await adapter._client._info_request("allMids")
        btc_mid = all_mids.get("BTC", "N/A") if isinstance(all_mids, dict) else "N/A"
        print(f"10. BTC mid price={btc_mid}")
    except Exception as e:
        print(f"10. ticker ERROR: {e}")
        import traceback
        traceback.print_exc()

    # 11. Test placing a small BTC long on testnet (0.001 BTC)
    bal_data = balance.get("data", balance) if isinstance(balance, dict) else {}
    equity = bal_data.get("equity", 0) if isinstance(bal_data, dict) else 0
    print(f"11. equity for order={equity}")

    if equity and float(equity) > 10:
        try:
            # Set leverage first
            lev_result = await adapter.set_leverage("BTC", 3, margin_mode="cross")
            print(f"12. set_leverage(BTC, 3)={lev_result}")

            # Place small market buy
            result = await adapter.place_order(
                symbol="BTC",
                side="Buy",
                qty=0.001,
                order_type="Market"
            )
            print(f"13. place_order(BTC, Buy, 0.001)={result}")

            success = result.get("success", False) if isinstance(result, dict) else False
            if success:
                # Wait and check positions
                await asyncio.sleep(2)
                positions2 = await adapter.get_positions()
                btc_pos = [p for p in (positions2 or []) if p.get("coin") == "BTC"]
                print(f"14. BTC position after order={btc_pos}")

                # Set SL/TP
                if btc_pos:
                    entry_px = float(btc_pos[0].get("entryPx", 0))
                    sl_price = round(entry_px * 0.95, 1)  # 5% below
                    tp_price = round(entry_px * 1.05, 1)  # 5% above
                    try:
                        sl_tp_result = await adapter.set_tp_sl(
                            coin="BTC",
                            sl_price=sl_price,
                            tp_price=tp_price,
                            sz=0.001,
                            address=adapter.main_wallet_address
                        )
                        print(f"15. set_tp_sl(sl={sl_price}, tp={tp_price})={sl_tp_result}")
                    except Exception as e:
                        print(f"15. set_tp_sl ERROR: {e}")
                        import traceback
                        traceback.print_exc()

                # Close the test position
                try:
                    close_result = await adapter.close_position(symbol="BTC", qty=0.001)
                    print(f"16. close_position(BTC)={close_result}")
                except Exception as e:
                    print(f"16. close ERROR: {e}")
            else:
                print(f"13. Order FAILED: {result}")
        except Exception as e:
            print(f"12-16. Trading test ERROR: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("11. Insufficient balance for test trade, skipping order test")

    print("\n=== TEST COMPLETE ===")

asyncio.run(test())
