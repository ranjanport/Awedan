import datetime
import bcrypt
from fastapi import APIRouter, HTTPException, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# Config Parameter Import
from modules.postgressConnections import executeQueryWithReturn, executeQuery
from modules.mongooConnection import executeMongoQueyWithReturn, executeMongoQueyInsert
from modules.parser import configs, activeDbConfig, credentialsSchema, credentialsCollection

# Models Import
from src.auth.models import returnMessage

# Getting Credentials location
schemaName = credentialsSchema['schema']
collectionName = credentialsCollection['collection']
activeDb = activeDbConfig['isActive']

# Setting Up Router - Auth
dashboardRouter = APIRouter()
templates = Jinja2Templates(directory="templates")