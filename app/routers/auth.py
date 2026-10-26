#Client ---- login username + password ---> API
#Client <---- token ----- API
#Client ---- posts, with token------> API
#Client <---- Data ----- API
#JWT includes HEADER: alg:HS256, typ:JWT
#PAYLOAD: info to send (less confedential)
#VERIFY Signature: Header + Payload + secret --> passed into signing algorithm HS256
# even if someone hacks to payload , he cant generate signature
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi import FastAPI,status, HTTPException,Depends,APIRouter,Depends
from ..database import get_db
from .. import schemas,models,utils, oauth2
from sqlalchemy.orm import Session
router = APIRouter(tags=["Authentication"])
def raiseError(id):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{id} not found")
    return

@router.post("/login",status_code=status.HTTP_200_OK)
def login(user_credentials : OAuth2PasswordRequestForm = Depends(),db : Session = Depends(get_db)):
    #oauth2 request form only fetches 2 items username and password
    #now you have to go to body x-www-encode form and pass username and password
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user: raiseError(user_credentials.username)
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id":user.id})
    #here we are creating token
    return {"token":access_token,"token_type":"bearer"}
    #bearer is a type of token which is used to access the protected routes, it is a type of access token