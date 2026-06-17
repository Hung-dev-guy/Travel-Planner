"""
dashboard/views.py
Django views for the Traplanner Dashboard API.
Serves real trip statistics and recent trips for a given user from MongoDB.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from workflow.db import get_mongo_db

logger = logging.getLogger(__name__)


def _json(data, status=200):
    return JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": False})


def _serialize(doc):
    """Convert ObjectId to str."""
    if doc is None:
        return {}
    out = {}
    from bson import ObjectId
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, dict):
            out[k] = _serialize(v)
        elif isinstance(v, list):
            out[k] = [_serialize(i) if isinstance(i, dict) else
                      (str(i) if isinstance(v, ObjectId) else i) for i in v]
        else:
            out[k] = v
    return out


@csrf_exempt
@require_http_methods(["GET"])
def dashboard_stats(request, user_id: str):
    """
    GET /dashboard/api/stats/<user_id>/
    Returns aggregated stats + recent trips for the dashboard.
    """
    try:
        db = get_mongo_db("TravelDB")
        trips_col = db["Trips"]

        # All trips for user
        all_trips = list(trips_col.find(
            {"userId": user_id},
            {"_id": 0, "tripId": 1, "destination": 1, "status": 1,
             "totalBudget": 1, "createdAt": 1}
        ).sort("createdAt", -1))

        total_trips = len(all_trips)
        upcoming = sum(1 for t in all_trips if t.get("status") in ("PLANNING", "CONFIRMED"))

        # Unique destinations (countries / cities)
        destinations = list({t.get("destination", "") for t in all_trips if t.get("destination")})

        # All trips sorted by newest
        recent_trips = [_serialize(t) for t in all_trips]

        return _json({
            "success": True,
            "user_id": user_id,
            "stats": {
                "total_trips": total_trips,
                "upcoming": upcoming,
                "destinations_count": len(destinations),
                "destinations": destinations[:8],
            },
            "recent_trips": recent_trips,
        })

    except Exception as exc:
        logger.error(f"dashboard_stats error: {exc}", exc_info=True)
        return _json({"success": False, "error": str(exc)}, 500)


@csrf_exempt
@require_http_methods(["GET"])
def health(request):
    """GET /dashboard/api/health/"""
    try:
        db = get_mongo_db("TravelDB")
        db.command("ping")
        return _json({"status": "ok", "mongodb": "healthy"})
    except Exception as exc:
        return _json({"status": "degraded", "error": str(exc)}, 500)
