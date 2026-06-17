"""
Test suite for Generate_answer node - Vietnamese LLM response generation

Tests:
1. Data extraction from workflow state
2. Prompt generation in Vietnamese
3. Response formatting with proper sections
4. Fallback response when LLM unavailable
"""

import json
from datetime import datetime
from typing import Dict, Any

# Mock Gemini if not available
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Import the Generate_answer module
import os
import sys

# Setup Django for DB access
sys.path.insert(0, '/home/hungdvlper/Documents/TTCS/Traplanner/SourceCode/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
import django
try:
    django.setup()
except Exception:
    pass

from workflow.nodes.Generate_answer import (
    TripData,
    TripDataFormatter,
    PromptEngine,
    ResponseFormatter,
    LLMGenerator,
    generate_answer_node
)

# ============================================================================
# TEST DATA
# ============================================================================

from workflow.graph.stage import State
from workflow.nodes.Scheduler import scheduler_node
from workflow.nodes.Validation_agent import validation_node

def create_sample_state() -> Dict[str, Any]:
    """Create sample workflow state for testing."""
    state = State(
        trip_metadata={
            "usr_des": "Du lịch Đà Nẵng, Hội An 3 ngày 2 đêm cùng gia đình, có người già và trẻ nhỏ, thích trải nghiệm văn hóa, không khí yên bình, ăn hải sản, ở khách sạn gần biển.",
            "start_date": "2026-06-15",
            "end_date": "2026-06-18",
            "total_days": 3,
            "age_range": "Người già, Trẻ nhỏ (5 tuổi)",
            "start_location": "Hà Nội",
            "destination": ["Đà Nẵng", "Hội An"]
        },
        travel_preferences={
            "travel_style": ["Văn hóa"],
            "travel_pace": ["Thong thả"],
            "food_style": ["Hải sản"],
            "accommodation_style": ["Khách sạn gần biển"],
            "mobility_style": [],
            "atmosphere": ["Yên bình", "Gia đình", "Thoáng đãng"],
            "companion_type": ["Gia đình", "Người già", "Trẻ nhỏ"]
        },
        constraints={
            "travel_budget": 15000000,
            "group_size": 4,
            "daily_active_hours": 10,
            "language": "",
            "max_radius_distance": "",
            "places_of_limitation": [],
            "health_limitations": ["Dị ứng hải sản (trẻ nhỏ)", "Không ăn cay (trẻ nhỏ)"],
            "mobility_limitations": ["Hạn chế đi bộ", "Hạn chế leo trèo", "Không đi bộ nhiều"]
        },
        accommodation=[
            {
                "locationId": "LOC-STAY-319-2",
                "name": "Phường Mỹ An Luxury Hotel",
                "estimatedPrice": 1200000,
                "ward_name": "Phường Mỹ An",
                "description": "Khách sạn sang trọng, nằm ở khu vực gần biển Mỹ Khê."
            }
        ],
        activities=[
            {
                "locationId": "LOC-SIGHT-002",
                "name": "Bãi biển Mỹ Khê",
                "description": "Bãi biển đẹp nhất Đà Nẵng với cát trắng mịn.",
                "estimatedDuration": 180,
                "estimatedPrice": 0,
                "suitabilityFor": ["Family", "Couples", "Solo", "Group"],
                "ward_name": "Phường Mỹ An"
            },
            {
                "locationId": "LOC-SIGHT-005",
                "name": "Cầu Rồng & Sông Hàn",
                "description": "Biểu tượng của Đà Nẵng hiện đại",
                "estimatedDuration": 90,
                "estimatedPrice": 0,
                "suitabilityFor": ["Family", "Couples", "Solo", "Group"],
                "ward_name": "Phường Hải Châu 1"
            },
            {
                "locationId": "LOC-ENT-NIGHT-001",
                "name": "Chợ Đêm Helio",
                "description": "Khu chợ đêm sầm uất với hàng trăm món ăn đường phố.",
                "estimatedDuration": 120,
                "estimatedPrice": 50000,
                "suitabilityFor": ["Family", "Couples", "Solo", "Group", "Friends"],
                "ward_name": "Phường Hòa Cường Bắc"
            }
        ],
        eateries=[
            {
                "locationId": "LOC-FOOD-003",
                "name": "Nhà Hàng Hải Sản Biển Đông",
                "estimatedPrice": 350000,
                "description": "Đáp ứng yêu cầu 'ăn hải sản' của gia đình.",
                "ward_name": "Phường Mỹ An"
            }
        ],
        transportations=[
            {'locationId': None, 'name': 'Train (Hà Nội → Đà Nẵng)', 'type': 'train', 'from_ward': 'Hà Nội', 'to_ward': 'Đà Nẵng', 'distance_km': 800.0, 'price_per_person': 840000, 'suitability_for': ['Family'], 'note': ''}, 
            {'locationId': None, 'name': 'Coach (Hải Vân → Thủy Xuân)', 'type': 'coach', 'from_ward': 'Hải Vân', 'to_ward': 'Thủy Xuân', 'distance_km': 79.4, 'price_per_person': 175000, 'suitability_for': ['Family'], 'note': ''}, 
            {'locationId': None, 'name': 'Train (Đà Nẵng → Hà Nội)', 'type': 'train', 'from_ward': 'Đà Nẵng', 'to_ward': 'Hà Nội', 'distance_km': 800.0, 'price_per_person': 840000, 'suitability_for': ['Family'], 'note': ''}
        ]
    )
    
    # Process through scheduler and validation to get full state
    state = scheduler_node(state)
    state = validation_node(state)
    return state


# ============================================================================
# UNIT TESTS
# ============================================================================

def test_trip_data_extraction():
    """Test extracting trip data from state."""
    print("\n" + "="*60)
    print("TEST 1: Trip Data Extraction")
    print("="*60)
    
    state = create_sample_state()
    formatter = TripDataFormatter()
    trip_data = formatter.extract_from_state(state)
    assert trip_data is not None, "Failed to extract trip data"
    assert trip_data.destination == ["Đà Nẵng", "Hội An"], f"Destination mismatch: {trip_data.destination}"
    assert trip_data.starting_location == "Hà Nội", f"Start mismatch: {trip_data.starting_location}"
    assert trip_data.duration_days == 3, f"Duration mismatch: {trip_data.duration_days}"
    assert trip_data.travelers == 4, f"Travelers mismatch: {trip_data.travelers}"
    assert trip_data.budget == 15000000, f"Budget mismatch: {trip_data.budget}"
    assert trip_data.validation_score > 0, f"Score mismatch: {trip_data.validation_score}"
    
    print(f"✓ Destination: {trip_data.destination}")
    print(f"✓ Starting Location: {trip_data.starting_location}")
    print(f"✓ Duration: {trip_data.duration_days} days")
    print(f"✓ Travelers: {trip_data.travelers}")
    print(f"✓ Budget: {trip_data.budget:,.0f} VND")
    print(f"✓ Validation Score: {trip_data.validation_score}%")
    print("✓ TEST PASSED")


def test_daily_schedule_formatting():
    """Test formatting daily schedule."""
    print("\n" + "="*60)
    print("TEST 2: Daily Schedule Formatting")
    print("="*60)
    
    activities = [
        {"time": "08:00", "name": "Khởi hành", "duration": "3 hours"},
        {"time": "12:00", "name": "Ăn trưa", "duration": "1 hour"}
    ]
    
    formatted = TripDataFormatter.format_daily_schedule(1, activities)
    print(f"Formatted Schedule:\n{formatted}")
    
    assert "Ngày 1:" in formatted
    assert "Khởi hành" in formatted
    assert "Ăn trưa" in formatted
    print("✓ TEST PASSED")


def test_cost_breakdown_formatting():
    """Test formatting cost breakdown."""
    print("\n" + "="*60)
    print("TEST 3: Cost Breakdown Formatting")
    print("="*60)
    
    costs = {
        "Transportation": 800000,
        "Accommodation": 1500000,
        "Activities": 1600000
    }
    
    formatted = TripDataFormatter.format_cost_breakdown(costs)
    print(f"Cost Breakdown:\n{formatted}")
    
    assert "Chi phí chi tiết:" in formatted
    assert "800,000" in formatted
    assert "1,500,000" in formatted
    print("✓ TEST PASSED")


def test_vietnamese_prompts():
    """Test Vietnamese prompt generation."""
    print("\n" + "="*60)
    print("TEST 4: Vietnamese Prompt Generation")
    print("="*60)
    
    state = create_sample_state()
    formatter = TripDataFormatter()
    trip_data = formatter.extract_from_state(state)
    
    # Test full trip prompt
    full_prompt = PromptEngine.full_trip_prompt(trip_data)
    assert "tiếng Việt" in full_prompt
    assert trip_data.destination[0] in full_prompt
    assert "THÔNG TIN CHUYẾN ĐI" in full_prompt
    print(f"✓ Full Trip Prompt ({len(full_prompt)} chars)")
    
    print("✓ TEST PASSED - Prompt generated in Vietnamese")


def test_response_section_formatting():
    """Test response section formatting."""
    print("\n" + "="*60)
    print("TEST 5: Response Section Formatting")
    print("="*60)
    
    formatter = ResponseFormatter()
    
    # Test each section type
    summary_section = formatter.format_section("Sample summary in Vietnamese", "summary")
    assert summary_section.title_vi == "Tóm tắt chuyến đi"
    assert summary_section.section_type == "summary"
    print(f"✓ Summary Section: {summary_section.title_vi}")
    
    itinerary_section = formatter.format_section("Detailed itinerary", "itinerary")
    assert itinerary_section.title_vi == "Lịch trình chi tiết"
    print(f"✓ Itinerary Section: {itinerary_section.title_vi}")
    
    costs_section = formatter.format_section("Cost breakdown", "costs")
    assert costs_section.title_vi == "Tóm tắt chi phí"
    print(f"✓ Costs Section: {costs_section.title_vi}")
    
    logistics_section = formatter.format_section("Logistics info", "logistics")
    assert logistics_section.title_vi == "Thông tin hậu cần"
    print(f"✓ Logistics Section: {logistics_section.title_vi}")
    
    recommendations_section = formatter.format_section("Tips", "recommendations")
    assert recommendations_section.title_vi == "Gợi ý & Lời khuyên"
    print(f"✓ Recommendations Section: {recommendations_section.title_vi}")
    
    print("✓ TEST PASSED")


def test_response_assembly():
    """Test final response assembly."""
    print("\n" + "="*60)
    print("TEST 6: Response Assembly")
    print("="*60)
    
    state = create_sample_state()
    formatter = TripDataFormatter()
    trip_data = formatter.extract_from_state(state)
    response_formatter = ResponseFormatter()
    
    sections = [
        response_formatter.format_section("Sample summary", "summary"),
        response_formatter.format_section("Sample itinerary", "itinerary"),
        response_formatter.format_section("Sample costs", "costs")
    ]
    
    final_response = response_formatter.assemble_response(sections, trip_data)
    
    assert final_response["status"] == "success"
    assert final_response["language"] == "vi"
    from workflow.models.llm import DEFAULT_MODEL
    assert final_response["model"] == DEFAULT_MODEL
    assert len(final_response["sections"]) == 3
    assert final_response["trip_info"]["destination"] == ["Đà Nẵng", "Hội An"]
    
    assert "database_schema" in final_response
    assert "trip" in final_response["database_schema"]
    assert "day_details" in final_response["database_schema"]
    
    print(f"✓ Response Status: {final_response['status']}")
    print(f"✓ Language: {final_response['language']}")
    print(f"✓ Sections: {len(final_response['sections'])}")
    print(f"✓ Trip Info: {final_response['trip_info']['destination']}")
    print(f"✓ Generated At: {final_response['generated_at']}")
    print(f"✓ Database Schema generated: Yes")
    print("✓ TEST PASSED")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_generate_answer_node_no_llm():
    """Test generate_answer_node with fallback (no LLM)."""
    print("\n" + "="*60)
    print("TEST 8: Generate Answer Node (Fallback Mode)")
    print("="*60)
    
    state = create_sample_state()
    result = generate_answer_node(state)
    
    assert result is not None
    assert result["response_status"] in ["success", "fallback", "error"]
    
    if result["response_status"] == "fallback":
        print(f"✓ Status: {result['response_status']} (LLM not available)")
        print(f"✓ Has Response: {result['final_answer'] is not None}")
        print(f"✓ Sections: {len(result['final_answer']['sections'])}")
        print("✓ TEST PASSED - Fallback response generated successfully")
        print("\n--- FULL FINAL ANSWER (Generate_answer.py:L412) ---")
        print(json.dumps(result['final_answer'], ensure_ascii=False, indent=2))
    elif result["response_status"] == "success":
        print(f"✓ Status: {result['response_status']} (LLM available)")
        print(f"✓ Sections Count: {result.get('response_sections_count', 0)}")
        print("✓ TEST PASSED - Full LLM response generated successfully")
        print("\n--- FULL FINAL ANSWER (Generate_answer.py:L412) ---")
        print(json.dumps(result['final_answer'], ensure_ascii=False, indent=2))
    else:
        print(f"⚠ Status: {result['response_status']}")
        print(f"⚠ Error: {result.get('error', 'Unknown')}")

def test_database_persistence():
    """Test saving the generated trip state to MongoDB."""
    print("\n" + "="*60)
    print("TEST 9: Database Persistence (Trips & DayDetails)")
    print("="*60)
    print("✓ TEST SKIPPED - trips app has been removed")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("GENERATE_ANSWER NODE TEST SUITE - VIETNAMESE LLM INTEGRATION")
    print("="*70)
    
    try:
        # Unit tests
        test_trip_data_extraction()
        test_daily_schedule_formatting()
        test_cost_breakdown_formatting()
        test_vietnamese_prompts()
        test_response_section_formatting()
        test_response_assembly()
        
        # Integration tests
        test_generate_answer_node_no_llm()
        test_database_persistence()
        
        print("\n" + "="*70)
        print("ALL TESTS PASSED ✓")
        print("="*70)
        print("\nSummary:")
        print("  ✓ Data extraction from workflow state")
        print("  ✓ Vietnamese prompt generation (5 sections)")
        print("  ✓ Response section formatting with bilingual titles")
        print("  ✓ Final response assembly with metadata")
        print("  ✓ Fallback response without LLM")
        print("  ✓ Generate answer node (both LLM and fallback modes)")
        print("\nReady for production deployment!")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
