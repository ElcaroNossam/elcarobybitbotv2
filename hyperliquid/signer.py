"""
HyperLiquid EIP-712 Signing Utilities
"""
import time
import hashlib
import msgpack
from typing import Dict, Any, Optional, List

from eth_account import Account
from eth_account.messages import encode_typed_data

from .constants import COIN_TO_ASSET, get_size_decimals


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


def sign_l1_action(
    private_key: str,
    action: Dict[str, Any],
    vault_address: Optional[str] = None,
    nonce: int = None,
    is_mainnet: bool = True
) -> Dict[str, Any]:
    if nonce is None:
        nonce = get_timestamp_ms()
    
    action_bytes = msgpack.packb(action)
    account = Account.from_key(private_key)
    source = "a" if is_mainnet else "b"
    connection_id = hashlib.sha256(action_bytes + nonce.to_bytes(8, 'big')).digest()
    
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Agent": [
                {"name": "source", "type": "string"},
                {"name": "connectionId", "type": "bytes32"},
            ],
        },
        "primaryType": "Agent",
        "domain": MAINNET_DOMAIN if is_mainnet else PHANTOM_DOMAIN,
        "message": {"source": source, "connectionId": connection_id},
    }
    
    signable = encode_typed_data(full_message=typed_data)
    signed = account.sign_message(signable)
    
    signature = {"r": hex(signed.r), "s": hex(signed.s), "v": signed.v}
    payload = {"action": action, "nonce": nonce, "signature": signature}
    
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
