from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static', template_folder=STATIC_DIR)
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
    "create_restaurant": lambda name, area, cuisine, token: create_restaurant(name, area, cuisine, token),
    "update_restaurant": lambda old_name, new_name, area, cuisine, token: update_restaurant(old_name, new_name, area, cuisine, token),
    "delete_restaurant": lambda name, token: delete_restaurant(name, token),
    "place_order": lambda restaurant_name, item, token: place_order(restaurant_name, item, token),
    "get_all_orders": lambda token: get_all_orders(token),
}

all_restaurants_func = genai.protos.FunctionDeclaration(
    name="get_all_restaurants", 
    description="Get a list of all available restaurants with their details including name, area, and cuisine type."
)

restaurant_by_name_func = genai.protos.FunctionDeclaration(
    name="get_restaurant_by_name", 
    description="Get detailed information about a single restaurant by its exact name.", 
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT, 
        properties={
            "name": genai.protos.Schema(
                type=genai.protos.Type.STRING, 
                description="The exact name of the restaurant."
            )
        }, 
        required=["name"]
    )
)

create_restaurant_func = genai.protos.FunctionDeclaration(
    name="create_restaurant",
    description="Create a new restaurant. Requires authentication. Use this when user wants to add a new restaurant to the system.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "name": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="The name of the restaurant to create."
            ),
            "area": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="The area/location where the restaurant is located."
            ),
            "cuisine": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="The type of cuisine the restaurant serves (e.g., Italian, Chinese, Indian)."
            ),
            "token": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Authentication token for the user."
            )
        },
        required=["name", "area", "cuisine", "token"]
    )
)

update_restaurant_func = genai.protos.FunctionDeclaration(
    name="update_restaurant",
    description="Update an existing restaurant's details. Requires authentication. Use this when user wants to modify restaurant information.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "old_name": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="The current name of the restaurant to update."
            ),
            "new_name": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="The new name for the restaurant."
            ),
            "area": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="The new area/location for the restaurant."
            ),
            "cuisine": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="The new cuisine type for the restaurant."
            ),
            "token": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Authentication token for the user."
            )
        },
        required=["old_name", "new_name", "area", "cuisine", "token"]
    )
)

delete_restaurant_func = genai.protos.FunctionDeclaration(
    name="delete_restaurant",
    description="Delete a restaurant from the system. Requires authentication. Use this when user wants to remove a restaurant.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "name": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="The name of the restaurant to delete."
            ),
            "token": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Authentication token for the user."
            )
        },
        required=["name", "token"]
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
                description="The name of the restaurant to order from."
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

get_all_orders_func = genai.protos.FunctionDeclaration(
    name="get_all_orders",
    description="Get all orders for the authenticated user. Requires authentication.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "token": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="Authentication token for the user."
            )
        },
        required=["token"]
    )
)

api_tool = genai.protos.Tool(
    function_declarations=[
        all_restaurants_func, 
        restaurant_by_name_func,
        create_restaurant_func,
        update_restaurant_func,
        delete_restaurant_func,
        place_order_func,
        get_all_orders_func
    ]
)

# Initialize model
model = genai.GenerativeModel(
    model_name='models/gemini-1.5-flash', 
    tools=[api_tool]
)

# Store chat sessions per user
chat_sessions = {}

# API Helper Functions
def get_all_restaurants():
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/")
        if response.status_code == 200:
            restaurants = response.json()
            # Format the response to be more readable for the AI
            formatted = []
            for r in restaurants:
                items_list = [f"{item['item_name']} (₹{item.get('price', 'N/A')})" for item in r.get('items', [])]
                formatted.append({
                    "name": r["name"],
                    "area": r["area"],
                    "items": items_list,
                    "item_count": len(r.get('items', []))
                })
            return formatted
        return []
    except Exception as e:
        print(f"Error fetching restaurants: {e}")
        return {"error": str(e)}

