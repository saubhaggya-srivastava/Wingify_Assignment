#!/usr/bin/env python3
"""
Test script for the Financial Document Analyzer API
Run this after starting the main.py server to test if everything works
"""

import requests
import json
import os
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoints"""
    print("🔍 Testing health check endpoints...")
    
    try:
        # Test root endpoint
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()['message']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            health_data = response.json()
            print(f"   Status: {health_data['status']}")
            print(f"   Agents: {', '.join(health_data['agents_available'])}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running:")
        print("   Run: python main.py")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    return True

def test_document_analysis():
    """Test the document analysis endpoint"""
    print("\n📊 Testing document analysis...")
    
    # Check if sample PDF exists
    pdf_path = "data/TSLA-Q2-2025-Update.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ Sample PDF not found at {pdf_path}")
        print("   Please ensure the Tesla PDF is in the data folder")
        return False
    
    try:
        # Test document analysis
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": pdf_file}
            data = {"query": "What are the key financial highlights and should I consider investing?"}
            
            print("   Uploading document and starting analysis...")
            print("   This may take 30-60 seconds...")
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/analyze", files=files, data=data)
            end_time = time.time()
            
            if response.status_code == 200:
                print(f"✅ Document analysis completed in {end_time - start_time:.1f} seconds")
                
                result = response.json()
                print(f"   Status: {result['status']}")
                print(f"   Query: {result['query']}")
                print(f"   File: {result['file_info']['filename']}")
                print(f"   Size: {result['file_info']['size_mb']} MB")
                print(f"   Agents used: {len(result['agents_used'])}")
                
                # Show first 200 characters of analysis
                analysis_preview = result['analysis']['result'][:200] + "..."
                print(f"   Analysis preview: {analysis_preview}")
                
                return True
            else:
                print(f"❌ Document analysis failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Document analysis test failed: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n🚨 Testing error handling...")
    
    try:
        # Test with non-PDF file
        test_content = b"This is not a PDF file"
        files = {"file": ("test.txt", test_content, "text/plain")}
        data = {"query": "Analyze this"}
        
        response = requests.post(f"{BASE_URL}/analyze", files=files, data=data)
        if response.status_code == 400:
            print("✅ Correctly rejected non-PDF file")
        else:
            print(f"❌ Should have rejected non-PDF file, got: {response.status_code}")
            
        # Test with empty query
        if os.path.exists("data/TSLA-Q2-2025-Update.pdf"):
            with open("data/TSLA-Q2-2025-Update.pdf", "rb") as pdf_file:
                files = {"file": pdf_file}
                data = {"query": ""}  # Empty query
                
                response = requests.post(f"{BASE_URL}/analyze", files=files, data=data)
                if response.status_code == 200:
                    print("✅ Handled empty query correctly (used default)")
                else:
                    print(f"❌ Failed to handle empty query: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")

def main():
    """Run all tests"""
    print("🧪 Financial Document Analyzer API Test Suite")
    print("=" * 50)
    
    # Test 1: Health checks
    if not test_health_check():
        print("\n❌ Health check failed. Cannot proceed with other tests.")
        return
    
    # Test 2: Document analysis
    test_document_analysis()
    
    # Test 3: Error handling
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\nIf all tests passed, your Financial Document Analyzer is working correctly!")
    print("You can now:")
    print("1. Visit http://localhost:8000/docs for interactive API documentation")
    print("2. Use the /analyze endpoint to analyze your own financial documents")
    print("3. Integrate the API into your applications")

if __name__ == "__main__":
    main()