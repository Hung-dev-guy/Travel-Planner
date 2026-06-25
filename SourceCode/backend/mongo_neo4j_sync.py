import os
import sys
import time
from pymongo import MongoClient
from neo4j import GraphDatabase

def sync_daemon():
    print("Khởi động MongoDB -> Neo4j Change Stream Sync Daemon...")
    
    mongo_uri = "mongodb://localhost:27017/"
    db_name = "TravelDB"
    col_name = "Locations"
    
    neo4j_uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USERNAME", "neo4j")
    neo4j_pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
    
    try:
        mongo_client = MongoClient(mongo_uri)
        db = mongo_client[db_name]
        col = db[col_name]
        
        # Thử mở change stream
        pipeline = [{"$match": {"operationType": {"$in": ["insert", "update", "replace", "delete"]}}}]
        stream = col.watch(pipeline)
        
        neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pwd))
        
        print("Đang lắng nghe các thay đổi trên collection Locations...")
        
        for change in stream:
            op_type = change["operationType"]
            doc_id = change["documentKey"]["_id"]
            print(f"Phát hiện sự kiện: {op_type} trên _id: {doc_id}")
            
            with neo4j_driver.session() as session:
                if op_type == "delete":
                    # Mặc dù không lấy được locationId cũ, ta cố xóa theo _id dạng chuỗi hoặc id gốc
                    session.run("MATCH (l:Location {mongo_id: $m_id}) DETACH DELETE l", m_id=str(doc_id))
                    # Xóa theo locationId nếu có query thủ công
                    print("Đã xóa node khỏi Neo4j (nếu tồn tại).")
                
                elif op_type in ["insert", "update", "replace"]:
                    full_doc = change.get("fullDocument")
                    if not full_doc and op_type == "update":
                        # Cần fetch lại
                        full_doc = col.find_one({"_id": doc_id})
                    
                    if not full_doc:
                        continue
                        
                    loc_id = full_doc.get("locationId", str(doc_id))
                    name = full_doc.get("name", "Unknown")
                    category = full_doc.get("category", "Activity")
                    ward = full_doc.get("ward_name")
                    province = full_doc.get("province_name")
                    
                    # Cập nhật Neo4j
                    if ward and province:
                        cypher = """
                        MERGE (p:Province {name: $province})
                        MERGE (w:Ward {name: $ward})
                        MERGE (p)-[:HAS]->(w)
                        MERGE (l:Location {locationId: $loc_id})
                        SET l.name = $name, l.category = $category, l.mongo_id = $m_id
                        WITH l, w
                        OPTIONAL MATCH (l)-[r:LOCATED_IN]->()
                        DELETE r
                        WITH l, w
                        MERGE (l)-[:LOCATED_IN]->(w)
                        """
                        session.run(cypher, province=province, ward=ward, loc_id=loc_id, name=name, category=category, m_id=str(doc_id))
                        print(f"Đã cập nhật/thêm node {name} vào Neo4j.")
                        
    except Exception as e:
        print(f"Lỗi: {e}")
        print("Lưu ý: Change Streams yêu cầu MongoDB phải chạy dưới dạng Replica Set.")

if __name__ == "__main__":
    sync_daemon()
