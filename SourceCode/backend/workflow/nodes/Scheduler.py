"""
workflow/nodes/Scheduler.py

Scheduler Node — LLM-Based Day-by-Day Itinerary Planning.

Takes activities, accommodations, and transportations from previous nodes
and uses Gemini to logically distribute them into a day-by-day schedule.
"""

from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from workflow.graph.stage import State
from workflow.models.llm import LLM
from dotenv import load_dotenv
import os
import json

load_dotenv()


# ==========================================
# DATA MODELS (Strict for LLM Output)
# ==========================================

class ScheduleItem(BaseModel):
    time_start: str = Field(description="HH:MM (e.g. 07:00)")
    time_end: str = Field(description="HH:MM (e.g. 08:00)")
    type: str = Field(description="transportation, activity, accommodation, meal, or rest")
    name: str = Field(description="TÊN CHÍNH XÁC của địa điểm/nhà hàng từ Input Data")
    locationId: Optional[str] = Field(default=None, description="Trường locationId lấy từ Input Data (bắt buộc phải có nếu địa điểm có trong database)")
    location: str = Field(description="Địa chỉ hoặc vị trí")
    description: str = ""
    duration_minutes: int
    cost: int = 0
    notes: str = ""
    img_url: Optional[str] = Field(default=None, alias="image")

class DaySummary(BaseModel):
    total_cost: int = 0
    activities_count: int = 0
    meals_count: int = 0
    travel_time_hours: float = 0.0
    active_hours: float = 0.0
    rest_hours: float = 0.0
    highlights: List[str] = []
    energy_level: str = Field(description="low, moderate, high")

class DaySchedule(BaseModel):
    day: int = Field(description="Day number (1, 2, ...)")
    date: str = Field(description="YYYY-MM-DD")
    title: str = Field(description="Day title")
    items: List[ScheduleItem]
    day_summary: DaySummary

class SchedulingOutput(BaseModel):
    scheduling: List[DaySchedule]


# ==========================================
# PROMPTS & LLM SETUP
# ==========================================

scheduler_prompt = ChatPromptTemplate.from_messages([
    ("system", """Bạn là Chuyên gia Lên Lịch Trình (Scheduler Agent).
Nhiệm vụ: Sắp xếp các địa điểm đã được chọn thành một lịch trình chi tiết từng ngày, liên tục từ sáng đến tối.

[INPUT DATA]
- Chỗ ở (Accommodations): {accommodations}
- Hoạt động (Activities): {activities}
- Quán ăn (Eateries): {eateries}
- Di chuyển (Transportations): {transportations}

[QUY TẮC LÊN LỊCH]
1. Luồng 1 ngày cơ bản: Sáng thức dậy -> Ăn sáng (45-60p) -> Tham quan -> Ăn trưa (45-60p) -> Tham quan -> Ăn tối (60-75p) -> Tham quan buổi tối / Vui chơi tự do -> Về Khách sạn ngủ (22:00 - 08:00).
2. Thời gian: Các hoạt động phải nối tiếp nhau hợp lý. Cần tính thêm thời gian di chuyển (15-30p) giữa các địa điểm.
3. Di chuyển liên tỉnh (Transportation): Nếu điểm xuất phát ({start_location}) khác điểm đến ({destination}), Bạn BẮT BUỘC PHẢI tạo hoạt động di chuyển (Xe khách, Tàu hỏa, Máy bay) làm HOẠT ĐỘNG ĐẦU TIÊN của Ngày 1 (từ {start_location} đến {destination}) và HOẠT ĐỘNG CUỐI CÙNG của Ngày cuối cùng (từ {destination} về {start_location}). Hãy tự ước lượng chi phí hợp lý (VD: Xe limousine 200000).
4. Chỗ ở (Accommodation): SAU KHI di chuyển đến nơi, BẮT BUỘC tạo hoạt động "Check-in khách sạn: [Tên]" vào Ngày 1. Khách sạn phải lấy từ danh sách Accommodations. TUYỆT ĐỐI KHÔNG ĐỂ cost = 0. Bạn BẮT BUỘC phải lấy giá trị `cost` của khách sạn đó nhân với số đêm để gán vào trường `cost` của hoạt động Check-in này.
5. Hoạt động (Activities): Phân bổ TẤT CẢ hoạt động được cung cấp vào các ngày sao cho hợp lý nhất. Đừng bỏ sót.
6. Bữa ăn (Meals): BẮT BUỘC CHỌN Quán ăn (Eateries) từ Input Data. TUYỆT ĐỐI KHÔNG ghi "Tự túc tìm quán ăn".
   - Trường `name` BẮT BUỘC phải là TÊN CHÍNH XÁC CỦA QUÁN ĂN (VD: "Mì Quảng Bà Mua"). Không được đặt tên chung chung như "Ăn trưa" hay "Ăn tối".
   - Trường `description` có thể ghi rõ là ăn sáng/trưa/tối.
7. Dữ liệu gốc (Chi phí, Hình ảnh, ID): BẮT BUỘC copy chính xác `cost`, `img_url` và `locationId` của activities/accommodations/eateries từ Input Data sang Output. TUYỆT ĐỐI KHÔNG để trống `locationId` và `img_url` nếu Input có.
8. TỔNG KẾT NGÀY (day_summary): Bạn BẮT BUỘC phải tạo object `day_summary` với các trường sau, không được bỏ sót:
   - `total_cost`: Tổng TẤT CẢ `cost` của các mục trong ngày. TUYỆT ĐỐI KHÔNG ĐỂ 0 nếu có chi phí.
   - `activities_count`, `meals_count`: Tổng số hoạt động và bữa ăn.
   - `travel_time_hours`: Tổng thời gian di chuyển giữa các địa điểm (giờ, VD: 1.5).
   - `active_hours`: Tổng thời gian tham quan, vui chơi, ăn uống.
   - `rest_hours`: Tổng thời gian ngủ và nghỉ ngơi tại khách sạn.
9. KHÔNG TỰ BỊA ĐỊA ĐIỂM THAM QUAN: CHỈ sử dụng các địa điểm tham quan có trong Input Data.

[RÀNG BUỘC PHẢN HỒI (VALIDATION FEEDBACK)]
Nếu có feedback điều chỉnh lịch trình, hãy tuân thủ nghiêm ngặt nó: {validation_feedback}
"""),
    ("human", """
Hãy lên lịch trình cho {total_days} ngày.
Ngày bắt đầu: {start_date}
Phong cách đi: {travel_pace}
""")
])

