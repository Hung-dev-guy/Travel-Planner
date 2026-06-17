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

new_hotels = [
    {
        "category": "Stay",
        "name": "Vinpearl Hotel Lạng Sơn",
        "description": "Khách sạn 5 sao cao cấp với tiện nghi hiện đại, vị trí trung tâm thành phố giúp dễ dàng di chuyển.",
        "estimatedDuration": 0,
        "estimatedPrice": 1200000,
        "img_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&q=80",
        "location": {"type": "Point", "coordinates": [106.758, 21.848]},
        "locationId": "LOC-STAY-LS-001",
        "openingHours": {"open": "00:00", "close": "23:59"},
        "province_name": "Lạng Sơn",
        "ward_name": "Kỳ Lừa",
        "suitabilityFor": ["Couples", "Family", "Business", "Solo"]
    },
    {
        "category": "Stay",
        "name": "Mường Thanh Luxury Lạng Sơn",
        "description": "Nằm ngay trung tâm, tầm nhìn thoáng đãng và dịch vụ chuyên nghiệp, lý tưởng cho gia đình nghỉ dưỡng.",
        "estimatedDuration": 0,
        "estimatedPrice": 950000,
        "img_url": "https://images.unsplash.com/photo-1542314831-c6a4d14d285c?w=600&q=80",
        "location": {"type": "Point", "coordinates": [106.762, 21.845]},
        "locationId": "LOC-STAY-LS-002",
        "openingHours": {"open": "00:00", "close": "23:59"},
        "province_name": "Lạng Sơn",
        "ward_name": "Chi Lăng",
        "suitabilityFor": ["Family", "Couples", "Group"]
    }
]

count = 0
for loc in new_hotels:
    if not col.find_one({"locationId": loc["locationId"]}):
        col.insert_one(loc)
        count += 1
        
print(f"Added {count} new hotels in Tây Hoa Lư, Ninh Bình to TravelDB.Locations!")