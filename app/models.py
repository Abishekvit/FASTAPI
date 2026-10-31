#We are gonna define schema
from sqlalchemy import Column, Integer, String,Boolean,ForeignKey
from .database import Base
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
#we imported relationship 

#Inherited properties and object mapping of Base class

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer,primary_key=True,nullable=False)
    title = Column(String,nullable=False)
    content = Column(String,nullable=False)
    published = Column(Boolean,server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,server_default=func.now())
    #there we has primary key and is null in postgre
    #we use alembic to create migration file and it can change the existing table also ulike rn, where if table exists it wont alter
    owner_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    #owner id Foreign key
    owner = relationship("User")
    #relationship is like NATURAL JOIN, automatically joins based on foreign key

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,nullable=False)
    email = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,server_default=func.now())

class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(Integer,ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer,ForeignKey(
            "posts.id", ondelete="CASCADE"), primary_key=True)