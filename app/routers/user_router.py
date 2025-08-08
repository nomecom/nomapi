from fastapi import APIRouter, HTTPException
from app.models.user_model import users
from app.schemas.user_schema import UserCreateRequestSchema, ForgotPasswordRequestSchema, ResetPasswordRequestSchema
from app.utils.password import hash_password
from uuid import uuid4
from app.utils.email_utils import send_verification_email, send_password_reset_email
from app.config.mailer import Mailer
from app.utils.password import verify_password
from pydantic import EmailStr
from datetime import datetime, timedelta

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
        domain=user.domain,
        verification_token=str(uuid4())
    )
    
    new_user = await new_user.insert()
    
    subject, body, html_body = send_verification_email(user.domain,new_user.verification_token)
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
async def verify_account(token: str):
    try:
        print(token)
        user = await users.find_one({"verification_token": token})
        print(user)
        if not user:
            raise HTTPException(status_code=404, detail="Invalid verification token")
        
        user.is_verified = True
        user.verification_token = ""
        await user.save()
        
        return {"message": "Account verified successfully"}
    except Exception as e:
        raise e

@router.get("/v1/user")
async def get_user(email:EmailStr, password:str):
    user = await users.find_one(users.email == email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_verified:
        user.verification_token = str(uuid4())
        await user.save()
        subject, body, html_body = send_verification_email(user.domain, user.verification_token)
        mailer.send_email(
            to_email=email,
            subject=subject,
            body_text=body,
            body_html=html_body
        )
        raise HTTPException(status_code=403, detail="User account not verified, verification email sent")
    
    res = verify_password(password, user.password)
    if not res:
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"message": "User fetched successfully"}
    
@router.post("/v1/forgot_password")
async def forgot_password(request: ForgotPasswordRequestSchema):
    user = await users.find_one(users.email == request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate reset token and set expiration (1 hour from now)
    reset_token = str(uuid4())
    reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    
    user.reset_password_token = reset_token
    user.reset_token_expires = reset_token_expires
    await user.save()
    
    # Send password reset email
    subject, body, html_body = send_password_reset_email(user.domain, reset_token)
    mailer.send_email(
        to_email=user.email,
        subject=subject,
        body_text=body,
        body_html=html_body
    )
    
    return {"message": "Email sent successfully"}

@router.post("/v1/reset_password")
async def reset_password(request: ResetPasswordRequestSchema):
    # Find user by reset token
    user = await users.find_one({"reset_password_token": request.token})
    if not user:
        raise HTTPException(status_code=404, detail="Invalid reset token")
    
    # Check if token has expired
    if user.reset_token_expires and datetime.utcnow() > user.reset_token_expires:
        # Clear expired token
        user.reset_password_token = None
        user.reset_token_expires = None
        await user.save()
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Hash the new password
    hashed_password = hash_password(request.new_password)
    
    # Update user password and clear reset token
    user.password = hashed_password
    user.reset_password_token = None
    user.reset_token_expires = None
    await user.save()
    
    return {"message": "Password reset successfully"}