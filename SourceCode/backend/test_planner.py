import sys
import os

# Add the backend directory to sys.path so we can import workflow modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow.nodes.Planner import Planner_node

def test_planner():
    # Giả lập input state cho node Planner
    state = {
        "trip_metadata": {
            "destination": ["Tây Hoa Lư"]
        },
        "travel_preferences": {
            "travel_pace": "Khám phá",
            "atmosphere": "Văn hóa",
            "companion_type": "Solo"
        },
        "constraints": {
            "travel_budget": 5000000,
            "group_size": 1,
            "daily_active_hours": 8
        },
        "total_budget": 5000000
    }
    
    print("Đang chạy Planner node cho điểm đến: Tây Hoa Lư...")
    try:
        result = Planner_node(state)
        print("✅ THÀNH CÔNG! Đã tìm thấy:")
        print(f"  - {len(result.get('accommodations', []))} nơi lưu trú:")
        for a in result.get('accommodations', []):
            print(f"      + {a.name} ({a.cost}đ) - {a.description}")
            
        print(f"  - {len(result.get('activities', []))} hoạt động:")
        for a in result.get('activities', []):
            print(f"      + {a.name} ({a.cost}đ) - {a.description}")
            
        print(f"  - {len(result.get('eateries', []))} quán ăn:")
        for a in result.get('eateries', []):
            print(f"      + {a.name} ({a.cost}đ) - {a.description}")
    except ValueError as e:
        print("❌ LỖI (Đúng như thiết kế):", str(e))
    except Exception as e:
        print("❌ LỖI KHÔNG MONG MUỐN:", str(e))

if __name__ == "__main__":
    test_planner()
