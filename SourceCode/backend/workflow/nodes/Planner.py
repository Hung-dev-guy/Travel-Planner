from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from workflow.graph.stage import State
from workflow.db import get_neo4j_driver, get_mongo_db
from workflow.models.llm import LLM
from typing import List
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
    price_per_night: int = Field(description="Giá một đêm (VNĐ)")
    ward_name: str = Field(description="Tên phường/xã nơi khách sạn tọa lạc")
    description: str = Field(description="Lý do chọn nơi ở này (VD: Gần biển, đúng budget, phù hợp gia đình)")

class SelectedActivity(BaseModel):
    locationId: str = Field(description="ID của địa điểm được chọn từ Database Context")
    name: str = Field(description="Tên hoạt động / địa điểm")
    description: str = Field(description="Mô tả ngắn về hoạt động")
    estimated_duration_minutes: int = Field(description="Thời gian dự kiến (phút)")
    estimated_cost: int = Field(description="Chi phí dự kiến (VNĐ)")
    suitability_for: List[str] = Field(description="Đối tượng phù hợp (VD: Family, Couples, Solo)")
    note: str = Field(description="Ghi chú thêm (VD: Nên đi buổi sáng, cần đặt trước)")

class SelectedEatery(BaseModel):
    locationId: str = Field(description="ID của quán ăn từ Database Context")
    name: str = Field(description="Tên quán ăn")
    price_per_person: int = Field(description="Giá trung bình mỗi người (VNĐ)")
    description: str = Field(description="Lý do chọn quán ăn này (VD: Đặc sản địa phương, phù hợp trẻ em)")

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
    1. NGÂN SÁCH: (estimatedPrice * group_size) vượt quá phần ngân sách còn lại (travel_budget). Chú ý: estimatedPrice trong database là giá CHO 1 NGƯỜI, bạn phải nhân với số người (group_size).
    2. SỨC KHỎE & THỂ LỰC: estimatedDuration quá dài hoặc địa điểm đòi hỏi thể lực không phù hợp với age_range, health_limitations, mobility_limitations.
    3. THỜI GIAN: Tổng thời gian các hoạt động trong ngày không vượt quá daily_active_hours.
    4. VÙNG CẤM: Địa điểm có tên xuất hiện trong places_of_limitation → loại bỏ.
    5. NHÓM: Địa điểm không phù hợp group_size (VD: tour ghép giới hạn số người).

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
    """),
        ("human", """
    Hãy tìm ra các địa điểm hoạt động, địa điểm ăn uống, chỗ ở, và các hoạt động khác phù hợp với yêu cầu chuyến đi của người dùng. Các thông tin về chuyến đi như sau:
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
ACTIVITY_CATS = ["Sightseeing", "Entertainment", "Culture"]
FOOD_CATS     = ["Food"]

PROJECTION = {
    "_id": 0,
    "locationId": 1,
    "name": 1,
    "description": 1,
    "category": 1,
    "estimatedDuration": 1,
    "estimatedPrice": 1,
    "suitabilityFor": 1,
    "openingHours": 1,
    "ward_name": 1,
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


def fetch_locations_from_mongo(ward_names: list[str]) -> dict:
    """
    Query MongoDB TravelDB.Locations filtered by ward_name list, split by category group.
    Returns dict with keys: hotels, activities, eateries.
    """
    db  = get_mongo_db("TravelDB")
    col = db["Locations"]
    query_base = {"ward_name": {"$in": ward_names}}

    hotels = list(col.find(
        {**query_base, "category": {"$in": STAY_CATS}}, PROJECTION
    ))
    activities = list(col.find(
        {**query_base, "category": {"$in": ACTIVITY_CATS}}, PROJECTION
    ))
    eateries = list(col.find(
        {**query_base, "category": {"$in": FOOD_CATS}}, PROJECTION
    ))

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
    db_context = fetch_locations_from_mongo(ward_names)
    prompt_value = planner_prompt.format(
        db_hotels=json.dumps(db_context["hotels"], ensure_ascii=False),
        db_activities=json.dumps(db_context["activities"], ensure_ascii=False),
        db_eateries=json.dumps(db_context["eateries"], ensure_ascii=False),
        trip_metadata=trip_metadata,
        travel_preferences=travel_preferences,
        constraints=constraints,
    )
    
    response_str = llm.invoke(prompt_value)
    response = PlannerOutput.model_validate_json(response_str)

    return {
        "accommodation": response.accommodation,
        "activities":    response.activities,
        "eateries":      response.eateries,
    }