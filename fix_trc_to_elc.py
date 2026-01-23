#!/usr/bin/env python3
"""
Fix TRC -> ELC token naming across the entire project.
TRC was the old name, ELC (Lyxen Coin) is the new unified token.
"""

import os
import re

# Files to process
FILES_TO_FIX = [
    'core/blockchain.py',
    'core/__init__.py',
    'bot.py',
    'db.py',
    'core/db_postgres.py',
    'services/license_blockchain_service.py',
    'webapp/app.py',
    'webapp/api/finance.py',
    'webapp/api/mobile.py',
    'webapp/api/marketplace.py',
    'webapp/api/blockchain.py',
    'webapp/templates/index.html',
    'webapp/templates/blockchain_admin.html',
    'webapp/templates/admin/index.html',
    'webapp/templates/strategies.html',
    'webapp/templates/marketplace.html',
    'webapp/templates/wallet.html',
    'webapp/templates/landing.html',
    'tests/test_payment_integration.py',
    'migrations/versions/017_marketplace_tables.py',
]

# Add all translation files
for lang in ['en', 'ru', 'de', 'fr', 'es', 'it', 'pl', 'cs', 'lt', 'sq', 'uk', 'zh', 'ja', 'ar', 'he']:
    FILES_TO_FIX.append(f'translations/{lang}.py')

