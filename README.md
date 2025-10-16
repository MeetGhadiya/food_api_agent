# 🍕 FoodieExpress V4.0 - AI-Powered Food Delivery Platform# 🍕 FoodieExpress V4.0 - AI-Powered Food Delivery Platform# Food API + Agent



[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/MeetGhadiya/food_api_agent)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](docker-compose.yml)[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/MeetGhadiya/food_api_agent)This repository contains a FastAPI-based backend for managing food items, orders and users (`food_api/`) plus a small agent client (`food_api_agent/`) used to interact with the API programmatically.



> A complete, production-ready food delivery platform with AI chatbot, reviews system, admin dashboard, and intelligent recommendations.[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)



---[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](docker-compose.yml)The README here focuses on how to set up and run both components locally (Windows PowerShell examples included).



## 🚀 What's New in V4.0



### ✨ Major Features> A complete, production-ready food delivery platform with AI chatbot, reviews system, admin dashboard, and intelligent recommendations.## Key features

- **🐳 Complete Dockerization** - One-command deployment with `docker-compose up`

- **⭐ Review & Rating System** - Users can review restaurants with social proof

- **👥 Admin Dashboard Backend** - Business intelligence and platform management

- **🤖 AI Personalization** - Context-aware greetings and recommendations---- CRUD operations for food items

- **🔒 Enhanced Security** - RBAC, rate limiting, input validation

- **📊 Business Analytics** - Revenue tracking, user engagement metrics- User registration and JWT-based authentication

- **🏥 Health Monitoring** - Container health checks and observability

## 🚀 What's New in V4.0- Order management endpoints

---

- Small programmatic agent client for scripted interactions

## 📁 Project Structure

### ✨ Major Features

```

food_api_agent-1/## Repo layout

├── docker-compose.yml          # Complete orchestration

├── README.md                   # This file- **🐳 Complete Dockerization** - One-command deployment with `docker-compose up`

│

├── food_api/                   # FastAPI Backend- **⭐ Review & Rating System** - Users can review restaurants and see social proof```

│   ├── app/

│   │   ├── main.py            # API routes and configuration- **👥 Admin Dashboard Backend** - Business intelligence and platform managementfood_api/

│   │   ├── models.py          # Database models

│   │   ├── schemas.py         # Pydantic schemas- **🤖 AI Personalization** - Context-aware greetings and recommendations   app/                # FastAPI application package

│   │   ├── crud.py            # Database operations

│   │   └── security.py        # Authentication & JWT- **🔒 Enhanced Security** - RBAC, rate limiting, input validation   requirements.txt    # dependencies for the API

│   ├── scripts/

│   │   └── make_admin.py      # Admin user creation- **📊 Business Analytics** - Revenue tracking, user engagement metrics

│   ├── tests/                 # API tests

│   └── requirements.txt- **🏥 Health Monitoring** - Container health checks and observabilityfood_api_agent/

│

├── food_chatbot_agent/         # Flask AI Agent   agent.py            # example agent that talks to the API

│   ├── agent.py               # AI chatbot logic

│   └── requirements.txt---   api_client.py       # lightweight client used by the agent

│

├── chatbot_frontend/           # React Frontend   requirements.txt    # dependencies for the agent

│   ├── src/

│   │   └── components/        # UI components## 🐳 Quick Start (Docker) - Recommended   README.md           # this file

│   └── package.json

│```

└── food_api_agent/             # API Client

    ├── agent.py               # Example usage### Prerequisites

    └── api_client.py          # Python client

```## Quick setup (recommended)



---- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running



## 🐳 Quick Start (Docker) - Recommended- 8GB RAM minimum (recommended: 16GB)These steps create isolated virtual environments and install dependencies for both the API and the agent. Examples below use Windows PowerShell.



### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running

- 8GB RAM minimum (recommended: 16GB)### Step 1: Clone and Configure1) Create and activate a venv for the API

- Git



### Step 1: Clone Repository

```powershell```powershell

```powershell

git clone https://github.com/MeetGhadiya/food_api_agent.gitgit clone https://github.com/MeetGhadiya/food_api_agent.gitcd "e:\agent workspace\agent\food_api"

cd food_api_agent-1

```cd food_api_agent-1python -m venv .venv; .\.venv\Scripts\Activate.ps1



### Step 2: Configure Environment Variables```pip install -r requirements.txt



Create a `.env` file in the **root directory**:```



```env### Step 2: Configure Environment Variables

# MongoDB Configuration

# IMPORTANT: Replace with your own MongoDB Atlas credentials2) Create and activate a venv for the agent (in a new shell or after deactivating the API venv)

MONGODB_URI=mongodb+srv://[YOUR_USERNAME]:[YOUR_PASSWORD]@[YOUR_CLUSTER].mongodb.net/[YOUR_DATABASE]?retryWrites=true&w=majority

