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

def view_daydetail_schema():
    print("Connecting to MongoDB...")
    db = get_mongo_db("TravelDB")
    daydetails_col = db["DayDetails"]
    
    # Check total day details
    total_details = daydetails_col.count_documents({})
    print(f"\nTotal DayDetails in database: {total_details}")
    
    if total_details == 0:
        print("No DayDetails found in the database. Cannot determine schema.")
        return
        
    # Get the most recent day detail
    sample_detail = daydetails_col.find_one({}, sort=[("_id", -1)])
    
    print("\n" + "="*50)
    print("DAYDETAILS COLLECTION SCHEMA / SAMPLE DOCUMENT")
    print("="*50)
    
    # Pretty print the document
    print(json.dumps(sample_detail, indent=2, ensure_ascii=False, cls=CustomJSONEncoder))
    
    print("\n" + "="*50)
    print("TOP-LEVEL FIELDS:")
    print("="*50)
    for key in sample_detail.keys():
        val_type = type(sample_detail[key]).__name__
        print(f"- {key}: {val_type}")

if __name__ == "__main__":
    view_daydetail_schema()