llm = LLM(
    api_keys=[os.getenv("GOOGLE_API_KEY") or ""],
    temperature=0.2, # Low temperature cho tư duy logic
    max_tokens=8192,
    response_schema=SchedulingOutput
)


# ==========================================
# MAIN SCHEDULER NODE
# ==========================================

def scheduler_node(state: dict) -> dict:
    import logging
    log = logging.getLogger(__name__)
    
    trip_metadata = state.get("trip_metadata", {})
    travel_preferences = state.get("travel_preferences", {})
    feedback = state.get("validation_feedback", [])
    
    # Gom dữ liệu từ các Node trước
    activities = state.get("activities", state.get("activity", []))
    accommodations = state.get("accommodations", state.get("accommodation", []))
    eateries = state.get("eateries", [])
    transportations = state.get("transportations", [])
    
    def _to_dict(obj):
        if isinstance(obj, dict): return obj
        try: return obj.model_dump()
        except AttributeError: pass
        try: return dict(obj)
        except (TypeError, ValueError): pass
        return obj
        
    activities = [_to_dict(a) for a in activities]
    accommodations = [_to_dict(a) for a in accommodations]
    eateries = [_to_dict(e) for e in eateries]
    transportations = [_to_dict(t) for t in transportations]
    
    start_date_str = trip_metadata.get("start_date", "2026-06-01")
    total_days = int(trip_metadata.get("total_days", 3))
    travel_pace = ", ".join(travel_preferences.get("travel_pace", ["Bình thường"]))
    
    destination = trip_metadata.get("destination", "Điểm đến")
    if isinstance(destination, list) and destination:
        destination = destination[0]
        
    start_location = trip_metadata.get("start_location", "Nơi xuất phát")
    if isinstance(start_location, list) and start_location:
        start_location = start_location[0]
    
    # ── Call LLM to schedule ────────────────────────────────────────────────
    log.info(f"Scheduling {total_days} days using LLM...")
    prompt_value = scheduler_prompt.format(
        accommodations=json.dumps(accommodations, ensure_ascii=False),
        activities=json.dumps(activities, ensure_ascii=False),
        eateries=json.dumps(eateries, ensure_ascii=False),
        transportations=json.dumps(transportations, ensure_ascii=False),
        validation_feedback=json.dumps(feedback, ensure_ascii=False) if feedback else "Không có",
        total_days=total_days,
        start_date=start_date_str,
        travel_pace=travel_pace,
        start_location=start_location,
        destination=destination
    )
    
    response_str = llm.invoke(prompt_value)
    
    try:
        response = SchedulingOutput.model_validate_json(response_str)
        # Convert Pydantic Object về List[Dict] để State graph xử lý dễ dàng
        state["scheduling"] = [day.model_dump() for day in response.scheduling]
        state["validation_feedback"] = [] # Clear feedback loop
    except Exception as e:
        log.error(f"Error parsing LLM schedule output: {e}")
        state["scheduling"] = []
    
    return state


# Alias used by the graph builder
scheduling_node = scheduler_node
