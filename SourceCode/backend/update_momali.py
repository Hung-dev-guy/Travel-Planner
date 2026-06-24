from pymongo import MongoClient

def update_momali():
    db = MongoClient("mongodb://localhost:27017/")["TravelDB"]
    url = "https://lh3.googleusercontent.com/gps-cs-s/APNQkAEcAQrv26V9di_lejCNZX_lNxmK0SDGfVKGyL9Henr5PW9GM6gPz9iOI-_sFgSLccj6IU_qVUDBu-byFutTUHGYMGoCqta0iR9shnXheuE6_E_UQbWRSJ6uQOcLtc9pUXVX4-w=w324-h312-n-k-no"
    res = db.Locations.update_many({"name": {"$regex": "Momali", "$options": "i"}}, {"$set": {"img_url": url, "image_url": url, "image": url}})
    print(f"Matched: {res.matched_count}, Modified: {res.modified_count}")

if __name__ == "__main__":
    update_momali()
