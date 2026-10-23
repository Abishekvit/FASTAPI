from fastapi import FastAPI,status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
#psycopg2 is an adapter for Postgre SQL which helps in communication between fastapi and dbms
import time

app=FastAPI()

records = []
def raiseError(id):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{id} not found")
    return

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

while True:
    try:
        conn = psycopg2.connect(host='localhost',database='postgres',user='postgres',password='00000000',cursor_factory=RealDictCursor)
        #conn controls session between fastapi and database AND trasactions like insert delete commit etc.
        cursor = conn.cursor()
        #cursor is the man behind the operations carrying out everything 
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
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    # returns list of tuple of values
    return {"content":posts}

@app.get("/posts/{id}")
def getpost(id:int):
    cursor.execute("""SELECT * from posts WHERE id = %s""",(str(id),))
    obtained_post = cursor.fetchone()
    if not obtained_post: raiseError(id)
    return{"message":"Post exists","post_content":obtained_post}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def createpost(new_post: Post):
    new_post = dict(new_post)
    cursor.execute("""INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *""",(new_post["title"],new_post["content"],new_post["published"]))
    # triple quote is a saftely layer also where sql injection is prevented, that is why we have to write %s all that
    created_post = cursor.fetchone()
    # return tuple of values
    conn.commit()
    #to commit changes to database
    print(f"New record created {created_post}")
    return{"message":f"Post created successfully : {created_post}"}

@app.patch("/posts/{id}",status_code=status.HTTP_202_ACCEPTED)
def updatepost(id : int,updated_post: Post):
    updated_post = dict(updated_post)
    cursor.execute("""UPDATE posts SET title= %s, content=%s, published = %s WHERE id = %s RETURNING *""",(updated_post["title"],updated_post["content"],updated_post["published"],str(id)))
    changed_post = cursor.fetchone()
    conn.commit()
    print(f"Updated the post : {changed_post}")
    return({"message":f"updated record of id : {id} {updated_post}"})

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def deletepost(id:int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""",(str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    print(f"Record {id} deleted : {deleted_post}")

#WE DIDNT USE ORM, this is general way using driver where we talk with dbms using sql queries and we have curson and conn, nextly we will see how ORM's help us code is python and they take care to DO OBJECT RELATIONAL MAPPING