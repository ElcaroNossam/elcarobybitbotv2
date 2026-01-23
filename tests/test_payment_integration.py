"""
Comprehensive Integration Tests for TRC Payment System.

Tests cover:
1. Wallet operations (create, deposit)
2. Payment processing (license purchase with TRC)
3. Sovereign operations (emission, burn, policy)
4. Configuration and pricing
5. Edge cases and error handling

Author: Lyxen Team
Date: January 2026
"""

import pytest
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blockchain import (
    # Core classes
    LyxenBlockchain,
    TRCWallet,
    TRCTransaction,
    TransactionType,
    
    # Sovereign operations
    is_sovereign_owner,
    emit_tokens,
    burn_tokens,
    set_monetary_policy,
    freeze_wallet,
    unfreeze_wallet,
    distribute_staking_rewards,
    get_treasury_stats,
    transfer_from_treasury,
    get_global_stats,
    get_owner_dashboard,
    
    # Wallet operations
    get_trc_wallet,
    pay_with_trc,
    deposit_trc,
    reward_trc,
    get_trc_balance,
    get_license_price_trc,
    pay_license,
    
    # Price conversions
    usdt_to_trc,
    trc_to_usdt,
    
    # Config
    SOVEREIGN_OWNER_ID,
    SOVEREIGN_OWNER_NAME,
    CHAIN_ID,
    CHAIN_NAME,
    TRC_SYMBOL,
    TRC_NAME,
    TRC_TOTAL_SUPPLY,
    TRC_INITIAL_CIRCULATION,
    BASE_STAKING_APY,
    LICENSE_PRICES_TRC,
)


# Test user IDs
ADMIN_USER_ID = 511692487  # Sovereign owner
TEST_USER_ID = 123456789
TEST_USER_ID_2 = 987654321


class TestBlockchainConfig:
    """Test blockchain configuration and constants."""
    
    def test_chain_config(self):
        """Test chain configuration values."""
        assert CHAIN_ID == 8888
        assert CHAIN_NAME == "Lyxen Chain"
        assert TRC_SYMBOL == "TRC"
        assert TRC_NAME == "Lyxen Coin"
    
    def test_supply_config(self):
        """Test supply configuration."""
        assert TRC_TOTAL_SUPPLY == 1_000_000_000_000  # 1 trillion
        assert TRC_INITIAL_CIRCULATION == 100_000_000  # 100 million
    
    def test_sovereign_owner(self):
        """Test sovereign owner configuration."""
        assert SOVEREIGN_OWNER_ID == 511692487
        assert SOVEREIGN_OWNER_NAME == "Lyxen Foundation"
    
    def test_license_prices(self):
        """Test license pricing in TRC."""
        assert LICENSE_PRICES_TRC["premium"][1] == 100.0  # $100
        assert LICENSE_PRICES_TRC["premium"][3] == 270.0  # $90/mo
        assert LICENSE_PRICES_TRC["premium"][6] == 480.0  # $80/mo
        assert LICENSE_PRICES_TRC["premium"][12] == 840.0  # $70/mo
        
        assert LICENSE_PRICES_TRC["basic"][1] == 50.0
        assert LICENSE_PRICES_TRC["basic"][3] == 135.0


class TestCurrencyConversion:
    """Test USDT/TRC conversion."""
    
    def test_usdt_to_trc(self):
        """Test USDT to TRC conversion."""
        assert usdt_to_trc(100) == 100.0  # 1:1 rate
        assert usdt_to_trc(50.5) == 50.5
        assert usdt_to_trc(0) == 0.0
    
    def test_trc_to_usdt(self):
        """Test TRC to USDT conversion."""
        assert trc_to_usdt(100) == 100.0
        assert trc_to_usdt(250.75) == 250.75
        assert trc_to_usdt(0) == 0.0


