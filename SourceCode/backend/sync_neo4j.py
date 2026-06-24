from neo4j import GraphDatabase
import os
from pymongo import MongoClient

def sync_transports_to_neo4j():
    uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
    
    # 1. Lấy dữ liệu phương tiện từ MongoDB
    db = MongoClient("mongodb://localhost:27017/")["TravelDB"]
    transports = list(db.Locations.find({"category": "Transport", "province_name": "Ninh Bình"}))
    
    if not transports:
        print("Không tìm thấy phương tiện nào trong MongoDB.")
        return
        
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    with driver.session() as session:
        for t in transports:
            loc_id = t.get("locationId")
            name = t.get("name")
            category = t.get("category")
            province = t.get("province_name")
            ward = t.get("ward_name")
            
            # 2. Ghi vào Neo4j (Node Location và quan hệ với Ward)
            cypher_query = """
            MERGE (p:Province {name: $province})
            MERGE (w:Ward {name: $ward})
            MERGE (p)-[:HAS]->(w)
            MERGE (l:Location {locationId: $loc_id})
            SET l.name = $name, l.category = $category
            MERGE (l)-[:LOCATED_IN]->(w)
            """
            session.run(cypher_query, 
                        province=province, 
                        ward=ward, 
                        loc_id=loc_id, 
                        name=name, 
                        category=category)
            
            print(f"Đã đồng bộ {name} sang Neo4j!")
            
    print("Hoàn tất đồng bộ Phương tiện vào Neo4j.")

if __name__ == "__main__":
    sync_transports_to_neo4j()
