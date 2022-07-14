from fastapi import APIRouter,status,HTTPException,Depends
from schemas import Vote
from oauth2 import get_current_user
from database import get_db
from sqlalchemy.orm import Session
import models

router=APIRouter(prefix="/vote",tags=["Votes"])

@router.post("/",status_code=status.HTTP_202_ACCEPTED)
def vote(vote:Vote,db: Session = Depends(get_db),get_current_user:str=Depends(get_current_user)):
    post_exists=db.query(models.Vote).filter(models.Vote.post_id==vote.post_id).first()
    if post_exists == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="the post you are trying to vote does not exists")
    voted=db.query(models.Vote).filter(models.Vote.post_id==vote.post_id,models.Vote.user_id==get_current_user.id)
    if_already_voted=voted.first()
    if vote.dir==1:
        if if_already_voted !=None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="this post is already voted by you")
        new_vote=models.Vote(user_id=get_current_user.id,post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        return {"message":f"successfully voted for post {vote.post_id}"}
    else:
        if if_already_voted == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="you have not voted it primarily to delete it")
        voted.delete(synchronize_session=False)
        db.commit()
        return {"message":"vote for this post is deleted"}

