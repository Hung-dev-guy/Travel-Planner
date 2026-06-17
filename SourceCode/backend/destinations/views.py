import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from workflow.db import get_mongo_db

logger = logging.getLogger(__name__)

def _serialize(doc):
    out = {}
    from bson import ObjectId
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, dict):
            out[k] = _serialize(v)
        elif isinstance(v, list):
            out[k] = [_serialize(i) if isinstance(i, dict) else (str(i) if isinstance(i, ObjectId) else i) for i in v]
        else:
            out[k] = v
    return out

@require_http_methods(["GET"])
def list_locations(request):
    try:
        db = get_mongo_db("TravelDB")
        col = db["Locations"]
        
        # Get query params
        category = request.GET.get('category', 'All')
        search_q = request.GET.get('q', '').strip()
        
        query = {}
        
        # Map frontend filters to DB categories
        if category != 'All':
            # Example mapping: 'Hotels' -> 'Stay', 'Activities' -> 'Activity', 'Rentals' -> 'Transport'
            cat_map = {
                'Hotels': 'Stay',
                'Activities': 'Activity',
                'Rentals': 'Transport',
                'Flights': 'Flight'
            }
            db_cat = cat_map.get(category, category)
            query["category"] = db_cat
            
        if search_q:
            query["name"] = {"$regex": search_q, "$options": "i"}
            
        locations = list(col.find(query).sort("_id", -1).limit(50))
        
        # Map DB docs to frontend expected format
        formatted_results = []
        for loc in locations:
            # Use img_url from DB or fake images for demo purposes based on category or province
            img = loc.get('img_url')
            if not img:
                prov = loc.get('province_name') or ''
                prov_lower = prov.lower()
                if 'đà nẵng' in prov_lower: img = 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=600&q=80'
                elif 'hội an' in prov_lower: img = 'https://images.unsplash.com/photo-1555921015-c26206080d81?w=600&q=80'
                elif 'hà nội' in prov_lower: img = 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=600&q=80'
                else:
                    if loc.get('category') == 'Stay': img = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&q=80'
                    else: img = 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&q=80'
            
            formatted_results.append({
                "type": "destination",
                "id": loc.get("locationId", str(loc["_id"])),
                "name": loc.get("name", "Unknown Location"),
                "description": loc.get("description", "Discover the magic of this amazing place."),
                "image": img,
                "price": loc.get("estimatedPrice", 0),
                "rating": 4.8, # Mock rating
                "category": loc.get("category", ""),
                "province": loc.get("province_name", ""),
            })
            
        return JsonResponse({"success": True, "results": formatted_results}, json_dumps_params={"ensure_ascii": False})
        
    except Exception as exc:
        logger.error(f"Error fetching locations: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)

@require_http_methods(["GET"])
def get_provinces(request):
    try:
        from neo4j import GraphDatabase
        import os
        uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session() as session:
            result = session.run("MATCH (p:Province) RETURN p.name AS name ORDER BY p.name")
            provinces = [record["name"] for record in result]
        return JsonResponse({"success": True, "provinces": provinces}, json_dumps_params={"ensure_ascii": False})
    except Exception as exc:
        logger.error(f"Error fetching provinces: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)

@require_http_methods(["GET"])
def get_wards(request):
    try:
        province = request.GET.get('province')
        if not province:
            return JsonResponse({"success": False, "error": "Missing province parameter"}, status=400)
            
        from neo4j import GraphDatabase
        import os
        uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session() as session:
            result = session.run("MATCH (p:Province {name: $province})-[:HAS]->(w:Ward) RETURN w.name AS name ORDER BY w.name", province=province)
            wards = [record["name"] for record in result]
        return JsonResponse({"success": True, "wards": wards}, json_dumps_params={"ensure_ascii": False})
    except Exception as exc:
        logger.error(f"Error fetching wards: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)

