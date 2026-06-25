"""
chatbot/tools.py
LangChain tools for the Traplanner travel advisor agent.

Tools available:
  - get_trip_details           : fetch trip + day-detail from MongoDB
  - search_alternative_hotels  : find alternative hotels (Neo4j + MongoDB)
  - search_alternative_restaurants : find alternative restaurants (Neo4j + MongoDB)
  - search_alternative_attractions : find attractions / activities (Neo4j + MongoDB)
  - search_transport_options   : find transport alternatives (Neo4j)
  - calculate_trip_budget      : compute cost breakdown from trip data
  - search_destination_info    : Google Custom Search for images + URL
  - summarize_conversation     : summarise chat history for memory
  - classify_query_type        : classify if retrieval is needed
  - direct_response            : generate a quick direct reply (no DB needed)
  - update_trip_activity       : update an existing activity in the trip
  - add_new_activity           : add a new activity to the trip
  - remove_activity            : remove an activity from the trip
"""

import os
import json
from .llm import CHATBOT_MODEL
import logging
import re
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory
import requests

from .db import (
    get_full_trip_context,
    get_trips_for_user,
    neo4j_find_alternative_hotels,
    neo4j_find_alternative_restaurants,
    neo4j_find_attractions,
    neo4j_find_transportation,
    get_locations_by_category,
    search_locations,
    add_activity_to_day,
    remove_activity_from_day,
    update_activity_in_day,
)

logger = logging.getLogger(__name__)

# ── Gemini model (for tool-internal LLM calls) ────────────────────────────────
_generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "max_output_tokens": 4096,
}
_safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

_gemini_model = genai.GenerativeModel(
    model_name=CHATBOT_MODEL,
    generation_config=_generation_config,
    safety_settings=_safety_settings,
)


def _call_gemini(prompt: str) -> str:
    """Helper: call Gemini and return the text response."""
    try:
        response = _gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.error(f"Gemini call failed: {exc}")
        return ""


def _format_vnd(amount: float) -> str:
    return f"{amount:,.0f} VNĐ"


# ── Tool 1: Trip details ───────────────────────────────────────────────────────

@tool
def get_trip_details(trip_id: str) -> Dict[str, Any]:
    """
    Lấy chi tiết đầy đủ của một kế hoạch du lịch từ MongoDB (bao gồm thông tin
    chuyến đi và lịch trình chi tiết từng ngày).

    Args:
        trip_id: ID của chuyến đi (trường 'tripId' trong collection Trips)

    Returns:
        Dict chứa 'trip' (thông tin tổng quan) và 'day_details' (lịch trình từng ngày).
    """
    logger.info(f"[Tool] get_trip_details: trip_id={trip_id}")
    ctx = get_full_trip_context(trip_id)
    if not ctx:
        return {"error": f"Không tìm thấy chuyến đi với ID: {trip_id}"}
    return ctx


# ── Tool 2: Alternative hotels ────────────────────────────────────────────────

@tool
def search_alternative_hotels(destination: str, max_price_per_night: float = 2000000.0,
                               limit: int = 5) -> List[Dict[str, Any]]:
    """
    Tìm kiếm các khách sạn thay thế tại điểm đến từ Neo4j và MongoDB.

    Args:
        destination: Tên thành phố / điểm đến
        max_price_per_night: Giá phòng tối đa mỗi đêm (VNĐ)
        limit: Số kết quả tối đa

    Returns:
        Danh sách khách sạn phù hợp với tên, giá, hạng sao, địa chỉ.
    """
    logger.info(f"[Tool] search_alternative_hotels: dest={destination}, max={max_price_per_night}")

    # Fetch directly from MongoDB Locations
    mongo_results = get_locations_by_category("Stay", destination, limit)
    results = []
    for loc in mongo_results:
        price = loc.get("estimatedPrice", 0)
        if price <= max_price_per_night:
            results.append({
                "name": loc.get("name", ""),
                "address": loc.get("address", loc.get("ward_name", "")),
                "price": f"{price:,.0f} VNĐ" if price > 0 else loc.get("price_range", "Liên hệ"),
                "description": loc.get("description", ""),
            })
            if len(results) >= limit:
                break

    if not results:
        return [{"message": f"Không tìm thấy khách sạn phù hợp tại {destination} trong ngân sách."}]

    return results


# ── Tool 3: Alternative restaurants ──────────────────────────────────────────

