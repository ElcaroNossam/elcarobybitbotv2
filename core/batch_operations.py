"""
Batch Operations Module for High-Performance Monitoring
========================================================
Optimized batch operations for monitoring positions across multiple users.

Best Practices Applied:
1. Batch database queries instead of N+1
2. Parallel API calls with semaphore limiting
3. Chunked processing to avoid memory issues
4. Error isolation - one user failure doesn't affect others
5. Context propagation for proper logging

Usage:
    from core.batch_operations import (
        batch_fetch_positions,
        batch_fetch_balances,
        parallel_process_users,
    )
    
    # Fetch all active positions in one query
    positions = await batch_fetch_positions(user_ids)
    
    # Process users in parallel with concurrency limit
    results = await parallel_process_users(
        user_ids=active_users,
        processor=process_user_positions,
        max_concurrent=10
    )
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import (
    Any, Callable, Dict, List, Optional, 
    TypeVar, Awaitable, Tuple, NamedTuple
)
from dataclasses import dataclass, field
from enum import Enum

from core.user_context import user_context, get_context_logger

logger = get_context_logger(__name__)

T = TypeVar('T')


# ═══════════════════════════════════════════════════════════════════════════════════
# BATCH RESULT TYPES
# ═══════════════════════════════════════════════════════════════════════════════════

class ResultStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class BatchResult:
    """Result of a batch operation for a single item"""
    user_id: int
    status: ResultStatus
    data: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    
    @property
    def is_success(self) -> bool:
        return self.status == ResultStatus.SUCCESS


@dataclass
class BatchSummary:
    """Summary of batch operation results"""
    total: int = 0
    success: int = 0
    errors: int = 0
    skipped: int = 0
    timeouts: int = 0
    total_duration_ms: float = 0.0
    results: List[BatchResult] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.success / self.total * 100
    
    @property
    def avg_duration_ms(self) -> float:
        if self.success == 0:
            return 0.0
        success_results = [r for r in self.results if r.is_success]
        return sum(r.duration_ms for r in success_results) / len(success_results)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "success": self.success,
            "errors": self.errors,
            "skipped": self.skipped,
            "timeouts": self.timeouts,
            "success_rate": round(self.success_rate, 1),
            "total_duration_ms": round(self.total_duration_ms, 1),
            "avg_duration_ms": round(self.avg_duration_ms, 1),
        }


# ═══════════════════════════════════════════════════════════════════════════════════
# BATCH DATABASE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════════

async def batch_fetch_positions(
    user_ids: List[int] = None,
    account_types: List[str] = None,
    exchange: str = None,
) -> Dict[int, List[Dict]]:
    """
    Fetch all active positions for multiple users in ONE query.
    
    Returns dict: {user_id: [positions]}
    
    Much faster than fetching positions for each user separately (N+1 problem).
    """
    from core.pool_manager import get_pool_manager
    
    pool = get_pool_manager()
    
    # Build query with optional filters
    conditions = ["1=1"]
    params = []
    param_idx = 1
    
    if user_ids:
        placeholders = ", ".join(f"${i}" for i in range(param_idx, param_idx + len(user_ids)))
        conditions.append(f"user_id IN ({placeholders})")
        params.extend(user_ids)
        param_idx += len(user_ids)
    
    if account_types:
        placeholders = ", ".join(f"${i}" for i in range(param_idx, param_idx + len(account_types)))
        conditions.append(f"account_type IN ({placeholders})")
        params.extend(account_types)
        param_idx += len(account_types)
    
    if exchange:
        conditions.append(f"exchange = ${param_idx}")
        params.append(exchange)
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT * FROM active_positions
        WHERE {where_clause}
        ORDER BY user_id, symbol
    """
    
    rows = await pool.async_fetch(query, *params)
    
    # Group by user_id
    result: Dict[int, List[Dict]] = {}
    for row in rows:
        uid = row['user_id']
        if uid not in result:
            result[uid] = []
        result[uid].append(row)
    
    return result


