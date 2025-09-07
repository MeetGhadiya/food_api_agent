# Food API Agent

A RESTful API for managing food items, orders, and user authentication. Designed for seamless integration with frontend applications and third-party services.

## Features

- CRUD operations for food items
- User registration and authentication
- Order management
- Secure endpoints with JWT authentication
- Scalable architecture

## Project Structure

```
food_api/
  app/
    __init__.py
    crud.py
    database.py
    dependencies.py
    main.py
    models.py
    schemas.py
    security.py
  requirements.txt

food_api_agent/
  agent.py
  api_client.py
  requirements.txt
```

## Installation

1. Clone the repository:
   ```
   git clone <your-repo-url>
   ```

2. Navigate to the project directory:
   ```
   cd food_api
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the API server:
   ```
   uvicorn app.main:app --reload
   ```

2. Access the API documentation at:
   ```
   http://localhost:8000/docs
   ```

## API Endpoints

- `/food/` - Manage food items
- `/orders/` - Manage orders
- `/users/` - User registration and authentication

## Agent

The `food_api_agent` directory contains scripts for interacting with the API programmatically.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License.