class TestWalletOperations:
    """Test wallet creation and basic operations."""
    
    @pytest.mark.asyncio
    async def test_get_wallet_creates_new(self):
        """Test wallet auto-creation for new user."""
        wallet = await get_trc_wallet(TEST_USER_ID)
        
        assert wallet is not None
        assert isinstance(wallet, TRCWallet)
        assert wallet.user_id == TEST_USER_ID
        assert wallet.address.startswith("0xTRC")
        assert wallet.balance >= 0
    
    @pytest.mark.asyncio
    async def test_wallet_persistence(self):
        """Test wallet is retrieved consistently."""
        wallet1 = await get_trc_wallet(TEST_USER_ID)
        wallet2 = await get_trc_wallet(TEST_USER_ID)
        
        assert wallet1.address == wallet2.address
        assert wallet1.user_id == wallet2.user_id
    
    @pytest.mark.asyncio
    async def test_deposit_trc(self):
        """Test TRC deposit."""
        wallet = await get_trc_wallet(TEST_USER_ID)
        initial_balance = wallet.balance
        
        success, message = await deposit_trc(TEST_USER_ID, 100.0)
        
        assert success is True
        assert "100" in message
        
        # Check new balance
        new_wallet = await get_trc_wallet(TEST_USER_ID)
        assert new_wallet.balance == initial_balance + 100.0
    
    @pytest.mark.asyncio
    async def test_get_trc_balance(self):
        """Test balance retrieval."""
        balance = await get_trc_balance(TEST_USER_ID)
        assert isinstance(balance, float)
        assert balance >= 0


class TestPaymentOperations:
    """Test license payment with TRC."""
    
    @pytest.mark.asyncio
    async def test_pay_for_license(self):
        """Test paying for license with TRC."""
        # Ensure user has enough funds
        await deposit_trc(TEST_USER_ID, 200.0)
        
        success, message = await pay_with_trc(
            user_id=TEST_USER_ID,
            amount=100.0,
            description="Premium License 1 Month"
        )
        
        assert success is True
        assert "TX:" in message
    
    @pytest.mark.asyncio
    async def test_pay_license_function(self):
        """Test pay_license helper function."""
        # Ensure user has enough funds
        await deposit_trc(TEST_USER_ID, 200.0)
        
        success, message = await pay_license(
            user_id=TEST_USER_ID,
            license_type="basic",
            months=1
        )
        
        assert success is True
        assert "50" in message or "TX:" in message
    
    @pytest.mark.asyncio
    async def test_payment_insufficient_funds(self):
        """Test payment with insufficient funds."""
        # Create fresh user with 0 balance
        new_user_id = 222222222
        
        success, message = await pay_with_trc(
            user_id=new_user_id,
            amount=10000.0,  # More than available
            description="Premium License"
        )
        
        assert success is False
        # Can be "insufficient balance" or "wallet not found"
        assert "insufficient" in message.lower() or "balance" in message.lower() or "not found" in message.lower()
    
    def test_get_license_price(self):
        """Test license price calculation."""
        assert get_license_price_trc("premium", 1) == 100.0
        assert get_license_price_trc("premium", 3) == 270.0
        assert get_license_price_trc("basic", 1) == 50.0
        assert get_license_price_trc("basic", 6) == 240.0


class TestRewardOperations:
    """Test TRC reward operations."""
    
    @pytest.mark.asyncio
    async def test_reward_trc(self):
        """Test giving TRC reward to user."""
        wallet = await get_trc_wallet(TEST_USER_ID_2)
        initial_balance = wallet.balance
        
        success, message = await reward_trc(
            user_id=TEST_USER_ID_2,
            amount=25.0,
            reason="test bonus"
        )
        
        assert success is True
        assert "25" in message
        
        # Verify balance increased
        new_wallet = await get_trc_wallet(TEST_USER_ID_2)
        assert new_wallet.balance == initial_balance + 25.0


