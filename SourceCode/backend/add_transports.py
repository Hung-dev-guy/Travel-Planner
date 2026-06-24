from pymongo import MongoClient

def add_ninh_binh_transports():
    db = MongoClient("mongodb://localhost:27017/")["TravelDB"]
    
    transports = [
        {
            "locationId": "TRP_NB_01",
            "name": "Thuê Xe Máy Ninh Bình - Motorbike Rental",
            "category": "Transport",
            "description": "Dịch vụ cho thuê xe máy uy tín tại trung tâm thành phố Ninh Bình, thủ tục nhanh gọn, xe ga và xe số đời mới.",
            "img_url": "https://motogo.vn/wp-content/uploads/2020/04/thue-xe-may-ninh-binh.jpg",
            "estimatedPrice": 150000,
            "province_name": "Ninh Bình",
            "ward_name": "Ninh Khánh",
            "location": {
                "type": "Point",
                "coordinates": [105.9760, 20.2660]
            }
        },
        {
            "locationId": "TRP_NB_02",
            "name": "Limousine Hà Nội - Ninh Bình (Tràng An Travel)",
            "category": "Transport",
            "description": "Xe Limousine 9 chỗ đón tận nơi tại Hà Nội và trả khách tại các điểm du lịch Tràng An, Tam Cốc, Hang Múa.",
            "img_url": "https://xelimousinevip.com/wp-content/uploads/2020/10/xe-limousine-ha-noi-ninh-binh.jpg",
            "estimatedPrice": 250000,
            "province_name": "Ninh Bình",
            "ward_name": "Trường Yên",
            "location": {
                "type": "Point",
                "coordinates": [105.9000, 20.2800]
            }
        },
        {
            "locationId": "TRP_NB_03",
            "name": "Taxi Mai Linh Ninh Bình",
            "category": "Transport",
            "description": "Dịch vụ taxi 4 chỗ, 7 chỗ phục vụ 24/7 di chuyển giữa các danh lam thắng cảnh ở Ninh Bình.",
            "img_url": "https://mailinh.vn/uploads/images/2020/12/28/taxi-mai-linh.jpg",
            "estimatedPrice": 12000, # Giá mở cửa
            "province_name": "Ninh Bình",
            "ward_name": "Đông Thành",
            "location": {
                "type": "Point",
                "coordinates": [105.9800, 20.2500]
            }
        }
    ]
    
    res = db.Locations.insert_many(transports)
    print(f"Added {len(res.inserted_ids)} transport options to Ninh Bình.")

if __name__ == "__main__":
    add_ninh_binh_transports()
