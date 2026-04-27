import random
import smtplib
import threading
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    VerifyOTPRequest,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = "HS256"
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def send_email(to_email: str, subject: str, html_body: str):
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASS

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        print(f"[DEV MODE] SMTP not configured. Email to {to_email} not sent.")
        print(f"Subject: {subject}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    part = MIMEText(html_body, "html")
    msg.attach(part)

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def send_email_async(to_email: str, subject: str, html_body: str):
    thread = threading.Thread(
        target=send_email, 
        args=(to_email, subject, html_body)
    )
    thread.daemon = True
    thread.start()

def send_welcome_email(to_email: str):
    subject = "Welcome to CodeTrace 🎉"
    html_body = f"""
    <html>
      <body style="background-color:
        <div style="max-width: 600px; margin: 0 auto; background-color:
          <div style="padding: 40px; text-align: center;">
            <h1 style="color:
            <h2 style="font-size: 24px; font-weight: 600; margin-bottom: 10px;">Welcome to CodeTrace!</h2>
            <p style="color:
            
            <div style="background-color:
              <p style="margin: 0; color:
              <p style="margin: 10px 0 0 0; color:
            </div>
            
            <a href="http://localhost:5173/login" style="display: inline-block; background-color:
            
            <hr style="border: 0; border-top: 1px solid
            <p style="color:
            <p style="color:
          </div>
        </div>
      </body>
    </html>
    """
    send_email_async(to_email, subject, html_body)

def send_otp_email(to_email: str, otp: str):
    subject = "Your CodeTrace Verification Code 🔐"
    html_body = f"""
    <html>
      <body style="background-color:
        <div style="max-width: 600px; margin: 0 auto; background-color:
          <div style="padding: 40px; text-align: center;">
            <h1 style="color:
            <h2 style="font-size: 24px; font-weight: 600; margin-bottom: 10px;">Password Reset Request</h2>
            <p style="color:
            
            <div style="background-color:
              <p style="margin: 0; color:
            </div>
            
            <p style="color:
            
            <hr style="border: 0; border-top: 1px solid
            <p style="color:
            <p style="color:
          </div>
        </div>
      </body>
    </html>
    """
    send_email_async(to_email, subject, html_body)
    
    if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER, settings.SMTP_PASS]):
        print(f"[DEV MODE] OTP for {to_email} is {otp}")
@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        is_verified=True,
    )
    db.add(new_user)
    db.commit()

    send_welcome_email(new_user.email)

    return {"message": "Registration successful."}

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "is_verified": user.is_verified,
        }
    )
    return TokenResponse(access_token=access_token)

@router.post("/logout")
def logout():
    return {"message": "Successfully logged out"}

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if user:
        otp = str(random.randint(100000, 999999))
        user.reset_otp = otp
        user.otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        db.commit()

        send_otp_email(user.email, otp)
    return {"message": "If that email is registered, an OTP has been sent."}

@router.post("/verify-otp")
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or user.reset_otp != request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid OTP"
        )

    if not user.otp_expiry or user.otp_expiry < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="OTP has expired"
        )
    user.hashed_password = get_password_hash(request.new_password)
    user.reset_otp = None
    user.otp_expiry = None
    user.is_verified = True
    db.commit()

    return {"message": "Password updated and email verified successfully."}

class ResetPasswordRequest(BaseModel):
    new_password: str

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    return {"message": "Password reset successfully."}
