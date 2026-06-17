import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[3]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

load_dotenv()

from workflow.graph.builder import build_workflow
from workflow.db import get_mongo_db

def test_full_pipeline_to_mongodb():
    print("=" * 60)
    print("🚀 RUNNING FULL END-TO-END WORKFLOW PIPELINE")
    print("=" * 60)
    
    # 1. Initialize Pipeline
    print("1. Compiling LangGraph workflow...")
    app = build_workflow()
    
    # 2. Prepare Initial Input State
    print("2. Preparing user input state...")
    initial_state = {
        "user_des_input": "Tôi muốn đi du lịch Đà Nẵng từ Hà Nội 3 ngày 2 đêm. Ngân sách khoảng 15 triệu, đi thong thả, thích ăn hải sản và ở khách sạn gần biển. Gia đình tôi có người già nên sẽ đi bộ ít thôi.",
        "usr_des_input": "Tôi muốn đi du lịch Đà Nẵng từ Hà Nội 3 ngày 2 đêm. Ngân sách khoảng 15 triệu, đi thong thả, thích ăn hải sản và ở khách sạn gần biển. Gia đình tôi có người già nên sẽ đi bộ ít thôi.",
        "group_size": 4,
        "start_date": "2026-06-15",
        "end_date": "2026-06-18",
        "start_location": "Hà Nội",
        "destination": ["Đà Nẵng", "Hội An"],
        "personal_travel_style_des": "Thích trải nghiệm văn hoá, không khí yên bình",
        "trip_metadata": {},
        "travel_preferences": {},
        "constraints": {},
        "validation_iteration": 1,
        "validation_feedback": []
    }
    
    # 3. Execute Pipeline
    print("3. Executing pipeline (This may take 1-3 minutes)...")
    try:
        config = {"configurable": {"thread_id": "test_thread"}}
        final_state = app.invoke(initial_state, config=config)
    except Exception as e:
        print(f"❌ Pipeline Execution Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Extract Final Answer and Schema
    print("4. Extracting generated data...")
    final_answer = final_state.get("final_answer")
    if not final_answer:
        print("❌ Error: Workflow completed but 'final_answer' is missing from state!")
        return
        
    database_schema = final_answer.get("database_schema")
    if not database_schema:
        print("❌ Error: 'database_schema' not found in final_answer!")
        return
        
    trip_doc = database_schema.get("trip")
    day_details_docs = database_schema.get("day_details", [])
    
    # 5. Persist to MongoDB
    print("5. Connecting to MongoDB to persist data...")
    try:
        db = get_mongo_db("TravelDB")
        trips_col = db["Trips"]
        daydetails_col = db["DayDetails"]
        
        # Insert Trip metadata
        print("   -> Inserting into 'Trips' collection...")
        trip_insert_result = trips_col.insert_one(trip_doc)
        if trip_insert_result.inserted_id:
            print(f"   ✅ Successfully inserted trip! (tripId: {trip_doc['tripId']}, MongoDB _id: {trip_insert_result.inserted_id})")
        else:
            print("   ❌ Failed to insert trip.")
            return

        # Insert Day Details
        if day_details_docs:
            print(f"   -> Inserting {len(day_details_docs)} items into 'DayDetails' collection...")
            daydetails_insert_result = daydetails_col.insert_many(day_details_docs)
            print(f"   ✅ Successfully inserted day details! MongoDB _ids: {daydetails_insert_result.inserted_ids}")
        else:
            print("   ⚠️ No day details found to insert.")
            
        print("\n🎉 WORKFLOW PIPELINE COMPLETED SUCCESSFULLY! 🎉")
        
    except Exception as e:
        print(f"❌ MongoDB Insertion Failed: {e}")

if __name__ == "__main__":
    test_full_pipeline_to_mongodb()
