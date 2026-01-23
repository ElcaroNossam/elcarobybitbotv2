"""
ELCARO Chain - Complete Blockchain Demo

Demonstrates full blockchain functionality:
- Chain initialization and block production
- Validator network
- DEX trading (AMM + Order Book)
- Perpetual futures
- Cross-chain bridge
- DAO governance
"""

import logging
from decimal import Decimal
import time

from blockchain.chain import LyxenChain, ConsensusEngine, generate_address, elc_to_wei
from blockchain.dex import LyxenDEX, OrderSide, OrderType, PositionSide
from blockchain.bridge import LyxenBridge, BridgeChain, BridgeRelayer
from blockchain.governance import LyxenDAO, VoteOption, ProposalType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_blockchain_basics():
    """Demo: Basic blockchain operations."""
    logger.info("\n" + "="*80)
    logger.info("DEMO 1: Blockchain Basics")
    logger.info("="*80)
    
    # Initialize chain
    chain = LyxenChain(chain_id=1, block_time=2, max_validators=100)
    consensus = ConsensusEngine(chain)
    
    logger.info(f"✅ Chain initialized: {chain.get_chain_stats()}")
    
    # Create accounts
    alice = generate_address()
    bob = generate_address()
    carol = generate_address()
    
    # Give initial balances
    chain.create_account(alice, elc_to_wei(1000000))  # 1M ELC
    chain.create_account(bob, elc_to_wei(500000))    # 500k ELC
    chain.create_account(carol, elc_to_wei(250000))  # 250k ELC
    
    logger.info(f"✅ Accounts created:")
    logger.info(f"   Alice: {alice[:20]}... = {chain.get_balance(alice)} wei")
    logger.info(f"   Bob: {bob[:20]}... = {chain.get_balance(bob)} wei")
    logger.info(f"   Carol: {carol[:20]}... = {chain.get_balance(carol)} wei")
    
    # Create transactions
    tx1 = chain.create_transaction(alice, bob, elc_to_wei(100))  # Alice → Bob: 100 ELC
    tx2 = chain.create_transaction(bob, carol, elc_to_wei(50))   # Bob → Carol: 50 ELC
    
    chain.add_transaction(tx1)
    chain.add_transaction(tx2)
    
    logger.info(f"✅ Transactions created and added to mempool: {len(chain.pending_transactions)}")
    
    # Register validators
    validator1 = generate_address()
    validator2 = generate_address()
    validator3 = generate_address()
    
    chain.create_account(validator1, elc_to_wei(1000000))
    chain.create_account(validator2, elc_to_wei(800000))
    chain.create_account(validator3, elc_to_wei(600000))
    
    chain.register_validator(validator1, elc_to_wei(150000), Decimal("0.05"))
    chain.register_validator(validator2, elc_to_wei(120000), Decimal("0.07"))
    chain.register_validator(validator3, elc_to_wei(100000), Decimal("0.10"))
    
    logger.info(f"✅ Validators registered: {len(chain.validators)}")
    
    # Produce blocks
    for i in range(3):
        producer = chain.select_block_producer()
        if producer:
            block = chain.produce_block(producer)
            logger.info(f"✅ Block #{block.block_number} produced by {producer[:20]}... with {len(block.transactions)} txs")
            
            # Validators sign block
            consensus.sign_block(block.block_hash, validator1)
            consensus.sign_block(block.block_hash, validator2)
            consensus.sign_block(block.block_hash, validator3)
            
            if consensus.is_block_finalized(block.block_hash):
                logger.info(f"   Block finalized with {len(consensus.get_block_signatures(block.block_hash))} signatures")
        
        time.sleep(0.5)  # Simulate block time
    
    # Check final balances
    logger.info(f"\n✅ Final balances:")
    logger.info(f"   Alice: {chain.get_balance(alice)} wei")
    logger.info(f"   Bob: {chain.get_balance(bob)} wei")
    logger.info(f"   Carol: {chain.get_balance(carol)} wei")
    
    stats = chain.get_chain_stats()
    logger.info(f"\n✅ Chain stats: {stats}")


