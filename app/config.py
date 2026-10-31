#to validate our envs
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname : str
    database_password : str
    database_port:str
    database_name : str
    database_username:str
    secret_key:str
    algorithm:str
    access_token_expire_minutes : int
    class Config:
        env_file=".env"

settings = Settings()

#as per my understanding why we need it
#directly using env gives all strings, can't control datatype
#you cant validate
#have to use BaseSettings not BaseModel for accessing env
