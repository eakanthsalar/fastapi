from fastapi import Response,status,HTTPException,Depends,APIRouter
from fastapi.params import Body
# import psycopg2
# it is a standard base driver(inderlined driver) to connect to database
from psycopg2.extras import RealDictCursor
 # RealDictCursor is a specialized DictCursor that enables to access columns only from keys (aka columns name), whereas DictCursor enables to access data both from keys or index number.
# before using orm we created all colums in database manually by using postgres gui, after using orm we defined colums,database tablename etc
import models
from sqlalchemy.orm import Session
from database import get_db
from schemas import Create_User_Schema,User_Created_Response,User_Display
from utills import password_hash

router=APIRouter(prefix="/users",tags=["users"])

@router.post("/signup",status_code=status.HTTP_201_CREATED,response_model=User_Created_Response)
def create_user(user_info:Create_User_Schema=Body(...),db: Session = Depends(get_db)):
    #seeing if any user of same username or email exists, if exists throw error
    username_alredy_exists=db.query(models.User).filter(models.User.username==user_info.username).first()
    if username_alredy_exists != None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"user with username {user_info.username} already exists")
    email_already_exists=db.query(models.User).filter(models.User.email==user_info.email).first()
    if email_already_exists != None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"email id {user_info.email} already used to create user {email_already_exists.username}")
    #hashing password
    user_info.password=password_hash(user_info.password)
    new_user=models.User(**user_info.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}",response_model=User_Display)
def get_user(id:int,db: Session = Depends(get_db)):
    fetched_user=db.query(models.User).filter(models.User.id==id).first()
    if fetched_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with id {id} does not exists ")
    return fetched_user