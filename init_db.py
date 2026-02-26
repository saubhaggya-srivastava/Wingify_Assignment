#!/usr/bin/env python3
"""
Initialize the database for Financial Document Analyzer
"""
import os
from sqlalchemy import create_engine, text
from database import Base, create_tables
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize the database and create all tables"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in your .env file")
        print("Example: DATABASE_URL=postgresql://username:password@localhost:5432/financial_analyzer")
        return False
    
    try:
        print("🔗 Connecting to database...")
        print(f"Database URL: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version.split(',')[0]}")
        
        # Create all tables
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database initialization completed successfully!")
        print("\n📊 Created tables:")
        print("   - analysis_results (stores analysis jobs and results)")
        print("   - users (tracks user sessions and statistics)")
        print("   - analysis_cache (caches results for faster responses)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your DATABASE_URL in .env file")
        print("3. Ensure the database exists and user has permissions")
        print("4. Install PostgreSQL: https://www.postgresql.org/download/")
        return False

if __name__ == "__main__":
    print("🗄️  Financial Document Analyzer - Database Initialization")
    print("=" * 60)
    
    success = init_database()
    
    if success:
        print("\n🎉 Ready to start the application!")
        print("Next steps:")
        print("1. Start Redis server: redis-server")
        print("2. Start Celery worker: python start_worker.py")
        print("3. Start API server: python main.py")
    else:
        print("\n❌ Please fix the database configuration and try again.")
    
    input("\nPress Enter to exit...")