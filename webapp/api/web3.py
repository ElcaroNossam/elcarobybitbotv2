"""
Web3 API Endpoints - FastAPI router for blockchain interactions
"""
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)

# Import blockchain modules
try:
    from blockchain import Web3Client, NetworkType, ElcaroToken, StrategyNFT, StrategyMarketplace
    from blockchain.wallet_integration import WalletAuth
    from blockchain.db_integration import (
        set_user_wallet, get_user_wallet, save_user_strategy, get_user_strategies,
        get_strategy_by_id, create_strategy_nft, get_user_nfts, log_blockchain_tx,
        update_tx_status, get_user_transactions, update_token_balance, init_web3_tables
    )
    from blockchain.token_contract import TokenPriceOracle
    WEB3_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Web3 modules not available: {e}")
    WEB3_AVAILABLE = False

router = APIRouter()


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class WalletConnectRequest(BaseModel):
    """Wallet connection request"""
    wallet_address: str = Field(..., description="Wallet address (0x...)")
    network: str = Field("polygon", description="Network name")


class WalletSignRequest(BaseModel):
    """Wallet signature verification"""
    wallet_address: str
    signature: str
    message: str


class StrategyCreateRequest(BaseModel):
    """Create/save strategy"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field("", max_length=500)
    base_strategy: str = Field("custom", description="Base strategy type")
    config: Dict[str, Any] = Field(..., description="Strategy configuration")


class StrategyMintRequest(BaseModel):
    """Mint strategy NFT"""
    strategy_id: int
    price_elcaro: float = Field(..., gt=0, description="NFT price in ELCARO")


class StrategyListRequest(BaseModel):
    """List strategy on marketplace"""
    token_id: int
    price_elcaro: float = Field(..., gt=0)
    royalty_percent: float = Field(5.0, ge=0, le=25)


class SubscriptionPurchaseRequest(BaseModel):
    """Purchase subscription with ELCARO"""
    plan: str = Field(..., pattern="^(basic|premium)$")
    months: int = Field(..., ge=1, le=12)


# ==========================================
# DEPENDENCY: GET CURRENT USER
# ==========================================

# Import centralized authentication
from webapp.api.auth import get_current_user


# ==========================================
# WALLET ENDPOINTS
# ==========================================

@router.post("/wallet/connect")
async def connect_wallet(
    request: WalletConnectRequest,
    user: Dict = Depends(get_current_user)
):
    """
    Step 1: Connect wallet to user account.
    Returns message to sign for verification.
    """
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    # Generate nonce and message
    nonce = WalletAuth.generate_nonce()
    message = WalletAuth.generate_signin_message(request.wallet_address, nonce)
    
    return {
        'success': True,
        'message': message,
        'nonce': nonce,
        'network': request.network
    }


@router.post("/wallet/verify")
async def verify_wallet(
    request: WalletSignRequest,
    user: Dict = Depends(get_current_user)
):
    """
    Step 2: Verify wallet signature and link to account.
    """
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    # Verify signature
    is_valid = WalletAuth.verify_signature(
        request.message,
        request.signature,
        request.wallet_address
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Link wallet to user
    set_user_wallet(
        user_id=user['user_id'],
        wallet_address=request.wallet_address,
        network="polygon",  # Default network
        verified=True
    )
    
    return {
        'success': True,
        'wallet_address': request.wallet_address,
        'verified': True
    }


@router.get("/wallet/info")
async def get_wallet_info(user: Dict = Depends(get_current_user)):
    """Get user's connected wallet info"""
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    wallet = get_user_wallet(user['user_id'])
    
    if not wallet:
        return {'connected': False}
    
    return {
        'connected': True,
        'wallet_address': wallet['wallet_address'],
        'network': wallet['network'],
        'verified': wallet['verified'],
        'elcaro_balance': wallet['elcaro_balance'],
        'balance_updated_at': wallet['balance_updated_at']
    }


