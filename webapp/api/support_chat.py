"""
Support Chat API
================
REST API for in-app support chat between users and admin.
Supports: text messages, FAQ quick answers, chat management.

Endpoints:
- POST /support/chat          - Create or get active chat
- GET  /support/chat          - Get user's active chat with messages
- POST /support/chat/message  - Send a message
- GET  /support/faq           - Get FAQ by language & category
- POST /support/chat/rate     - Rate resolved chat
- POST /support/chat/close    - Close chat

Admin endpoints:
- GET  /support/admin/chats         - List all active chats
- GET  /support/admin/chat/{id}     - Get specific chat
- POST /support/admin/chat/{id}/reply - Admin reply
- POST /support/admin/chat/{id}/resolve - Resolve chat
"""

import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from webapp.api.auth import get_current_user
from core.db_postgres import execute, execute_one, get_conn
from coin_params import ADMIN_ID

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/support", tags=["support"])


# ============================================================================
# Models
# ============================================================================

class CreateChatRequest(BaseModel):
    subject: Optional[str] = None
    language: str = "en"

class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)

class RateChatRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)

class AdminReplyRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    id: int
    status: str
    subject: Optional[str]
    language: str
    created_at: str
    updated_at: str
    messages: list = []
    unread_count: int = 0

class MessageResponse(BaseModel):
    id: int
    sender_type: str
    message: str
    message_type: str
    is_read: bool
    created_at: str

class FAQResponse(BaseModel):
    id: int
    category: str
    question: str
    answer: str


# ============================================================================
# User Endpoints
# ============================================================================

@router.post("/chat")
async def create_or_get_chat(req: CreateChatRequest, user: dict = Depends(get_current_user)):
    """Create a new support chat or return existing open one."""
    uid = user["user_id"]
    
    # Check for existing open/waiting chat
    existing = execute_one(
        "SELECT * FROM support_chats WHERE user_id = %s AND status IN ('open', 'waiting') ORDER BY created_at DESC LIMIT 1",
        (uid,)
    )
    
    if existing:
        messages = _get_chat_messages(existing["id"])
        return {
            "chat": _format_chat(existing),
            "messages": messages,
            "is_new": False
        }
    
    # Create new chat
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO support_chats (user_id, subject, language, status)
               VALUES (%s, %s, %s, 'open')
               RETURNING id, user_id, status, subject, language, created_at, updated_at""",
            (uid, req.subject, req.language)
        )
        chat = cur.fetchone()
        conn.commit()
    
    if not chat:
        raise HTTPException(500, "Failed to create chat")
    
    # Add welcome system message
    _add_system_message(chat["id"], f"Welcome to Enliko Support! An admin will respond shortly.")
    
    messages = _get_chat_messages(chat["id"])
    return {
        "chat": _format_chat(chat),
        "messages": messages,
        "is_new": True
    }


@router.get("/chat")
async def get_active_chat(user: dict = Depends(get_current_user)):
    """Get user's active chat with all messages."""
    uid = user["user_id"]
    
    chat = execute_one(
        "SELECT * FROM support_chats WHERE user_id = %s AND status IN ('open', 'waiting') ORDER BY updated_at DESC LIMIT 1",
        (uid,)
    )
    
    if not chat:
        return {"chat": None, "messages": []}
    
    # Mark admin messages as read
    execute(
        "UPDATE support_messages SET is_read = TRUE WHERE chat_id = %s AND sender_type = 'admin' AND is_read = FALSE",
        (chat["id"],)
    )
    
    messages = _get_chat_messages(chat["id"])
    return {
        "chat": _format_chat(chat),
        "messages": messages
    }


