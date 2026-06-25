import sys
import os

# Cấu hình sys.path để có thể import các thư viện của backend
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "../../.."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from workflow.db import get_neo4j_driver

def create_relationships():
    """
    Tạo mối quan hệ CONNECTED_TO giữa các phường Bãi Cháy, Hạ Long, Hòn Gai
    """
    query = """
    // Tạo các Phường (MERGE để tạo nếu chưa có)
    MERGE (w1:Ward {name: "Bãi Cháy"})
    MERGE (w2:Ward {name: "Hạ Long"})
    MERGE (w3:Ward {name: "Hòn Gai"})
    
    // Đảm bảo chúng thuộc tỉnh Quảng Ninh
    MERGE (p:Province {name: "Quảng Ninh"})
    MERGE (p)-[:HAS]->(w1)
    MERGE (p)-[:HAS]->(w2)
    MERGE (p)-[:HAS]->(w3)
    
    // Tạo quan hệ hai chiều với khoảng cách (giả định)
    MERGE (w1)-[r12:CONNECTED_TO]->(w2) ON CREATE SET r12.distance_km = 5.0
    MERGE (w2)-[r21:CONNECTED_TO]->(w1) ON CREATE SET r21.distance_km = 5.0
    
    MERGE (w2)-[r23:CONNECTED_TO]->(w3) ON CREATE SET r23.distance_km = 4.0
    MERGE (w3)-[r32:CONNECTED_TO]->(w2) ON CREATE SET r32.distance_km = 4.0
    
    MERGE (w1)-[r13:CONNECTED_TO]->(w3) ON CREATE SET r13.distance_km = 8.0
    MERGE (w3)-[r31:CONNECTED_TO]->(w1) ON CREATE SET r31.distance_km = 8.0
    """
    
    print("Đang thực thi query tạo relationship...")
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            session.run(query)
        print("-> THÀNH CÔNG: Đã tạo mối quan hệ CONNECTED_TO giữa Bãi Cháy, Hạ Long và Hòn Gai.")
    except Exception as e:
        print(f"-> THẤT BẠI: {e}")

if __name__ == "__main__":
    create_relationships()
