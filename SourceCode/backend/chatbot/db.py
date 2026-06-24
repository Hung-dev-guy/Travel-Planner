"""
chatbot/db.py
Database layer for the Traplanner chatbot.
- MongoDB: fetches Trips, DayDetails (TravelDB) and location/POI data.
- Neo4j: queries for optimal alternatives (hotels, eateries, attractions, transport).
All connections are lazily initialised singletons shared across requests.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Singletons 
_mongo_client: MongoClient = None
_neo4j_driver = None


# MongoDB

def get_mongo_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        if uri and "tlsAllowInvalidCertificates" not in uri:
            sep = "&" if "?" in uri else "?"
            uri = f"{uri}{sep}tlsAllowInvalidCertificates=true"
        _mongo_client = MongoClient(
            uri,
            serverSelectionTimeoutMS=15_000,
            connectTimeoutMS=15_000,
            retryWrites=True,
        )
        try:
            _mongo_client.admin.command("ping")
            logger.info("MongoDB connected (chatbot)")
        except Exception as e:
            logger.warning(f"MongoDB ping failed: {e}")
    return _mongo_client


def get_travel_db():
    """Return TravelDB database handle."""
    db_name = os.getenv("MONGO_DB_NAME", "TravelDB")
    return get_mongo_client()[db_name]


# Trip helpers

def serialize(doc: dict) -> dict:
    """Convert ObjectId fields to strings so the doc is JSON-serialisable."""
    if doc is None:
        return {}
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, dict):
            out[k] = serialize(v)
        elif isinstance(v, list):
            out[k] = [serialize(i) if isinstance(i, dict) else
                      (str(i) if isinstance(i, ObjectId) else i)
                      for i in v]
        else:
            out[k] = v
    return out


def get_trips_for_user(user_id: str) -> List[Dict[str, Any]]:
    """Return all trips belonging to *user_id* (sorted newest first)."""
    try:
        db = get_travel_db()
        cursor = db["Trips"].find(
            {"userId": user_id},
            {"_id": 1, "tripId": 1, "destination": 1, "status": 1,
             "totalBudget": 1, "createdAt": 1}
        ).sort("createdAt", -1)
        return [serialize(doc) for doc in cursor]
    except Exception as exc:
        logger.error(f"get_trips_for_user error: {exc}")
        return []


def get_trip_by_id(trip_id: str) -> Optional[Dict[str, Any]]:
    """Return a single Trip document by its tripId string."""
    try:
        db = get_travel_db()
        doc = db["Trips"].find_one({"tripId": trip_id})
        return serialize(doc) if doc else None
    except Exception as exc:
        logger.error(f"get_trip_by_id error: {exc}")
        return None


def get_day_details_for_trip(trip_id: str) -> List[Dict[str, Any]]:
    """Return all DayDetails documents for a trip, sorted by dayNumber."""
    try:
        db = get_travel_db()
        cursor = db["DayDetails"].find(
            {"tripId": trip_id}
        ).sort("dayNumber", 1)
        return [serialize(doc) for doc in cursor]
    except Exception as exc:
        logger.error(f"get_day_details_for_trip error: {exc}")
        return []


def get_full_trip_context(trip_id: str) -> Dict[str, Any]:
    """Return a single dict combining Trip + DayDetails for LLM context."""
    trip = get_trip_by_id(trip_id)
    if not trip:
        return {}
    days = get_day_details_for_trip(trip_id)
    return {"trip": trip, "day_details": days}


def update_trip(trip_id: str, updates: Dict[str, Any]) -> bool:
    """Update fields on a Trip document. Returns True on success."""
    try:
        db = get_travel_db()
        result = db["Trips"].update_one(
            {"tripId": trip_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    except Exception as exc:
        logger.error(f"update_trip error: {exc}")
        return False


def update_day_detail(day_schedule_id: str, updates: Dict[str, Any]) -> bool:
    """Update a single DayDetails document by dayScheduleDetailedId."""
    try:
        db = get_travel_db()
        result = db["DayDetails"].update_one(
            {"dayScheduleDetailedId": day_schedule_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    except Exception as exc:
        logger.error(f"update_day_detail error: {exc}")
        return False


def save_full_trip(trip_id: str, trip_doc: Dict[str, Any],
                   day_details: List[Dict[str, Any]]) -> bool:
    """
    Upsert the Trip document and replace all its DayDetails.
    Used when the user saves a manually edited itinerary.
    """
    try:
        db = get_travel_db()
        db["Trips"].update_one(
            {"tripId": trip_id},
            {"$set": trip_doc},
            upsert=True
        )
        if day_details:
            # Remove old day details then insert new ones
            db["DayDetails"].delete_many({"tripId": trip_id})
            db["DayDetails"].insert_many(day_details)
        logger.info(f"Saved trip {trip_id} with {len(day_details)} day-detail docs")
        return True
    except Exception as exc:
        logger.error(f"save_full_trip error: {exc}")
        return False


def add_activity_to_day(trip_id: str, day_number: int, new_activity: Dict[str, Any]) -> bool:
    try:
        db = get_travel_db()
        result = db["DayDetails"].update_one(
            {"tripId": trip_id, "dayNumber": day_number},
            {"$push": {"dayActs": new_activity}}
        )
        return result.modified_count > 0
    except Exception as exc:
        logger.error(f"add_activity_to_day error: {exc}")
        return False

def remove_activity_from_day(trip_id: str, day_number: int, activity_name: str) -> bool:
    try:
        db = get_travel_db()
        # Find the day document first to handle case-insensitive or partial match
        day_doc = db["DayDetails"].find_one({"tripId": trip_id, "dayNumber": day_number})
        if not day_doc or "dayActs" not in day_doc:
            return False
            
        acts = day_doc["dayActs"]
        new_acts = [act for act in acts if activity_name.lower() not in str(act.get("name", "")).lower()]
        
        if len(acts) == len(new_acts):
            return False # Nothing removed
            
        result = db["DayDetails"].update_one(
            {"_id": day_doc["_id"]},
            {"$set": {"dayActs": new_acts}}
        )
        return result.modified_count > 0
    except Exception as exc:
        logger.error(f"remove_activity_from_day error: {exc}")
        return False

def update_activity_in_day(trip_id: str, day_number: int, old_activity_name: str, new_activity: Dict[str, Any]) -> bool:
    try:
        db = get_travel_db()
        day_doc = db["DayDetails"].find_one({"tripId": trip_id, "dayNumber": day_number})
        if not day_doc or "dayActs" not in day_doc:
            return False
            
        acts = day_doc["dayActs"]
        updated = False
        for i, act in enumerate(acts):
            if old_activity_name.lower() in str(act.get("name", "")).lower():
                # Merge fields to preserve existing startTime, endTime, and location
                for k, v in new_activity.items():
                    if v != "":
                        act[k] = v
                updated = True
                break # Only replace the first match
                
        if not updated:
            return False
            
        result = db["DayDetails"].update_one(
            {"_id": day_doc["_id"]},
            {"$set": {"dayActs": acts}}
        )
        return result.modified_count > 0
    except Exception as exc:
        logger.error(f"update_activity_in_day error: {exc}")
        return False



# Location helpers (MongoDB Locations collection) 
def search_locations(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Simple text search on the Locations collection."""
    try:
        db = get_travel_db()
        # Use regex search if no full-text index is configured
        cursor = db["Locations"].find(
            {"name": {"$regex": query, "$options": "i"}},
            {"_id": 1, "name": 1, "category": 1, "address": 1,
             "description": 1, "price_range": 1, "image_url": 1}
        ).limit(limit)
        return [serialize(doc) for doc in cursor]
    except Exception as exc:
        logger.error(f"search_locations error: {exc}")
        return []


