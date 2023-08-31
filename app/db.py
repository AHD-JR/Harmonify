from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get("MONGODB_URL")

client = MongoClient(DB_URL)
db = client['store']

