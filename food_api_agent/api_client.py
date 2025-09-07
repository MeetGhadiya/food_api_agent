# Import the 'requests' library, which is the standard for making HTTP requests in Python.
import requests

# Define a constant for the base URL of your FastAPI server.
# This makes it easy to change the server address in one place if needed.
BASE_URL = "http://127.0.0.1:8000"

def login(username, password):
    """Logs in a user and returns the access token."""
    # Prepare the data in a dictionary format that the login endpoint expects.
    login_data = {"username": username, "password": password}
    try:
        # Send an HTTP POST request to the /users/login endpoint.
        # Use the 'data' parameter to send the payload as form data (x-www-form-urlencoded).
        response = requests.post(f"{BASE_URL}/users/login", data=login_data)
        # Check if the response status code is an error (4xx or 5xx). If so, raise an exception.
        response.raise_for_status()
        # If the request was successful, parse the JSON response and return the 'access_token' value.
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        # If any network error or bad HTTP status occurs, print an error and return None.
        print(f"Login failed: {e}")
        return None

def get_all_restaurants():
    """Fetches a list of all restaurants from the API."""
    try:
        # Send an HTTP GET request to the /restaurants/ endpoint.
        response = requests.get(f"{BASE_URL}/restaurants/")
        # Raise an exception for any HTTP errors.
        response.raise_for_status()  
        # Return the JSON data (a list of restaurants) from the successful response.
        return response.json()
    except requests.exceptions.RequestException as e:
        # If the request fails, return a formatted error string.
        return f"An error occurred while connecting to the API: {e}"

def get_restaurant_by_name(name: str):
    """Fetches a single restaurant by its specific name from the API."""
    try:
        # Send an HTTP GET request, including the restaurant name in the URL path.
        response = requests.get(f"{BASE_URL}/restaurants/{name}")
        # Raise an exception for any HTTP errors.
        response.raise_for_status()
        # Return the JSON data (a single restaurant's details) from the successful response.
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle errors gracefully. Specifically check if the error was a 404 Not Found.
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
            # Return a user-friendly "not found" message.
            return f"Sorry, the restaurant '{name}' could not be found."
        # For all other errors, return a generic error message.
        return f"An error occurred while connecting to the API: {e}"

def place_order(restaurant_name: str, item: str, token: str):
    """Places a food order for a specific item from a restaurant."""
    # Prepare the request headers to include the JWT for authentication.
    headers = {"Authorization": f"Bearer {token}"}
    # Prepare the JSON payload with the order details.
    order_data = {"restaurant_name": restaurant_name, "item": item}
    
    try:
        # Send an HTTP POST request to the /orders/ endpoint.
        # Use the 'json' parameter to send the payload as a JSON object.
        # Include the authorization headers.
        response = requests.post(f"{BASE_URL}/orders/", json=order_data, headers=headers)
        # Raise an exception for any HTTP errors.
        response.raise_for_status()
        # Return the JSON data (the newly created order) from the successful response.
        return response.json()
    except requests.exceptions.RequestException as e:
        # If the request fails, return a formatted error string.
        return f"An error occurred: {e}"