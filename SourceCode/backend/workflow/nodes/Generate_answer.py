"""
Generate_answer Agent: Natural Language Response Generation (Tiếng Việt)

This node transforms structured trip data into natural, personalized responses
using Google Generative AI (Gemini), with all output in Vietnamese.

Process:
1. Extract and format trip data from state
2. Create Vietnamese prompts for different sections
3. Call Gemini API to generate natural language 
4. Format responses into user-friendly structure
5. Return complete trip plan in Vietnamese

Output Sections (Tiếng Việt):
- Tóm tắt (Summary): 2-3 sentence overview
- Lịch trình chi tiết (Detailed itinerary): Day-by-day schedule
- Tóm tắt chi phí (Cost breakdown): Budget analysis
- Thông tin hậu cần (Logistics): Practical info
- Gợi ý (Recommendations): Tips and improvements
"""
import re
import os
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field
from google import genai
import dotenv 
dotenv.load_dotenv()   

logger = logging.getLogger(__name__)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class TripData:
    """Structured trip information for response generation."""
    destination: str
    starting_location: str
    duration_days: int
    travelers: int
    budget: float
    preferences: Dict[str, Any]
    validation_score: float
    validation_feedback: str
    category_scores: Dict[str, float]
    schedule: List[Dict[str, Any]]
    accommodations: List[Dict[str, Any]]
    activities: List[Dict[str, Any]]
    transportation: List[Dict[str, Any]]
    costs: Dict[str, float]


@dataclass
class ResponseSection:
    """Single section of generated response."""
    title_vi: str
    content: str
    section_type: str  # summary, itinerary, costs, logistics, recommendations


class FullTripResponse(BaseModel):
    """Pydantic model for structured Gemini output"""
    summary: str = Field(description="Tóm tắt chuyến đi 2-3 câu")
    costs: str = Field(description="Phân tích chi phí và ngân sách ngắn gọn")
    logistics: str = Field(description="Thông tin hậu cần, di chuyển, visa")
    recommendations: str = Field(description="Lời khuyên và mẹo du lịch, gạch đầu dòng")


# ============================================================================
# TRIP DATA FORMATTER
# ============================================================================

class TripDataFormatter:
    """Extract and structure trip data from workflow state."""
    @staticmethod
    def parse_budget(budget_val: Any) -> float:
        if isinstance(budget_val, (int, float)):
            return float(budget_val)
        if not budget_val:
            return 0.0
            
        s = str(budget_val).lower().strip()
        # Extract the first sequence of digits/decimals
        nums = re.findall(r"[\d\.]+", s)
        if not nums:
            return 0.0
            
        val = float(nums[0])   
        # Handle Vietnamese text multipliers
        if "triệu" in s:
            val *= 1_000_000
        elif "trăm" in s and "nghìn" in s:
            val *= 100_000
        elif "k" in s or "nghìn" in s or "ngàn" in s:
            val *= 1_000         
        return val

    @staticmethod
    def extract_from_state(state: Dict[str, Any]) -> Optional[TripData]:
        """Extract trip data from workflow state."""
        # Handle both new and old state formats
        destination = state.get("destination") or state.get("trip_metadata", {}).get("destination", "Unknown")
        starting_location = state.get("starting_location") or state.get("trip_metadata", {}).get("start_location", "Unknown")
        duration_days = state.get("duration_days") or state.get("trip_metadata", {}).get("total_days", 0)
        travelers = state.get("travelers") or state.get("constraints", {}).get("group_size", 1)
        
        budget_raw = state.get("total_budget") or state.get("constraints", {}).get("travel_budget", 0)
        budget = TripDataFormatter.parse_budget(budget_raw)
        
        # Get all required fields from state
        trip_data = TripData(
            destination=destination,
            starting_location=starting_location,
            duration_days=duration_days,
            travelers=travelers,
            budget=budget,
            preferences=state.get("preferences", state.get("travel_preferences", {})),
            validation_score=state.get("validation_score", state.get("validation", {}).get("overall_score", 0)),
            validation_feedback=state.get("validation_feedback", state.get("validation", {}).get("status", "")),
            category_scores=state.get("validation", {}).get("category_scores", {}),
            schedule=state.get("schedule", state.get("scheduling", [])),
            accommodations=state.get("accommodations", []),
            activities=state.get("activities", []),
            transportation=state.get("transportation", []),
            costs=state.get("costs", {})
        )
        return trip_data

    
    @staticmethod
    def format_daily_schedule(day_num: int, activities: List[Dict]) -> str:
        """Format activities for a single day."""
        formatted = f"Ngày {day_num}:\n"
        if not activities:
            formatted += "  (Thời gian tự do)\n"
        else:
            for activity in activities:
                time = activity.get("time", "N/A")
                name = activity.get("name", "Hoạt động")
                duration = activity.get("duration", "")
                if duration:
                    formatted += f"  • {time}: {name} ({duration})\n"
                else:
                    formatted += f"  • {time}: {name}\n"
        return formatted.strip()
    
    @staticmethod
    def format_cost_breakdown(costs: Dict[str, float]) -> str:
        """Format cost breakdown."""
        if not costs:
            return "Chi phí chưa được xác định"
        
        formatted = "Chi phí chi tiết:\n"
        for category, amount in costs.items():
            formatted += f"  • {category}: {amount:,.0f} VND\n"
        total = sum(costs.values())
        formatted += f"  • Tổng cộng: {total:,.0f} VND"
        return formatted.strip()


