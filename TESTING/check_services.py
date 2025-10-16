"""
Service Status Checker
Quickly verify all required services are running before testing
"""

import requests
import sys

class colors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def check_service(name, url, timeout=5):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {colors.OKGREEN}{name} is running{colors.ENDC} - {url}")
            return True
        else:
            print(f"❌ {colors.FAIL}{name} returned status {response.status_code}{colors.ENDC}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {colors.FAIL}{name} is NOT running{colors.ENDC} - {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {colors.FAIL}{name} timed out{colors.ENDC} - {url}")
        return False
    except Exception as e:
        print(f"❌ {colors.FAIL}{name} error: {e}{colors.ENDC}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  FoodieExpress - Service Status Check")
    print("="*60)
    print()
    
    all_ok = True
    
    # Check FastAPI
    print("Checking FastAPI Backend...")
    all_ok &= check_service("FastAPI", "http://localhost:8000/health")
    print()
    
    # Check Flask Agent
    print("Checking Flask Agent...")
    all_ok &= check_service("Flask Agent", "http://localhost:5000/health")
    print()
    
    # Summary
    print("="*60)
    if all_ok:
        print(f"{colors.OKGREEN}{colors.BOLD}✅ All services are running! Ready to test.{colors.ENDC}")
        print("="*60)
        sys.exit(0)
    else:
        print(f"{colors.FAIL}{colors.BOLD}❌ Some services are not running!{colors.ENDC}")
        print("\nPlease start the missing services:")
        print("  1. FastAPI: cd food_api && uvicorn app.main:app --reload")
        print("  2. Flask Agent: cd food_chatbot_agent && python agent.py")
        print("  3. Ollama: ollama serve")
        print("="*60)
        sys.exit(1)
