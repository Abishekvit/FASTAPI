#We are gonna define schema
from sqlalchemy import Column, Integer, String,Boolean
from .database import Base
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
#Inherited properties and object mapping of Base class
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer,primary_key=True,nullable=False)
    title = Column(String,nullable=False)
    content = Column(String,nullable=False)
    published = Column(Boolean,server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,server_default=func.now())
    #there we has primary key and is null in postgre
    #we use alembic to create migration file and it can chnage the existing table also ulike rn, where if table exists it wont alter