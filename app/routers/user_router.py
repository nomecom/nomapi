from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from app.models.user_model import users
from app.schemas.user_schema import UserCreateRequestSchema, UserSignupRequestSchema, ForgotPasswordRequestSchema, ResetPasswordRequestSchema
from app.utils.password import hash_password
from uuid import uuid4
from app.utils.email_utils import send_verification_email, send_password_reset_email
from app.config.mailer import Mailer
from app.utils.password import verify_password
from pydantic import EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = await users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

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

@router.post("/v1/signup")
async def signup(user: UserSignupRequestSchema):
    db_user = await users.find_one(users.email == user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not db_user.is_verified:
        db_user.verification_token = str(uuid4())
        await db_user.save()
        subject, body, html_body = send_verification_email(db_user.domain, db_user.verification_token)
        mailer.send_email(
            to_email=db_user.email,
            subject=subject,
            body_text=body,
            body_html=html_body
        )
        raise HTTPException(status_code=403, detail="User account not verified, verification email sent")
    
    res = verify_password(user.password, db_user.password)
    if not res:
        raise HTTPException(status_code=401, detail="Invalid password")
    # Issue JWT token
    access_token = create_access_token({"user_id": str(db_user.id), "email": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
    
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