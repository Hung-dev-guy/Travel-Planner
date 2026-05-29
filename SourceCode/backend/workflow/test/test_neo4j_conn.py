import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

# Add backend directory to path if run as a standalone script
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

def test_neo4j_connection():
    """
    Validate the Neo4j Graph Database connection using the configured credentials.
    """
    uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "12345678")

    print(f"Connecting to Neo4j at {uri}...")
    try:
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            # Verify connectivity
            driver.verify_connectivity()
            print("✅ Successfully connected to Neo4j!")
            
            # Execute a basic Cypher query to assert performance and session logic
            with driver.session() as session:
                result = session.run("RETURN 'Connection successful!' AS message")
                record = result.single()
                if record:
                    print(f"Cypher Query Output: {record['message']}")
                    
    except AuthError as e:
        print(f"❌ Neo4j Authentication Error: {e}")
        sys.exit(1)
    except ServiceUnavailable as e:
        print(f"❌ Neo4j Service Unavailable: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error connecting to Neo4j: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_neo4j_connection()