# ============================================================================
# VIETNAMESE PROMPT ENGINE
# ============================================================================

class PromptEngine:
    """Generate Vietnamese prompts for response sections."""
    @staticmethod
    def full_trip_prompt(trip_data: TripData) -> str:
        """Prompt to generate all 5 sections in one API call."""
        travel_style = trip_data.preferences.get('travel_style', 'cân bằng')
        if isinstance(travel_style, list):
            travel_style = ', '.join(travel_style) if travel_style else 'cân bằng'
            
        activity_types = trip_data.preferences.get('activity_types', [])
        if isinstance(activity_types, list):
            activity_types = ', '.join(activity_types) if activity_types else 'đa dạng'

        validation_msg = f"Điểm đánh giá: {trip_data.validation_score:.0f}%\nTrạng thái: {trip_data.validation_feedback}"
        
        # Compress input context to reduce token usage
        compressed_schedule = []
        for day in trip_data.schedule:
            compressed_schedule.append(f"--- Ngày {day.get('day', 1)} ---")
            for item in day.get('activities', []):
                compressed_schedule.append(f"- {item.get('time', 'N/A')}: {item.get('name', 'Hoạt động')}")
        schedule_text = "\n".join(compressed_schedule) if compressed_schedule else "Chưa có lịch trình chi tiết"
        costs_text = PromptEngine._format_costs(trip_data.costs)

        return f"""Dựa trên dữ liệu rút gọn dưới đây, hãy tạo một kế hoạch chuyến đi hoàn chỉnh bằng tiếng Việt.
        
            [THÔNG TIN CHUYẾN ĐI]
            Từ: {trip_data.starting_location}
            Đến: {trip_data.destination}
            Thời gian: {trip_data.duration_days} ngày
            Số du khách: {trip_data.travelers}
            Ngân sách: {trip_data.budget:,.0f} VND
            Phong cách: {travel_style}
            Loại hoạt động: {activity_types}
            Đánh giá lịch trình: {validation_msg}

            [LỊCH TRÌNH DỰ KIẾN]
            {schedule_text}

            [CHI PHÍ DỰ KIẾN]
            {costs_text}

            Yêu cầu khắt khe:
            1. Trả về đúng định dạng JSON theo cấu trúc yêu cầu.
            2. Cực kỳ ngắn gọn, súc tích, đi thẳng vào vấn đề. Sử dụng gạch đầu dòng (bullet points) nhiều nhất có thể.
            3. KHÔNG viết các đoạn văn dài dòng không cần thiết để tiết kiệm token."""

    @staticmethod
    def _format_costs(costs: Dict[str, float]) -> str:
        """Format costs for prompt."""
        if not costs:
            return "(Chi phí chưa xác định)"
        lines = []
        for category, amount in costs.items():
            lines.append(f"  - {category}: {amount:,.0f} VND")
        return "\n".join(lines)


