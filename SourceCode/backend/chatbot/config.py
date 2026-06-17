import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Traplanner chatbot configuration."""
    SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "traplanner-dev-secret-key")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID")

    # MongoDB
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "TravelDB")

    # Neo4j
    NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "12345678")

    # Redis – used for conversation history (short-term memory)
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
    REDIS_DECODE_RESPONSES = True

    # Memory TTLs
    SHORT_TERM_MEMORY_TTL = int(os.environ.get("SHORT_TERM_MEMORY_TTL", 7200))   # 2 hours
    LONG_TERM_MEMORY_TTL = int(os.environ.get("LONG_TERM_MEMORY_TTL", 2592000))  # 30 days
    MAX_SHORT_TERM_MESSAGES = int(os.environ.get("MAX_SHORT_TERM_MESSAGES", 30))