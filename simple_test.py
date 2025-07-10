import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore_api.settings')
django.setup()

from django.test import Client
from django.urls import reverse
import json

print("=== Django Bookstore API Test ===")

client = Client()

# Test health endpoint
print("\n1. Testing Health Check:")
try:
    response = client.get('/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test API schema
print("\n2. Testing API Schema:")
try:
    response = client.get('/api/schema/')
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.get('Content-Type', 'N/A')}")
except Exception as e:
    print(f"   Error: {e}")

# Test documentation endpoints
print("\n3. Testing Documentation Endpoints:")
endpoints = ['/api/docs/', '/api/v1/docs/', '/api/redoc/', '/api/v1/redoc/']
for endpoint in endpoints:
    try:
        response = client.get(endpoint)
        print(f"   {endpoint}: Status {response.status_code}")
    except Exception as e:
        print(f"   {endpoint}: Error - {e}")

# Test books API
print("\n4. Testing Books API:")
try:
    response = client.get('/api/v1/books/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data.get('results', []))} books")
except Exception as e:
    print(f"   Error: {e}")

# Test stats endpoint
print("\n5. Testing Stats Endpoint:")
try:
    response = client.get('/api/v1/books/stats/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Stats data: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

print("\n=== Test Complete ===")
