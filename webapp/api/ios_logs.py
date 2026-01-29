"""
iOS Logs API
Receives and stores logs from iOS app for monitoring and debugging
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime

router = APIRouter(prefix="/logs", tags=["iOS Logs"])
logger = logging.getLogger("ios_logs")

# Store recent logs in memory (last 1000)
_ios_logs: List[dict] = []
MAX_LOGS = 1000


class LogEntry(BaseModel):
    level: str
    category: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    timestamp: Optional[str] = None


class IOSLogsRequest(BaseModel):
    logs: List[LogEntry]
    device: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None


@router.post("/ios")
async def receive_ios_logs(request: Request, body: IOSLogsRequest):
    """
    Receive logs from iOS app for monitoring
    """
    global _ios_logs
    
    client_ip = request.client.host if request.client else "unknown"
    
    for log in body.logs:
        log_entry = {
            "level": log.level,
            "category": log.category,
            "message": log.message,
            "file": log.file,
            "line": log.line,
            "timestamp": log.timestamp or datetime.utcnow().isoformat(),
            "device": body.device,
            "os_version": body.os_version,
            "app_version": body.app_version,
            "client_ip": client_ip,
            "received_at": datetime.utcnow().isoformat()
        }
        
        _ios_logs.append(log_entry)
        
        # Log to server console for real-time monitoring
        log_level = log.level.upper()
        if "ERROR" in log_level or "CRITICAL" in log_level:
            logger.error(f"📱 iOS [{body.device}] [{log.category}] {log.message}")
        elif "WARNING" in log_level:
            logger.warning(f"📱 iOS [{body.device}] [{log.category}] {log.message}")
        else:
            logger.info(f"📱 iOS [{body.device}] [{log.category}] {log.message}")
    
    # Trim old logs
    if len(_ios_logs) > MAX_LOGS:
        _ios_logs = _ios_logs[-MAX_LOGS:]
    
    return {"success": True, "received": len(body.logs)}


@router.get("/ios")
async def get_ios_logs(
    limit: int = 100,
    level: Optional[str] = None,
    category: Optional[str] = None,
    device: Optional[str] = None
):
    """
    Get recent iOS logs (for admin monitoring)
    """
    logs = _ios_logs.copy()
    
    # Filter by level
    if level:
        logs = [l for l in logs if level.upper() in l.get("level", "").upper()]
    
    # Filter by category
    if category:
        logs = [l for l in logs if category.lower() in l.get("category", "").lower()]
    
    # Filter by device
    if device:
        logs = [l for l in logs if device.lower() in (l.get("device") or "").lower()]
    
    # Return most recent
    return {
        "logs": logs[-limit:],
        "total": len(logs),
        "all_total": len(_ios_logs)
    }


@router.delete("/ios")
async def clear_ios_logs():
    """
    Clear all stored iOS logs
    """
    global _ios_logs
    count = len(_ios_logs)
    _ios_logs = []
    return {"success": True, "cleared": count}
