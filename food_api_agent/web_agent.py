from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configure Gemini AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("WARNING: GOOGLE_API_KEY not found in .env file")
else:
    genai.configure(api_key=api_key)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Function declarations for Gemini
available_tools = {
    "get_all_restaurants": lambda: get_all_restaurants(),
    "get_restaurant_by_name": lambda name: get_restaurant_by_name(name),
    "place_order": lambda restaurant_name, item, token: place_order(restaurant_name, item, token),
}

all_restaurants_func = genai.protos.FunctionDeclaration(
    name="get_all_restaurants", 
    description="Get a list of all available restaurants with their details including name, area, and cuisine."
)

restaurant_by_name_func = genai.protos.FunctionDeclaration(
    name="get_restaurant_by_name", 
    description="Get detailed information about a single restaurant by its name.", 
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT, 
        properties={
            "name": genai.protos.Schema(
                type=genai.protos.Type.STRING, 
                description="The name of the restaurant."
            )
        }, 
        required=["name"]
    )
)

place_order_func = genai.protos.FunctionDeclaration(
    name="place_order", 
    description="Place a food order for a specific item from a restaurant. Requires user authentication.", 
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT, 
        properties={
            "restaurant_name": genai.protos.Schema(
                type=genai.protos.Type.STRING, 
                description="The name of the restaurant."
            ), 
            "item": genai.protos.Schema(
                type=genai.protos.Type.STRING, 
                description="The food item to order."
            ),
            "token": genai.protos.Schema(
                type=genai.protos.Type.STRING, 
                description="Authentication token for the user."
            )
        }, 
        required=["restaurant_name", "item", "token"]
    )
)

api_tool = genai.protos.Tool(
    function_declarations=[
        all_restaurants_func, 
        restaurant_by_name_func, 
        place_order_func
    ]
)

# Initialize model
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash', 
    tools=[api_tool]
)

# Store chat sessions per user
chat_sessions = {}

# API Helper Functions
def get_all_restaurants():
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        return {"error": str(e)}

def get_restaurant_by_name(name):
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/{name}")
        if response.status_code == 200:
            return response.json()
        return {"error": "Restaurant not found"}
    except Exception as e:
        return {"error": str(e)}

def place_order(restaurant_name, item, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"restaurant_name": restaurant_name, "item": item}
        response = requests.post(
            f"{API_BASE_URL}/orders/", 
            json=data, 
            headers=headers
        )
        if response.status_code == 201:
            return response.json()
        return {"error": "Failed to place order"}
    except Exception as e:
        return {"error": str(e)}

# Routes
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        token = data.get('token')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get or create chat session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = model.start_chat()
        
        chat = chat_sessions[session_id]
        
        # Send message to Gemini
        response = chat.send_message(user_message)
        
        # Handle function calls
        try:
            response_message = response.candidates[0].content
            if response_message.parts and response_message.parts[0].function_call:
                fc = response_message.parts[0].function_call
                function_name = fc.name
                function_args = {key: value for key, value in fc.args.items()}
                
                if function_name in available_tools:
                    # Add token for place_order function
                    if function_name == "place_order":
                        if not token:
                            return jsonify({
                                "response": "Please login first to place an order!"
                            })
                        function_args['token'] = token
                    
                    # Call the function
                    if function_name == "place_order":
                        api_response = available_tools[function_name](
                            function_args.get('restaurant_name'),
                            function_args.get('item'),
                            function_args.get('token')
                        )
                    elif function_name == "get_restaurant_by_name":
                        api_response = available_tools[function_name](
                            function_args.get('name')
                        )
                    else:
                        api_response = available_tools[function_name]()
                    
                    # Send function response back to Gemini
                    response = chat.send_message(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"result": str(api_response)}
                            )
                        )
                    )
        except (ValueError, IndexError) as e:
            print(f"Error processing function call: {e}")
        
        # Extract final text response
        try:
            if response.text:
                return jsonify({"response": response.text})
            else:
                return jsonify({
                    "response": "I'm sorry, I'm having trouble processing that request. Could you rephrase?"
                })
        except ValueError:
            return jsonify({
                "response": "I encountered an error. Please try again."
            })
            
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("🚀 Starting Food Delivery AI Agent Server...")
    print("📡 Frontend: http://localhost:5000")
    print("🤖 Agent API: http://localhost:5000/chat")
    print("💾 API Backend: http://localhost:8000")
    app.run(debug=True, port=5000)
