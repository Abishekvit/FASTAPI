import datetime
from pydantic import BaseModel
# Creating schemas for request response

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

class PostResponse(Post):
    id: int
    # created_at: datetime
    class Config:
        orm_mode = True
        #this class is to tell pydantic that orm dict can also be validated reponse

class PostCreate(Post):
    pass


