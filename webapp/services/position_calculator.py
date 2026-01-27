"""
Enliko Position Size Calculator
Calculates position size based on stop loss and risk percentage
EXACTLY like in bot.py - same formulas
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
import math


@dataclass
class PositionCalculation:
    """Position size calculation result"""
    symbol: str
    side: str
    entry_price: float
    stop_loss_price: float
    stop_loss_percent: float
    risk_amount_usd: float
    risk_percent: float
    position_size: float  # In base currency (BTC, ETH, etc.)
    position_value_usd: float
    leverage: int
    margin_required: float
    take_profit_price: Optional[float] = None
    take_profit_percent: Optional[float] = None
    potential_profit_usd: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "entry_price": self.entry_price,
            "stop_loss_price": self.stop_loss_price,
            "stop_loss_percent": self.stop_loss_percent,
            "risk_amount_usd": self.risk_amount_usd,
            "risk_percent": self.risk_percent,
            "position_size": self.position_size,
            "position_value_usd": self.position_value_usd,
            "leverage": self.leverage,
            "margin_required": self.margin_required,
            "take_profit_price": self.take_profit_price,
            "take_profit_percent": self.take_profit_percent,
            "potential_profit_usd": self.potential_profit_usd,
            "risk_reward_ratio": self.risk_reward_ratio
        }


class PositionSizeCalculator:
    """Calculate position size exactly like bot.py does"""
    
    @staticmethod
    def calculate(
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        risk_percent: float,
        leverage: int = 10,
        side: str = "Buy",
        symbol: str = "BTCUSDT",
        take_profit_price: Optional[float] = None
    ) -> PositionCalculation:
        """
        Calculate position size based on risk parameters
        
        Formula from bot.py:
        1. Calculate stop loss distance in % = abs((entry - stop) / entry) * 100
        2. Calculate risk amount in USD = account_balance * (risk_percent / 100)
        3. Calculate position size = risk_amount / (entry_price * (stop_loss_percent / 100))
        4. Position value = position_size * entry_price
        5. Margin required = position_value / leverage
        
        Args:
            account_balance: Account balance in USDT
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_percent: Risk per trade as percentage of balance (e.g., 1.0 for 1%)
            leverage: Leverage multiplier
            side: "Buy" or "Sell"
            symbol: Trading symbol
            take_profit_price: Optional take profit price
        
        Returns:
            PositionCalculation with all calculated values
        """
        # Validate inputs
        if account_balance <= 0:
            raise ValueError("Account balance must be positive")
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")
        if stop_loss_price <= 0:
            raise ValueError("Stop loss price must be positive")
        if risk_percent <= 0 or risk_percent > 100:
            raise ValueError("Risk percent must be between 0 and 100")
        if leverage < 1 or leverage > 125:
            raise ValueError("Leverage must be between 1 and 125")
        
        # Validate stop loss position
        if side.lower() in ["buy", "long"]:
            if stop_loss_price >= entry_price:
                raise ValueError("Stop loss must be below entry price for LONG positions")
        else:
            if stop_loss_price <= entry_price:
                raise ValueError("Stop loss must be above entry price for SHORT positions")
        
        # Calculate stop loss distance in %
        stop_distance = abs(entry_price - stop_loss_price)
        stop_loss_percent = (stop_distance / entry_price) * 100
        
        # Calculate risk amount in USD
        risk_amount_usd = account_balance * (risk_percent / 100)
        
        # Calculate position size using the formula:
        # position_size = risk_amount / (entry_price * (stop_loss_percent / 100))
        # This gives us the size in base currency (BTC, ETH, etc.)
        position_size = risk_amount_usd / (entry_price * (stop_loss_percent / 100))
        
        # Calculate position value in USD
        position_value_usd = position_size * entry_price
        
        # Calculate required margin
        margin_required = position_value_usd / leverage
        
        # Validate margin requirement
        if margin_required > account_balance:
            raise ValueError(f"Insufficient balance. Required margin: ${margin_required:.2f}, Available: ${account_balance:.2f}")
        
        # Calculate take profit metrics if provided
        take_profit_percent = None
        potential_profit_usd = None
        risk_reward_ratio = None
        
        if take_profit_price:
            # Validate TP position
            if side.lower() in ["buy", "long"]:
                if take_profit_price <= entry_price:
                    raise ValueError("Take profit must be above entry price for LONG positions")
            else:
                if take_profit_price >= entry_price:
                    raise ValueError("Take profit must be below entry price for SHORT positions")
            
            # Calculate TP distance in %
            tp_distance = abs(take_profit_price - entry_price)
            take_profit_percent = (tp_distance / entry_price) * 100
            
            # Calculate potential profit
            if side.lower() in ["buy", "long"]:
                potential_profit_usd = position_size * (take_profit_price - entry_price)
            else:
                potential_profit_usd = position_size * (entry_price - take_profit_price)
            
            # Calculate risk/reward ratio
            risk_reward_ratio = potential_profit_usd / risk_amount_usd
        
        return PositionCalculation(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            stop_loss_percent=stop_loss_percent,
            risk_amount_usd=risk_amount_usd,
            risk_percent=risk_percent,
            position_size=position_size,
            position_value_usd=position_value_usd,
            leverage=leverage,
            margin_required=margin_required,
            take_profit_price=take_profit_price,
            take_profit_percent=take_profit_percent,
            potential_profit_usd=potential_profit_usd,
            risk_reward_ratio=risk_reward_ratio
        )
    
    @staticmethod
    def calculate_from_percent(
        account_balance: float,
        entry_price: float,
        stop_loss_percent: float,
        risk_percent: float,
        leverage: int = 10,
        side: str = "Buy",
        symbol: str = "BTCUSDT",
        take_profit_percent: Optional[float] = None
    ) -> PositionCalculation:
        """
        Calculate position size using percentage-based stop loss
        
        Args:
            stop_loss_percent: Stop loss distance in percent (e.g., 2.0 for 2%)
            take_profit_percent: Take profit distance in percent
        """
        # Calculate stop loss price from percentage
        if side.lower() in ["buy", "long"]:
            stop_loss_price = entry_price * (1 - stop_loss_percent / 100)
            take_profit_price = entry_price * (1 + take_profit_percent / 100) if take_profit_percent else None
        else:
            stop_loss_price = entry_price * (1 + stop_loss_percent / 100)
            take_profit_price = entry_price * (1 - take_profit_percent / 100) if take_profit_percent else None
        
        return PositionSizeCalculator.calculate(
            account_balance=account_balance,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            risk_percent=risk_percent,
            leverage=leverage,
            side=side,
            symbol=symbol,
            take_profit_price=take_profit_price
        )
    
    @staticmethod
    def calculate_quick(
        balance: float,
        price: float,
        sl_percent: float = 2.0,
        risk_percent: float = 1.0,
        leverage: int = 10,
        side: str = "Buy"
    ) -> float:
        """
        Quick calculation returning only position size
        
        Returns:
            Position size in base currency
        """
        try:
            result = PositionSizeCalculator.calculate_from_percent(
                account_balance=balance,
                entry_price=price,
                stop_loss_percent=sl_percent,
                risk_percent=risk_percent,
                leverage=leverage,
                side=side
            )
            return result.position_size
        except Exception:
            return 0.0
    
    @staticmethod
    def validate_order(
        calculation: PositionCalculation,
        min_order_size: float,
        max_order_size: float,
        tick_size: float
    ) -> Dict[str, Any]:
        """
        Validate order against exchange limits and round to proper precision
        
        Returns:
            Dict with 'valid', 'adjusted_size', 'errors' keys
        """
        errors = []
        adjusted_size = calculation.position_size
        
        # Round to tick size
        adjusted_size = math.floor(adjusted_size / tick_size) * tick_size
        
        # Check minimum
        if adjusted_size < min_order_size:
            errors.append(f"Position size {adjusted_size:.8f} is below minimum {min_order_size:.8f}")
            adjusted_size = min_order_size
        
        # Check maximum
        if adjusted_size > max_order_size:
            errors.append(f"Position size {adjusted_size:.8f} exceeds maximum {max_order_size:.8f}")
            adjusted_size = max_order_size
        
        return {
            "valid": len(errors) == 0,
            "adjusted_size": adjusted_size,
            "errors": errors,
            "needs_adjustment": adjusted_size != calculation.position_size
        }


# Global instance
position_calculator = PositionSizeCalculator()
