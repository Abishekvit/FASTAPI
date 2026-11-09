# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.main import app
# from app import schemas
# from app.config import settings
# from app.database import get_db,Base
# from alembic import command
# import pytest

# SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/fastapi_test'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# app.dependency_overrides[get_db] = override_get_db
#our aim is to create new table for testing while keeping code intact, so this override function helps us to replace the dependency of session with our new session with a different database



# #client does not send the message over network, it uses the code inside the route processes it and gets the output
# @pytest.fixture(scope="module")
# #scope being module, client wont be destroyed in every function, it will stay intact for entire module and then when we run again it will drop at end
# def client():
#     #run our code before we run our test
#     Base.metadata.create_all(bind=engine)
#     yield TestClient(app)
#     Base.metadata.drop_all(bind=engine)
#     # run our code after our test finishes
#     #yield pauses the function until its use is done then unpauses and drops all
# #so while testing we can create tables and drop when work is done 
