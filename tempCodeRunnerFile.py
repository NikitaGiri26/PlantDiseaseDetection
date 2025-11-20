import os
import bcrypt
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")  # Store this in .env file
client = MongoClient(MONGO_URI)
db = client["plant_disease_db"]
users_collection = db["users"]

# Function to register a new user
def register_user(username, password):
    if users_collection.find_one({"username": username}):
        return "Username already exists."
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({"username": username, "password": hashed_password.decode('utf-8')})
    return "Registration successful!"

# Function to check login
def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        return True
    return False
