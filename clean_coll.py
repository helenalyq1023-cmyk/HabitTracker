import pymongo, os, json
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["Habit_tracker"]

# Ensure collections exist only if they do not already exist
existing_collections = db.list_collection_names()
if "users" not in existing_collections:
    db.create_collection("users")
if "tasks" not in existing_collections:
    db.create_collection("tasks")
if "user_tasks" not in existing_collections:
    db.create_collection("user_tasks")
if "entertainment" not in existing_collections:
    db.create_collection("entertainment")
if "completed_tasks" not in existing_collections:
    db.create_collection("completed_tasks")
if "user_entertainment" not in existing_collections:
    db.create_collection("user_entertainment")

# Get the collections
users_collection = db["users"]
tasks_collection = db["tasks"]
user_tasks_collection = db["user_tasks"]
entertainment_collection = db["entertainment"]
completed_coll = db["completed_tasks"]
user_entertainment_collection = db["user_entertainment"]
#db.create_collection("score")

user_tasks_collection.delete_many({})
completed_coll.delete_many({})
user_entertainment_collection.delete_many({})
entertainment_collection.delete_many({})

scr = db["score"]
scr.delete_many({})

scr_path = os.path.join(os.path.dirname(__file__), "scores.json")
with open(scr_path, "r") as file:
    scr_data = json.load(file)

if scr.count_documents({}) == 0:
    scr.insert_many(scr_data)

tasks_json_path = os.path.join(os.path.dirname(__file__), "tasks.json")
with open(tasks_json_path, "r") as file:
    tasks_data = json.load(file)

# Write records into the tasks collection (replace all with new if you want a fresh start)
#tasks_collection.delete_many({})  # Optional: clear existing records
if tasks_collection.count_documents({}) == 0:
    tasks_collection.insert_many(tasks_data)

ent_path = os.path.join(os.path.dirname(__file__), "entertain.json")
with open(ent_path, "r") as file:
    ent_data = json.load(file)

if entertainment_collection.count_documents({}) == 0:
    entertainment_collection.insert_many(ent_data)