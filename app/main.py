#FASTAPI TALKS TO DBMS USING PSYCOPG2 AND SQL QUERIES
#FASTAPI -----PYTHON ---ORM----PSYCOG2,SQL----DBMS
#SQLAlchemy - most popular ORM(No relationship with Fastapi, can be used with any framework)
from fastapi import FastAPI,status, HTTPException,Depends,APIRouter
#SQL Alchemy doesn't know to talk to database, so we still need PSYCOPG2
#psycopg2 is an adapter for Postgre SQL which helps in communication between fastapi and dbms
from . import models
from .database import engine,SessionLocal,get_db
from . routers import post,user,auth


models.Base.metadata.create_all(bind=engine)
#our post class info is saved in Base.metadata, we are trying to push every change using engine
#create all checks is already table there, ignore, else fetch
#bind=engine to get the connection string of which database
app=FastAPI()
app.include_router(post.router)
#basically we are telling app class to look for routes in post.router and include them in the main app
app.include_router(user.router)
app.include_router(auth.router)

