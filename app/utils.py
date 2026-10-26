from passlib.context import CryptContext
#passlib is a library which helps in hashing the password, so that we dont store password in plain text
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#we are saying bcrypt is hashing algorithm and deprecated auto means if we change the hashing algorithm in future, it will automatically update the password hash
def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#verify automatically converts our plain password to hashed and compares
