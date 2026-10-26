from datetime import datetime
from pydantic import BaseModel, EmailStr
# Creating schemas for request response

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

class PostResponse(Post):
    id: int
    # created_at: datetime
    class Config:
        from_attributes = True
        #this class is to tell pydantic that orm dict can also be validated reponse

class PostCreate(Post):
    pass

class UserCreate(BaseModel):
    email: EmailStr
    password: str
#pydantic model can validate password
class UserResponse(BaseModel):
    id : int
    email: EmailStr
    created_at: datetime
    class Config:
            from_attributes = True
class UserLogin(BaseModel):
     email: EmailStr
     password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
     id: int | None = None
