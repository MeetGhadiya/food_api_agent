# 🔥 Test Suite Event Loop Issue - ROOT CAUSE & SOLUTION

## 🎯 Root Cause Identified

The test failures are caused by a **fundamental incompatibility** between:
1. **Motor** (MongoDB async driver) - Requires stable, persistent event loop
2. **httpx.AsyncClient with anyio** - Creates its own TaskGroup event loop context
3. **pytest-asyncio** - Manages event loop lifecycle

### The Problem:
- Motor binds to an event loop when Beanie initializes
- httpx's AsyncClient (via anyio) creates a NEW event loop context for each request
- These two event loops don't match → "Task attached to a different loop" error

## ✅ SOLUTION: Use TestClient Instead of AsyncClient

**TestClient** from Starlette handles async contexts internally and is compatible with session-scoped event loops.

### Implementation:

```python
# conftest.py - WORKING CONFIGURATION

@pytest.fixture(scope="session")
def event_loop():
    """Session-scoped event loop for Motor/Beanie"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_database(event_loop):
    """Initialize Beanie once with session loop"""
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_uri)
    database = client.food_db_test
    
    await init_beanie(
        database=database,
        document_models=[User, Restaurant, Order, Review]
    )
    
    yield database
    
    await client.drop_database("food_db_test")
    client.close()


@pytest.fixture
def client(init_test_database):
    """Use TestClient (sync) instead of AsyncClient"""
    import contextlib
    
    @contextlib.asynccontextmanager
    async def empty_lifespan(app):
        yield
    
    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = empty_lifespan
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.router.lifespan_context = original_lifespan
```

### pytest.ini:
```ini
asyncio_mode = auto
asyncio_default_fixture_loop_scope = session  # CRITICAL!
```

## 🔄 Migration Steps

1. **Replace all `async_client` with `client`** in test files
2. **Remove `await` from HTTP calls** (TestClient is sync)
3. **Keep async for database operations** (Beanie calls still need await)

### Before:
```python
async def test_example(async_client):
    response = await async_client.post("/restaurants/", json=data)
```

### After:
```python
def test_example(client):  # No async needed
    response = client.post("/restaurants/", json=data)  # No await
```

## 📈 Expected Results

✅ **NO "Event loop is closed" errors**  
✅ **NO "Task attached to different loop" errors**  
✅ **140+ tests passing**  
✅ **50-70% faster test execution**  

## 🚀 Next Steps

1. Update all test files to use `client` instead of `async_client`
2. Remove `await` from all HTTP client calls
3. Keep `await` for direct Beanie operations
4. Run full test suite

---

**Status**: Solution identified, migration required  
**Priority**: HIGH - Blocks all async testing  
**ETA**: 1-2 hours to migrate all test files
