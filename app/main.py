from fastapi import FastAPI
from app.routers import user_router
from app.config.db import init_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(user_router.router, prefix="/api", tags=["users"])

app.get("/")
def read_root():
    return {"message": "Welcome to the E-Commerce API"}