"""Check stored private keys and their addresses"""
import sys
sys.path.insert(0, '/Users/elcarosam/project/elcarobybitbotv2')

from core.db_postgres import execute_one
from hyperliquid.signer import get_address_from_private_key

user = execute_one('SELECT hl_testnet_private_key, hl_mainnet_private_key, hl_testnet_wallet_address, hl_mainnet_wallet_address FROM users WHERE user_id = 511692487')
if user:
    testnet_key = user.get('hl_testnet_private_key') or ''
    mainnet_key = user.get('hl_mainnet_private_key') or ''
    testnet_wallet = user.get('hl_testnet_wallet_address') or ''
    mainnet_wallet = user.get('hl_mainnet_wallet_address') or ''
    
    print(f'=== Database values ===')
    print(f'Testnet key exists: {bool(testnet_key)} (length: {len(testnet_key) if testnet_key else 0})')
    print(f'Mainnet key exists: {bool(mainnet_key)} (length: {len(mainnet_key) if mainnet_key else 0})')
    print(f'Testnet wallet: {testnet_wallet}')
    print(f'Mainnet wallet: {mainnet_wallet}')
    
    print(f'\n=== Derived addresses from keys ===')
    if testnet_key:
        testnet_addr = get_address_from_private_key(testnet_key)
        print(f'Testnet key -> address: {testnet_addr}')
    
    if mainnet_key:
        mainnet_addr = get_address_from_private_key(mainnet_key)
        print(f'Mainnet key -> address: {mainnet_addr}')
    
    # Check if same key
    if testnet_key and mainnet_key:
        print(f'\n=== Keys comparison ===')
        print(f'Same key for both networks: {testnet_key == mainnet_key}')
