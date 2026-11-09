from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app import schemas
from app.config import settings
from app.database import get_db,Base
from alembic import command
import pytest
from sqlalchemy import text
from app.oauth2 import create_access_token
SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/fastapi_test'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
#our aim is to create new table for testing while keeping code intact, so this override function helps us to replace the dependency of session with our new session with a different database



#client does not send the message over network, it uses the code inside the route processes it and gets the output
@pytest.fixture(scope="function")
#scope being module, client wont be destroyed in every function, it will stay intact for entire module and then when we run again it will drop at end
def client():
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        connection.commit()
    #run our code before we run our test
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)
    # run our code after our test finishes
    #yield pauses the function until its use is done then unpauses and drops all
#so while testing we can create tables and drop when work is done 
@pytest.fixture
def client_2():
    return TestClient(app)
@pytest.fixture
def test_user(client):
    user_data = {"email":"abc@gmail.com","password":"00000000"}
    res = client.post("/users/",json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user_2(client_2):
    user_data = {"email":"abcd@gmail.com","password":"00000000"}
    res = client_2.post("/users/",json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user
## This file is accessible to all tests , the fixtures 

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id":test_user['id']})

@pytest.fixture
def token_2(test_user_2):
    return create_access_token({"user_id":test_user_2['id']})

@pytest.fixture
def authorized_client(client,token):
    client.headers = {
        **client.headers,
        "Authorization":f"Bearer {token}"
    }
    return client

@pytest.fixture
def authorized_client_2(client_2,token_2):
    client_2.headers = {
        **client_2.headers,
        "Authorization":f"Bearer {token_2}"
    }
    return client_2
## so we are doing this cause we want the auth header to be filled by token 

@pytest.fixture
def test_posts(authorized_client,test_user,):
    posts_data = [{"title":"first title","content":"first content","owner_id":test_user['id']},
                {"title":"2nd title","content":"2nd content","owner_id":test_user['id']},
                {"title":"3rd title","content":"3rd content","owner_id":test_user['id']}]
    data_out =[]
    for i in posts_data:
        res = authorized_client.post("/posts/",json=i)
        print(res.json())
        data_out.append(res.json())
    return data_out

@pytest.fixture
def test_posts_2(authorized_client_2,test_user_2,):
    posts_data = [{"title":"fi title","content":"first content","owner_id":test_user_2['id']},
                {"title":"2 title","content":"2nd content","owner_id":test_user_2['id']},
                {"title":"3 title","content":"3rd content","owner_id":test_user_2['id']}]
    data_out =[]
    for i in posts_data:
        res = authorized_client_2.post("/posts/",json=i)
        print(res.json())
        data_out.append(res.json())
    return data_out

@pytest.fixture
def test_votes(authorized_client,test_posts):
    res = authorized_client.post("/vote/",json={"post_id":test_posts[0]['id'],"dir":1})
    res = authorized_client.post("/vote/",json={"post_id":test_posts[1]['id'],"dir":1})
    res = authorized_client.post("/vote/",json={"post_id":test_posts[1]['id'],"dir":0})
    res = authorized_client.post("/vote/",json={"post_id":test_posts[2]['id'],"dir":1})
    some_votes = [{"post_id":test_posts[0]['id'],"dir":1},
                  {"post_id":test_posts[1]['id'],"dir":1},  
                  {"post_id":test_posts[1]['id'],"dir":0},
                  {"post_id":test_posts[2]['id'],"dir":1}]
    return some_votes

import pymupdf
import pytest

@pytest.fixture
def test_documents(authorized_client):
    documents = [
        ("fastapi.pdf", "DummyFastAPI is a Python web Hollywood Actor. It uses Pydantic for validation."),
            ("postgresql.pdf", "PostgreSQL ID IS 00929 is a relational database. It supports vector similarity search."),
            ("rag.pdf", "Retrieval Augmented Generation combines document retrieval with LLM generation.")
    ]

    uploaded = []

    for filename, content in documents:
        pdf = pymupdf.open()
        page = pdf.new_page()
        page.insert_text((50, 50), content)

        pdf_bytes = pdf.tobytes()
        pdf.close()

        res = authorized_client.post(
            "/documents/",
            files={"file": (filename, pdf_bytes, "application/pdf")}
        )

        assert res.status_code == 201, res.json()
        uploaded.append(res.json())

    return uploaded