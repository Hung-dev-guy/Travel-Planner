import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.db import get_neo4j_driver, get_mongo_db


def debug_neo4j():
    """Inspect Neo4j data structure."""
    print("\n" + "="*60)
    print("NEO4J DEBUG")
    print("="*60)
    
    driver = get_neo4j_driver()
    with driver.session() as session:
        # Check all node types
        nodes_query = """
        MATCH (n) 
        RETURN DISTINCT labels(n) AS node_type, COUNT(*) AS count 
        LIMIT 10
        """
        print(f"\n📊 Node Types in Neo4j:")
        for record in session.run(nodes_query):
            print(f"  {record['node_type']}: {record['count']} nodes")
        
        # List all Provinces
        provinces_query = "MATCH (p:Province) RETURN p.name AS name"
        print(f"\n🗺️  Provinces:")
        provinces = []
        for record in session.run(provinces_query):
            print(f"  - {record['name']}")
            provinces.append(record['name'])
        
        # List Wards for first province
        if provinces:
            first_province = provinces[0]
            wards_query = (
                "MATCH (p:Province {name: $prov})-[:HAS]->(w:Ward) "
                "RETURN w.name AS name LIMIT 5"
            )
            print(f"\n🏘️  Wards in '{first_province}':")
            for record in session.run(wards_query, prov=first_province):
                print(f"  - {record['name']}")
        
        # Check connected routes
        if provinces:
            routes_query = (
                "MATCH (p:Province {name: $prov})-[:HAS]->(w1:Ward) "
                "MATCH (w1)-[r:CONNECTED_TO]->(w2:Ward) "
                "RETURN w1.name AS from_ward, w2.name AS to_ward, r.distance_km AS dist "
                "LIMIT 5"
            )
            print(f"\n🛣️  Sample Routes in '{first_province}':")
            for record in session.run(routes_query, prov=first_province):
                print(f"  {record['from_ward']} → {record['to_ward']}: {record['dist']}km")


def debug_mongodb():
    """Inspect MongoDB data structure."""
    print("\n" + "="*60)
    print("MONGODB DEBUG")
    print("="*60)
    
    db = get_mongo_db("TravelDB")
    
    # List collections
    print(f"\n📦 Collections in TravelDB:")
    for coll in db.list_collection_names():
        print(f"  - {coll}")
    
    # Check Locations collection
    locations = db["Locations"]
    print(f"\n📍 Locations count: {locations.count_documents({})}")
    
    # Sample transport locations
    print(f"\n🚗 Sample Transport Locations:")
    transport_cats = ["Transport", "Transportation", "Mobility"]
    samples = locations.find(
        {"category": {"$in": transport_cats}},
        {"name": 1, "category": 1, "ward_name": 1}
    ).limit(5)
    for doc in samples:
        print(f"  - {doc.get('name', 'N/A')} ({doc.get('category', 'N/A')}) in {doc.get('ward_name', 'N/A')}")
    
    # Unique wards in Locations
    print(f"\n🏘️  Wards with Locations:")
    wards = locations.distinct("ward_name")
    for ward in wards[:10]:
        count = locations.count_documents({"ward_name": ward})
        print(f"  - {ward}: {count} locations")


def test_fetch_functions():
    """Test the actual fetch functions."""
    print("\n" + "="*60)
    print("TESTING FETCH FUNCTIONS")
    print("="*60)
    
    from workflow.nodes.Mobility_agent import fetch_connected_wards, fetch_transport_options
    
    # Get first province from Neo4j
    driver = get_neo4j_driver()
    with driver.session() as session:
        province_query = "MATCH (p:Province) RETURN p.name AS name LIMIT 1"
        result = session.run(province_query).single()
        
        if result:
            first_province = result["name"]
            print(f"\n🔍 Testing with province: {first_province}")
            
            try:
                wards, routes = fetch_connected_wards(first_province)
                print(f"  ✓ Connected wards: {len(wards)}")
                if wards:
                    print(f"    {wards}")
                print(f"  ✓ Routes: {len(routes)}")
                if routes:
                    print(f"    {routes[0]}")
                
                # Test fetch_transport_options
                if wards:
                    providers = fetch_transport_options(wards[:3])
                    print(f"  ✓ Providers found: {len(providers)}")
                    if providers:
                        print(f"    {providers[0]}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    debug_neo4j()
    debug_mongodb()
    test_fetch_functions()
