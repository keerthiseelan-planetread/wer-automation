from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017/wer_automation"

client = MongoClient(MONGO_URL)

db = client["wer"]

# ✅ THIS IS IMPORTANT
report_collection = db["reports"]