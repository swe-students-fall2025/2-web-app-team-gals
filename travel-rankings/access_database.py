from pymongo import MongoClient, DESCENDING, ASCENDING
from dotenv import load_dotenv
from bson import ObjectId
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

try:
    client = MongoClient(MONGO_URI)
    client.admin.command("ping")
    print("connected to MongoDB")
except Exception as e:
    print("MongoDB connection failed:", e)

db = client[DB_NAME]
users = db["users"]
experiences = db["experiences"]
bucketlist = db["bucketlist"]
friend_experiences = db["friend_experiences"]

docs_list = list(friend_experiences.find())
print(docs_list)

# result = friend_experiences.delete_one({'_id': ObjectId('68f3d854d0b345c19fa060b6')})

# print("Deleted" if result.deleted_count > 0 else "Not found")
docs_list = list(friend_experiences.find())
friend_experiences.update_one(
    {'_id': ObjectId('68f65cc8582ddf48e2f2b8ca')},  # filter
    {'$set': {'picture': 'outhouse_orchards.jpeg'}}    # update
)

docs_list = list(friend_experiences.find())
print(docs_list)
