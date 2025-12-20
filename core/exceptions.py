"""
Custom exceptions for Bybit Demo Trading Bot
"""


class BotException(Exception):
    """Base exception for all bot errors"""
    
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or "BOT_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details
        }


class ExchangeError(BotException):
    """Base exception for exchange-related errors"""
    
    def __init__(self, message: str, exchange: str = None, **kwargs):
        self.exchange = exchange
        super().__init__(message, code="EXCHANGE_ERROR", **kwargs)
        self.details["exchange"] = exchange


class AuthenticationError(ExchangeError):
    """Raised when API authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, **kwargs)
        self.code = "AUTH_ERROR"


class RateLimitError(ExchangeError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)
        self.code = "RATE_LIMIT"
        self.details["retry_after"] = retry_after


class InsufficientBalanceError(ExchangeError):
    """Raised when account balance is insufficient"""
    
    def __init__(self, required: float = None, available: float = None, **kwargs):
        message = "Insufficient balance"
        if required and available:
            message = f"Insufficient balance: required {required}, available {available}"
        self.required = required
        self.available = available
        super().__init__(message, **kwargs)
        self.code = "INSUFFICIENT_BALANCE"
        self.details.update({"required": required, "available": available})


class PositionNotFoundError(ExchangeError):
    """Raised when position is not found"""
    
    def __init__(self, symbol: str = None, **kwargs):
        message = f"Position not found: {symbol}" if symbol else "Position not found"
        self.symbol = symbol
        super().__init__(message, **kwargs)
        self.code = "POSITION_NOT_FOUND"
        self.details["symbol"] = symbol


class OrderError(ExchangeError):
    """Raised when order operation fails"""
    
    def __init__(self, message: str, order_id: str = None, **kwargs):
        self.order_id = order_id
        super().__init__(message, **kwargs)
        self.code = "ORDER_ERROR"
        self.details["order_id"] = order_id


class LicenseError(BotException):
    """Raised when license validation fails"""
    
    def __init__(self, message: str = "License required", license_type: str = None, **kwargs):
        self.license_type = license_type
        super().__init__(message, code="LICENSE_ERROR", **kwargs)
        self.details["required_license"] = license_type


class ConfigurationError(BotException):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        self.config_key = config_key
        super().__init__(message, code="CONFIG_ERROR", **kwargs)
        self.details["config_key"] = config_key


class DatabaseError(BotException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str, operation: str = None, **kwargs):
        self.operation = operation
        super().__init__(message, code="DB_ERROR", **kwargs)
        self.details["operation"] = operation


class SignalParseError(BotException):
    """Raised when signal parsing fails"""
    
    def __init__(self, message: str, raw_signal: str = None, **kwargs):
        self.raw_signal = raw_signal
        super().__init__(message, code="SIGNAL_PARSE_ERROR", **kwargs)
        if raw_signal:
            self.details["raw_signal"] = raw_signal[:200]


class PremiumRequiredError(LicenseError):
    """Raised when premium license is required for a feature"""
    
    def __init__(self, feature: str = None, **kwargs):
        message = f"Premium license required for: {feature}" if feature else "Premium license required"
        self.feature = feature
        super().__init__(message, license_type="premium", **kwargs)
        self.code = "PREMIUM_REQUIRED"
        self.details["feature"] = feature


class ExchangeNotConnectedError(ExchangeError):
    """Raised when exchange is not connected"""
    
    def __init__(self, exchange: str = None, **kwargs):
        message = f"Exchange not connected: {exchange}" if exchange else "Exchange not connected"
        super().__init__(message, exchange=exchange, **kwargs)
        self.code = "EXCHANGE_NOT_CONNECTED"


class InvalidSymbolError(ExchangeError):
    """Raised when symbol is invalid or not supported"""
    
    def __init__(self, symbol: str = None, **kwargs):
        message = f"Invalid or unsupported symbol: {symbol}" if symbol else "Invalid symbol"
        self.symbol = symbol
        super().__init__(message, **kwargs)
        self.code = "INVALID_SYMBOL"
        self.details["symbol"] = symbol


class MaintenanceError(ExchangeError):
    """Raised when exchange is under maintenance"""
    
    def __init__(self, exchange: str = None, **kwargs):
        message = f"Exchange under maintenance: {exchange}" if exchange else "Exchange under maintenance"
        super().__init__(message, exchange=exchange, **kwargs)
        self.code = "MAINTENANCE"
