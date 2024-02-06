from datetime import  timedelta, date
import bcrypt, pytz
from cryptography.fernet import Fernet
from fastapi import APIRouter, HTTPException, Request, Form, Depends, Response, status, BackgroundTasks
from fastapi.params import Body, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from src.auth.utils import *
import json
# Config Parameter Import
from modules.postgressConnections import executeQueryWithReturn, executeQuery, getPostgresConnection
from modules.mongooConnection import getMongoConnection
from modules.parser import configs, activeDbConfig, credentialsSchema, credentialsCollection, companyConfig

# Models Import
from src.auth.models import UserCreate, User, Annotated


def getInsertKeyRecord(_data:dict):
    return f'''({', '.join(_data.keys())})'''

def getInsertValueRecord(_data:dict):
    return f'''({', '.join([str(value) for value in _data.values()])})'''

def verify_password(plain_password, hashed_password):
    # Use bcrypt to check if the provided password matches the stored hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def create_password_hash(password):
    # Convert the password into bytes
    password_bytes = password.encode()
    
    # Create a key and initialize the cipher
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    
    # Encrypt the password and convert it into a string
    encrypted_password = cipher_suite.encrypt(password_bytes).decode()
    
    return encrypted_password

def check_password(entered_password, password_hash):
    # Convert the entered password into bytes
    entered_password_bytes = entered_password.encode()
    key = Fernet.generate_key()
    # Decrypt the password_hash
    cipher_suite = Fernet(key)
    decrypted_password = cipher_suite.decrypt(password_hash.encode()).decode()

    # Check if the entered password is correct
    if decrypted_password == entered_password:
        print("Password is correct.")
        return True
    else:
        print("Password is incorrect.")
        return False

# Getting Credentials location
schemaName = credentialsSchema['schema']
collectionName = credentialsCollection['collection']
activeDb = activeDbConfig['isActive']

# Setting Up Router - Auth
PauthRouter = APIRouter(tags=["PAuth"])
templates = Jinja2Templates(directory="templates")

@PauthRouter.get('/login', response_class=HTMLResponse)
async def render_LoginPage(request:Request):
     return templates.TemplateResponse('routes/login.html',  {"request" : request, "year" : date.today().year})

@PauthRouter.get('/singup', response_class=HTMLResponse)
async def render_SingupPage(request:Request):
    return templates.TemplateResponse("routes/singup.html", {"request" : request, "year" : date.today().year})

@PauthRouter.get("/signup-redirect/sign-in", response_class=HTMLResponse)
async def render_SingupPage_Redirect(request:Request):
    return templates.TemplateResponse("routes/sign-in-redirect.html", {"request" : request, "year" : date.today().year})

# bcrypt.hashpw('sdfsdfsadf'.encode('utf-8'), bcrypt.gensalt())

# bcrypt.checkpw(b'sdfsdfsadf', b'\x2432622431322435386536595a70346e6e6d674d46314a72772e317365414a486973782f34643243755a724c4c5233734246544a456b68734b674b57')

@PauthRouter.post("/register/user", status_code=status.HTTP_201_CREATED, response_class=JSONResponse)
async def register(background_tasks: BackgroundTasks, user_data: UserCreate):
    # Check if the username already exists
    if user_data.password != user_data.rePassword:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not matched")
    conn, cur = getPostgresConnection()
    if conn:
        cur.execute("""select email from %s.users where email='%s' """%(schemaName,user_data.username))
        
        if cur.fetchone():
            conn.close()
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail="Username already registered")
        # Create a new user if not exists
        # Create verification token
        verification_token = create_access_token(data={"sub": user_data.username}, expires_delta=timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS))
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode()
        # hashed_password = create_password_hash(user_data.password)
        new_user = {
            "fname" :user_data.fname,
            "lname" : user_data.lname,
            "email": user_data.username,
            "passwd": hashed_password,
            "is_verified": False,
            "v_token": verification_token,
        }
        conn, cur = getPostgresConnection()
        insert_query = f"""INSERT INTO {schemaName}.users (fname, lname, email, passwd, is_verified, v_token)
        VALUES (%(fname)s, %(lname)s, %(email)s, %(passwd)s, %(is_verified)s, %(v_token)s) RETURNING email"""
        cur.execute(insert_query, new_user)
        conn.commit()
        conn.close()
        # Send verification email
        background_tasks.add_task(send_verification_email, user_data.username, verification_token, user_data.fname)
        return {"message": "User Created Please Verify Your Account", "Verification_Mail_Status": "Sent", "VerificationToken" : verification_token}
    else:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(cur))

