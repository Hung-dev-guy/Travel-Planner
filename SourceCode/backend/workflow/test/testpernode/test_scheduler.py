import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.nodes.Scheduler import scheduler_node
from workflow.graph.stage import State
import json

def test_scheduler_node():
    print("\n" + "="*60)
    print("TESTING SCHEDULER_NODE WITH MOBILITY OUTPUT")
    print("="*60)

    # State from Planner + Mobility output
    state = State(
        trip_metadata={
            "usr_des": "Du lịch Đà Nẵng, Hội An 3 ngày 2 đêm cùng gia đình, có người già và trẻ nhỏ, thích trải nghiệm văn hóa, không khí yên bình, ăn hải sản, ở khách sạn gần biển.",
            "start_date": "2026-06-15",
            "end_date": "2026-06-18",
            "total_days": 3,
            "age_range": "Người già, Trẻ nhỏ (5 tuổi)",
            "start_location": "Hà Nội",
            "destination": ["Đà Nẵng", "Hội An"]
        },
        travel_preferences={
            "travel_style": ["Văn hóa"],
            "travel_pace": ["Thong thả"],
            "food_style": ["Hải sản"],
            "accommodation_style": ["Khách sạn gần biển"],
            "mobility_style": [],
            "atmosphere": ["Yên bình", "Gia đình", "Thoáng đãng"],
            "companion_type": ["Gia đình", "Người già", "Trẻ nhỏ"]
        },
        constraints={
            "travel_budget": 15000000, # parsed budget
            "group_size": 4,
            "daily_active_hours": 10,
            "language": "",
            "max_radius_distance": "",
            "places_of_limitation": [],
            "health_limitations": ["Dị ứng hải sản (trẻ nhỏ)", "Không ăn cay (trẻ nhỏ)"],
            "mobility_limitations": ["Hạn chế đi bộ", "Hạn chế leo trèo", "Không đi bộ nhiều"]
        },
        accommodation=[
            {
                "locationId": "LOC-STAY-319-2",
                "name": "Phường Mỹ An Luxury Hotel",
                "estimatedPrice": 1200000,
                "ward_name": "Phường Mỹ An",
                "description": "Khách sạn sang trọng, nằm ở khu vực gần biển Mỹ Khê, phù hợp với yêu cầu 'khách sạn gần biển' và 'gia đình' với nhịp độ 'thong thả'. Giá cả hợp lý trong ngân sách."
            }
        ],
        activities=[
            {
                "locationId": "LOC-SIGHT-002",
                "name": "Bãi biển Mỹ Khê",
                "description": "Bãi biển đẹp nhất Đà Nẵng với cát trắng mịn, sóng vừa phải, lý tưởng cho tắm biển và thư giãn.",
                "estimatedDuration": 180,
                "estimatedPrice": 0,
                "suitabilityFor": ["Family", "Couples", "Solo", "Group"],
                "ward_name": "Phường Mỹ An"
            },
            {
                "locationId": "LOC-SIGHT-005",
                "name": "Cầu Rồng & Sông Hàn",
                "description": "Biểu tượng của Đà Nẵng hiện đại",
                "estimatedDuration": 90,
                "estimatedPrice": 0,
                "suitabilityFor": ["Family", "Couples", "Solo", "Group"],
                "ward_name": "Phường Hải Châu 1"
            },
            {
                "locationId": "LOC-ENT-NIGHT-001",
                "name": "Chợ Đêm Helio",
                "description": "Khu chợ đêm sầm uất với hàng trăm món ăn đường phố, sân khấu nhạc live sôi động.",
                "estimatedDuration": 120,
                "estimatedPrice": 50000,
                "suitabilityFor": ["Family", "Couples", "Solo", "Group", "Friends"],
                "ward_name": "Phường Hòa Cường Bắc"
            }
        ],
        eateries=[
            {
                "locationId": "LOC-FOOD-003",
                "name": "Nhà Hàng Hải Sản Biển Đông",
                "estimatedPrice": 350000,
                "description": "Đáp ứng yêu cầu 'ăn hải sản' của gia đình.",
                "ward_name": "Phường Mỹ An"
            }
        ],
        transportations=[
            {'locationId': None, 'name': 'Train (Hà Nội → Đà Nẵng)', 'type': 'train', 'from_ward': 'Hà Nội', 'to_ward': 'Đà Nẵng', 'distance_km': 800.0, 'price_per_person': 840000, 'suitability_for': ['Family', 'Group', 'Friends', 'Couples'], 'note': 'Quãng đường 800 km.'}, 
            {'locationId': None, 'name': 'Coach (Hải Vân → Thủy Xuân)', 'type': 'coach', 'from_ward': 'Hải Vân', 'to_ward': 'Thủy Xuân', 'distance_km': 79.4, 'price_per_person': 175000, 'suitability_for': ['Family', 'Group', 'Friends', 'Couples'], 'note': 'Quãng đường 79.4 km. Chi phí ước tính: 175,000 VNĐ/người × 4 người = 700,000 VNĐ. Phù hợp với nhịp du lịch thong thả. Xe giường nằm/ngồi, phù hợp chặng dài.'}, 
            {'locationId': None, 'name': 'Bus (Hải Vân → Phường Hải Châu 1)', 'type': 'bus', 'from_ward': 'Hải Vân', 'to_ward': 'Phường Hải Châu 1', 'distance_km': 27.5, 'price_per_person': 71000, 'suitability_for': ['Solo', 'Friends', 'Group'], 'note': 'Quãng đường 27.5 km. Chi phí ước tính: 71,000 VNĐ/người × 4 người = 284,000 VNĐ. Phù hợp với nhịp du lịch thong thả. Tiết kiệm chi phí, phù hợp nhóm đông.'}, 
            {'locationId': None, 'name': 'Bicycle (Phường Thạc Gián → Phường Vĩnh Trung)', 'type': 'bicycle', 'from_ward': 'Phường Thạc Gián', 'to_ward': 'Phường Vĩnh Trung', 'distance_km': 1.5, 'price_per_person': 14000, 'suitability_for': ['Solo', 'Couples', 'Friends'], 'note': 'Quãng đường 1.5 km. Chi phí ước tính: 14,000 VNĐ/người × 4 người = 56,000 VNĐ. Phù hợp với nhịp du lịch thong thả. Thân thiện môi trường, linh hoạt.'}, 
            {'locationId': None, 'name': 'Motorbike (Xã Hòa Phong → Xã Hòa Tiến)', 'type': 'motorbike', 'from_ward': 'Xã Hòa Phong', 'to_ward': 'Xã Hòa Tiến', 'distance_km': 6.0, 'price_per_person': 36000, 'suitability_for': ['Solo', 'Couples', 'Friends'], 'note': 'Quãng đường 6.0 km. Chi phí ước tính: 36,000 VNĐ/người × 4 người = 144,000 VNĐ. Phù hợp với nhịp du lịch thong thả. Cơ động, dễ tìm thuê tại địa phương.'},
            {'locationId': None, 'name': 'Train (Đà Nẵng → Hà Nội)', 'type': 'train', 'from_ward': 'Đà Nẵng', 'to_ward': 'Hà Nội', 'distance_km': 800.0, 'price_per_person': 840000, 'suitability_for': ['Family', 'Group', 'Friends', 'Couples'], 'note': 'Quãng đường 800 km.'}
        ]
    )
    
    try:
        # Scheduler execution
        result_state = scheduler_node(state)
        
        print(f"\n✓ Scheduler node executed successfully!")
        
        scheduling = result_state.get('scheduling', [])
        
        # Assertions
        assert scheduling, "Should have scheduling options"
        assert isinstance(scheduling, list), "Scheduling should be a list"
        
        for day in scheduling:
            print(f"\nDay {day.get('day')} - {day.get('title')}")
            for item in day.get('items', []):
                print(f"  [{item.get('time_start')} - {item.get('time_end')}] {item.get('name')} ({item.get('type')}) - Cost: {item.get('cost')}")
            
            summary = day.get('day_summary', {})
            print(f"  Summary: Active {summary.get('active_hours')}h, Cost {summary.get('total_cost')}VND")

        print(f"\n✓ All assertions passed!")
        
        print("\n" + "="*60)
        print("TESTING VALIDATION_NODE WITH SCHEDULER OUTPUT")
        print("="*60)
        
        from workflow.nodes.Validation_agent import validation_node
        validated_state = validation_node(result_state)
        val_result = validated_state.get("validation", {})
        
        print(f"\nOverall Score: {val_result.get('overall_score', 0):.0f}%")
        print(f"Summary: {val_result.get('summary')}")
        
        if val_result.get("issues"):
            print(f"\n📋 Issues ({len(val_result['issues'])}):")
            for issue in val_result["issues"]:
                day_str = f"Day {issue.get('day')}" if issue.get('day') else "General"
                print(f"  - [{issue['severity'].upper()}] {day_str}: {issue['message']}")
                
        if val_result.get("recommendations"):
            print(f"\n💡 Recommendations ({len(val_result['recommendations'])}):")
            for rec in val_result["recommendations"]:
                print(f"  - [{rec.get('priority', 'normal').upper()}] {rec['suggestion']}")
                
        print("\n" + "="*60)
        print("TESTING GENERATE_ANSWER_NODE WITH VALIDATION OUTPUT")
        print("="*60)
        
        from workflow.nodes.Generate_answer import generate_answer_node
        final_state = generate_answer_node(validated_state)
        
        print(f"\nResponse Status: {final_state.get('response_status')}")
        if "final_answer" in final_state and final_state["final_answer"]:
            answer = final_state["final_answer"]
            print(f"Generated at: {answer.get('generated_at')}")
            for section in answer.get('sections', []):
                print(f"\n--- {section.get('title_vi', 'Unknown')} ---")
                content = section.get('content', '')
                print(content[:500] + ("..." if len(content) > 500 else ""))
                
        return True
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scheduler_node()
    exit(0 if success else 1)
