#!/usr/bin/env python3
"""
Setup script for bonus features: Redis Queue + PostgreSQL Database
"""
import os
import subprocess
import sys
from dotenv import load_dotenv

def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running and accessible")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def check_postgresql():
    """Check if PostgreSQL is accessible"""
    try:
        import psycopg2
        from sqlalchemy import create_engine
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not set in .env file")
            return False
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        print("✅ PostgreSQL is running and accessible")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing bonus feature dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    env_file = ".env"
    env_example = ".env.example"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            print("📝 Creating .env file from .env.example...")
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✅ .env file created")
            print("⚠️  Please update .env file with your actual API keys and database URL")
            return False
        else:
            print("❌ .env.example file not found")
            return False
    
    load_dotenv()
    
    # Check required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "SERPER_API_KEY", 
        "REDIS_URL",
        "DATABASE_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith("your_"):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or placeholder values for: {', '.join(missing_vars)}")
        print("Please update your .env file with actual values")
        return False
    
    print("✅ Environment variables configured")
    return True

def main():
    """Main setup function"""
    print("🚀 Financial Document Analyzer - Bonus Features Setup")
    print("=" * 60)
    print("Setting up Redis Queue + PostgreSQL Database integration...")
    print()
    
    # Step 1: Install dependencies
    if not install_dependencies():
        return False
    
    # Step 2: Setup environment
    if not setup_environment():
        return False
    
    # Step 3: Check Redis
    print("\n🔍 Checking Redis connection...")
    redis_ok = check_redis()
    
    # Step 4: Check PostgreSQL
    print("\n🔍 Checking PostgreSQL connection...")
    postgres_ok = check_postgresql()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Setup Summary:")
    print(f"   Dependencies: ✅ Installed")
    print(f"   Environment:  ✅ Configured")
    print(f"   Redis:        {'✅ Ready' if redis_ok else '❌ Not Ready'}")
    print(f"   PostgreSQL:   {'✅ Ready' if postgres_ok else '❌ Not Ready'}")
    
    if redis_ok and postgres_ok:
        print("\n🎉 All bonus features are ready!")
        print("\n🚀 Next steps:")
        print("1. Initialize database: python init_db.py")
        print("2. Start Celery worker: python start_worker.py")
        print("3. Start API server: python main.py")
        print("4. Monitor with Flower: celery -A celery_app flower")
        
        return True
    else:
        print("\n❌ Some services are not ready. Please fix the issues above.")
        
        if not redis_ok:
            print("\n🔧 Redis Setup:")
            print("   - Install Redis: https://redis.io/download")
            print("   - Start Redis: redis-server")
            print("   - Test: redis-cli ping")
        
        if not postgres_ok:
            print("\n🔧 PostgreSQL Setup:")
            print("   - Install PostgreSQL: https://www.postgresql.org/download/")
            print("   - Create database: createdb financial_analyzer")
            print("   - Update DATABASE_URL in .env file")
        
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n⚠️  Setup incomplete. Please resolve the issues above.")
    
    input("\nPress Enter to exit...")