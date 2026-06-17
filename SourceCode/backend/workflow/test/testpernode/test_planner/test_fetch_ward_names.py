import sys
import os
import json
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "../../../.."))

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from workflow.nodes.Planner import fetch_ward_names

def run_tests():
    print("Bắt đầu test hàm fetch_ward_names...\n" + "="*40)
    province_test = "Ninh Bình"
    print(f"\n[Test Case 1]: Tìm kiếm danh sách Phường/Xã thuộc Tỉnh '{province_test}'")
    try:
        wards = fetch_ward_names(province_test)
        print(f"-> Đã tìm thấy {len(wards)} Ward.")
        print(f"-> Danh sách:\n{json.dumps(wards, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"-> [LỖI]: {e}")

    ward_test = "Tây Hoa Lư"
    print(f"\n[Test Case 2]: Tìm kiếm các Phường/Xã lân cận (connected) với khu vực '{ward_test}'")
    try:
        wards = fetch_ward_names(ward_test)
        print(f"-> Đã tìm thấy {len(wards)} Ward.")
        print(f"-> Danh sách:\n{json.dumps(wards, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"-> [LỖI]: {e}")

if __name__ == "__main__":
    run_tests()
