#FASTAPI TALKS TO DBMS USING PSYCOPG2 AND SQL QUERIES
#FASTAPI -----PYTHON ---ORM----PSYCOG2,SQL----DBMS
#SQLAlchemy - most popular ORM(No relationship with Fastapi, can be used with any framework)
from fastapi import FastAPI,status, HTTPException,Depends
from pydantic import BaseModel
#SQL Alchemy doesn't know to talk to database, so we still need PSYCOPG2
import psycopg2
from psycopg2.extras import RealDictCursor
#psycopg2 is an adapter for Postgre SQL which helps in communication between fastapi and dbms
import time
from . import models
from .database import engine,SessionLocal,get_db
from sqlalchemy.orm import Session
  


models.Base.metadata.create_all(bind=engine)
#our post class info is saved in Base.metadata, we are trying to push every change using engine
#create all checks is already table there, ignore, else fetch
#bind=engine to get the connection string of which database
app=FastAPI()

def raiseError(id):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{id} not found")
    return

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

@app.get("/")
def root():
    return{"message":"Hello World"}

@app.get("/sqlalchemy")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    #db is session state and it has query method which sees post class for table and fetches evrything
    return{"data" : posts}
#db Session uses Depends get_db : get_db creates session and return that to api request 

@app.get("/posts")
def getposts(db:Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return{"data": posts}

@app.get("/posts/{id}")
def getpost(id:int,db:Session=Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).all()
    print(post)
    if not post: raiseError(id)
    return {"post_detail": post}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def createpost(new_post: Post,db:Session=Depends(get_db)):
    new_post = models.Post(**dict(new_post))
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data":new_post}

@app.patch("/posts/{id}",status_code=status.HTTP_202_ACCEPTED)
def updatepost(id : int,updated_post: Post,db:Session=Depends(get_db)):
     post = db.query(models.Post).filter(models.Post.id == id)
     if not post.first(): raiseError(id)
     post.update(dict(updated_post),synchronize_session=False)
     db.commit()
     return {"data": post.first() }

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def deletepost(id:int,db:Session=Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first(): raiseError(id)
    post.delete(synchronize_session=False)
    #synchronize objects in memory
    db.commit()
