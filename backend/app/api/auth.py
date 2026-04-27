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

import os

def send_email(to: str, subject: str, html_body: str):
    try:
        SMTP_HOST = settings.SMTP_HOST
        SMTP_PORT = settings.SMTP_PORT
        SMTP_USER = settings.SMTP_USER
        SMTP_PASS = settings.SMTP_PASS

        if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS]):
            print(f"[DEV MODE] Email to {to}: {subject}")
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"CodeTrace <{SMTP_USER}>"
        msg["To"] = to

        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(html_part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to, msg.as_string())
            
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

def send_email_async(to: str, subject: str, html_body: str):
    thread = threading.Thread(
        target=send_email,
        args=(to, subject, html_body)
    )
    thread.daemon = True
    thread.start()

def send_welcome_email(to_email: str):
    subject = "Welcome to CodeTrace 🎉"
    html_body = f"""
    <html>
      <body style="background-color: #0d0d14; color: #ffffff; font-family: sans-serif; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #12121a; border: 1px solid #1e1e2e; border-radius: 16px; overflow: hidden;">
          <div style="padding: 40px; text-align: center;">
            <h1 style="color: #00ff9f; font-size: 28px; font-weight: 900; margin: 0; letter-spacing: -1px; white-space: nowrap;">CodeTrace</h1>
            <h2 style="font-size: 24px; font-weight: 600; margin-bottom: 10px; margin-top: 20px;">Welcome to CodeTrace!</h2>
            <p style="color: #8888aa; line-height: 1.6; margin-bottom: 30px;">
              Thank you for joining CodeTrace. Our advanced AST and Winnowing-based engine is ready to help you analyze and protect your codebase.
            </p>
            
            <div style="background-color: rgba(0, 255, 159, 0.1); border: 1px solid rgba(0, 255, 159, 0.2); border-radius: 12px; padding: 20px; margin-bottom: 30px;">
              <p style="margin: 0; color: #00ff9f; font-size: 16px; font-weight: 600;">Account Successfully Created</p>
              <p style="margin: 10px 0 0 0; color: #8888aa; font-size: 14px;">You can now log in to the dashboard and start your first code analysis.</p>
            </div>
            
            <a href="https://codetrace.vercel.app/login" style="display: inline-block; background-color: #00ff9f; color: #0a0a0f; text-decoration: none; font-weight: 700; padding: 14px 28px; border-radius: 12px; font-size: 16px;">Go to Dashboard</a>
            
            <hr style="border: 0; border-top: 1px solid #1e1e2e; margin: 40px 0 20px;" />
            <p style="color: #8888aa; font-size: 12px; margin: 0;">If you didn't create this account, please ignore this email.</p>
            <p style="color: #8888aa; font-size: 12px; margin: 5px 0 0;">© {datetime.now().year} CodeTrace. All rights reserved.</p>
          </div>
        </div>
      </body>
    </html>
    """
    send_email_async(to_email, subject, html_body)

def send_otp_email(to: str, otp: str):
    html = f"""
    <html>
    <body style="margin:0;padding:0;background-color:#0a0a0f;font-family:Arial,sans-serif;">
      <div style="max-width:500px;margin:40px auto;background-color:#12121a;border-radius:12px;padding:40px;border:1px solid #1e1e2e;">
        <h1 style="color:#00ff9f;text-align:center;font-size:28px;margin-bottom:8px;">CodeTrace</h1>
        <p style="color:#888;text-align:center;margin-bottom:32px;">Code Plagiarism Detection System</p>
        <h2 style="color:#ffffff;text-align:center;">Password Reset Request</h2>
        <p style="color:#aaa;text-align:center;">Use the code below to reset your password.</p>
        <div style="background-color:#0d0d14;border:2px solid #00ff9f;border-radius:8px;padding:24px;text-align:center;margin:24px 0;">
          <span style="color:#00ff9f;font-size:48px;font-weight:bold;letter-spacing:12px;">{otp}</span>
        </div>
        <p style="color:#ff4444;text-align:center;">This code expires in 10 minutes.</p>
        <p style="color:#666;text-align:center;font-size:12px;">If you didn't request this, ignore this email.</p>
        <hr style="border:0;border-top:1px solid #1e1e2e;margin:24px 0;">
        <p style="color:#444;text-align:center;font-size:12px;">CodeTrace - Code Plagiarism Detection System</p>
      </div>
    </body>
    </html>
    """
    send_email_async(to, "Your CodeTrace Verification Code 🔐", html)
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
