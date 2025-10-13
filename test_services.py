#!/usr/bin/env python3
"""Test script to verify all services are running"""

import requests
import sys

def test_service(name, url, method='GET', data=None):
    """Test if a service is responding"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        print(f"✅ {name}: Status {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection Refused (Service not running)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {name}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Testing All Services")
    print("=" * 60)
    
    results = []
    
    # Test FastAPI Backend
    results.append(test_service(
        "FastAPI Backend",
        "http://localhost:8000/restaurants/"
    ))
    
    # Test Flask AI Agent Health
    results.append(test_service(
        "Flask Agent Health",
        "http://localhost:5000/health"
    ))
    
    # Test Flask AI Agent Chat
    results.append(test_service(
        "Flask Agent Chat",
        "http://localhost:5000/chat",
        method='POST',
        data={"message": "test", "user_id": "test"}
    ))
    
    # Test Frontend (just check if server responds)
    results.append(test_service(
        "Frontend",
        "http://localhost:5174/"
    ))
    
    print("=" * 60)
    if all(results):
        print("✅ All services are running!")
        sys.exit(0)
    else:
        print("❌ Some services are not running!")
        sys.exit(1)

if __name__ == "__main__":
    main()
