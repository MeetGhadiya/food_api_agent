"""
Check OpenAPI Schema for Security Schemes
"""

import requests
import json

try:
    response = requests.get("http://localhost:8000/openapi.json", timeout=5)
    schema = response.json()
    
    print("="*70)
    print("  OPENAPI SECURITY SCHEMES")
    print("="*70)
    
    if "components" in schema and "securitySchemes" in schema["components"]:
        schemes = schema["components"]["securitySchemes"]
        print(f"\n✅ Found {len(schemes)} security scheme(s):\n")
        print(json.dumps(schemes, indent=2))
        
        # Check for OAuth2
        if "oauth2" in schemes or "OAuth2PasswordBearer" in schemes:
            print("\n⚠️  WARNING: OAuth2 schemes detected!")
            print("This is causing the Swagger OAuth2 dialog issue.")
        else:
            print("\n✅ No OAuth2 schemes found - using HTTPBearer only!")
    else:
        print("\n❌ No security schemes found in schema")
    
    print("\n" + "="*70)

except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure the API server is running on localhost:8000")
