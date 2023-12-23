import datetime
from datetime import datetime, timedelta
import bcrypt
from fastapi import APIRouter, HTTPException, Request, Form, Depends, status, BackgroundTasks
from fastapi.params import Body, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from src.auth.utils import ACCESS_TOKEN_EXPIRE_SECONDS, create_access_token, send_verification_email

# Config Parameter Import
from modules.postgressConnections import executeQueryWithReturn, executeQuery
from modules.mongooConnection import executeMongoQueyWithReturn, executeMongoQueyInsert, getMongoConnection
from modules.parser import configs, activeDbConfig, credentialsSchema, credentialsCollection

# Models Import
from src.userProfile.models import *

# Getting Credentials location
schemaName = credentialsSchema['schema']
collectionName = credentialsCollection['collection']
activeDb = activeDbConfig['isActive']

# Setting Up Router - Auth
profileRouter = APIRouter()
templates = Jinja2Templates(directory="templates")


# @profileRouter.get()