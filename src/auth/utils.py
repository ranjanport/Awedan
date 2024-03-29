import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Optional
import hashlib
import jwt
import bson
import smtplib
from email.message import EmailMessage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
sender_email = os.getenv('sender_email')
sender_password = os.getenv('sender_password')
# from models import UserIsActive
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "ACCESS-Token"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
ACCESS_TOKEN_EXPIRE_SECONDS = 300.00
expires_delta = timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)

def getSessionToken(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        # Invalid token
        return {"error": "Invalid token"}

def send_verification_email(email_to: str, verification_token: str, name : str):
    subject = "SingUp Verification ! - Verify Your Email"
    body = f"Hi {name} \n\n Click the link to verify your email: \n\n http://localhost:8800/verify/user?token={verification_token}"
    
    msg = MIMEMultipart()
    msg['From'] = "PortalAuth"
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
    return True

def resend_verification_email(email_to: str, verification_token: str):
    subject = "Account Verification : Verify Account"
    body = f"Click the link to verify your email: \n\n http://localhost:8800/verify/user?token={verification_token}"
    
    msg = MIMEMultipart()
    msg['From'] = "PortalAuth"
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
    return True

def sendMail(email_to: str, subject: str, body : str ):

    msg = MIMEMultipart()
    msg['From'] = "PortalAuth"
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
    return True

