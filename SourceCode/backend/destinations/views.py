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
        loc_col = db["Locations"]
        trans_col = db["Transportations"]
        
        # Get query params
        category = request.GET.get('category', 'All')
        search_q = request.GET.get('q', '').strip()
        
        query = {}
        trans_query = {}
        
        fetch_locs = True
        fetch_trans = True
        
        # Map frontend filters to DB categories
        if category != 'All':
            if category == 'Transport':
                fetch_locs = False
            else:
                fetch_trans = False
                cat_map = {
                    'Hotels': 'Stay',
                    'Activities': 'Activity',
                    'Stay': 'Stay',
                    'Activity': 'Activity',
                    'Food': 'Food'
                }
                db_cat = cat_map.get(category, category)
                query["category"] = db_cat
            
        if search_q:
            query["name"] = {"$regex": search_q, "$options": "i"}
            trans_query["name"] = {"$regex": search_q, "$options": "i"}
            
        locations = []
        if fetch_locs:
            locations.extend(list(loc_col.find(query).sort("_id", -1).limit(50)))
            
        if fetch_trans:
            transports = list(trans_col.find(trans_query).sort("_id", -1).limit(50))
            # Normalize transport docs to look like location docs for the frontend
            for t in transports:
                t["locationId"] = t.get("transportId")
                t["category"] = "Transport"
                t["estimatedPrice"] = t.get("price", 0)
                # Map provinces/wards to frontend expected fields
                t["province_name"] = t.get("from_province", "")
                t["ward_name"] = t.get("from_province", "")
                locations.append(t)
        
        # Sort combined results by _id roughly
        try:
            locations.sort(key=lambda x: x.get("_id"), reverse=True)
        except Exception:
            pass
            
        # Map DB docs to frontend expected format
        formatted_results = []
        for loc in locations:
            lat = loc.get("location", {}).get("coordinates", [None, None])[1] if loc.get("location") else None
            lng = loc.get("location", {}).get("coordinates", [None, None])[0] if loc.get("location") else None
            
            formatted_results.append({
                "type": "destination" if loc.get("category") != "Transport" else "transport",
                "id": loc.get("locationId", str(loc["_id"])),
                "name": loc.get("name", "Unknown"),
                "description": loc.get("description", ""),
                "image": loc.get('img_url') or loc.get('image_url') or "",
                "price": loc.get("estimatedPrice", 0),
                "rating": loc.get("rating", 0),
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
            result = session.run("MATCH (p:Province) RETURN DISTINCT p.name AS name ORDER BY p.name")
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
            result = session.run("MATCH (p:Province {name: $province})-[:HAS]->(w:Ward) RETURN DISTINCT w.name AS name ORDER BY w.name", province=province)
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
        open_time = payload.get("openingHours_open", "08:00") or "08:00"
        close_time = payload.get("openingHours_close", "22:00") or "22:00"
        opening_hours = f"{open_time} - {close_time}"

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
            "openingHours": opening_hours
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
        from_province = payload.get("from_province", "").strip()
        to_province = payload.get("to_province", "").strip()
        transport_type = payload.get("transportType", "Coach").strip()
        provider = payload.get("provider", "").strip()
        price = float(payload.get("price", 0))
        estimatedDuration = float(payload.get("estimatedDuration", 1))
        distance_km = float(payload.get("distance_km", 0))
        op_open = payload.get("operatingHours_open", "06:00")
        op_close = payload.get("operatingHours_close", "22:00")
        img_url = payload.get("img_url", "")
        
        if not from_province or not to_province or not transport_type:
            return JsonResponse({"success": False, "error": "Thiếu thông tin bắt buộc (from_province, to_province, transportType)"}, status=400)
            
        from neo4j import GraphDatabase
        import os
        uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
        
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session() as session:
            # Create a CONNECTED_TO relationship in Neo4j (simulating routes between provinces/wards)
            cypher_query = """
            MERGE (w1:Ward {name: $from_ward})
            MERGE (w2:Ward {name: $to_ward})
            MERGE (w1)-[r:CONNECTED_TO]-(w2)
            ON CREATE SET r.distance_km = $distance
            ON MATCH SET r.distance_km = $distance
            """
            session.run(cypher_query, from_ward=from_province, to_ward=to_province, distance=distance_km)
            
        # Save to MongoDB Transportations collection
        try:
            db = get_mongo_db("TravelDB")
            transport_id = f"T-{uuid.uuid4().hex[:6].upper()}"
            
            provider_text = f" ({provider})" if provider else ""
            transport_doc = {
                "transportId": transport_id,
                "transportType": transport_type,
                "name": f"{transport_type} ({from_province} → {to_province}){provider_text}",
                "description": f"Dịch vụ vận chuyển từ {from_province} đến {to_province}. Giờ khởi hành: {op_open}",
                "distance_km": distance_km,
                "price": price,
                "estimatedDuration": estimatedDuration,
                "operatingHours": {
                    "open": op_open,
                    "close": op_close
                },
                "img_url": img_url,
                "createdAt": {"$date": datetime.datetime.utcnow().isoformat() + "Z"},
                "from_province": from_province,
                "to_province": to_province
            }
            db["Transportations"].insert_one(transport_doc)
            
        except Exception as e:
            logger.warning(f"Failed to save transport to MongoDB: {e}")
            
        return JsonResponse({"success": True, "message": "Thêm phương tiện thành công vào Transportations!"})
        
    except Exception as exc:
        logger.error(f"Error adding transport: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)
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
        
        new_avg = 0
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
        for key in ["name", "description", "category", "estimatedPrice", "province_name", "ward_name", "img_url", "rating", "price", "from_province", "to_province", "distance_km", "estimatedDuration"]:
            if key in payload:
                if key in ["estimatedPrice", "rating", "price", "distance_km", "estimatedDuration"]:
                    try: update_data[key] = float(payload[key])
                    except: pass
                else:
                    update_data[key] = payload[key]
                    
        # Support operatingHours updates
        if "operatingHours_open" in payload or "operatingHours_close" in payload:
            update_data["operatingHours"] = {
                "open": payload.get("operatingHours_open", "06:00"),
                "close": payload.get("operatingHours_close", "22:00")
            }
            
        is_transport = location_id.startswith("T-") or location_id.startswith("TRANS_")
        
        # Nếu là Transport, map province_name vào from_province/to_province để dễ dùng lại UI
        if is_transport and "province_name" in update_data:
            update_data["from_province"] = update_data["province_name"]
            update_data["to_province"] = update_data["province_name"] # Default to same or let user specify later
            if "ward_name" in update_data:
                update_data["from_ward"] = update_data["ward_name"]
                update_data["to_ward"] = update_data["ward_name"]
            
            # Map estimatedPrice to price
            if "estimatedPrice" in update_data:
                update_data["price"] = update_data["estimatedPrice"]
                    
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
        col_name = "Transportations" if is_transport else "Locations"
        id_field = "transportId" if is_transport else "locationId"
        
        result = db[col_name].update_one(
            {id_field: location_id},
            {"$set": update_data}
        )
        
        # Cập nhật Neo4j nếu có thay đổi liên quan
        from neo4j import GraphDatabase
        import os
        uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
        
        try:
            if not is_transport:
                # Lấy bản ghi mới nhất từ MongoDB để đồng bộ Neo4j
                updated_doc = db["Locations"].find_one({"locationId": location_id})
                if updated_doc and updated_doc.get("ward_name") and updated_doc.get("province_name"):
                    driver = GraphDatabase.driver(uri, auth=(user, pwd))
                    with driver.session() as session:
                        cypher_query = """
                        MERGE (p:Province {name: $province})
                        MERGE (w:Ward {name: $ward})
                        MERGE (p)-[:HAS]->(w)
                        MERGE (l:Location {locationId: $loc_id})
                        SET l.name = $name, l.category = $category
                        WITH l, w
                        OPTIONAL MATCH (l)-[r:LOCATED_IN]->()
                        DELETE r
                        WITH l, w
                        MERGE (l)-[:LOCATED_IN]->(w)
                        """
                        session.run(
                            cypher_query,
                            loc_id=location_id,
                            name=updated_doc.get("name"),
                            category=updated_doc.get("category", "Activity"),
                            province=updated_doc.get("province_name"),
                            ward=updated_doc.get("ward_name")
                        )
        except Exception as e:
            logger.warning(f"Failed to update Neo4j for {location_id}: {e}")
                
        return JsonResponse({"success": True, "message": "Cập nhật thành công!"})
        
    except Exception as exc:
        logger.error(f"Error editing location/transport: {exc}")
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
                
        is_transport = location_id.startswith("T-") or location_id.startswith("TRANS_")
        col_name = "Transportations" if is_transport else "Locations"
        id_field = "transportId" if is_transport else "locationId"
        
        # Delete from MongoDB
        delete_result = db[col_name].delete_one({id_field: location_id})
        if delete_result.deleted_count == 0:
            return JsonResponse({"success": False, "error": "Không tìm thấy địa điểm/phương tiện này."}, status=404)
            
        # Delete from Neo4j (if applicable)
        from neo4j import GraphDatabase
        import os
        uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        pwd = os.environ.get("NEO4J_PASSWORD", "12345678")
        
        try:
            if not is_transport:
                driver = GraphDatabase.driver(uri, auth=(user, pwd))
                with driver.session() as session:
                    session.run("MATCH (l:Location {locationId: $loc_id}) DETACH DELETE l", loc_id=location_id)
        except Exception as e:
            logger.warning(f"Failed to delete from Neo4j for {location_id}: {e}")
            
        return JsonResponse({"success": True, "message": "Đã xóa thành công!"})
        
    except Exception as exc:
        logger.error(f"Error deleting location/transport: {exc}")
        return JsonResponse({"success": False, "error": str(exc)}, status=500)
