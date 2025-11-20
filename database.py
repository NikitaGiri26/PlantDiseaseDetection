# database.py

import os
import bcrypt
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")  # Store this in .env file
client = MongoClient(MONGO_URI)
db = client["plant_disease_db"]
users_collection = db["users"]
admin_collection = db["admins"]
prediction_logs = db["prediction_logs"]
supplements_collection = db["supplements"]
carts_collection = db["carts"]
orders_collection = db["orders"]

# Register Users
def register_user(username, password):
    if users_collection.find_one({"username": username}):
        return "Username already exists."

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({"username": username, "password": hashed_password.decode('utf-8')})
    return "Registration successful!"

# Login Users
def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        return True
    return False

# Register Admin (One-Time Setup)
def register_admin(admin_username, admin_password):
    if admin_collection.find_one({"username": admin_username}):
        return "Admin already exists."

    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
    admin_collection.insert_one({"username": admin_username, "password": hashed_password.decode('utf-8')})
    return "Admin registration successful!"

# Admin Login
def login_admin(admin_username, admin_password):
    admin = admin_collection.find_one({"username": admin_username})
    if admin and bcrypt.checkpw(admin_password.encode('utf-8'), admin["password"].encode('utf-8')):
        return True
    return False

# Save Prediction Logs
def save_prediction(username, image_name, disease_name):
    prediction_logs.insert_one({
        "username": username,
        "image_name": image_name,
        "disease_name": disease_name,
        "timestamp": datetime.now()
    })

# Add Supplement with Image
def add_supplement(name, description, price, image_url):
    if supplements_collection.find_one({"name": name}):
        return "Supplement already exists."
    supplements_collection.insert_one({
        "name": name,
        "description": description,
        "price": price,
        "image_url": image_url
    })
    return "Supplement added successfully!"

# Get All Supplements
def get_all_supplements():
    return list(supplements_collection.find({}, {"_id": 0}))

# Delete Supplement
def delete_supplement(name):
    result = supplements_collection.delete_one({"name": name})
    if result.deleted_count > 0:
        return f"Supplement '{name}' deleted successfully."
    return f"Supplement '{name}' not found."

# Add to Cart
def add_to_cart(username, supplement_name, quantity):
    supplement = supplements_collection.find_one({"name": supplement_name})
    if not supplement:
        return "Supplement not found."
    
    cart_item = carts_collection.find_one({"username": username, "supplement_name": supplement_name})
    if cart_item:
        carts_collection.update_one({"_id": cart_item["_id"]}, {"$inc": {"quantity": quantity}})
    else:
        carts_collection.insert_one({
            "username": username,
            "supplement_name": supplement_name,
            "quantity": quantity,
            "price": supplement["price"]
        })
    return "Item added to cart!"

# View Cart
def view_cart(username):
    return list(carts_collection.find({"username": username}, {"_id": 0}))

# Place Order
def place_order(username):
    cart_items = view_cart(username)
    if not cart_items:
        return "Cart is empty."

    order = {
        "username": username,
        "items": [
            {
                "supplement_name": item["supplement_name"],
                "quantity": item["quantity"],
                "price": item["price"]
            }
            for item in cart_items
        ],
        "total_price": sum(item['price'] * item['quantity'] for item in cart_items),
        "order_date": datetime.now()
    }
    orders_collection.insert_one(order)
    carts_collection.delete_many({"username": username})
    return "Order placed successfully!"

# Get All Orders
def get_all_orders():
    return list(orders_collection.find({}, {"_id": 0}))


def get_user_orders(username):
    return list(orders_collection.find({"username": username}, {"_id": 0}))
