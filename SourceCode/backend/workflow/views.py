import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import uuid
from langsmith import traceable

from workflow.graph.builder import build_workflow
from workflow.db import get_mongo_db

logger = logging.getLogger(__name__)

def _json(data, status=200):
    return JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": False})

@csrf_exempt
@require_http_methods(["POST"])
@traceable(run_type="chain", name="Traplanner_API_Pipeline")
def run_pipeline(request):
    try:
        payload = json.loads(request.body)
    except Exception:
        return _json({"error": "Invalid JSON payload"}, 400)

    try:
        app = build_workflow()
        
        # Build initial state
        initial_state = {
            "user_des_input": payload.get("user_des_input", ""),
            "usr_des_input": payload.get("user_des_input", ""),
            "group_size": int(payload.get("group_size", 2)),
            "start_date": payload.get("start_date", ""),
            "end_date": payload.get("end_date", ""),
            "start_location": payload.get("starting_location", ""),
            "destination": payload.get("destination", []) if isinstance(payload.get("destination"), list) else ([payload.get("destination")] if payload.get("destination") else []),
            "personal_travel_style_des": f"Phong cách: {', '.join(payload.get('travel_style', []))}. Nhịp độ: {payload.get('travel_pace', '')}. Đối tượng đi cùng: {payload.get('companion_type', '')}.",
            "trip_metadata": {"total_budget": int(payload.get("budget", 2000000))},
            "travel_preferences": {},
            "constraints": {},
            "validation_iteration": 1,
            "validation_feedback": []
        }

        # Configure LangSmith threading and metadata
        thread_id = payload.get("thread_id", str(uuid.uuid4()))
        config = {
            "configurable": {
                "thread_id": thread_id
            },
            "tags": ["traplanner", "production-api"],
            "metadata": {
                "user_id": payload.get("user_id", "anonymous"),
                "destination": payload.get("destination", "")
            }
        }

        # Run pipeline with LangSmith tracking
        final_state = app.invoke(initial_state, config=config)

        # Persist to MongoDB
        final_answer = final_state.get("final_answer", {})
        db_schema = final_answer.get("database_schema")
        
        db_schema = final_answer.get("database_schema")

        # Format for frontend
        trip_meta = final_state.get("trip_metadata", {})
        val_res = final_state.get("validation", {})
        scheduling_data = final_state.get("scheduling", [])
        
        # Calculate budget stuff
        trip_meta = final_state.get("trip_metadata", {})
        total_budget = trip_meta.get("total_budget", int(payload.get("budget", 2000000)))
        frontend_scheduling = []
        total_cost = 0
        for day_data in scheduling_data:
            day_num = day_data.get("day", 1)
            items = []
            for act in day_data.get("items", []):
                cost = int(act.get("cost", act.get("estimatedPrice", 0)))
                total_cost += cost
                items.append({
                    "type": act.get("type", "activity").lower(),
                    "name": act.get("name", "Activity"),
                    "time_start": act.get("time_start", act.get("time", "08:00")),
                    "time_end": act.get("time_end", "10:00"),
                    "location": act.get("locationId", ""),
                    "cost": cost
                })
            frontend_scheduling.append({
                "day": int(day_num),
                "title": day_data.get("theme", f"Ngày {day_num}"),
                "date": day_data.get("date", ""),
                "items": items,
                "day_summary": day_data.get("metrics", {})
            })
            
        frontend_scheduling.sort(key=lambda x: x["day"])
        
        utilization = (total_cost / total_budget * 100) if total_budget else 0

        # Highlights from generated response
        highlights = []
        if final_answer and "sections" in final_answer:
            summary_section = next((s for s in final_answer["sections"] if s["type"] == "summary"), None)
            if summary_section:
                highlights = summary_section.get("content", "").split("\n")[:3]

        response_data = {
            "trip_overview": {
                "total_days": trip_meta.get("total_days", payload.get("duration", len(frontend_scheduling))),
                "destination": payload.get("destination", ""),
                "start_date": payload.get("start_date", ""),
                "end_date": payload.get("end_date", ""),
                "group_size": payload.get("group_size", 2),
                "travel_budget": total_budget,
                "total_estimated_cost": total_cost,
                "budget_utilization_pct": utilization,
                "highlights": highlights
            },
            "scheduling": frontend_scheduling,
            "validation": {
                "overall_score": val_res.get("overall_score", 0),
                "status": val_res.get("status", "APPROVED"),
                "category_scores": val_res.get("category_scores", {}),
                "issues": val_res.get("issues", []),
                "recommendations": val_res.get("recommendations", [])
            },
            "db_schema": db_schema,
            "status_message": "Kế hoạch đã được tạo thành công!" if val_res.get("status") == "APPROVED" else "Kế hoạch cần được tối ưu thêm."
        }
        
        # Ensure db_schema has the correct budget before sending to frontend
        if response_data["db_schema"] and "trip" in response_data["db_schema"]:
            response_data["db_schema"]["trip"]["totalBudget"] = total_budget
        
        return _json(response_data)
        
    except Exception as exc:
        logger.error(f"Pipeline error: {exc}", exc_info=True)
        error_msg = str(exc)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            friendly_error = "Hệ thống AI đã hết lượt sử dụng (Quota Exceeded) hoặc bị giới hạn tốc độ. Vui lòng kiểm tra API Key hoặc thử lại sau."
            return _json({"error": friendly_error}, 500)
        elif "503" in error_msg:
            friendly_error = "Hệ thống AI hiện đang quá tải (Lỗi 503). Vui lòng chờ ít phút rồi thử lại."
            return _json({"error": friendly_error}, 500)
        
        return _json({"error": "Lỗi hệ thống: " + error_msg}, 500)

