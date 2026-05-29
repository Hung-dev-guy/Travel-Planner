import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Add backend directory to path if run as a standalone script
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """
    Validate the MongoDB Atlas connection using the configured URI.
    """
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("❌ Error: MONGO_URI not found in environment or .env file.")
        sys.exit(1)

    print(f"Connecting to MongoDB...")
    try:
        # Set server selection timeout to 5 seconds
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Ping the admin database to verify connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # List available databases
        db_names = client.list_database_names()
        print("Available databases:")
        for db in db_names:
            print(f" - {db}")
            
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)
    except OperationFailure as e:
        print(f"⚠️ Connected, but failed to list databases (authorization limits): {e}")
    except Exception as e:
        print(f"❌ Unexpected error connecting to MongoDB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_mongodb_connection()
