import motor.motor_asyncio
from beanie import init_beanie

# Your actual connection string from Atlas
MONGO_DATABASE_URL = "mongodb+srv://foodapi_user:{{Password}}@foodapicluster.6z9sntm.mongodb.net/?retryWrites=true&w=majority&appName=FoodAPICluster"

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGO_DATABASE_URL, uuidRepresentation="standard"
)

database = client.food_db

async def init_db():
    await init_beanie(
        database=database,
        document_models=[
            "app.models.User",
            "app.models.Restaurant",
            "app.models.Order",
        ]

    )
