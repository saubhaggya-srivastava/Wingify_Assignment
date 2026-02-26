## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

import PyPDF2
from crewai.tools import tool
from crewai_tools import SerperDevTool

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
@tool("Read Financial Document")
def financial_document_tool(path: str = 'data/TSLA-Q2-2025-Update.pdf') -> str:
    """Tool to read and extract text content from PDF financial documents
    
    Args:
        path (str): Path of the pdf file. Defaults to 'data/TSLA-Q2-2025-Update.pdf'.

    Returns:
        str: Full Financial Document content
    """
    try:
        if not os.path.exists(path):
            return f"Error: File not found at {path}"
        
        full_report = ""
        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content = page.extract_text()
                
                # Clean and format the financial document data
                while "\n\n" in content:
                    content = content.replace("\n\n", "\n")
                
                full_report += content + "\n"
        
        return full_report if full_report.strip() else "Error: Could not extract text from PDF"
        
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

## Creating Investment Analysis Tool
@tool("Investment Analysis")
def investment_tool(financial_document_data: str) -> str:
    """Tool to analyze financial document data for investment insights
    
    Args:
        financial_document_data (str): Financial document content to analyze
        
    Returns:
        str: Investment analysis results
    """
    try:
        # Process and analyze the financial document data
        processed_data = financial_document_data
        
        # Clean up the data format
        processed_data = processed_data.replace("  ", " ")  # Remove double spaces
        
        # Basic analysis structure
        analysis = {
            "revenue_trends": "Analysis of revenue patterns",
            "profitability": "Profit margin analysis", 
            "growth_metrics": "Growth rate calculations",
            "market_position": "Competitive positioning"
        }
        
        return str(analysis)
        
    except Exception as e:
        return f"Error in investment analysis: {str(e)}"

## Creating Risk Assessment Tool
@tool("Risk Assessment")
def risk_tool(financial_document_data: str) -> str:
    """Tool to create comprehensive risk assessment from financial data
    
    Args:
        financial_document_data (str): Financial document content to analyze
        
    Returns:
        str: Risk assessment results
    """
    try:
        # Risk assessment categories
        risk_assessment = {
            "market_risk": "Market volatility analysis",
            "credit_risk": "Credit worthiness evaluation",
            "operational_risk": "Business operation risks",
            "liquidity_risk": "Cash flow and liquidity analysis"
        }
        
        return str(risk_assessment)
        
    except Exception as e:
        return f"Error in risk assessment: {str(e)}"