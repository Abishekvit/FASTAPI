from fastapi import FastAPI, Response, status, HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from .. import schemas,models,database,oauth2
router = APIRouter(prefix="/vote",tags=['Vote'])

@router.post("/",status_code=status.HTTP_201_CREATED)
def vote(vote : schemas.Vote, db: Session = Depends(database.get_db),current_user: int = Depends(oauth2.get_current_user)):
    vote_post_query = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if(not vote_post_query): raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post doesn't exist")
    # if post itself doesnt exist
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,models.Vote.user_id==current_user.id)
    #if post id exists and if the user has already voted for that post
    found_vote = vote_query.first()
    if(vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT,detail = f"use {current_user.id} has already voted on post {vote.post_id}")
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message":"successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="Vote doesn't exist")
        else:
            vote_query.delete(synchronize_session=False)
            db.commit()
            return{"message":"successfully deleted vote"}
    #simply dir =1 means want to vote, 0 means remove, if record found then dont need to upvote, if not found means create, similarly, if want to delete and record doesnt exist - error, else delete

