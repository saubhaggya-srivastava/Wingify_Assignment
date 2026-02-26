from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
import hashlib
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

# Celery and Redis imports
from celery.result import AsyncResult
from tasks import analyze_financial_document_task
from database import get_db, create_tables, AnalysisResult, User, AnalysisCache

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial document analysis system using CrewAI with Redis Queue and Database Integration",
    version="2.0.0"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

def get_client_info(request) -> dict:
    """Extract client information for user tracking"""
    return {
        "ip_address": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown")
    }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Financial Document Analyzer API v2.0 is running",
        "version": "2.0.0",
        "status": "healthy",
        "features": {
            "queue_processing": "Redis + Celery",
            "database": "PostgreSQL + SQLAlchemy",
            "caching": "Intelligent result caching",
            "concurrent_requests": "Supported"
        },
        "endpoints": {
            "analyze": "/analyze - POST - Upload and analyze financial documents (async)",
            "status": "/status/{job_id} - GET - Check analysis status",
            "result": "/result/{job_id} - GET - Get analysis results",
            "health": "/health - GET - Detailed health check",
            "stats": "/stats - GET - System statistics"
        }
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check endpoint with database connectivity"""
    try:
        # Test database connection
        total_analyses = db.query(AnalysisResult).count()
        cached_results = db.query(AnalysisCache).count()
        
        return {
            "status": "healthy",
            "service": "Financial Document Analyzer v2.0",
            "features": {
                "agents_available": ["financial_analyst", "verifier", "investment_advisor", "risk_assessor"],
                "supported_formats": ["PDF"],
                "max_file_size": "10MB",
                "queue_processing": "Redis + Celery",
                "database": "PostgreSQL",
                "caching": "Enabled"
            },
            "statistics": {
                "total_analyses": total_analyses,
                "cached_results": cached_results
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": f"Database connection failed: {str(e)}"
            }
        )

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(..., description="Financial document to analyze (PDF format)"),
    query: str = Form(
        default="Provide a comprehensive analysis of this financial document including investment insights and risk assessment",
        description="Specific question or analysis request for the financial document"
    ),
    db: Session = Depends(get_db)
):
    """
    Analyze financial document asynchronously using Redis queue
    
    Returns job_id for status tracking instead of blocking until completion
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported. Please upload a PDF financial document."
        )
    
    # Generate unique file ID and path
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Validate file size (10MB limit)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Validate and clean query
        if not query or query.strip() == "":
            query = "Provide a comprehensive analysis of this financial document including investment insights and risk assessment"
        
        query = query.strip()
        file_size_mb = round(len(file_content) / (1024 * 1024), 2)
        
        # Submit task to Celery queue
        task = analyze_financial_document_task.delay(
            file_path=file_path,
            query=query,
            filename=file.filename,
            file_size_mb=file_size_mb
        )
        
        # Create database record
        analysis_record = AnalysisResult(
            job_id=task.id,
            filename=file.filename,
            file_size_mb=file_size_mb,
            query=query,
            status="queued"
        )
        db.add(analysis_record)
        db.commit()
        
        return {
            "status": "accepted",
            "message": "Financial document analysis queued successfully",
            "job_id": task.id,
            "query": query,
            "file_info": {
                "filename": file.filename,
                "size_mb": file_size_mb,
                "queued_at": datetime.utcnow().isoformat()
            },
            "next_steps": {
                "check_status": f"/status/{task.id}",
                "get_result": f"/result/{task.id}"
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
        
    except Exception as e:
        # Handle unexpected errors
        error_message = f"Error queuing financial document analysis: {str(e)}"
        
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Internal server error",
                "message": "Failed to queue the financial document analysis",
                "details": str(e)
            }
        )

