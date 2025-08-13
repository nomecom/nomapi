from beanie import Document
from pydantic import EmailStr, Field, BaseModel
from typing import Optional
from uuid import UUID,uuid4
from datetime import datetime, timedelta


class users(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    full_name: str
    email: EmailStr
    password: str
    is_verified: Optional[bool] = False
    verification_token: str
    reset_password_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    phone: Optional[str] = None
    domain: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "users"