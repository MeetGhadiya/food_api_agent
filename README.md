# 🍕 FoodieExpress V4.0 - AI-Powered Food Delivery Platform# Food API + Agent



[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/MeetGhadiya/food_api_agent)This repository contains a FastAPI-based backend for managing food items, orders and users (`food_api/`) plus a small agent client (`food_api_agent/`) used to interact with the API programmatically.

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](docker-compose.yml)The README here focuses on how to set up and run both components locally (Windows PowerShell examples included).



> A complete, production-ready food delivery platform with AI chatbot, reviews system, admin dashboard, and intelligent recommendations.## Key features



---- CRUD operations for food items

- User registration and JWT-based authentication

## 🚀 What's New in V4.0- Order management endpoints

- Small programmatic agent client for scripted interactions

### ✨ Major Features

## Repo layout

- **🐳 Complete Dockerization** - One-command deployment with `docker-compose up`

- **⭐ Review & Rating System** - Users can review restaurants and see social proof```

- **👥 Admin Dashboard Backend** - Business intelligence and platform managementfood_api/

- **🤖 AI Personalization** - Context-aware greetings and recommendations   app/                # FastAPI application package

- **🔒 Enhanced Security** - RBAC, rate limiting, input validation   requirements.txt    # dependencies for the API

- **📊 Business Analytics** - Revenue tracking, user engagement metrics

- **🏥 Health Monitoring** - Container health checks and observabilityfood_api_agent/

   agent.py            # example agent that talks to the API

---   api_client.py       # lightweight client used by the agent

   requirements.txt    # dependencies for the agent

## 🐳 Quick Start (Docker) - Recommended   README.md           # this file

```

### Prerequisites

## Quick setup (recommended)

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running

- 8GB RAM minimum (recommended: 16GB)These steps create isolated virtual environments and install dependencies for both the API and the agent. Examples below use Windows PowerShell.



### Step 1: Clone and Configure1) Create and activate a venv for the API



```powershell```powershell

git clone https://github.com/MeetGhadiya/food_api_agent.gitcd "e:\agent workspace\agent\food_api"

cd food_api_agent-1python -m venv .venv; .\.venv\Scripts\Activate.ps1

```pip install -r requirements.txt

```

### Step 2: Configure Environment Variables

2) Create and activate a venv for the agent (in a new shell or after deactivating the API venv)

Create `.env` files:

```powershell

**Root `.env`:**cd "e:\agent workspace\agent\food_api_agent"

```envpython -m venv .venv; .\.venv\Scripts\Activate.ps1

MONGODB_URI=your_mongodb_connection_stringpip install -r requirements.txt

SECRET_KEY=your_jwt_secret_key```

GOOGLE_API_KEY=your_google_gemini_api_key

ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000Notes:

```- On PowerShell you may need to allow running scripts once: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` (run as Admin if required).



### Step 3: Start All Services## Environment variables



```powershellThe API uses a few environment variables for configuration. You can set them in PowerShell before starting the server. Reasonable defaults may already be present in the code, but set them explicitly for production or custom runs:

docker-compose up --build

```- DATABASE_URL - SQLAlchemy/DB connection string (e.g. `sqlite:///./test.db` or a full Postgres URL)

- SECRET_KEY - JWT secret key

### Step 4: Access the Application- ACCESS_TOKEN_EXPIRE_MINUTES - token expiry (integer)



- **Frontend**: http://localhost:5173Example:

- **API Docs**: http://localhost:8000/docs

- **Health Check**: http://localhost:8000/health```powershell

$env:DATABASE_URL = 'sqlite:///./dev.db'

### Step 5: Create Admin User$env:SECRET_KEY = 'replace-this-with-a-secure-secret'

$env:ACCESS_TOKEN_EXPIRE_MINUTES = '30'

```powershell```

docker exec -it foodie-backend python scripts/make_admin.py --email your@email.com

```## Running the API



---From the `food_api` folder (with the venv activated):



## 📁 Project Structure```powershell

uvicorn app.main:app --reload

``````

food_api_agent-1/