async def batch_fetch_user_settings(
    user_ids: List[int],
    strategy: str = None,
    exchange: str = None,
) -> Dict[int, Dict]:
    """
    Fetch strategy settings for multiple users in ONE query.
    
    Returns dict: {user_id: settings_dict}
    """
    from core.pool_manager import get_pool_manager
    
    pool = get_pool_manager()
    
    if not user_ids:
        return {}
    
    # Build query
    placeholders = ", ".join(f"${i+1}" for i in range(len(user_ids)))
    conditions = [f"user_id IN ({placeholders})"]
    params = list(user_ids)
    param_idx = len(user_ids) + 1
    
    if strategy:
        conditions.append(f"strategy = ${param_idx}")
        params.append(strategy)
        param_idx += 1
    
    if exchange:
        conditions.append(f"exchange = ${param_idx}")
        params.append(exchange)
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT * FROM user_strategy_settings
        WHERE {where_clause}
    """
    
    rows = await pool.async_fetch(query, *params)
    
    # Group by user_id
    result: Dict[int, Dict] = {}
    for row in rows:
        uid = row['user_id']
        if uid not in result:
            result[uid] = {}
        # Key by (strategy, exchange, account_type)
        key = f"{row.get('strategy', '')}:{row.get('exchange', '')}:{row.get('account_type', '')}"
        result[uid][key] = row
    
    return result


async def batch_fetch_active_users() -> List[Dict]:
    """
    Fetch all active trading users with their essential settings.
    
    Optimized query that fetches only what's needed for monitoring.
    """
    from core.pool_manager import get_pool_manager
    
    pool = get_pool_manager()
    
    query = """
        SELECT 
            user_id,
            trading_mode,
            exchange_type,
            demo_api_key IS NOT NULL as has_demo_key,
            real_api_key IS NOT NULL as has_real_key,
            hl_enabled,
            hl_testnet,
            hl_mainnet_private_key IS NOT NULL as has_hl_mainnet,
            hl_testnet_private_key IS NOT NULL as has_hl_testnet
        FROM users
        WHERE is_banned = 0
        AND is_allowed = 1
        AND (
            demo_api_key IS NOT NULL 
            OR real_api_key IS NOT NULL
            OR (hl_enabled = 1 AND (
                hl_mainnet_private_key IS NOT NULL 
                OR hl_testnet_private_key IS NOT NULL
            ))
        )
    """
    
    return await pool.async_fetch(query)


async def batch_update_positions(
    updates: List[Tuple[int, str, str, str, Dict[str, Any]]]
) -> int:
    """
    Batch update multiple positions with 4D multitenancy support.
    
    Args:
        updates: List of (user_id, symbol, account_type, exchange, fields_dict)
    
    Returns:
        Number of updated rows
    """
    from core.pool_manager import get_pool_manager
    
    if not updates:
        return 0
    
    pool = get_pool_manager()
    updated = 0
    
    # Process in transaction for atomicity
    async with pool.async_transaction() as conn:
        for user_id, symbol, account_type, exchange, fields in updates:
            # Build SET clause
            set_parts = []
            params = []
            param_idx = 1
            
            for field_name, value in fields.items():
                set_parts.append(f"{field_name} = ${param_idx}")
                params.append(value)
                param_idx += 1
            
            params.extend([user_id, symbol, account_type, exchange])
            
            query = f"""
                UPDATE active_positions
                SET {', '.join(set_parts)}
                WHERE user_id = ${param_idx} 
                AND symbol = ${param_idx + 1} 
                AND account_type = ${param_idx + 2}
                AND exchange = ${param_idx + 3}
            """
            
            result = await conn.execute(query, *params)
            if "UPDATE 1" in result:
                updated += 1
    
    return updated


# ═══════════════════════════════════════════════════════════════════════════════════
# PARALLEL USER PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════════

async def parallel_process_users(
    user_ids: List[int],
    processor: Callable[[int], Awaitable[Any]],
    max_concurrent: int = 10,
    timeout_per_user: float = 30.0,
    skip_on_error: bool = True,
) -> BatchSummary:
    """
    Process multiple users in parallel with proper error isolation.
    
    Features:
    - Semaphore-limited concurrency
    - Per-user timeout
    - Error isolation (one failure doesn't affect others)
    - Proper context propagation
    - Detailed result tracking
    
    Args:
        user_ids: List of user IDs to process
        processor: Async function that processes a single user
        max_concurrent: Maximum concurrent operations
        timeout_per_user: Timeout for each user in seconds
        skip_on_error: Continue processing other users on error
    
    Usage:
        async def sync_user_positions(user_id: int) -> dict:
            # ... sync logic
            return {"synced": 5}
        
        results = await parallel_process_users(
            user_ids=[1, 2, 3],
            processor=sync_user_positions,
            max_concurrent=5
        )
    """
    start_time = time.time()
    semaphore = asyncio.Semaphore(max_concurrent)
    summary = BatchSummary(total=len(user_ids))
    
    async def process_one(user_id: int) -> BatchResult:
        """Process single user with error handling"""
        async with semaphore:
            user_start = time.time()
            
            try:
                # Set user context for logging
                async with user_context(user_id=user_id):
                    # Apply timeout
                    result = await asyncio.wait_for(
                        processor(user_id),
                        timeout=timeout_per_user
                    )
                    
                    return BatchResult(
                        user_id=user_id,
                        status=ResultStatus.SUCCESS,
                        data=result,
                        duration_ms=(time.time() - user_start) * 1000
                    )
                    
            except asyncio.TimeoutError:
                logger.warning(f"User {user_id} processing timed out")
                return BatchResult(
                    user_id=user_id,
                    status=ResultStatus.TIMEOUT,
                    error=f"Timeout after {timeout_per_user}s",
                    duration_ms=(time.time() - user_start) * 1000
                )
                
            except Exception as e:
                logger.exception(f"Error processing user {user_id}: {e}")
                return BatchResult(
                    user_id=user_id,
                    status=ResultStatus.ERROR,
                    error=str(e),
                    duration_ms=(time.time() - user_start) * 1000
                )
    
    # Process all users in parallel
    tasks = [process_one(uid) for uid in user_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Aggregate results
    for result in results:
        if isinstance(result, Exception):
            # Shouldn't happen with our error handling, but just in case
            summary.errors += 1
            continue
            
        summary.results.append(result)
        
        if result.status == ResultStatus.SUCCESS:
            summary.success += 1
        elif result.status == ResultStatus.ERROR:
            summary.errors += 1
        elif result.status == ResultStatus.TIMEOUT:
            summary.timeouts += 1
        elif result.status == ResultStatus.SKIPPED:
            summary.skipped += 1
    
    summary.total_duration_ms = (time.time() - start_time) * 1000
    
    # Log summary
    logger.info(
        f"Batch processing complete: {summary.success}/{summary.total} success "
        f"({summary.errors} errors, {summary.timeouts} timeouts) "
        f"in {summary.total_duration_ms:.0f}ms"
    )
    
    return summary


async def parallel_fetch_exchange_data(
    user_ids: List[int],
    fetch_func: Callable[[int, str, str], Awaitable[Any]],
    account_configs: Dict[int, List[Tuple[str, str]]],  # {user_id: [(exchange, account_type), ...]}
    max_concurrent: int = 20,
    timeout: float = 10.0,
) -> Dict[Tuple[int, str, str], Any]:
    """
    Fetch exchange data (balance, positions, etc) for multiple user+account combos.
    
    Optimized for the case where users may have multiple accounts (demo/real, bybit/hl).
    
    Args:
        user_ids: User IDs to fetch for
        fetch_func: Async function(user_id, exchange, account_type) -> data
        account_configs: Dict mapping user_id to list of (exchange, account_type)
        max_concurrent: Max concurrent API calls
        timeout: Per-call timeout
    
    Returns:
        Dict mapping (user_id, exchange, account_type) to fetched data
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    results: Dict[Tuple[int, str, str], Any] = {}
    
    async def fetch_one(user_id: int, exchange: str, account_type: str):
        async with semaphore:
            try:
                async with user_context(
                    user_id=user_id, 
                    exchange=exchange, 
                    account_type=account_type
                ):
                    data = await asyncio.wait_for(
                        fetch_func(user_id, exchange, account_type),
                        timeout=timeout
                    )
                    return (user_id, exchange, account_type), data
                    
            except asyncio.TimeoutError:
                logger.warning(
                    f"Timeout fetching data for user={user_id} "
                    f"{exchange}/{account_type}"
                )
                return (user_id, exchange, account_type), None
                
            except Exception as e:
                logger.error(
                    f"Error fetching data for user={user_id} "
                    f"{exchange}/{account_type}: {e}"
                )
                return (user_id, exchange, account_type), None
    
    # Build task list
    tasks = []
    for user_id in user_ids:
        configs = account_configs.get(user_id, [])
        for exchange, account_type in configs:
            tasks.append(fetch_one(user_id, exchange, account_type))
    
    # Execute all
    task_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Collect results
    for result in task_results:
        if isinstance(result, tuple) and len(result) == 2:
            key, data = result
            if data is not None:
                results[key] = data
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════════
# CHUNKED PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════════

async def chunked_process(
    items: List[T],
    processor: Callable[[List[T]], Awaitable[Any]],
    chunk_size: int = 100,
    delay_between_chunks: float = 0.1,
) -> List[Any]:
    """
    Process items in chunks with delay between batches.
    
    Useful for:
    - Avoiding rate limits
    - Memory management with large datasets
    - Giving other tasks a chance to run
    
    Usage:
        results = await chunked_process(
            items=all_users,
            processor=batch_sync_positions,
            chunk_size=50,
            delay_between_chunks=0.5
        )
    """
    results = []
    
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        
        logger.debug(f"Processing chunk {i//chunk_size + 1}, items {i}-{i+len(chunk)}")
        
        result = await processor(chunk)
        results.append(result)
        
        # Small delay between chunks
        if i + chunk_size < len(items):
            await asyncio.sleep(delay_between_chunks)
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════════
# MONITORING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class MonitoringCycleStats:
    """Statistics for a single monitoring cycle"""
    cycle_id: int
    start_time: float
    end_time: float = 0.0
    users_checked: int = 0
    positions_checked: int = 0
    positions_closed: int = 0
    errors: int = 0
    
    @property
    def duration_ms(self) -> float:
        if self.end_time == 0:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000
    
    def complete(self):
        self.end_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "duration_ms": round(self.duration_ms, 1),
            "users_checked": self.users_checked,
            "positions_checked": self.positions_checked,
            "positions_closed": self.positions_closed,
            "errors": self.errors,
        }


