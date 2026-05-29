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

import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Import Google Generative AI
try:
    import google.generativeai as genai
except ImportError:
    genai = None

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
    schedule: List[Dict[str, Any]]
    accommodations: List[Dict[str, Any]]
    activities: List[Dict[str, Any]]
    transportation: List[Dict[str, Any]]
    costs: Dict[str, float]


@dataclass
class ResponseSection:
    """Single section of generated response."""
    title_en: str
    title_vi: str
    content: str
    section_type: str  # summary, itinerary, costs, logistics, recommendations


# ============================================================================
# TRIP DATA FORMATTER
# ============================================================================

class TripDataFormatter:
    """Extract and structure trip data from workflow state."""
    
    @staticmethod
    def extract_from_state(state: Dict[str, Any]) -> Optional[TripData]:
        """Extract trip data from workflow state."""
        try:
            # Handle both new and old state formats
            destination = state.get("destination") or state.get("trip_metadata", {}).get("destination", "Unknown")
            starting_location = state.get("starting_location", "Unknown")
            duration_days = state.get("duration_days") or state.get("trip_metadata", {}).get("total_days", 0)
            travelers = state.get("travelers") or state.get("constraints", {}).get("group_size", 1)
            budget = float(state.get("total_budget") or state.get("constraints", {}).get("travel_budget", 0))
            
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
                schedule=state.get("schedule", state.get("scheduling", [])),
                accommodations=state.get("accommodations", []),
                activities=state.get("activities", []),
                transportation=state.get("transportation", []),
                costs=state.get("costs", {})
            )
            return trip_data
        except Exception as e:
            logger.error(f"Error extracting trip data: {e}")
            return None
    
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
    """Generate Vietnamese prompts for different response sections."""
    
    @staticmethod
    def summary_prompt(trip_data: TripData) -> str:
        """Prompt for trip summary."""
        travel_style = trip_data.preferences.get('travel_style', 'cân bằng')
        if isinstance(travel_style, list):
            travel_style = ', '.join(travel_style) if travel_style else 'cân bằng'
        
        activity_types = trip_data.preferences.get('activity_types', [])
        if isinstance(activity_types, list):
            activity_types = ', '.join(activity_types) if activity_types else 'đa dạng'
        
        return f"""Hãy viết một tóm tắt ngắn gọn (2-3 câu) về chuyến đi này bằng tiếng Việt:
        
        Từ: {trip_data.starting_location}
        Đến: {trip_data.destination}
        Thời gian: {trip_data.duration_days} ngày
        Số du khách: {trip_data.travelers}
        Ngân sách: {trip_data.budget:,.0f} VND
        Phong cách du lịch: {travel_style}
        Loại hoạt động: {activity_types}

        Hãy tạo một tóm tắt hấp dẫn và chuyên nghiệp về chuyến đi này."""

    @staticmethod
    def itinerary_prompt(trip_data: TripData) -> str:
        """Prompt for detailed itinerary."""
        schedule_text = "\n".join([
            PromptEngine._format_day(day) for day in trip_data.schedule
        ]) if trip_data.schedule else "Lịch trình còn được hoàn thiện"
        
        return f"""Hãy viết một lịch trình chi tiết cho chuyến đi {trip_data.duration_days} ngày từ {trip_data.starting_location} đến {trip_data.destination} bằng tiếng Việt:

        Lịch trình dự kiến:
        {schedule_text}

        Vui lòng:
        1. Mô tả chi tiết từng ngày
        2. Gợi ý các hoạt động hấp dẫn tại địa phương
        3. Đề cập đến các điểm tham quan nổi tiếng
        4. Tính toán thời gian di chuyển hợp lý"""

    @staticmethod
    def costs_prompt(trip_data: TripData) -> str:
        """Prompt for cost analysis."""
        costs_text = PromptEngine._format_costs(trip_data.costs)
        
        return f"""Phân tích chi phí cho chuyến đi {trip_data.duration_days} ngày tới {trip_data.destination} bằng tiếng Việt:

        Ngân sách tổng: {trip_data.budget:,.0f} VND
        Chi tiết:
        {costs_text}

        Vui lòng:
        1. Phân tích từng khoản chi phí
        2. Gợi ý cách tiết kiệm chi phí hợp lý
        3. Cảnh báo nếu chi phí cao hơn ngân sách
        4. Đề xuất các lựa chọn thay thế rẻ hơn nếu cần"""

    @staticmethod
    def logistics_prompt(trip_data: TripData) -> str:
        """Prompt for logistics information."""
        travel_style = trip_data.preferences.get('travel_style', 'cân bằng')
        if isinstance(travel_style, list):
            travel_style = ', '.join(travel_style) if travel_style else 'cân bằng'
        
        return f"""Cung cấp thông tin hậu cần quan trọng cho chuyến đi đến {trip_data.destination} bằng tiếng Việt:

        Thời gian: {trip_data.duration_days} ngày
        Loại du lịch: {travel_style}
        Số du khách: {trip_data.travelers}

        Vui lòng bao gồm:
        1. Yêu cầu hộ chiếu/visa
        2. Mùa du lịch tốt nhất
        3. Tiền tệ và thanh toán
        4. An toàn du lịch
        5. Giao thông nội địa
        6. Nước sạch và sức khỏe
        7. Thông tin liên hệ khẩn cấp"""

    @staticmethod
    def recommendations_prompt(trip_data: TripData) -> str:
        """Prompt for recommendations and tips."""
        validation_msg = f"Điểm đánh giá: {trip_data.validation_score:.0f}%\nTrạng thái: {trip_data.validation_feedback}"
        travel_style = trip_data.preferences.get('travel_style', 'cân bằng')
        if isinstance(travel_style, list):
            travel_style = ', '.join(travel_style) if travel_style else 'cân bằng'
        
        return f"""Đưa ra các gợi ý và lời khuyên cho chuyến đi đến {trip_data.destination} bằng tiếng Việt:

        Thông tin chuyến đi:
        - Số du khách: {trip_data.travelers}
        - Loại du lịch: {travel_style}
        - Đánh giá: {validation_msg}

        Vui lòng đề xuất:
        1. Cách chuẩn bị tốt nhất trước chuyến đi
        2. Những đồ vật cần thiết mang theo
        3. Các mẹo du lịch địa phương
        4. Trải nghiệm không nên bỏ lỡ
        5. Cảnh báo về những rủi ro tiềm ẩn"""

    @staticmethod
    def _format_day(day_data: Dict[str, Any]) -> str:
        """Format a single day's schedule."""
        day_num = day_data.get("day", 1)
        activities = day_data.get("activities", [])
        accommodation = day_data.get("accommodation", "N/A")
        
        result = f"Ngày {day_num}:\n"
        result += f"  Nơi ở: {accommodation}\n"
        for activity in activities:
            time = activity.get("time", "N/A")
            name = activity.get("name", "Hoạt động")
            result += f"  {time}: {name}\n"
        return result
    
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
# LLM GENERATOR (GOOGLE GENERATIVE AI)
# ============================================================================

