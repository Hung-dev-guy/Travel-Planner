"""
chatbot/routes.py
Django views (function-based) for the Traplanner chatbot API.

Endpoints:
  POST /chatbot/api/chat/                   – Send a message to the agent
  GET  /chatbot/api/trips/<user_id>/        – List all trips for a user
  GET  /chatbot/api/trip/<trip_id>/         – Get trip + day details
  GET  /chatbot/api/health/                 – Health check (Redis + MongoDB)
  DELETE /chatbot/api/memory/<user_id>/     – Clear conversation memory
"""

import json
import logging
import time
import hashlib
import os
import uuid
from langsmith import traceable

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .llm import CHATBOT_MODEL  
from .agent import AgentState, create_agent_graph
from .memory import MemoryManager
from .db import (
    get_trips_for_user,
    get_full_trip_context,
)
from .prompts import GREETING_TEMPLATE

logger = logging.getLogger(__name__)

# ── LLM + agent graph (module-level singleton) ────────────────────────────────
_agent_graph = None


def _get_agent_graph():
    global _agent_graph
    if _agent_graph is None:
        llm = ChatGoogleGenerativeAI(
            model=CHATBOT_MODEL,
            google_api_key=os.environ.get("GOOGLE_API_KEY", ""),
            temperature=0.3,
        )
        _agent_graph = create_agent_graph(llm)
        logger.info("Agent graph created")
    return _agent_graph


# ── Helpers ───────────────────────────────────────────────────────────────────

def _json_response(data: dict, status: int = 200) -> JsonResponse:
    return JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": False})


def _error(message: str, status: int = 400) -> JsonResponse:
    return _json_response({"success": False, "error": message}, status)


def _extract_final_response(final_state: dict) -> str:
    """Pull the last AIMessage content from the final graph state."""
    messages = final_state.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not getattr(msg, "tool_calls", None):
            content = msg.content
            extracted_text = ""
            if isinstance(content, list):
                # Extract text blocks if it's a list
                text_blocks = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_blocks.append(block.get("text", ""))
                    elif isinstance(block, str):
                        text_blocks.append(block)
                extracted_text = "\n\n".join(text_blocks).strip()
            else:
                extracted_text = str(content).strip()
            
            if extracted_text:
                return extracted_text
            else:
                return "Tôi đã thực hiện xong các thao tác theo yêu cầu của bạn!"
    return "Xin lỗi, không thể tạo phản hồi lúc này."


# ── View: list trips for user ─────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET"])
def list_trips(request, user_id: str):
    """
    GET /chatbot/api/trips/<user_id>/
    Returns all trip plans created by the user.
    """
    try:
        trips = get_trips_for_user(user_id)
        return _json_response({
            "success": True,
            "user_id": user_id,
            "count": len(trips),
            "trips": trips,
        })
    except Exception as exc:
        logger.error(f"list_trips error: {exc}", exc_info=True)
        return _error(str(exc), 500)


# ── View: get trip detail ─────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET"])
def get_trip(request, trip_id: str):
    """
    GET /chatbot/api/trip/<trip_id>/
    Returns full trip data (trip + day details) from MongoDB.
    """
    try:
        ctx = get_full_trip_context(trip_id)
        if not ctx:
            return _error(f"Không tìm thấy chuyến đi: {trip_id}", 404)

        trip = ctx.get("trip", {})
        return _json_response({
            "success": True,
            "trip_id": trip_id,
            "trip": trip,
            "day_details": ctx.get("day_details", []),
            "greeting": GREETING_TEMPLATE.format(
                destination=trip.get("destination", ""),
                duration_days=len(ctx.get("day_details", [])),
                budget=float(trip.get("totalBudget", 0)),
            ),
        })
    except Exception as exc:
        logger.error(f"get_trip error: {exc}", exc_info=True)
        return _error(str(exc), 500)


