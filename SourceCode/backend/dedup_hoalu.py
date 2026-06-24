from neo4j import GraphDatabase
import os

def deduplicate_ward():
    uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
    
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    with driver.session() as session:
        # Find all wards containing Hoa Lư (ignoring case)
        result = session.run("MATCH (w:Ward) WHERE w.name CONTAINS 'Hoa Lư' RETURN id(w) AS node_id, w.name AS name")
        wards = [{"id": record["node_id"], "name": record["name"]} for record in result]
        
        print("Found wards:", wards)
        
        # If there are exactly two, let's delete the one that is not exactly 'Hoa Lư' or just the second one
        if len(wards) > 1:
            # We keep the one that matches exactly 'Hoa Lư' or the first one if both are the same string
            keep_id = None
            for w in wards:
                if w["name"] == "Hoa Lư":
                    keep_id = w["id"]
                    break
            
            if not keep_id:
                keep_id = wards[0]["id"]
                
            for w in wards:
                if w["id"] != keep_id:
                    print(f"Deleting duplicate ward: {w['name']} (ID: {w['id']})")
                    # Delete the node and its relationships
                    session.run("MATCH (w:Ward) WHERE id(w) = $id DETACH DELETE w", id=w["id"])
                    print("Deleted.")
        else:
            print("No duplicates found.")

if __name__ == "__main__":
    deduplicate_ward()
