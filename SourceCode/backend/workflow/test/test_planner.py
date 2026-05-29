import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add backend root to sys.path
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found.")
    exit(1)
else:
    print("✅ GOOGLE_API_KEY loaded.")

try:
    from workflow.nodes.Planner import Planner_node, fetch_ward_names, fetch_locations_from_mongo
    from workflow.db import get_mongo_db
    print("✅ Successfully imported Planner_node and helpers.")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    exit(1)


# ── Sample state matching Extractor output ────────────────────────────────────
MOCK_STATE = {
    "trip_metadata": {
        "usr_des": "Đi du lịch Đà Nẵng 3 ngày 2 đêm cùng gia đình",
        "start_date": "2026-06-15",
        "end_date": "2026-06-18",
        "total_days": "3",
        "age_range": "25-60",
        "destination": "Đà Nẵng",
    },
    "travel_preferences": {
        "travel_style": ["Nghỉ dưỡng", "Ẩm thực"],
        "travel_pace": ["Thong thả"],
        "food_style": ["Hải sản", "Đặc sản địa phương"],
        "accommodation_style": ["Gần biển"],
        "mobility_style": ["Taxi"],
        "atmosphere": ["Yên bình", "Lãng mạn"],
        "companion_type": ["Gia đình"],
    },
    "constraints": {
        "travel_budget": 15000000,
        "group_size": 4,
        "daily_active_hours": "6",
        "language": "Tiếng Việt",
        "max_radius_distance": 30,
        "places_of_limitation": [],
        "health_limitations": ["Người lớn tuổi đi bộ ít"],
        "mobility_limitations": [],
    },
}


def test_neo4j_fetch():
    """Step 1: Verify Neo4j returns ward names for Đà Nẵng."""
    print("\n--- [1] Testing fetch_ward_names (Neo4j) ---")
    wards = fetch_ward_names("Đà Nẵng")
    if wards:
        print(f"✅ Found {len(wards)} wards: {wards[:5]}{'...' if len(wards) > 5 else ''}")
    else:
        print("❌ No wards returned — check Neo4j data for Province 'Đà Nẵng'")
    return wards


def test_mongo_fetch(ward_names: list):
    """Step 2: Verify MongoDB returns locations by ward names."""
    print("\n--- [2] Testing fetch_locations_from_mongo (MongoDB) ---")
    db_context = fetch_locations_from_mongo(ward_names)
    h = len(db_context["hotels"])
    a = len(db_context["activities"])
    e = len(db_context["eateries"])
    print(f"Hotels: {h}, Activities: {a}, Eateries: {e}")
    if h == 0 and a == 0 and e == 0:
        print("❌ No locations found — ensure seed_locations.py has been run.")
    else:
        print("✅ Locations fetched from MongoDB successfully.")
    return db_context


def test_planner_node():
    """Step 3: Run the full Planner_node end-to-end and verify grounding."""
    print("\n--- [3] Testing Planner_node (full pipeline) ---")
    try:
        new_state = Planner_node(MOCK_STATE)
        print("✅ Planner_node returned successfully.")

        # Serialize for display
        serialized = {}
        for k, v in new_state.items():
            serialized[k] = [
                item.model_dump() if hasattr(item, "model_dump") else item
                for item in v
            ]
        print(json.dumps(serialized, indent=2, ensure_ascii=False))

        # Grounding check — returned locationIds must exist in MongoDB
        print("\n--- [4] Grounding check (locationIds in MongoDB) ---")
        db  = get_mongo_db("TravelDB")
        col = db["Locations"]
        all_returned_ids = []
        for key in ["accommodation", "activities", "eateries"]:
            for item in new_state.get(key, []):
                lid = item.locationId if hasattr(item, "locationId") else item.get("locationId")
                if lid:
                    all_returned_ids.append(lid)

        for lid in all_returned_ids:
            exists = col.find_one({"locationId": lid}, {"_id": 0, "name": 1}) is not None
            status = "✅" if exists else "❌ NOT FOUND"
            print(f"  {status}  {lid}")

    except Exception as e:
        print(f"❌ Planner_node failed: {e}")
        raise


if __name__ == "__main__":
    ward_names  = test_neo4j_fetch()
    db_context  = test_mongo_fetch(ward_names)
    print("=" * 60)
    test_planner_node()
