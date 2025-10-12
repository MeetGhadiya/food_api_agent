"""
Simple test to check if the Gemini API key is valid
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv('food_api_agent/.env')
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ No API key found!")
    exit(1)

print(f"API Key: {api_key}")
print(f"Length: {len(api_key)}")
print(f"Starts with: {api_key[:20]}...")

# Try configuring
try:
    genai.configure(api_key=api_key)
    print("✅ API key configured")
    
    # Try a simple request
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello")
    print(f"✅ API working! Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nThis API key appears to be invalid or the Gemini API has changed.")
    print("Please get a new API key from: https://makersuite.google.com/app/apikey")