@router.post("/wallet/refresh-balance")
async def refresh_token_balance(user: Dict = Depends(get_current_user)):
    """Refresh LYXEN token balance from blockchain"""
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    wallet = get_user_wallet(user['user_id'])
    if not wallet:
        raise HTTPException(status_code=400, detail="No wallet connected")
    
    try:
        # Create Web3 client
        network = NetworkType(wallet['network'])
        client = Web3Client(network=network)
        
        # Get token contract
        token = ElcaroToken(client)
        
        # Get balance
        balance = await token.balance_of(wallet['wallet_address'])
        
        # Update in database
        update_token_balance(user['user_id'], balance)
        
        return {
            'success': True,
            'balance': balance,
            'updated_at': int(datetime.now().timestamp())
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh balance: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh balance")


# ==========================================
# STRATEGY ENDPOINTS
# ==========================================

@router.post("/strategies/save")
async def save_strategy(
    request: StrategyCreateRequest,
    user: Dict = Depends(get_current_user)
):
    """
    Save custom strategy configuration.
    User can then mint it as NFT.
    """
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    try:
        strategy_id = save_user_strategy(
            user_id=user['user_id'],
            name=request.name,
            config=request.config,
            description=request.description,
            base_strategy=request.base_strategy
        )
        
        return {
            'success': True,
            'strategy_id': strategy_id,
            'message': 'Strategy saved successfully'
        }
        
    except Exception as e:
        logger.error(f"Failed to save strategy: {e}")
        raise HTTPException(status_code=500, detail="Failed to save strategy")


@router.get("/strategies/my")
async def get_my_strategies(
    active_only: bool = True,
    user: Dict = Depends(get_current_user)
):
    """Get all strategies created by user"""
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    strategies = get_user_strategies(user['user_id'], active_only=active_only)
    
    return {
        'success': True,
        'strategies': strategies,
        'count': len(strategies)
    }


@router.get("/strategies/{strategy_id}")
async def get_strategy_detail(
    strategy_id: int,
    user: Dict = Depends(get_current_user)
):
    """Get strategy details"""
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    strategy = get_strategy_by_id(strategy_id)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Check ownership or public
    if strategy['user_id'] != user['user_id'] and not strategy['is_public']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        'success': True,
        'strategy': strategy
    }


@router.post("/strategies/mint-nft")
async def mint_strategy_nft(
    request: StrategyMintRequest,
    user: Dict = Depends(get_current_user)
):
    """
    Mint strategy as NFT on blockchain.
    Requires wallet connection and gas fees.
    """
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    # Get wallet
    wallet = get_user_wallet(user['user_id'])
    if not wallet:
        raise HTTPException(status_code=400, detail="Please connect wallet first")
    
    # Get strategy
    strategy = get_strategy_by_id(request.strategy_id)
    if not strategy or strategy['user_id'] != user['user_id']:
        raise HTTPException(status_code=403, detail="Strategy not found or access denied")
    
    try:
        # Create Web3 client with user's wallet
        # Note: In production, user signs transaction in browser
        # This is simplified version
        network = NetworkType(wallet['network'])
        client = Web3Client(network=network)
        
        # Get NFT contract
        nft_contract = StrategyNFT(client)
        
        # Prepare metadata
        from blockchain.nft_contract import create_strategy_metadata
        metadata = create_strategy_metadata(
            strategy_id=strategy['id'],
            name=strategy['name'],
            description=strategy['description'],
            creator=user['username'],
            base_strategy=strategy['base_strategy'],
            performance={
                'win_rate': strategy.get('win_rate', 0),
                'total_pnl_percent': strategy.get('total_pnl', 0),
                'total_trades': strategy.get('total_trades', 0)
            }
        )
        
        # Mint NFT (this would be done by user in browser)
        result = await nft_contract.mint_strategy_nft(
            to_address=wallet['wallet_address'],
            strategy_id=strategy['id'],
            metadata=metadata
        )
        
        # Save NFT record
        nft_id = create_strategy_nft(
            strategy_id=strategy['id'],
            contract_address=nft_contract.contract_address,
            network=wallet['network'],
            owner_address=wallet['wallet_address'],
            creator_address=wallet['wallet_address'],
            mint_tx_hash=result['tx_hash']
        )
        
        # Log transaction
        log_blockchain_tx(
            user_id=user['user_id'],
            tx_hash=result['tx_hash'],
            network=wallet['network'],
            tx_type='nft_mint',
            from_address=wallet['wallet_address'],
            to_address=nft_contract.contract_address,
            data={'strategy_id': strategy['id'], 'nft_id': nft_id}
        )
        
        return {
            'success': True,
            'tx_hash': result['tx_hash'],
            'nft_id': nft_id,
            'explorer_url': result['explorer_url']
        }
        
    except Exception as e:
        logger.error(f"Failed to mint NFT: {e}")
        raise HTTPException(status_code=500, detail="Failed to mint NFT")


@router.get("/strategies/my-nfts")
async def get_my_nfts(user: Dict = Depends(get_current_user)):
    """Get all strategy NFTs owned by user"""
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    wallet = get_user_wallet(user['user_id'])
    if not wallet:
        return {'success': True, 'nfts': [], 'count': 0}
    
    nfts = get_user_nfts(wallet['wallet_address'])
    
    return {
        'success': True,
        'nfts': nfts,
        'count': len(nfts)
    }


# ==========================================
# MARKETPLACE ENDPOINTS
# ==========================================

