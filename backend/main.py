from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Import all the components we've built
from . import crud, models, schemas
from .database import create_db_and_tables, get_db

app = FastAPI(
    title="LogiOpt API",
    description="API for managing logistics optimization jobs and shipments.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    """
    Event handler for application startup.
    Creates database tables if they don't exist.
    """
    create_db_and_tables()

#==============================================================================
# Job Endpoints
#==============================================================================

@app.post("/jobs/", response_model=schemas.Job, tags=["Jobs"])
def create_job_endpoint(job: schemas.JobCreate, db: Session = Depends(get_db)):
    """
    Create a new job.
    - `job`: The request body, validated against the JobCreate schema.
    - `db`: The database session, injected by the get_db dependency.
    - `response_model`: Filters the output to match the Job schema.
    """
    return crud.create_job(db=db, job=job)

@app.get("/jobs/", response_model=List[schemas.Job], tags=["Jobs"])
def read_jobs_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all jobs (paginated).
    """
    jobs = crud.get_jobs(db, skip=skip, limit=limit)
    return jobs

@app.get("/jobs/{job_id}", response_model=schemas.Job, tags=["Jobs"])
def read_job_endpoint(job_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single job by its ID.
    """
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

#==============================================================================
# Shipment Endpoint
#==============================================================================

@app.post("/jobs/{job_id}/shipments/", response_model=schemas.Shipment, tags=["Shipments"])
def create_shipment_for_job_endpoint(
    job_id: int, shipment: schemas.ShipmentCreate, db: Session = Depends(get_db)
):
    """
    Create a new shipment for a specific job.
    Validates that the parent job exists before creation.
    """
    # First, verify the parent job exists
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # If it exists, create the shipment
    return crud.create_shipment_for_job(db=db, shipment=shipment, job_id=job_id)