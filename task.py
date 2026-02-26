## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, financial_document_tool

## Creating a task to analyze financial documents
analyze_financial_document = Task(
    description="""Read the financial document at {file_path} and analyze it thoroughly to answer the user's query: {query}

    Step-by-step process:
    1. Use the financial document tool to read the PDF file at the provided path
    2. Extract and identify key financial data from the document (revenue, profit, cash flow, debt, etc.)
    3. Analyze trends and patterns in the financial data
    4. Research current market conditions using web search
    5. Provide a comprehensive analysis answering the user's specific query
    
    IMPORTANT: You must actually read the document using the financial document tool before providing analysis.""",

    expected_output="""A comprehensive financial analysis report that includes:
    
    **Document Summary:**
    - Company name and reporting period
    - Key financial highlights extracted from the actual document
    
    **Financial Metrics Analysis:**
    - Specific revenue figures and growth rates from the document
    - Actual profitability metrics (margins, earnings) with numbers
    - Real cash flow data from the financial statements
    - Actual debt levels and liquidity position with figures
    
    **Market Context:**
    - Industry comparison and benchmarks
    - Current market conditions affecting the company
    
    **Response to User Query:**
    - Direct answer to: {query}
    - Supporting evidence with specific data from the financial document
    
    **Key Insights:**
    - Most important findings from the actual document analysis
    - Notable trends or concerns identified from real data
    
    All analysis must be based on actual data extracted from the document at {file_path}.""",

    agent=financial_analyst,
    tools=[financial_document_tool, search_tool],
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis = Task(
    description="""Based on the financial document analysis, provide professional investment insights for the user query: {query}

    Your investment analysis should:
    1. Review the financial health and performance metrics
    2. Assess the company's competitive position and market outlook
    3. Identify key investment strengths and potential concerns
    4. Research current analyst opinions and market sentiment
    5. Provide balanced investment perspective with proper risk considerations
    
    Maintain professional standards and avoid speculative recommendations.""",

    expected_output="""A professional investment analysis including:
    
    **Investment Thesis:**
    - Clear summary of investment opportunity or concerns
    - Key factors supporting the investment case
    
    **Financial Strengths:**
    - Strong performance metrics and positive trends
    - Competitive advantages identified
    
    **Areas of Concern:**
    - Financial weaknesses or declining metrics
    - Market or operational risks
    
    **Valuation Perspective:**
    - Assessment of current valuation relative to fundamentals
    - Comparison to industry peers where relevant
    
    **Investment Recommendation:**
    - Balanced perspective on investment merit
    - Appropriate investor profile for this investment
    - Time horizon considerations
    
    **Important Disclaimers:**
    - This analysis is for informational purposes only
    - Past performance does not guarantee future results
    - Investors should conduct their own due diligence""",

    agent=investment_advisor,
    tools=[search_tool],
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment = Task(
    description="""Conduct a comprehensive risk assessment based on the financial document and user query: {query}

    Your risk analysis should cover:
    1. Financial risks (liquidity, credit, operational)
    2. Market risks (industry trends, economic factors)
    3. Company-specific risks (management, strategy, competition)
    4. External risks (regulatory, technological, environmental)
    5. Provide practical risk management recommendations
    
    Focus on identifying real, material risks based on the financial data.""",

    expected_output="""A detailed risk assessment report including:
    
    **Executive Risk Summary:**
    - Overall risk level assessment
    - Most critical risks identified
    
    **Financial Risks:**
    - Liquidity and cash flow risks
    - Debt and credit risks
    - Operational efficiency risks
    
    **Market and Industry Risks:**
    - Industry-specific challenges
    - Economic sensitivity analysis
    - Competitive positioning risks
    
    **Company-Specific Risks:**
    - Management and governance risks
    - Strategic execution risks
    - Key dependency risks
    
    **Risk Mitigation Strategies:**
    - Recommended risk management approaches
    - Diversification considerations
    - Monitoring indicators to watch
    
    **Risk Rating:**
    - Overall risk assessment (Low/Medium/High)
    - Risk-adjusted return considerations
    
    All risk assessments must be supported by specific evidence from the financial document.""",

    agent=risk_assessor,
    tools=[search_tool],
    async_execution=False,
)

## Creating a document verification task
verification = Task(
    description="""Read and verify the financial document at {file_path} to ensure it's suitable for analysis.

    Your verification process should:
    1. Use the financial document tool to read the PDF file at {file_path}
    2. Identify the type of financial report (10-K, 10-Q, earnings report, etc.)
    3. Check for standard financial statement components
    4. Verify data consistency and completeness
    5. Confirm the document contains legitimate financial data
    
    IMPORTANT: You must actually read the document using the financial document tool.""",

    expected_output="""A document verification report including:
    
    **Document Classification:**
    - Type of financial document identified from actual content
    - Company name and reporting period extracted from the document
    - Document source and authenticity assessment
    
    **Completeness Check:**
    - Key financial statements present (Income Statement, Balance Sheet, Cash Flow)
    - Important sections and disclosures found in the document
    - Any missing or incomplete information identified
    
    **Data Quality Assessment:**
    - Consistency of financial data found in the document
    - Readability and format quality of the extracted text
    - Any data extraction issues encountered
    
    **Verification Status:**
    - Overall document quality rating based on actual content
    - Suitability for financial analysis
    - Any limitations or caveats for analysis
    
    **Recommendations:**
    - Whether the document is suitable for investment analysis
    - Any additional documents that would be helpful
    - Specific areas requiring careful interpretation
    
    Base all assessments on the actual content read from {file_path}.""",

    agent=verifier,
    tools=[financial_document_tool],
    async_execution=False
)