from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from workflow.graph.stage import State
from workflow.db import get_neo4j_driver, get_mongo_db
from workflow.models.llm import LLM
from typing import List, Optional
from dotenv import load_dotenv
import os
import json

load_dotenv()

# ==========================================
# PYDANTIC MODELS
# ==========================================

class SelectedAccommodation(BaseModel):
    locationId: str = Field(description="ID của khách sạn được chọn từ Database Context")
    name: str = Field(description="Tên nơi ở")
    cost: int = Field(description="Giá một đêm cho một phòng (VNĐ)")
    ward_name: str = Field(description="Tên phường/xã nơi khách sạn tọa lạc")
    description: str = Field(description="Lý do chọn nơi ở này (VD: Gần biển, đúng budget, phù hợp gia đình), tối đa 15 chữ")
    img_url: Optional[str] = Field(default=None, description="Trường image_url của khách sạn từ Database Context (nếu có)")

class SelectedActivity(BaseModel):
    locationId: str = Field(description="ID của địa điểm được chọn từ Database Context")
    name: str = Field(description="Tên hoạt động / địa điểm")
    description: str = Field(description="Mô tả ngắn về hoạt động")
    estimated_duration_minutes: int = Field(description="Thời gian dự kiến (phút)")
    cost: int = Field(description="Chi phí dự kiến cho mỗi người (VNĐ)")
    suitability_for: List[str] = Field(description="Đối tượng phù hợp (VD: Family, Couples, Solo)")
    note: str = Field(description="Ghi chú thêm (VD: Nên đi buổi sáng, cần đặt trước), tối đa 15 chữ")
    img_url: Optional[str] = Field(default=None, description="Trường image_url của địa điểm từ Database Context (nếu có)")

class SelectedEatery(BaseModel):
    locationId: str = Field(description="ID của quán ăn từ Database Context")
    name: str = Field(description="Tên quán ăn")
    cost: int = Field(description="Giá trung bình mỗi người (VNĐ)")
    description: str = Field(description="Lý do chọn quán ăn này (VD: Đặc sản địa phương, phù hợp trẻ em), tối đa 15 chữ")
    img_url: Optional[str] = Field(default=None, description="Trường image_url của quán ăn từ Database Context (nếu có)")

class PlannerOutput(BaseModel):
    accommodation: List[SelectedAccommodation] = Field(description="Danh sách nơi ở được chọn.")
    activities: List[SelectedActivity] = Field(description="Danh sách hoạt động / địa điểm tham quan được chọn lọc.")
    eateries: List[SelectedEatery] = Field(description="Danh sách quán ăn được chọn.")

# ==========================================
# PROMPTS & CHAIN SETUP
# ==========================================

