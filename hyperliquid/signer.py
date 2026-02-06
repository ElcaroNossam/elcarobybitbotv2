"""
HyperLiquid EIP-712 Signing Utilities
Based on official hyperliquid-python-sdk
"""
import time
import msgpack
from typing import Dict, Any, Optional, List

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import keccak, to_hex

from .constants import COIN_TO_ASSET, get_size_decimals


# Domains are no longer used directly - we use l1_payload() instead
PHANTOM_DOMAIN = {
    "name": "Exchange",
    "version": "1",
    "chainId": 1337,
    "verifyingContract": "0x0000000000000000000000000000000000000000",
}

MAINNET_DOMAIN = {
    "name": "Exchange",
    "version": "1",
    "chainId": 42161,
    "verifyingContract": "0x0000000000000000000000000000000000000000",
}


def get_timestamp_ms() -> int:
    return int(time.time() * 1000)


def float_to_wire(x: float, decimals: int = 8) -> str:
    rounded = round(x, decimals)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.{decimals}f}".rstrip('0').rstrip('.')


def float_to_int_for_hashing(x: float) -> int:
    return round(x * 1e8)


def order_type_to_wire(order_type: Dict[str, Any]) -> Dict[str, Any]:
    if "limit" in order_type:
        return {"limit": {"tif": order_type["limit"].get("tif", "Gtc")}}
    elif "trigger" in order_type:
        trigger = order_type["trigger"]
        return {
            "trigger": {
                "isMarket": trigger.get("isMarket", True),
                "triggerPx": float_to_wire(trigger["triggerPx"]),
                "tpsl": trigger.get("tpsl", "sl")
            }
        }
    return {"limit": {"tif": "Gtc"}}


def order_request_to_order_wire(order: Dict[str, Any], asset: int) -> Dict[str, Any]:
    coin = order.get("coin", "")
    sz_decimals = get_size_decimals(coin)
    
    wire = {
        "a": asset,
        "b": order["is_buy"],
        "p": float_to_wire(order["limit_px"]),
        "s": float_to_wire(order["sz"], sz_decimals),
        "r": order.get("reduce_only", False),
        "t": order_type_to_wire(order.get("order_type", {"limit": {"tif": "Gtc"}}))
    }
    
    if order.get("cloid"):
        wire["c"] = order["cloid"]
    
    return wire


def order_wire_to_action(orders: List[Dict[str, Any]], grouping: str = "na", builder: Optional[Dict] = None) -> Dict[str, Any]:
    action = {"type": "order", "orders": orders, "grouping": grouping}
    if builder:
        action["builder"] = builder
    return action


def cancel_wire_to_action(cancels: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"type": "cancel", "cancels": cancels}


def address_to_bytes(address: str) -> bytes:
    """Convert address string to bytes."""
    return bytes.fromhex(address[2:] if address.startswith("0x") else address)


def action_hash(action: Dict[str, Any], vault_address: Optional[str], nonce: int, expires_after: Optional[int] = None) -> bytes:
    """
    Create action hash for signing.
    This matches the official SDK implementation.
    """
    data = msgpack.packb(action)
    data += nonce.to_bytes(8, "big")
    
    if vault_address is None:
        data += b"\x00"
    else:
        data += b"\x01"
        data += address_to_bytes(vault_address)
    
    if expires_after is not None:
        data += b"\x00"
        data += expires_after.to_bytes(8, "big")
    
    return keccak(data)


def construct_phantom_agent(hash_bytes: bytes, is_mainnet: bool) -> Dict[str, Any]:
    """Construct phantom agent for L1 signing."""
    return {
        "source": "a" if is_mainnet else "b",
        "connectionId": hash_bytes
    }


def l1_payload(phantom_agent: Dict[str, Any]) -> Dict[str, Any]:
    """Create EIP-712 payload for L1 action. Uses chainId 1337 always."""
    return {
        "domain": {
            "chainId": 1337,
            "name": "Exchange",
            "verifyingContract": "0x0000000000000000000000000000000000000000",
            "version": "1",
        },
        "types": {
            "Agent": [
                {"name": "source", "type": "string"},
                {"name": "connectionId", "type": "bytes32"},
            ],
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
        },
        "primaryType": "Agent",
        "message": phantom_agent,
    }


def sign_inner(wallet: Account, data: Dict[str, Any]) -> Dict[str, Any]:
    """Sign EIP-712 typed data and return signature."""
    structured_data = encode_typed_data(full_message=data)
    signed = wallet.sign_message(structured_data)
    return {
        "r": to_hex(signed["r"]),
        "s": to_hex(signed["s"]),
        "v": signed["v"]
    }


def sign_l1_action(
    private_key: str,
    action: Dict[str, Any],
    vault_address: Optional[str] = None,
    nonce: int = None,
    expires_after: Optional[int] = None,
    is_mainnet: bool = True
) -> Dict[str, Any]:
    """
    Sign L1 action and return full payload ready for /exchange endpoint.
    Based on official hyperliquid-python-sdk implementation.
    """
    if nonce is None:
        nonce = get_timestamp_ms()
    
    # Create wallet from private key
    wallet = Account.from_key(private_key)
    
    # Create action hash (using keccak as in official SDK)
    hash_bytes = action_hash(action, vault_address, nonce, expires_after)
    
    # Create phantom agent
    phantom_agent = construct_phantom_agent(hash_bytes, is_mainnet)
    
    # Create L1 payload
    data = l1_payload(phantom_agent)
    
    # Sign
    signature = sign_inner(wallet, data)
    
    # Build final payload
    payload = {
        "action": action,
        "nonce": nonce,
        "signature": signature
    }
    
    if vault_address:
        payload["vaultAddress"] = vault_address
    
    return payload


def sign_update_leverage_action(
    private_key: str,
    asset: int,
    is_cross: bool,
    leverage: int,
    nonce: int = None,
    is_mainnet: bool = True
) -> Dict[str, Any]:
    action = {"type": "updateLeverage", "asset": asset, "isCross": is_cross, "leverage": leverage}
    return sign_l1_action(private_key, action, nonce=nonce, is_mainnet=is_mainnet)


def sign_usd_transfer_action(
    private_key: str,
    amount: float,
    destination: str,
    nonce: int = None,
    is_mainnet: bool = True
) -> Dict[str, Any]:
    action = {
        "type": "usdTransfer",
        "signatureChainId": "0xa4b1" if is_mainnet else "0x66eee",
        "destination": destination,
        "amount": str(amount),
    }
    return sign_l1_action(private_key, action, nonce=nonce, is_mainnet=is_mainnet)


def sign_withdraw_action(
    private_key: str,
    amount: float,
    destination: str,
    nonce: int = None,
    is_mainnet: bool = True
) -> Dict[str, Any]:
    action = {
        "type": "withdraw3",
        "signatureChainId": "0xa4b1" if is_mainnet else "0x66eee",
        "destination": destination,
        "amount": str(amount),
    }
    return sign_l1_action(private_key, action, nonce=nonce, is_mainnet=is_mainnet)


def get_address_from_private_key(private_key: str) -> str:
    account = Account.from_key(private_key)
    return account.address