# ============================================================================
# LLM GENERATOR 
# ============================================================================
from workflow.models.llm import DEFAULT_MODEL

class LLMGenerator:
    """Generate responses using Google Generative AI (Gemini)."""
    def __init__(self):
        """Initialize Gemini API."""
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.model_name = DEFAULT_MODEL
        self.client = None
        
        if genai and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Gemini API initialized with {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        else:
            logger.warning("Gemini API not available or API key missing")
    
    def generate_full_response(self, prompt: str, temperature: float = 0.5) -> Optional[Dict[str, str]]:
        """Generate the full JSON response using structured output."""
        import time
        max_retries = 5
        attempts = 0
        
        while attempts < max_retries:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction="Bạn là trợ lý du lịch AI. Trả lời cực kỳ ngắn gọn, súc tích, đi thẳng vào vấn đề. Sử dụng gạch đầu dòng (bullet points) thay vì viết các đoạn văn dài dòng không cần thiết.",
                        temperature=temperature,
                        max_output_tokens=8192,
                        top_p=0.95,
                        top_k=40,
                        response_mime_type="application/json",
                        response_schema=FullTripResponse
                    )
                )
                break # Success!
            except Exception as e:
                attempts += 1
                error_str = str(e)
                logger.error(f"Generate Answer API Error: {error_str}")
                
                if "Quota exceeded" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.error("Hết quota API. Ngưng retry.")
                    raise e
                    
                if attempts < max_retries and ("429" in error_str or "503" in error_str):
                    wait_time = 3 * attempts
                    logger.warning(f"API quá tải (429/503). Đợi {wait_time}s trước khi thử lại ({attempts}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    if attempts >= max_retries:
                        logger.error("Đã hết số lần retry. Bỏ cuộc!")
                    raise e
                    
        if response and response.text:
            text = response.text.strip()
            if text.startswith("```json"):
                text = text.strip("```json").strip("```").strip()
            return json.loads(text)
        return None
            


# ============================================================================
# RESPONSE FORMATTER
# ============================================================================

class ResponseFormatter:
    """Format generated responses into user-friendly structure."""
    
    SECTION_TITLES = {
        "summary": "Tóm tắt chuyến đi",
        "costs": "Tóm tắt chi phí",
        "logistics": "Thông tin hậu cần",
        "recommendations": "Gợi ý & Lời khuyên"
    }

    @classmethod
    def format_section(cls, content: str, section_type: str) -> ResponseSection:
        return ResponseSection(
            title_vi=cls.SECTION_TITLES.get(section_type, section_type.title()),
            content=content,
            section_type=section_type
        )
    
    @staticmethod
    def assemble_response(sections: List[ResponseSection], trip_data: TripData) -> Dict[str, Any]:
        """Assemble final response and database schema representations."""
        import uuid
        
        # Generate Trip Document Schema
        trip_id = f"T{uuid.uuid4().hex[:8]}"
        now_iso = datetime.now().isoformat()
        
        # Extract destination string
        dest = trip_data.destination
        if isinstance(dest, list):
            dest = ", ".join(dest)
            
        trip_document = {
            "tripId": trip_id,
            "userId": "",
            "budgetId": None,
            "status": "PLANNING",
            "version": 1,
            "destination": dest,
            "totalBudget": int(trip_data.budget),
            "validationScore": trip_data.validation_score,
            "categoryScores": trip_data.category_scores,
            "createdAt": now_iso
        }
        
        # Generate DayDetails Document Schema
        day_details_documents = []
        for day_idx, day_info in enumerate(trip_data.schedule):
            # Try to get the real date or fallback
            day_num = day_info.get("day", day_idx + 1)
            date_str = day_info.get("date", "")
            if date_str:
                try:
                    # Format to ISO if it's YYYY-MM-DD
                    date_iso = datetime.strptime(date_str, "%Y-%m-%d").isoformat()
                except ValueError:
                    date_iso = date_str
            else:
                date_iso = now_iso
                
            day_acts = []
            for act in day_info.get("items", day_info.get("activities", [])):
                # Map scheduling items to dayActs schema
                # Some properties may differ depending on what the scheduler outputs
                start_time = act.get("time_start", act.get("time", "08:00"))
                end_time = act.get("time_end", "10:00")
                if date_iso and "T" in date_iso:
                    # Combine date with time
                    base_date = date_iso.split("T")[0]
                    full_start = f"{base_date}T{start_time}:00"
                    full_end = f"{base_date}T{end_time}:00"
                else:
                    full_start = start_time
                    full_end = end_time
                    
                act_type = act.get("type", "Activity").capitalize()
                if act_type == "Meal": act_type = "Food"
                elif act_type == "Transportation": act_type = "Transport"
                elif act_type == "Accommodation": act_type = "Stay"
                else: act_type = "Sightseeing"
                
                day_acts.append({
                    "activityId": f"A{uuid.uuid4().hex[:8]}",
                    "name": act.get("name", "Unknown Activity"),
                    "type": act_type,
                    "startTime": full_start,
                    "endTime": full_end,
                    "price": int(act.get("cost", act.get("estimatedPrice", 0))),
                    "note": act.get("notes", act.get("description", "")),
                    "image": act.get("img_url", "/src/assets/images/default.jpg"),
                    "locationId": act.get("locationId"),
                    "eateryId": None,
                    "accommodationId": act.get("locationId") if act_type == "Stay" else None,
                    "transportId": None
                })
                
            day_details_documents.append({
                "dayScheduleDetailedId": f"D{uuid.uuid4().hex[:8]}",
                "tripId": trip_id,
                "dayNumber": day_num,
                "date": date_iso,
                "dayActs": day_acts
            })

        return {
            "status": "success",
            "generated_at": now_iso,
            "trip_info": {
                "destination": trip_data.destination,
                "starting_location": trip_data.starting_location,
                "duration_days": trip_data.duration_days,
                "travelers": trip_data.travelers,
                "budget": trip_data.budget,
                "validation_score": trip_data.validation_score,
            },
            "sections": [
                {
                    "type": section.section_type,
                    "title_vi": section.title_vi,
                    "content": section.content
                }
                for section in sections
            ],
            "database_schema": {
                "trip": trip_document,
                "day_details": day_details_documents
            },
            "status": "APPROVED",
            "model": DEFAULT_MODEL
        }


# ============================================================================
# MAIN GENERATE ANSWER NODE
# ============================================================================

def generate_answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main node function: Generate natural language response.
    Args:
        state: Workflow state with validated trip plan
    Returns:
        Updated state with generated response
    """
    # 1. Extract trip data
    formatter = TripDataFormatter()
    trip_data = formatter.extract_from_state(state)
    # 2. Initialize LLM
    llm = LLMGenerator()
    # 3. Generate all sections using Gemini Call 
    prompt_engine = PromptEngine()
    response_formatter = ResponseFormatter()
    prompt = prompt_engine.full_trip_prompt(trip_data)
    result_data = llm.generate_full_response(prompt) or {}
    sections = [
        response_formatter.format_section(result_data.get(k, ""), k)
        for k in ["summary", "costs", "logistics", "recommendations"]
    ]
    # 4. Assemble final response
    final_response = response_formatter.assemble_response(sections, trip_data)

    return {
        **state,
        "final_answer": final_response,
        "response_status": "success",
        "response_sections_count": len(sections)
    }