planner_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Bạn là Planner Agent chuyên nghiệp của hệ thống Traplanner.
    Nhiệm vụ: LỰA CHỌN và LỌC địa điểm từ DATABASE thực tế dưới đây — TUYỆT ĐỐI KHÔNG tự bịa ra địa điểm.

    [DATABASE CONTEXT — Dữ liệu thực từ hệ thống]
    - Khách sạn/Nơi lưu trú (Stay):   {db_hotels}
    - Địa điểm tham quan (Sightseeing/Entertainment/Culture): {db_activities}
    - Quán ăn/Nhà hàng (Food):         {db_eateries}

    [BƯỚC 1 — PHỄU LỌC CỨNG (Loại bỏ không khả thi)]
    Duyệt qua từng địa điểm và loại bỏ nếu vi phạm BẤT KỲ điều kiện nào:
    1. NGÂN SÁCH: Chọn ra một tập hợp các địa điểm (Ít nhất 1 Nơi ở, nhiều Hoạt động, nhiều Quán ăn) sao cho TỔNG CHI PHÍ không vượt quá NGÂN SÁCH ({total_budget} VND). 
       - Lưu ý 1: `estimatedPrice` của Khách sạn (Stay) là giá cho 1 phòng/đêm. Bạn BẮT BUỘC gán giá trị này vào trường `cost` của SelectedAccommodation, TUYỆT ĐỐI KHÔNG để cost = 0 cho khách sạn.
       - Lưu ý 2: `estimatedPrice` của Hoạt động/Quán ăn là giá cho 1 NGƯỜI, bạn phải nhân với số người (group_size).
       - TUYỆT ĐỐI KHÔNG BỎ TRỐNG NƠI Ở VÀ HOẠT ĐỘNG. Việc không trả về nơi lưu trú là một lỗi nghiêm trọng.
    2. SỨC KHỎE & THỂ LỰC: estimatedDuration quá dài hoặc địa điểm đòi hỏi thể lực không phù hợp với age_range, health_limitations.
    3. THỜI GIAN: Tổng thời gian các hoạt động trong ngày không vượt quá daily_active_hours.
    4. VÙNG CẤM: Địa điểm có tên xuất hiện trong places_of_limitation → loại bỏ.

    [BƯỚC 2 — ƯU TIÊN & CHẤM ĐIỂM (Sắp xếp khả thi)]
    Sau khi lọc, ưu tiên địa điểm dựa trên:
    1. NHỊP ĐỘ (travel_pace): "Thong thả" → chọn ít địa điểm hơn, thêm thời gian nghỉ. "Khám phá" → lịch trình dày đặc hơn.
    2. PHONG CÁCH (travel_style, atmosphere): Ưu tiên category khớp với sở thích (VD: "Văn hóa" → Culture/Sightseeing lên trước).
    3. ĐỐI TƯỢNG (companion_type, suitabilityFor): Ưu tiên địa điểm có suitabilityFor khớp companion_type (Family, Couples, Solo...).

    [YÊU CẦU ĐẦU RA]
    - Chọn 1 nơi lưu trú phù hợp nhất.
    - Chọn các hoạt động phù hợp nhất có thể. Nếu Database không có đủ địa điểm đáp ứng tiêu chí, HÃY CHỌN ÍT LẠI.
    - Chọn ít nhất 2 quán ăn đa dạng (sáng/trưa/tối).
    - Ghi rõ lý do chọn vào trường `note` của mỗi địa điểm.
    - CẢNH BÁO NGHIÊM TRỌNG: CHỈ chọn địa điểm có thật trong [DATABASE CONTEXT]. TUYỆT ĐỐI KHÔNG trả về các giá trị rác, dữ liệu mẫu như "string" hay tự bịa ra địa điểm. Nếu không có gì phù hợp, hãy trả về danh sách rỗng [].
    
    [RÀNG BUỘC PHẢN HỒI (VALIDATION FEEDBACK)]
    Nếu có feedback từ Validation Agent, bạn BẮT BUỘC phải thay đổi sự lựa chọn để khắc phục:
    {validation_feedback}
    
    Hãy tìm ra các địa điểm hoạt động, địa điểm ăn uống, chỗ ở, và các hoạt động khác phù hợp với yêu cầu chuyến đi của người dùng. Các thông tin về chuyến đi như sau:
    - Tổng Ngân Sách:      {total_budget} VNĐ
    - TripMetadata:        {trip_metadata}
    - TravelPreferences:   {travel_preferences}
    - Constraints:         {constraints}
    """)
])

llm = LLM(
    api_keys=[os.getenv("GOOGLE_API_KEY") or ""],
    temperature=0.5,
    max_tokens=8192,
    response_schema=PlannerOutput
)

# ==========================================
# DATABASE FETCH FUNCTIONS
# ==========================================

# Category groupings
STAY_CATS     = ["Stay"]
ACTIVITY_CATS = ["Sightseeing", "Entertainment", "Culture", "nature", "Activity"]
FOOD_CATS     = ["Food"]

PROJECTION = {
    "_id": 0,
    "locationId": 1,
    "name": 1,
    "category": 1,
    "estimatedDuration": 1,
    "estimatedPrice": 1,
    "suitabilityFor": 1,
    "openingHours": 1,
    "ward_name": 1,
    "img_url": 1,
}


def fetch_ward_names(destination: str) -> list[str]:
    """
    Query Neo4j to retrieve all Ward names under the given Province.
    Uses relationship: (Province {name: destination})-[:HAS]->(Ward)
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        results = session.run(
            """
            MATCH (p:Province {name: $destination})-[:HAS]->(w:Ward) 
            RETURN w.name AS ward_name
            UNION
            MATCH (w1:Ward {name: $destination})-[:CONNECTED_TO]-(w:Ward)
            RETURN w.name AS ward_name
            UNION
            MATCH (w:Ward {name: $destination})
            RETURN w.name AS ward_name
            """,
            destination=destination
        ).data()
    ward_names = [r["ward_name"] for r in results]
    return ward_names


