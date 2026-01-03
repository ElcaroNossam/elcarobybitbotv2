"""
Safe asyncio task management utilities.

Provides fire-and-forget task creation with proper exception handling
to prevent silent failures in background tasks.
"""

import asyncio
import logging
import functools
from typing import Any, Callable, Coroutine, Optional, Set, TypeVar

logger = logging.getLogger(__name__)

# Track all background tasks to prevent garbage collection
_background_tasks: Set[asyncio.Task] = set()

T = TypeVar('T')


def safe_create_task(
    coro: Coroutine[Any, Any, T],
    *,
    name: Optional[str] = None,
    log_exceptions: bool = True,
    on_error: Optional[Callable[[Exception], None]] = None
) -> asyncio.Task[T]:
    """
    Create an asyncio task with proper exception handling.
    
    Unlike asyncio.create_task(), this function:
    - Logs any unhandled exceptions
    - Prevents "Task exception was never retrieved" warnings
    - Keeps reference to task to prevent garbage collection
    - Optionally calls error callback on failure
    
    Args:
        coro: The coroutine to run
        name: Optional name for the task (for logging)
        log_exceptions: Whether to log exceptions (default True)
        on_error: Optional callback to call on exception
        
    Returns:
        The created Task object
        
    Example:
        # Instead of:
        asyncio.create_task(some_background_work())
        
        # Use:
        safe_create_task(some_background_work(), name="background_work")
    """
    task = asyncio.create_task(coro, name=name)
    
    # Keep reference to prevent GC
    _background_tasks.add(task)
    
    def _handle_task_result(task: asyncio.Task) -> None:
        # Remove from tracking set
        _background_tasks.discard(task)
        
        # Check for exception
        try:
            exc = task.exception()
        except asyncio.CancelledError:
            # Task was cancelled, not an error
            return
        
        if exc is not None:
            task_name = name or task.get_name()
            
            if log_exceptions:
                logger.exception(
                    f"Background task '{task_name}' failed with exception: {exc}",
                    exc_info=exc
                )
            
            if on_error:
                try:
                    on_error(exc)
                except Exception as callback_error:
                    logger.error(
                        f"Error callback for task '{task_name}' also failed: {callback_error}"
                    )
    
    task.add_done_callback(_handle_task_result)
    return task


def fire_and_forget(
    name: Optional[str] = None,
    log_exceptions: bool = True
) -> Callable[[Callable[..., Coroutine]], Callable[..., asyncio.Task]]:
    """
    Decorator to turn an async function into a fire-and-forget task launcher.
    
    Example:
        @fire_and_forget(name="notification")
        async def send_notification(user_id: int, message: str):
            await some_async_work()
            
        # Calling it creates a background task immediately
        send_notification(123, "Hello!")  # Returns Task, doesn't await
    """
    def decorator(func: Callable[..., Coroutine]) -> Callable[..., asyncio.Task]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> asyncio.Task:
            coro = func(*args, **kwargs)
            task_name = name or func.__name__
            return safe_create_task(coro, name=task_name, log_exceptions=log_exceptions)
        return wrapper
    return decorator


async def gather_with_exceptions(
    *coros: Coroutine,
    return_exceptions: bool = False,
    log_failures: bool = True
) -> list:
    """
    Like asyncio.gather but with proper exception logging.
    
    Args:
        *coros: Coroutines to run concurrently
        return_exceptions: If True, exceptions are returned as results
        log_failures: If True, log any exceptions that occur
        
    Returns:
        List of results (or exceptions if return_exceptions=True)
    """
    results = await asyncio.gather(*coros, return_exceptions=True)
    
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            if log_failures:
                logger.exception(f"Task {i} failed: {result}", exc_info=result)
            if not return_exceptions:
                raise result
        processed_results.append(result)
    
    return processed_results


def get_active_background_tasks() -> int:
    """Return count of currently tracked background tasks."""
    return len(_background_tasks)


def cancel_all_background_tasks() -> int:
    """
    Cancel all tracked background tasks.
    
    Returns:
        Number of tasks cancelled
    """
    count = 0
    for task in list(_background_tasks):
        if not task.done():
            task.cancel()
            count += 1
    return count


# Convenience alias
create_task_safe = safe_create_task
