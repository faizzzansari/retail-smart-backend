from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["retailsmart"]

products_collection = db["products"]
sales_collection = db["sales"]