from fastapi import FastAPI
from routers import post,user,auth,vote
import models
from database import engine

app=FastAPI()
#initializing all dependincies of database to make database interaction and is mentioned in fastapi sql database connection documentation https://fastapi.tiangolo.com/tutorial/sql-databases/
models.Base.metadata.create_all(bind=engine)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)