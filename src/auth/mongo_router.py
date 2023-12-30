from datetime import  timedelta, date
import bcrypt
from fastapi import APIRouter, HTTPException, Request, Form, Depends, Response, status, BackgroundTasks
from fastapi.params import Body, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from src.auth.utils import *

# Config Parameter Import
from modules.postgressConnections import executeQueryWithReturn, executeQuery
from modules.mongooConnection import getMongoConnection
from modules.parser import configs, activeDbConfig, credentialsSchema, credentialsCollection, companyConfig

# Models Import
from src.auth.models import UserCreate, User

# Getting Credentials location
schemaName = credentialsSchema['schema']
collectionName = credentialsCollection['collection']
activeDb = activeDbConfig['isActive']

# Setting Up Router - Auth
authRouter = APIRouter(tags=["Auth"])
templates = Jinja2Templates(directory="templates")

@authRouter.get('/login', response_class=HTMLResponse)
async def render_LoginPage(request:Request):
     return templates.TemplateResponse('routes/login.html',  {"request" : request, "year" : date.today().year})

@authRouter.get('/singup', response_class=HTMLResponse)
async def render_SingupPage(request:Request):
    return templates.TemplateResponse("routes/singup.html", {"request" : request, "year" : date.today().year})

@authRouter.get("/signup-redirect/sign-in", response_class=HTMLResponse)
async def render_SingupPage_Redirect(request:Request):
    return templates.TemplateResponse("routes/sign-in-redirect.html", {"request" : request, "year" : date.today().year})

@authRouter.post("/register/user", status_code=status.HTTP_201_CREATED, response_class=JSONResponse)
async def register(background_tasks: BackgroundTasks, user_data: UserCreate):
    # Check if the username already exists
    if user_data.password != user_data.rePassword:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not matched")
    client, db = getMongoConnection()
    existing_user = await db.credentials.find_one({"username": user_data.username})
    if existing_user:
        client.close()
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail="Username already registered")
    # Create a new user
    # Create access token
    access_token_expires = timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    verification_token = create_access_token(data={"sub": user_data.username}, expires_delta=access_token_expires)
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
    new_user = {
        "_id": user_data.username,
        "username": user_data.username,
        "password": hashed_password,
        "is_verified": False,
        "verification_token": verification_token,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    newUserRoles = {
        "_id" : user_data.username,
        "role": 0
    }

    newUser_data ={
        "_id" : user_data.username,
        "fullName" : user_data.name
    }
    await db.credentials.insert_one(new_user)
    await db.roles.insert_one(newUserRoles)
    await db.userdata.insert_one(newUser_data)

    # Send verification email
    background_tasks.add_task(send_verification_email, user_data.username, verification_token, user_data.name)
    client.close()
    return {"message": "User Created Please Verify Your Account", "Verification_Mail_Status": "Sent", "VerificationToken" : verification_token}

@authRouter.get("/verify/user")
async def verify_token(token: str = Query(...)):
    # Check if the token exists
    client, db =getMongoConnection()
    user = await db.credentials.find_one({"verification_token": token})
    if not user:
        return HTTPException(status_code=400, detail="Invalid verification token")
        client.close()
    if datetime.utcnow() >  user["created_at"] + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS):
        return HTTPException(status_code=400, detail="Verification token Expires")
        client.close()
    else:
        # Verify the user and update the database
        await db.credentials.update_one({"_id": user["_id"]}, {"$set": {"is_verified": True, "verification_token": None}})
    client.close()
    return {"details":"Success"}

@authRouter.post("/reset-token/user")
async def reset_Token(user_data: User, background_tasks: BackgroundTasks):
    if user_data.password: 
        client, db =getMongoConnection()
        existing_user = await db.credentials.find_one({"username": user_data.username})
        if not existing_user:
            return HTTPException(status_code=400, detail="User not registered")
            client.close()
        if not bcrypt.checkpw(user_data.password.encode('utf-8'), existing_user['password']):
            return HTTPException(status_code=404, detail="Incorrect Password")
            client.close()
        access_token_expires = timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
        verification_token = create_access_token(data={"sub": user_data.username}, expires_delta=access_token_expires)
        
        await db.credentials.update_one({"_id": existing_user["_id"]}, {"$set": {"created_at": datetime.utcnow(), "updated_at": datetime.utcnow(), "verification_token": verification_token}})

        # Send verification email
        background_tasks.add_task(resend_verification_email, user_data.username, verification_token)
        client.close()
        return {"message": "Re-Verify Account", "Verification_Mail_Status": f"Sent to {user_data.username}", "VerificationToken" :"Changed"}
    else:
        return HTTPException(status_code=400, detail="Password not supplied")
    
@authRouter.post('/loginUser', response_class=HTMLResponse)
async def auth_Login(request: Request, user_data: User, background_tasks: BackgroundTasks):
    if  user_data.username != "" and  user_data.password != '':
        try:
            if activeDb == 'postgresql':
                records = executeQueryWithReturn(f"select password from {schemaName}.user_credentials where username='{user_data.username}'")
                if records != []:
                    if records[0][0] == bcrypt.checkpw(user_data.password.encode('utf-8'), existing_user['password']):
                        message = {"message" : "Login Success", "status" : 200} 
                        return message
                    else:
                        message = {"message" : "Login Failed Incorrect Password", "status" : status.HTTP_401_UNAUTHORIZED} 
                        return message
                else:
                    message = {"message" : "Login Failed Incorrect Username or Password", "status" : status.HTTP_401_UNAUTHORIZED} 
                    return message
                    # return templates.TemplateResponse('homepage.html', {"request" : request})
            elif activeDb == 'mongodb':
                client, db =getMongoConnection()
                existing_user = await db.credentials.find_one({"username": user_data.username})
                if not existing_user:
                    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username not registered")
                
                if not bcrypt.checkpw(user_data.password.encode('utf-8'), existing_user['password']):
                    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Password")
                session_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                session_token = getSessionToken(data={"username":user_data.username}, expires_delta=session_token)
                client, dbs =  getMongoConnection()
                role = await dbs.roles.find_one({"_id": user_data.username})
                role = role["role"]
                data = {"username" : user_data.username,
                        "logtime" : datetime.utcnow(),
                        "sessionToken" : session_token,
                        "role" : role
                        }
                db.loginlogs.insert_one(data)
                ip = request.client.host
                browser = request.headers.get("user-agent", "Unknown")
                location = "Unknown"
                message = {"message" : "Login Success", "status" : 200}
                background_tasks.add_task(sendMail, user_data.username, "Accounts : New Device Login", f"Your Account has been access from \n\n: {ip} at {datetime.utcnow()} near {location} using {browser}")
                client.close()
                return templates.TemplateResponse('routes/dashboard.html',{"request" : request, "year" : date.today().year, "companyName" : companyConfig['name']})
        except Exception as e:
            message = {"message" : f"Request Failed Possible Cause {e}", "status" : status.HTTP_400_BAD_REQUEST} 
            return message
    else:
        message = {"message" : "Login Failed Credentials Not Supplied", "status" : status.HTTP_401_UNAUTHORIZED} 
        return message