def demo_dex_trading():
    """Demo: DEX trading with AMM and order book."""
    logger.info("\n" + "="*80)
    logger.info("DEMO 2: DEX Trading")
    logger.info("="*80)
    
    # Initialize DEX
    dex = LyxenDEX()
    
    # Create trading pair: ELC/USDT
    dex.create_trading_pair(
        symbol="ELC/USDT",
        token_a="ELC",
        token_b="USDT",
        initial_a=Decimal("1000000"),  # 1M ELC
        initial_b=Decimal("1000000")   # 1M USDT (1:1 initial price)
    )
    
    logger.info(f"✅ Trading pair created: ELC/USDT")
    
    # AMM: Swap tokens
    alice = "alice_address"
    amount_out = dex.swap_tokens("ELC_USDT", "USDT", Decimal("1000"), min_amount_out=Decimal("990"))
    logger.info(f"✅ Swap: 1000 USDT → {amount_out} ELC")
    
    # Add liquidity
    bob = "bob_address"
    shares = dex.amm.add_liquidity(bob, "ELC_USDT", Decimal("50000"), Decimal("50000"))
    logger.info(f"✅ Liquidity added: 50k ELC + 50k USDT → {shares} LP tokens")
    
    # Order Book: Place limit orders
    order1_id = dex.place_limit_order(
        user=alice,
        symbol="ELC/USDT",
        side=OrderSide.BUY,
        price=Decimal("0.98"),
        size=Decimal("10000")
    )
    logger.info(f"✅ Limit order placed: BUY 10k ELC @ $0.98")
    
    order2_id = dex.place_limit_order(
        user=bob,
        symbol="ELC/USDT",
        side=OrderSide.SELL,
        price=Decimal("1.02"),
        size=Decimal("8000")
    )
    logger.info(f"✅ Limit order placed: SELL 8k ELC @ $1.02")
    
    # Perpetual Futures: Open long position
    carol = "carol_address"
    position = dex.open_perpetual(
        user=carol,
        symbol="BTC/USDT",
        side=PositionSide.LONG,
        size=Decimal("1.0"),  # 1 BTC
        entry_price=Decimal("50000"),
        leverage=10
    )
    logger.info(f"✅ Perpetual opened: 1 BTC LONG @ $50k with 10x leverage")
    logger.info(f"   Margin: {position.margin} USDT, Liquidation: ${position.liquidation_price}")
    
    # Update PnL
    dex.perpetuals.update_position_pnl(carol, "BTC/USDT", Decimal("52000"))
    updated_position = dex.perpetuals.get_position(carol, "BTC/USDT")
    logger.info(f"✅ PnL updated: Current price $52k, Unrealized PnL: ${updated_position.unrealized_pnl}")
    
    # DEX stats
    stats = dex.get_stats()
    logger.info(f"\n✅ DEX stats: {stats}")