@tool
def search_alternative_restaurants(destination: str, cuisine_type: str = "",
                                    max_price_per_person: float = 300_000,
                                    limit: int = 5) -> List[Dict[str, Any]]:
    """
    Tìm kiếm các nhà hàng / quán ăn thay thế tại điểm đến.

    Args:
        destination: Tên thành phố / điểm đến
        cuisine_type: Loại ẩm thực (ví dụ: 'hải sản', 'bbq', 'chay', …)
        max_price_per_person: Giá bữa ăn tối đa mỗi người (VNĐ)
        limit: Số kết quả tối đa

    Returns:
        Danh sách nhà hàng với tên, loại ẩm thực, giá trung bình, địa chỉ.
    """
    logger.info(f"[Tool] search_alternative_restaurants: dest={destination}, cuisine={cuisine_type}")

    category_key = cuisine_type if cuisine_type else "Food"
    mongo_results = get_locations_by_category(category_key, destination, limit)
    results = []
    for loc in mongo_results:
        price = loc.get("estimatedPrice", 0)
        if price <= max_price_per_person:
            results.append({
                "name": loc.get("name", ""),
                "address": loc.get("address", loc.get("ward_name", "")),
                "cuisine": cuisine_type or "Đa dạng",
                "avg_price": f"{price:,.0f} VNĐ" if price > 0 else loc.get("price_range", "Liên hệ"),
            })
            if len(results) >= limit:
                break

    if not results:
        return [{"message": f"Không tìm thấy nhà hàng phù hợp tại {destination}."}]

    return results


# ── Tool 4: Alternative attractions ──────────────────────────────────────────

@tool
def search_alternative_attractions(destination: str, activity_type: str = "",
                                    limit: int = 5) -> List[Dict[str, Any]]:
    """
    Tìm kiếm các địa điểm tham quan / hoạt động vui chơi tại điểm đến.

    Args:
        destination: Tên thành phố / điểm đến
        activity_type: Loại hoạt động (ví dụ: 'bãi biển', 'núi', 'bảo tàng', 'giải trí')
        limit: Số kết quả tối đa

    Returns:
        Danh sách địa điểm với tên, loại, giá vé, mô tả, địa chỉ.
    """
    logger.info(f"[Tool] search_alternative_attractions: dest={destination}, type={activity_type}")

    mongo_results = get_locations_by_category(
        activity_type or "Activity", destination, limit
    )
    results = []
    for loc in mongo_results:
        price = loc.get("estimatedPrice", 0)
        results.append({
            "name": loc.get("name", ""),
            "address": loc.get("address", loc.get("ward_name", "")),
            "type": activity_type or "Tham quan",
            "entry_fee": f"{price:,.0f} VNĐ" if price > 0 else loc.get("price_range", "Miễn phí"),
            "description": loc.get("description", ""),
        })
        if len(results) >= limit:
            break

    if not results:
        return [{"message": f"Không tìm thấy địa điểm phù hợp tại {destination}."}]

    return results


# ── Tool 5: Transport options ─────────────────────────────────────────────────

@tool
def search_transport_options(from_city: str, to_city: str,
                              transport_type: str = "",
                              limit: int = 5) -> List[Dict[str, Any]]:
    """
    Tìm kiếm các phương tiện di chuyển giữa hai thành phố.

    Args:
        from_city: Thành phố xuất phát
        to_city: Thành phố đến
        transport_type: Loại phương tiện ('máy bay', 'tàu hỏa', 'xe khách', 'xe máy', …)
        limit: Số kết quả tối đa

    Returns:
        Danh sách các phương tiện với loại, nhà cung cấp, thời gian, giá.
    """
    logger.info(f"[Tool] search_transport_options: {from_city} → {to_city}, type={transport_type}")

    results = neo4j_find_transportation(from_city, to_city, transport_type, limit)

    if not results:
        return [{
            "message": f"Không tìm thấy thông tin phương tiện từ {from_city} đến {to_city} trong cơ sở dữ liệu.",
            "suggestion": "Bạn có thể tham khảo các website đặt vé như Vexere.com, BabaGo.vn, hoặc hãng bay Vietnam Airlines, Vietjet."
        }]

    return results


# ── Tool 6: Budget calculation ────────────────────────────────────────────────

