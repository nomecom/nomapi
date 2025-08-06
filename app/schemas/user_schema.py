from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreateRequestSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone:Optional[str] = None
    domain:str
    
class UserCreateResponseSchema(BaseModel):
    message: str
    
class UserFetchRequestSchema(BaseModel):
    email: EmailStr
    password: str