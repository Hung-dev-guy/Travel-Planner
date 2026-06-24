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
        day_details_col = db["DayDetails"]

        # All trips for user
        all_trips = list(trips_col.find(
            {"userId": user_id},
            {"_id": 0, "tripId": 1, "destination": 1, "status": 1,
             "totalBudget": 1, "createdAt": 1}
        ).sort("createdAt", -1))

        # Fallback to demo data if user has no trips
        if len(all_trips) == 0 and user_id != "U001":
            all_trips = list(trips_col.find(
                {"userId": "U001"},
                {"_id": 0, "tripId": 1, "destination": 1, "status": 1,
                 "totalBudget": 1, "createdAt": 1}
            ).sort("createdAt", -1))

        total_trips = len(all_trips)
        upcoming = sum(1 for t in all_trips if t.get("status") in ("PLANNING", "CONFIRMED"))

        # Calculate total budget
        total_budget = sum(float(t.get("totalBudget", 0)) for t in all_trips)

        # Unique destinations (countries / cities)
        destinations = list({t.get("destination", "") for t in all_trips if t.get("destination")})

        # Calculate trips per month
        from collections import defaultdict
        import datetime
        trips_per_month_dict = defaultdict(int)
        for t in all_trips:
            created_at = t.get("createdAt")
            if isinstance(created_at, datetime.datetime):
                month_str = created_at.strftime("%Y-%m")
                trips_per_month_dict[month_str] += 1
            elif isinstance(created_at, str) and len(created_at) >= 7:
                month_str = created_at[:7]
                trips_per_month_dict[month_str] += 1
        
        trips_per_month = [{"month": k, "count": v} for k, v in sorted(trips_per_month_dict.items())]

        # Calculate cost distribution by category from DayDetails
        trip_ids = [t.get("tripId") for t in all_trips if t.get("tripId")]
        cost_dist_dict = defaultdict(float)
        
        if trip_ids:
            day_details = list(day_details_col.find({"tripId": {"$in": trip_ids}}))
            for day in day_details:
                for act in day.get("dayActs", []):
                    act_type = act.get("type", "Other")
                    price = float(act.get("price", 0))
                    cost_dist_dict[act_type] += price
                    
        cost_distribution = [{"category": k, "amount": v} for k, v in cost_dist_dict.items()]

        # All trips sorted by newest
        recent_trips = [_serialize(t) for t in all_trips]

        return _json({
            "success": True,
            "user_id": user_id,
            "stats": {
                "total_trips": total_trips,
                "upcoming": upcoming,
                "total_budget": total_budget,
                "destinations_count": len(destinations),
                "destinations": destinations[:8],
                "trips_per_month": trips_per_month,
                "cost_distribution": cost_distribution
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
