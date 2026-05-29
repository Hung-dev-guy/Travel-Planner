"""
trips/views.py

Django view that exposes the Traplanner pipeline as a REST endpoint.

POST /api/pipeline/run
  Body (JSON):
    {
      "user_des_input":   str,
      "destination":      str,
      "start_date":       str   (YYYY-MM-DD),
      "end_date":         str   (YYYY-MM-DD),
      "group_size":       int,
      "budget":           int   (total VNĐ),
      "travel_style":     list[str],
      "travel_pace":      str,
      "companion_type":   str,
      "accommodation_style": str,
      "health_limitations":  list[str]   (optional)
    }

  Response (JSON): final_answer dict from Generate_answer node
"""

import json
import logging
from datetime import datetime, date, timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from workflow.nodes.Mobility_agent import mobility_node
from workflow.nodes.Scheduler import scheduler_node
from workflow.nodes.Validation_agent import validation_node
from workflow.nodes.Generate_answer import generate_answer_node
from workflow.db import get_mongo_db, reset_mongo_connection

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Fallback mock data (used when MongoDB returns nothing)
# ─────────────────────────────────────────────────────────────────────────────

MOCK_ACTIVITIES = [
    {
        "_id": "act_001",
        "name": "Hạ Long Bay Cruise",
        "description": "UNESCO World Heritage limestone karsts cruise",
        "ward_name": "Hạ Long",
        "estimatedPrice": 150_000,
        "estimatedDuration": 180,
        "suitabilityFor": ["Couples", "Family"],
        "category": "nature",
    },
    {
        "_id": "act_002",
        "name": "Sung Sot Cave Exploration",
        "description": "Famous limestone cave with stunning formations",
        "ward_name": "Bạch Đằng",
        "estimatedPrice": 80_000,
        "estimatedDuration": 120,
        "suitabilityFor": ["Couples", "Group", "Solo"],
        "category": "cultural",
    },
    {
        "_id": "act_003",
        "name": "Titop Island Beach",
        "description": "Beautiful beach with crystal clear water",
        "ward_name": "Hạ Long",
        "estimatedPrice": 50_000,
        "estimatedDuration": 240,
        "suitabilityFor": ["Couples", "Family"],
        "category": "nature",
    },
    {
        "_id": "act_004",
        "name": "Mong Cai Border Market",
        "description": "Traditional border trading town experience",
        "ward_name": "Mong Cai",
        "estimatedPrice": 30_000,
        "estimatedDuration": 150,
        "suitabilityFor": ["Couples", "Group", "Solo"],
        "category": "cultural",
    },
]