@tool
def calculate_trip_budget(trip_id: str) -> Dict[str, Any]:
    """
    Tính toán và phân tích chi phí chi tiết của kế hoạch du lịch.

    Args:
        trip_id: ID của chuyến đi

    Returns:
        Dict chứa tổng chi phí, chi phí theo ngày, phân loại theo loại hoạt động.
    """
    logger.info(f"[Tool] calculate_trip_budget: trip_id={trip_id}")

    ctx = get_full_trip_context(trip_id)
    if not ctx:
        return {"error": f"Không tìm thấy chuyến đi: {trip_id}"}

    trip = ctx.get("trip", {})
    day_details = ctx.get("day_details", [])

    total_budget = trip.get("totalBudget", 0)
    breakdown: Dict[str, float] = {
        "accommodation": 0.0,
        "food": 0.0,
        "transport": 0.0,
        "sightseeing": 0.0,
        "other": 0.0,
    }
    daily_costs: List[Dict[str, Any]] = []
    grand_total = 0.0

    for day in day_details:
        day_total = 0.0
        for act in day.get("dayActs", []):
            price = float(act.get("price", 0))
            act_type = act.get("type", "other").lower()
            day_total += price
            grand_total += price

            if act_type in ("stay", "accommodation"):
                breakdown["accommodation"] += price
            elif act_type in ("food", "meal"):
                breakdown["food"] += price
            elif act_type in ("transport", "transportation"):
                breakdown["transport"] += price
            elif act_type in ("sightseeing", "activity"):
                breakdown["sightseeing"] += price
            else:
                breakdown["other"] += price

        daily_costs.append({
            "day": day.get("dayNumber"),
            "date": day.get("date", ""),
            "total": day_total,
            "total_formatted": _format_vnd(day_total),
        })

    remaining = total_budget - grand_total

    return {
        "trip_id": trip_id,
        "destination": trip.get("destination", ""),
        "total_budget": total_budget,
        "total_budget_formatted": _format_vnd(total_budget),
        "total_spent": grand_total,
        "total_spent_formatted": _format_vnd(grand_total),
        "remaining_budget": remaining,
        "remaining_budget_formatted": _format_vnd(remaining),
        "budget_usage_percent": round(grand_total / total_budget * 100, 1) if total_budget else 0,
        "breakdown": {k: {"amount": v, "formatted": _format_vnd(v)}
                      for k, v in breakdown.items()},
        "daily_costs": daily_costs,
    }


# ── Tool 7: Destination info (Google Custom Search) ───────────────────────────

@tool
def search_destination_info(place_name: str, location_context: str = "") -> Dict[str, Any]:
    """
    Tìm kiếm thông tin, hình ảnh và đường link về một địa điểm du lịch cụ thể
    bằng Google Custom Search API.

    Args:
        place_name: Tên địa điểm cần tìm (ví dụ: 'Bãi biển Mỹ Khê', 'Cầu Rồng Đà Nẵng')
        location_context: Ngữ cảnh vị trí bổ sung (ví dụ: 'Đà Nẵng')

    Returns:
        Dict chứa 'description', 'images' (list URL), 'url' (link tham khảo chính).
    """
    logger.info(f"[Tool] search_destination_info: place={place_name}, ctx={location_context}")

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    cse_id = os.environ.get("GOOGLE_CSE_ID", "")

    query = f"{place_name} {location_context} địa điểm du lịch".strip()
    images: List[str] = []
    url = ""
    description = ""

    # ── Text search ──────────────────────────────────────────────────────────
    if api_key and cse_id:
        try:
            text_resp = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": api_key,
                    "cx": cse_id,
                    "q": query,
                    "num": 3,
                },
                timeout=10,
            )
            text_data = text_resp.json()
            items = text_data.get("items", [])
            if items:
                top = items[0]
                url = top.get("link", "")
                description = top.get("snippet", "")
        except Exception as exc:
            logger.warning(f"Google text search failed: {exc}")

        # ── Image search ──────────────────────────────────────────────────────
        try:
            img_resp = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": api_key,
                    "cx": cse_id,
                    "q": query,
                    "searchType": "image",
                    "num": 3,
                    "imgSize": "LARGE",
                },
                timeout=10,
            )
            img_data = img_resp.json()
            images = [
                item.get("link", "")
                for item in img_data.get("items", [])
                if item.get("link")
            ]
        except Exception as exc:
            logger.warning(f"Google image search failed: {exc}")
    else:
        logger.warning("GOOGLE_API_KEY or GOOGLE_CSE_ID not set — skipping search.")
        description = f"Chưa cấu hình Google Search API. Không thể tìm thêm thông tin về {place_name}."

    # ── Enrich description with Gemini if short ───────────────────────────────
    if len(description) < 100:
        gemini_desc = _call_gemini(
            f"Mô tả ngắn gọn (3-5 câu) bằng tiếng Việt về địa điểm du lịch: "
            f"'{place_name}' ở {location_context or 'Việt Nam'}. "
            "Nêu điểm nổi bật, hoạt động và thời điểm tốt nhất để ghé thăm."
        )
        if gemini_desc:
            description = gemini_desc

    return {
        "place_name": place_name,
        "description": description,
        "images": images[:3],
        "url": url,
        "search_query": query,
    }


