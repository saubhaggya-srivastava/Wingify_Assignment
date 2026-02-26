#!/usr/bin/env python3
"""
Start Celery worker for background task processing
"""
import os
import sys
from celery_app import celery_app

if __name__ == "__main__":
    print("🚀 Starting Celery Worker for Financial Document Analysis...")
    print("📋 Available tasks:")
    print("   - analyze_financial_document_task")
    print("   - cleanup_old_cache_entries")
    print("🔄 Worker will process tasks from Redis queue")
    print("📊 Monitor with Flower: celery -A celery_app flower")
    print("⏹️  Stop with Ctrl+C")
    print("-" * 60)
    
    # Start the worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=1',  # Process 1 task at a time
        '--pool=solo',      # Use solo pool for Windows compatibility
    ])