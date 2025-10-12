# Food API + Agent

This repository contains a FastAPI-based backend for managing food items, orders and users (`food_api/`) plus a small agent client (`food_api_agent/`) used to interact with the API programmatically.

The README here focuses on how to set up and run both components locally (Windows PowerShell examples included).

## Key features

- CRUD operations for food items
- User registration and JWT-based authentication
- Order management endpoints
- Small programmatic agent client for scripted interactions

## Repo layout

```
food_api/
   app/                # FastAPI application package
   requirements.txt    # dependencies for the API

food_api_agent/
   agent.py            # example agent that talks to the API
   api_client.py       # lightweight client used by the agent
   requirements.txt    # dependencies for the agent
   README.md           # this file
```

## Quick setup (recommended)

These steps create isolated virtual environments and install dependencies for both the API and the agent. Examples below use Windows PowerShell.

1) Create and activate a venv for the API

```powershell
cd "e:\agent workspace\agent\food_api"
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Create and activate a venv for the agent (in a new shell or after deactivating the API venv)

```powershell
cd "e:\agent workspace\agent\food_api_agent"
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Notes:
- On PowerShell you may need to allow running scripts once: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` (run as Admin if required).

## Environment variables

The API uses a few environment variables for configuration. You can set them in PowerShell before starting the server. Reasonable defaults may already be present in the code, but set them explicitly for production or custom runs:

- DATABASE_URL - SQLAlchemy/DB connection string (e.g. `sqlite:///./test.db` or a full Postgres URL)
- SECRET_KEY - JWT secret key
- ACCESS_TOKEN_EXPIRE_MINUTES - token expiry (integer)

Example:

```powershell
$env:DATABASE_URL = 'sqlite:///./dev.db'
$env:SECRET_KEY = 'replace-this-with-a-secure-secret'
$env:ACCESS_TOKEN_EXPIRE_MINUTES = '30'
```

## Running the API

From the `food_api` folder (with the venv activated):

```powershell
uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000 and the interactive docs at http://127.0.0.1:8000/docs

If you prefer the provided helper scripts at the repo root, there are `start_all.bat` / `start.ps1` which attempt to start services together — inspect them to understand how they wire the components.

## Running the agent

From the `food_api_agent` folder (with the venv activated):

```powershell
python agent.py
```

The agent is an example script that uses `api_client.py` to exercise the API (create items, place orders, etc.). Check `agent.py` to see the available actions and modify it for your use-case.

## Development notes

- The FastAPI app lives in `food_api/app/`. Key files:
   - `main.py` - app factory and route registration
   - `crud.py` - DB access helpers
   - `models.py` / `schemas.py` - DB and Pydantic models
   - `security.py` - JWT and auth helpers

- If you change database schemas, update the DB and any seed scripts (`add_dummy_data.py`, `add_via_api.py`).

## Troubleshooting

- If imports fail, ensure the venv is activated and you installed `requirements.txt` in the right folder.
- If the API can't connect to the database, verify `DATABASE_URL` and that the database file/host is reachable.
- For PowerShell script policy errors, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` as Administrator.

## Next steps / suggestions

- Add a small Makefile or `tasks.json` for common dev tasks (start api, start agent, run tests).
- Provide a .env.example file with recommended env vars for local development.

## License & Contact

This repository doesn't include a license file. Add a LICENSE if you plan to publish.

For questions or to report issues, open an issue in the repository.

---
Updated README to clarify setup and usage for both the API and the agent.



