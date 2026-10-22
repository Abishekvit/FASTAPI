from fastapi import FastAPI,status,HTTPException
# FastAPI is a class 
# status is for return status code to user
# HTTPException is to raise an exception for user and give reason why

from pydantic import BaseModel
#pydantic is a tool which has connection with FastAPI, validation class is BaseModel
#it also allows us to parse the request in dictionary form

from random import randrange

app=FastAPI()
#class instance created

records = []
def findPostIndex(id):
    for i in range(len(records)):
        if records[i]["id"]==id: return i
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{id} not found")
    return
#give the exception if id not found while get ,delete or update 

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None = None
#Post class inherts features of BaseModel, so validation happens

class UpdatedPost(BaseModel):
    title: str| None = None
    content: str| None = None
    published: bool = True
    rating: int | None = None
#UpdatedPost is made to validate request for update

@app.get("/")
def root():
    return{"message":"Hello World"}
#app is class, it has get decorator factory: it creates custom decorator according to routes
# and this function uses our root function for message

@app.get("/posts")
def getposts():
    return {"content":records}

@app.get("/posts/{id}")
def getpost(id:int):
    postidx = findPostIndex(id)
    return{"message":"Post exists","post_content":records[postidx]}
#getpost fucntion goes inside get function inside decroator fucntion, so the decorator function must get these properties of id, from parent fucntion

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def createpost(new_post: Post):
    new_post = dict(new_post)
    new_post["id"] = randrange(1,1000000)
    records.append(new_post)
    print(f"New record created {new_post}")
    return{"message":"Post created successfully"}
#custom decorator made using routes and status code to return
#fastapi loops to check if there is arequest, then validates it after seeing Post
#status code outside becuase fastapi routes before the function is even called
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

#A decoratory factory takes arguments adn creates custom decorator
#the decorator(func), takes function, uses function and custom parameters , and thereby returns whole decrator fucntion is name name and calls it

