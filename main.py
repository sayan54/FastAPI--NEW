#**THE PASSWORD AND USERNAME FOR AUTHENTICATION IS BOTH "admin"**

# main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from model import Asset, PerformanceMetrics,User
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List
app = FastAPI()

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
database = client.asset_performance
assets_collection = database.asset
metrics_collection = database.metrics

# Authentication Function
def authenticate_user(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    user = authenticate(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

def authenticate(username: str, password: str):
    # This is a simple authentication function.
    # For demonstration purposes, let's assume there is only one user.
    if username == "admin" and password == "admin":#PASSWORD AND USERNAME FOR AUTHENTICATION IS "admin"
        return User(username=username, password=password)  # Include password here

# Authenticator Dependency
def get_current_user(credentials: User = Depends(authenticate_user)):
    return credentials

from database import (
    fetch_one_asset,
    fetch_one_metrics,
)


# Function to fetch all performance metrics
async def fetch_all_metrics():
    metrics_list = []
    cursor = metrics_collection.find({})
    for document in cursor:
        metrics_list.append(PerformanceMetrics(**document))
    return metrics_list

# Function to calculate average downtime
def calculate_average_downtime(metrics_list: List[PerformanceMetrics]) -> float:
    total_downtime = sum(metrics.downtime for metrics in metrics_list)
    return total_downtime / len(metrics_list) if metrics_list else 0.0

# Function to calculate total maintenance costs
def calculate_total_maintenance_costs(metrics_list: List[PerformanceMetrics]) -> float:
    total_costs = sum(metrics.maintenance_costs for metrics in metrics_list)
    return total_costs

# Function to identify assets with high failure rates
def identify_assets_with_high_failure_rates(metrics_list: List[PerformanceMetrics], threshold: float = 0.1) -> List[str]:
    high_failure_assets = [metrics.asset_id for metrics in metrics_list if metrics.failure_rate > threshold]
    return high_failure_assets

# Endpoints...
# CRUD operations for assets
@app.post("/assets/", dependencies=[Depends(get_current_user)])
async def create_asset(asset: Asset, user: User = Depends(authenticate_user)):
    asset_dict = asset.dict()
    inserted_asset = assets_collection.insert_one(asset_dict)
    return {"asset_id": str(inserted_asset.inserted_id)}

@app.get("/api/assets/{asset_id}", response_model=Asset, dependencies=[Depends(get_current_user)])
async def get_todo_by_asset(asset_id, user: User = Depends(authenticate_user)):
    response = await fetch_one_asset(asset_id)
    if response:
        return response
    raise HTTPException(404, f"There is no todo with the title {asset_id}")

@app.put("/assets/{asset_id}" ,dependencies=[Depends(get_current_user)])
async def update_asset(asset_id: str, asset: Asset, user: User = Depends(authenticate_user)):
    updated_asset = assets_collection.update_one({"asset_id": asset_id}, {"$set": asset.dict()})
    if updated_asset.modified_count == 1:
        return {"message": "Asset updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Asset not found")

@app.delete("/assets/{asset_id}", dependencies=[Depends(get_current_user)])
async def delete_asset(asset_id: str, user: User = Depends(authenticate_user)):
    deleted_asset = assets_collection.delete_one({"asset_id": asset_id})
    if deleted_asset.deleted_count == 1:
        return {"message": "Asset deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Asset not found")

# CRUD operations for performance metrics
@app.post("/metrics/",dependencies=[Depends(get_current_user)])
async def create_metrics(metrics: PerformanceMetrics,user: User = Depends(authenticate_user)):
    metrics_dict = metrics.dict()
    inserted_metrics = metrics_collection.insert_one(metrics_dict)
    return {"metrics_id": str(inserted_metrics.inserted_id)}

@app.get("/api/metrics/{asset_id}", response_model=PerformanceMetrics,dependencies=[Depends(get_current_user)])
async def get_metrics_by_metrics(asset_id,user: User = Depends(authenticate_user)):
    response = await fetch_one_metrics(asset_id)
    if response:
        return response
    raise HTTPException(404, f"There is no todo with the title {asset_id}")
    
@app.put("/metrics/{asset_id}",dependencies=[Depends(get_current_user)])
async def update_metrics(asset_id: str, metrics: PerformanceMetrics,user: User = Depends(authenticate_user)):
    metrics_dict = metrics.dict()
    updated_metrics = metrics_collection.update_one(
        {"asset_id": asset_id},
        {"$set": metrics_dict}
    )
    if updated_metrics.modified_count == 1:
        return {"message": "Metrics updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Metrics not found")

@app.delete("/metrics/{asset_id}",dependencies=[Depends(get_current_user)])
async def delete_metrics(asset_id: str ,user: User = Depends(authenticate_user)):
    # Check if metrics for the asset exist
    existing_metrics = metrics_collection.find_one({"asset_id": asset_id})
    if existing_metrics:
        # Delete the metrics document
        deleted_metrics = metrics_collection.delete_one({"asset_id": asset_id})
        if deleted_metrics.deleted_count == 1:
            return {"message": "Metrics deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete metrics")
    else:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
@app.get("/average-downtime", dependencies=[Depends(get_current_user)])
async def get_average_downtime(user: User = Depends(authenticate_user)):
    metrics_list = await fetch_all_metrics()
    average_downtime = calculate_average_downtime(metrics_list)
    return {"average_downtime": average_downtime}

@app.get("/total-maintenance-costs", dependencies=[Depends(get_current_user)])
async def get_total_maintenance_costs(user: User = Depends(authenticate_user)):
    metrics_list = await fetch_all_metrics()
    total_maintenance_costs = calculate_total_maintenance_costs(metrics_list)
    return {"total_maintenance_costs": total_maintenance_costs}

@app.get("/high-failure-assets", dependencies=[Depends(get_current_user)])
async def get_high_failure_assets(user: User = Depends(authenticate_user)):
    metrics_list = await fetch_all_metrics()
    high_failure_assets = identify_assets_with_high_failure_rates(metrics_list)
    return {"high_failure_assets": high_failure_assets}