# Replacements (order matters - more specific first)
REPLACEMENTS = [
    # Comments/docs
    ('TRC Token Implementation', 'ELC Token Implementation'),
    ('Lyxen Coin (TRC)', 'Lyxen Coin (ELC)'),
    ('TRC is designed', 'ELC is designed'),
    ('SOLVED BY TRC', 'SOLVED BY ELC'),
    ('backing TRC', 'backing ELC'),
    ('for TRC tokens', 'for ELC tokens'),
    
    # Variable names
    ('TRC_PEG_RATE', 'ELC_PEG_RATE'),
    ('TRC_SYMBOL', 'ELC_SYMBOL'),
    ('TRC_NAME', 'ELC_NAME'),
    ('TRC_TO_USDT_RATE', 'ELC_TO_USDT_RATE'),
    ('LICENSE_PRICES_TRC', 'LICENSE_PRICES_ELC'),
    ('TRC_INITIAL_CIRCULATION', 'ELC_INITIAL_CIRCULATION'),
    ('TRC_TOTAL_SUPPLY', 'ELC_TOTAL_SUPPLY'),
    ('TRC_DECIMALS', 'ELC_DECIMALS'),
    ('TRC_FULL_NAME', 'ELC_FULL_NAME'),
    ('TRC_MASTER_WALLET', 'ELC_MASTER_WALLET'),
    
    # Price variables
    ('PREMIUM_TRC_', 'PREMIUM_ELC_'),
    ('BASIC_TRC_', 'BASIC_ELC_'),
    ('ENTERPRISE_TRC_', 'ENTERPRISE_ELC_'),
    
    # Functions
    ('get_trc_balance', 'get_elc_balance'),
    ('get_trc_wallet', 'get_elc_wallet'),
    ('pay_with_trc', 'pay_with_elc'),
    ('deposit_trc', 'deposit_elc'),
    ('reward_trc', 'reward_elc'),
    ('get_license_price_trc', 'get_license_price_elc'),
    ('get_trc_usd_rate', 'get_elc_usd_rate'),
    ('get_trc_price_info', 'get_elc_price_info'),
    
    # Wallet addresses
    ('0xTRC', '0xELC'),
    
    # Chain symbol
    ('CHAIN_SYMBOL = "TRC"', 'CHAIN_SYMBOL = "ELC"'),
    
    # Classes
    ('class TRCWallet', 'class ELCWallet'),
    ('class TRCTransaction', 'class ELCTransaction'),
    ('class TRCBlock', 'class ELCBlock'),
    ('TRCWallet', 'ELCWallet'),
    ('TRCTransaction', 'ELCTransaction'),
    ('TRCBlock', 'ELCBlock'),
    
    # Currency in strings/dicts - remove "trc" key, keep only "elc"
    ('"trc":', '"elc":'),
    ("'trc':", "'elc':"),
    ('"trc"', '"elc"'),
    ("'trc'", "'elc'"),
    
    # Display text
    ('TRC/USD', 'ELC/USD'),
    ('1 TRC = 1', '1 ELC = 1'),
    ('TRC/ELC', 'ELC'),
    ('TRC, ELC', 'ELC'),
    ('TRC or ELC', 'ELC'),
    
    # Translation keys
    ('btn_pay_trc', 'btn_pay_elc'),
    ('payment_trc_title', 'payment_elc_title'),
    ('payment_trc_desc', 'payment_elc_desc'),
    ('payment_trc_insufficient', 'payment_elc_insufficient'),
    ('total_trc', 'total_elc'),
    
    # UI text patterns - these appear in user-visible strings
    (':.0f} TRC', ':.0f} ELC'),
    (':,.0f} TRC', ':,.0f} ELC'),
    (' TRC ⚡', ' ELC ⚡'),
    (' TRC 🔥', ' ELC 🔥'),
    (' TRC 🎯', ' ELC 🎯'),
    (' TRC 🏆', ' ELC 🏆'),
    (' TRC)', ' ELC)'),
    (' TRC.', ' ELC.'),
    (' TRC\n', ' ELC\n'),
    (' TRC"', ' ELC"'),
    (" TRC'", " ELC'"),
    ('TRC*', 'ELC*'),
    ('*TRC*', '*ELC*'),
    (' TRC (~$', ' ELC (~$'),
    ("'TRC'", "'ELC'"),
    ('"TRC"', '"ELC"'),
    
    # Comments
    ('# TRC ', '# ELC '),
    ('Wallet & TRC', 'Wallet & ELC'),
    ('TRC-Guthaben', 'ELC-Guthaben'),  # German
    ('TRC-Wallet', 'ELC-Wallet'),
    
    # Price columns in DB
    ('price_trc', 'price_elc'),
    
    # Comments in bot.py
    ('LYXEN COIN (TRC)', 'LYXEN COIN (ELC)'),
    ('(TRC)', '(ELC)'),
    ('replace TRC', 'deprecated'),
    ('same as TRC', 'same as USDT'),
    ('TRC + ELC', 'ELC'),
    ('TRC prices', 'ELC prices'),
    ('TRC (Lyxen', 'ELC (Lyxen'),
    ('# Secondary: TRC', '# Payment: ELC'),
    
    # UI strings in wallet functions
    ('amount of TRC', 'amount of ELC'),
    ('Transfer TRC', 'Transfer ELC'),
    ("user's TRC wallet", "user's ELC wallet"),
    ('Stake TRC', 'Stake ELC'),
    ('Ways to get TRC', 'Ways to get ELC'),
    ('receive TRC 1:1', 'receive ELC 1:1'),
    ('Get 100 TRC', 'Get 100 ELC'),
    ('Buy TRC', 'Buy ELC'),
    ('100 TRC for', '100 ELC for'),
    ('+100 TRC credited', '+100 ELC credited'),
    ('TRC purchases', 'ELC purchases'),
    ('TRC Balance', 'ELC Balance'),
    ('Convert TRC', 'Convert ELC'),
    ('TRC → ELC', 'ELC Token'),
    ('TRC to ELC', 'ELC'),
    ('Minimum 10 TRC', 'Minimum 10 ELC'),
    ('Insufficient TRC', 'Insufficient ELC'),
    ('convert_trc_elc', 'wallet_info'),
    ('do_convert:', 'deposit:'),
    
    # More UI strings
    (':.2f} TRC', ':.2f} ELC'),
    ('TRC Staking', 'ELC Staking'),
    ('on your TRC', 'on your ELC'),
    ('Minimum 1 TRC', 'Minimum 1 ELC'),
    ('TRC successfully', 'ELC successfully'),
    ('staked TRC', 'staked ELC'),
    ('enough TRC', 'enough ELC'),
    ('TRC balance', 'ELC balance'),
    ('insufficient_trc', 'insufficient_elc'),
    ('Deposit TRC', 'Deposit ELC'),
    ('payment_success_trc', 'payment_success_elc'),
    ('TRC payments', 'ELC payments'),
    ('Use TRC tokens', 'Use ELC tokens'),
    ('Use TRC payments', 'Use ELC payments'),
    ('converts TRC', 'converts ELC'),
    
    # blockchain.py specific
    ('TRC is pegged', 'ELC is pegged'),
    ('comprehensive TRC', 'comprehensive ELC'),
    ('backing the TRC', 'backing the ELC'),
    (':,.2f} TRC', ':,.2f} ELC'),
    ('Created TRC wallet', 'Created ELC wallet'),
    ('purchases TRC', 'purchases ELC'),
    ('Withdraw TRC', 'Withdraw ELC'),
    ('deposit TRC', 'deposit ELC'),
    ('Give TRC', 'Give ELC'),
    ('TRC reward', 'ELC reward'),
    ('USDT to TRC', 'USDT to ELC'),
    ('Format TRC', 'Format ELC'),
    ('prices in TRC', 'prices in ELC'),
    (' TRC to user', ' ELC to user'),
    (' TRC from', ' ELC from'),
    
    # HTML specific
    ('Blockchain/TRC', 'Blockchain/ELC'),
    ('TRC wallet', 'ELC wallet'),
    ('TRC blockchain', 'ELC blockchain'),
    ('TRC Blockchain', 'ELC Blockchain'),
    ('TRC Wallet', 'ELC Wallet'),
    ('TRC Amount', 'ELC Amount'),
    ('purchaseTRC', 'purchaseELC'),
    ('0 TRC', '0 ELC'),
    ('100 TRC', '100 ELC'),
    ('50 TRC', '50 ELC'),
    ('} TRC<', '} ELC<'),
    ('>TRC<', '>ELC<'),
    ('TRC tokens', 'ELC tokens'),
    ('TRC Tokens', 'ELC Tokens'),
    ('Price in TRC', 'Price in ELC'),
    ('priceTRC', 'priceELC'),
    ('"TRC"', '"ELC"'),
    ("'TRC'", "'ELC'"),
    ('>TRC</span>', '>ELC</span>'),
    ('TRC</span>', 'ELC</span>'),
    
    # Translation specific (various languages)
    ('} TRC`', '} ELC`'),
    ("TRC'", "ELC'"),
    ('USDT/TRC', 'USDT/ELC'),
    ('TRC残高', 'ELC残高'),
    ('TRCウォレット', 'ELCウォレット'),
    ('TRCトークン', 'ELCトークン'),
    ('TRC入金', 'ELC入金'),
    ('TRCステーク', 'ELCステーク'),
    ('TRC出金', 'ELC出金'),
    ('TRC報酬', 'ELC報酬'),
    ('TRC Кошелёк', 'ELC Кошелёк'),
    ('TRC Piniginė', 'ELC Piniginė'),
    ('TRC Stakinimas', 'ELC Stakinimas'),
    ('TRC Išėmimas', 'ELC Išėmimas'),
    ('TRC įnėšimas', 'ELC įnėšimas'),
    ('TRC Peněženka', 'ELC Peněženka'),
    ('TRC钱包', 'ELC钱包'),
    ('TRC余额', 'ELC余额'),
    ('通过TRC', '通过ELC'),
    ('h-TRC', 'h-ELC'),  # Hebrew
    ('-TRC', '-ELC'),
    
    # More translations
    ('TRCをステーク', 'ELCをステーク'),
    ('TRC代币', 'ELC代币'),
    ('TRC奖励', 'ELC奖励'),
    ('TRC Гаманець', 'ELC Гаманець'),
    ('.2f} TRC', '.2f} ELC'),
    ('TRC-Token', 'ELC-Token'),
    ('TRC einzahlen', 'ELC einzahlen'),
    ('TRC staken', 'ELC staken'),
    ('TRC abheben', 'ELC abheben'),
    ('Ihre TRC', 'Ihre ELC'),
    ('将TRC', '将ELC'),
    ('您的TRC', '您的ELC'),
    
    # General catch-all (but NOT TRC20!)
    (' TRC ', ' ELC '),
    (' TRC.', ' ELC.'),
    (' TRC,', ' ELC,'),
    (' TRC:', ' ELC:'),
    (' TRC\n', ' ELC\n'),
    (' TRC!', ' ELC!'),
    (' TRC？', ' ELC？'),
    ('{amount} TRC', '{amount} ELC'),
]

def fix_file(filepath):
    """Apply replacements to a single file."""
    if not os.path.exists(filepath):
        print(f"  Skip (not found): {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Fixed: {filepath}")
        return True
    else:
        print(f"  No changes: {filepath}")
        return False


def main():
    print("=" * 60)
    print("TRC -> ELC Token Rename Script")
    print("=" * 60)
    
    fixed_count = 0
    for filepath in FILES_TO_FIX:
        if fix_file(filepath):
            fixed_count += 1
    
    print("=" * 60)
    print(f"Done! Fixed {fixed_count} files.")
    print("=" * 60)


if __name__ == "__main__":
    main()
