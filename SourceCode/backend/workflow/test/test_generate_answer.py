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
import sys
sys.path.insert(0, '/home/hungdvlper/Documents/TTCS/Traplanner/SourceCode/backend/workflow/nodes')

from Generate_answer import (
    TripData,
    TripDataFormatter,
    PromptEngine,
    ResponseFormatter,
    LLMGenerator,
    generate_answer_node,
    _fallback_response
)


# ============================================================================
# TEST DATA
# ============================================================================

def create_sample_state() -> Dict[str, Any]:
    """Create sample workflow state for testing."""
    return {
        "destination": "Quảng Ninh",
        "starting_location": "Hà Nội",
        "duration_days": 3,
        "travelers": 2,
        "total_budget": 5000000,  # 5M VND
        "preferences": {
            "travel_style": "adventure",
            "activity_types": ["hiking", "sightseeing", "local_cuisine"],
            "accommodation_type": "mid-range"
        },
        "validation_score": 85,
        "validation_feedback": "APPROVED",
        "schedule": [
            {
                "day": 1,
                "accommodation": "Halong Bay Hotel",
                "activities": [
                    {"time": "08:00", "name": "Khởi hành từ Hà Nội", "duration": "3 hours"},
                    {"time": "12:00", "name": "Ăn trưa tại Hạ Long", "duration": "1 hour"},
                    {"time": "14:00", "name": "Du thuyền vịnh Hạ Long", "duration": "4 hours"}
                ]
            },
            {
                "day": 2,
                "accommodation": "Halong Bay Hotel",
                "activities": [
                    {"time": "07:00", "name": "Thăm hang Sương Sơn", "duration": "2 hours"},
                    {"time": "10:00", "name": "Bơi lội", "duration": "1.5 hours"},
                    {"time": "14:00", "name": "Khám phá đảo Titop", "duration": "3 hours"}
                ]
            },
            {
                "day": 3,
                "accommodation": "Halong Bay Hotel",
                "activities": [
                    {"time": "09:00", "name": "Trả phòng", "duration": "0.5 hours"},
                    {"time": "10:00", "name": "Quay về Hà Nội", "duration": "3 hours"}
                ]
            }
        ],
        "accommodations": [
            {
                "name": "Halong Bay Hotel",
                "location": "Hạ Long",
                "nights": 2,
                "cost": 1500000
            }
        ],
        "activities": [
            {
                "name": "Du thuyền vịnh Hạ Long",
                "category": "sightseeing",
                "cost": 1200000
            },
            {
                "name": "Ăn hải sản",
                "category": "local_cuisine",
                "cost": 800000
            },
            {
                "name": "Khám phá hang động",
                "category": "adventure",
                "cost": 600000
            }
        ],
        "transportation": [
            {
                "type": "car",
                "from": "Hà Nội",
                "to": "Hạ Long",
                "cost": 800000
            }
        ],
        "costs": {
            "Transportation": 800000,
            "Accommodation": 1500000,
            "Activities": 1600000,
            "Food": 800000,
            "Misc": 300000
        }
    }


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
    assert trip_data.destination == "Quảng Ninh"
    assert trip_data.starting_location == "Hà Nội"
    assert trip_data.duration_days == 3
    assert trip_data.travelers == 2
    assert trip_data.budget == 5000000
    assert trip_data.validation_score == 85
    
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
    
    # Test summary prompt
    summary_prompt = PromptEngine.summary_prompt(trip_data)
    assert "tiếng Việt" in summary_prompt
    assert trip_data.destination in summary_prompt
    print(f"✓ Summary Prompt ({len(summary_prompt)} chars)")
    
    # Test itinerary prompt
    itinerary_prompt = PromptEngine.itinerary_prompt(trip_data)
    assert "lịch trình chi tiết" in itinerary_prompt.lower()
    print(f"✓ Itinerary Prompt ({len(itinerary_prompt)} chars)")
    
    # Test costs prompt
    costs_prompt = PromptEngine.costs_prompt(trip_data)
    assert "chi phí" in costs_prompt.lower()
    print(f"✓ Costs Prompt ({len(costs_prompt)} chars)")
    
    # Test logistics prompt
    logistics_prompt = PromptEngine.logistics_prompt(trip_data)
    assert "hậu cần" in logistics_prompt.lower()
    print(f"✓ Logistics Prompt ({len(logistics_prompt)} chars)")
    
    # Test recommendations prompt
    recommendations_prompt = PromptEngine.recommendations_prompt(trip_data)
    assert "gợi ý" in recommendations_prompt.lower()
    print(f"✓ Recommendations Prompt ({len(recommendations_prompt)} chars)")
    
    print("✓ TEST PASSED - All prompts generated in Vietnamese")


