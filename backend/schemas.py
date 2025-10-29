from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

#==============================================================================
# Shipment Schemas
#==============================================================================

class ShipmentBase(BaseModel):
    """
    Base Pydantic schema for a Shipment.
    Contains all common fields required for creation and read.
    """
    origin: str
    destination: str
    weight: float

class ShipmentCreate(ShipmentBase):
    """
    Schema for creating a new Shipment.
    Inherits all fields from ShipmentBase.
    """
    pass

class Shipment(ShipmentBase):
    """
    Schema for reading a Shipment from the API.
    Includes database-generated fields like id and job_id.
    """
    id: int
    job_id: int

    class Config:
        # Enables ORM (Object-Relational Mapping) mode.
        # Tells Pydantic to read data from SQLAlchemy model attributes.
        from_attributes = True

#==============================================================================
# Job Schemas
#==============================================================================

class JobBase(BaseModel):
    """
    Base Pydantic schema for a Job.
    """
    status: Optional[str] = "pending"

class JobCreate(JobBase):
    """
    Schema for creating a new Job.
    """
    pass

class Job(JobBase):
    """
    Schema for reading a Job from the API.
    Includes database-generated fields and a nested list of shipments.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    # This automatically nests the related Shipment objects
    # using the 'Shipment' read schema.
    shipments: List[Shipment] = []

    class Config:
        from_attributes = True


#==============================================================================
# Solution Schemas
#==============================================================================

class SolutionStop(BaseModel):
    """
    Represents a single stop in the solved route.
    """
    id: int         # The ID of the shipment
    location: str   # The 'origin' or 'destination'
    type: str       # 'PICKUP' or 'DROP'
    
class SolutionRoute(BaseModel):
    """
    Represents the complete route for a single vehicle.
    """
    stops: List[SolutionStop] = []

class Solution(BaseModel):
    """
    The final solution response, containing all routes.
    For our simple VRP, we'll only have one route.
    """
    routes: List[SolutionRoute] = []