def demo_bridge():
    """Demo: Cross-chain bridge operations."""
    logger.info("\n" + "="*80)
    logger.info("DEMO 3: Cross-Chain Bridge")
    logger.info("="*80)
    
    # Initialize bridge
    bridge = LyxenBridge()
    
    # Register wrapped tokens
    bridge.register_wrapped_token(
        symbol="WETH",
        name="Wrapped Ethereum",
        origin_chain=BridgeChain.ETHEREUM,
        origin_address="0x0000000000000000000000000000000000000000",
        elcaro_address="0xELC_WETH_ADDRESS"
    )
    logger.info(f"✅ Wrapped token registered: WETH from Ethereum")
    
    # Register validators
    for i in range(10):
        validator_addr = f"validator_{i}"
        bridge.register_validator(
            address=validator_addr,
            chains=[BridgeChain.ETHEREUM, BridgeChain.ELCARO, BridgeChain.BSC]
        )
    logger.info(f"✅ Bridge validators registered: {len(bridge.validators)}")
    
    # Initiate bridge transfer (ETH → ELCARO)
    alice = "alice_eth_address"
    transfer_id = bridge.initiate_transfer(
        from_chain=BridgeChain.ETHEREUM,
        to_chain=BridgeChain.ELCARO,
        from_address=alice,
        to_address="alice_elcaro_address",
        token="WETH",
        amount=Decimal("10"),  # 10 ETH
        lock_tx_hash="0xeth_lock_tx_hash"
    )
    logger.info(f"✅ Bridge transfer initiated: {transfer_id}")
    logger.info(f"   10 ETH locked on Ethereum, awaiting signatures...")
    
    # Validators sign transfer
    for i in range(7):  # Need 7-of-10
        validator_addr = f"validator_{i}"
        signature = f"sig_{validator_addr}_{transfer_id}"
        bridge.sign_transfer(transfer_id, validator_addr, signature)
    
    transfer = bridge.get_transfer(transfer_id)
    logger.info(f"✅ Transfer status: {transfer.status.value}")
    logger.info(f"   Signatures: {len(transfer.signatures)}/{transfer.required_signatures}")
    
    # Large transfer (with timelock)
    bob = "bob_eth_address"
    large_transfer_id = bridge.initiate_transfer(
        from_chain=BridgeChain.ETHEREUM,
        to_chain=BridgeChain.ELCARO,
        from_address=bob,
        to_address="bob_elcaro_address",
        token="WETH",
        amount=Decimal("150000"),  # $150k worth
        lock_tx_hash="0xeth_large_lock_tx"
    )
    large_transfer = bridge.get_transfer(large_transfer_id)
    logger.info(f"✅ Large transfer initiated with timelock")
    logger.info(f"   Amount: {large_transfer.amount}, Timelock until: {large_transfer.timelock_until}")
    
    # Bridge stats
    stats = bridge.get_stats()
    logger.info(f"\n✅ Bridge stats: {stats}")


