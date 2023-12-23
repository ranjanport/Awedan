# from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile, BackgroundTasks, APIRouter
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, EmailStr
# # from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
# # from sqlalchemy.ext.declarative import declarative_base
# # from sqlalchemy.orm import sessionmaker
# from datetime import datetime, timedelta
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import os


# testRouter = APIRouter()

# # SQLite database setup
# DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(DATABASE_URL)
# Base = declarative_base()

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     password = Column(String)
#     is_verified = Column(Boolean, default=False)
#     verification_token = Column(String, unique=True, index=True, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Base.metadata.create_all(bind=engine)

# # Dependency to get the database session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# app = FastAPI()

# # Pydantic models
# class UserCreate(BaseModel):
#     username: str
#     password: str

# class UserVerify(BaseModel):
#     verification_token: str

# # Dependency to get the database session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Background task to send email
# def send_verification_email(email_to: str, verification_token: str):
#     subject = "Verify Your Email"
#     body = f"Click the link to verify your email: http://yourdomain.com/verify?token={verification_token}"
    
#     sender_email = "your_email@gmail.com"  # Replace with your email
#     sender_password = "your_email_password"  # Replace with your email password

#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = email_to
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))

#     with smtplib.SMTP('smtp.gmail.com', 587) as server:
#         server.starttls()
#         server.login(sender_email, sender_password)
#         server.send_message(msg)

# # Signup endpoint
# @testRouter.post("/signup")
# async def signup(
#     user_data: UserCreate,
#     db: Session = Depends(get_db),
#     background_tasks: BackgroundTasks
# ):
#     # Check if the username already exists
#     existing_user = db.query(User).filter(User.username == user_data.username).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Username already registered")

#     # Create a new user
#     verification_token = os.urandom(32).hex()
#     new_user = User(username=user_data.username, password=user_data.password, verification_token=verification_token)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     # Send verification email
#     background_tasks.add_task(send_verification_email, user_data.username, verification_token)

#     return JSONResponse(content={"message": "User registered. Check your email for verification link."})

# # Verification endpoint
# @testRouter.post("/verify")
# async def verify(
#     user_data: UserVerify,
#     db: Session = Depends(get_db)
# ):
#     # Check if the token exists
#     user = db.query(User).filter(User.verification_token == user_data.verification_token).first()
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid verification token")

#     # Verify the user and update the database
#     user.is_verified = True
#     user.verification_token = None
#     db.commit()

#     return JSONResponse(content={"message": "Email verified successfully"})


from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from modules.mongooConnection import uri, database_name
from src.auth.utils import create_access_token, send_verification_email

# app = FastAPI(openapi_tags="tests")
testRouter = APIRouter(prefix="/TESTS")

# MongoDB setup
MONGODB_URI = uri
DATABASE_NAME = database_name

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Pydantic models


class UserVerify(BaseModel):
    verification_token: str

# Background task to send email



ACCESS_TOKEN_EXPIRE_SECONDS = 45
# # Signup endpoint
# @testRouter.post("/signup")
# async def signup(user_data: UserCreate, background_tasks: BackgroundTasks):
#     # Check if the username already exists
#     existing_user = await db.credentials.find_one({"username": user_data.username})
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
        
#     # Create a new user
#     # Create access token
#     ACCESS_TOKEN_EXPIRE_SECONDS = 45
    # access_token_expires = timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
#     verification_token = create_access_token(data={"sub": user_data.username}, expires_delta=access_token_expires)
#     # verification_token = os.urandom(32).hex()
#     hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
#     new_user = {
#         "_id": user_data.username,
#         "username": user_data.username,
#         "password": hashed_password,
#         "is_verified": False,
#         "verification_token": verification_token,
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow(),
#     }
#     await db.credentials.insert_one(new_user)

#     # Send verification email
#     background_tasks.add_task(send_verification_email, user_data.username, verification_token)
#     return {"message": "User Created Please Verify Your Account", "Verification_Mail_Status": "Sent"}

# class UserVerify(BaseModel):
#     verification_token: str

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     username: str | None = None



# Verification endpoint
# @testRouter.post("/verify")
# async def verify(user_data: UserVerify):
#     # Check if the token exists
#     user = await db.credentials.find_one({"verification_token": user_data.verification_token})
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid verification token")

#     # Verify the user and update the database
#     await db.credentials.update_one({"_id": user["_id"]}, {"$set": {"is_verified": True, "verification_token": None}})

#     # Create access token
#     access_token_expires = timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
#     access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

#     return {"access_token": access_token, "token_type": "bearer"}


