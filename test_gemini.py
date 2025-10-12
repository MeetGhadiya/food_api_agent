import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env from the food_api_agent directory
load_dotenv('food_api_agent/.env')

api_key = os.getenv("GOOGLE_API_KEY")
print(f"✓ API Key loaded: {api_key[:20]}..." if api_key else "✗ No API key found")

if api_key:
    genai.configure(api_key=api_key)
    
    # Test the model with different formats
    print("\nTrying different model name formats...")
    for model_name in ['models/gemini-1.5-flash', 'models/gemini-pro', 'gemini-1.5-flash', 'gemini-pro']:
        try:
            print(f"\n  Testing '{model_name}'...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hi")
            print(f"  ✅ SUCCESS! {model_name} works!")
            print(f"  Response: {response.text}")
            break
        except Exception as e:
            print(f"  ❌ {model_name} failed: {str(e)[:120]}")
