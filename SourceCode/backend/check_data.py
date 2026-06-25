import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from workflow.db import get_mongo_db, get_neo4j_driver

db = get_mongo_db("TravelDB")
loc_col = db["Locations"]

activities = list(loc_col.find({"category": "Activity", "ward_name": "Bãi Cháy", "province_name": "Quảng Ninh"}))
print(f"MongoDB Activities in Bãi Cháy, Quảng Ninh: {len(activities)}")
for act in activities:
    print(f" - {act.get('name')}")

driver = get_neo4j_driver()
with driver.session() as session:
    result = session.run("MATCH (l:Location {category: 'Activity'})-[:LOCATED_IN]->(w:Ward {name: 'Bãi Cháy'}) RETURN l.name AS name")
    neo_acts = [r["name"] for r in result]
    print(f"Neo4j Activities in Bãi Cháy, Quảng Ninh: {len(neo_acts)}")
    for act in neo_acts:
        print(f" - {act}")
