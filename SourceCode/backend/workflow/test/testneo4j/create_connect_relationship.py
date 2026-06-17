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
    Tạo mối quan hệ CONNECTED_TO giữa phường Tây Hoa Lư với Hoa Lư và Nam Hoa Lư
    """
    query = """
    // Tạo các Phường (MERGE để tạo nếu chưa có)
    MERGE (w1:Ward {name: "Tây Hoa Lư"})
    MERGE (w2:Ward {name: "Hoa Lư"})
    MERGE (w3:Ward {name: "Nam Hoa Lư"})
    
    // Đảm bảo chúng thuộc tỉnh Ninh Bình
    MERGE (p:Province {name: "Ninh Bình"})
    MERGE (p)-[:HAS]->(w1)
    MERGE (p)-[:HAS]->(w2)
    MERGE (p)-[:HAS]->(w3)
    
    // Tạo quan hệ hai chiều (hoặc một chiều vì truy vấn của Planner không quan tâm hướng)
    MERGE (w1)-[:CONNECTED_TO]->(w2)
    MERGE (w2)-[:CONNECTED_TO]->(w1)
    
    MERGE (w1)-[:CONNECTED_TO]->(w3)
    MERGE (w3)-[:CONNECTED_TO]->(w1)
    """
    
    print("Đang thực thi query tạo relationship...")
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            session.run(query)
        print("-> THÀNH CÔNG: Đã tạo mối quan hệ CONNECTED_TO giữa Tây Hoa Lư với Hoa Lư và Nam Hoa Lư.")
    except Exception as e:
        print(f"-> THẤT BẠI: {e}")

if __name__ == "__main__":
    create_relationships()