def demo_governance():
    """Demo: DAO governance and voting."""
    logger.info("\n" + "="*80)
    logger.info("DEMO 4: DAO Governance")
    logger.info("="*80)
    
    # Initialize DAO
    dao = LyxenDAO(
        treasury_balance=Decimal("200000000"),  # 200M ELC
        circulating_supply=Decimal("1000000000")  # 1B ELC
    )
    
    logger.info(f"✅ DAO initialized with {dao.treasury_balance} ELC treasury")
    
    # Users lock tokens for voting
    alice = "alice_address"
    bob = "bob_address"
    carol = "carol_address"
    david = "david_address"
    
    dao.lock_tokens_for_voting(alice, Decimal("500000"))   # 500k ELC
    dao.lock_tokens_for_voting(bob, Decimal("300000"))     # 300k ELC
    dao.lock_tokens_for_voting(carol, Decimal("200000"))   # 200k ELC
    dao.lock_tokens_for_voting(david, Decimal("150000"))   # 150k ELC
    
    logger.info(f"✅ Users locked tokens for voting:")
    logger.info(f"   Alice: {dao.get_voting_power(alice)}")
    logger.info(f"   Bob: {dao.get_voting_power(bob)}")
    logger.info(f"   Carol: {dao.get_voting_power(carol)}")
    logger.info(f"   David: {dao.get_voting_power(david)}")
    
    # Create proposal: Reduce trading fees
    proposal_id = dao.create_proposal(
        proposer=alice,
        proposal_type=ProposalType.PARAMETER_CHANGE,
        title="Reduce Trading Fees: 0.1% → 0.08%",
        description="Proposal to reduce spot trading fees from 0.1% to 0.08% to increase volume and compete with other DEXs.\n\nBenefits:\n- More competitive fees\n- Higher trading volume\n- More fee revenue (via volume increase)\n\nRisks:\n- Reduced per-trade revenue\n- May not significantly increase volume"
    )
    logger.info(f"✅ Proposal created: {proposal_id}")
    
    # Simulate discussion period ending
    proposal = dao.get_proposal(proposal_id)
    proposal.voting_start = int(time.time()) - 1  # Make voting start immediately
    dao.activate_proposal(proposal_id)
    logger.info(f"✅ Proposal activated for voting")
    
    # Cast votes
    dao.cast_vote(alice, proposal_id, VoteOption.FOR, "Lower fees will attract more traders")
    dao.cast_vote(bob, proposal_id, VoteOption.FOR, "Agree, volume is more important than per-trade fees")
    dao.cast_vote(carol, proposal_id, VoteOption.AGAINST, "Fees are already competitive")
    dao.cast_vote(david, proposal_id, VoteOption.FOR, "Support fee reduction")
    
    logger.info(f"✅ Votes cast:")
    logger.info(f"   For: {proposal.votes_for}")
    logger.info(f"   Against: {proposal.votes_against}")
    logger.info(f"   Total: {proposal.total_votes} (Quorum: {proposal.quorum})")
    
    # Finalize proposal
    proposal.voting_end = int(time.time()) - 1  # Make voting end immediately
    dao.finalize_proposal(proposal_id)
    logger.info(f"✅ Proposal finalized: {proposal.status.value}")
    
    if proposal.has_succeeded:
        logger.info(f"   ✅ Proposal passed! Queued for execution at {proposal.execution_time}")
    
    # Create treasury spending proposal
    grant_proposal_id = dao.create_proposal(
        proposer=bob,
        proposal_type=ProposalType.TREASURY_SPENDING,
        title="Developer Grant: 100,000 ELC for New DEX UI",
        description="Proposal to grant 100,000 ELC to development team for building improved DEX user interface.\n\nDeliverables:\n- Modern React-based UI\n- Mobile responsive design\n- Advanced charting (TradingView)\n- One-click trading\n\nTimeline: 3 months",
        targets=["dev_team_address"],
        values=[Decimal("100000")]
    )
    logger.info(f"✅ Treasury spending proposal created: {grant_proposal_id}")
    
    # DAO stats
    stats = dao.get_stats()
    logger.info(f"\n✅ DAO stats:")
    for key, value in stats.items():
        logger.info(f"   {key}: {value}")


