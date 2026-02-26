#!/usr/bin/env python3
"""
Test the new asynchronous API with Redis queue
"""
import requests
import time
import json

def test_async_workflow():
    """Test the complete async workflow"""
    
    print("🧪 Testing Asynchronous Financial Document Analysis")
    print("=" * 60)
    
    # Step 1: Health check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API is healthy")
            health_data = response.json()
            print(f"   Service: {health_data['service']}")
            print(f"   Features: {health_data['features']['queue_processing']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the server is running: python main_simple.py")
        return False
    
    # Step 2: Upload document (should return job_id instantly)
    print("\n2️⃣ Uploading Tesla PDF for analysis...")
    try:
        with open("data/TSLA-Q2-2025-Update.pdf", "rb") as f:
            files = {"file": f}
            data = {"query": "Should I invest in Tesla? Provide detailed analysis."}
            
            start_time = time.time()
            response = requests.post("http://localhost:8000/analyze", files=files, data=data)
            upload_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                job_id = result["job_id"]
                print(f"✅ Upload successful in {upload_time:.2f} seconds")
                print(f"   Job ID: {job_id}")
                print(f"   Status: {result['status']}")
                print(f"   File: {result['file_info']['filename']} ({result['file_info']['size_mb']} MB)")
                return job_id
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
    except FileNotFoundError:
        print("❌ Tesla PDF not found at data/TSLA-Q2-2025-Update.pdf")
        return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_status_tracking(job_id):
    """Test status tracking"""
    print(f"\n3️⃣ Tracking analysis progress for job {job_id}...")
    
    max_attempts = 30  # 5 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"http://localhost:8000/status/{job_id}")
            if response.status_code == 200:
                status_data = response.json()
                status = status_data["status"]
                progress = status_data.get("progress", 0)
                message = status_data.get("message", "Processing...")
                
                print(f"   Status: {status} ({progress}%) - {message}")
                
                if status == "SUCCESS":
                    print("✅ Analysis completed!")
                    return True
                elif status == "FAILURE":
                    error = status_data.get("error", "Unknown error")
                    print(f"❌ Analysis failed: {error}")
                    return False
                
                # Wait before next check
                time.sleep(10)
                attempt += 1
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return False
    
    print("⏰ Analysis taking longer than expected")
    return False

def test_get_results(job_id):
    """Test getting results"""
    print(f"\n4️⃣ Retrieving analysis results for job {job_id}...")
    
    try:
        response = requests.get(f"http://localhost:8000/result/{job_id}")
        if response.status_code == 200:
            result_data = response.json()
            print("✅ Results retrieved successfully!")
            print(f"   Status: {result_data['status']}")
            print(f"   Cached: {result_data['analysis'].get('cached', False)}")
            
            # Show first 500 characters of analysis
            analysis_result = result_data['analysis']['result']
            if len(analysis_result) > 500:
                preview = analysis_result[:500] + "..."
            else:
                preview = analysis_result
                
            print(f"\n📊 Analysis Preview:")
            print("-" * 50)
            print(preview)
            print("-" * 50)
            
            return True
        else:
            print(f"❌ Failed to get results: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Results retrieval error: {e}")
        return False

if __name__ == "__main__":
    # Test complete workflow
    job_id = test_async_workflow()
    
    if job_id:
        # Track progress
        if test_status_tracking(job_id):
            # Get results
            test_get_results(job_id)
        
        print(f"\n🎯 Summary:")
        print(f"   Job ID: {job_id}")
        print(f"   Check status: http://localhost:8000/status/{job_id}")
        print(f"   Get results: http://localhost:8000/result/{job_id}")
    
    print("\n✅ Async API testing completed!")
    input("Press Enter to exit...")