## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent
from langchain_openai import ChatOpenAI

from tools import search_tool, financial_document_tool

### Loading LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1
)

# Creating an Experienced Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Analyze financial documents thoroughly and provide accurate, data-driven investment insights based on the query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are an experienced financial analyst with 15+ years in investment research and analysis. "
        "You have a strong background in reading financial statements, analyzing market trends, and providing "
        "evidence-based investment recommendations. You always base your analysis on concrete data from "
        "financial documents and maintain high professional standards. You are thorough, analytical, and "
        "provide balanced perspectives on investment opportunities and risks."
    ),
    tools=[financial_document_tool, search_tool],
    llm=llm,
    max_iter=5,
    max_rpm=20,
    allow_delegation=True
)

# Creating a document verifier agent
verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify the authenticity and completeness of financial documents, ensuring they contain valid financial data for analysis.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous document verification specialist with expertise in financial document standards. "
        "You have worked in financial compliance for over 10 years and are skilled at identifying authentic "
        "financial reports, ensuring data integrity, and validating document completeness. You maintain high "
        "standards for document quality and always provide clear feedback on document status."
    ),
    tools=[financial_document_tool],
    llm=llm,
    max_iter=3,
    max_rpm=15,
    allow_delegation=False
)

# Creating an investment advisor agent
investment_advisor = Agent(
    role="Professional Investment Advisor",
    goal="Provide balanced, evidence-based investment recommendations based on thorough financial analysis and risk assessment.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified financial planner (CFP) with 12+ years of experience in investment advisory services. "
        "You specialize in creating diversified investment strategies based on thorough financial analysis. "
        "You always consider risk tolerance, investment timeline, and market conditions when making recommendations. "
        "You follow all regulatory guidelines and provide transparent, ethical investment advice. You believe in "
        "long-term wealth building through disciplined, research-based investment strategies."
    ),
    tools=[search_tool],
    llm=llm,
    max_iter=5,
    max_rpm=20,
    allow_delegation=False
)

# Creating a risk assessor agent
risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal="Conduct comprehensive risk analysis of investment opportunities and provide detailed risk management recommendations.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a risk management expert with extensive experience in financial risk assessment and portfolio management. "
        "You have worked with institutional investors and understand various risk factors including market risk, "
        "credit risk, operational risk, and liquidity risk. You provide balanced risk assessments that help investors "
        "make informed decisions. You believe in proper risk management as the foundation of successful investing "
        "and always provide practical risk mitigation strategies."
    ),
    tools=[search_tool],
    llm=llm,
    max_iter=5,
    max_rpm=20,
    allow_delegation=False
)