def get_locations_by_category(category: str, destination: str = "",
                               limit: int = 10) -> List[Dict[str, Any]]:
    """Return locations filtered by category and optional destination."""
    try:
        db = get_travel_db()
        query: Dict[str, Any] = {"category": {"$regex": category, "$options": "i"}}
        if destination:
            query["address"] = {"$regex": destination, "$options": "i"}
        cursor = db["Locations"].find(
            query,
            {"_id": 1, "name": 1, "category": 1, "address": 1,
             "description": 1, "price_range": 1, "image_url": 1}
        ).limit(limit)
        return [serialize(doc) for doc in cursor]
    except Exception as exc:
        logger.error(f"get_locations_by_category error: {exc}")
        return []


# Neo4j helpers

def _get_neo4j_driver():
    global _neo4j_driver
    if _neo4j_driver is None:
        from neo4j import GraphDatabase
        uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "12345678")
        _neo4j_driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info("Neo4j driver initialised (chatbot)")
    return _neo4j_driver


def neo4j_find_alternative_hotels(destination: str,
                                   max_price: float,
                                   limit: int = 5) -> List[Dict[str, Any]]:
    """Query Neo4j for hotels in *destination* within budget."""
    try:
        driver = _get_neo4j_driver()
        with driver.session() as session:
            result = session.run(
                """
                MATCH (h:Hotel)
                WHERE toLower(h.city) CONTAINS toLower($destination)
                  AND h.price_per_night <= $max_price
                RETURN h.name AS name, h.price_per_night AS price,
                       h.star_rating AS stars, h.address AS address
                ORDER BY h.star_rating DESC
                LIMIT $limit
                """,
                destination=destination, max_price=max_price, limit=limit
            )
            return [dict(r) for r in result]
    except Exception as exc:
        logger.warning(f"neo4j_find_alternative_hotels error: {exc}")
        return []


