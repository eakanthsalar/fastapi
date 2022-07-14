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
from schemas import Post_structure,Response_Schema,ResposnseWithVotes
from typing import List, Optional
from oauth2 import get_current_user
from sqlalchemy import func

router=APIRouter(prefix="/posts",tags=["posts"])#since every single route consists of /posts in this routes we can use prefix
#tags are used to view in swagger as clear routes documented

#giving only posts that is owned by that user
@router.get("/",response_model=List[ResposnseWithVotes])#,response_model=List[Response_Schema]
def get_posts(db: Session = Depends(get_db),get_current_user:str=Depends(get_current_user),limit:int=6,skip:int=0,search:Optional[str]=""):
    #select new_posts.*,count(user_id) as votes from new_posts left join votes on new_posts.id=votes.post_id group by id order by id;
    post_withvotes=db.query(models.Post,func.count(models.Vote.user_id).label("votes")).join(models.Vote,models.Post.id==models.Vote.post_id,isouter=True).group_by(models.Post.id).order_by(models.Post.id).filter(models.Post.owner_id == get_current_user.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # .lable is used for renaming count table as votes
    #post=db.query(models.Post).all()
    return post_withvotes
    # cursor.execute("""SELECT * FROM posts""")
    # post=cursor.fetchall()
    # return {"posts":post}

#giving all post regardless of owner owns it or not
@router.get("/public",response_model=List[ResposnseWithVotes])#gets all post irrespective of user login or owned etc #,response_model=List[Response_Schema]
def get_posts(db: Session = Depends(get_db),limit:int=6,skip:int=0,search:Optional[str]=""):
    
    post=db.query(models.Post,func.count(models.Vote.user_id).label("votes")).join(models.Vote,models.Post.id==models.Vote.post_id,isouter=True).group_by(models.Post.id).order_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return post

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=Response_Schema)
def create_post(new_post:Post_structure = Body(...),db: Session = Depends(get_db),get_current_user:str=Depends(get_current_user)):
    #new_data=models.Post(title=new_post.title,content=new_post.content,published=new_post.published)
    #insted of doing all above stuff we can use dict fn to unfold new post in defined format
    print(get_current_user.username)#username='salar12345' is printed

    new_data=models.Post(owner_id=get_current_user.id,**new_post.dict())
    db.add(new_data)
    db.commit()
    db.refresh(new_data)#for returning data we sent to put in db we use refresh method
    return new_data
    
    # cursor.execute("""INSERT INTO posts (title,content) VALUES (%s,%s) RETURNING * """,(new_post.title,new_post.content,))
    # post_returned=cursor.fetchone()
    # conn.commit()
    # return {"data": post_returned}

@router.get("/{id}",status_code=status.HTTP_200_OK,response_model=ResposnseWithVotes)#,response_model=Response_Schema
def get_post(id:int,db: Session = Depends(get_db),get_current_user:str=Depends(get_current_user)):
    #select new_posts.*,count(user_id) as votes from new_posts left join votes on id=post_id where id=1 group by id order by id;
    post_with_votes=db.query(models.Post,func.count(models.Vote.user_id).label("votes")).join(models.Vote,models.Post.id==models.Vote.post_id,isouter=True).filter(models.Post.id==id).group_by(models.Post.id).first()
    #post=db.query(models.Post).filter(models.Post.id==id).first()
    if post_with_votes.Post.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {post_with_votes.Post.id} does not exists")
    
    return post_with_votes
    


   



    # cursor.execute("""SELECT * FROM posts WHERE id=%s """,(str(id),))
    # post_obtained = cursor.fetchone()
    # if not post_obtained:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id :{id} was not found")
    # return {"post fetched =":post_obtained}

# @app.put("/posts/{id}")
# def update_post(id:int):

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db: Session = Depends(get_db),get_current_user:str=Depends(get_current_user)):
    post=db.query(models.Post).filter(models.Post.id==id)
    if post.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} not found")
    if post.first().owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="not authorized to delete this post")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

    # cursor.execute("""DELETE FROM posts WHERE id = %s returning * """,(str(id),))
    # deleted_post=cursor.fetchone()
    # conn.commit()
    # if deleted_post == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} may already be deleted or does not exist")
    # return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",response_model=ResposnseWithVotes)#,response_model=Response_Schema
def update_post(id:int,update_req_post:Post_structure=Body(...),db: Session = Depends(get_db),get_current_user:str=Depends(get_current_user)):
    post_query=db.query(models.Post).filter(models.Post.id == id)
    post=post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} not found")
    if post.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="you do not own this post")
    post_query.update(update_req_post.dict(),synchronize_session=False)
    db.commit()
    post_with_votes=db.query(models.Post,func.count(models.Vote.user_id).label("votes")).join(models.Vote,models.Post.id==models.Vote.post_id,isouter=True).filter(models.Post.id==id).group_by(models.Post.id).first()
    return post_with_votes

    # cursor.execute("""UPDATE posts SET title=%s,content=%s,published=%s WHERE id = %s RETURNING * """,(post.title,post.content,post.published,(str(id))))
    # # note: insted of using %s we can also use f string and give {post.title} but user can give sql command and directly attack out code so it is not used 
    # # when we use %s method sycorg makes sure that there is no weird sql code in user input
    # post_updated=cursor.fetchone()
    # conn.commit()
    # if post_updated==None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} not found")
    # return {"data": post_updated}