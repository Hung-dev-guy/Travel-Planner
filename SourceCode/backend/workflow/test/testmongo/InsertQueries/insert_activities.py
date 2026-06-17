import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.environ.get("MONGO_URI")
if not mongo_uri:
    print("MONGO_URI not found")
    exit(1)

client = MongoClient(mongo_uri)
db = client["TravelDB"]
col = db["Locations"]

new_locations = [
    {
        "category": "Sightseeing",
        "name": "Vịnh Hạ Long",
        "description": "Di sản thiên nhiên thế giới với cảnh quan kì vĩ của hàng ngàn hòn đảo đá vôi và hang động.",
        "estimatedDuration": 240,
        "estimatedPrice": 500000,
        "img_url": "https://images.unsplash.com/photo-1528127269322-539801943592?w=600&q=80",
        "location": {"type": "Point", "coordinates": [107.045, 20.950]},
        "locationId": "LOC-ACT-QN-001",
        "openingHours": {"open": "07:00", "close": "18:00"},
        "province_name": "Quảng Ninh",
        "ward_name": "Hạ Long",
        "suitabilityFor": ["Family", "Couples", "Group", "Solo"]
    },
    {
        "category": "Entertainment",
        "name": "Sun World Hạ Long",
        "description": "Khu vui chơi giải trí phức hợp hàng đầu với cáp treo Nữ Hoàng và công viên Rồng.",
        "estimatedDuration": 300,
        "estimatedPrice": 350000,
        "img_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&q=80",
        "location": {"type": "Point", "coordinates": [107.039, 20.955]},
        "locationId": "LOC-ACT-QN-002",
        "openingHours": {"open": "09:00", "close": "22:00"},
        "province_name": "Quảng Ninh",
        "ward_name": "Bạch Đằng",
        "suitabilityFor": ["Family", "Group", "Couples"]
    }
]

count = 0
for loc in new_locations:
    if not col.find_one({"locationId": loc["locationId"]}):
        col.insert_one(loc)
        count += 1
        
print(f"Added {count} new activities to TravelDB.Locations!")
