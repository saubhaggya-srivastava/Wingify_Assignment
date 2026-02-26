#!/usr/bin/env python3
"""
Check what's stored in the database
"""
from database import SessionLocal, AnalysisResult, AnalysisCache, User
from datetime import datetime

def check_database():
    """Display all data stored in the database"""
    
    db = SessionLocal()
    
    try:
        print("🗄️  Financial Document Analyzer - Database Contents")
        print("=" * 70)
        
        # Check Analysis Results
        print("\n📊 ANALYSIS RESULTS:")
        print("-" * 70)
        
        analyses = db.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).all()
        
        if analyses:
            for i, analysis in enumerate(analyses, 1):
                print(f"\n{i}. Analysis #{analysis.id}")
                print(f"   Job ID: {analysis.job_id}")
                print(f"   Filename: {analysis.filename}")
                print(f"   File Size: {analysis.file_size_mb} MB")
                print(f"   Query: {analysis.query[:80]}...")
                print(f"   Status: {analysis.status}")
                print(f"   Created: {analysis.created_at}")
                print(f"   Completed: {analysis.completed_at}")
                print(f"   Processing Time: {analysis.processing_time_seconds} seconds")
                
                if analysis.detailed_result:
                    result_preview = analysis.detailed_result[:200].replace('\n', ' ')
                    print(f"   Result Preview: {result_preview}...")
                
                if analysis.agents_used:
                    print(f"   Agents Used: {len(analysis.agents_used)} agents")
        else:
            print("   No analyses found in database")
        
        # Check Cache
        print("\n\n💾 ANALYSIS CACHE:")
        print("-" * 70)
        
        cache_entries = db.query(AnalysisCache).order_by(AnalysisCache.created_at.desc()).all()
        
        if cache_entries:
            for i, cache in enumerate(cache_entries, 1):
                print(f"\n{i}. Cache Entry #{cache.id}")
                print(f"   Filename: {cache.filename}")
                print(f"   File Hash: {cache.file_hash[:16]}...")
                print(f"   Query Hash: {cache.query_hash[:16]}...")
                print(f"   Created: {cache.created_at}")
                print(f"   Access Count: {cache.access_count}")
                print(f"   Last Accessed: {cache.last_accessed}")
                
                if cache.analysis_result:
                    result_preview = cache.analysis_result[:200].replace('\n', ' ')
                    print(f"   Cached Result: {result_preview}...")
        else:
            print("   No cache entries found")
        
        # Check Users
        print("\n\n👥 USERS:")
        print("-" * 70)
        
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        if users:
            for i, user in enumerate(users, 1):
                print(f"\n{i}. User #{user.id}")
                print(f"   Session ID: {user.session_id}")
                print(f"   IP Address: {user.ip_address}")
                print(f"   Total Analyses: {user.total_analyses}")
                print(f"   Created: {user.created_at}")
                print(f"   Last Activity: {user.last_activity}")
        else:
            print("   No users found")
        
        # Summary
        print("\n\n📈 SUMMARY:")
        print("-" * 70)
        print(f"   Total Analyses: {len(analyses)}")
        print(f"   Cached Results: {len(cache_entries)}")
        print(f"   Total Users: {len(users)}")
        
        if analyses:
            completed = sum(1 for a in analyses if a.status == "completed")
            failed = sum(1 for a in analyses if a.status == "failed")
            pending = sum(1 for a in analyses if a.status in ["queued", "processing"])
            
            print(f"   Completed: {completed}")
            print(f"   Failed: {failed}")
            print(f"   Pending: {pending}")
            
            if completed > 0:
                avg_time = sum(a.processing_time_seconds for a in analyses if a.processing_time_seconds) / completed
                print(f"   Average Processing Time: {avg_time:.2f} seconds")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
    input("\nPress Enter to exit...")