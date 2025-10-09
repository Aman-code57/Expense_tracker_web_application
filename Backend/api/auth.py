from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import re
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jose import jwt
from database import get_db
from models import User
from core.security import verify_password, get_password_hash, create_access_token, create_reset_token, validate_email, validate_mobile, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from core.config import SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASSWORD
from crud.user_crud import create_user, get_user_by_email, get_user_by_email_or_mobile, update_user_reset_token, update_user_password

router = APIRouter()

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def send_email_bg(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()
        print(f"[INFO] Email sent to {to_email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {str(e)}")

@router.post("/signup")
async def signup(user_data: dict, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        fullname = user_data.get("fullname", "").strip()
        email = user_data.get("email", "").strip().lower()
        gender = user_data.get("gender", "").strip()
        mobilenumber = user_data.get("mobilenumber", "").strip()
        password = user_data.get("password", "")

        errors = {}

        if not fullname or len(fullname) < 3 or len(fullname) > 100:
            errors["fullname"] = "Full name must be 3-100 characters"
        elif not re.match(r"^[A-Za-z\s]+$", fullname):
            errors["fullname"] = "Full name can only contain letters and spaces"

        if not email or not validate_email(email):
            errors["email"] = "Valid email is required"

        if not gender:
            errors["gender"] = "Gender is required"

        if not mobilenumber or not validate_mobile(mobilenumber):
            errors["mobilenumber"] = "Valid 10-digit mobile number is required"

        if not password or len(password) < 6:
            errors["password"] = "Password must be at least 6 characters"
        elif not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            errors["password"] = "Password must contain at least 1 letter and 1 number"

        existing_user = get_user_by_email_or_mobile(db, email, mobilenumber)

        if existing_user:
            if existing_user.email == email:
                errors["email"] = "Email already registered"
            if existing_user.mobilenumber == mobilenumber:
                errors["mobilenumber"] = "Mobile number already registered"

        if errors:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Validation failed", "errors": errors})

        hashed_password = get_password_hash(password)
        new_user = create_user(db, fullname, email, gender, mobilenumber, hashed_password)

        return JSONResponse(status_code=201, content={"status": "success", "message": "User registered successfully", "user_id": new_user.id})
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Registration failed: {str(e)}"})

@router.post("/signin")
async def signin(credentials: dict, db: Session = Depends(get_db)):
    try:
        email = credentials.get("email", "").strip().lower()
        password = credentials.get("password", "")
        if not email or not password:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Email and password are required"})

        user = get_user_by_email(db, email)
        if not user or not verify_password(password, user.password):
            return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid email or password"})

        access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return JSONResponse(status_code=200, content={"status": "success", "message": "Login successful", "access_token": access_token, "user": {"id": user.id, "fullname": user.fullname, "email": user.email, "gender": user.gender}})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Login failed: {str(e)}"})

@router.post("/forgot-password")
async def forgot_password(request: dict, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        email = request.get("email", "").strip().lower()
        if not email or not validate_email(email):
            return JSONResponse(status_code=400, content={"status": "error", "message": "Valid email is required"})

        user = get_user_by_email(db, email)
        if not user:
            return JSONResponse(status_code=404, content={"status": "error", "message": "User not found"})

        reset_token = create_reset_token(data={"sub": user.email})
        update_user_reset_token(db, user, reset_token, datetime.utcnow() + timedelta(hours=1))

        if background_tasks:
            background_tasks.add_task(
                send_email_bg,
                user.email,
                "Password Reset Request",
                f"Click to reset password: http://localhost:5173/reset-password?token={reset_token}"
            )

        return JSONResponse(status_code=200, content={"status": "success", "message": "Password reset link sent!"})
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error: {str(e)}"})

@router.post("/send-otp")
async def send_otp(request: dict, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        email = request.get("email", "").strip().lower()
        if not email or not validate_email(email):
            return JSONResponse(status_code=400, content={"status": "error", "message": "Valid email is required"})

        user = get_user_by_email(db, email)
        if not user:
            return JSONResponse(status_code=404, content={"status": "error", "message": "User not found"})

        otp = generate_otp()
        update_user_reset_token(db, user, otp, datetime.utcnow() + timedelta(minutes=10))

        if background_tasks:
            background_tasks.add_task(
                send_email_bg,
                user.email,
                "OTP for Password Reset",
                f"Your OTP is {otp}"
            )

        return JSONResponse(status_code=200, content={"status": "success", "message": "OTP sent to your email"})
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error: {str(e)}"})

@router.post("/verify-otp")
async def verify_otp(request: dict, db: Session = Depends(get_db)):
    try:
        email = request.get("email", "").strip().lower()
        otp = request.get("otp", "").strip()
        if not email or not otp:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Email and OTP are required"})

        user = get_user_by_email(db, email)
        if not user:
            return JSONResponse(status_code=404, content={"status": "error", "message": "User not found"})
        if not user.reset_token or user.reset_token != otp:
            return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid OTP"})
        if user.reset_token_expires and datetime.utcnow() > user.reset_token_expires:
            return JSONResponse(status_code=401, content={"status": "error", "message": "OTP expired"})

        reset_token = create_reset_token(data={"sub": user.email}, expires_delta=timedelta(hours=1))
        update_user_reset_token(db, user, reset_token, datetime.utcnow() + timedelta(hours=1))
        return JSONResponse(status_code=200, content={"status": "success", "message": "OTP verified", "reset_token": reset_token})
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error: {str(e)}"})

@router.post("/reset-password-with-otp")
async def reset_password_with_otp(request: dict, db: Session = Depends(get_db)):
    try:
        reset_token = request.get("reset_token")
        new_password = request.get("new_password")
        if not reset_token or not new_password:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Reset token and new password required"})

        payload = jwt.decode(reset_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user = get_user_by_email(db, email)
        if not user:
            return JSONResponse(status_code=404, content={"status": "error", "message": "User not found"})

        update_user_password(db, user, get_password_hash(new_password))
        return JSONResponse(status_code=200, content={"status": "success", "message": "Password reset successfully"})
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error: {str(e)}"})
