import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[3]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from workflow.db import get_mongo_db



def query_locations():
    db = get_mongo_db("TravelDB")
    locations_col = db["Locations"]

    # 1. Total number of locations
    total_locations = locations_col.count_documents({})
    print(f"Total locations in database: {total_locations}")

    # 2. Count locations by category
    print("\n--- Locations by Category ---")
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]
    categories = list(locations_col.aggregate(pipeline))
    for cat in categories:
        print(f"Category: {cat['_id']} - Count: {cat['count']}")

    # 3. Query a few sample locations (e.g., Accommodations)
    print("\n--- Sample Accommodations ---")
    accommodations = list(locations_col.find({"category": "Stay"}).limit(3))
    for acc in accommodations:
        print(f"[{acc.get('locationId')}] {acc.get('name')} - {acc.get('ward_name', 'Unknown Ward')}, {acc.get('province_name', 'Unknown Province')}")
        print(f"  Price: {acc.get('estimatedPrice', 'N/A')} VND")

    # 4. Query a few sample sightseeing spots
    print("\n--- Sample Sightseeing Spots ---")
    sightseeing = list(locations_col.find({"category": "Sightseeing"}).limit(3))
    for sight in sightseeing:
        print(f"[{sight.get('locationId')}] {sight.get('name')} - {sight.get('ward_name', 'Unknown Ward')}, {sight.get('province_name', 'Unknown Province')}")
        print(f"  Duration: {sight.get('estimatedDuration', 'N/A')} minutes")

if __name__ == "__main__":
    query_locations()
