import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.db import get_mongo_db
from datetime import datetime


def add_coach_transportation():
    """Add a Coach transportation from Hà Nội to Quảng Ninh."""
    print("\n" + "="*70)
    print("ADDING COACH TRANSPORTATION: HÀ NỘI → QUẢNG NINH")
    print("="*70)
    
    db = get_mongo_db("TravelDB")
    
    # Get locations in Hà Nội and Quảng Ninh
    hanoi_locations = list(db["Locations"].find(
        {"province_name": "Hà Nội"},
        {"locationId": 1, "_id": 0}
    ))
    
    quangninh_locations = list(db["Locations"].find(
        {"province_name": "Quảng Ninh"},
        {"locationId": 1, "_id": 0}
    ))
    
    print(f"\n📍 Locations found:")
    print(f"  Hà Nội: {len(hanoi_locations)} locations")
    print(f"  Quảng Ninh: {len(quangninh_locations)} locations")
    
    # Combine all location IDs
    available_location_ids = [l["locationId"] for l in hanoi_locations + quangninh_locations]
    
    print(f"  Total available locations: {len(available_location_ids)}")
    
    # Create Coach transportation entry
    coach_entry = {
        "transportId": "T-COACH-HN-QN",
        "transportType": "Coach",
        "name": "Coach (Hà Nội → Hạ Long)",
        "description": "Dịch vụ vận chuyển coach từ Hà Nội đến Hạ Long. Khoảng cách: 160km. Thích hợp cho nhóm đông, tiết kiệm chi phí, thoải mái cho chuyến đi dài.",
        "from_ward": "Hà Nội",
        "to_ward": "Hạ Long",
        "province_name": "Hà Nội - Hạ Long",
        "distance_km": 160,
        "price": 250_000,  # Total price for the coach
        "price_per_person": 125_000,  # Estimated per person (for 2 people)
        "estimatedDuration": 3,  # 3 hours
        "available_in": available_location_ids,  # List of location IDs where this transport is available
        "suitabilityFor": ["Solo", "Couples", "Family", "Friends", "Group"],
        "operatingHours": {
            "open": "05:00",
            "close": "22:00"
        },
        "schedule": [
            {"departure": "06:00", "arrival": "09:00"},
            {"departure": "08:00", "arrival": "11:00"},
            {"departure": "10:00", "arrival": "13:00"},
            {"departure": "14:00", "arrival": "17:00"},
            {"departure": "16:00", "arrival": "19:00"},
            {"departure": "18:00", "arrival": "21:00"},
        ],
        "createdAt": datetime.now(),
    }
    
    # Insert or update
    try:
        result = db["Transportations"].find_one_and_update(
            {"transportId": "T-COACH-HN-QN"},
            {"$set": coach_entry},
            upsert=True,
            return_document=True
        )
        
        if result:
            print(f"\n✅ Coach transportation added/updated successfully!")
            print(f"\n📝 Coach Entry Details:")
            print(f"  ID: {coach_entry['transportId']}")
            print(f"  Route: {coach_entry['name']}")
            print(f"  Distance: {coach_entry['distance_km']}km")
            print(f"  Price/person: {coach_entry['price_per_person']:,} VNĐ")
            print(f"  Duration: ~{coach_entry['estimatedDuration']} hours")
            print(f"  Available in {len(available_location_ids)} locations")
            print(f"  Operating hours: {coach_entry['operatingHours']['open']} - {coach_entry['operatingHours']['close']}")
            print(f"  Daily schedules: {len(coach_entry['schedule'])} trips")
            
            # Show sample schedules
            print(f"\n  Sample departure times:")
            for schedule in coach_entry['schedule'][:3]:
                print(f"    - {schedule['departure']} (arrival: {schedule['arrival']})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error adding coach: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = add_coach_transportation()
    
    print("\n" + "="*70)
    if success:
        print("✅ COACH TRANSPORTATION ADDED SUCCESSFULLY")
    else:
        print("❌ FAILED TO ADD COACH TRANSPORTATION")
    print("="*70)
    
    exit(0 if success else 1)
