from fastapi import Depends, HTTPException,status
from jose import JWTError,jwt
from datetime import datetime, timedelta
from schemas import Token_Data
#in order to use jwt web tokens pip install "python-jose[cryptography]"
# to get random hex as a secret code --openssl rand -hex 32
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import models
from config import setting

#serect key 
#logic
#expry time

oauth2_schema=OAuth2PasswordBearer(tokenUrl='users/signin')

SECRET_KEY=setting.secret_key
ALGORITHM = setting.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = setting.access_token_expire_minutes#from documentation https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

def create_access_token(data:dict):#here we sign access token
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})#data comes in as a dict so we use .update method to update expiry time to 30 minutes
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)#to sign token we need data with expiry,secret key,algorithm
    return encoded_jwt

def verify_access_token(token:str,credentials_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        name:str=payload.get("user_name")#look at auth.py what inputs were given to create jwt token
        if name==None:
            raise credentials_exception
        token_data=Token_Data(username=name)#checking if schema matches
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(token:str=Depends(oauth2_schema),db:Session = Depends(get_db)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate credentials",headers={"WWW-Authenticate":"Bearer"})
    token=verify_access_token(token,credentials_exception)#here we have TokenData(username=name)
    user=db.query(models.User).filter(models.User.username==token.username).first()#this is token obtained from calling fn and is not a schema
    return user
