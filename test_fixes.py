#!/usr/bin/env python
"""
Test script to verify the Django bookstore API fixes
"""

import os
import sys
import django
import requests
from django.test import TestCase
from django.urls import reverse
from django.test.client import Client

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore_api.settings')
django.setup()

def test_url_routing():
    """Test URL routing and documentation endpoints"""
    client = Client()

    print("Testing Django Bookstore API URL routing...")

    # Test health check
    try:
        response = client.get('/')
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

    # Test API schema endpoint
    try:
        response = client.get('/api/schema/')
        print(f"✅ Schema endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Schema endpoint failed: {e}")

    # Test Swagger docs endpoints
    try:
        response = client.get('/api/docs/')
        print(f"✅ Swagger docs (/api/docs/): {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger docs (/api/docs/) failed: {e}")

    try:
        response = client.get('/api/v1/docs/')
        print(f"✅ Swagger docs (/api/v1/docs/): {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger docs (/api/v1/docs/) failed: {e}")

    # Test books API endpoints
    try:
        response = client.get('/api/v1/books/')
        print(f"✅ Books list: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('results', []))} books")
    except Exception as e:
        print(f"❌ Books list failed: {e}")

    # Test books stats endpoint
    try:
        response = client.get('/api/v1/books/stats/')
        print(f"✅ Books stats: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Stats: {data}")
    except Exception as e:
        print(f"❌ Books stats failed: {e}")

if __name__ == '__main__':
    test_url_routing()
