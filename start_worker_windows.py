#!/usr/bin/env python3
"""
Start Celery worker for Windows with proper configuration
"""
import os
import sys

# Set environment variable for Windows compatibility
os.environ['FORKED_BY_MULTIPROCESSING'] = '1'

from celery_app import celery_app

if __name__ == "__main__":
    print("🚀 Starting Celery Worker for Financial Document Analysis (Windows)...")
    print("📋 Available tasks:")
    print("   - analyze_financial_document_task")
    print("   - cleanup_old_cache_entries")
    print("🔄 Worker will process tasks from Redis queue")
    print("📊 Monitor with Flower: celery -A celery_app flower")
    print("⏹️  Stop with Ctrl+C")
    print("-" * 60)
    
    # Start the worker with Windows-compatible settings
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',      # Solo pool for Windows
        '--concurrency=1',  # Single worker
    ])