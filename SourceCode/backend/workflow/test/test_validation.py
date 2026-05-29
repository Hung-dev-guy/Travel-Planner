"""
Test suite for Validation Agent

Tests validation of schedules under various scenarios:
1. Perfect schedule (score ~95%)
2. Budget overrun (score ~30%)
3. Over-packed schedule (score ~50%)
4. Health/safety constraints (score ~60%)
5. Iterative improvement with feedback loop
"""

import sys
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from workflow.nodes.Validation_agent import (
    validation_node,
    validation_feedback_loop,
    ValidationIssue,
    ValidationRecommendation
)


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_validation_result(result):
    """Pretty print validation result"""
    print(result["summary"])
    
    if result.get("issues"):
        print(f"\n📋 Issues ({len(result['issues'])}):")
        for issue in result["issues"]:
            severity_icon = "🔴" if issue["severity"] == "critical" else "🟡" if issue["severity"] == "warning" else "ℹ️"
            day_str = f" (Day {issue['day']})" if issue["day"] else ""
            print(f"  {severity_icon} {issue['message']}{day_str}")
    
    if result.get("recommendations"):
        print(f"\n💡 Recommendations ({len(result['recommendations'])}):")
        for i, rec in enumerate(result["recommendations"], 1):
            priority_icon = "🔥" if rec["priority"] == "high" else "⚠️" if rec["priority"] == "medium" else "💬"
            print(f"  {i}. {priority_icon} {rec['suggestion']}")


# ============================================================================
# Test Scenarios
# ============================================================================

def test_perfect_schedule():
    """Test 1: Perfect schedule (all criteria met)"""
    print_section("Test 1: Perfect Schedule")
    
    state = {
        "scheduling": [
            {
                "day": 1,
                "day_type": "arrival",
                "items": [
                    {"type": "transport", "name": "Bus from airport", "duration": 120, "cost": 68000, "from_location": "Hà Nội", "to_location": "Hạ Long"},
                    {"type": "meal", "name": "Lunch", "cost": 100000, "duration": 60},
                    {"type": "accommodation", "name": "Hạ Long Hotel", "cost": 100000, "duration": 480, "quality_level": "comfortable"},
                ]
            },
            {
                "day": 2,
                "day_type": "full",
                "items": [
                    {"type": "meal", "name": "Breakfast", "cost": 80000, "duration": 60},
                    {"type": "activity", "name": "Hạ Long Bay Cruise", "category": "nature", "cost": 150000, "duration": 240, "suitability": ["Couples", "Families"]},
                    {"type": "meal", "name": "Lunch", "cost": 100000, "duration": 60},
                    {"type": "activity", "name": "Sung Sot Cave", "category": "nature", "cost": 80000, "duration": 120, "suitability": ["Families", "Adventure"]},
                    {"type": "meal", "name": "Dinner", "cost": 120000, "duration": 60},
                    {"type": "accommodation", "name": "Hạ Long Hotel", "cost": 100000, "duration": 480, "quality_level": "comfortable"},
                ]
            },
            {
                "day": 3,
                "day_type": "departure",
                "items": [
                    {"type": "meal", "name": "Breakfast", "cost": 80000, "duration": 60},
                    {"type": "activity", "name": "Titop Island Beach", "category": "nature", "cost": 50000, "duration": 120, "suitability": ["Families"]},
                    {"type": "meal", "name": "Lunch", "cost": 100000, "duration": 60},
                    {"type": "transport", "name": "Bus to airport", "duration": 120, "cost": 68000, "from_location": "Hạ Long", "to_location": "Hà Nội"},
                ]
            }
        ],
        "constraints": {
            "travel_budget": 1500000,  # Sufficient budget
            "group_size": 2,
            "daily_active_hours": 10,
            "health_limitations": []
        },
        "travel_preferences": {
            "travel_style": ["nature", "cultural"],
            "travel_pace": "moderate",
            "accommodation_style": "comfortable",
            "companion_type": "couple"
        }
    }
    
    state = validation_node(state)
    print_validation_result(state["validation"])
    
    return state["validation"]["overall_score"]


