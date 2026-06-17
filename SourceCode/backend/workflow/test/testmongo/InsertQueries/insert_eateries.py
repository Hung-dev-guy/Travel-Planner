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

new_eateries = [
    {
        "category": "Food",
        "name": "Nhà hàng hải sản Hồng Hạnh",
        "description": "Nhà hàng hải sản tươi ngon, nổi tiếng bậc nhất Hạ Long với không gian nhìn ra biển.",
        "estimatedDuration": 90,
        "estimatedPrice": 350000,
        "img_url": "https://images.unsplash.com/photo-1544378730-8b5af1fbcf51?w=600&q=80",
        "location": {"type": "Point", "coordinates": [107.040, 20.952]},
        "locationId": "LOC-EAT-QN-001",
        "openingHours": {"open": "09:00", "close": "22:00"},
        "province_name": "Quảng Ninh",
        "ward_name": "Hạ Long",
        "suitabilityFor": ["Family", "Group", "Business"]
    },
    {
        "category": "Food",
        "name": "Sữa chua trân châu Hạ Long",
        "description": "Món ăn vặt đặc sản không thể bỏ qua khi đến Hạ Long.",
        "estimatedDuration": 30,
        "estimatedPrice": 30000,
        "img_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600&q=80",
        "location": {"type": "Point", "coordinates": [107.042, 20.958]},
        "locationId": "LOC-EAT-QN-002",
        "openingHours": {"open": "08:00", "close": "23:00"},
        "province_name": "Quảng Ninh",
        "ward_name": "Bạch Đằng",
        "suitabilityFor": ["Family", "Group", "Couples", "Solo"]
    }
]

count = 0
for loc in new_eateries:
    if not col.find_one({"locationId": loc["locationId"]}):
        col.insert_one(loc)
        count += 1
        
print(f"Added {count} new eateries in Kỳ Lừa, Lạng Sơn to TravelDB.Locations!")