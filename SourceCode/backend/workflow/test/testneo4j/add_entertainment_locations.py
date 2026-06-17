"""
Add entertainment and activity locations to MongoDB Locations collection.
Bổ sung các địa điểm giải trí (activities) vào collection Locations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.db import get_mongo_db
from datetime import datetime

def add_entertainment_locations():
    """Add various entertainment and activity locations to MongoDB."""
    
    db = get_mongo_db("TravelPlanner")
    locations_collection = db["Locations"]
    
    entertainment_locations = [
        # ==================== Hạ Long ====================
        {
            "name": "Hạ Long Bay Cruise",
            "province": "Quảng Ninh",
            "ward_name": "Hạ Long",
            "type": "attraction",
            "category": "nature",
            "description": "UNESCO World Heritage limestone karsts cruise experience",
            "estimatedPrice": 150_000,
            "estimatedDuration": 240,
            "images": ["ha_long_1.jpg", "ha_long_2.jpg"],
            "suitabilityFor": ["Couples", "Family", "Group"],
            "atmosphere": ["scenic", "romantic"],
            "operatingHours": "06:00-17:00",
            "contact": "0555123456",
            "website": "halongbay.com",
            "coordinates": {"latitude": 20.8533, "longitude": 107.1860},
            "createdAt": datetime.now(),
            "tags": ["UNESCO", "boat", "scenic", "natural"],
        },
        {
            "name": "Sung Sot Cave",
            "province": "Quảng Ninh",
            "ward_name": "Hạ Long",
            "type": "attraction",
            "category": "nature",
            "description": "Famous limestone cave with stunning stalactite formations",
            "estimatedPrice": 80_000,
            "estimatedDuration": 120,
            "images": ["sung_sot_cave.jpg"],
            "suitabilityFor": ["Couples", "Family", "Solo", "Group"],
            "atmosphere": ["adventurous", "mysterious"],
            "operatingHours": "08:00-17:00",
            "contact": "0555234567",
            "website": "sungsotcave.vn",
            "coordinates": {"latitude": 20.8412, "longitude": 107.1975},
            "createdAt": datetime.now(),
            "tags": ["cave", "limestone", "formations", "adventure"],
        },
        {
            "name": "Titop Island Beach",
            "province": "Quảng Ninh",
            "ward_name": "Hạ Long",
            "type": "attraction",
            "category": "nature",
            "description": "Beautiful white sand beach with crystal clear water",
            "estimatedPrice": 50_000,
            "estimatedDuration": 240,
            "images": ["titop_beach.jpg"],
            "suitabilityFor": ["Couples", "Family", "Solo", "Group"],
            "atmosphere": ["relaxing", "scenic", "romantic"],
            "operatingHours": "06:00-18:00",
            "contact": "0555345678",
            "coordinates": {"latitude": 20.8275, "longitude": 107.1880},
            "createdAt": datetime.now(),
            "tags": ["beach", "swimming", "scenic", "water"],
        },
        
        # ==================== Bạch Đằng ====================
        {
            "name": "Bạch Đằng Strait Sunset View",
            "province": "Quảng Ninh",
            "ward_name": "Bạch Đằng",
            "type": "attraction",
            "category": "viewpoint",
            "description": "Historic strait with scenic sunset views and historical significance",
            "estimatedPrice": 0,
            "estimatedDuration": 120,
            "images": ["bach_dang_sunset.jpg"],
            "suitabilityFor": ["Couples", "Family", "Solo", "Group"],
            "atmosphere": ["romantic", "historic", "scenic"],
            "operatingHours": "06:00-18:00",
            "contact": "0555456789",
            "coordinates": {"latitude": 20.9333, "longitude": 107.2667},
            "createdAt": datetime.now(),
            "tags": ["viewpoint", "sunset", "historic", "free"],
        },
        
        # ==================== Mong Cai ====================
        {
            "name": "Mong Cai Border Market",
            "province": "Quảng Ninh",
            "ward_name": "Mong Cai",
            "type": "attraction",
            "category": "cultural",
            "description": "Traditional border trading town with authentic local culture and goods",
            "estimatedPrice": 30_000,
            "estimatedDuration": 180,
            "images": ["mong_cai_market.jpg"],
            "suitabilityFor": ["Solo", "Couples", "Family", "Group"],
            "atmosphere": ["cultural", "authentic", "vibrant"],
            "operatingHours": "07:00-17:00",
            "contact": "0555567890",
            "coordinates": {"latitude": 21.5333, "longitude": 107.9667},
            "createdAt": datetime.now(),
            "tags": ["market", "culture", "trading", "authentic"],
        },
        {
            "name": "Mong Cai Beach",
            "province": "Quảng Ninh",
            "ward_name": "Mong Cai",
            "type": "attraction",
            "category": "nature",
            "description": "Northern coast beach with pristine sands and local seafood stalls",
            "estimatedPrice": 0,
            "estimatedDuration": 180,
            "images": ["mong_cai_beach.jpg"],
            "suitabilityFor": ["Couples", "Family", "Group"],
            "atmosphere": ["relaxing", "scenic", "local"],
            "operatingHours": "06:00-18:00",
            "contact": "0555678901",
            "coordinates": {"latitude": 21.5400, "longitude": 107.9750},
            "createdAt": datetime.now(),
            "tags": ["beach", "seaside", "free", "local"],
        },
        
        # ==================== Cat Ba ====================
        {
            "name": "Cat Ba Island Hiking",
            "province": "Quảng Ninh",
            "ward_name": "Cat Ba",
            "type": "attraction",
            "category": "adventure",
            "description": "Mountain trek with panoramic island and sea views",
            "estimatedPrice": 70_000,
            "estimatedDuration": 180,
            "images": ["cat_ba_hiking.jpg"],
            "suitabilityFor": ["Adventure Seekers", "Couples", "Group"],
            "atmosphere": ["adventurous", "scenic", "active"],
            "operatingHours": "06:00-17:00",
            "contact": "0555789012",
            "website": "catbaisland.vn",
            "coordinates": {"latitude": 20.7333, "longitude": 107.3667},
            "createdAt": datetime.now(),
            "tags": ["hiking", "mountain", "views", "adventure"],
        },
        {
            "name": "Cat Ba Island Beaches",
            "province": "Quảng Ninh",
            "ward_name": "Cat Ba",
            "type": "attraction",
            "category": "nature",
            "description": "Multiple beautiful beaches with calm waters and beach activities",
            "estimatedPrice": 30_000,
            "estimatedDuration": 240,
            "images": ["cat_ba_beach.jpg"],
            "suitabilityFor": ["Couples", "Family", "Solo", "Group"],
            "atmosphere": ["relaxing", "scenic", "fun"],
            "operatingHours": "06:00-18:00",
            "contact": "0555890123",
            "coordinates": {"latitude": 20.7500, "longitude": 107.3500},
            "createdAt": datetime.now(),
            "tags": ["beach", "water", "activities", "scenic"],
        },
        {
            "name": "Cat Ba National Park",
            "province": "Quảng Ninh",
            "ward_name": "Cat Ba",
            "type": "attraction",
            "category": "nature",
            "description": "Diverse ecosystem with forests, limestone, and wildlife",
            "estimatedPrice": 120_000,
            "estimatedDuration": 300,
            "images": ["cat_ba_national_park.jpg"],
            "suitabilityFor": ["Adventure Seekers", "Nature Lovers", "Group"],
            "atmosphere": ["natural", "adventurous", "pristine"],
            "operatingHours": "06:00-17:00",
            "contact": "0555901234",
            "website": "catbanationalpark.vn",
            "coordinates": {"latitude": 20.7200, "longitude": 107.3500},
            "createdAt": datetime.now(),
            "tags": ["national_park", "nature", "hiking", "wildlife"],
        },
        
        # ==================== Hòn Gai (Hạ Long City Center) ====================
        {
            "name": "Quảng Ninh Museum",
            "province": "Quảng Ninh",
            "ward_name": "Hòn Gai",
            "type": "attraction",
            "category": "cultural",
            "description": "Local history and culture museum with exhibits on coal mining heritage",
            "estimatedPrice": 40_000,
            "estimatedDuration": 120,
            "images": ["museum.jpg"],
            "suitabilityFor": ["Solo", "Couples", "Family", "Group"],
            "atmosphere": ["educational", "cultural", "historic"],
            "operatingHours": "08:00-17:00",
            "contact": "0555012345",
            "website": "quangninh-museum.vn",
            "coordinates": {"latitude": 20.9667, "longitude": 107.0333},
            "createdAt": datetime.now(),
            "tags": ["museum", "culture", "history", "education"],
        },
        {
            "name": "Hạ Long Night Market",
            "province": "Quảng Ninh",
            "ward_name": "Hòn Gai",
            "type": "attraction",
            "category": "cultural",
            "description": "Night market with local food, crafts, and entertainment",
            "estimatedPrice": 100_000,
            "estimatedDuration": 180,
            "images": ["night_market.jpg"],
            "suitabilityFor": ["Couples", "Family", "Group"],
            "atmosphere": ["vibrant", "fun", "local"],
            "operatingHours": "18:00-23:00",
            "contact": "0555123456",
            "coordinates": {"latitude": 20.9700, "longitude": 107.0400},
            "createdAt": datetime.now(),
            "tags": ["market", "night", "food", "shopping", "fun"],
        },
        
        # ==================== Cát Bà (Town) ====================
        {
            "name": "Cát Bà Island Diving",
            "province": "Quảng Ninh",
            "ward_name": "Cat Ba",
            "type": "attraction",
            "category": "adventure",
            "description": "Scuba diving with rich marine life and coral reefs",
            "estimatedPrice": 200_000,
            "estimatedDuration": 180,
            "images": ["diving.jpg"],
            "suitabilityFor": ["Adventure Seekers", "Couples", "Group"],
            "atmosphere": ["adventurous", "exciting", "scenic"],
            "operatingHours": "07:00-17:00",
            "contact": "0555234567",
            "website": "catba-diving.vn",
            "coordinates": {"latitude": 20.7500, "longitude": 107.3600},
            "createdAt": datetime.now(),
            "tags": ["diving", "water_sports", "adventure", "marine"],
        },
        
        # ==================== Yên Tử ====================
        {
            "name": "Yên Tử Mountain Temple",
            "province": "Quảng Ninh",
            "ward_name": "Yên Tử",
            "type": "attraction",
            "category": "cultural",
            "description": "Ancient Buddhist temple complex with spiritual significance and scenic views",
            "estimatedPrice": 50_000,
            "estimatedDuration": 240,
            "images": ["yen_tu_temple.jpg"],
            "suitabilityFor": ["Solo", "Couples", "Family", "Group"],
            "atmosphere": ["spiritual", "peaceful", "scenic"],
            "operatingHours": "07:00-17:00",
            "contact": "0555345678",
            "website": "yentumountain.vn",
            "coordinates": {"latitude": 21.0667, "longitude": 107.0833},
            "createdAt": datetime.now(),
            "tags": ["temple", "religion", "mountain", "scenic", "history"],
        },
        
        # ==================== Đông Triều ====================
        {
            "name": "Đông Triều Waterfall",
            "province": "Quảng Ninh",
            "ward_name": "Đông Triều",
            "type": "attraction",
            "category": "nature",
            "description": "Beautiful waterfall in forest setting with natural pool for swimming",
            "estimatedPrice": 30_000,
            "estimatedDuration": 180,
            "images": ["waterfall.jpg"],
            "suitabilityFor": ["Couples", "Family", "Group"],
            "atmosphere": ["natural", "refreshing", "scenic"],
            "operatingHours": "08:00-17:00",
            "contact": "0555456789",
            "coordinates": {"latitude": 21.0833, "longitude": 106.7500},
            "createdAt": datetime.now(),
            "tags": ["waterfall", "nature", "swimming", "hiking"],
        },
        
        # ==================== Vân Đồn ====================
        {
            "name": "Vân Đồn Ancient Town",
            "province": "Quảng Ninh",
            "ward_name": "Vân Đồn",
            "type": "attraction",
            "category": "cultural",
            "description": "Historic trading port town with colonial architecture",
            "estimatedPrice": 0,
            "estimatedDuration": 120,
            "images": ["van_don_town.jpg"],
            "suitabilityFor": ["Solo", "Couples", "Family", "Group"],
            "atmosphere": ["historic", "charming", "cultural"],
            "operatingHours": "08:00-17:00",
            "contact": "0555567890",
            "coordinates": {"latitude": 21.1667, "longitude": 107.3667},
            "createdAt": datetime.now(),
            "tags": ["historic", "architecture", "walking", "culture"],
        },
        {
            "name": "Vân Đồn Beach",
            "province": "Quảng Ninh",
            "ward_name": "Vân Đồn",
            "type": "attraction",
            "category": "nature",
            "description": "Sandy beach with calm waters, perfect for relaxation and water sports",
            "estimatedPrice": 0,
            "estimatedDuration": 240,
            "images": ["van_don_beach.jpg"],
            "suitabilityFor": ["Couples", "Family", "Solo", "Group"],
            "atmosphere": ["relaxing", "scenic"],
            "operatingHours": "06:00-18:00",
            "contact": "0555678901",
            "coordinates": {"latitude": 21.1800, "longitude": 107.3600},
            "createdAt": datetime.now(),
            "tags": ["beach", "water_sports", "free", "relaxing"],
        },
    ]
    
    print("="*70)
    print("ADDING ENTERTAINMENT & ACTIVITY LOCATIONS TO MONGODB")
    print("="*70)
    
    try:
        # Check existing locations
        existing_count = locations_collection.count_documents({})
        print(f"\n📍 Existing locations in database: {existing_count}")
        
        # Insert new locations
        result = locations_collection.insert_many(entertainment_locations, ordered=False)
        
        print(f"\n✅ Successfully inserted {len(result.inserted_ids)} new entertainment locations!")
        
        # Show summary by category
        categories = {}
        for loc in entertainment_locations:
            cat = loc.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n📊 LOCATIONS BY CATEGORY:")
        for category, count in sorted(categories.items()):
            print(f"  - {category}: {count}")
        
        # Show summary by ward
        wards = {}
        for loc in entertainment_locations:
            ward = loc.get("ward_name", "unknown")
            wards[ward] = wards.get(ward, 0) + 1
        
        print(f"\n🏘️  LOCATIONS BY WARD:")
        for ward, count in sorted(wards.items()):
            print(f"  - {ward}: {count}")
        
        # Verify insertion
        total_after = locations_collection.count_documents({})
        print(f"\n✅ Total locations after insertion: {total_after}")
        
        # Show sample of inserted locations
        print(f"\n📋 SAMPLE LOCATIONS INSERTED:")
        samples = locations_collection.find({}).limit(5)
        for i, loc in enumerate(samples, 1):
            print(f"\n  {i}. {loc.get('name')}")
            print(f"     Ward: {loc.get('ward_name')}")
            print(f"     Category: {loc.get('category')}")
            print(f"     Price: {loc.get('estimatedPrice', 0):,} VNĐ")
            print(f"     Duration: {loc.get('estimatedDuration', 0)} min")
        
        print(f"\n" + "="*70)
        print("✅ ENTERTAINMENT LOCATIONS ADDED SUCCESSFULLY")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = add_entertainment_locations()
    exit(0 if success else 1)
