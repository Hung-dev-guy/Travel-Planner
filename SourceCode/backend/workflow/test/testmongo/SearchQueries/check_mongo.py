import os, sys
from dotenv import load_dotenv
sys.path.append('.')
load_dotenv()
from workflow.db import get_mongo_db

db = get_mongo_db("TravelDB")
print("Trips count:", db["Trips"].count_documents({}))
print("DayDetails count:", db["DayDetails"].count_documents({}))