MOCK_ACCOMMODATIONS = [
    {
        "_id": "acc_001",
        "name": "Halong Bay Hotel",
        "ward_name": "Hạ Long",
        "estimatedPrice": 200_000,
        "accommodation_style": "comfortable",
        "quality_level": "comfortable",
    },
    {
        "_id": "acc_002",
        "name": "Halong Bay Hotel",
        "ward_name": "Hạ Long",
        "estimatedPrice": 200_000,
        "accommodation_style": "comfortable",
        "quality_level": "comfortable",
    },
    {
        "_id": "acc_003",
        "name": "Halong Bay Hotel",
        "ward_name": "Hạ Long",
        "estimatedPrice": 200_000,
        "accommodation_style": "comfortable",
        "quality_level": "comfortable",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_daily_active_hours(raw) -> int:
    """Convert '8-10', '8h', 10, etc. to an integer."""
    if isinstance(raw, (int, float)):
        return int(raw)
    if isinstance(raw, str):
        raw = raw.strip().lower().replace("h", "").replace(" ", "")
        if "-" in raw:
            return int(raw.split("-")[0])
        try:
            return int(float(raw))
        except ValueError:
            pass
    return 10


def _compute_total_days(start_date_str: str, end_date_str: str) -> int:
    try:
        start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        return max(1, (end - start).days + 1)
    except Exception:
        return 3


def _load_activities_from_mongo() -> list:
    try:
        db = get_mongo_db("TravelPlanner")
        docs = list(db["Locations"].find(
            {"category": {"$in": ["nature", "adventure", "cultural", "viewpoint"]}},
            {"_id": 1, "name": 1, "description": 1, "ward_name": 1,
             "estimatedPrice": 1, "estimatedDuration": 1,
             "suitabilityFor": 1, "category": 1},
        ))
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs
    except Exception as e:
        logger.warning(f"MongoDB activity fetch failed: {e}")
        return []


def _build_mock_accommodations(total_days: int) -> list:
    """Return enough mock accommodations for total_days nights."""
    base = {
        "name": "Local Hotel",
        "ward_name": "Hạ Long",
        "estimatedPrice": 200_000,
        "quality_level": "comfortable",
    }
    return [{"_id": f"acc_{i:03d}", **base} for i in range(1, total_days + 1)]


# ─────────────────────────────────────────────────────────────────────────────
# Views
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """GET /api/pipeline/health — quick liveness check."""
    return JsonResponse({"status": "ok", "service": "traplanner-pipeline"})


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def generate_plan(request):
    """
    POST /api/pipeline/run

    Runs the full Mobility → Scheduler → Validation → Generate_answer pipeline
    and returns the final_answer as JSON.
    """
    if request.method == "OPTIONS":
        return JsonResponse({}, status=200)

    # ── Parse request body ────────────────────────────────────────────────────
    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": f"Invalid JSON: {e}"}, status=400)

    # Required fields
    destination = body.get("destination", "Quảng Ninh")
    start_date  = body.get("start_date", "2026-06-01")
    end_date    = body.get("end_date",   "2026-06-03")
    group_size  = int(body.get("group_size", 2))
    budget      = int(body.get("budget", 2_000_000))

    # Optional / preference fields
    user_des_input       = body.get("user_des_input", "")
    travel_style         = body.get("travel_style", ["nature", "cultural"])
    travel_pace          = body.get("travel_pace", "moderate")
    companion_type       = body.get("companion_type", "Couples")
    accommodation_style  = body.get("accommodation_style", "comfortable")
    health_limitations   = body.get("health_limitations", [])

    # Normalize list fields
    if isinstance(travel_style, str):
        travel_style = [travel_style]
    if isinstance(travel_pace, str):
        travel_pace = [travel_pace]
    if isinstance(companion_type, str):
        companion_type = [companion_type]

    total_days = _compute_total_days(start_date, end_date)

    logger.info(
        f"Pipeline request: destination={destination}, dates={start_date}→{end_date}, "
        f"days={total_days}, group={group_size}, budget={budget:,}"
    )

    # ── Build initial state ───────────────────────────────────────────────────
    state = {
        "user_des_input": user_des_input,
        "group_size": group_size,
        "start_date": start_date,
        "end_date": end_date,
        "start_location": "Hà Nội",
        "destination": [destination],
        "personal_travel_style_des": ", ".join(travel_style),

        "trip_metadata": {
            "usr_des": user_des_input,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": str(total_days),
            "age_range": "18-60",
            "start_location": "Hà Nội",
            "destination": destination,
        },

        "constraints": {
            "travel_budget": budget,
            "group_size": group_size,
            "daily_active_hours": 8,        # int — validation expects int
            "language": "Vietnamese",
            "max_radius_distance": 50,
            "places_of_limitation": [],
            "health_limitations": health_limitations,
            "mobility_limitations": [],
        },

        "travel_preferences": {
            "travel_style": travel_style,
            "travel_pace": travel_pace,
            "food_style": ["local"],
            "accommodation_style": accommodation_style,   # scalar string
            "mobility_style": ["flexible"],
            "atmosphere": ["lãng mạn"],
            "companion_type": companion_type,
        },

        "activities":      [],
        "accommodations":  [],
        "transportations": [],
        "scheduling":      [],
        "validation":      None,
        "validation_feedback": [],
        "validation_iteration": 1,
        "final_answer":    None,
    }

    # ── Step 1: Mobility_agent ────────────────────────────────────────────────
    try:
        reset_mongo_connection()
        state = mobility_node(state)
        logger.info(f"Mobility OK: {len(state.get('transportations', []))} transport options")
    except Exception as e:
        logger.warning(f"Mobility_agent failed ({e}) — continuing without transport data")
        state["transportations"] = []

    # ── Step 1b: Activities & Accommodations ──────────────────────────────────
    activities = _load_activities_from_mongo()
    state["activities"] = activities if activities else MOCK_ACTIVITIES
    logger.info(f"Activities: {len(state['activities'])} loaded")

    if not state.get("accommodations"):
        state["accommodations"] = _build_mock_accommodations(total_days)

    # ── Step 2: Scheduler ─────────────────────────────────────────────────────
    try:
        state = scheduler_node(state)
        logger.info(f"Scheduler OK: {len(state.get('scheduling', []))} days")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
        return JsonResponse({"error": f"Scheduler error: {e}"}, status=500)

    # ── Step 3: Validation ────────────────────────────────────────────────────
    try:
        state = validation_node(state)
        val = state.get("validation", {})
        logger.info(f"Validation OK: score={val.get('overall_score', 0):.0f}, status={val.get('status')}")
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return JsonResponse({"error": f"Validation error: {e}"}, status=500)

    # ── Step 4: Generate_answer ───────────────────────────────────────────────
    try:
        state = generate_answer_node(state)
    except Exception as e:
        logger.error(f"Generate_answer failed: {e}")
        return JsonResponse({"error": f"Generate answer error: {e}"}, status=500)

    final_answer = state.get("final_answer", {})
    logger.info(f"Pipeline complete → returning final_answer")
    return JsonResponse(final_answer, json_dumps_params={"ensure_ascii": False})
