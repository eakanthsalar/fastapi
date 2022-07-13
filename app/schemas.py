from datetime import datetime
from typing import Optional
from pydantic import BaseModel,EmailStr # used to define standard schema of data packets that comes in order to match with db

class Post_structure(BaseModel):
    title: str
    content:str
    published:bool = False

class Ret_Username(BaseModel):
    username:str
    email:str
    created_at:datetime

    class Config:#pydantic only work with dictionaries so in order to make it convert response from db into this format we use this class that is shown in fast api-sql db documentation
        orm_mode=True

class Response_Schema(BaseModel):
    title:str
    content:str
    published:bool
    owner_id:int
    owner: Ret_Username

    class Config:#pydantic only work with dictionaries so in order to make it convert response from db into this format we use this class that is shown in fast api-sql db documentation
        orm_mode=True



class User_Created_Response(BaseModel):
    username:str
    class Config:
        orm_mode=True

class User_Display(User_Created_Response):
    email:str #EmailStr if we are giving original email everytime
    created_at:datetime

class User_Login_Schema(BaseModel):
    username:str
    password:str

class Create_User_Schema(User_Login_Schema):
    email:str#can use Emailstr to make sure it is a valid email id

class Token_Data(BaseModel):
    username:Optional[str]=None

class Token(BaseModel):
    access_token:str
    token_type:str

