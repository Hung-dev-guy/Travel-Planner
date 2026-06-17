import sys
import json
from pathlib import Path
from bson import ObjectId

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[3]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from workflow.db import get_mongo_db

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        # Handle datetime if present
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)

def view_trips_schema():
    print("Connecting to MongoDB...")
    db = get_mongo_db("TravelDB")
    trips_col = db["Trips"]
    
    # Check total trips
    total_trips = trips_col.count_documents({})
    print(f"\nTotal trips in database: {total_trips}")
    
    if total_trips == 0:
        print("No trips found in the database. Cannot determine schema.")
        return
        
    # Get the most recent trip
    sample_trip = trips_col.find_one({}, sort=[("_id", -1)])
    
    print("\n" + "="*50)
    print("TRIPS COLLECTION SCHEMA / SAMPLE DOCUMENT")
    print("="*50)
    
    # Pretty print the document
    print(json.dumps(sample_trip, indent=2, ensure_ascii=False, cls=CustomJSONEncoder))
    
    print("\n" + "="*50)
    print("TOP-LEVEL FIELDS:")
    print("="*50)
    for key in sample_trip.keys():
        val_type = type(sample_trip[key]).__name__
        print(f"- {key}: {val_type}")

if __name__ == "__main__":
    view_trips_schema()
