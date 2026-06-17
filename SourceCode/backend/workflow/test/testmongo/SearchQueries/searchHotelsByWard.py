import os
import argparse
from pprint import pprint
from pymongo import MongoClient
from dotenv import load_dotenv

def search_hotels_by_ward(ward_name):
    # Load environment variables (e.g., MONGO_URI) from .env file
    load_dotenv()
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    
    client = MongoClient(mongo_uri)
    db = client["TravelDB"]
    col = db["Locations"]

    query = {
        "category": "Stay",
        "ward_name": ward_name
    }
    
    print(f"Searching for hotels (Stay) in ward: '{ward_name}'...")
    hotels = list(col.find(query))
    
    if not hotels:
        print("No hotels found.")
    else:
        print(f"Found {len(hotels)} hotels:")
        for idx, hotel in enumerate(hotels, 1):
            print(f"\n--- Hotel {idx} ---")
            pprint(hotel)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search hotels by ward in MongoDB.")
    parser.add_argument("--ward", type=str, default="Tây Hoa Lư", help="Name of the ward to search for")
    args = parser.parse_args()
    
    search_hotels_by_ward(args.ward)
