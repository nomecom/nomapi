from fastapi import APIRouter, HTTPException
from app.models.user_model import users
from app.schemas.user_schema import UserCreateRequestSchema
from app.utils.password import hash_password
from uuid import uuid4
from app.utils.email_utils import send_verification_email
from app.config.mailer import Mailer

mailer = Mailer()
router = APIRouter()

@router.post("/v1/user")
async def create_user(user: UserCreateRequestSchema):
    existing_user = await users.find_one(users.email == user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    hashed_password = hash_password(user.password)
    
    new_user = users(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
        phone=user.phone,
        is_verified=False,
        verification_token=str(uuid4())
    )
    
    new_user = await new_user.insert()
    
    subject, body, html_body = send_verification_email(new_user.verification_token)
    mailer.send_email(
        to_email=new_user.email,
        subject=subject,
        body_text=body,
        body_html=html_body
    )
        
    print(f"New user created: {new_user}")
    if not new_user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return{"message": "User created successfully"}

@router.get("/v1/verify_account")
async def verify_account(token:str):
    print(token)
    user = await users.find_one({"verification_token": token})
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="Invalid verification token")
    
    user.is_verified = True
    user.verification_token = None
    await user.save()
    
    return {"message": "Account verified successfully"}