# @authRouter.post('/register-user', response_class=HTMLResponse)
# async def register_user(request:Request, name:str = Form("name"), username:str = Form("email"), password:str = Form("pass"), re_password:str = Form("re_pass")):
#     if username != "username" and username != "" and  password != '' and password != 'password' and re_password != '' and re_password != 're_pass':
#         try:
#             if activeDb == 'postgresql':
#                 # Hash the password before storing it
#                 hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#                 # Create a user document
#                 isInserted = executeQuery(f"INSERT INTO {credentialsSchema}.user_credentials (id, username, password) VALUES ( , '{username}',  crypt('{password}', gen_salt('bf')))")
#                 if isInserted == True:
#                     message = {"message" : "User Register Success", "status" : 200} 
#                     return returnMessage(**message)
#                 else:
#                     message = {"message" : f"User Register Failed \n {isInserted}", "status" : 200} 
#                     return returnMessage(**message)
#             if activeDb == 'mongodb':
#                 if password == re_password:
#                 # Hash the password before storing it
#                     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#                     # Create a user document
#                     user_document = {
#                         "_id" : username,
#                         "username": username,
#                         "password": hashed_password
#                     }
#                     isInserted = executeMongoQueyInsert(collection_name=collectionName, user_document=user_document)
#                     if isInserted == True:
#                         message = {"message" : "User Register Success", "status" : 200} 
#                         return returnMessage(**message)
#                     else:
#                         message = {"message" : f"User Register Failed \n {isInserted}", "status" : 200} 
#                         return returnMessage(**message)
#                 else:
#                     message = {"message" : f"User Register Failed Password does not match", "status" : 200} 
#                     return returnMessage(**message)
#         except Exception as e:
#             print(f"Error: {e}")

# @authRouter.post('/loginUser', response_class=JSONResponse)
# async def login(request:Request,username: str = Form("username"), password: str = Form("password")):
#     # print(username, password)
#     if  username != "username" and username != "" and  password != '' and password != 'password':
#         try:
#             if activeDb == 'postgresql':
#                 records = executeQueryWithReturn(f"select password from {schemaName}.user_credentials where username='{username}'")
#                 if records != []:
#                     if records[0][0] == bcrypt.checkpw(password.encode('utf-8'), records[0][2]):
#                         message = {"message" : "Login Success", "status" : 200} 
#                         return returnMessage(**message)
#                     else:
#                         message = {"message" : "Login Failed Incorrect Password", "status" : status.HTTP_401_UNAUTHORIZED} 
#                         return returnMessage(**message)
#                 else:
#                     message = {"message" : "Login Failed Incorrect Username or Password", "status" : status.HTTP_401_UNAUTHORIZED} 
#                     return returnMessage(**message)
#                     # return templates.TemplateResponse('homepage.html', {"request" : request})
#             elif activeDb == 'mongodb':
#                     records = executeMongoQueyWithReturn(collection_name=collectionName, findMethod=1, query={ "username" : username })
#                     if records:
#                         hashed_password = bcrypt.checkpw(password.encode('utf-8'), records['password'] )
#                         if hashed_password:
#                             message = {"message" : "Login Success", "status" : 200} 
#                             return returnMessage(**message)
#                         else:
#                             message = {"message" : "Login Failed Incorrect Password", "status" : status.HTTP_401_UNAUTHORIZED} 
#                             return returnMessage(**message)
#                     else:
#                         message = {"message" : "Login Failed Incorrect Username or Password", "status" : status.HTTP_401_UNAUTHORIZED} 
#                         return returnMessage(**message)
#         except Exception as e:
#             message = {"message" : f"Request Failed Possible Cause {e}", "status" : status.HTTP_400_BAD_REQUEST} 
#             return returnMessage(**message)
#     else:
#         message = {"message" : "Login Failed Credentials Not Supplied", "status" : status.HTTP_401_UNAUTHORIZED} 
#         return returnMessage(**message)

# @authRouter.put('/register', response_class=JSONResponse)
# async def register_user(request:Request,username: str = Form("username"), password: str = Form("password")):
#     try:
#         if activeDb == 'postgresql':
#             # Hash the password before storing it
#             hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#             # Create a user document
#             isInserted = executeQuery(f"INSERT INTO {credentialsSchema}.user_credentials (id, username, password) VALUES ( , '{username}',  crypt('{password}', gen_salt('bf')))")
#             if isInserted == True:
#                 message = {"message" : "User Register Success", "status" : 200} 
#                 return returnMessage(**message)
#             else:
#                 message = {"message" : f"User Register Failed \n {isInserted}", "status" : 200} 
#                 return returnMessage(**message)
#         if activeDb == 'mongodb':
#             # Hash the password before storing it
#             hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#             # Create a user document
#             user_document = {
#                 "_id" : username,
#                 "username": username,
#                 "password": hashed_password
#             }
#             isInserted = executeMongoQueyInsert(collection_name=collectionName, user_document=user_document)
#             if isInserted == True:
#                 message = {"message" : "User Register Success", "status" : 200} 
#                 return returnMessage(**message)
#             else:
#                 message = {"message" : f"User Register Failed \n {isInserted}", "status" : 200} 
#                 return returnMessage(**message)
#     except Exception as e:
#         print(f"Error: {e}")
