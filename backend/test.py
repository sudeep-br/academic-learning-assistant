#!/usr/bin/env python3
"""
Quick test script to verify backend is working
Run this after starting the Flask server
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✓ Health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_api_init():
    """Test API initialization (use dummy key for test)"""
    try:
        response = requests.post(
            f"{BASE_URL}/init-api",
            json={"api_key": "sk-test-key"}
        )
        print(f"✓ API init endpoint responds: {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ API init failed: {e}")
        return False

def test_documents():
    """Test document listing"""
    try:
        response = requests.get(f"{BASE_URL}/documents")
        data = response.json()
        print(f"✓ Documents endpoint: {response.status_code}")
        print(f"  Current documents: {len(data.get('documents', []))}")
        return True
    except Exception as e:
        print(f"✗ Documents endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("\n=== Academic Learning Assistant - Backend Test ===\n")
    
    print("Make sure the Flask server is running with:")
    print("  python app.py\n")
    
    time.sleep(1)
    
    tests = [
        ("Health Check", test_health),
        ("API Initialization", test_api_init),
        ("Document Listing", test_documents),
    ]
    
    passed = 0
    for name, test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n=== Results: {passed}/{len(tests)} tests passed ===\n")
