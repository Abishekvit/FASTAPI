from .. import schemas,utils,models
from ..database import engine,SessionLocal,get_db
from sqlalchemy.orm import Session
from fastapi import FastAPI,status, HTTPException,Depends,APIRouter
router = APIRouter(prefix="/posts",tags=["Posts"])
#we created a router object
#it groups all the routers together and we can include them in main.py
def raiseError(id):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{id} not found")
    return



@router.get("/",response_model=list[schemas.PostResponse]) #as it is list of dict, we have to tell fastapi it is a list
def getposts(db:Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@router.get("/{id}",response_model=schemas.PostResponse)
def getpost(id:int,db:Session=Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)
    if not post: raiseError(id)
    return post

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.PostResponse)
def createpost(new_post: schemas.PostCreate,db:Session=Depends(get_db)):
    new_post = models.Post(**dict(new_post))
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.patch("/{id}",status_code=status.HTTP_202_ACCEPTED,response_model=schemas.PostResponse)
def updatepost(id : int,updated_post: schemas.PostCreate,db:Session=Depends(get_db)):
     post = db.query(models.Post).filter(models.Post.id == id)
     if not post.first(): raiseError(id)
     post.update(dict(updated_post),synchronize_session=False)
     db.commit()
     return post.first()

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def deletepost(id:int,db:Session=Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first(): raiseError(id)
    post.delete(synchronize_session=False)
    #synchronize objects in memory
    db.commit()