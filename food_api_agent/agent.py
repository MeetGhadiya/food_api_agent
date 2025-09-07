import os
import sys
import msvcrt
import google.generativeai as genai
from dotenv import load_dotenv

from api_client import get_all_restaurants, get_restaurant_by_name, place_order, login

def get_masked_password(prompt="Password: "):
    print(prompt, end='', flush=True)
    password = ""
    while True:
        char = msvcrt.getch().decode('utf-8', errors='ignore')
        if char == '\r' or char == '\n':
            print()
            break
        if char == '\x08':
            if len(password) > 0:
                password = password[:-1]
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        else:
            password += char
            sys.stdout.write('*')
            sys.stdout.flush()
    return password

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found.")
genai.configure(api_key=api_key)

available_tools = {
    "get_all_restaurants": get_all_restaurants,
    "get_restaurant_by_name": get_restaurant_by_name,
    "place_order": place_order,
}
all_restaurants_func = genai.protos.FunctionDeclaration(
    name="get_all_restaurants", 
    description="Get a list of all available restaurants."
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
    description="Use this function to place a food order for a specific item from a restaurant.", 
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
            )
        }, 
        required=["restaurant_name", "item"]
    )
)
api_tool = genai.protos.Tool(
    function_declarations=[all_restaurants_func, 
                           restaurant_by_name_func, 
                           place_order_func]
)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash', 
    tools=[api_tool]
)

print("🤖 To get started, please log in.")
username = input("Username: ")
password = get_masked_password()
session_token = login(username, password)
if not session_token:
    print("Login failed. Exiting.")
    exit()

chat = model.start_chat()
print("\n✅ Login successful! How can I help you today?")
print("   (Type 'quit' to exit)")

while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        print("THANK YOU FOR USING THE FOOD DELIVERY AGENT!")
        break

    response = chat.send_message(user_input)
    
    try:
        response_message = response.candidates[0].content
        if response_message.parts and response_message.parts[0].function_call:
            fc = response_message.parts[0].function_call
            function_name = fc.name
            function_args = {key: value for key, value in fc.args.items()}

            if function_name in available_tools:
                function_to_call = available_tools[function_name]
                
                if function_name == "place_order":
                    function_args['token'] = session_token
                
                api_response = function_to_call(**function_args)
                
                response = chat.send_message(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=function_name,
                            response={"result": str(api_response)}
                        )
                    )
                )
    except (ValueError, IndexError):
        pass

    try:
        if response.text:
            print(f"Agent: {response.text}")
        else:
            print("Agent: I'm sorry, I seem to have gotten stuck. Could you please rephrase?")
    except ValueError:
        print("Agent: I'm sorry, I got a response I didn't understand. Please try again.")