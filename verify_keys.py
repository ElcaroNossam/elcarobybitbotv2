#!/usr/bin/env python3
from eth_account import Account

# TESTNET
testnet_key = '0x6c8b4ffa6a52449b9fbdb14b6aad1d9cf9eee6b467a1ec3d405e657e0b99f58b'
testnet_addr = Account.from_key(testnet_key).address
print('TESTNET:')
print(f'  Derived: {testnet_addr}')
print(f'  Expected: 0x5a1928289d14c9af8d1c5557b8756e552b6d67ec')
print(f'  Match: {testnet_addr.lower() == "0x5a1928289d14c9af8d1c5557b8756e552b6d67ec"}')

# MAINNET  
mainnet_key = '0xeb098a5091005fecca489b736f34cb8ec751ebdbd06f121ccf460c82695fce40'
mainnet_addr = Account.from_key(mainnet_key).address
print('MAINNET:')
print(f'  Derived: {mainnet_addr}')
print(f'  Expected: 0x157a40d254c174a8132d207251ba24514ccc6a2f')
print(f'  Match: {mainnet_addr.lower() == "0x157a40d254c174a8132d207251ba24514ccc6a2f"}')
