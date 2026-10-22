from fastapi import FastAPI,status, Response, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
app=FastAPI()

records = []
def findPostIndex(id):
    for i in range(len(records)):
        if records[i]["id"]==id: return i
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{id} not found")
    return

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

class UpdatedPost(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: bool = True
    rating: Optional[int] = None

while True:
    try:
        conn = psycopg2.connect(host='localhost',database='postgres',user='postgres',password='00000000',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Databse connection successful")
        break
    except Exception as error:
        print("Connection failed")
        print("Error: ",error)
        time.sleep(2)

@app.get("/")
def root():
    return{"message":"Hello World"}

@app.get("/posts")
def getposts():
    return {"content":records}

@app.get("/posts/{id}")
def getpost(id:int):
    postidx = findPostIndex(id)
    return{"message":"Post exists","post_content":records[postidx]}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def createpost(new_post: Post):
    new_post = dict(new_post)
    new_post["id"] = randrange(1,1000000)
    records.append(new_post)
    print(f"New record created {new_post}")
    return{"message":"Post created successfully"}

@app.patch("/posts/{id}",status_code=status.HTTP_202_ACCEPTED)
def updatepost(id : int,updated_post: UpdatedPost):
    updated_post = dict(updated_post)
    postidx = findPostIndex(id)
    post = records[postidx]
    for i in updated_post:
        if updated_post[i]!=None :
            post[i]=updated_post[i]
    records[postidx]=post
    print(f"Updated the post : {post}")
    return({"message":f"updated record of id : {id}"})

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def deletepost(id:int):
    postidx = findPostIndex(id)
    records.pop(postidx)
    print(f"Record {id} deleted")


            
    


