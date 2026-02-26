#!/usr/bin/env python3
"""
View detailed content of a specific analysis from database
"""
from database import SessionLocal, AnalysisResult
import json

def view_analysis_details(analysis_id=None):
    """Display full details of an analysis"""
    
    db = SessionLocal()
    
    try:
        print("🔍 Financial Document Analyzer - Detailed Analysis View")
        print("=" * 80)
        
        if analysis_id:
            analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
            analyses = [analysis] if analysis else []
        else:
            # Get the most recent completed analysis
            analyses = db.query(AnalysisResult).filter(
                AnalysisResult.status == "completed"
            ).order_by(AnalysisResult.completed_at.desc()).limit(1).all()
        
        if not analyses:
            print("❌ No completed analyses found in database")
            return
        
        for analysis in analyses:
            print(f"\n📊 ANALYSIS #{analysis.id}")
            print("=" * 80)
            
            print(f"\n📋 METADATA:")
            print(f"   Job ID: {analysis.job_id}")
            print(f"   Filename: {analysis.filename}")
            print(f"   File Size: {analysis.file_size_mb} MB")
            print(f"   Status: {analysis.status}")
            print(f"   Created: {analysis.created_at}")
            print(f"   Completed: {analysis.completed_at}")
            print(f"   Processing Time: {analysis.processing_time_seconds:.2f} seconds")
            
            print(f"\n❓ USER QUERY:")
            print(f"   {analysis.query}")
            
            if analysis.agents_used:
                print(f"\n🤖 AGENTS USED ({len(analysis.agents_used)}):")
                for i, agent in enumerate(analysis.agents_used, 1):
                    print(f"   {i}. {agent}")
            
            if analysis.detailed_result:
                print(f"\n📄 FULL ANALYSIS RESULT:")
                print("=" * 80)
                print(analysis.detailed_result)
                print("=" * 80)
                
                # Show character count
                print(f"\n📊 Result Statistics:")
                print(f"   Total Characters: {len(analysis.detailed_result):,}")
                print(f"   Total Lines: {analysis.detailed_result.count(chr(10)) + 1}")
                
                # Count key sections
                sections = [
                    "Executive Risk Summary",
                    "Financial Risks",
                    "Market and Industry Risks",
                    "Company-Specific Risks",
                    "Risk Mitigation Strategies",
                    "Risk Rating"
                ]
                
                found_sections = [s for s in sections if s in analysis.detailed_result]
                if found_sections:
                    print(f"   Sections Found: {len(found_sections)}/{len(sections)}")
                    for section in found_sections:
                        print(f"      ✓ {section}")
            
            if analysis.error_message:
                print(f"\n❌ ERROR MESSAGE:")
                print(f"   {analysis.error_message}")
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    analysis_id = None
    if len(sys.argv) > 1:
        try:
            analysis_id = int(sys.argv[1])
        except ValueError:
            print("Usage: python view_analysis_details.py [analysis_id]")
            sys.exit(1)
    
    view_analysis_details(analysis_id)
    input("\nPress Enter to exit...")