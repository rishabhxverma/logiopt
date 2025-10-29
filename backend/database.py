"""
Database setup and session management using SQLAlchemy.
This module defines the database connection, session factory,
and base class for models.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the database connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is the central source of database connectivity.
# It manages a pool of connections.
engine = create_engine(DATABASE_URL)

# SessionLocal is a "factory" for creating new database sessions.
# Each session will be a short-lived "conversation" with the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is a declarative base class that our models will inherit from.
# SQLAlchemy uses this to map our models (like Job, Shipment) to database tables.
Base = declarative_base()

def create_db_and_tables():
    """
    Creates all database tables defined by models that inherit from Base.
    This function is called once on application startup.
    """
    Base.metadata.create_all(bind=engine)

# ... (all your existing code: DATABASE_URL, engine, SessionLocal, Base, create_db_and_tables) ...

def get_db():
    """
    A dependency function to get a database session per request.
    Ensures the session is always closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()