@PauthRouter.get("/verify/user", status_code=status.HTTP_202_ACCEPTED)
async def verify_token(background_tasks: BackgroundTasks, token: str = Query(...)):
    # Check if the token exists
    conn, cur = getPostgresConnection()
    if conn:
        decoded_token = decode_token(token)
        if "error" in decoded_token:
            conn.close()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {decoded_token['error']}")
        else:
            cur.execute("""select is_verified, v_token from %s.users WHERE email='%s' """%(schemaName, decoded_token['sub']))
            existing_user = cur.fetchone()
            if existing_user['is_verified'] == True:
                conn.close()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error: User Already Verified")
            else:
                if not existing_user['v_token']:
                    conn.close()
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error: Token Not Present")
                # Get the current time in UTC
                current_utc_time = datetime.utcnow()
                # Attach the UTC timezone to the timestamp
                GMT_timezone = pytz.timezone('GMT')
                current_utc_time_with_timezone = GMT_timezone.localize(current_utc_time)
                cur.execute("""UPDATE %s.users SET updated_at='%s', is_verified=%s, v_token=%s WHERE email='%s'"""%(schemaName,current_utc_time_with_timezone, True, 'Null', decoded_token['sub']))
                conn.commit()
                conn.close()
                background_tasks.add_task(sendMail, decoded_token['sub'],  'Welcome to Awedan', 'Hi,\n\n Your Account has been succesfully verified')
                return Response(content="User Verified",background=background_tasks)
    else:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(cur))

@PauthRouter.post("/reset-token/user", status_code=status.HTTP_202_ACCEPTED,)
async def reset_Token(user_data: User,  background_tasks: BackgroundTasks):
    if user_data.password: 
        conn, cur = getPostgresConnection()
        if conn:
            cur.execute(""" select * from %s.users where email='%s' or username='%s'""" %(schemaName, user_data.username, user_data.username))
            existing_user = cur.fetchone()
            if not existing_user:
                conn.close()
                return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username not registered")
            
            if not verify_password(user_data.password, existing_user['passwd'].encode('utf-8')):
                conn.close()
                return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Password")
            else:
                access_token_expires = timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
                verification_token = create_access_token(data={"sub": user_data.username}, expires_delta=access_token_expires)
                # Get the current time in UTC
                current_utc_time = datetime.utcnow()
                # Attach the UTC timezone to the timestamp
                GMT_timezone = pytz.timezone('GMT')
                current_utc_time_with_timezone = GMT_timezone.localize(current_utc_time)
                cur.execute("""UPDATE %s.users SET updated_at='%s', is_verified='%s', v_token='%s' WHERE email='%s' or username = '%s' """%(schemaName, current_utc_time_with_timezone, False, verification_token, user_data.username , user_data.username))  
                # Send verification email
                conn.commit()
                conn.close()
                background_tasks.add_task(resend_verification_email, user_data.username, verification_token)
                response = {"message": "Re-Verify Account", "Verification_Mail_Status": f"Sent to {user_data.username}", "VerificationToken" :"Changed"}
                return Response(content=str(json.dumps(response)),background=background_tasks) 
    else:
        return HTTPException(status_code=400, detail="Password not supplied")
    
@PauthRouter.post('/loginUser') #, response_class=HTMLResponse
# async def auth_Login(request: Request, user_data: User, background_tasks: BackgroundTasks):
async def auth_Login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return Response(content=username)
    # if  user_data.username != "" and  user_data.password != '':
    #     conn, cur = getPostgresConnection()
    #     if conn:
    #         cur.execute(""" select * from %s.users where email='%s' or username='%s'""" %(schemaName, user_data.username, user_data.username))
    #         existing_user = cur.fetchone()
    #         if not existing_user:
    #             conn.close()
    #             return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username not registered")
    #         if existing_user['is_verified'] == False:
    #             conn.close()
    #             return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not Verified")
    #         elif not verify_password(user_data.password, existing_user['passwd'].encode('utf-8')):
    #             conn.close()
    #             return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Password")
    #         else:
    #             session_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #             session_token = getSessionToken(data={"username":user_data.username}, expires_delta=session_token)
    #             data = {"username" : user_data.username,
    #                     "logtime" : datetime.utcnow(),
    #                     "sessionToken" : session_token,
    #                     # "role" : role
    #                     }
    #             ip = request.client.host
    #             browser = request.headers.get("user-agent", "Unknown")
    #             location = "Unknown"
    #             message = {"message" : "Login Success", "status" : 200}
    #             background_tasks.add_task(sendMail, user_data.username, "Accounts : New Device Login", f"Your Account has been access from \n\n: {ip} at {datetime.utcnow()} near {location} using {browser}")
    #             # client.close()
    #             return templates.TemplateResponse('routes/dashboard.html',{"request" : request, "year" : date.today().year, "companyName" : companyConfig['name']})
    #     else:
    #         raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(cur))
    # else:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail= "Login Failed Credentials Not Supplied") 