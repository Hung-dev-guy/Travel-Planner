"""
workflow/db.py
Shared, lazily-initialized database connectors.
Import `get_neo4j_driver()` or `get_mongo_db()` in any node — connections
are created once per process and reused across calls.
"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pymongo import MongoClient

load_dotenv()

# ── Internal singletons (do not use directly) ─────────────────────────────────
_neo4j_driver = None
_mongo_client = None

# ── Public accessors ──────────────────────────────────────────────────────────

def get_neo4j_driver():
    """Return a shared Neo4j driver instance (created lazily)."""
    global _neo4j_driver
    if _neo4j_driver is None:
        uri      = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "12345678")
        _neo4j_driver = GraphDatabase.driver(uri, auth=(username, password))
    return _neo4j_driver


def get_mongo_db(database: str = "TravelDB"):
    """Return a PyMongo Database handle (client created lazily)."""
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGO_URI")
        # Add SSL parameters to URI if not already present
        if uri and "tlsAllowInvalidCertificates" not in uri:
            separator = "&" if "?" in uri else "?"
            uri = f"{uri}{separator}tlsAllowInvalidCertificates=true"
        
        _mongo_client = MongoClient(
            uri,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            retryWrites=True,
        )
        # Test connection
        try:
            _mongo_client.admin.command('ping')
        except Exception as e:
            print(f"MongoDB connection warning: {e}")
    return _mongo_client[database]

def reset_mongo_connection():
    """Reset MongoDB connection (useful for testing or reconnecting after network issues)."""
    global _mongo_client
    if _mongo_client is not None:
        try:
            _mongo_client.close()
        except Exception:
            pass
    _mongo_client = None