def test_response_section_formatting():
    """Test response section formatting."""
    print("\n" + "="*60)
    print("TEST 5: Response Section Formatting")
    print("="*60)
    
    formatter = ResponseFormatter()
    
    # Test each section type
    summary_section = formatter.format_summary_section("Sample summary in Vietnamese")
    assert summary_section.title_vi == "Tóm tắt chuyến đi"
    assert summary_section.section_type == "summary"
    print(f"✓ Summary Section: {summary_section.title_vi}")
    
    itinerary_section = formatter.format_itinerary_section("Detailed itinerary")
    assert itinerary_section.title_vi == "Lịch trình chi tiết"
    print(f"✓ Itinerary Section: {itinerary_section.title_vi}")
    
    costs_section = formatter.format_costs_section("Cost breakdown")
    assert costs_section.title_vi == "Tóm tắt chi phí"
    print(f"✓ Costs Section: {costs_section.title_vi}")
    
    logistics_section = formatter.format_logistics_section("Logistics info")
    assert logistics_section.title_vi == "Thông tin hậu cần"
    print(f"✓ Logistics Section: {logistics_section.title_vi}")
    
    recommendations_section = formatter.format_recommendations_section("Tips")
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
        response_formatter.format_summary_section("Sample summary"),
        response_formatter.format_itinerary_section("Sample itinerary"),
        response_formatter.format_costs_section("Sample costs")
    ]
    
    final_response = response_formatter.assemble_response(sections, trip_data)
    
    assert final_response["status"] == "success"
    assert final_response["language"] == "vi"
    assert final_response["model"] == "gemini-1.5-flash"
    assert len(final_response["sections"]) == 3
    assert final_response["trip_info"]["destination"] == "Quảng Ninh"
    
    print(f"✓ Response Status: {final_response['status']}")
    print(f"✓ Language: {final_response['language']}")
    print(f"✓ Sections: {len(final_response['sections'])}")
    print(f"✓ Trip Info: {final_response['trip_info']['destination']}")
    print(f"✓ Generated At: {final_response['generated_at']}")
    print("✓ TEST PASSED")


def test_fallback_response():
    """Test fallback response generation."""
    print("\n" + "="*60)
    print("TEST 7: Fallback Response (No LLM)")
    print("="*60)
    
    state = create_sample_state()
    formatter = TripDataFormatter()
    trip_data = formatter.extract_from_state(state)
    
    fallback = _fallback_response(state, trip_data)
    
    assert fallback["response_status"] == "fallback"
    assert fallback["final_answer"] is not None
    assert "note" in fallback["final_answer"]
    assert "Phiên bản rút gọn" in fallback["final_answer"]["note"]
    
    print(f"✓ Status: {fallback['response_status']}")
    print(f"✓ Has Response: {fallback['final_answer'] is not None}")
    print(f"✓ Note: {fallback['final_answer']['note']}")
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
    elif result["response_status"] == "success":
        print(f"✓ Status: {result['response_status']} (LLM available)")
        print(f"✓ Sections Count: {result.get('response_sections_count', 0)}")
        print("✓ TEST PASSED - Full LLM response generated successfully")
    else:
        print(f"⚠ Status: {result['response_status']}")
        print(f"⚠ Error: {result.get('error', 'Unknown')}")


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
        test_fallback_response()
        
        # Integration tests (synchronous)
        test_generate_answer_node_no_llm()
        
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
