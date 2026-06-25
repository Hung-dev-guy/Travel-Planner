import sys
import os
sys.path.append(os.getcwd())
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from chatbot.db import get_travel_db

db = get_travel_db()
print("Distinct categories in Locations:")
print(db["Locations"].distinct("category"))

print("\nSample locations in Hạ Long:")
for loc in db["Locations"].find({"address": {"$regex": "Hạ Long", "$options": "i"}}).limit(3):
    print(loc["name"], loc["category"])
