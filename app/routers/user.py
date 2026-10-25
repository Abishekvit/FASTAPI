from .. import schemas,utils,models
from ..database import engine,SessionLocal,get_db
from sqlalchemy.orm import Session
from fastapi import FastAPI,status, HTTPException,Depends,APIRouter

router = APIRouter(prefix="/users",tags=["Users"])




def raiseError(id):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{id} not found")
    return
@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.UserResponse)
def create_user(new_user : schemas.UserCreate,db:Session=Depends(get_db)):
    hashed_password = utils.hash(new_user.password)
    new_user.password = hashed_password
    new_user = models.User(**dict(new_user))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}",response_model=schemas.UserResponse,status_code=status.HTTP_200_OK)
def get_user(id:int,db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user: raiseError(id)
    return user