# ── Tool 8: Summarise conversation ────────────────────────────────────────────

@tool
def summarize_conversation(messages: List[str],
                            trip_destination: str = "") -> str:
    """
    Tóm tắt cuộc hội thoại để lưu vào Redis (bộ nhớ ngắn hạn).

    Args:
        messages: Danh sách nội dung tin nhắn cần tóm tắt
        trip_destination: Điểm đến của chuyến đi (ngữ cảnh bổ sung)

    Returns:
        Chuỗi tóm tắt ngắn gọn.
    """
    logger.info("[Tool] summarize_conversation")
    if not messages:
        return "Chưa có nội dung hội thoại."

    conversation_text = "\n".join(messages[-15:])
    prompt = f"""Tóm tắt ngắn gọn cuộc hội thoại về kế hoạch du lịch dưới đây trong 3-5 câu.
Ghi lại các thông tin quan trọng: câu hỏi của người dùng, gợi ý đã đưa ra, thay đổi đề xuất.
Điểm đến: {trip_destination or 'chưa xác định'}

Cuộc hội thoại:
{conversation_text}

Tóm tắt:"""
    summary = _call_gemini(prompt)
    return summary or "Cuộc hội thoại về kế hoạch du lịch."


# ── Action tools: Modify Trip ────────────────────────────────────────────────

@tool
def update_trip_activity(trip_id: str, day_number: int, old_activity_name: str, new_activity_name: str, new_activity_type: str, new_activity_price: int) -> str:
    """
    Thay thế/cập nhật một hoạt động trong lịch trình (Sửa đổi trực tiếp vào Database).
    
    Args:
        trip_id: ID chuyến đi
        day_number: Ngày số mấy (1, 2, ...)
        old_activity_name: Tên hoạt động cũ cần thay thế
        new_activity_name: Tên hoạt động mới
        new_activity_type: Loại (stay, eat, transport, activity, v.v.)
        new_activity_price: Chi phí ước tính (VNĐ)
    """
    logger.info(f"[Tool] update_trip_activity: {trip_id} day {day_number} - {old_activity_name} -> {new_activity_name}")
    
    # Auto-detect locationId from Locations collection
    from .db import get_travel_db
    db = get_travel_db()
    
    clean_name = new_activity_name
    prefixes = ["Check-in ", "Ăn trưa tại ", "Ăn tối tại ", "Ăn sáng tại ", "Di chuyển đến ", "Thăm quan "]
    for p in prefixes:
        if clean_name.lower().startswith(p.lower()):
            clean_name = clean_name[len(p):].strip()

    loc = db["Locations"].find_one({"name": {"$regex": clean_name, "$options": "i"}})
    location_id = loc.get("locationId", "") if loc else ""
    image_url = loc.get("image_url", loc.get("image", "")) if loc else ""

    new_act = {
        "name": new_activity_name,
        "type": new_activity_type,
        "price": new_activity_price,
        "startTime": "", 
        "endTime": "",
        "note": "Đã được cập nhật bởi Travel Bot"
    }
    
    if location_id:
        new_act["locationId"] = location_id
    if image_url:
        new_act["image"] = image_url

    success = update_activity_in_day(trip_id, day_number, old_activity_name, new_act)
    if success:
        return f"Thành công! Đã thay đổi '{old_activity_name}' thành '{new_activity_name}' trong Ngày {day_number}."
    return f"Lỗi: Không tìm thấy '{old_activity_name}' trong Ngày {day_number} hoặc không thể lưu."