def test_budget_overrun():
    """Test 2: Budget significantly overrun"""
    print_section("Test 2: Budget Overrun Schedule")
    
    state = {
        "scheduling": [
            {
                "day": 1,
                "day_type": "arrival",
                "items": [
                    {"type": "transport", "name": "Flight", "duration": 120, "cost": 500000},
                    {"type": "accommodation", "name": "5-star Resort", "cost": 800000, "duration": 480},
                ]
            },
            {
                "day": 2,
                "day_type": "full",
                "items": [
                    {"type": "accommodation", "name": "5-star Resort", "cost": 800000, "duration": 480},
                    {"type": "activity", "name": "Private Yacht Tour", "category": "luxury", "cost": 3000000, "duration": 240},
                    {"type": "activity", "name": "Diving with Instructor", "category": "adventure", "cost": 2000000, "duration": 300},
                ]
            },
            {
                "day": 3,
                "day_type": "departure",
                "items": [
                    {"type": "activity", "name": "Spa Treatment", "category": "luxury", "cost": 1500000, "duration": 120},
                    {"type": "transport", "name": "Flight", "duration": 120, "cost": 500000},
                ]
            }
        ],
        "constraints": {
            "travel_budget": 1500000,  # 1.5 million but spending 8.1 million
            "group_size": 1,
            "daily_active_hours": 8,
            "health_limitations": []
        },
        "travel_preferences": {
            "travel_style": ["luxury"],
            "travel_pace": "leisurely"
        }
    }
    
    state = validation_node(state)
    print_validation_result(state["validation"])
    
    return state["validation"]["overall_score"]


def test_overpacked_schedule():
    """Test 3: Overpacked with exhausting daily hours"""
    print_section("Test 3: Overpacked Schedule")
    
    state = {
        "scheduling": [
            {
                "day": 1,
                "day_type": "arrival",
                "items": [
                    {"type": "transport", "name": "Bus", "duration": 60, "cost": 50000},
                    {"type": "accommodation", "name": "Hotel", "cost": 150000, "duration": 480},
                ]
            },
            {
                "day": 2,
                "day_type": "full",
                "items": [
                    {"type": "activity", "name": "Activity 1", "category": "nature", "cost": 100000, "duration": 180, "suitability": ["Everyone"]},
                    {"type": "activity", "name": "Activity 2", "category": "adventure", "cost": 150000, "duration": 180, "suitability": ["Adventure"]},
                    {"type": "activity", "name": "Activity 3", "category": "cultural", "cost": 80000, "duration": 180, "suitability": ["Cultural"]},
                    {"type": "activity", "name": "Activity 4", "category": "nature", "cost": 120000, "duration": 180, "suitability": ["Nature"]},
                    {"type": "activity", "name": "Activity 5", "category": "adventure", "cost": 200000, "duration": 180, "suitability": ["Adventure"]},
                ]
            },
            {
                "day": 3,
                "day_type": "departure",
                "items": [
                    {"type": "transport", "name": "Bus", "duration": 60, "cost": 50000},
                ]
            }
        ],
        "constraints": {
            "travel_budget": 1500000,
            "group_size": 2,
            "daily_active_hours": 8,  # Constraint: max 8 hours
            "health_limitations": []
        },
        "travel_preferences": {
            "travel_style": ["adventure", "nature"],
            "travel_pace": "fast"
        }
    }
    
    state = validation_node(state)
    print_validation_result(state["validation"])
    
    return state["validation"]["overall_score"]


