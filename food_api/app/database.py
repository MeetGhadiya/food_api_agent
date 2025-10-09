import motor.motor_asyncio
from beanie import init_beanie

# Your actual connection string from Atlas
MONGO_DATABASE_URL = "mongodb+srv://foodapi_user:Meet7805@foodapicluster.6z9sntm.mongodb.net/?retryWrites=true&w=majority&appName=FoodAPICluster"

# Add tlsAllowInvalidCertificates to bypass SSL issues (for development only)
try:
    client = motor.motor_asyncio.AsyncIOMotorClient(
        MONGO_DATABASE_URL, 
        uuidRepresentation="standard",
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000
    )
    database = client.food_db
except Exception as e:
    print(f"Warning: Could not connect to MongoDB: {e}")
    client = None
    database = None

async def init_db():
    if database is not None:
        try:
            await init_beanie(
                database=database,
                document_models=[
                    "app.models.User",
                    "app.models.Restaurant",
                    "app.models.Order",
                ]
            )
            print("✅ Database connection established.")
        except Exception as e:
            print(f"⚠️  WARNING: Could not initialize database: {e}")
            print("⚠️  Running without database - API will have limited functionality")
    else:
        print("⚠️  WARNING: Running without database - API will have limited functionality")
