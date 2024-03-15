# model.py

from pydantic import BaseModel
from typing import Optional 

# User Model
class User(BaseModel):
    username: str
    password: str
    
class Asset(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: str
    location: str
    purchase_date: str
    initial_cost: float
    operational_status: bool

class PerformanceMetrics(BaseModel):
    asset_id: str
    metrics_id: Optional[str] = None  # Making metrics_id optional
    uptime: float
    downtime: float
    maintenance_costs: float
    failure_rate: float
    efficiency: float
