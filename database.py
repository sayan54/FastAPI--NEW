# import motor.motor_asyncio
from model import Asset 
from model import PerformanceMetrics# Assuming Todo is defined in a separate model file
from pymongo import MongoClient
# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
database = client.asset_performance
assets_collection = database.asset
metrics_collection = database.metrics

async def fetch_one_asset(asset_id):
    document =  assets_collection.find_one({"asset_id": asset_id})
    return document
async def fetch_one_metrics(asset_id):
    document =  metrics_collection.find_one({"asset_id": asset_id})
    return document

