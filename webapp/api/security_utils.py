"""
Security utilities for safe error handling and logging.
SECURITY: Never expose internal error details to users!
"""
import logging
import uuid
from fastapi import HTTPException
from typing import Optional

logger = logging.getLogger(__name__)

# Generic error messages for users
GENERIC_ERRORS = {
    400: "Invalid request. Please check your input.",
    401: "Authentication required.",
    403: "Access denied.",
    404: "Resource not found.",
    422: "Invalid data format.",
    429: "Too many requests. Please try again later.",
    500: "Internal server error. Please try again later.",
    502: "Service temporarily unavailable.",
    503: "Service maintenance in progress.",
}


def safe_exception(
    status_code: int,
    e: Exception,
    context: Optional[str] = None,
    user_message: Optional[str] = None
) -> HTTPException:
    """
    Create a safe HTTPException that logs full details but shows generic message to user.
    
    Args:
        status_code: HTTP status code
        e: The original exception
        context: Optional context string for logging (e.g., "close_position", "get_balance")
        user_message: Optional custom user-facing message
    
    Returns:
        HTTPException with safe message for user
    
    Example:
        try:
            do_something()
        except Exception as e:
            raise safe_exception(500, e, context="close_position")
    """
    # Generate unique error ID for tracking
    error_id = str(uuid.uuid4())[:8]
    
    # Log full details for debugging
    log_msg = f"[{error_id}] Error"
    if context:
        log_msg += f" in {context}"
    log_msg += f": {type(e).__name__}: {str(e)}"
    
    logger.exception(log_msg)
    
    # Return safe message to user
    if user_message:
        detail = f"{user_message} (Error ID: {error_id})"
    else:
        generic = GENERIC_ERRORS.get(status_code, GENERIC_ERRORS[500])
        detail = f"{generic} (Error ID: {error_id})"
    
    return HTTPException(status_code=status_code, detail=detail)


def safe_error_response(
    e: Exception,
    context: Optional[str] = None,
    user_message: str = "An error occurred. Please try again."
) -> dict:
    """
    Create a safe error response dict for JSON responses.
    
    Args:
        e: The original exception
        context: Optional context for logging
        user_message: Message to show to user
    
    Returns:
        Dict with success=False and safe error message
    """
    error_id = str(uuid.uuid4())[:8]
    
    log_msg = f"[{error_id}] Error"
    if context:
        log_msg += f" in {context}"
    log_msg += f": {type(e).__name__}: {str(e)}"
    
    logger.exception(log_msg)
    
    return {
        "success": False,
        "error": f"{user_message} (Error ID: {error_id})"
    }


# Sanitize user input for display
def sanitize_for_log(s: str, max_length: int = 200) -> str:
    """Sanitize a string for safe logging (remove newlines, truncate)."""
    if not isinstance(s, str):
        s = str(s)
    # Remove newlines and control characters
    s = s.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # Truncate if too long
    if len(s) > max_length:
        s = s[:max_length] + "..."
    return s
