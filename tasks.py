"""
Background tasks for financial document analysis using Celery
"""
import os
import hashlib
from datetime import datetime
from typing import Dict, Any
from celery import current_task
from sqlalchemy.orm import Session

from celery_app import celery_app
from database import SessionLocal, AnalysisResult, AnalysisCache
from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document, investment_analysis, risk_assessment, verification

def get_file_hash(file_path: str) -> str:
    """Generate SHA256 hash of file content for caching"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def get_query_hash(query: str) -> str:
    """Generate hash of query for cache key"""
    return hashlib.sha256(query.encode()).hexdigest()

@celery_app.task(bind=True)
def analyze_financial_document_task(self, file_path: str, query: str, filename: str, file_size_mb: float) -> Dict[str, Any]:
    """
    Background task to analyze financial documents using CrewAI
    
    Args:
        file_path: Path to the uploaded PDF file
        query: User's analysis query
        filename: Original filename
        file_size_mb: File size in MB
        
    Returns:
        Dict containing analysis results
    """
    # Try to create database session, but continue without it if it fails
    db = None
    try:
        db = SessionLocal()
    except Exception as e:
        print(f"Database connection failed, continuing without database: {e}")
        db = None
    
    job_id = self.request.id
    start_time = datetime.utcnow()
    
    try:
        # Update task status to processing
        current_task.update_state(
            state="PROCESSING",
            meta={"status": "Starting financial analysis...", "progress": 0}
        )
        
        # Create or update database record (if database is available)
        analysis_record = None
        if db:
            try:
                analysis_record = db.query(AnalysisResult).filter(AnalysisResult.job_id == job_id).first()
                if not analysis_record:
                    analysis_record = AnalysisResult(
                        job_id=job_id,
                        filename=filename,
                        file_size_mb=file_size_mb,
                        query=query,
                        status="processing"
                    )
                    db.add(analysis_record)
                    db.commit()
            except Exception as e:
                print(f"Database record creation failed: {e}")
                analysis_record = None
        
        # Check cache first (if database is available)
        cached_result = None
        if db:
            try:
                file_hash = get_file_hash(file_path)
                query_hash = get_query_hash(query)
                
                current_task.update_state(
                    state="PROCESSING",
                    meta={"status": "Checking cache...", "progress": 10}
                )
                
                cached_result = db.query(AnalysisCache).filter(
                    AnalysisCache.file_hash == file_hash,
                    AnalysisCache.query_hash == query_hash
                ).first()
                
                if cached_result:
                    # Return cached result
                    current_task.update_state(
                        state="PROCESSING",
                        meta={"status": "Found cached result, returning...", "progress": 100}
                    )
                    
                    # Update cache access
                    cached_result.access_count += 1
                    cached_result.last_accessed = datetime.utcnow()
                    
                    # Update analysis record
                    if analysis_record:
                        analysis_record.status = "completed"
                        analysis_record.detailed_result = cached_result.analysis_result
                        analysis_record.agents_used = cached_result.agents_used
                        analysis_record.completed_at = datetime.utcnow()
                        analysis_record.processing_time_seconds = 0.1  # Cached result
                    
                    db.commit()
                    
                    return {
                        "status": "success",
                        "message": "Analysis completed (from cache)",
                        "cached": True,
                        "result": cached_result.analysis_result,
                        "agents_used": cached_result.agents_used
                    }
            except Exception as e:
                print(f"Cache check failed: {e}")
                cached_result = None
        
        # Run CrewAI analysis
        current_task.update_state(
            state="PROCESSING",
            meta={"status": "Running AI analysis...", "progress": 20}
        )
        
        # Create the financial analysis crew
        financial_crew = Crew(
            agents=[
                verifier,           # First: Verify document quality
                financial_analyst,  # Second: Analyze financial data
                investment_advisor, # Third: Provide investment insights
                risk_assessor      # Fourth: Assess risks
            ],
            tasks=[
                verification,              # Task 1: Verify document
                analyze_financial_document, # Task 2: Analyze financials
                investment_analysis,       # Task 3: Investment recommendations
                risk_assessment           # Task 4: Risk analysis
            ],
            process=Process.sequential,
            verbose=True
        )
        
        current_task.update_state(
            state="PROCESSING",
            meta={"status": "AI agents processing document...", "progress": 50}
        )
        
        # Execute the crew
        result = financial_crew.kickoff({
            'query': query,
            'file_path': file_path
        })
        
        current_task.update_state(
            state="PROCESSING",
            meta={"status": "Finalizing results...", "progress": 90}
        )
        
        # Process results
        analysis_result = str(result)
        agents_used = [
            "Document Verifier - Validated document authenticity",
            "Financial Analyst - Analyzed financial metrics and trends", 
            "Investment Advisor - Provided investment recommendations",
            "Risk Assessor - Conducted comprehensive risk analysis"
        ]
        
        # Cache the result and update database (if available)
        if db:
            try:
                if 'file_hash' in locals() and 'query_hash' in locals():
                    cache_entry = AnalysisCache(
                        file_hash=file_hash,
                        filename=filename,
                        query_hash=query_hash,
                        analysis_result=analysis_result,
                        agents_used=agents_used
                    )
                    db.add(cache_entry)
                
                # Update analysis record
                if analysis_record:
                    end_time = datetime.utcnow()
                    processing_time = (end_time - start_time).total_seconds()
                    
                    analysis_record.status = "completed"
                    analysis_record.detailed_result = analysis_result
                    analysis_record.agents_used = agents_used
                    analysis_record.completed_at = end_time
                    analysis_record.processing_time_seconds = processing_time
                
                db.commit()
            except Exception as e:
                print(f"Database save failed: {e}")
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        current_task.update_state(
            state="SUCCESS",
            meta={"status": "Analysis completed successfully!", "progress": 100}
        )
        
        return {
            "status": "success",
            "message": "Financial document analysis completed successfully",
            "cached": False,
            "result": analysis_result,
            "agents_used": agents_used,
            "processing_time": processing_time
        }
        
    except Exception as e:
        # Handle errors
        error_message = f"Error processing financial document: {str(e)}"
        
        # Update database record (if available)
        if db and analysis_record:
            try:
                analysis_record.status = "failed"
                analysis_record.error_message = error_message
                analysis_record.completed_at = datetime.utcnow()
                db.commit()
            except Exception as db_error:
                print(f"Database error update failed: {db_error}")
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": f"Analysis failed: {error_message}", "progress": 0}
        )
        
        raise Exception(error_message)
        
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up temporary file: {file_path}")
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up file {file_path}: {cleanup_error}")
        
        # Close database session (if available)
        if db:
            try:
                db.close()
            except Exception as e:
                print(f"Database close error: {e}")

@celery_app.task
def cleanup_old_cache_entries():
    """Periodic task to clean up old cache entries"""
    db: Session = SessionLocal()
    try:
        # Delete cache entries older than 30 days with low access count
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_entries = db.query(AnalysisCache).filter(
            AnalysisCache.created_at < cutoff_date,
            AnalysisCache.access_count < 5
        ).all()
        
        for entry in old_entries:
            db.delete(entry)
        
        db.commit()
        return f"Cleaned up {len(old_entries)} old cache entries"
        
    finally:
        db.close()