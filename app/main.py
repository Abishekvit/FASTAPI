from fastapi import FastAPI,status, HTTPException,Depends
from .database import engine
#engine is needed to bind and perform operations in db
from . import models
#models has all ORM classes inherited classes for tables to create all tables
# models.Base.metadata.create_all(bind=engine)
# we dont need to do this as alembic will do this for us, we just need to create revision and upgrade it
from . routers import post,user,auth,gpt,vote,vector

#Cross origin resource sharing, it is a security feature which allows only certain domains to access the api
origins = ["*"]

app=FastAPI()

# app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
app.include_router(vector.router)
# app.include_router(gpt.router)
#basically we are telling app class to look for routes in post.router and include them in the main app