# ── View: chat ────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
@traceable(run_type="chain", name="Traplanner_Chatbot_API")
def chat(request):
    """
    POST /chatbot/api/chat/
    Body (JSON):
      {
        "message": "...",
        "user_id": "...",
        "trip_id": "..."       // optional but recommended
      }

    Returns:
      { "success": bool, "response": str, "request_id": str, ... }
    """
    request_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    start = time.time()

    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return _error("Invalid JSON body", 400)

    message = body.get("message", "").strip()
    if not message:
        return _error("'message' field is required and cannot be empty", 400)

    user_id = body.get("user_id", "")
    if not user_id:
        # Derive a deterministic user-id from IP + User-Agent
        ua = request.META.get("HTTP_USER_AGENT", "")
        ip = request.META.get("REMOTE_ADDR", "unknown")
        user_id = "u_" + hashlib.md5(f"{ip}:{ua}".encode()).hexdigest()[:12]

    trip_id = body.get("trip_id", "")

    logger.info(f"[{request_id}] chat: user={user_id}, trip={trip_id}, msg='{message[:80]}'")

    graph = _get_agent_graph()

    initial_state: AgentState = {
        "input": message,
        "user_id": user_id,
        "trip_id": trip_id or None,
        "messages": [HumanMessage(content=message)],
        "trip_context": None,
        "memory_manager": None,
        "short_term_memory": None,
        "conversation_summaries": None,
        "needs_retrieval": None,
        "query_type": None,
        "confidence": None,
    }

    # Configure LangSmith threading and metadata
    thread_id = body.get("thread_id", str(uuid.uuid4()))
    invoke_config = {
        "recursion_limit": 30,
        "configurable": {
            "thread_id": thread_id
        },
        "tags": ["traplanner", "chatbot-api"],
        "metadata": {
            "user_id": user_id,
            "trip_id": trip_id
        }
    }

    try:
        final_state = graph.invoke(initial_state, config=invoke_config)
    except Exception as exc:
        logger.error(f"[{request_id}] graph.invoke error: {exc}", exc_info=True)
        return _json_response({
            "success": False,
            "request_id": request_id,
            "error": f"Lỗi xử lý: {type(exc).__name__}",
            "timing": {"total_seconds": round(time.time() - start, 3)},
        }, 500)

    response_text = _extract_final_response(final_state)
    total = round(time.time() - start, 3)

    logger.info(f"[{request_id}] done in {total}s, response={response_text[:100]}")

    return _json_response({
        "success": True,
        "request_id": request_id,
        "user_id": user_id,
        "trip_id": trip_id,
        "response": response_text,
        "query_type": final_state.get("query_type"),
        "timing": {"total_seconds": total},
    })


# ── View: health check ────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET"])
def health(request):
    """GET /chatbot/api/health/"""
    status_info: dict = {"status": "ok"}

    # Redis
    try:
        mm = MemoryManager.from_env()
        status_info["redis"] = mm.health_check()
    except Exception as exc:
        status_info["redis"] = {"status": "unhealthy", "error": str(exc)}
        status_info["status"] = "degraded"

    # MongoDB
    try:
        from .db import get_travel_db
        db = get_travel_db()
        db.command("ping")
        status_info["mongodb"] = {"status": "healthy"}
    except Exception as exc:
        status_info["mongodb"] = {"status": "unhealthy", "error": str(exc)}
        status_info["status"] = "degraded"

    return _json_response(status_info)


# ── View: clear memory ────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["DELETE"])
def clear_memory(request, user_id: str):
    """DELETE /chatbot/api/memory/<user_id>/"""
    try:
        mm = MemoryManager.from_env()
        ok = mm.clear_short_term_memory(user_id)
        return _json_response({
            "success": ok,
            "user_id": user_id,
            "message": "Bộ nhớ hội thoại đã được xóa." if ok else "Xóa thất bại.",
        })
    except Exception as exc:
        logger.error(f"clear_memory error: {exc}")
        return _error(str(exc), 500)