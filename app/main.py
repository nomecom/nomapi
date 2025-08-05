from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- Import CORS middleware
from app.routers import user_router
from app.config.db import init_db

app = FastAPI()

# ===== CORS SETUP =====
# Allow all origins (replace "*" with specific domains in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(user_router.router, prefix="/api", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the E-Commerce API"}