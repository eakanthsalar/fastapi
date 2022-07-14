from database import Base
from sqlalchemy import  Boolean, Column, ForeignKey, Integer,String
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

class Post(Base):
    __tablename__='new_posts'

    id=Column(Integer, primary_key=True,nullable=False)
    title=Column(String,nullable=False)
    content=Column(String,nullable=False)
    published=Column(Boolean,server_default='TRUE',nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    #now() will give exact time when it is called
    owner_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    owner=relationship("User")

class User(Base):
    __tablename__='users'

    id=Column(Integer,nullable=False,primary_key=True)
    username=Column(String,nullable=False,unique=True)
    email=Column(String,nullable=False,unique=True)#EmailStr if we are giving original email everytime
    password=Column(String,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)

class Vote(Base):
    __tablename__='votes'
    user_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),primary_key=True)
    post_id=Column(Integer,ForeignKey("new_posts.id",ondelete="CASCADE"),primary_key=True)