@router.post("/chat/message")
async def send_message(req: SendMessageRequest, user: dict = Depends(get_current_user)):
    """Send a message in user's active chat."""
    uid = user["user_id"]
    
    chat = execute_one(
        "SELECT * FROM support_chats WHERE user_id = %s AND status IN ('open', 'waiting') ORDER BY updated_at DESC LIMIT 1",
        (uid,)
    )
    
    if not chat:
        raise HTTPException(404, "No active chat. Create one first.")
    
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO support_messages (chat_id, sender_id, sender_type, message, message_type)
               VALUES (%s, %s, 'user', %s, 'text')
               RETURNING id, sender_type, message, message_type, is_read, created_at""",
            (chat["id"], uid, req.message)
        )
        msg = cur.fetchone()
        # Update chat timestamp and status
        cur.execute(
            "UPDATE support_chats SET updated_at = NOW(), status = 'waiting' WHERE id = %s",
            (chat["id"],)
        )
        conn.commit()
    
    return {"message": _format_message(msg)}


@router.get("/faq")
async def get_faq(language: str = "en", category: Optional[str] = None):
    """Get FAQ entries by language and optional category."""
    if category:
        rows = execute(
            "SELECT id, category, question, answer FROM support_faq WHERE language = %s AND category = %s AND is_active = TRUE ORDER BY sort_order",
            (language, category)
        )
    else:
        rows = execute(
            "SELECT id, category, question, answer FROM support_faq WHERE language = %s AND is_active = TRUE ORDER BY category, sort_order",
            (language,)
        )
    
    # Fallback to English if no results
    if not rows and language != "en":
        if category:
            rows = execute(
                "SELECT id, category, question, answer FROM support_faq WHERE language = 'en' AND category = %s AND is_active = TRUE ORDER BY sort_order",
                (category,)
            )
        else:
            rows = execute(
                "SELECT id, category, question, answer FROM support_faq WHERE language = 'en' AND is_active = TRUE ORDER BY category, sort_order",
                ()
            )
    
    return {"faq": [dict(r) for r in (rows or [])]}


@router.post("/chat/rate")
async def rate_chat(req: RateChatRequest, user: dict = Depends(get_current_user)):
    """Rate a resolved chat."""
    uid = user["user_id"]
    
    chat = execute_one(
        "SELECT * FROM support_chats WHERE user_id = %s AND status = 'resolved' ORDER BY resolved_at DESC LIMIT 1",
        (uid,)
    )
    
    if not chat:
        raise HTTPException(404, "No resolved chat to rate")
    
    execute(
        "UPDATE support_chats SET rating = %s WHERE id = %s",
        (req.rating, chat["id"])
    )
    
    return {"success": True, "rating": req.rating}


@router.post("/chat/close")
async def close_chat(user: dict = Depends(get_current_user)):
    """User closes their active chat."""
    uid = user["user_id"]
    
    execute(
        "UPDATE support_chats SET status = 'closed', resolved_at = NOW() WHERE user_id = %s AND status IN ('open', 'waiting')",
        (uid,)
    )
    
    return {"success": True}


@router.get("/chat/history")
async def get_chat_history(user: dict = Depends(get_current_user), limit: int = 10):
    """Get user's past resolved/closed chats."""
    uid = user["user_id"]
    limit = min(limit, 50)
    
    chats = execute(
        "SELECT * FROM support_chats WHERE user_id = %s AND status IN ('resolved', 'closed') ORDER BY created_at DESC LIMIT %s",
        (uid, limit)
    )
    
    return {"chats": [_format_chat(c) for c in (chats or [])]}


# ============================================================================
# Admin Endpoints
# ============================================================================

def _require_admin(user: dict = Depends(get_current_user)):
    """Dependency: require admin user."""
    if user["user_id"] != ADMIN_ID:
        raise HTTPException(403, "Admin access required")
    return user


@router.get("/admin/chats")
async def admin_list_chats(status: Optional[str] = None, admin: dict = Depends(_require_admin)):
    """List all support chats for admin. Filter by status."""
    if status:
        chats = execute(
            """SELECT sc.*, u.email, u.first_name, u.lang,
                      (SELECT COUNT(*) FROM support_messages sm WHERE sm.chat_id = sc.id AND sm.sender_type = 'user' AND sm.is_read = FALSE) as unread
               FROM support_chats sc
               LEFT JOIN users u ON u.user_id = sc.user_id
               WHERE sc.status = %s
               ORDER BY sc.updated_at DESC""",
            (status,)
        )
    else:
        chats = execute(
            """SELECT sc.*, u.email, u.first_name, u.lang,
                      (SELECT COUNT(*) FROM support_messages sm WHERE sm.chat_id = sc.id AND sm.sender_type = 'user' AND sm.is_read = FALSE) as unread
               FROM support_chats sc
               LEFT JOIN users u ON u.user_id = sc.user_id
               WHERE sc.status IN ('open', 'waiting')
               ORDER BY sc.updated_at DESC"""
        )
    
    result = []
    for c in (chats or []):
        item = _format_chat(c)
        item["email"] = c.get("email")
        item["first_name"] = c.get("first_name")
        item["user_lang"] = c.get("lang", "en")
        item["unread"] = c.get("unread", 0)
        result.append(item)
    
    return {"chats": result, "total": len(result)}


