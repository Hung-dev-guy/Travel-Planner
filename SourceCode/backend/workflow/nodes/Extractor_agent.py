from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from workflow.graph.stage import State, TripMetadata, TravelPreferences, Constraints
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
load_dotenv()

class ExtractorOutput(BaseModel):
    trip_metadata: dict = Field(
        description="Thông tin cơ bản của chuyến đi. Bao gồm: usr_des, start_date, end_date, total_days, age_range."
    )
    travel_preferences: dict = Field(
        description="Sở thích du lịch của người dùng. Bao gồm danh sách các chuỗi cho: travel_style, travel_pace, food_style, accommodation_style, mobility_style, atmosphere, companion_type."
    )
    constraints: dict = Field(
        description="Các ràng buộc cứng của chuyến đi. Bao gồm: travel_budget, group_size, daily_active_hours, language, max_radius_distance, places_of_limitation, health_limitations, mobility_limitations."
    )

extractor_prompt = ChatPromptTemplate.from_messages([
    ("system", """Bạn là một chuyên gia phân tích dữ liệu du lịch (Extractor Agent).
    Nhiệm vụ của bạn là đọc yêu cầu của người dùng và trích xuất thông tin vào một cấu trúc JSON chuẩn xác.

    HƯỚNG DẪN TRÍCH XUẤT:
    1. TripMetadata: Chứa thông tin ngày tháng, mô tả chung, độ tuổi. Nếu không rõ ngày, để trống.
    2. TravelPreferences: Các sở thích mang tính linh hoạt (phong cách, đồ ăn, không khí...). Hãy dùng các từ khóa ngắn gọn.
    3. Constraints: Các giới hạn bắt buộc (ngân sách, số lượng người, bán kính, giới hạn sức khỏe/phương tiện). Nếu người dùng cấm một địa điểm, đưa vào places_of_limitation.

    Nếu thông tin nào người dùng không cung cấp, hãy thêm thông tin vào giúp họ dựa trên dữ liệu đã có sẵn."""),
    ("human", "Thông tin từ người dùng: {user_input}")
])

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=1.0, google_api_key=os.getenv("GOOGLE_API_KEY")) 
structured_llm = llm.with_structured_output(ExtractorOutput)
extractor_chain = extractor_prompt | structured_llm

def extractor_node(state: State) -> State:
    user_des_input = state.get("user_des_input") or state.get("usr_des_input") or ""
    group_size = state.get("group_size")
    start_date = state.get("start_date") 
    end_date = state.get("end_date") 
    destination = state.get("destination") 
    personal_travel_style_des = state.get("personal_travel_style_des") 

    combined_input = f"""
    - Yêu cầu chính: {user_des_input}
    - Điểm đến: {', '.join(destination) if isinstance(destination, list) else destination}
    - Số người trong đoàn: {group_size}
    - Ngày bắt đầu: {start_date}
    - Ngày kết thúc: {end_date}
    - Sở thích & phong cách cá nhân: {personal_travel_style_des}
    """

    response: ExtractorOutput = extractor_chain.invoke({"user_input": combined_input})
    
    trip_meta: TripMetadata = response.trip_metadata
    travel_prefs: TravelPreferences = response.travel_preferences
    constraints: Constraints = response.constraints

    trip_meta["start_date"] = start_date
    trip_meta["end_date"] = end_date
    trip_meta["destination"] = destination
    constraints["group_size"] = group_size

    return {
        "trip_metadata": trip_meta,
        "travel_preferences": travel_prefs,
        "constraints": constraints
    }