@tool
def add_new_activity(trip_id: str, day_number: int, activity_name: str, activity_type: str, activity_price: int, start_time: str = "") -> str:
    """
    Thêm một hoạt động hoàn toàn mới vào lịch trình của một ngày (Sửa đổi trực tiếp vào Database).
    
    Args:
        trip_id: ID chuyến đi
        day_number: Ngày số mấy
        activity_name: Tên hoạt động mới
        activity_type: Loại hoạt động (stay, eat, transport, activity)
        activity_price: Chi phí ước tính (VNĐ)
        start_time: Giờ dự kiến (vd: 14:00)
    """
    logger.info(f"[Tool] add_new_activity: {trip_id} day {day_number} + {activity_name}")
    new_act = {
        "name": activity_name,
        "type": activity_type,
        "price": activity_price,
        "startTime": start_time,
        "endTime": "",
        "note": "Đã thêm bởi Travel Bot"
    }
    success = add_activity_to_day(trip_id, day_number, new_act)
    if success:
        return f"Thành công! Đã thêm '{activity_name}' vào Ngày {day_number}."
    return f"Lỗi: Không thể thêm hoạt động vào Ngày {day_number}."

@tool
def remove_activity(trip_id: str, day_number: int, activity_name: str) -> str:
    """
    Xóa một hoạt động khỏi lịch trình (Sửa đổi trực tiếp vào Database).
    
    Args:
        trip_id: ID chuyến đi
        day_number: Ngày số mấy
        activity_name: Tên hoạt động cần xóa
    """
    logger.info(f"[Tool] remove_activity: {trip_id} day {day_number} - {activity_name}")
    success = remove_activity_from_day(trip_id, day_number, activity_name)
    if success:
        return f"Thành công! Đã xóa '{activity_name}' khỏi Ngày {day_number}."
    return f"Lỗi: Không tìm thấy '{activity_name}' trong Ngày {day_number} để xóa."

@tool 
def update_transport_options(trip_id: str, day_number: int, old_transport: str, new_transport: str, new_price: int) -> str:
    """
    Thay thế/cập nhật phương tiện di chuyển trong lịch trình (Sửa đổi trực tiếp vào Database).
    
    Args:
        trip_id: ID chuyến đi
        day_number: Ngày số mấy (1, 2, ...)
        old_transport: Tên phương tiện cũ cần thay thế
        new_transport: Tên phương tiện mới
        new_price: Chi phí ước tính (VNĐ)
    """
    logger.info(f"[Tool] update_transport_options: {trip_id} day {day_number} - {old_transport} -> {new_transport}")
    new_act = {
        "name": new_transport,
        "type": "Transport",
        "price": new_price,
        "startTime": "", 
        "endTime": "",
        "note": "Đã cập nhật phương tiện bởi Travel Bot"
    }
    success = update_activity_in_day(trip_id, day_number, old_transport, new_act)
    if success:
        return f"Thành công! Đã thay đổi phương tiện từ '{old_transport}' thành '{new_transport}' trong Ngày {day_number}."
    return f"Lỗi: Không tìm thấy phương tiện '{old_transport}' trong Ngày {day_number} hoặc không thể lưu."

# ── Tool 9: Classify query ────────────────────────────────────────────────────