@router.post("/marketplace/list")
async def list_strategy_on_marketplace(
    request: StrategyListRequest,
    user: Dict = Depends(get_current_user)
):
    """List strategy NFT for sale on marketplace"""
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    wallet = get_user_wallet(user['user_id'])
    if not wallet:
        raise HTTPException(status_code=400, detail="Please connect wallet first")
    
    try:
        network = NetworkType(wallet['network'])
        client = Web3Client(network=network)
        
        marketplace = StrategyMarketplace(client)
        
        # List on marketplace
        result = await marketplace.list_strategy(
            token_id=request.token_id,
            price=request.price_elcaro,
            royalty_percent=request.royalty_percent
        )
        
        # Log transaction
        log_blockchain_tx(
            user_id=user['user_id'],
            tx_hash=result['tx_hash'],
            network=wallet['network'],
            tx_type='marketplace_list',
            from_address=wallet['wallet_address'],
            to_address=marketplace.contract_address,
            amount=request.price_elcaro,
            token_symbol='ELCARO',
            data={'token_id': request.token_id, 'royalty_percent': request.royalty_percent}
        )
        
        return {
            'success': True,
            'tx_hash': result['tx_hash'],
            'explorer_url': result['explorer_url']
        }
        
    except Exception as e:
        logger.error(f"Failed to list strategy: {e}")
        raise HTTPException(status_code=500, detail="Failed to list strategy")


@router.get("/marketplace/listings")
async def get_marketplace_listings():
    """Get all active marketplace listings"""
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    # TODO: Implement pagination
    # For now, return simplified version
    
    return {
        'success': True,
        'listings': [],
        'message': 'Marketplace coming soon'
    }


# ==========================================
# SUBSCRIPTION ENDPOINTS
# ==========================================

@router.post("/subscription/purchase")
async def purchase_subscription_with_tokens(
    request: SubscriptionPurchaseRequest,
    user: Dict = Depends(get_current_user)
):
    """Purchase subscription with LYXEN tokens"""
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    wallet = get_user_wallet(user['user_id'])
    if not wallet:
        raise HTTPException(status_code=400, detail="Please connect wallet first")
    
    try:
        # Calculate price in ELCARO
        price_elcaro = await TokenPriceOracle.convert_subscription_price(
            request.plan, request.months
        )
        
        # Create Web3 client
        network = NetworkType(wallet['network'])
        client = Web3Client(network=network)
        
        # Get marketplace contract (handles subscriptions)
        marketplace = StrategyMarketplace(client)
        
        # Purchase subscription
        result = await marketplace.purchase_subscription(
            plan=request.plan,
            months=request.months
        )
        
        # Log transaction
        log_blockchain_tx(
            user_id=user['user_id'],
            tx_hash=result['tx_hash'],
            network=wallet['network'],
            tx_type='subscription',
            from_address=wallet['wallet_address'],
            to_address=marketplace.contract_address,
            amount=price_elcaro,
            token_symbol='ELCARO',
            data={'plan': request.plan, 'months': request.months}
        )
        
        return {
            'success': True,
            'tx_hash': result['tx_hash'],
            'price_elcaro': price_elcaro,
            'plan': request.plan,
            'months': request.months,
            'explorer_url': result['explorer_url']
        }
        
    except Exception as e:
        logger.error(f"Failed to purchase subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to purchase subscription")


# ==========================================
# TRANSACTION HISTORY
# ==========================================

@router.get("/transactions")
async def get_transaction_history(
    limit: int = 50,
    user: Dict = Depends(get_current_user)
):
    """Get user's blockchain transaction history"""
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    transactions = get_user_transactions(user['user_id'], limit=limit)
    
    return {
        'success': True,
        'transactions': transactions,
        'count': len(transactions)
    }


# ==========================================
# TOKEN INFO
# ==========================================

@router.get("/token/info")
async def get_token_info():
    """Get LYXEN token information"""
    if not WEB3_AVAILABLE:
        raise HTTPException(status_code=503, detail="Web3 not configured")
    
    try:
        client = Web3Client(network=NetworkType.POLYGON)
        token = ElcaroToken(client)
        
        info = await token.get_info()
        price = await TokenPriceOracle.get_price()
        
        return {
            'success': True,
            'name': info.name,
            'symbol': info.symbol,
            'decimals': info.decimals,
            'total_supply': info.total_supply,
            'contract_address': info.contract_address,
            'price_usd': price,
            'network': 'Polygon',
            'explorer_url': token.get_explorer_url()
        }
        
    except Exception as e:
        logger.error(f"Failed to get token info: {e}")
        # Return default info
        return {
            'success': True,
            'name': 'Lyxen Token',
            'symbol': 'ELCARO',
            'decimals': 18,
            'price_usd': 1.0,
            'network': 'Polygon',
            'message': 'Token not yet deployed'
        }


# ==========================================
# INITIALIZE WEB3 TABLES ON STARTUP
# ==========================================

@router.on_event("startup")
async def startup_event():
    """Initialize Web3 tables on app startup"""
    if WEB3_AVAILABLE:
        try:
            init_web3_tables()
            logger.info("Web3 tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Web3 tables: {e}")
