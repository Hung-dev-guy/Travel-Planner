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
            "destination": "Quảng Ninh",
        },
        constraints={
            "group_size": 2,
            "travel_budget": 200_000,
            "mobility_limitations": [],
        },
        travel_preferences={
            "travel_pace": ["thong thả"],
            "vibe": ["lãng mạn"],
            "companion_type": ["Couples"],
            "health_constraints": []
        },
        extracted_activities=[],
        planned_itinerary=[],
    )
    
    print(f"\n📍 Input State:")
    destination = state['trip_metadata'].get('destination', 'Unknown')
    print(f"  Destination: {destination}")
    print(f"  Group: {state['constraints'].get('group_size')} people")
    print(f"  Budget: {state['constraints'].get('travel_budget'):,.0f} VNĐ")
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