def demo_complete_ecosystem():
    """Demo: Complete ecosystem in action."""
    logger.info("\n" + "="*80)
    logger.info("DEMO 5: Complete Ecosystem")
    logger.info("="*80)
    
    # 1. Initialize all components
    logger.info("\n📦 Initializing ELCARO Chain ecosystem...")
    
    chain = LyxenChain(chain_id=1)
    consensus = ConsensusEngine(chain)
    dex = LyxenDEX()
    bridge = LyxenBridge()
    dao = LyxenDAO()
    
    logger.info("✅ All components initialized")
    
    # 2. Setup validators
    logger.info("\n👥 Setting up validator network...")
    validators = []
    for i in range(5):
        addr = generate_address()
        chain.create_account(addr, elc_to_wei(1000000))
        chain.register_validator(addr, elc_to_wei(150000), Decimal("0.05"))
        validators.append(addr)
        logger.info(f"   Validator {i+1}: {addr[:20]}...")
    
    # 3. Create trading pairs
    logger.info("\n💱 Creating trading pairs...")
    dex.create_trading_pair("ELC/USDT", "ELC", "USDT", Decimal("1000000"), Decimal("1000000"))
    dex.create_trading_pair("BTC/USDT", "BTC", "USDT", Decimal("20"), Decimal("1000000"))
    logger.info("   ✅ ELC/USDT pair created")
    logger.info("   ✅ BTC/USDT pair created")
    
    # 4. Setup bridge
    logger.info("\n🌉 Setting up cross-chain bridge...")
    bridge.register_wrapped_token("WETH", "Wrapped Ethereum", BridgeChain.ETHEREUM, "0x...", "0xELC...")
    bridge.register_wrapped_token("WBNB", "Wrapped BNB", BridgeChain.BSC, "0x...", "0xELC...")
    logger.info("   ✅ WETH registered")
    logger.info("   ✅ WBNB registered")
    
    # 5. Simulate trading activity
    logger.info("\n📈 Simulating trading activity...")
    
    trader1 = generate_address()
    trader2 = generate_address()
    chain.create_account(trader1, elc_to_wei(100000))
    chain.create_account(trader2, elc_to_wei(100000))
    
    # Spot trades
    dex.swap_tokens("ELC_USDT", "USDT", Decimal("10000"))
    dex.swap_tokens("ELC_USDT", "ELC", Decimal("5000"))
    logger.info("   ✅ 2 spot trades executed")
    
    # Perpetual positions
    dex.open_perpetual(trader1, "BTC/USDT", PositionSide.LONG, Decimal("0.5"), Decimal("50000"), 20)
    dex.open_perpetual(trader2, "BTC/USDT", PositionSide.SHORT, Decimal("0.3"), Decimal("50000"), 15)
    logger.info("   ✅ 2 perpetual positions opened")
    
    # 6. Governance activity
    logger.info("\n🏛️ Governance activity...")
    
    dao_member = generate_address()
    dao.lock_tokens_for_voting(dao_member, Decimal("500000"))
    
    prop_id = dao.create_proposal(
        proposer=dao_member,
        proposal_type=ProposalType.PARAMETER_CHANGE,
        title="Increase Max Leverage: 100x → 125x",
        description="Proposal to increase maximum leverage for perpetual futures."
    )
    logger.info(f"   ✅ Proposal created: {prop_id}")
    
    # 7. Block production
    logger.info("\n⛏️ Producing blocks...")
    for i in range(5):
        producer = chain.select_block_producer()
        block = chain.produce_block(producer)
        logger.info(f"   Block #{block.block_number}: {len(block.transactions)} txs by {producer[:20]}...")
        
        # Consensus
        for val in validators[:3]:
            consensus.sign_block(block.block_hash, val)
        
        time.sleep(0.3)
    
    # 8. Final stats
    logger.info("\n" + "="*80)
    logger.info("📊 FINAL ECOSYSTEM STATS")
    logger.info("="*80)
    
    chain_stats = chain.get_chain_stats()
    dex_stats = dex.get_stats()
    bridge_stats = bridge.get_stats()
    dao_stats = dao.get_stats()
    
    logger.info(f"\n🔗 Blockchain:")
    logger.info(f"   Block height: {chain_stats['block_height']}")
    logger.info(f"   Total transactions: {chain_stats['total_transactions']}")
    logger.info(f"   Active validators: {chain_stats['active_validators']}")
    
    logger.info(f"\n💱 DEX:")
    logger.info(f"   Fees collected: {dex_stats['total_fees_collected']}")
    logger.info(f"   Fees burned: {dex_stats['fees_burned']}")
    logger.info(f"   Active positions: {dex_stats['active_positions']}")
    
    logger.info(f"\n🌉 Bridge:")
    logger.info(f"   Total transfers: {bridge_stats['total_transfers']}")
    logger.info(f"   Total volume: {bridge_stats['total_volume']}")
    logger.info(f"   Insurance fund: {bridge_stats['insurance_fund']}")
    
    logger.info(f"\n🏛️ DAO:")
    logger.info(f"   Total proposals: {dao_stats['total_proposals']}")
    logger.info(f"   Treasury balance: {dao_stats['treasury_balance']}")
    logger.info(f"   Unique voters: {dao_stats['unique_voters']}")


if __name__ == "__main__":
    logger.info("\n" + "="*80)
    logger.info("🚀 ELCARO CHAIN - COMPLETE BLOCKCHAIN DEMO")
    logger.info("="*80)
    
    try:
        # Run all demos
        demo_blockchain_basics()
        demo_dex_trading()
        demo_bridge()
        demo_governance()
        demo_complete_ecosystem()
        
        logger.info("\n" + "="*80)
        logger.info("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\n❌ Demo failed: {e}", exc_info=True)
