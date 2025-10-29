"""
Main application file for the LogiOpt backend API.
Defines FastAPI app, startup events, and API endpoints for managing jobs and shipments.
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# NEW: Import the CORS middleware
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas, optimization
from .database import create_db_and_tables, get_db

app = FastAPI(
    title="LogiOpt API",
    description="API for managing logistics optimization jobs and shipments.",
    version="1.0.0"
)

# --- NEW: CORS Configuration ---

# Define the list of origins that are allowed to make requests.
# For development, this is just our Vite frontend.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)
# --- End of CORS Configuration ---


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
    return crud.create_job(db=db, job=job)

@app.get("/jobs/", response_model=List[schemas.Job], tags=["Jobs"])
def read_jobs_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db, skip=skip, limit=limit)
    return jobs

@app.get("/jobs/{job_id}", response_model=schemas.Job, tags=["Jobs"])
def read_job_endpoint(job_id: int, db: Session = Depends(get_db)):
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
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return crud.create_shipment_for_job(db=db, shipment=shipment, job_id=job_id)

#==============================================================================
# Optimization Endpoint
#==============================================================================

@app.post("/jobs/{job_id}/solve", response_model=schemas.Solution, tags=["Optimization"])
def solve_job_endpoint(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if not db_job.shipments:
        raise HTTPException(status_code=400, detail="Job has no shipments to optimize")

    solution = optimization.solve_vrp(db_job)

    if not solution:
        raise HTTPException(status_code=500, detail="Optimization failed to find a solution")

    crud.update_job_status(db, job_id=job_id, status="completed")
    return solution