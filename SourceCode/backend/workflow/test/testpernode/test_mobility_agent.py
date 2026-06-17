import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.nodes.Mobility_agent import (
    mobility_node,
    fetch_connected_wards,
    fetch_transport_options,
    build_transport_candidates,
)
from workflow.graph.stage import State
from workflow.db import reset_mongo_connection


def test_mobility_node_with_previous_node_output():
    """Test mobility_node with realistic State from previous node."""
    print("\n" + "="*60)
    print("TESTING MOBILITY_NODE WITH PREVIOUS NODE OUTPUT")
    print("="*60)
    
    # Reset MongoDB connection to ensure fresh connection
    reset_mongo_connection()
    
    # Simulate output from previous node (Extractor/Planner)
    # NOTE: destination must be a Province name from Neo4j with routes
    # Quảng Ninh has 1 route in Neo4j and we'll use transportation from MongoDB
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
            "travel_budget": "Khoảng 15 triệu",
            "group_size": 4,
            "daily_active_hours": "",
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
                "price_per_night": 1200000,
                "ward_name": "Phường Mỹ An",
                "description": "Khách sạn sang trọng, nằm ở khu vực gần biển Mỹ Khê, phù hợp với yêu cầu 'khách sạn gần biển' và 'gia đình' với nhịp độ 'thong thả'. Giá cả hợp lý trong ngân sách."
            }
        ],
        activities=[
            {
                "locationId": "LOC-SIGHT-002",
                "name": "Bãi biển Mỹ Khê",
                "description": "Bãi biển đẹp nhất Đà Nẵng với cát trắng mịn, sóng vừa phải, lý tưởng cho tắm biển và thư giãn.",
                "estimated_duration_minutes": 180,
                "estimated_cost": 0,
                "suitability_for": ["Family", "Couples", "Solo", "Group"],
                "note": "Bãi biển đẹp, cát mịn, lý tưởng để gia đình thư giãn..."
            },
            {
                "locationId": "LOC-SIGHT-005",
                "name": "Cầu Rồng & Sông Hàn",
                "description": "Biểu tượng của Đà Nẵng hiện đại",
                "estimated_duration_minutes": 90,
                "estimated_cost": 0,
                "suitability_for": ["Family", "Couples", "Solo", "Group"],
                "note": "Biểu tượng của Đà Nẵng"
            }
        ],
        eateries=[
            {
                "locationId": "LOC-FOOD-003",
                "name": "Nhà Hàng Hải Sản Biển Đông",
                "price_per_person": 350000,
                "description": "Đáp ứng yêu cầu 'ăn hải sản' của gia đình."
            }
        ]
    )
    
    print(f"\n📍 Input State:")
    destination = state['trip_metadata'].get('destination', 'Unknown')
    print(f"  Destination: {destination}")
    print(f"  Group: {state['constraints'].get('group_size')} people")
    print(f"  Budget: {state['constraints'].get('travel_budget')} VNĐ")
    print(f"  Companions: {state['travel_preferences'].get('companion_type', [])}")
    print(f"  Preferences: {state['travel_preferences']}")
    
    # Debug: Test database functions
    print(f"\n🔍 DEBUG: Testing database functions...")
    try:
        destination_prov = state['trip_metadata'].get('destination', '')
        wards, routes = fetch_connected_wards(destination_prov)
        print(f"  ✓ Connected wards: {len(wards)} wards")
        print(f"  ✓ Routes count: {len(routes)}")
        
        providers = fetch_transport_options(wards if wards else [])
        print(f"  ✓ Transport providers: {len(providers)}")
        
        candidates = build_transport_candidates(
            routes=routes,
            providers=providers,
            constraints=state['constraints'],
            travel_preferences=state['travel_preferences'],
        )
        print(f"  ✓ Built candidates: {len(candidates)}")
        if candidates:
            print(f"    Sample: {candidates[0]}")
    except Exception as e:
        print(f"  ✗ Database function error: {e}")
        import traceback
        traceback.print_exc()
    
    # Run mobility_node
    try:
        result_state = mobility_node(state)
        
        print(f"\n✓ Mobility node executed successfully!")
        print(f"\n🚗 Output State:")
        print(f"  Transportations: {result_state.get('transportations', [])}")
        
        transportations = result_state.get('transportations', [])
        if transportations:
            print(f"\n  Sample transportation:")
            print(f"    Type: {transportations[0].get('type')}")
            print(f"    Distance: {transportations[0].get('distance_km')}km")
            print(f"    Price/person: {transportations[0].get('price_per_person', 0):,.0f} VNĐ")
            print(f"    Note: {transportations[0].get('note')}")
        
        # Assertions
        assert transportations, "Should have transportation options"
        assert isinstance(transportations, list), "Transportations should be a list"
        
        print(f"\n✓ All assertions passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_mobility_node_with_previous_node_output()
    exit(0 if success else 1)