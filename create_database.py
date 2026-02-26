#!/usr/bin/env python3
"""
Create the financial_analyzer database
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create the financial_analyzer database if it doesn't exist"""
    
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            user="postgres",
            password="Viprance1"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'financial_analyzer'")
        exists = cursor.fetchone()
        
        if exists:
            print("✅ Database 'financial_analyzer' already exists")
        else:
            # Create database
            cursor.execute("CREATE DATABASE financial_analyzer")
            print("✅ Database 'financial_analyzer' created successfully")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == "__main__":
    print("🗄️  Creating financial_analyzer database...")
    print("=" * 50)
    
    if create_database():
        print("\n🎉 Database setup complete!")
        print("Next step: python init_db.py")
    else:
        print("\n❌ Database creation failed")
        print("Please create the database manually in pgAdmin")
    
    input("\nPress Enter to exit...")