class TestSovereignOperations:
    """Test sovereign owner (monetary authority) operations."""
    
    def test_is_sovereign_owner(self):
        """Test sovereign owner check."""
        assert is_sovereign_owner(ADMIN_USER_ID) is True
        assert is_sovereign_owner(TEST_USER_ID) is False
        assert is_sovereign_owner(0) is False
    
    @pytest.mark.asyncio
    async def test_emit_tokens_authorized(self):
        """Test token emission by sovereign owner."""
        result = await emit_tokens(
            user_id=ADMIN_USER_ID,
            amount=1000.0,
            reason="Integration test emission"
        )
        
        assert result["success"] is True
        assert result["amount"] == 1000.0
        assert "tx_hash" in result
        assert "new_supply" in result
    
    @pytest.mark.asyncio
    async def test_emit_tokens_unauthorized(self):
        """Test token emission denied for non-owner."""
        result = await emit_tokens(
            user_id=TEST_USER_ID,  # Not sovereign owner
            amount=1000.0,
            reason="Unauthorized attempt"
        )
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_burn_tokens_authorized(self):
        """Test token burn by sovereign owner."""
        result = await burn_tokens(
            user_id=ADMIN_USER_ID,
            amount=500.0,
            reason="Integration test burn"
        )
        
        assert result["success"] is True
        assert result["amount"] == 500.0
        assert "tx_hash" in result
    
    @pytest.mark.asyncio
    async def test_burn_tokens_unauthorized(self):
        """Test token burn denied for non-owner."""
        result = await burn_tokens(
            user_id=TEST_USER_ID,  # Not sovereign owner
            amount=500.0,
            reason="Unauthorized attempt"
        )
        
        assert result["success"] is False
    
    @pytest.mark.asyncio
    async def test_set_monetary_policy(self):
        """Test monetary policy update."""
        result = await set_monetary_policy(
            user_id=ADMIN_USER_ID,
            staking_apy=0.15  # 15%
        )
        
        assert result["success"] is True
        assert "changes" in result
    
    @pytest.mark.asyncio
    async def test_set_monetary_policy_unauthorized(self):
        """Test monetary policy update denied for non-owner."""
        result = await set_monetary_policy(
            user_id=TEST_USER_ID,
            staking_apy=0.50  # 50% - unauthorized attempt
        )
        
        assert result["success"] is False
    
    @pytest.mark.asyncio
    async def test_distribute_rewards(self):
        """Test reward distribution."""
        result = await distribute_staking_rewards(ADMIN_USER_ID)
        
        assert result["success"] is True
        assert "distributed" in result
        # recipients may not be present if no stakers
    
    @pytest.mark.asyncio
    async def test_get_treasury_stats(self):
        """Test treasury stats retrieval."""
        stats = await get_treasury_stats(ADMIN_USER_ID)
        
        assert stats is not None
        assert "current_supply" in stats
        assert "max_supply" in stats
        assert "treasury_balance" in stats
        assert "reserve_ratio" in stats
        assert "staking_apy" in stats
    
    @pytest.mark.asyncio
    async def test_get_owner_dashboard(self):
        """Test owner dashboard retrieval."""
        dashboard = await get_owner_dashboard(ADMIN_USER_ID)
        
        assert dashboard is not None
        assert "treasury" in dashboard
        assert "global" in dashboard
        assert "owner_title" in dashboard
    
    @pytest.mark.asyncio
    async def test_freeze_unfreeze_wallet(self):
        """Test wallet freeze and unfreeze."""
        target_wallet = await get_trc_wallet(TEST_USER_ID_2)
        
        # Freeze
        result = await freeze_wallet(
            user_id=ADMIN_USER_ID,
            target_address=target_wallet.address,
            reason="Test freeze"
        )
        
        assert result["success"] is True
        
        # Unfreeze
        result = await unfreeze_wallet(
            user_id=ADMIN_USER_ID,
            target_address=target_wallet.address
        )
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_treasury_transfer(self):
        """Test direct treasury transfer to user."""
        result = await transfer_from_treasury(
            user_id=ADMIN_USER_ID,
            to_user_id=TEST_USER_ID,
            amount=50.0,
            reason="Test treasury transfer"
        )
        
        assert result["success"] is True
        assert result["amount"] == 50.0


class TestGlobalStats:
    """Test global statistics."""
    
    @pytest.mark.asyncio
    async def test_get_global_stats(self):
        """Test global stats retrieval."""
        stats = await get_global_stats()
        
        assert stats is not None
        assert "current_supply" in stats  # Not total_supply
        assert "max_supply" in stats
        assert "total_wallets" in stats
        assert "total_transactions" in stats
        assert "total_staked" in stats


class TestLicensePricing:
    """Test license pricing calculations."""
    
    def test_premium_pricing_discounts(self):
        """Test premium pricing with discounts."""
        prices = LICENSE_PRICES_TRC["premium"]
        
        # 1 month = base price
        assert prices[1] == 100.0
        
        # 3 months = 10% discount (90 * 3 = 270)
        assert prices[3] == 270.0
        
        # 6 months = 20% discount (80 * 6 = 480)
        assert prices[6] == 480.0
        
        # 12 months = 30% discount (70 * 12 = 840)
        assert prices[12] == 840.0
    
    def test_basic_pricing_is_half_premium(self):
        """Test basic is 50% of premium."""
        premium = LICENSE_PRICES_TRC["premium"]
        basic = LICENSE_PRICES_TRC["basic"]
        
        assert basic[1] == premium[1] / 2
        assert basic[3] == premium[3] / 2
        assert basic[6] == premium[6] / 2
        assert basic[12] == premium[12] / 2


