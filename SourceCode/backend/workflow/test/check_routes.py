import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from workflow.db import get_neo4j_driver


def check_danang_routes():
    """Check if Đà Nẵng has CONNECTED_TO routes."""
    driver = get_neo4j_driver()
    with driver.session() as session:
        print("\n" + "="*60)
        print("CHECKING ĐÀ NẴNG ROUTES")
        print("="*60)
        
        # Check if any wards in Đà Nẵng have CONNECTED_TO relationships
        query = """
        MATCH (p:Province {name: "Đà Nẵng"})-[:HAS]->(w1:Ward)
        MATCH (w1)-[r:CONNECTED_TO]->(w2:Ward)
        RETURN w1.name AS from_ward, w2.name AS to_ward, r.distance_km AS distance
        LIMIT 10
        """
        
        results = session.run(query).data()
        print(f"\nRoutes found: {len(results)}")
        for r in results:
            print(f"  {r['from_ward']} → {r['to_ward']}: {r['distance']}km")
        
        if len(results) == 0:
            print("\n⚠️  No CONNECTED_TO routes found for Đà Nẵng!")
            print("\nChecking all routes in database...")
            all_routes = session.run(
                "MATCH ()-[r:CONNECTED_TO]->() RETURN COUNT(r) AS count"
            ).single()
            print(f"Total CONNECTED_TO relationships: {all_routes['count']}")
            
            # Find which provinces have routes
            prov_with_routes = session.run("""
            MATCH (p:Province)-[:HAS]->(w1:Ward)-[r:CONNECTED_TO]->(w2:Ward)
            RETURN DISTINCT p.name AS province, COUNT(r) AS route_count
            ORDER BY route_count DESC
            """).data()
            
            print(f"\nProvinces with routes:")
            for p in prov_with_routes:
                print(f"  - {p['province']}: {p['route_count']} routes")


if __name__ == "__main__":
    check_danang_routes()