def neo4j_find_alternative_restaurants(destination: str,
                                        cuisine: str = "",
                                        max_price: float = 500_000,
                                        limit: int = 5) -> List[Dict[str, Any]]:
    """Query Neo4j for restaurants matching cuisine and budget."""
    try:
        driver = _get_neo4j_driver()
        with driver.session() as session:
            cypher = """
                MATCH (r:Restaurant)
                WHERE toLower(r.city) CONTAINS toLower($destination)
                  AND r.avg_price <= $max_price
            """
            if cuisine:
                cypher += " AND toLower(r.cuisine) CONTAINS toLower($cuisine)"
            cypher += """
                RETURN r.name AS name, r.cuisine AS cuisine,
                       r.avg_price AS avg_price, r.address AS address
                ORDER BY r.avg_price ASC
                LIMIT $limit
            """
            result = session.run(
                cypher, destination=destination, max_price=max_price,
                cuisine=cuisine, limit=limit
            )
            return [dict(r) for r in result]
    except Exception as exc:
        logger.warning(f"neo4j_find_alternative_restaurants error: {exc}")
        return []


def neo4j_find_attractions(destination: str,
                            activity_type: str = "",
                            limit: int = 5) -> List[Dict[str, Any]]:
    """Query Neo4j for tourist attractions / activities."""
    try:
        driver = _get_neo4j_driver()
        with driver.session() as session:
            cypher = """
                MATCH (a:Attraction)
                WHERE toLower(a.city) CONTAINS toLower($destination)
            """
            if activity_type:
                cypher += " AND toLower(a.type) CONTAINS toLower($activity_type)"
            cypher += """
                RETURN a.name AS name, a.type AS type,
                       a.entry_fee AS entry_fee, a.description AS description,
                       a.address AS address
                ORDER BY a.popularity DESC
                LIMIT $limit
            """
            result = session.run(
                cypher, destination=destination,
                activity_type=activity_type, limit=limit
            )
            return [dict(r) for r in result]
    except Exception as exc:
        logger.warning(f"neo4j_find_attractions error: {exc}")
        return []


def neo4j_find_transportation(from_city: str,
                               to_city: str,
                               transport_type: str = "",
                               limit: int = 5) -> List[Dict[str, Any]]:
    """Query Neo4j for transport options between two cities."""
    try:
        driver = _get_neo4j_driver()
        with driver.session() as session:
            cypher = """
                MATCH (t:Transportation)
                WHERE toLower(t.from_city) CONTAINS toLower($from_city)
                  AND toLower(t.to_city) CONTAINS toLower($to_city)
            """
            if transport_type:
                cypher += " AND toLower(t.type) CONTAINS toLower($transport_type)"
            cypher += """
                RETURN t.type AS type, t.provider AS provider,
                       t.duration_hours AS duration_hours,
                       t.price AS price, t.departure_times AS departure_times
                ORDER BY t.price ASC
                LIMIT $limit
            """
            result = session.run(
                cypher, from_city=from_city, to_city=to_city,
                transport_type=transport_type, limit=limit
            )
            return [dict(r) for r in result]
    except Exception as exc:
        logger.warning(f"neo4j_find_transportation error: {exc}")
        return []