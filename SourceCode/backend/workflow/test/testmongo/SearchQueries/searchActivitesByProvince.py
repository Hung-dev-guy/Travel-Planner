import os
import argparse
from pprint import pprint
from pymongo import MongoClient
from dotenv import load_dotenv

def search_activities_by_province(province_name):
    # Load environment variables (e.g., MONGO_URI) from .env file
    load_dotenv()
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    
    client = MongoClient(mongo_uri)
    db = client["TravelDB"]
    col = db["Locations"]

    # In our database, Activities can be under categories like Entertainment, Sightseeing, Culture, etc.
    # Exclude Stay and Transport (which are for hotels and flights/cars)
    query = {
        "province_name": province_name,
        "category": {"$nin": ["Stay", "Transport", "Flight"]}
    }
    
    print(f"Searching for activities in province: '{province_name}'...")
    activities = list(col.find(query))
    
    if not activities:
        print("No activities found.")
    else:
        print(f"Found {len(activities)} activities:")
        for idx, act in enumerate(activities, 1):
            print(f"\n--- Activity {idx} ---")
            pprint(act)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search activities by province in MongoDB.")
    parser.add_argument("--province", type=str, default="Ninh Bình", help="Name of the province to search for")
    args = parser.parse_args()
    
    search_activities_by_province(args.province)
