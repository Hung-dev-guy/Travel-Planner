import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from workflow.db import get_mongo_db
import json
import uuid
import datetime

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
            lat = loc.get("location", {}).get("coordinates", [None, None])[1] if loc.get("location") else None
            lng = loc.get("location", {}).get("coordinates", [None, None])[0] if loc.get("location") else None
            
            formatted_results.append({
                "type": "destination",
                "id": loc.get("locationId", str(loc["_id"])),
                "name": loc.get("name", "Unknown Location"),
                "description": loc.get("description", "Discover the magic of this amazing place."),
                "image": loc.get('img_url') or loc.get('image_url') or "",
                "price": loc.get("estimatedPrice", 0),
                "rating": 4.8, # Mock rating
                "category": loc.get("category", ""),
                "province_name": loc.get("province_name", ""),
                "ward_name": loc.get("ward_name", ""),
                "latitude": lat,
                "longitude": lng,
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

@csrf_exempt
@require_http_methods(["POST"])
def add_location(request):
    try:
        # 1. Lấy dữ liệu từ Request
        payload = json.loads(request.body)
        name = payload.get("name", "").strip()
        category = payload.get("category", "Activity")
        description = payload.get("description", "")
        img_url = payload.get("img_url", "")
        price = int(payload.get("estimatedPrice", 0))
        ward_name = payload.get("ward_name", "").strip()
        province_name = payload.get("province_name", "").strip()
        
        if not name or not ward_name or not province_name:
            return JsonResponse({"success": False, "error": "Thiếu thông tin bắt buộc (name, ward_name, province_name)"}, status=400)
            
        location_id = f"LOC_{uuid.uuid4().hex[:8].upper()}"
        
        # 2. GHI VÀO MONGODB (Thick Data)
        db = get_mongo_db("TravelDB")
        new_loc = {
            "locationId": location_id,
            "name": name,
            "category": category,
            "description": description,
            "img_url": img_url,
            "estimatedPrice": price,
            "ward_name": ward_name,
            "province_name": province_name,
            "suitabilityFor": payload.get("suitabilityFor", ["Family", "Couples", "Solo"]),
            "estimatedDuration": payload.get("estimatedDuration", 120),
            "openingHours": payload.get("openingHours", "08:00 - 22:00")
        }
        
        latitude = payload.get("latitude")
        longitude = payload.get("longitude")
        if latitude is not None and longitude is not None and str(latitude).strip() != "" and str(longitude).strip() != "":
            try:
                lat = float(latitude)
                lng = float(longitude)
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    return JsonResponse({"success": False, "error": "Vĩ độ phải từ -90 đến 90, kinh độ từ -180 đến 180."}, status=400)
                new_loc["location"] = {
                    "type": "Point",
                    "coordinates": [lng, lat]
                }
            except ValueError:
                return JsonResponse({"success": False, "error": "Tọa độ không hợp lệ."}, status=400)
                
        db["Locations"].insert_one(new_loc)
        
        # 3. GHI KÉP VÀO NEO4J (Thin Data & Graph)
        from neo4j import GraphDatabase
        import os
        uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
        
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session() as session:
            # Cypher MERGE: Nếu chưa có Tỉnh/Phường thì tạo mới, có rồi thì bỏ qua. Sau đó tạo Location Node và nối vào Phường
            cypher_query = """
            MERGE (p:Province {name: $province})
            MERGE (w:Ward {name: $ward})
            MERGE (p)-[:HAS]->(w)
            MERGE (l:Location {locationId: $loc_id})
            SET l.name = $name, l.category = $category
            MERGE (l)-[:LOCATED_IN]->(w)
            """
            session.run(cypher_query, 
                        province=province_name, 
                        ward=ward_name, 
                        loc_id=location_id, 
                        name=name, 
                        category=category)
            
        return JsonResponse({"success": True, "message": "Thêm địa điểm thành công vào MongoDB và Neo4j!", "locationId": location_id})
        
    except Exception as exc:
        logger.error(f"Error adding location: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_transport(request):
    try:
        payload = json.loads(request.body)
        from_city = payload.get("from_city", "").strip()
        to_city = payload.get("to_city", "").strip()
        transport_type = payload.get("type", "").strip()
        provider = payload.get("provider", "").strip()
        price = float(payload.get("price", 0))
        duration_hours = float(payload.get("duration_hours", 0))
        departure_times = payload.get("departure_times", "")
        
        if not from_city or not to_city or not transport_type:
            return JsonResponse({"success": False, "error": "Thiếu thông tin bắt buộc (from_city, to_city, type)"}, status=400)
            
        from neo4j import GraphDatabase
        import os
        uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
        
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session() as session:
            cypher_query = """
            CREATE (t:Transportation {
                from_city: $from_city,
                to_city: $to_city,
                type: $type,
                provider: $provider,
                price: $price,
                duration_hours: $duration_hours,
                departure_times: $departure_times
            })
            """
            session.run(cypher_query, 
                        from_city=from_city, 
                        to_city=to_city, 
                        type=transport_type, 
                        provider=provider, 
                        price=price,
                        duration_hours=duration_hours,
                        departure_times=departure_times)
            
        # Optional: Save to MongoDB so it shows up in destinations list
        try:
            db = get_mongo_db("TravelDB")
            db["Locations"].insert_one({
                "locationId": f"TRANS_{uuid.uuid4().hex[:8].upper()}",
                "name": f"{transport_type.capitalize()} từ {from_city} đi {to_city} ({provider})",
                "category": "Transport",
                "description": f"Hành trình: {duration_hours} giờ. Khởi hành: {departure_times}",
                "estimatedPrice": price,
                "province_name": from_city
            })
        except Exception as e:
            logger.warning(f"Failed to save transport to MongoDB: {e}")
            
        return JsonResponse({"success": True, "message": "Thêm phương tiện thành công!"})
        
    except Exception as exc:
        logger.error(f"Error adding transport: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_review(request):
    try:
        payload = json.loads(request.body)
        location_id = payload.get("locationId")
        user_name = payload.get("userName", "Anonymous")
        rating = float(payload.get("rating", 5))
        comment = payload.get("comment", "").strip()
        
        if not location_id:
            return JsonResponse({"success": False, "error": "Thiếu locationId"}, status=400)
            
        db = get_mongo_db("TravelDB")
        
        review_doc = {
            "locationId": location_id,
            "userName": user_name,
            "rating": rating,
            "comment": comment,
            "createdAt": datetime.datetime.now()
        }
        db["Reviews"].insert_one(review_doc)
        
        pipeline = [
            {"$match": {"locationId": location_id}},
            {"$group": {"_id": "$locationId", "avgRating": {"$avg": "$rating"}, "count": {"$sum": 1}}}
        ]
        stats = list(db["Reviews"].aggregate(pipeline))
        
        new_avg = 4.8
        if stats:
            new_avg = round(stats[0]["avgRating"], 1)
            
        db["Locations"].update_one(
            {"locationId": location_id},
            {"$set": {"rating": new_avg}}
        )
        
        return JsonResponse({"success": True, "message": "Thêm đánh giá thành công!", "newRating": new_avg})
        
    except Exception as exc:
        logger.error(f"Error adding review: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)

@require_http_methods(["GET"])
def get_reviews(request):
    try:
        location_id = request.GET.get('locationId')
        if not location_id:
            return JsonResponse({"success": False, "error": "Thiếu locationId"}, status=400)
            
        db = get_mongo_db("TravelDB")
        reviews = list(db["Reviews"].find({"locationId": location_id}).sort("createdAt", -1))
        
        formatted = []
        for r in reviews:
            formatted.append({
                "id": str(r["_id"]),
                "userName": r.get("userName", "Anonymous"),
                "rating": r.get("rating", 5),
                "comment": r.get("comment", ""),
                "createdAt": r.get("createdAt", "").isoformat() if hasattr(r.get("createdAt", ""), "isoformat") else str(r.get("createdAt", ""))
            })
            
        return JsonResponse({"success": True, "reviews": formatted})
    except Exception as exc:
        logger.error(f"Error fetching reviews: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)

@require_http_methods(["GET"])
def get_trips_by_location(request):
    try:
        location_name = request.GET.get('locationName')
        if not location_name:
            return JsonResponse({"success": False, "error": "Thiếu locationName"}, status=400)
            
        db = get_mongo_db("TravelDB")
        
        day_details = list(db["DayDetails"].find({"dayActs.name": {"$regex": location_name, "$options": "i"}}))
        trip_ids = list(set([str(d["tripId"]) for d in day_details]))
        
        trips = list(db["Trips"].find({"tripId": {"$in": trip_ids}}))
        
        formatted = []
        for t in trips:
            formatted.append({
                "tripId": t["tripId"],
                "destination": t.get("destination", "Chuyến đi"),
                "totalBudget": t.get("totalBudget", 0),
                "durationDays": t.get("durationDays", 1)
            })
            
        return JsonResponse({"success": True, "trips": formatted})
    except Exception as exc:
        logger.error(f"Error fetching trips by location: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)

@csrf_exempt
@require_http_methods(["PUT", "POST"])
def edit_location(request):
    try:
        payload = json.loads(request.body)
        location_id = payload.get("locationId")
        if not location_id:
            return JsonResponse({"success": False, "error": "Thiếu locationId"}, status=400)
            
        update_data = {}
        for key in ["name", "description", "category", "estimatedPrice", "province_name", "ward_name", "image", "rating"]:
            if key in payload:
                if key in ["estimatedPrice", "rating"]:
                    try: update_data[key] = float(payload[key])
                    except: pass
                else:
                    update_data[key] = payload[key]
                    
        latitude = payload.get("latitude")
        longitude = payload.get("longitude")
        if latitude is not None and longitude is not None and str(latitude).strip() != "" and str(longitude).strip() != "":
            try:
                lat = float(latitude)
                lng = float(longitude)
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    return JsonResponse({"success": False, "error": "Vĩ độ phải từ -90 đến 90, kinh độ từ -180 đến 180."}, status=400)
                update_data["location"] = {
                    "type": "Point",
                    "coordinates": [lng, lat]
                }
            except ValueError:
                return JsonResponse({"success": False, "error": "Tọa độ không hợp lệ."}, status=400)
                    
        if not update_data:
            return JsonResponse({"success": False, "error": "Không có dữ liệu để cập nhật"}, status=400)
            
        db = get_mongo_db("TravelDB")
        result = db["Locations"].update_one(
            {"locationId": location_id},
            {"$set": update_data}
        )
        
        # Cập nhật Neo4j nếu có thay đổi liên quan
        if any(k in update_data for k in ["name", "category", "ward_name", "province_name"]):
            from neo4j import GraphDatabase
            import os
            uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
            user = os.environ.get("NEO4J_USERNAME", "neo4j")
            pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
            
            try:
                driver = GraphDatabase.driver(uri, auth=(user, pwd))
                with driver.session() as session:
                    cypher_query = """
                    MATCH (l:Location {locationId: $loc_id})
                    SET l.name = COALESCE($name, l.name), 
                        l.category = COALESCE($category, l.category)
                    WITH l
                    """
                    if "ward_name" in update_data and "province_name" in update_data:
                        cypher_query += """
                        OPTIONAL MATCH (l)-[r:LOCATED_IN]->()
                        DELETE r
                        WITH l
                        MERGE (p:Province {name: $province})
                        MERGE (w:Ward {name: $ward})
                        MERGE (p)-[:HAS]->(w)
                        MERGE (l)-[:LOCATED_IN]->(w)
                        """
                    
                    session.run(
                        cypher_query,
                        loc_id=location_id,
                        name=update_data.get("name"),
                        category=update_data.get("category"),
                        province=update_data.get("province_name"),
                        ward=update_data.get("ward_name")
                    )
            except Exception as e:
                logger.warning(f"Failed to update Neo4j for location {location_id}: {e}")
                
        return JsonResponse({"success": True, "message": "Cập nhật thành công!"})
        
    except Exception as exc:
        logger.error(f"Error editing location: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_location(request):
    try:
        payload = json.loads(request.body)
        location_id = payload.get("locationId")
        location_name = payload.get("name")
        
        if not location_id:
            return JsonResponse({"success": False, "error": "Thiếu locationId"}, status=400)
            
        db = get_mongo_db("TravelDB")
        
        # Check if used in trips
        if location_name:
            day_details = list(db["DayDetails"].find({"dayActs.name": {"$regex": location_name, "$options": "i"}}))
            if len(day_details) > 0:
                return JsonResponse({
                    "success": False, 
                    "error": f"Không thể xóa. Địa điểm/Phương tiện này đang được sử dụng trong {len(set([str(d['tripId']) for d in day_details]))} chuyến đi."
                }, status=400)
                
        # Delete from MongoDB
        delete_result = db["Locations"].delete_one({"locationId": location_id})
        if delete_result.deleted_count == 0:
            return JsonResponse({"success": False, "error": "Không tìm thấy địa điểm/phương tiện này."}, status=404)
            
        # Delete from Neo4j
        from neo4j import GraphDatabase
        import os
        uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
        
        try:
            driver = GraphDatabase.driver(uri, auth=(user, pwd))
            with driver.session() as session:
                session.run("MATCH (l:Location {locationId: $loc_id}) DETACH DELETE l", loc_id=location_id)
        except Exception as e:
            logger.warning(f"Failed to delete from Neo4j for location {location_id}: {e}")
            
        return JsonResponse({"success": True, "message": "Đã xóa thành công!"})
        
    except Exception as exc:
        logger.error(f"Error deleting location: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)