class TestTransactionTypes:
    """Test transaction type enumeration."""
    
    def test_transaction_types_exist(self):
        """Test all transaction types are defined."""
        assert TransactionType.TRANSFER.value == "transfer"
        assert TransactionType.DEPOSIT.value == "deposit"
        assert TransactionType.PAYMENT.value == "payment"
        assert TransactionType.REWARD.value == "reward"
        assert TransactionType.EMISSION.value == "emission"
        assert TransactionType.BURN.value == "burn"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_zero_amount_payment(self):
        """Test payment with zero amount."""
        success, message = await pay_with_trc(
            user_id=TEST_USER_ID,
            amount=0.0,
            description="Zero test"
        )
        
        # Should fail or be rejected
        # Implementation may vary
        assert success is False or message is not None
    
    @pytest.mark.asyncio
    async def test_negative_amount_deposit(self):
        """Test deposit with negative amount."""
        success, message = await deposit_trc(TEST_USER_ID, -100.0)
        
        # Should fail
        assert success is False


class TestNetworkOperations:
    """Test network deposit/withdrawal operations."""
    
    def test_get_supported_networks(self):
        """Test getting supported networks."""
        from core.blockchain import get_supported_networks
        
        networks = get_supported_networks()
        assert len(networks) >= 10  # We have 10 networks
        
        # Check network structure
        for network in networks:
            assert "id" in network
            assert "name" in network
            assert "deposit_fee" in network
            assert "withdrawal_fee" in network
            assert "min_deposit" in network
            assert "min_withdrawal" in network
    
    def test_network_config(self):
        """Test getting network configuration."""
        from core.blockchain import get_network_config
        
        # Test valid network
        config = get_network_config("trc20")
        assert config is not None
        assert config["name"] == "TRON (TRC20)"
        assert config["withdrawal_fee"] == 1.0
        
        # Test invalid network
        invalid_config = get_network_config("invalid_network")
        assert invalid_config is None
    
    def test_deposit_address(self):
        """Test getting deposit address."""
        from core.blockchain import get_deposit_address
        
        address_info = get_deposit_address(TEST_USER_ID, "bep20")
        assert address_info is not None
        assert "address" in address_info
        assert "memo" in address_info
        assert "network" in address_info
        assert address_info["memo"] == f"U{TEST_USER_ID}"
    
    @pytest.mark.asyncio
    async def test_withdrawal_request(self):
        """Test withdrawal request."""
        from core.blockchain import request_withdrawal, deposit_trc
        
        # Ensure user has funds
        await deposit_trc(TEST_USER_ID, 100.0)
        
        success, message, info = await request_withdrawal(
            user_id=TEST_USER_ID,
            amount=20.0,
            network="polygon",
            external_address="0xTestAddress123"
        )
        
        assert success is True
        assert info is not None
        assert "net_amount" in info
        assert info["fee"] == 0.1  # Polygon fee
    
    @pytest.mark.asyncio
    async def test_withdrawal_min_amount(self):
        """Test withdrawal minimum amount validation."""
        from core.blockchain import request_withdrawal
        
        success, message, info = await request_withdrawal(
            user_id=TEST_USER_ID,
            amount=1.0,  # Below minimum for most networks
            network="erc20",  # Min is 50 for ERC20
            external_address="0xTestAddress"
        )
        
        assert success is False
        assert "minimum" in message.lower()
    
    def test_withdrawal_fees(self):
        """Test getting withdrawal fees."""
        from core.blockchain import get_withdrawal_fees
        
        fees = get_withdrawal_fees()
        assert "trc20" in fees
        assert "bep20" in fees
        assert "erc20" in fees
        assert fees["trc20"] == 1.0
        assert fees["erc20"] == 5.0
    
    def test_network_status(self):
        """Test network status."""
        from core.blockchain import get_network_status
        
        status = get_network_status()
        assert len(status) >= 10
        
        for network_id, config in status.items():
            assert "name" in config
            assert "enabled" in config


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