├── docker-compose.yml          # V4.0: Complete orchestrationThe API will be available at http://127.0.0.1:8000 and the interactive docs at http://127.0.0.1:8000/docs

├── problems.txt                # V4.0: Development roadmap

├── food_api/                   # FastAPI BackendIf you prefer the provided helper scripts at the repo root, there are `start_all.bat` / `start.ps1` which attempt to start services together — inspect them to understand how they wire the components.

│   ├── app/

│   │   ├── main.py            # Enhanced with reviews & admin## Running the agent

│   │   ├── models.py          # V4.0: Review model

│   │   └── schemas.py         # V4.0: Admin schemasFrom the `food_api_agent` folder (with the venv activated):

│   ├── scripts/

│   │   └── make_admin.py      # V4.0: Admin promotion```powershell

│   └── tests/python agent.py

│       └── test_api_reviews.py # V4.0: Review tests```

├── food_chatbot_agent/         # Flask AI Agent

│   └── agent.py               # V4.0: Personalized AIThe agent is an example script that uses `api_client.py` to exercise the API (create items, place orders, etc.). Check `agent.py` to see the available actions and modify it for your use-case.

└── chatbot_frontend/           # React Frontend

    └── src/components/## Development notes

        └── ReviewCard.jsx     # V4.0: Review display

```- The FastAPI app lives in `food_api/app/`. Key files:

   - `main.py` - app factory and route registration

---   - `crud.py` - DB access helpers

   - `models.py` / `schemas.py` - DB and Pydantic models

## 📚 API Documentation   - `security.py` - JWT and auth helpers



### V4.0 Review Endpoints- If you change database schemas, update the DB and any seed scripts (`add_dummy_data.py`, `add_via_api.py`).



| Method | Endpoint | Description | Auth |## Troubleshooting

|--------|----------|-------------|------|

| POST | `/restaurants/{name}/reviews` | Submit review | Yes |- If imports fail, ensure the venv is activated and you installed `requirements.txt` in the right folder.

| GET | `/restaurants/{name}/reviews` | Get reviews | No |- If the API can't connect to the database, verify `DATABASE_URL` and that the database file/host is reachable.

| PUT | `/reviews/{id}` | Update review | Owner |- For PowerShell script policy errors, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` as Administrator.

| DELETE | `/reviews/{id}` | Delete review | Owner |

| GET | `/users/me/reviews` | My reviews | Yes |## Next steps / suggestions



### V4.0 Admin Endpoints- Add a small Makefile or `tasks.json` for common dev tasks (start api, start agent, run tests).

- Provide a .env.example file with recommended env vars for local development.

| Method | Endpoint | Description | Auth |

|--------|----------|-------------|------|## License & Contact

| GET | `/admin/stats` | Platform statistics | Admin |

| GET | `/admin/orders` | All orders | Admin |This repository doesn't include a license file. Add a LICENSE if you plan to publish.

| GET | `/admin/users` | All users | Admin |

For questions or to report issues, open an issue in the repository.

Full documentation: http://localhost:8000/docs

---

---Updated README to clarify setup and usage for both the API and the agent.



## 🧪 Testing



```powershell
cd food_api
pytest

# Run review tests
pytest tests/test_api_reviews.py -v

# With coverage
pytest --cov=app
```

---

## 🐛 Troubleshooting

### Docker Issues

```powershell
# Check logs
docker-compose logs -f

# Rebuild
docker-compose build --no-cache
docker-compose up
```

### Database Connection

- Verify `MONGODB_URI` in `.env`
- Check MongoDB Atlas IP whitelist (allow 0.0.0.0/0 for Docker)

### CORS Errors

- Add frontend URL to `ALLOWED_ORIGINS`
- Restart backend

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push and open Pull Request

---

## 📄 License

MIT License - see LICENSE file

---

## 👨‍💻 Author

**Meet Ghadiya**
- GitHub: [@MeetGhadiya](https://github.com/MeetGhadiya)

---

**Made with ❤️ and 🍕 by the FoodieExpress Team**
