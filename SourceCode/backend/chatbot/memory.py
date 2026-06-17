"""
chatbot/memory.py
Redis-backed short-term and long-term memory manager for the Traplanner chatbot.
"""

import json
import logging
import os
import time
from typing import List, Dict, Optional, Any
from datetime import datetime

import redis
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)

_MAX_SHORT_TERM = int(os.environ.get("MAX_SHORT_TERM_MESSAGES", 30))
_SHORT_TTL = int(os.environ.get("SHORT_TERM_MEMORY_TTL", 7200))       # 2 h
_LONG_TTL = int(os.environ.get("LONG_TERM_MEMORY_TTL", 2592000))       # 30 d


class MemoryManager:
    """Manages conversation memory using Redis."""

    def __init__(self, redis_client: redis.Redis):
        self.r = redis_client

    # ── Factory ────────────────────────────────────────────────────────────────

    @classmethod
    def from_env(cls) -> "MemoryManager":
        """Create a MemoryManager from environment variables."""
        client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            password=os.environ.get("REDIS_PASSWORD") or None,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        client.ping()
        logger.info("Redis connected (MemoryManager)")
        return cls(client)

    # ── Short-term memory ──────────────────────────────────────────────────────

    def save_short_term_memory(self, user_id: str,
                                messages: List[BaseMessage]) -> bool:
        """Persist the last N messages to Redis."""
        try:
            key = f"traplanner:short:{user_id}"
            data = []
            for msg in messages[-_MAX_SHORT_TERM:]:
                entry: Dict[str, Any] = {
                    "type": msg.__class__.__name__,
                    "content": msg.content,
                    "timestamp": time.time(),
                }
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    entry["tool_calls"] = [
                        {"name": tc.get("name", ""), "args": tc.get("args", {}), "id": tc.get("id", "")}
                        for tc in msg.tool_calls
                    ]
                data.append(entry)
            self.r.setex(key, _SHORT_TTL, json.dumps(data, ensure_ascii=False))
            logger.info(f"Saved {len(data)} messages for user {user_id}")
            return True
        except Exception as exc:
            logger.error(f"save_short_term_memory error: {exc}")
            return False

    def load_short_term_memory(self, user_id: str) -> List[BaseMessage]:
        """Load recent messages from Redis."""
        try:
            key = f"traplanner:short:{user_id}"
            raw = self.r.get(key)
            if not raw:
                return []
            messages: List[BaseMessage] = []
            for entry in json.loads(raw):
                if entry["type"] == "HumanMessage":
                    messages.append(HumanMessage(content=entry["content"]))
                elif entry["type"] == "AIMessage":
                    msg = AIMessage(content=entry["content"])
                    if "tool_calls" in entry:
                        msg.tool_calls = entry["tool_calls"]
                    messages.append(msg)
            logger.info(f"Loaded {len(messages)} messages for user {user_id}")
            return messages
        except Exception as exc:
            logger.error(f"load_short_term_memory error: {exc}")
            return []

    def clear_short_term_memory(self, user_id: str) -> bool:
        """Clear a user's short-term memory."""
        try:
            self.r.delete(f"traplanner:short:{user_id}")
            return True
        except Exception as exc:
            logger.error(f"clear_short_term_memory error: {exc}")
            return False

    # ── Conversation summaries ─────────────────────────────────────────────────

    def save_conversation_summary(self, user_id: str, summary: str,
                                   conversation_id: str = "") -> bool:
        """Append a summary to the user's long-term conversation list."""
        try:
            entry = {
                "summary": summary,
                "conversation_id": conversation_id or f"conv_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
            }
            key = f"traplanner:summaries:{user_id}"
            raw = self.r.get(key)
            summaries: List[dict] = json.loads(raw) if raw else []
            summaries.append(entry)
            summaries = summaries[-50:]   # keep last 50
            self.r.setex(key, _LONG_TTL, json.dumps(summaries, ensure_ascii=False))
            logger.info(f"Saved summary for user {user_id}")
            return True
        except Exception as exc:
            logger.error(f"save_conversation_summary error: {exc}")
            return False

    def get_conversation_summaries(self, user_id: str,
                                    limit: int = 10) -> List[Dict[str, Any]]:
        """Return recent conversation summaries."""
        try:
            key = f"traplanner:summaries:{user_id}"
            raw = self.r.get(key)
            if not raw:
                return []
            return json.loads(raw)[-limit:]
        except Exception as exc:
            logger.error(f"get_conversation_summaries error: {exc}")
            return []

    # ── User preferences ───────────────────────────────────────────────────────

    def save_user_preferences(self, user_id: str,
                               preferences: Dict[str, Any]) -> bool:
        try:
            key = f"traplanner:prefs:{user_id}"
            self.r.setex(key, _LONG_TTL, json.dumps(preferences, ensure_ascii=False))
            return True
        except Exception as exc:
            logger.error(f"save_user_preferences error: {exc}")
            return False

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        try:
            key = f"traplanner:prefs:{user_id}"
            raw = self.r.get(key)
            return json.loads(raw) if raw else {}
        except Exception as exc:
            logger.error(f"get_user_preferences error: {exc}")
            return {}

    # ── Health ─────────────────────────────────────────────────────────────────

    def health_check(self) -> Dict[str, Any]:
        try:
            t0 = time.time()
            self.r.ping()
            info = self.r.info()
            return {
                "status": "healthy",
                "response_time_ms": round((time.time() - t0) * 1000, 2),
                "redis_version": info.get("redis_version", "?"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "?"),
            }
        except Exception as exc:
            return {"status": "unhealthy", "error": str(exc)}