"""
Seed script: populates TravelDB.Locations with ~25 realistic locations for Đà Nẵng.
Ward names are matched exactly to Neo4j Ward.name values.

Run from backend/:
    uv run workflow/tools/seed_locations.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient, GEOSPHERE

# ── Path & env setup ──────────────────────────────────────────────────────────
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
load_dotenv()

# ── Data ──────────────────────────────────────────────────────────────────────
# Ward names sourced directly from Neo4j: (Province {name:"Đà Nẵng"})-[:HAS]->(Ward)
LOCATIONS = [
    # ── STAY (Hotels / Accommodation) ────────────────────────────────────────
    {
        "locationId": "LOC-STAY-001",
        "name": "Mường Thanh Luxury Đà Nẵng",
        "description": "Khách sạn 5 sao sang trọng ngay trung tâm thành phố, view biển tuyệt đẹp.",
        "category": "Stay",
        "estimatedDuration": 0,
        "estimatedPrice": 1200000,
        "suitabilityFor": ["Family", "Couples", "Business"],
        "openingHours": {"open": "00:00", "close": "23:59"},
        "ward_name": "Phường Hải Châu 1",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2208, 16.0678]},
    },
    {
        "locationId": "LOC-STAY-002",
        "name": "Fusion Maia Resort Đà Nẵng",
        "description": "Resort nghỉ dưỡng 5 sao ven biển Mỹ Khê, bao gồm spa toàn diện trong gói phòng.",
        "category": "Stay",
        "estimatedDuration": 0,
        "estimatedPrice": 3500000,
        "suitabilityFor": ["Couples", "Solo"],
        "openingHours": {"open": "00:00", "close": "23:59"},
        "ward_name": "Phường Khuê Mỹ",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2470, 16.0412]},
    },
    {
        "locationId": "LOC-STAY-003",
        "name": "Brilliant Hotel Đà Nẵng",
        "description": "Khách sạn 4 sao tầm trung, vị trí trung tâm tiện di chuyển, có hồ bơi rooftop.",
        "category": "Stay",
        "estimatedDuration": 0,
        "estimatedPrice": 700000,
        "suitabilityFor": ["Family", "Solo", "Group"],
        "openingHours": {"open": "00:00", "close": "23:59"},
        "ward_name": "Phường Thạch Thang",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2192, 16.0710]},
    },

    # ── SIGHTSEEING ───────────────────────────────────────────────────────────
    {
        "locationId": "LOC-SIGHT-001",
        "name": "Bà Nà Hills & Cầu Vàng",
        "description": "Khu du lịch trên núi với cầu Vàng nổi tiếng thế giới, cáp treo dài nhất thế giới, công viên Fantasy Park.",
        "category": "Sightseeing",
        "estimatedDuration": 360,
        "estimatedPrice": 900000,
        "suitabilityFor": ["Family", "Couples", "Group"],
        "openingHours": {"open": "07:00", "close": "22:00"},
        "ward_name": "Xã Hòa Phong",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [107.9930, 15.9956]},
    },
    {
        "locationId": "LOC-SIGHT-002",
        "name": "Bãi biển Mỹ Khê",
        "description": "Bãi biển đẹp nhất Đà Nẵng với cát trắng mịn, sóng vừa phải, lý tưởng cho tắm biển và thư giãn.",
        "category": "Sightseeing",
        "estimatedDuration": 180,
        "estimatedPrice": 0,
        "suitabilityFor": ["Family", "Couples", "Solo", "Group"],
        "openingHours": {"open": "05:00", "close": "22:00"},
        "ward_name": "Phường Phước Mỹ",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2462, 16.0600]},
    },
    {
        "locationId": "LOC-SIGHT-003",
        "name": "Ngũ Hành Sơn (Marble Mountains)",
        "description": "Quần thể 5 ngọn núi đá cẩm thạch huyền bí với hang động, chùa chiền và tác phẩm điêu khắc cổ.",
        "category": "Sightseeing",
        "estimatedDuration": 150,
        "estimatedPrice": 40000,
        "suitabilityFor": ["Family", "Solo", "Culture"],
        "openingHours": {"open": "07:00", "close": "17:30"},
        "ward_name": "Phường Hòa Hải",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2639, 15.9727]},
    },
    {
        "locationId": "LOC-SIGHT-004",
        "name": "Bán đảo Sơn Trà & Chùa Linh Ứng",
        "description": "Bán đảo xanh mướt với tượng Phật bà cao 67m, rừng nguyên sinh, bãi biển hoang sơ và voọc chà vá chân nâu.",
        "category": "Sightseeing",
        "estimatedDuration": 180,
        "estimatedPrice": 0,
        "suitabilityFor": ["Family", "Solo", "Couples"],
        "openingHours": {"open": "06:00", "close": "18:00"},
        "ward_name": "Phường Thọ Quang",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2844, 16.1033]},
    },
    {
        "locationId": "LOC-SIGHT-005",
        "name": "Cầu Rồng & Sông Hàn",
        "description": "Biểu tượng của Đà Nẵng hiện đại — cây cầu hình rồng phun lửa và phun nước vào cuối tuần. Dạo bờ sông Hàn về đêm.",
        "category": "Sightseeing",
        "estimatedDuration": 90,
        "estimatedPrice": 0,
        "suitabilityFor": ["Family", "Couples", "Solo", "Group"],
        "openingHours": {"open": "00:00", "close": "23:59"},
        "ward_name": "Phường Hải Châu 1",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2272, 16.0610]},
    },
    {
        "locationId": "LOC-SIGHT-006",
        "name": "Bảo tàng Chăm",
        "description": "Bảo tàng lưu giữ bộ sưu tập điêu khắc Chăm lớn nhất thế giới, kiến trúc Pháp cổ điển.",
        "category": "Sightseeing",
        "estimatedDuration": 90,
        "estimatedPrice": 60000,
        "suitabilityFor": ["Solo", "Couples", "Culture"],
        "openingHours": {"open": "07:00", "close": "17:30"},
        "ward_name": "Phường Bình Hiên",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2211, 16.0608]},
    },

    # ── ENTERTAINMENT ─────────────────────────────────────────────────────────
    {
        "locationId": "LOC-ENT-001",
        "name": "Asia Park & Vòng quay Mặt Trời Sun Wheel",
        "description": "Công viên giải trí với Sun Wheel cao 115m, các khu vực văn hóa Châu Á thu nhỏ.",
        "category": "Entertainment",
        "estimatedDuration": 240,
        "estimatedPrice": 200000,
        "suitabilityFor": ["Family", "Group", "Couples"],
        "openingHours": {"open": "15:00", "close": "22:30"},
        "ward_name": "Phường An Hải Bắc",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2400, 16.0550]},
    },
    {
        "locationId": "LOC-ENT-002",
        "name": "K-Surf Water Sports",
        "description": "Trung tâm thể thao biển: lướt sóng, kayak, lặn snorkel, dù kéo và jet-ski ngay bãi biển Mỹ Khê.",
        "category": "Entertainment",
        "estimatedDuration": 120,
        "estimatedPrice": 300000,
        "suitabilityFor": ["Solo", "Couples", "Group"],
        "openingHours": {"open": "07:00", "close": "18:00"},
        "ward_name": "Phường Phước Mỹ",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2480, 16.0650]},
    },

    # ── CULTURE ───────────────────────────────────────────────────────────────
    {
        "locationId": "LOC-CULT-001",
        "name": "Làng đá mỹ nghệ Non Nước",
        "description": "Làng nghề truyền thống chuyên điêu khắc đá cẩm thạch, tham quan và mua sắm tác phẩm thủ công.",
        "category": "Culture",
        "estimatedDuration": 90,
        "estimatedPrice": 0,
        "suitabilityFor": ["Family", "Solo", "Couples"],
        "openingHours": {"open": "08:00", "close": "17:00"},
        "ward_name": "Phường Hòa Hải",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2620, 15.9790]},
    },
    {
        "locationId": "LOC-CULT-002",
        "name": "Chợ Hàn",
        "description": "Chợ truyền thống sầm uất nhất Đà Nẵng — mua sắm đặc sản địa phương, hàng thổ cẩm và ẩm thực.",
        "category": "Culture",
        "estimatedDuration": 60,
        "estimatedPrice": 0,
        "suitabilityFor": ["Family", "Solo", "Couples", "Group"],
        "openingHours": {"open": "06:00", "close": "19:00"},
        "ward_name": "Phường Hải Châu 1",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2230, 16.0672]},
    },

    # ── FOOD ──────────────────────────────────────────────────────────────────
    {
        "locationId": "LOC-FOOD-001",
        "name": "Mì Quảng Bà Mua",
        "description": "Quán mì Quảng nổi tiếng lâu đời nhất Đà Nẵng, nước dùng đậm đà, tôm thịt tươi ngon.",
        "category": "Food",
        "estimatedDuration": 45,
        "estimatedPrice": 50000,
        "suitabilityFor": ["Family", "Solo", "Couples", "Group"],
        "openingHours": {"open": "06:00", "close": "22:00"},
        "ward_name": "Phường Thạc Gián",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2115, 16.0590]},
    },
    {
        "locationId": "LOC-FOOD-002",
        "name": "Bánh Mì Phượng",
        "description": "Thương hiệu bánh mì nổi tiếng được Anthony Bourdain khen ngợi, nhân phong phú đặc biệt.",
        "category": "Food",
        "estimatedDuration": 20,
        "estimatedPrice": 30000,
        "suitabilityFor": ["Solo", "Couples", "Group"],
        "openingHours": {"open": "06:30", "close": "21:30"},
        "ward_name": "Phường Hải Châu 1",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2215, 16.0655]},
    },
    {
        "locationId": "LOC-FOOD-003",
        "name": "Nhà Hàng Hải Sản Biển Đông",
        "description": "Nhà hàng hải sản tươi sống lớn ngay bờ biển, tôm hùm, cua ghẹ, ốc và cá theo mùa.",
        "category": "Food",
        "estimatedDuration": 90,
        "estimatedPrice": 350000,
        "suitabilityFor": ["Family", "Group", "Couples"],
        "openingHours": {"open": "10:00", "close": "22:00"},
        "ward_name": "Phường Phước Mỹ",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2455, 16.0590]},
    },
    {
        "locationId": "LOC-FOOD-004",
        "name": "Bún Chả Cá Bà Thanh",
        "description": "Quán bún chả cá đặc trưng xứ Quảng, nước lèo ngọt tự nhiên từ xương cá, phong cách dân dã.",
        "category": "Food",
        "estimatedDuration": 45,
        "estimatedPrice": 45000,
        "suitabilityFor": ["Family", "Solo"],
        "openingHours": {"open": "06:00", "close": "14:00"},
        "ward_name": "Phường Hòa Cường Bắc",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2180, 16.0530]},
    },
    {
        "locationId": "LOC-FOOD-005",
        "name": "Cơm Gà Bà Buội",
        "description": "Cơm gà Hội An – Đà Nẵng nổi tiếng, gà ta thả vườn, cơm nấu nước dừa thơm béo.",
        "category": "Food",
        "estimatedDuration": 45,
        "estimatedPrice": 55000,
        "suitabilityFor": ["Family", "Solo", "Couples"],
        "openingHours": {"open": "10:00", "close": "21:00"},
        "ward_name": "Phường Vĩnh Trung",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2100, 16.0640]},
    },
    {
        "locationId": "LOC-FOOD-006",
        "name": "Quán Nhậu Sông Hàn",
        "description": "Nhà hàng bia hơi bờ sông view Cầu Rồng, đồ nhậu đa dạng, không khí sôi động về đêm.",
        "category": "Food",
        "estimatedDuration": 120,
        "estimatedPrice": 150000,
        "suitabilityFor": ["Group", "Solo", "Couples"],
        "openingHours": {"open": "16:00", "close": "23:59"},
        "ward_name": "Phường Hải Châu 1",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2250, 16.0630]},
    },
    {
        "locationId": "LOC-FOOD-007",
        "name": "Nem Lụi Bà Hào",
        "description": "Nem lụi nướng than hoa đặc sản Đà Nẵng, ăn kèm bánh tráng cuốn rau sống và tương đậu phộng.",
        "category": "Food",
        "estimatedDuration": 60,
        "estimatedPrice": 80000,
        "suitabilityFor": ["Family", "Solo", "Couples"],
        "openingHours": {"open": "11:00", "close": "22:00"},
        "ward_name": "Phường Thuận Phước",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2050, 16.0700]},
    },
    {
        "locationId": "LOC-FOOD-008",
        "name": "The Espresso Station",
        "description": "Quán cà phê specialty nổi tiếng, menu brunch phong phú, không gian thoáng mát phù hợp để nghỉ ngơi giữa ngày.",
        "category": "Food",
        "estimatedDuration": 60,
        "estimatedPrice": 70000,
        "suitabilityFor": ["Solo", "Couples"],
        "openingHours": {"open": "07:00", "close": "21:00"},
        "ward_name": "Phường Mỹ An",
        "province_name": "Đà Nẵng",
        "location": {"type": "Point", "coordinates": [108.2430, 16.0490]},
    },
]


def seed():
    client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
    db = client["TravelDB"]
    col = db["Locations"]

    # Drop existing seed data to allow idempotent re-runs
    existing_ids = [loc["locationId"] for loc in LOCATIONS]
    deleted = col.delete_many({"locationId": {"$in": existing_ids}}).deleted_count
    if deleted:
        print(f"🗑  Removed {deleted} existing documents before re-seeding.")

    result = col.insert_many(LOCATIONS)
    print(f"✅ Seeded {len(result.inserted_ids)} locations into TravelDB.Locations")

    # Create indexes for efficient querying
    col.create_index("locationId", unique=True)
    col.create_index("ward_name")
    col.create_index("province_name")
    col.create_index("category")
    col.create_index([("location", GEOSPHERE)])
    print("✅ Indexes created: locationId (unique), ward_name, province_name, category, location (2dsphere)")

    # Summary
    print("\nCategory breakdown:")
    for cat in ["Stay", "Sightseeing", "Entertainment", "Culture", "Food"]:
        count = col.count_documents({"category": cat})
        print(f"  {cat:15s}: {count} documents")


if __name__ == "__main__":
    seed()
