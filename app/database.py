from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import setting

SQLALCHEMY_DATABASE_URL=f'postgresql://{setting.database_username}:{setting.database_password}@{setting.database_hostname}:{setting.database_port}/{setting.database_name}' 
#'postgresql://<username>:<password>@<ip-address> or <hostname>/<database_name>'
engine=create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
#all models we create in database we import from this base class

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    # everytime when we interact with db we use sessions and get_db creates session for us and closes session whenever db interaction is finished
    #so now we call this fn everytime when we want to interact with db
    # so when we use it in fn we use db: Session = Depends(get_db) in fn input

    # while True:
#     try:
#         conn = psycopg2.connect(host='localhost',database='fastAPI',user='postgres',password='postgres',cursor_factory=RealDictCursor)# sql alchemy cannot connect with db without help of base underlined driver eg psycopg2,ultimately this helps us to contact db
#         cursor=conn.cursor()
#         print("db sucessfull")
#         break
#     except Exception as error:
#         print("error",error)
#         time.sleep(2)