import uvicorn, time
from datetime import date 
from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from modules.parser import companyConfig
from modules.postgressConnections import checkConnection

from src.auth.mongo_router import *
from src.auth.postgres_router import *
from src.dashboard.router import *
from src.test.router import *

app = FastAPI(title="Awedan", summary="It is a API based Full Stack Project which is used to apply an application at various levels in an University",
              description='''\n
                The Student : They can make application and assing it to respective faculty \n 
                The Faculty : They can approve the request and may or may not forward it to the Higher authorities.''',
                version='1.0.0',
                docs_url="/awedan-docs",
                redoc_url="/backup/awedan-docs")

while True:
    isActive = checkConnection()
    if isActive == True:
        print('Connection To Server is Established [OK]')
        break
    else:
        print('Trying to Connect to Database Server')
        time.sleep(5)

app.mount("/assets", StaticFiles(directory="assets", html=True), name="assets")
templates = Jinja2Templates(directory="templates")
# app.include_router(router=authRouter)
app.include_router(router=PauthRouter)
app.include_router(router=dashboardRouter)
app.include_router(router=testRouter)


@app.get('/', response_class=HTMLResponse)
async def homepage(request:Request):
    return templates.TemplateResponse('index.html', {"request" : request,"year" : date.today().year, "CompanyName" : companyConfig['name']})

if __name__ == "__main__":
    uvicorn.run('main:app', host='localhost', port=8800, reload=True)