Create `.env` files:

# JWT Secret Key

# Generate a secure secret key (minimum 32 characters)```powershell

SECRET_KEY=your_super_secret_jwt_key_here_min_32_chars

**Root `.env`:**cd "e:\agent workspace\agent\food_api_agent"

# CORS Configuration

ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:5000```envpython -m venv .venv; .\.venv\Scripts\Activate.ps1



# Optional: Google Gemini API (for AI features)MONGODB_URI=your_mongodb_connection_stringpip install -r requirements.txt

GOOGLE_API_KEY=your_google_gemini_api_key_here

```SECRET_KEY=your_jwt_secret_key```



#### 📝 How to Get MongoDB Connection String:GOOGLE_API_KEY=your_google_gemini_api_key



1. **Sign up for MongoDB Atlas** (Free tier available):ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000Notes:

   - Go to [https://www.mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register)

   - Create a free cluster```- On PowerShell you may need to allow running scripts once: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` (run as Admin if required).



2. **Create Database User**:

   - Navigate to "Database Access"

   - Click "Add New Database User"### Step 3: Start All Services## Environment variables

   - Choose "Password" authentication

   - Set username and password (save these!)



3. **Whitelist IP Address**:```powershellThe API uses a few environment variables for configuration. You can set them in PowerShell before starting the server. Reasonable defaults may already be present in the code, but set them explicitly for production or custom runs:

   - Navigate to "Network Access"

   - Click "Add IP Address"docker-compose up --build

   - For development: Add `0.0.0.0/0` (allows all IPs)

   - For production: Add your specific IP```- DATABASE_URL - SQLAlchemy/DB connection string (e.g. `sqlite:///./test.db` or a full Postgres URL)



4. **Get Connection String**:- SECRET_KEY - JWT secret key

   - Navigate to "Database" → "Connect"

   - Choose "Connect your application"### Step 4: Access the Application- ACCESS_TOKEN_EXPIRE_MINUTES - token expiry (integer)

   - Copy the connection string

   - Replace `<username>`, `<password>`, and `<database>` with your values



**Example:**- **Frontend**: http://localhost:5173Example:

```

mongodb+srv://myuser:mypassword123@mycluster.abc123.mongodb.net/foodie_db?retryWrites=true&w=majority- **API Docs**: http://localhost:8000/docs

```

- **Health Check**: http://localhost:8000/health```powershell

#### 🔑 Generate Secure SECRET_KEY:

$env:DATABASE_URL = 'sqlite:///./dev.db'

**PowerShell:**

```powershell### Step 5: Create Admin User$env:SECRET_KEY = 'replace-this-with-a-secure-secret'

-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

```$env:ACCESS_TOKEN_EXPIRE_MINUTES = '30'



**Python:**```powershell```

```python

python -c "import secrets; print(secrets.token_urlsafe(32))"docker exec -it foodie-backend python scripts/make_admin.py --email your@email.com

```

```## Running the API

### Step 3: Start All Services



```powershell

docker-compose up --build---From the `food_api` folder (with the venv activated):

```



Wait for all containers to start (usually 1-2 minutes).

## 📁 Project Structure```powershell

### Step 4: Access the Application

uvicorn app.main:app --reload

- **Frontend**: [http://localhost:5173](http://localhost:5173)

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)``````

- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