@csrf_exempt
@require_http_methods(["POST"])
def save_trip(request):
    try:
        payload = json.loads(request.body)
        db_schema = payload.get("db_schema")
        if not db_schema:
            return _json({"error": "Missing db_schema"}, 400)
            
        trip_doc = db_schema.get("trip")
        day_details = db_schema.get("day_details", [])
        
        db = get_mongo_db("TravelDB")
        if trip_doc:
            trip_doc["userId"] = payload.get("user_id", "U001")
            db["Trips"].insert_one(trip_doc)
        if day_details:
            db["DayDetails"].insert_many(day_details)
            
        return _json({"success": True, "message": "Trip saved successfully!"})
    except Exception as exc:
        logger.error(f"MongoDB persistence failed: {exc}")
        return _json({"error": str(exc)}, 500)

@csrf_exempt
@require_http_methods(["GET"])
def health(request):
    return _json({"status": "ok"})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_trip(request, trip_id):
    try:
        db = get_mongo_db("TravelDB")
        db["Trips"].delete_one({"tripId": trip_id})
        db["DayDetails"].delete_many({"tripId": trip_id})
        return _json({"success": True, "message": "Deleted successfully"})
    except Exception as exc:
        logger.error(f"delete_trip failed: {exc}")
        return _json({"error": str(exc)}, 500)

@csrf_exempt
@require_http_methods(["GET"])
def get_trip(request, trip_id):
    try:
        db = get_mongo_db("TravelDB")
        trip = db["Trips"].find_one({"tripId": trip_id})
        if not trip:
            return _json({"error": "Trip not found"}, 404)
        
        day_details = list(db["DayDetails"].find({"tripId": trip_id}).sort("dayNumber", 1))
        
        scheduling = []
        total_cost = 0
        for day in day_details:
            items = []
            for act in day.get("dayActs", []):
                price = int(act.get("price", 0))
                total_cost += price
                items.append({
                    "type": act.get("type", "activity").lower(),
                    "name": act.get("name", "Activity"),
                    "time_start": act.get("startTime", ""),
                    "time_end": act.get("endTime", ""),
                    "cost": price,
                    "location": act.get("locationId", ""),
                    "description": act.get("note", ""),
                    "image": act.get("image", None)
                })
            scheduling.append({
                "day": day.get("dayNumber"),
                "title": f"Ngày {day.get('dayNumber')}",
                "date": day.get("date", ""),
                "items": items,
                "day_summary": {
                    "total_cost": sum(i["cost"] for i in items),
                    "activities_count": len([i for i in items if i["type"] not in ["stay", "eat"]]),
                    "meals_count": len([i for i in items if i["type"] == "eat"])
                }
            })
            
        budget = trip.get("totalBudget", 2000000)
        
        result = {
            "trip_overview": {
                "total_days": len(scheduling),
                "destination": trip.get("destination", ""),
                "start_date": trip.get("startDate", ""),
                "end_date": trip.get("endDate", ""),
                "group_size": trip.get("groupSize", 2),
                "travel_budget": budget,
                "total_estimated_cost": total_cost,
                "budget_utilization_pct": (total_cost / budget * 100) if budget else 0,
                "highlights": []
            },
            "scheduling": scheduling,
            "validation": {
                "overall_score": trip.get("validationScore", 100),
                "status": "APPROVED",
                "category_scores": trip.get("categoryScores", {
                    "budget": 20, "time": 15, "activity_suitability": 20, 
                    "accommodation": 15, "transport": 10, "balance": 10, "health": 10
                }),
                "issues": [],
                "recommendations": []
            },
            "status_message": "Kế hoạch đã được tạo thành công!"
        }
        return _json({"success": True, "result": result})
    except Exception as exc:
        logger.error(f"get_trip failed: {exc}")
        return _json({"error": str(exc)}, 500)
