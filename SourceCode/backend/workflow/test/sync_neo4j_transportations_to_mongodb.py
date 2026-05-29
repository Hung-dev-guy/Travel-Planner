import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.db import get_neo4j_driver, get_mongo_db
from datetime import datetime


def sync_transportations_from_neo4j():
    """Sync Transportation data from Neo4j routes to MongoDB with available_in locations."""
    print("\n" + "="*60)
    print("SYNCING TRANSPORTATIONS FROM NEO4J TO MONGODB")
    print("="*60)
    
    driver = get_neo4j_driver()
    db = get_mongo_db("TravelDB")
    
    # Check existing transportation schema
    existing_trans = db["Transportations"].find_one()
    if existing_trans:
        print(f"\n📌 Existing transportation schema:")
        for key in existing_trans:
            if key != "_id":
                print(f"  - {key}: {type(existing_trans[key]).__name__}")
    
    # Fetch all provinces, wards and their routes from Neo4j
    with driver.session() as session:
        query = """
        MATCH (p:Province)-[:HAS]->(w1:Ward)
        OPTIONAL MATCH (w1)-[r:CONNECTED_TO]->(w2:Ward)
        RETURN DISTINCT p.name AS province_name, w1.name AS from_ward, w2.name AS to_ward, r.distance_km AS distance
        ORDER BY p.name, w1.name, w2.name
        """
        
        results = session.run(query).data()
        print(f"\n🔍 Found {len(results)} route relationships in Neo4j")
        
        transportations_to_insert = []
        
        for i, record in enumerate(results):
            province_name = record['province_name']
            from_ward = record['from_ward']
            to_ward = record['to_ward']
            distance = record['distance']
            
            if to_ward and distance:
                # Determine transport type by distance
                if distance <= 3:
                    trans_type = "Motorbike"
                    price = int(distance * 3500 + 15000)
                elif distance <= 10:
                    trans_type = "Taxi"
                    price = int(distance * 8000 + 25000)
                elif distance <= 30:
                    trans_type = "Bus"
                    price = int(distance * 1500 + 30000)
                else:
                    trans_type = "Coach"
                    price = int(distance * 1200 + 80000)
                
                # Get locations available in from_ward and to_ward
                locations_from = list(db["Locations"].find(
                    {"ward_name": from_ward, "province_name": province_name},
                    {"locationId": 1, "_id": 0}
                ))
                
                locations_to = list(db["Locations"].find(
                    {"ward_name": to_ward, "province_name": province_name},
                    {"locationId": 1, "_id": 0}
                ))
                
                available_location_ids = [l["locationId"] for l in locations_from + locations_to]
                
                trans_entry = {
                    "transportId": f"T-{i}",
                    "transportType": trans_type,
                    "name": f"{trans_type} ({from_ward} → {to_ward})",
                    "description": f"Dịch vụ vận chuyển từ {from_ward} đến {to_ward}, {province_name}. Khoảng cách: {distance}km",
                    "from_ward": from_ward,
                    "to_ward": to_ward,
                    "province_name": province_name,
                    "distance_km": distance,
                    "price": price,
                    "estimatedDuration": max(1, int(distance / 30)),  # Estimate in hours
                    "available_in": available_location_ids,  # List of location IDs where this transport is available
                    "suitabilityFor": ["Solo", "Couples", "Family", "Friends", "Group"],
                    "operatingHours": {
                        "open": "05:00",
                        "close": "22:00"
                    },
                    "createdAt": datetime.now(),
                }
                transportations_to_insert.append(trans_entry)
        
        # Insert transportations
        if transportations_to_insert:
            print(f"\n✅ Preparing to insert {len(transportations_to_insert)} transportation entries...")
            existing_ids = set(db["Transportations"].distinct("transportId"))
            new_entries = [t for t in transportations_to_insert if t["transportId"] not in existing_ids]
            
            if new_entries:
                print(f"\n📝 Sample entries to insert:")
                for entry in new_entries[:3]:
                    print(f"  - {entry['transportId']}: {entry['name']}")
                    print(f"    Type: {entry['transportType']}, Distance: {entry['distance_km']}km")
                    print(f"    Price: {entry['price']:,} VNĐ")
                    print(f"    Available in {len(entry['available_in'])} locations")
                
                try:
                    result = db["Transportations"].insert_many(new_entries, ordered=False)
                    print(f"\n✓ Inserted {len(result.inserted_ids)} new transportations into MongoDB")
                except Exception as e:
                    # Continue even if some insertions fail
                    print(f"\n⚠️  Some entries skipped: {str(e)[:100]}")
                    # Try individual inserts to skip duplicates
                    inserted_count = 0
                    for entry in new_entries:
                        try:
                            db["Transportations"].insert_one(entry)
                            inserted_count += 1
                        except:
                            pass
                    print(f"✓ Inserted {inserted_count} new transportations (skipped duplicates)")
                
                # Verify insertion
                count = db["Transportations"].count_documents({})
                print(f"  Total transportations now in database: {count}")
                
                # Show by type
                print(f"\n📊 Transportations by type:")
                types = db["Transportations"].aggregate([
                    {"$group": {"_id": "$transportType", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ])
                for t in types:
                    print(f"  - {t['_id']}: {t['count']} entries")
                
                # Show by province
                print(f"\n📊 Transportations by province:")
                provinces = db["Transportations"].aggregate([
                    {"$group": {"_id": "$province_name", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 10}
                ])
                for p in provinces:
                    print(f"  - {p['_id']}: {p['count']} entries")
            else:
                print(f"  ℹ️  All transportations already exist")
        else:
            print("  ⚠️  No transportation data generated")


if __name__ == "__main__":
    sync_transportations_from_neo4j()
    print("\n" + "="*60)
    print("✅ SYNC COMPLETE")
    print("="*60)