class MonitoringStats:
    """Aggregated monitoring statistics"""
    
    def __init__(self, max_history: int = 100):
        self._history: List[MonitoringCycleStats] = []
        self._max_history = max_history
        self._cycle_counter = 0
    
    def start_cycle(self) -> MonitoringCycleStats:
        """Start a new monitoring cycle"""
        self._cycle_counter += 1
        stats = MonitoringCycleStats(
            cycle_id=self._cycle_counter,
            start_time=time.time()
        )
        return stats
    
    def complete_cycle(self, stats: MonitoringCycleStats):
        """Complete and record a monitoring cycle"""
        stats.complete()
        
        self._history.append(stats)
        
        # Trim history
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        logger.info(
            f"Monitoring cycle #{stats.cycle_id} complete: "
            f"{stats.users_checked} users, {stats.positions_checked} positions "
            f"({stats.positions_closed} closed, {stats.errors} errors) "
            f"in {stats.duration_ms:.0f}ms"
        )
    
    @property
    def avg_cycle_time_ms(self) -> float:
        if not self._history:
            return 0.0
        return sum(s.duration_ms for s in self._history) / len(self._history)
    
    @property
    def total_cycles(self) -> int:
        return self._cycle_counter
    
    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary"""
        recent = self._history[-10:] if self._history else []
        
        return {
            "total_cycles": self._cycle_counter,
            "avg_cycle_time_ms": round(self.avg_cycle_time_ms, 1),
            "recent_cycles": [s.to_dict() for s in recent],
        }


# Global monitoring stats instance
monitoring_stats = MonitoringStats()
