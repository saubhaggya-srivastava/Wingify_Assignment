"""
Database models and configuration for Financial Document Analyzer
"""
import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/financial_analyzer")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AnalysisResult(Base):
    """Store financial document analysis results"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)  # Celery job ID
    filename = Column(String, nullable=False)
    file_size_mb = Column(Float)
    query = Column(Text)
    
    # Analysis results
    status = Column(String, default="pending")  # pending, processing, completed, failed
    summary = Column(Text)
    detailed_result = Column(Text)
    agents_used = Column(JSON)  # List of agents that processed the document
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    processing_time_seconds = Column(Float)
    
    # Error handling
    error_message = Column(Text)
    
class User(Base):
    """Store user information and session data"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    
    # Usage statistics
    total_analyses = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)

class AnalysisCache(Base):
    """Cache analysis results for identical documents"""
    __tablename__ = "analysis_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String, unique=True, index=True)  # SHA256 hash of file content
    filename = Column(String)
    query_hash = Column(String, index=True)  # Hash of query for cache key
    
    # Cached results
    analysis_result = Column(Text)
    agents_used = Column(JSON)
    
    # Cache metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=1)
    last_accessed = Column(DateTime, default=datetime.utcnow)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()