def test_health_constraints():
    """Test 4: Health constraints and safety validation"""
    print_section("Test 4: Health & Safety Constraints")
    
    state = {
        "scheduling": [
            {
                "day": 1,
                "day_type": "arrival",
                "items": [
                    {"type": "transport", "name": "Bus", "duration": 120, "cost": 68000},
                    {"type": "accommodation", "name": "Hotel", "cost": 100000, "duration": 480},
                ]
            },
            {
                "day": 2,
                "day_type": "full",
                "items": [
                    {"type": "activity", "name": "Cát Bà Hiking Trek", "category": "hiking", "cost": 150000, "duration": 240, "suitability": ["Adventure"]},
                ]
            },
            {
                "day": 3,
                "day_type": "departure",
                "items": [
                    {"type": "transport", "name": "Bus", "duration": 120, "cost": 68000},
                ]
            }
        ],
        "constraints": {
            "travel_budget": 1000000,
            "group_size": 1,
            "daily_active_hours": 10,
            "health_limitations": ["limited walking", "mobility issues"],  # But scheduled for hiking!
            "age_range": (60, 75)
        },
        "travel_preferences": {
            "travel_style": ["relaxation"],
            "travel_pace": "leisurely"
        }
    }
    
    state = validation_node(state)
    print_validation_result(state["validation"])
    
    return state["validation"]["overall_score"]


def test_feedback_loop():
    """Test 5: Iterative validation with feedback loop"""
    print_section("Test 5: Validation Feedback Loop (Iterative Improvement)")
    
    initial_state = {
        "scheduling": [
            {
                "day": 1,
                "day_type": "arrival",
                "items": [
                    {"type": "transport", "name": "Bus", "duration": 120, "cost": 68000},
                    {"type": "accommodation", "name": "Budget Hotel", "cost": 50000, "duration": 480},
                ]
            },
            {
                "day": 2,
                "day_type": "full",
                "items": [
                    {"type": "activity", "name": "Diving", "category": "adventure", "cost": 200000, "duration": 240},
                    {"type": "activity", "name": "Hiking", "category": "adventure", "cost": 100000, "duration": 240},
                ]
            },
            {
                "day": 3,
                "day_type": "departure",
                "items": [
                    {"type": "transport", "name": "Bus", "duration": 120, "cost": 68000},
                ]
            }
        ],
        "constraints": {
            "travel_budget": 300000,  # 300k budget but spending 486k
            "group_size": 1,
            "daily_active_hours": 8,
            "health_limitations": []
        },
        "travel_preferences": {
            "travel_style": ["nature"],
            "travel_pace": "moderate"
        }
    }
    
    # Run feedback loop
    final_state, history = validation_feedback_loop(
        initial_state,
        max_iterations=3,
        min_acceptable_score=70
    )
    
    # Print iteration history
    print("📊 Iteration History:\n")
    for record in history:
        status_icon = "✅" if record["score"] >= 70 else "⚠️"
        print(f"  Iteration {record['iteration']}: {status_icon} Score={record['score']:.0f}%, Status={record['status']}")
        for category, score in record["category_scores"].items():
            print(f"    - {category}: {score:.0f}%")
    
    print(f"\n📈 Improvement: {history[0]['score']:.0f}% → {history[-1]['score']:.0f}%")
    
    final_result = final_state.get("validation", {})
    print_validation_result(final_result)
    
    return history[-1]["score"]


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  VALIDATION AGENT TEST SUITE")
    print("="*80)
    
    results = {}
    
    # Run all tests
    try:
        results["Perfect Schedule"] = test_perfect_schedule()
        results["Budget Overrun"] = test_budget_overrun()
        results["Overpacked Schedule"] = test_overpacked_schedule()
        results["Health Constraints"] = test_health_constraints()
        results["Feedback Loop"] = test_feedback_loop()
    except Exception as e:
        print(f"\n❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print_section("TEST SUMMARY")
    
    print("Score Comparison:\n")
    for test_name, score in results.items():
        status_icon = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
        print(f"  {status_icon} {test_name:.<40} {score:.0f}%")
    
    print(f"\n✅ All tests completed successfully!")
