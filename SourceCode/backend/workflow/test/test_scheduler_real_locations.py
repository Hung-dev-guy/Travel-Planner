"""
Test Scheduler with real entertainment locations from MongoDB.
Kiểm tra Scheduler với các địa điểm giải trí thực từ MongoDB.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.nodes.Scheduler import scheduler_node
from workflow.db import get_mongo_db, reset_mongo_connection
from workflow.graph.stage import State
import json
from datetime import datetime, timedelta


def test_scheduler_with_real_locations():
    """Test scheduler using real locations from MongoDB."""
    print("\n" + "="*70)
    print("TEST: Scheduler with Real Entertainment Locations from MongoDB")
    print("="*70)
    
    # Reset connection
    reset_mongo_connection()
    
    # Fetch real locations from MongoDB
    db = get_mongo_db("TravelPlanner")
    locations_collection = db["Locations"]
    
    # Get activities from different wards
    activities = []
    for loc in locations_collection.find({"category": {"$in": ["nature", "adventure", "cultural", "viewpoint"]}}):
        activities.append({
            "_id": str(loc.get("_id")),
            "name": loc.get("name"),
            "description": loc.get("description", ""),
            "ward_name": loc.get("ward_name"),
            "estimatedPrice": loc.get("estimatedPrice", 0),
            "estimatedDuration": loc.get("estimatedDuration", 60),
            "suitabilityFor": loc.get("suitabilityFor", ["Couples"]),
            "category": loc.get("category"),
        })
    
    # Get accommodations (mock since we don't have real accommodation data yet)
    accommodations = [
        {
            "_id": "acc_001",
            "name": "Luxury Halong Bay Hotel",
            "ward_name": "Hạ Long",
            "estimatedPrice": 250_000,
        },
        {
            "_id": "acc_002",
            "name": "Budget Halong Hotel",
            "ward_name": "Hạ Long",
            "estimatedPrice": 150_000,
        },
        {
            "_id": "acc_003",
            "name": "Cozy Halong Hotel",
            "ward_name": "Hạ Long",
            "estimatedPrice": 180_000,
        },
    ]
    
    # Get transportations (mock for now)
    transportations = [
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
    ]
    
    # Create state
    state = State(
        user_des_input="Test trip with real entertainment locations",
        group_size=2,
        start_date="2026-06-01",
        end_date="2026-06-03",
        start_location="Hà Nội",
        destination=["Quảng Ninh"],
        personal_travel_style_des="Adventure and cultural exploration",
        
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
        
        activities=activities,
        accommodations=accommodations,
        transportations=transportations,
        scheduling=[],
    )
    
    print(f"\n📊 DATA SUMMARY:")
    print(f"  Activities loaded: {len(activities)}")
    print(f"  Accommodations: {len(accommodations)}")
    print(f"  Transportations: {len(transportations)}")
    
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
            type_icon = {
                "transportation": "🚌",
                "activity": "🎭",
                "accommodation": "🏨",
                "meal": "🍽️",
                "rest": "😴"
            }.get(item.get("type"), "📌")
            
            print(f"\n  {i}. {type_icon} {item.get('name', 'N/A')}")
            print(f"     Time: {item.get('time_start')} - {item.get('time_end')}")
            if item.get('location'):
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
        if summary.get('highlights'):
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
    print(f"Budget per person: 300,000 VNĐ")
    print(f"Budget utilization: {((total_trip_cost // 2) / 300_000 * 100):.1f}%")
    
    # Show activity details
    print(f"\n{'='*70}")
    print("SELECTED ACTIVITIES DETAILS")
    print(f"{'='*70}")
    selected_activities = {}
    for day in scheduling:
        for item in day.get('items', []):
            if item.get('type') == 'activity':
                name = item.get('name')
                location = item.get('location')
                cost = item.get('cost', 0)
                category = next((a.get('category') for a in activities if a.get('name') == name), 'unknown')
                if name not in selected_activities:
                    selected_activities[name] = {
                        "location": location,
                        "cost": cost,
                        "category": category,
                        "count": 0
                    }
                selected_activities[name]["count"] += 1
    
    if selected_activities:
        for i, (name, details) in enumerate(selected_activities.items(), 1):
            print(f"\n{i}. {name}")
            print(f"   Location: {details['location']}")
            print(f"   Category: {details['category']}")
            print(f"   Cost: {details['cost']:,} VNĐ")
    
    return result


if __name__ == "__main__":
    result = test_scheduler_with_real_locations()
    print("\n✅ TEST COMPLETED SUCCESSFULLY")