@router.get("/admin/chat/{chat_id}")
async def admin_get_chat(chat_id: int, admin: dict = Depends(_require_admin)):
    """Get specific chat with all messages."""
    chat = execute_one("SELECT * FROM support_chats WHERE id = %s", (chat_id,))
    if not chat:
        raise HTTPException(404, "Chat not found")
    
    # Mark user messages as read for admin
    execute(
        "UPDATE support_messages SET is_read = TRUE WHERE chat_id = %s AND sender_type = 'user' AND is_read = FALSE",
        (chat_id,)
    )
    
    messages = _get_chat_messages(chat_id)
    return {
        "chat": _format_chat(chat),
        "messages": messages
    }


@router.post("/admin/chat/{chat_id}/reply")
async def admin_reply(chat_id: int, req: AdminReplyRequest, admin: dict = Depends(_require_admin)):
    """Admin sends a reply to a chat."""
    chat = execute_one("SELECT * FROM support_chats WHERE id = %s", (chat_id,))
    if not chat:
        raise HTTPException(404, "Chat not found")
    
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO support_messages (chat_id, sender_id, sender_type, message, message_type)
               VALUES (%s, %s, 'admin', %s, 'text')
               RETURNING id, sender_type, message, message_type, is_read, created_at""",
            (chat_id, admin["user_id"], req.message)
        )
        msg = cur.fetchone()
        cur.execute(
            "UPDATE support_chats SET updated_at = NOW(), status = 'open' WHERE id = %s",
            (chat_id,)
        )
        conn.commit()
    
    return {"message": _format_message(msg)}


@router.post("/admin/chat/{chat_id}/resolve")
async def admin_resolve_chat(chat_id: int, admin: dict = Depends(_require_admin)):
    """Admin resolves a chat."""
    chat = execute_one("SELECT * FROM support_chats WHERE id = %s", (chat_id,))
    if not chat:
        raise HTTPException(404, "Chat not found")
    
    _add_system_message(chat_id, "This chat has been resolved by support. Thank you!")
    
    execute(
        "UPDATE support_chats SET status = 'resolved', resolved_at = NOW(), resolved_by = %s WHERE id = %s",
        (admin["user_id"], chat_id)
    )
    
    return {"success": True}


@router.get("/admin/stats")
async def admin_support_stats(admin: dict = Depends(_require_admin)):
    """Get support chat statistics."""
    stats = execute_one("""
        SELECT 
            COUNT(*) FILTER (WHERE status IN ('open', 'waiting')) as active_chats,
            COUNT(*) FILTER (WHERE status = 'waiting') as waiting_reply,
            COUNT(*) FILTER (WHERE status = 'resolved') as resolved_total,
            AVG(rating) FILTER (WHERE rating IS NOT NULL) as avg_rating,
            COUNT(*) as total_chats
        FROM support_chats
    """)
    
    return {
        "active_chats": stats["active_chats"] if stats else 0,
        "waiting_reply": stats["waiting_reply"] if stats else 0,
        "resolved_total": stats["resolved_total"] if stats else 0,
        "avg_rating": round(float(stats["avg_rating"] or 0), 1) if stats else 0,
        "total_chats": stats["total_chats"] if stats else 0,
    }


# ============================================================================
# Helpers
# ============================================================================

def _get_chat_messages(chat_id: int) -> list:
    """Get all messages for a chat."""
    rows = execute(
        "SELECT id, sender_type, message, message_type, is_read, created_at FROM support_messages WHERE chat_id = %s ORDER BY created_at ASC",
        (chat_id,)
    )
    return [_format_message(r) for r in (rows or [])]


def _format_chat(chat) -> dict:
    """Format chat row to response dict."""
    return {
        "id": chat["id"],
        "user_id": chat["user_id"],
        "status": chat["status"],
        "subject": chat.get("subject"),
        "language": chat.get("language", "en"),
        "created_at": str(chat["created_at"]) if chat.get("created_at") else "",
        "updated_at": str(chat["updated_at"]) if chat.get("updated_at") else "",
        "rating": chat.get("rating"),
    }


def _format_message(msg) -> dict:
    """Format message row to response dict."""
    return {
        "id": msg["id"],
        "sender_type": msg["sender_type"],
        "message": msg["message"],
        "message_type": msg.get("message_type", "text"),
        "is_read": msg.get("is_read", False),
        "created_at": str(msg["created_at"]) if msg.get("created_at") else "",
    }


def _add_system_message(chat_id: int, text: str):
    """Add a system message to a chat."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO support_messages (chat_id, sender_id, sender_type, message, message_type)
                   VALUES (%s, 0, 'admin', %s, 'system')""",
                (chat_id, text)
            )
            conn.commit()
    except Exception as e:
        logger.warning(f"Failed to add system message: {e}")
