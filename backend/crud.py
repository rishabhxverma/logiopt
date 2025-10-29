from sqlalchemy.orm import Session
from . import models, schemas

# --- READ Operations ---

def get_job(db: Session, job_id: int):
    # .query(models.Job): Start a query on the 'jobs' table.
    # .filter(models.Job.id == job_id): Find the one where the 'id' column matches our job_id.
    # .first(): Get the first result (or None if not found).
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    # .offset(skip): Skip the first 'skip' results.
    # .limit(limit): Only return a maximum of 'limit' results.
    # .all(): Get all results that match.
    # This is how you do "pagination" (e.g., "show me page 2 of the results").
    return db.query(models.Job).offset(skip).limit(limit).all()

# --- CREATE Operations ---

def create_job(db: Session, job: schemas.JobCreate):
    # 1. Convert the Pydantic schema (schemas.JobCreate) into a dictionary.
    #    **job.dict() is a cool Python trick to "unpack" the dictionary as keyword arguments.
    #    So, if job.dict() is {'status': 'pending'}, this becomes:
    #    db_job = models.Job(status='pending')
    db_job = models.Job(**job.dict())
    
    # 2. Add the new, in-memory 'db_job' object to the database session.
    db.add(db_job)
    
    # 3. Commit the "transaction." This is what actually saves it to the database.
    db.commit()
    
    # 4. Refresh the 'db_job' object. This pulls the new data from the DB,
    #    like the auto-generated 'id' and 'created_at' timestamp.
    db.refresh(db_job)
    
    # 5. Return the newly created job.
    return db_job

def create_shipment_for_job(db: Session, shipment: schemas.ShipmentCreate, job_id: int):
    # Same pattern as create_job, but we also pass in the 'job_id'
    db_shipment = models.Shipment(**shipment.dict(), job_id=job_id)
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment