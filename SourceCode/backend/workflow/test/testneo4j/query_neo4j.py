import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

load_dotenv()

uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
username = os.getenv("NEO4J_USERNAME", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "12345678")

try:
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            result = session.run("MATCH (p:Province) RETURN p.name AS name LIMIT 10")
            print("Provinces in Neo4j:")
            for record in result:
                print(f"- {record['name']}")
except Exception as e:
    print(f"Error: {e}")
