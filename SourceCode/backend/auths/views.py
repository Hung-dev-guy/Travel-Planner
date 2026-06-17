import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import google.generativeai as genai
from workflow.models.llm import DEFAULT_MODEL

import uuid
from django.contrib.auth.hashers import make_password, check_password

# We can reuse the MongoDB connection from chatbot.db
from chatbot.db import get_travel_db, get_trips_for_user, get_day_details_for_trip

logger = logging.getLogger(__name__)

def extract_preferences_from_history(user_id):
    """Phân tích lịch sử chuyến đi của user bằng AI để tự động suy luận sở thích."""
    trips = get_trips_for_user(user_id)
    if not trips:
        return []
        
    history_text = ""
    for t in trips:
        trip_id = t.get("tripId")
        if not trip_id: continue
        dest = t.get("destination", "Không rõ")
        budget = t.get("totalBudget", 0)
        days = get_day_details_for_trip(trip_id)
        
        history_text += f"- Chuyến đi tới {dest}, Ngân sách: {budget} VNĐ.\n"
        for d in days:
            acts = d.get("dayActs", [])
            acts_str = ", ".join([f"[{a.get('type')}] {a.get('name')}" for a in acts if a.get('name')])
            if acts_str:
                history_text += f"  + Ngày {d.get('dayNumber')}: {acts_str}\n"
            
    if not history_text.strip():
        return []
        
    prompt = f"""
    Dưới đây là lịch sử các chuyến du lịch của một người dùng trên hệ thống. 
    Dựa vào các địa điểm đến, loại hình hoạt động (ăn uống, tham quan, khách sạn...), và chi phí, hãy phân tích và rút ra 3-5 điểm về "Sở thích và phong cách du lịch" của người này.
    (Ví dụ: thích thiên nhiên, hay đi bảo tàng, ăn nhiều hải sản, chi tiêu tiết kiệm, v.v.)

    Lịch sử chuyến đi:
    {history_text}

    Trả về ĐÚNG MỘT định dạng JSON là một mảng các chuỗi, ví dụ: ["Thích đi biển", "Thích ăn hải sản"]. Không thêm bất kỳ văn bản nào khác ngoài JSON.
    """
    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        prefs = json.loads(text)
        return prefs if isinstance(prefs, list) else []
    except Exception as e:
        logger.error(f"Error extracting preferences with AI: {e}")
        return []

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """
    Login flow with password check. Also checks if the user has >= 5 new trips
    since their last AI preference update, and flags it.
    """
    try:
        payload = json.loads(request.body)
        username = payload.get("username", "").strip() 
        password = payload.get("password", "")
        
        if not username:
            return JsonResponse({"error": "Username is required"}, status=400)
            
        db = get_travel_db()
        user = db["Users"].find_one({"username": username})
        
        if not user:
            return JsonResponse({"error": "Tài khoản không tồn tại"}, status=404)
            
        if user.get("password") and not check_password(password, user.get("password")):
            return JsonResponse({"error": "Sai mật khẩu"}, status=401)
            
        # Check if they have 5 or more new trips since last preference update
        trips = get_trips_for_user(user["userId"])
        current_trips_count = len(trips)
        last_update_count = user.get("last_update_trip_count", 0)
        
        can_auto_update_preferences = (current_trips_count - last_update_count) >= 5
        
        return JsonResponse({
            "success": True,
            "user": {
                "userId": user["userId"],
                "username": user["username"],
                "full_name": user.get("full_name", ""),
                "preferences": user.get("preferences", []),
                "can_auto_update_preferences": can_auto_update_preferences
            }
        })
    except Exception as exc:
        logger.error(f"Login error: {exc}")
        return JsonResponse({"error": str(exc)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """
    Đăng ký người dùng mới.
    """
    try:
        payload = json.loads(request.body)
        username = payload.get("username", "").strip()
        password = payload.get("password", "")
        full_name = payload.get("full_name", "").strip()
        
        if not username or not password:
            return JsonResponse({"error": "Username và Password là bắt buộc"}, status=400)
            
        db = get_travel_db()
        if db["Users"].find_one({"username": username}):
            return JsonResponse({"error": "Tên đăng nhập đã tồn tại"}, status=400)
            
        user_id = str(uuid.uuid4())
        new_user = {
            "userId": user_id,
            "username": username,
            "password": make_password(password),
            "full_name": full_name,
            "preferences": [],
            "last_update_trip_count": 0,
            "createdAt": datetime.utcnow()
        }
        db["Users"].insert_one(new_user)
        
        return JsonResponse({
            "success": True,
            "message": "Đăng ký thành công",
            "user": {
                "userId": user_id,
                "username": username,
                "full_name": full_name,
                "preferences": []
            }
        })
    except Exception as exc:
        logger.error(f"Register error: {exc}")
        return JsonResponse({"error": str(exc)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_profile(request):
    """
    Cập nhật thông tin profile: username, full_name, password, và manual preferences.
    """
    try:
        payload = json.loads(request.body)
        user_id = payload.get("userId", "").strip()
        if not user_id:
            return JsonResponse({"error": "userId is required"}, status=400)
            
        db = get_travel_db()
        user = db["Users"].find_one({"userId": user_id})
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)
            
        updates = {}
        if "username" in payload and payload["username"].strip():
            new_username = payload["username"].strip()
            if new_username != user.get("username") and db["Users"].find_one({"username": new_username}):
                return JsonResponse({"error": "Username đã được sử dụng"}, status=400)
            updates["username"] = new_username
            
        if "full_name" in payload:
            updates["full_name"] = payload["full_name"].strip()
            
        if "password" in payload and payload["password"]:
            updates["password"] = make_password(payload["password"])
            
        if "preferences" in payload and isinstance(payload["preferences"], list):
            updates["preferences"] = payload["preferences"]
            
        if updates:
            updates["updatedAt"] = datetime.utcnow()
            db["Users"].update_one({"userId": user_id}, {"$set": updates})
            
        return JsonResponse({"success": True, "message": "Cập nhật hồ sơ thành công"})
    except Exception as exc:
        logger.error(f"Update profile error: {exc}")
        return JsonResponse({"error": str(exc)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_preferences(request):
    """
    Endpoint for users to manually trigger a refresh of their preferences 
    based on their past trips history.
    """
    try:
        payload = json.loads(request.body)
        username = payload.get("username", "").strip()
        
        if not username:
            return JsonResponse({"error": "Username is required"}, status=400)
            
        db = get_travel_db()
        user_id = username
        
        user = db["Users"].find_one({"userId": user_id})
        if not user:
            return JsonResponse({"error": "User not found. Please login first."}, status=404)
            
        # Tự động trích xuất sở thích mới từ lịch sử chuyến đi
        extracted_preferences = extract_preferences_from_history(user_id)
        
        # Cập nhật số lượng chuyến đi tại thời điểm trích xuất để dùng cho lần kiểm tra sau
        current_trips_count = len(get_trips_for_user(user_id))
        
        # Merge hoặc ghi đè. Ở đây ta ghi đè (override) để phản ánh lịch sử mới nhất
        if extracted_preferences:
            db["Users"].update_one(
                {"userId": user_id},
                {"$set": {
                    "preferences": extracted_preferences, 
                    "last_update_trip_count": current_trips_count,
                    "updatedAt": datetime.utcnow()
                }}
            )
            return JsonResponse({
                "success": True,
                "message": "Cập nhật sở thích thành công.",
                "preferences": extracted_preferences
            })
        else:
            return JsonResponse({
                "success": True,
                "message": "Không tìm thấy dữ liệu lịch sử hoặc không thể suy luận thêm sở thích.",
                "preferences": user.get("preferences", [])
            })
            
    except Exception as exc:
        logger.error(f"Update preferences error: {exc}")
        return JsonResponse({"error": str(exc)}, status=500)

