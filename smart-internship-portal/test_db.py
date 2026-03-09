from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "smart_internship_portal"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.server_info() # force connection
    print("MongoDB connection successful!")
    db = client[DB_NAME]
    print(f"Collections in {DB_NAME}: {db.list_collection_names()}")
    
    students = list(db.students.find())
    print(f"Number of students: {len(students)}")
    for s in students:
        print(f" - {s.get('email')}: {s.get('name')}")
        
except Exception as e:
    print(f"MongoDB connection failed: {e}")
