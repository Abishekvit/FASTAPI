from app import schemas
# from .database import client
import pytest
from app.config import settings
from jose import jwt
@pytest.fixture
def test_user(client):
    user_data = {"email":"abc@gmail.com","password":"00000000"}
    res = client.post("/users/",json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

def test_root(client):
    res = client.get("/")
    print(res.json())
    assert res.json() == "Hello"
    assert res.status_code == 200

def test_create_user(client):
    res = client.post("/users",json={"email":"hello1234@gmail.com","password":"password123"})
    new_user = schemas.UserResponse(**res.json())
    # when we send somethign outside , the reponse schema just checks, it cant send pydantic object
    assert new_user.email == "hello1234@gmail.com"
    print(res.json())
    assert res.status_code ==201

def test_login_user(client,test_user):
    res = client.post('/login',data={"username":test_user["email"],"password":test_user["password"]})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,settings.secret_key,algorithms=[settings.algorithm])
    assert payload.get("user_id") == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200
@pytest.mark.parametrize("email,password,status_code",[
    ("abc@gmail.com", "wrongpassword", 403),
    ("nonexistent@example.com", "password123", 404),
])
def test_incorrect_login(client,test_user,email,password,status_code):
    res = client.post('/login',data={"username":email,"password":password})
    assert res.status_code == status_code
# do pytest --disable-warnings 
# do pytest --disable-warnings -v -x, this -x means it will stop after first failure, else it will continue to test other stuff also after failure