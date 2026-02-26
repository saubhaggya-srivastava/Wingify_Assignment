from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import asyncio

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document, investment_analysis, risk_assessment, verification

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial document analysis system using CrewAI",
    version="1.0.0"
)

def run_financial_analysis_crew(query: str, file_path: str):
    """Run the complete financial analysis crew with all agents and tasks"""
    
    # Create the financial analysis crew with all agents and tasks
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
        process=Process.sequential,  # Run tasks in order
        verbose=True
    )
    
    # Pass both query and file_path to the crew
    result = financial_crew.kickoff({
        'query': query,
        'file_path': file_path
    })
    
    return result

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Financial Document Analyzer API is running",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "analyze": "/analyze - POST - Upload and analyze financial documents",
            "health": "/ - GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "Financial Document Analyzer",
        "agents_available": ["financial_analyst", "verifier", "investment_advisor", "risk_assessor"],
        "supported_formats": ["PDF"],
        "max_file_size": "10MB"
    }

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(..., description="Financial document to analyze (PDF format)"),
    query: str = Form(
        default="Provide a comprehensive analysis of this financial document including investment insights and risk assessment",
        description="Specific question or analysis request for the financial document"
    )
):
    """
    Analyze financial document and provide comprehensive investment recommendations
    
    This endpoint:
    1. Verifies the uploaded document is a valid financial report
    2. Extracts and analyzes key financial metrics
    3. Provides professional investment insights
    4. Conducts comprehensive risk assessment
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
        
        # Process the financial document with the complete crew
        print(f"Starting analysis for file: {file.filename}")
        print(f"Query: {query}")
        
        analysis_result = run_financial_analysis_crew(
            query=query, 
            file_path=file_path
        )
        
        return {
            "status": "success",
            "message": "Financial document analysis completed successfully",
            "query": query,
            "file_info": {
                "filename": file.filename,
                "size_mb": round(len(file_content) / (1024 * 1024), 2),
                "processed_at": file_id
            },
            "analysis": {
                "summary": "Complete financial analysis including verification, metrics analysis, investment insights, and risk assessment",
                "result": str(analysis_result)
            },
            "agents_used": [
                "Document Verifier - Validated document authenticity",
                "Financial Analyst - Analyzed financial metrics and trends", 
                "Investment Advisor - Provided investment recommendations",
                "Risk Assessor - Conducted comprehensive risk analysis"
            ]
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
        
    except Exception as e:
        # Handle unexpected errors
        error_message = f"Error processing financial document: {str(e)}"
        print(f"Error: {error_message}")
        
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Internal server error",
                "message": "Failed to process the financial document",
                "details": str(e),
                "suggestion": "Please ensure the uploaded file is a valid PDF financial document"
            }
        )
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up temporary file: {file_path}")
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up file {file_path}: {cleanup_error}")

if __name__ == "__main__":
    try:
        import uvicorn
        print("Starting Financial Document Analyzer API...")
        print("API will be available at: http://localhost:8000")
        print("API documentation at: http://localhost:8000/docs")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=False,  # Disable reload to avoid the warning
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")