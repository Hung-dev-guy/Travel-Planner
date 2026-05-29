"""
Test Scheduler.py with mock data for activities, accommodations, and transportations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.nodes.Scheduler import scheduler_node
from workflow.graph.stage import State
import json
from datetime import datetime, timedelta


def test_scheduler_with_full_data():
    """Test scheduler with complete trip data."""
    print("\n" + "="*70)
    print("TEST: Scheduler with Full Trip Data (3 days in Quảng Ninh)")
    print("="*70)
    
    # Create state with activities, accommodations, and transportations
    state = State(
        user_des_input="Test trip to Quảng Ninh",
        group_size=2,
        start_date="2026-06-01",
        end_date="2026-06-03",
        start_location="Hà Nội",
        destination=["Quảng Ninh"],
        personal_travel_style_des="Romantic, leisurely exploration",
        
        trip_metadata={
            "usr_des": "Test trip to explore Quảng Ninh",
            "start_date": "2026-06-01",
            "end_date": "2026-06-03",
            "total_days": "3",
            "age_range": "25-40",
            "start_location": "Hà Nội",
            "destination": "Quảng Ninh",
        },
        constraints={
            "travel_budget": 600_000,
            "group_size": 2,
            "daily_active_hours": "8-10",
            "language": "Vietnamese",
            "max_radius_distance": 50,
            "places_of_limitation": [],
            "health_limitations": [],
            "mobility_limitations": []
        },
        travel_preferences={
            "travel_style": ["adventure", "cultural"],
            "travel_pace": ["thong thả"],
            "food_style": ["local", "seafood"],
            "accommodation_style": ["comfortable"],
            "mobility_style": ["flexible"],
            "atmosphere": ["romantic"],
            "companion_type": ["Couples"]
        },
        
        # Mock activities
        activities=[
            {
                "_id": "act_001",
                "name": "Hạ Long Bay Cruise",
                "description": "UNESCO World Heritage limestone karsts cruise",
                "ward_name": "Hạ Long",
                "estimatedPrice": 150_000,
                "estimatedDuration": 180,  # 3 hours
                "suitabilityFor": ["Couples", "Family"],
                "atmosphere": "scenic",
            },
            {
                "_id": "act_002",
                "name": "Sung Sot Cave Exploration",
                "description": "Famous limestone cave with stunning formations",
                "ward_name": "Bạch Đằng",
                "estimatedPrice": 80_000,
                "estimatedDuration": 120,  # 2 hours
                "suitabilityFor": ["Couples", "Group", "Solo"],
                "atmosphere": "adventurous",
            },
            {
                "_id": "act_003",
                "name": "Titop Island Beach",
                "description": "Beautiful beach with crystal clear water",
                "ward_name": "Hạ Long",
                "estimatedPrice": 50_000,
                "estimatedDuration": 240,  # 4 hours
                "suitabilityFor": ["Couples", "Family"],
                "atmosphere": "relaxing",
            },
            {
                "_id": "act_004",
                "name": "Mong Cai Border Market",
                "description": "Traditional border trading town experience",
                "ward_name": "Mong Cai",
                "estimatedPrice": 30_000,
                "estimatedDuration": 150,  # 2.5 hours
                "suitabilityFor": ["Couples", "Group", "Solo"],
                "atmosphere": "cultural",
            },
            {
                "_id": "act_005",
                "name": "Cat Ba Island Hiking",
                "description": "Mountain trek with panoramic island views",
                "ward_name": "Cat Ba",
                "estimatedPrice": 70_000,
                "estimatedDuration": 180,  # 3 hours
                "suitabilityFor": ["Adventure Seekers"],
                "atmosphere": "adventurous",
            },
        ],
        
        # Mock accommodations
        accommodations=[
            {
                "_id": "acc_001",
                "name": "Luxury Halong Bay Hotel",
                "ward_name": "Hạ Long",
                "estimatedPrice": 250_000,  # Per night
                "amenities": ["WiFi", "AC", "Restaurant", "Beach access"],
                "accommodation_style": "comfortable",
            },
            {
                "_id": "acc_002",
                "name": "Deluxe Halong Bay Hotel",
                "ward_name": "Hạ Long",
                "estimatedPrice": 200_000,  # Per night
                "amenities": ["WiFi", "AC", "Restaurant"],
                "accommodation_style": "comfortable",
            },
            {
                "_id": "acc_003",
                "name": "Cat Ba Island Resort",
                "ward_name": "Cat Ba",
                "estimatedPrice": 180_000,  # Per night
                "amenities": ["WiFi", "AC", "Beach"],
                "accommodation_style": "comfortable",
            },
        ],
        
        # Mock transportations
        transportations=[
            {
                "name": "Coach (Hà Nội → Hạ Long)",
                "type": "coach",
                "from_ward": "Hà Nội",
                "to_ward": "Hạ Long",
                "distance_km": 160.0,
                "price_per_person": 125_000,
                "schedule": [
                    {
                        "departure": "06:00",
                        "arrival": "09:00",
                    }
                ],
            },
            {
                "name": "Bus (Hạ Long → Bạch Đằng)",
                "type": "bus",
                "from_ward": "Hạ Long",
                "to_ward": "Bạch Đằng",
                "distance_km": 25.0,
                "price_per_person": 68_000,
                "schedule": [
                    {
                        "departure": "10:00",
                        "arrival": "11:00",
                    }
                ],
            },
            {
                "name": "Coach (Hạ Long → Hà Nội)",
                "type": "coach",
                "from_ward": "Hạ Long",
                "to_ward": "Hà Nội",
                "distance_km": 160.0,
                "price_per_person": 125_000,
                "schedule": [
                    {
                        "departure": "17:00",
                        "arrival": "20:00",
                    }
                ],
            },
        ],
        
        scheduling=[],
    )
    
    # Run scheduler
    result = scheduler_node(state)
    
    # Display results
    print("\n" + "-"*70)
    print("SCHEDULING OUTPUT")
    print("-"*70)
    
    scheduling = result.get("scheduling", [])
    print(f"\nTotal days scheduled: {len(scheduling)}")
    
    for day in scheduling:
        print(f"\n{'='*70}")
        print(f"Day {day['day']}: {day['title']}")
        print(f"Date: {day['date']}")
        print(f"{'='*70}")
        
        items = day.get("items", [])
        print(f"\nScheduled Items ({len(items)}):")
        for i, item in enumerate(items, 1):
            print(f"\n  {i}. {item.get('name', 'N/A')}")
            print(f"     Time: {item.get('time_start')} - {item.get('time_end')}")
            print(f"     Type: {item.get('type')}")
            print(f"     Location: {item.get('location')}")
            print(f"     Cost: {item.get('cost', 0):,} VNĐ")
            if item.get('description'):
                print(f"     Description: {item.get('description')}")
        
        summary = day.get("day_summary", {})
        print(f"\nDay Summary:")
        print(f"  - Total cost: {summary.get('total_cost', 0):,} VNĐ")
        print(f"  - Activities: {summary.get('activities_count', 0)}")
        print(f"  - Meals: {summary.get('meals_count', 0)}")
        print(f"  - Travel time: {summary.get('travel_time_hours', 0)} hours")
        print(f"  - Active hours: {summary.get('active_hours', 0)} hours")
        print(f"  - Energy level: {summary.get('energy_level', 'N/A')}")
        print(f"  - Highlights: {', '.join(summary.get('highlights', []))}")
    
    # Calculate trip totals
    total_trip_cost = sum(day.get('day_summary', {}).get('total_cost', 0) for day in scheduling)
    total_activities = sum(day.get('day_summary', {}).get('activities_count', 0) for day in scheduling)
    
    print(f"\n{'='*70}")
    print("TRIP SUMMARY")
    print(f"{'='*70}")
    print(f"Total trip cost: {total_trip_cost:,} VNĐ")
    print(f"Cost per person: {total_trip_cost // 2:,} VNĐ")
    print(f"Total activities: {total_activities}")
    print(f"Budget available: 600,000 VNĐ per person")
    print(f"Budget used: {(total_trip_cost // 2):,} VNĐ per person ({((total_trip_cost // 2) / 300_000 * 100):.1f}%)")
    
    # Output JSON
    print(f"\n{'='*70}")
    print("JSON OUTPUT (Scheduling field)")
    print(f"{'='*70}")
    print(json.dumps(scheduling, indent=2, ensure_ascii=False))
    
    return result


if __name__ == "__main__":
    result = test_scheduler_with_full_data()
    print("\n✅ TEST COMPLETED SUCCESSFULLY")
