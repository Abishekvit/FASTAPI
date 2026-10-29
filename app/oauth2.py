from datetime import datetime, timedelta
#we are importing datetime and timedelta to set the expiration time of the token

from jose import JWTError, jwt

from . import schemas,database,models
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#tokenurl is just metadata, you need to write, but no use, just semantics
#this check authorization header for token, if not present, it will raise 401 error

#SECRET_KEY
#Algo 
#Expiration time

from .config import settings
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    #data is payload
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # with data we are storing expiration time in payload copy
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            #we get payload back by . decode
            id: str = payload.get("user_id")
            if id is None:
                raise credentials_exception
            token_data = schemas.TokenData(id=id)
            #to validate token data we are using pydantic model TokenData
        except JWTError:
            raise credentials_exception
        return dict(token_data)
# jwt guarantees that no one tampers with data it doesnt guarantee, no one can access except you and all, if someone gets the jwt, you are gone

def get_current_user(token: str = Depends(oauth2_scheme),db : Session = Depends(database.get_db)):
    #Depends(oauth2_scheme) will check for token in authorization header and pass it to this function
    #Depends is used will call the function and pass the return value to this function - SOMETHING MORE USEFUL WE DONT KNOW
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    #headers just to give client more clarity, it is not needed, but it is a good practice to include it
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token["id"]).first()
    #models.User is queried to fetch the table ,and then we filter
    return user