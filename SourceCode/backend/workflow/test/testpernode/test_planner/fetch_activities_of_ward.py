import sys
import os
import json

# Cấu hình sys.path để có thể import các thư viện của backend
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "../../../.."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from workflow.nodes.Planner import fetch_locations_from_mongo

def run_tests():
    print("Bắt đầu test hàm fetch_locations_from_mongo...\n" + "="*40)
    
    # Chúng ta sẽ tìm các địa điểm ở phường "Tây Hoa Lư" (nơi bạn vừa insert các activity)
    test_wards = ["Tây Hoa Lư", "Hoa Lư"]
    print(f"\n[Test Case]: Tìm kiếm Locations thuộc các Phường/Xã: {test_wards}")
    
    try:
        results = fetch_locations_from_mongo(test_wards)
        activities = results.get("activities", [])
        hotels = results.get("hotels", [])
        eateries = results.get("eateries", [])
        
        print(f"\n[+] Đã tìm thấy {len(activities)} Hoạt động (Activities):")
        for act in activities:
            print(f"   - {act.get('name')} | Thể loại: {act.get('category')} | Giá: {act.get('estimatedPrice')}đ | Phù hợp: {act.get('suitabilityFor')}")
            
        print(f"\n[+] Đã tìm thấy {len(hotels)} Khách sạn (Hotels):")
        for h in hotels:
            print(f"   - {h.get('name')} | Thể loại: {h.get('category')} | Giá: {h.get('estimatedPrice')}đ")
            
        print(f"\n[+] Đã tìm thấy {len(eateries)} Quán ăn (Eateries):")
        for e in eateries:
            print(f"   - {e.get('name')} | Thể loại: {e.get('category')} | Giá: {e.get('estimatedPrice')}đ")
            
    except Exception as e:
        print(f"-> [LỖI]: {e}")

if __name__ == "__main__":
    run_tests()
