from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "smart_internship_portal"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("--- Data in 'students' collection ---")
print(list(db.students.find()))

print("\n--- Data in 'students_collection' collection ---")
print(list(db.students_collection.find()))

print("\n--- Data in 'internships' collection ---")
print(list(db.internships.find()))