class LLMGenerator:
    """Generate responses using Google Generative AI (Gemini)."""
    
    def __init__(self):
        """Initialize Gemini API."""
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.model_name = "gemini-1.5-flash"
        self.client = None
        
        if genai and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.client = genai
                logger.info(f"Gemini API initialized with {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        else:
            logger.warning("Gemini API not available or API key missing")
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Optional[str]:
        """Generate text using Gemini API."""
        if not self.client:
            logger.error("Gemini client not initialized")
            return None
        
        try:
            model = self.client.GenerativeModel(self.model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=0.95,
                    top_k=40
                )
            )
            
            if response and response.text:
                logger.info(f"Generated {len(response.text)} characters")
                return response.text.strip()
            return None
            
        except Exception as e:
            logger.error(f"Error generating with Gemini: {e}")
            return None


# ============================================================================
# RESPONSE FORMATTER
# ============================================================================

class ResponseFormatter:
    """Format generated responses into user-friendly structure."""
    
    @staticmethod
    def format_summary_section(content: str) -> ResponseSection:
        """Format summary section."""
        return ResponseSection(
            title_en="Trip Summary",
            title_vi="Tóm tắt chuyến đi",
            content=content,
            section_type="summary"
        )
    
    @staticmethod
    def format_itinerary_section(content: str) -> ResponseSection:
        """Format itinerary section."""
        return ResponseSection(
            title_en="Detailed Itinerary",
            title_vi="Lịch trình chi tiết",
            content=content,
            section_type="itinerary"
        )
    
    @staticmethod
    def format_costs_section(content: str) -> ResponseSection:
        """Format costs section."""
        return ResponseSection(
            title_en="Cost Breakdown",
            title_vi="Tóm tắt chi phí",
            content=content,
            section_type="costs"
        )
    
    @staticmethod
    def format_logistics_section(content: str) -> ResponseSection:
        """Format logistics section."""
        return ResponseSection(
            title_en="Logistics & Information",
            title_vi="Thông tin hậu cần",
            content=content,
            section_type="logistics"
        )
    
    @staticmethod
    def format_recommendations_section(content: str) -> ResponseSection:
        """Format recommendations section."""
        return ResponseSection(
            title_en="Recommendations & Tips",
            title_vi="Gợi ý & Lời khuyên",
            content=content,
            section_type="recommendations"
        )
    
    @staticmethod
    def assemble_response(sections: List[ResponseSection], trip_data: TripData) -> Dict[str, Any]:
        """Assemble final response."""
        return {
            "status": "success",
            "generated_at": datetime.now().isoformat(),
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
                    "title_en": section.title_en,
                    "content": section.content
                }
                for section in sections
            ],
            "language": "vi",
            "model": "gemini-1.5-flash"
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
    logger.info("=" * 60)
    logger.info("GENERATE_ANSWER NODE: Starting response generation (Vietnamese)")
    logger.info("=" * 60)
    
    try:
        # 1. Extract trip data
        formatter = TripDataFormatter()
        trip_data = formatter.extract_from_state(state)
        
        if not trip_data:
            logger.error("Failed to extract trip data")
            return {
                **state,
                "error": "Failed to extract trip data",
                "final_answer": None
            }
        
        logger.info(f"Trip data extracted: {trip_data.destination} ({trip_data.duration_days} days)")
        
        # 2. Initialize LLM
        llm = LLMGenerator()
        if not llm.client:
            logger.warning("Gemini not available, using fallback response")
            return _fallback_response(state, trip_data)
        
        # 3. Generate sections using Gemini
        prompt_engine = PromptEngine()
        response_formatter = ResponseFormatter()
        sections = []
        
        # Generate each section
        section_configs = [
            ("summary", prompt_engine.summary_prompt, response_formatter.format_summary_section, 300),
            ("itinerary", prompt_engine.itinerary_prompt, response_formatter.format_itinerary_section, 800),
            ("costs", prompt_engine.costs_prompt, response_formatter.format_costs_section, 400),
            ("logistics", prompt_engine.logistics_prompt, response_formatter.format_logistics_section, 500),
            ("recommendations", prompt_engine.recommendations_prompt, response_formatter.format_recommendations_section, 500)
        ]
        
        for section_name, prompt_func, format_func, max_tokens in section_configs:
            logger.info(f"Generating {section_name} section...")
            
            prompt = prompt_func(trip_data)
            content = llm.generate(prompt, temperature=0.7, max_tokens=max_tokens)
            
            if content:
                section = format_func(content)
                sections.append(section)
                logger.info(f"✓ {section_name} section generated ({len(content)} chars)")
            else:
                logger.warning(f"Failed to generate {section_name} section")
        
        # 4. Assemble final response
        final_response = response_formatter.assemble_response(sections, trip_data)
        
        logger.info("=" * 60)
        logger.info(f"RESPONSE GENERATION COMPLETE: {len(sections)} sections generated (Vietnamese)")
        logger.info("=" * 60)
        
        return {
            **state,
            "final_answer": final_response,
            "response_status": "success",
            "response_sections_count": len(sections)
        }
        
    except Exception as e:
        logger.error(f"Error in generate_answer_node: {e}", exc_info=True)
        return {
            **state,
            "error": str(e),
            "final_answer": None,
            "response_status": "error"
        }


def _fallback_response(state: Dict[str, Any], trip_data: TripData) -> Dict[str, Any]:
    """Generate fallback response when LLM is unavailable."""
    logger.warning("Using fallback response generation (no LLM)")
    
    formatter = ResponseFormatter()
    sections = [
        formatter.format_summary_section(
            f"Chuyến đi {trip_data.duration_days} ngày từ {trip_data.starting_location} đến {trip_data.destination} "
            f"cho {trip_data.travelers} du khách với ngân sách {trip_data.budget:,.0f} VND."
        ),
        formatter.format_itinerary_section(
            "\n".join([
                TripDataFormatter.format_daily_schedule(day["day"], day.get("activities", []))
                for day in trip_data.schedule
            ]) if trip_data.schedule else "Lịch trình đang được xử lý"
        ),
        formatter.format_costs_section(
            TripDataFormatter.format_cost_breakdown(trip_data.costs)
        )
    ]
    
    final_response = formatter.assemble_response(sections, trip_data)
    final_response["note"] = "Phiên bản rút gọn - API LLM không khả dụng"
    
    return {
        **state,
        "final_answer": final_response,
        "response_status": "fallback"
    }