@app.get("/status/{job_id}")
async def get_analysis_status(job_id: str, db: Session = Depends(get_db)):
    """Get the status of a financial analysis job"""
    
    # Check database record
    analysis_record = db.query(AnalysisResult).filter(AnalysisResult.job_id == job_id).first()
    if not analysis_record:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get Celery task status
    task = AsyncResult(job_id)
    
    status_info = {
        "job_id": job_id,
        "status": task.state,
        "filename": analysis_record.filename,
        "query": analysis_record.query,
        "created_at": analysis_record.created_at.isoformat(),
    }
    
    if task.state == "PENDING":
        status_info.update({
            "message": "Analysis is queued and waiting to be processed",
            "progress": 0
        })
    elif task.state == "PROCESSING":
        status_info.update({
            "message": task.info.get("status", "Processing..."),
            "progress": task.info.get("progress", 0)
        })
    elif task.state == "SUCCESS":
        status_info.update({
            "message": "Analysis completed successfully",
            "progress": 100,
            "completed_at": analysis_record.completed_at.isoformat() if analysis_record.completed_at else None,
            "processing_time": analysis_record.processing_time_seconds,
            "result_available": True
        })
    elif task.state == "FAILURE":
        status_info.update({
            "message": "Analysis failed",
            "progress": 0,
            "error": str(task.info) if task.info else analysis_record.error_message,
            "completed_at": analysis_record.completed_at.isoformat() if analysis_record.completed_at else None
        })
    
    return status_info

@app.get("/result/{job_id}")
async def get_analysis_result(job_id: str, db: Session = Depends(get_db)):
    """Get the results of a completed financial analysis"""
    
    # Check database record
    analysis_record = db.query(AnalysisResult).filter(AnalysisResult.job_id == job_id).first()
    if not analysis_record:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if analysis_record.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Analysis not completed yet. Current status: {analysis_record.status}"
        )
    
    return {
        "status": "success",
        "message": "Financial document analysis completed successfully",
        "job_id": job_id,
        "query": analysis_record.query,
        "file_info": {
            "filename": analysis_record.filename,
            "size_mb": analysis_record.file_size_mb,
            "processed_at": analysis_record.created_at.isoformat()
        },
        "analysis": {
            "summary": "Complete financial analysis including verification, metrics analysis, investment insights, and risk assessment",
            "result": analysis_record.detailed_result
        },
        "agents_used": analysis_record.agents_used,
        "processing_info": {
            "completed_at": analysis_record.completed_at.isoformat(),
            "processing_time_seconds": analysis_record.processing_time_seconds
        }
    }

@app.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Get system statistics and performance metrics"""
    
    try:
        # Database statistics
        total_analyses = db.query(AnalysisResult).count()
        completed_analyses = db.query(AnalysisResult).filter(AnalysisResult.status == "completed").count()
        failed_analyses = db.query(AnalysisResult).filter(AnalysisResult.status == "failed").count()
        pending_analyses = db.query(AnalysisResult).filter(AnalysisResult.status.in_(["queued", "processing"])).count()
        
        # Cache statistics
        cached_results = db.query(AnalysisCache).count()
        total_cache_hits = db.query(AnalysisCache).with_entities(
            db.func.sum(AnalysisCache.access_count)
        ).scalar() or 0
        
        # Performance statistics
        avg_processing_time = db.query(AnalysisResult).filter(
            AnalysisResult.processing_time_seconds.isnot(None)
        ).with_entities(
            db.func.avg(AnalysisResult.processing_time_seconds)
        ).scalar()
        
        return {
            "system_status": "operational",
            "analysis_statistics": {
                "total_analyses": total_analyses,
                "completed": completed_analyses,
                "failed": failed_analyses,
                "pending": pending_analyses,
                "success_rate": f"{(completed_analyses/total_analyses*100):.1f}%" if total_analyses > 0 else "N/A"
            },
            "cache_statistics": {
                "cached_results": cached_results,
                "total_cache_hits": total_cache_hits,
                "cache_hit_rate": f"{(total_cache_hits/(total_analyses+total_cache_hits)*100):.1f}%" if (total_analyses + total_cache_hits) > 0 else "N/A"
            },
            "performance": {
                "average_processing_time_seconds": round(avg_processing_time, 2) if avg_processing_time else None
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to retrieve statistics: {str(e)}"}
        )

if __name__ == "__main__":
    try:
        import uvicorn
        print("Starting Financial Document Analyzer API v2.0...")
        print("Features: Redis Queue + PostgreSQL Database + Intelligent Caching")
        print("API will be available at: http://localhost:8000")
        print("API documentation at: http://localhost:8000/docs")
        print("System statistics at: http://localhost:8000/stats")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")