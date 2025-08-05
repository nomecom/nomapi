from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user_model import users

from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

async def init_db():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["nom-ecom"]
    
    # Debug output
    print(f"Connecting to: {MONGO_URL}")
    print(f"Database name: {db.name}")
    print("Existing collections:", await db.list_collection_names())
    
    await init_beanie(database=db, document_models=[users])
    
    # Verify post-init
    print("Post-init collections:", await db.list_collection_names())
    print(f"Confirmed UserModel collection: {users.get_collection_name()}")