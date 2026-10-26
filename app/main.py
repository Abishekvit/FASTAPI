from fastapi import FastAPI,status, HTTPException,Depends
from . import models
#
from .database import engine,SessionLocal,get_db
from . routers import post,user,auth


models.Base.metadata.create_all(bind=engine)

app=FastAPI()
app.include_router(post.router)
#basically we are telling app class to look for routes in post.router and include them in the main app
app.include_router(user.router)
app.include_router(auth.router)

