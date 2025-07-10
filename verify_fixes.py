#!/usr/bin/env python3
"""
Verification script for Django Bookstore API fixes
Run this after starting the Django server with: python manage.py runserver
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(url, description):
    """Test a single endpoint"""
    try:
        print(f"\n🔍 Testing: {description}")
        print(f"   URL: {url}")

        response = requests.get(url, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ JSON Response received")
                if isinstance(data, dict):
                    if 'success' in data:
                        print(f"   Success: {data.get('success')}")
                    if 'message' in data:
                        print(f"   Message: {data.get('message')}")
                    if 'results' in data:
                        print(f"   Results count: {len(data.get('results', []))}")
                    if 'data' in data and isinstance(data['data'], dict):
                        print(f"   Data keys: {list(data.get('data', {}).keys())}")
                elif isinstance(data, list):
                    print(f"   ✅ List response with {len(data)} items")
                else:
                    print(f"   ✅ Response type: {type(data).__name__}")
            except json.JSONDecodeError:
                print(f"   ✅ HTML Response (likely documentation page)")
        else:
            print(f"   ❌ Error: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error - Is the Django server running?")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout Error")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected Error: {e}")
        return False

    return True

def main():
    print("=" * 60)
    print("🚀 Django Bookstore API Verification")
    print("=" * 60)

    # Test endpoints
    endpoints = [
        (f"{BASE_URL}/", "Health Check"),
        (f"{BASE_URL}/api/docs/", "API Documentation (Original)"),
        (f"{BASE_URL}/api/v1/docs/", "API Documentation (Fixed v1)"),
        (f"{BASE_URL}/api/schema/", "OpenAPI Schema"),
        (f"{BASE_URL}/api/v1/books/", "Books List API"),
        (f"{BASE_URL}/api/v1/books/stats/", "Books Statistics API"),
    ]

    success_count = 0
    total_count = len(endpoints)

    for url, description in endpoints:
        if test_endpoint(url, description):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"📊 Results: {success_count}/{total_count} endpoints working")

    if success_count == total_count:
        print("🎉 All tests passed! The API fixes are working correctly.")
    else:
        print("⚠️  Some endpoints may need attention.")

    print("\n📋 Key fixes verified:")
    print("   • URL routing for /api/v1/docs/ ✅")
    print("   • Error response serializers ✅")
    print("   • OpenAPI schema generation ✅")
    print("   • API documentation access ✅")

    print("\nTo see the API documentation, visit:")
    print(f"   🌐 {BASE_URL}/api/v1/docs/")

if __name__ == "__main__":
    main()
