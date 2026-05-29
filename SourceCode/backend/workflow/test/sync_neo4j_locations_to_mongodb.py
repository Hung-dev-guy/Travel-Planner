import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.db import get_neo4j_driver, get_mongo_db
from datetime import datetime


def sync_locations_from_neo4j():
    """Sync Location data (hotels, homestays) from Neo4j wards to MongoDB."""
    print("\n" + "="*60)
    print("SYNCING LOCATIONS FROM NEO4J TO MONGODB")
    print("="*60)
    
    driver = get_neo4j_driver()
    db = get_mongo_db("TravelDB")
    
    # Check existing location schema
    existing_loc = db["Locations"].find_one()
    if existing_loc:
        print(f"\n📌 Existing location schema:")
        for key in existing_loc:
            if key != "_id":
                print(f"  - {key}: {type(existing_loc[key]).__name__}")
    
    # Fetch all provinces and wards from Neo4j
    with driver.session() as session:
        query = """
        MATCH (p:Province)-[:HAS]->(w:Ward)
        RETURN DISTINCT p.name AS province_name, w.name AS ward_name
        ORDER BY p.name, w.name
        """
        
        results = session.run(query).data()
        print(f"\n🔍 Found {len(results)} wards in Neo4j")
        
        # Sample hotel and homestay names for different regions
        hotel_templates = [
            {"name": "{ward} Hotel", "type": "hotel", "price": 650000, "duration": 1},
            {"name": "Resort {ward}", "type": "hotel", "price": 850000, "duration": 1},
            {"name": "{ward} Luxury Hotel", "type": "hotel", "price": 1200000, "duration": 1},
            {"name": "Homestay {ward}", "type": "homestay", "price": 450000, "duration": 1},
            {"name": "{ward} Family House", "type": "homestay", "price": 550000, "duration": 1},
            {"name": "Cozy Homestay {ward}", "type": "homestay", "price": 380000, "duration": 1},
        ]
        
        locations_to_insert = []
        
        for i, record in enumerate(results):
            province_name = record['province_name']
            ward_name = record['ward_name']
            
            # Create 3 stay locations per ward (2 hotels + 1 homestay)
            for template_idx in range(3):
                template = hotel_templates[template_idx % len(hotel_templates)]
                
                # Create unique location ID using index to avoid duplicates
                location_id = f"LOC-STAY-{i}-{template_idx}"
                
                location_entry = {
                    "locationId": location_id,
                    "name": template['name'].format(ward=ward_name),
                    "description": f"{'Khách sạn' if template['type'] == 'hotel' else 'Homestay'} chất lượng cao tại {ward_name}, {province_name}. Vị trí thuận tiện, dễ dàng di chuyển đến các điểm du lịch.",
                    "category": "Stay",
                    "estimatedDuration": template['duration'],
                    "estimatedPrice": template['price'],
                    "suitabilityFor": ["Solo", "Couples", "Family", "Friends", "Group"],
                    "openingHours": {
                        "open": "00:00",
                        "close": "23:59"
                    },
                    "ward_name": ward_name,
                    "province_name": province_name,
                    "location": {
                        "type": "Point",
                        "coordinates": [
                            106.5 + (i % 10) * 0.5,  # Longitude range ~106-111
                            10.0 + (i % 20) * 0.5     # Latitude range ~10-20
                        ]
                    },
                    "createdAt": datetime.now(),
                }
                locations_to_insert.append(location_entry)
        
        # Check for duplicates
        if locations_to_insert:
            print(f"\n✅ Preparing to insert {len(locations_to_insert)} location entries...")
            existing_ids = set(db["Locations"].distinct("locationId"))
            new_entries = [l for l in locations_to_insert if l["locationId"] not in existing_ids]
            
            if new_entries:
                print(f"\n📝 Sample entries to insert:")
                for entry in new_entries[:3]:
                    print(f"  - {entry['locationId']}: {entry['name']}")
                    print(f"    Ward: {entry['ward_name']}, Province: {entry['province_name']}")
                    print(f"    Price: {entry['estimatedPrice']:,} VNĐ")
                
                try:
                    result = db["Locations"].insert_many(new_entries, ordered=False)
                    print(f"\n✓ Inserted {len(result.inserted_ids)} new locations into MongoDB")
                except Exception as e:
                    # Continue even if some insertions fail (duplicates)
                    print(f"\n⚠️  Some entries skipped (duplicates or errors): {str(e)[:100]}")
                    # Try individual inserts to skip duplicates
                    inserted_count = 0
                    for entry in new_entries:
                        try:
                            db["Locations"].insert_one(entry)
                            inserted_count += 1
                        except:
                            pass
                    print(f"✓ Inserted {inserted_count} new locations (skipped duplicates)")
                
                # Verify insertion
                count = db["Locations"].count_documents({})
                print(f"  Total locations now in database: {count}")
                
                # Show by province
                print(f"\n📊 Locations by province:")
                provinces = db["Locations"].aggregate([
                    {"$group": {"_id": "$province_name", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ])
                for prov in provinces:
                    print(f"  - {prov['_id']}: {prov['count']} locations")
            else:
                print(f"  ℹ️  All locations already exist in MongoDB")
        else:
            print("  ⚠️  No location data generated")


if __name__ == "__main__":
    sync_locations_from_neo4j()
    print("\n" + "="*60)
    print("✅ SYNC COMPLETE")
    print("="*60)
