from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from workflow.graph.stage import State, TripMetadata, TravelPreferences, Constraints
from workflow.models.llm import LLM
from dotenv import load_dotenv
import os
load_dotenv(override=True)

class TripMetadataModel(BaseModel):
    usr_des: str = Field(description="Mô tả chung của người dùng", default="")
    start_date: str = Field(description="Ngày bắt đầu", default="")
    end_date: str = Field(description="Ngày kết thúc", default="")
    total_days: int = Field(description="Tổng số ngày", default=0)
    age_range: str = Field(description="Độ tuổi", default="")
    start_location: str = Field(description="Điểm xuất phát", default="")

class TravelPreferencesModel(BaseModel):
    travel_style: list[str] = Field(description="Phong cách du lịch", default_factory=list)
    travel_pace: list[str] = Field(description="Nhịp độ chuyến đi", default_factory=list)
    food_style: list[str] = Field(description="Sở thích ăn uống", default_factory=list)
    accommodation_style: list[str] = Field(description="Sở thích lưu trú", default_factory=list)
    mobility_style: list[str] = Field(description="Sở thích di chuyển", default_factory=list)
    atmosphere: list[str] = Field(description="Không khí mong muốn", default_factory=list)
    companion_type: list[str] = Field(description="Đối tượng đi cùng", default_factory=list)

class ConstraintsModel(BaseModel):
    travel_budget: str = Field(description="Ngân sách", default="")
    group_size: int = Field(description="Số lượng người", default=1)
    daily_active_hours: str = Field(description="Giờ hoạt động mỗi ngày", default="")
    language: str = Field(description="Ngôn ngữ", default="")
    max_radius_distance: str = Field(description="Bán kính di chuyển tối đa", default="")
    places_of_limitation: list[str] = Field(description="Địa điểm không muốn đến", default_factory=list)
    health_limitations: list[str] = Field(description="Giới hạn sức khỏe", default_factory=list)
    mobility_limitations: list[str] = Field(description="Giới hạn khả năng di chuyển", default_factory=list)

class ExtractorOutput(BaseModel):
    trip_metadata: TripMetadataModel
    travel_preferences: TravelPreferencesModel
    constraints: ConstraintsModel

extractor_prompt = ChatPromptTemplate.from_messages([
    ("system", """Bạn là một chuyên gia phân tích dữ liệu du lịch (Extractor Agent).
    Nhiệm vụ của bạn là đọc yêu cầu của người dùng và trích xuất thông tin vào một cấu trúc JSON chuẩn xác.

    HƯỚNG DẪN TRÍCH XUẤT:
    1. TripMetadata: Chứa thông tin ngày tháng, mô tả chung, độ tuổi. Nếu không rõ ngày, để trống.
    2. TravelPreferences: Các sở thích mang tính linh hoạt (phong cách, đồ ăn, không khí...). Hãy dùng các từ khóa ngắn gọn.
    3. Constraints: Các giới hạn bắt buộc (ngân sách, số lượng người, bán kính, giới hạn sức khỏe/phương tiện). Nếu người dùng cấm một địa điểm, đưa vào places_of_limitation.
    
    [SUY LUẬN NGẦM - IMPLICIT INFERENCE]
    Nếu người dùng để trống các trường sở thích hoặc ràng buộc, BẠN PHẢI TỰ ĐỘNG SUY LUẬN dựa trên đối tượng đi cùng (companion_type) hoặc độ tuổi (age_range).
    - Nếu có "Trẻ nhỏ/Trẻ em" -> Tự động thêm Constraints (không đi bộ nhiều, tránh nguy hiểm) và Preferences (đồ ăn không cay, không gian thoáng).
    - Nếu có "Người già" -> Tự động thêm Constraints (hạn chế leo trèo, hạn chế đi bộ) và Preferences (nhịp độ thong thả, yên bình).
    - Nếu là "Cặp đôi" -> Tự động ưu tiên atmosphere "Lãng mạn, chill".
    - Với các thông số kỹ thuật (như max_radius_distance) nếu không thể suy luận chính xác, hãy để rỗng ("") để hệ thống tự do quét dữ liệu mở rộng."""),
    ("human", "Thông tin từ người dùng: {user_input}")
])

# Use custom LLM wrapper for API Key rotation and structured JSON parsing
llm = LLM(
    api_keys=[os.getenv("GOOGLE_API_KEY") or ""],
    temperature=0.5,
    response_schema=ExtractorOutput
)

def extractor_node(state: State) -> State:
    user_des_input = state.get("user_des_input") or state.get("usr_des_input") or ""
    group_size = state.get("group_size")
    start_date = state.get("start_date") 
    end_date = state.get("end_date") 
    start_location = state.get("start_location")
    destination = state.get("destination")
    personal_travel_style_des = state.get("personal_travel_style_des") 

    combined_input = f"""
    - Yêu cầu chính: {user_des_input}
    - Điểm xuất phát: {start_location}
    - Điểm đến: {', '.join(destination) if isinstance(destination, list) else destination}
    - Số người trong đoàn: {group_size}
    - Ngày bắt đầu: {start_date}
    - Ngày kết thúc: {end_date}
    - Sở thích & phong cách cá nhân: {personal_travel_style_des}
    """

    prompt_value = extractor_prompt.format(user_input=combined_input)
    response_str = llm.invoke(prompt_value)
    response = ExtractorOutput.model_validate_json(response_str)
    
    trip_meta = response.trip_metadata.model_dump()
    travel_prefs = response.travel_preferences.model_dump()
    constraints = response.constraints.model_dump()

    trip_meta["start_date"] = start_date
    trip_meta["end_date"] = end_date
    trip_meta["start_location"] = start_location
    trip_meta["destination"] = destination
    constraints["group_size"] = group_size

    return {
        "trip_metadata": trip_meta,
        "travel_preferences": travel_prefs,
        "constraints": constraints
    }