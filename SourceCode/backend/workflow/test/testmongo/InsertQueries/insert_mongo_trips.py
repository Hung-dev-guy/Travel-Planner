import sys
from pathlib import Path
from datetime import datetime

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[3]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from workflow.db import get_mongo_db
from workflow.nodes.Generate_answer import generate_answer_node
from workflow.test.testpernode.test_generate_answer import create_sample_state

def insert_trip_to_mongo():
    print("Generating sample state...")
    # 1. Get sample state
    state = create_sample_state()
    
    # 2. Extract trip_data and bypass LLM to reliably test DB insertion
    print("Formatting schema without LLM (to bypass API limits)...")
    from workflow.nodes.Generate_answer import ResponseFormatter, TripDataFormatter, ResponseSection
    trip_data = TripDataFormatter().extract_from_state(state)
    
    # Mock sections so we can assemble the final_answer payload
    sections = [
        ResponseSection(title_vi="Tóm tắt chuyến đi", content="Mô tả", section_type="summary")
    ]
    
    final_answer = ResponseFormatter.assemble_response(sections, trip_data)
    result_state = {**state, "final_answer": final_answer}

    # 3. Extract the final answer and database schema
    final_answer = result_state.get("final_answer", {})
    database_schema = final_answer.get("database_schema")
    
    if not database_schema:
        print("Error: database_schema not found in final_answer!")
        return
        
    trip_doc = database_schema.get("trip")
    day_details_docs = database_schema.get("day_details", [])
    
    print("Connecting to MongoDB...")
    # 4. Connect to MongoDB
    db = get_mongo_db("TravelDB")
    trips_col = db["Trips"]
    daydetails_col = db["DayDetails"]
    
    # 5. Insert Trip document
    print("Inserting trip into MongoDB 'Trips' collection...")
    trip_insert_result = trips_col.insert_one(trip_doc)
    
    if trip_insert_result.inserted_id:
        print(f"✅ Successfully inserted trip with ID: {trip_doc['tripId']} (MongoDB _id: {trip_insert_result.inserted_id})")
    else:
        print("❌ Failed to insert trip.")
        return

    # 6. Insert DayDetails documents
    if day_details_docs:
        print(f"Inserting {len(day_details_docs)} day details into 'DayDetails' collection...")
        daydetails_insert_result = daydetails_col.insert_many(day_details_docs)
        print(f"✅ Successfully inserted day details! MongoDB _ids: {daydetails_insert_result.inserted_ids}")
    else:
        print("⚠️ No day details found to insert.")

if __name__ == "__main__":
    insert_trip_to_mongo()
