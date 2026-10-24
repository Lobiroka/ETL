"""Exemplo MongoDB. Execute pela raiz com `python -m exemplos.teste_mongo`."""

from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.config import MONGODB_URI, require_config


uri = require_config("MONGODB_URI", MONGODB_URI)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

db = client["sample_mflix"]

collection = db["movies"]

print(collection.find_one())