- **AI Chatbot**: [http://localhost:5000](http://localhost:5000)food_api_agent-1/



### Step 5: Create Admin User├── docker-compose.yml          # V4.0: Complete orchestrationThe API will be available at http://127.0.0.1:8000 and the interactive docs at http://127.0.0.1:8000/docs



```powershell├── problems.txt                # V4.0: Development roadmap

docker exec -it foodie-backend python scripts/make_admin.py --email your@email.com

```├── food_api/                   # FastAPI BackendIf you prefer the provided helper scripts at the repo root, there are `start_all.bat` / `start.ps1` which attempt to start services together — inspect them to understand how they wire the components.



---│   ├── app/



## 💻 Manual Setup (Without Docker)│   │   ├── main.py            # Enhanced with reviews & admin## Running the agent



### Prerequisites│   │   ├── models.py          # V4.0: Review model

- Python 3.9+

- Node.js 16+│   │   └── schemas.py         # V4.0: Admin schemasFrom the `food_api_agent` folder (with the venv activated):

- MongoDB Atlas account

│   ├── scripts/

### Backend Setup

│   │   └── make_admin.py      # V4.0: Admin promotion```powershell

1. **Create virtual environment:**

```powershell│   └── tests/python agent.py

cd food_api

python -m venv .venv│       └── test_api_reviews.py # V4.0: Review tests```

.\.venv\Scripts\Activate.ps1

```├── food_chatbot_agent/         # Flask AI Agent



2. **Install dependencies:**│   └── agent.py               # V4.0: Personalized AIThe agent is an example script that uses `api_client.py` to exercise the API (create items, place orders, etc.). Check `agent.py` to see the available actions and modify it for your use-case.

```powershell

pip install -r requirements.txt└── chatbot_frontend/           # React Frontend

```

    └── src/components/## Development notes

3. **Create `.env` file** in `food_api/` folder with MongoDB credentials (see Step 2 above)

        └── ReviewCard.jsx     # V4.0: Review display

4. **Start API:**

```powershell```- The FastAPI app lives in `food_api/app/`. Key files:

uvicorn app.main:app --reload

```   - `main.py` - app factory and route registration



API runs at: [http://127.0.0.1:8000](http://127.0.0.1:8000)---   - `crud.py` - DB access helpers



### Frontend Setup   - `models.py` / `schemas.py` - DB and Pydantic models



1. **Navigate to frontend:**## 📚 API Documentation   - `security.py` - JWT and auth helpers

```powershell

cd chatbot_frontend

```

### V4.0 Review Endpoints- If you change database schemas, update the DB and any seed scripts (`add_dummy_data.py`, `add_via_api.py`).

2. **Install dependencies:**

```powershell

npm install

```| Method | Endpoint | Description | Auth |## Troubleshooting



3. **Start development server:**|--------|----------|-------------|------|

```powershell

npm run dev| POST | `/restaurants/{name}/reviews` | Submit review | Yes |- If imports fail, ensure the venv is activated and you installed `requirements.txt` in the right folder.

```

| GET | `/restaurants/{name}/reviews` | Get reviews | No |- If the API can't connect to the database, verify `DATABASE_URL` and that the database file/host is reachable.

Frontend runs at: [http://localhost:5173](http://localhost:5173)

| PUT | `/reviews/{id}` | Update review | Owner |- For PowerShell script policy errors, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` as Administrator.

### AI Chatbot Setup

| DELETE | `/reviews/{id}` | Delete review | Owner |

1. **Navigate to chatbot:**

```powershell| GET | `/users/me/reviews` | My reviews | Yes |## Next steps / suggestions

cd food_chatbot_agent

```



2. **Create virtual environment:**### V4.0 Admin Endpoints- Add a small Makefile or `tasks.json` for common dev tasks (start api, start agent, run tests).

```powershell

python -m venv .venv- Provide a .env.example file with recommended env vars for local development.

.\.venv\Scripts\Activate.ps1

```| Method | Endpoint | Description | Auth |



3. **Install dependencies:**|--------|----------|-------------|------|## License & Contact

```powershell

pip install -r requirements.txt| GET | `/admin/stats` | Platform statistics | Admin |

```

| GET | `/admin/orders` | All orders | Admin |This repository doesn't include a license file. Add a LICENSE if you plan to publish.

4. **Start chatbot:**

```powershell| GET | `/admin/users` | All users | Admin |

python agent.py

```For questions or to report issues, open an issue in the repository.



Chatbot runs at: [http://localhost:5000](http://localhost:5000)Full documentation: http://localhost:8000/docs



------



## 📚 API Documentation---Updated README to clarify setup and usage for both the API and the agent.



### Authentication Endpoints



| Method | Endpoint | Description | Auth Required |## 🧪 Testing

|--------|----------|-------------|---------------|

| POST | `/register` | Register new user | No |

| POST | `/login` | Login and get JWT token | No |

| GET | `/users/me` | Get current user info | Yes |```powershell

cd food_api

### Restaurant Endpointspytest



| Method | Endpoint | Description | Auth Required |# Run review tests

|--------|----------|-------------|---------------|pytest tests/test_api_reviews.py -v

| GET | `/restaurants/` | List all restaurants | No |

| GET | `/restaurants/{name}` | Get restaurant details | No |# With coverage

| POST | `/restaurants/` | Create restaurant | Admin |pytest --cov=app

| PUT | `/restaurants/{name}` | Update restaurant | Admin |```

| DELETE | `/restaurants/{name}` | Delete restaurant | Admin |

---

### Review Endpoints (V4.0)

## 🐛 Troubleshooting

| Method | Endpoint | Description | Auth Required |

|--------|----------|-------------|---------------|### Docker Issues

| POST | `/restaurants/{name}/reviews` | Submit review | Yes |

| GET | `/restaurants/{name}/reviews` | Get restaurant reviews | No |```powershell

| PUT | `/reviews/{id}` | Update own review | Yes (Owner) |# Check logs

| DELETE | `/reviews/{id}` | Delete own review | Yes (Owner) |docker-compose logs -f

| GET | `/users/me/reviews` | Get my reviews | Yes |

# Rebuild

### Order Endpointsdocker-compose build --no-cache

docker-compose up

| Method | Endpoint | Description | Auth Required |```

|--------|----------|-------------|---------------|

| POST | `/orders/` | Create new order | Yes |### Database Connection

| GET | `/orders/` | Get user's orders | Yes |

| GET | `/orders/{id}` | Get order details | Yes |- Verify `MONGODB_URI` in `.env`

- Check MongoDB Atlas IP whitelist (allow 0.0.0.0/0 for Docker)

### Admin Endpoints (V4.0)

### CORS Errors

| Method | Endpoint | Description | Auth Required |

|--------|----------|-------------|---------------|- Add frontend URL to `ALLOWED_ORIGINS`

| GET | `/admin/stats` | Platform statistics | Admin |- Restart backend

| GET | `/admin/orders` | All orders | Admin |

| GET | `/admin/users` | All users | Admin |---

| POST | `/admin/users/{id}/promote` | Promote to admin | Admin |

## 🤝 Contributing

**Full Interactive Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

1. Fork the repository

---2. Create feature branch

3. Commit changes

## 🧪 Testing4. Push and open Pull Request



### Run All Tests---



```powershell## 📄 License

cd food_api

pytestMIT License - see LICENSE file

```

---

### Run Specific Test Files

## 👨‍💻 Author

```powershell

# Test authentication**Meet Ghadiya**

pytest tests/test_api_auth.py -v- GitHub: [@MeetGhadiya](https://github.com/MeetGhadiya)



# Test reviews---

pytest tests/test_api_reviews.py -v

**Made with ❤️ and 🍕 by the FoodieExpress Team**

# Test security
pytest tests/test_security.py -v
```

### Run with Coverage

```powershell
pytest --cov=app --cov-report=html
```

View coverage report: `htmlcov/index.html`

---

## 🐛 Troubleshooting

### Docker Issues

**Problem**: Containers won't start
```powershell
# Check logs
docker-compose logs -f

# Rebuild without cache
docker-compose build --no-cache
docker-compose up
```

**Problem**: Port already in use
```powershell
# Stop all containers
docker-compose down

# Check what's using the port
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Database Connection Issues

**Problem**: Cannot connect to MongoDB

✅ **Solutions**:
1. Verify `MONGODB_URI` in `.env` file
2. Check MongoDB Atlas IP whitelist (add `0.0.0.0/0` for development)
3. Verify username and password are correct
4. Ensure database name exists in connection string

**Problem**: Authentication failed

✅ **Solutions**:
1. Check database user has read/write permissions
2. Password may contain special characters - URL encode them
3. Verify cluster is not paused (free tier auto-pauses after inactivity)

### CORS Errors

**Problem**: Frontend can't connect to API

✅ **Solutions**:
1. Add frontend URL to `ALLOWED_ORIGINS` in `.env`
2. Restart backend after changing `.env`
3. Clear browser cache

### Python Environment Issues

**Problem**: Module not found errors

✅ **Solutions**:
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Problem**: PowerShell script execution policy

✅ **Solution**:
```powershell
# Run as Administrator
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

## 🔒 Security Best Practices

### ⚠️ IMPORTANT: Never Commit Secrets

- **Never commit** `.env` files to git
- `.gitignore` is configured to exclude `.env` files
- Use placeholders in documentation (like this README)
- Rotate credentials if accidentally exposed

### 🛡️ Production Checklist

Before deploying to production:

- [ ] Generate strong `SECRET_KEY` (minimum 32 characters)
- [ ] Use production-grade MongoDB cluster
- [ ] Restrict MongoDB IP whitelist (remove `0.0.0.0/0`)
- [ ] Enable MongoDB authentication
- [ ] Set strong database passwords
- [ ] Configure HTTPS/SSL
- [ ] Set appropriate `ALLOWED_ORIGINS`
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Regular security audits

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines

- Write tests for new features
- Follow PEP 8 style guide
- Update documentation
- Add docstrings to functions
- Run tests before submitting PR

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 👨‍💻 Author

**Meet Ghadiya**
- GitHub: [@MeetGhadiya](https://github.com/MeetGhadiya)
- Repository: [food_api_agent](https://github.com/MeetGhadiya/food_api_agent)

---

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- MongoDB Atlas for database hosting
- Docker for containerization
- React for the frontend framework

---

## 📞 Support

Having issues? Here's how to get help:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [API Documentation](http://localhost:8000/docs)
3. Open an [Issue](https://github.com/MeetGhadiya/food_api_agent/issues)

---

**Made with ❤️ and 🍕 by the FoodieExpress Team**

---

## 🗺️ Roadmap

- [ ] Payment gateway integration
- [ ] Real-time order tracking
- [ ] Push notifications
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
