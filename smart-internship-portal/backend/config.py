import os
from pymongo import MongoClient

# Load environment variables or use defaults
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "smart_internship_portal")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Securty settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-for-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Export collections for easy import elsewhere
students_collection = db["students"]
internships_collection = db["internships"]
applications_collection = db["applications"]