@tool
def classify_query_type(user_query: str) -> Dict[str, Any]:
    """
    Phân loại câu hỏi của người dùng để xác định luồng xử lý.

    Args:
        user_query: Câu hỏi của người dùng

    Returns:
        Dict với 'needs_retrieval' (bool), 'query_type' (str), 'confidence' (float).
    """
    logger.info(f"[Tool] classify_query_type: '{user_query[:80]}'")

    normalized = user_query.lower().strip()

    # Greeting patterns
    greeting_patterns = [
        r"^(xin\s+chào|chào|hello|hi|hey|hế\s*lô|alo)\s*[!.]*$",
    ]
    for p in greeting_patterns:
        if re.search(p, normalized):
            return {"needs_retrieval": False, "query_type": "greeting", "confidence": 0.95}

    # Farewell
    farewell_patterns = [
        r"^(tạm\s+biệt|bye|goodbye|hẹn\s+gặp|see\s+you)\s*[!.]*$",
    ]
    for p in farewell_patterns:
        if re.search(p, normalized):
            return {"needs_retrieval": False, "query_type": "farewell", "confidence": 0.95}

    # General thanks / acks
    ack_patterns = [
        r"^(cảm\s+ơn|thank|ok|okay|được\s+rồi|tốt|hiểu\s+rồi)\s*[!.]*$",
    ]
    for p in ack_patterns:
        if re.search(p, normalized):
            return {"needs_retrieval": False, "query_type": "general_chat", "confidence": 0.90}

    # Trip-related keywords → retrieval needed
    travel_keywords = [
        "khách sạn", "nhà hàng", "ăn", "địa điểm", "hoạt động", "vé",
        "phương tiện", "di chuyển", "lịch trình", "ngày", "chi phí",
        "ngân sách", "hotel", "restaurant", "transport", "itinerary",
        "schedule", "budget", "day", "activity", "thay đổi", "gợi ý",
        "hình ảnh", "ảnh", "link", "tìm", "đề xuất", "giá",
    ]
    if any(kw in normalized for kw in travel_keywords):
        return {"needs_retrieval": True, "query_type": "trip_query", "confidence": 0.90}

    # Use Gemini for ambiguous cases
    try:
        prompt = f"""Phân loại câu hỏi sau (liên quan đến chatbot tư vấn du lịch):
Câu hỏi: "{user_query}"

Phân loại:
- "greeting": Chào hỏi đơn giản
- "farewell": Tạm biệt
- "general_chat": Trò chuyện chung, không cần tra cứu
- "trip_query": Câu hỏi cần truy vấn dữ liệu chuyến đi / địa điểm

Trả về JSON: {{"needs_retrieval": bool, "query_type": str, "confidence": float}}
Chỉ trả về JSON, không giải thích."""
        resp = _call_gemini(prompt)
        resp = resp.replace("```json", "").replace("```", "").strip()
        result = json.loads(resp)
        if isinstance(result.get("needs_retrieval"), bool):
            return result
    except Exception:
        pass

    return {"needs_retrieval": True, "query_type": "trip_query", "confidence": 0.5}


# ── Tool 10: Direct response ──────────────────────────────────────────────────

@tool
def direct_response(user_query: str, query_type: str = "general_chat") -> str:
    """
    Tạo câu trả lời trực tiếp cho các câu hỏi không cần tra cứu dữ liệu
    (chào hỏi, tạm biệt, trò chuyện chung).

    Args:
        user_query: Câu hỏi / tin nhắn của người dùng
        query_type: Loại câu hỏi ('greeting', 'farewell', 'general_chat')

    Returns:
        Câu trả lời phù hợp.
    """
    logger.info(f"[Tool] direct_response: type={query_type}")

    import random

    if query_type == "greeting":
        greetings = [
            "Xin chào! 👋 Tôi là Travel Bot – trợ lý du lịch AI của Traplanner. Tôi có thể giúp gì cho bạn về chuyến đi hôm nay?",
            "Chào bạn! 😊 Rất vui được hỗ trợ bạn lên kế hoạch du lịch. Bạn cần tư vấn gì không?",
            "Xin chào! 🌏 Tôi sẵn sàng giúp bạn khám phá và tối ưu hành trình du lịch của mình!",
        ]
        return random.choice(greetings)

    if query_type == "farewell":
        farewells = [
            "Tạm biệt! 👋 Chúc bạn có một chuyến đi thật vui và ý nghĩa! 🌟",
            "Hẹn gặp lại! 😊 Chúc bạn trải nghiệm những kỷ niệm đáng nhớ trong chuyến hành trình!",
            "Tạm biệt và chúc bạn du lịch vui vẻ! Nếu cần tư vấn thêm, tôi luôn ở đây! 🏖️",
        ]
        return random.choice(farewells)

    normalized = user_query.lower()
    if "cảm ơn" in normalized or "thank" in normalized:
        return "Không có gì! 😊 Tôi rất vui khi được hỗ trợ bạn. Nếu có câu hỏi nào thêm về chuyến đi, cứ hỏi nhé!"

    if "ok" in normalized or "được rồi" in normalized or "hiểu rồi" in normalized:
        return "Tốt! 👍 Nếu bạn cần thêm thông tin gì về lịch trình hoặc địa điểm, tôi luôn sẵn sàng hỗ trợ!"

    # Fallback – use Gemini
    resp = _call_gemini(
        f"Bạn là Travel Bot, trợ lý du lịch thân thiện. Trả lời ngắn gọn câu sau "
        f"theo phong cách thân thiện, chuyên nghiệp:\n\"{user_query}\""
    )
    return resp or "Tôi có thể giúp gì thêm cho bạn về chuyến đi không? 😊"
