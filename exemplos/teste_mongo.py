from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.config import MONGODB_URI, require_config


uri = require_config("MONGODB_URI", MONGODB_URI)


client = MongoClient(uri, server_api=ServerApi("1"))








db = client["sample_mflix"]

collection = db["movies"]

print(collection.find_one())
