import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "../../../.."))

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from workflow.nodes.Planner import fetch_locations_from_mongo

ward_names = ["Tây Hoa Lư", "Hạ Long"]
result = fetch_locations_from_mongo(ward_names)
print(result)