def get_restaurant_by_name(name):
    try:
        response = requests.get(f"{API_BASE_URL}/restaurants/{name}")
        if response.status_code == 200:
            return response.json()
        return {"error": "Restaurant not found"}
    except Exception as e:
        return {"error": str(e)}

def create_restaurant(name, area, cuisine, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"name": name, "area": area, "cuisine": cuisine}
        response = requests.post(
            f"{API_BASE_URL}/restaurants/",
            json=data,
            headers=headers
        )
        if response.status_code == 201:
            return response.json()
        return {"error": response.json().get("detail", "Failed to create restaurant")}
    except Exception as e:
        return {"error": str(e)}

def update_restaurant(old_name, new_name, area, cuisine, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"name": new_name, "area": area, "cuisine": cuisine}
        response = requests.put(
            f"{API_BASE_URL}/restaurants/{old_name}",
            json=data,
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Failed to update restaurant")}
    except Exception as e:
        return {"error": str(e)}

def delete_restaurant(name, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(
            f"{API_BASE_URL}/restaurants/{name}",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Failed to delete restaurant")}
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
        return {"error": response.json().get("detail", "Failed to place order")}
    except Exception as e:
        return {"error": str(e)}

def get_all_orders(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/orders/",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Failed to get orders")}
    except Exception as e:
        return {"error": str(e)}

# Routes
@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

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
                    # Check if function requires authentication
                    auth_required_functions = ["place_order", "get_all_orders", "create_restaurant", 
                                              "update_restaurant", "delete_restaurant"]
                    
                    if function_name in auth_required_functions:
                        if not token:
                            action_messages = {
                                "place_order": "place an order",
                                "get_all_orders": "view your orders",
                                "create_restaurant": "create a restaurant",
                                "update_restaurant": "update a restaurant",
                                "delete_restaurant": "delete a restaurant"
                            }
                            action = action_messages.get(function_name, "perform this action")
                            return jsonify({
                                "response": f"🔒 Please login first to {action}! Click the Login button to get started."
                            })
                        function_args['token'] = token
                    
                    # Call the appropriate function with correct arguments
                    try:
                        if function_name == "get_all_restaurants":
                            api_response = available_tools[function_name]()
                        elif function_name == "get_restaurant_by_name":
                            api_response = available_tools[function_name](function_args.get('name'))
                        elif function_name == "create_restaurant":
                            api_response = available_tools[function_name](
                                function_args.get('name'),
                                function_args.get('area'),
                                function_args.get('cuisine'),
                                function_args.get('token')
                            )
                        elif function_name == "update_restaurant":
                            api_response = available_tools[function_name](
                                function_args.get('old_name'),
                                function_args.get('new_name'),
                                function_args.get('area'),
                                function_args.get('cuisine'),
                                function_args.get('token')
                            )
                        elif function_name == "delete_restaurant":
                            api_response = available_tools[function_name](
                                function_args.get('name'),
                                function_args.get('token')
                            )
                        elif function_name == "place_order":
                            api_response = available_tools[function_name](
                                function_args.get('restaurant_name'),
                                function_args.get('item'),
                                function_args.get('token')
                            )
                        elif function_name == "get_all_orders":
                            api_response = available_tools[function_name](
                                function_args.get('token')
                            )
                        else:
                            api_response = {"error": "Unknown function"}
                    except Exception as func_error:
                        api_response = {"error": f"Function execution error: {str(func_error)}"}
                    
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

# Route for popup widget (NEW)
@app.route('/widget')
def widget():
    return send_from_directory(STATIC_DIR, 'popup_widget.html')

if __name__ == '__main__':
    print("🚀 Starting Food Delivery AI Agent Server...")
    print("📡 Full Interface: http://localhost:5000")
    print("🎯 Popup Widget: http://localhost:5000/widget")
    print("🤖 Agent API: http://localhost:5000/chat")
    print("💾 API Backend: http://localhost:8000")
    app.run(debug=True, port=5000)
