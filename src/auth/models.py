from pydantic import BaseModel
from typing import Optional, Annotated

class returnMessage(BaseModel):
    message: str
    status : int 

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    password: str

class UserIsActive(BaseModel):
    username: str
    password: str
    email: str
    is_active: bool = False

class UserRemove(BaseModel):
    username : str
    password : str
    token : str | bool

class UserCreate(BaseModel):
    fname : str
    lname : str
    username: str
    password: str
    rePassword : str


class UserVerify(BaseModel):
    token: str

class Token(BaseModel):
    token: str

from typing import List
from typing import Optional

from fastapi import Request


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get(
            "username"
        )  # since outh works on username field we are considering email as username
        self.password = form.get("password")

    async def is_valid(self):
        if not self.username or not (self.username.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False