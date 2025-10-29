"""
SQLAlchemy models for Job and Shipment entities.
Defines the database schema and relationships for logistics optimization jobs
and their associated shipments.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Job(Base):
    """
    SQLAlchemy model for a logistics optimization job.
    Each job can contain multiple shipments to be optimized.
    """
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Use onupdate for fields that should update on any change to the row
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Defines the one-to-many relationship from Job -> Shipment
    # 'back_populates' creates the bi-directional link.
    shipments = relationship("Shipment", back_populates="job")

class Shipment(Base):
    """
    SQLAlchemy model for an individual shipment.
    Each shipment belongs to exactly one job.
    """
    __tablename__ = "shipments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # The foreign key linking this shipment to its parent job
    job_id = Column(Integer, ForeignKey("jobs.id"))
    
    origin = Column(String, index=True)
    destination = Column(String, index=True)
    weight = Column(Float)
    
    # Defines the many-to-one relationship from Shipment -> Job
    job = relationship("Job", back_populates="shipments")