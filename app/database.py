from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
##SQLAlchemy is an ORM which helps in communication between fastapi and dbms, BUT IT still needs driver psycopg2
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:00000000@localhost:5432/postgres"
#url is used  for easy change of database, if we want to change database we just have to change this url and not the whole code
engine = create_engine(SQLALCHEMY_DATABASE_URL)
#engine uses psycopg2 to create multiple connections to database
#session is created for a trasaction, say you want to insert, then each time it interacts with db, one session created,so these 5 to 6 connections allows pipelining, 5to6 parallele requests or sessions
#engine is the one who has connection and has cursor object to execute
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#creates session , or generates a phone call for eg, it might not connect but just initiate, and binded to engine
Base = declarative_base()
#declarative base is a factory function which has all the functionality of sqlalchemy and is used to create models which are used to create tables in
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()