def fetch_locations_from_mongo(ward_names: list[str], destinations: list[str] = None) -> dict:
    """
    Query MongoDB TravelDB.Locations filtered by ward_name list, split by category group.
    Returns dict with keys: hotels, activities, eateries.
    """
    db  = get_mongo_db("TravelDB")
    col = db["Locations"]
    query_base = {"ward_name": {"$in": ward_names}}

    hotels = list(col.find(
        {**query_base, "category": {"$in": STAY_CATS}}, PROJECTION
    ).limit(20))
    
    # Fallback: Mở rộng tìm kiếm khách sạn theo province_name nếu ward không có
    if not hotels and destinations:
        for dest in destinations:
            fallback_hotels = list(col.find(
                {
                    "$or": [
                        {"province_name": {"$regex": dest, "$options": "i"}},
                        {"ward_name": {"$regex": dest, "$options": "i"}}
                    ],
                    "category": {"$in": STAY_CATS}
                }, PROJECTION
            ).limit(10))
            if fallback_hotels:
                hotels = fallback_hotels
                break
    
    activities = list(col.find(
        {**query_base, "category": {"$in": ACTIVITY_CATS}}, PROJECTION
    ).limit(20))
    eateries = list(col.find(
        {**query_base, "category": {"$in": FOOD_CATS}}, PROJECTION
    ).limit(20))

    return {"hotels": hotels, "activities": activities, "eateries": eateries}


# ==========================================
# LANGGRAPH NODE FUNCTION
# ==========================================

def Planner_node(state: State) -> State:
    trip_metadata      = state.get("trip_metadata", {})
    travel_preferences = state.get("travel_preferences", {})
    constraints        = state.get("constraints", {})

    destinations = trip_metadata.get("destination", [])
    if isinstance(destinations, str):
        destinations = [destinations]
        
    ward_names = []
    for dest in destinations:
        if dest:
            dest = dest.split(",")[0].strip()
            ward_names.extend(fetch_ward_names(dest))
            
    ward_names = list(set(ward_names))
    db_context = fetch_locations_from_mongo(ward_names, destinations)
    
    # Không cho phép trả về mock data, nếu không tìm thấy dữ liệu thật thì phải báo lỗi
    if not db_context["hotels"]:
        raise ValueError(f"Lỗi: Không tìm thấy bất kỳ Nơi lưu trú nào tại {destinations}. Vui lòng thêm dữ liệu thực tế vào hệ thống.")
    if not db_context["activities"]:
        raise ValueError(f"Lỗi: Không tìm thấy bất kỳ Hoạt động tham quan nào tại {destinations}. Vui lòng thêm dữ liệu thực tế vào hệ thống.")
    if not db_context["eateries"]:
        raise ValueError(f"Lỗi: Không tìm thấy bất kỳ Quán ăn/Nhà hàng nào tại {destinations}. Vui lòng thêm dữ liệu thực tế vào hệ thống.")
    
    total_budget = state.get("total_budget") or constraints.get("travel_budget", 0)
    if isinstance(total_budget, str):
        import re
        nums = re.findall(r"[\d\.]+", total_budget.replace(",", ""))
        total_budget = float(nums[0]) if nums else 0.0
    
    feedback = state.get("validation_feedback", [])
    prompt_value = planner_prompt.format(
        validation_feedback=json.dumps(feedback, ensure_ascii=False) if feedback else "Không có",
        db_hotels=json.dumps(db_context["hotels"], ensure_ascii=False),
        db_activities=json.dumps(db_context["activities"], ensure_ascii=False),
        db_eateries=json.dumps(db_context["eateries"], ensure_ascii=False),
        trip_metadata=trip_metadata,
        travel_preferences=travel_preferences,
        constraints=constraints,
        total_budget=total_budget,
    )
    
    response_str = llm.invoke(prompt_value)
    response = PlannerOutput.model_validate_json(response_str)

    return {
        "accommodations": response.accommodation,
        "activities":    response.activities,
        "eateries":      response.eateries,
    }