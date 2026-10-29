from .. import schemas,utils,models,oauth2
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
def getposts(db:Session = Depends(get_db),current_user :int =Depends(oauth2.get_current_user),limit:int =20,skip:int=0,search: str=""):
    #we just pass the query parameter stuff after ? , in decorator
    #.limit is to get certain number of rec. and .offset is to skip certain rec 
    print(limit)
    posts = db.query(models.Post).filter(models.Post.owner_id==current_user.id).filter(models.Post.content.contains(search)).offset(skip).limit(limit).all()
    return posts

@router.get("/{id}",response_model=schemas.PostResponse)
def getpost(id:int,db:Session=Depends(get_db),current_user :int =Depends(oauth2.get_current_user)):
    #Cant help it int variable is wrong, but be it anything , a pydantic model is returned
    print(current_user.email)
    # we can print its columns
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post.title)
    if not post: raiseError(id)
    return post

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.PostResponse)
def createpost(new_post: schemas.PostCreate,db:Session=Depends(get_db),current_user :int =Depends(oauth2.get_current_user)):
    print(current_user)
    #now it makes sense, why we return user, cause we can use that to fill in user data
    current_post = dict(new_post)
    current_post["owner_id"] = current_user.id
    #we know that sqlalchemy object have dot method
    new_post = models.Post(**dict(current_post))
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.patch("/{id}",status_code=status.HTTP_202_ACCEPTED,response_model=schemas.PostResponse)
def updatepost(id : int,updated_post: schemas.PostCreate,db:Session=Depends(get_db),current_user :int =Depends(oauth2.get_current_user)):
     post = db.query(models.Post).filter(models.Post.id == id)
     if not post.first(): raiseError(id)
     print(post.first().owner_id,current_user.id)
     if post.first().owner_id != current_user.id : raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorised to perform this operation")
     #we want only the person who created to delete
     post.update(dict(updated_post),synchronize_session=False)
     db.commit()
     return post.first()

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def deletepost(id:int,db:Session=Depends(get_db),current_user :int =Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first(): raiseError(id)
    print(post.first().owner_id,current_user.id)
    if post.first().owner_id != current_user.id : raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorised to perform this operation")
    #we want only the person who created to delete
    post.delete(synchronize_session=False)
    #synchronize objects in memory
    db.commit()