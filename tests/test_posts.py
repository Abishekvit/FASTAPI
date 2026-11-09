import app.schemas
import pytest
def test_get_all_posts(authorized_client,test_posts):
    res = authorized_client.get("/posts/")
    res_validate = [app.schemas.PostVoteOut(**i) for i in res.json()]
    
    print(res.json())
    assert res.status_code == 200
    assert len(res_validate) == len(test_posts)

def test_unauthorized_user_get_posts(client):
    res = client.get("/posts/")
    assert res.status_code == 401

def test_auth_user_get_post(authorized_client,test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0]['id']}")
    assert res.status_code == 200

@pytest.mark.parametrize("title,content,published",[
    ("title1","content1",True), 
    ("title2","content2",False),
    ("title3","content3",True)
])
def test_create_post(authorized_client,test_user,title,content,published):  
    
    res = authorized_client.post("/posts/",json={"title":title,"content":content,"published":published})
    created_post = app.schemas.PostResponse(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']

def test_unauthorized_user_delete_post(client):
    res = client.delete(f"/posts/1")
    assert res.status_code == 401

def test_authorized_user_delete_post_otheruser(authorized_client,test_posts_2):
    res = authorized_client.delete(f"/posts/{test_posts_2[0]['id']}")
    assert res.status_code == 403

def test_authorized_user_update_post_otheruser(authorized_client,test_posts_2):
    res = authorized_client.patch(f"/posts/{test_posts_2[0]['id']}",json={"title":"Doraemon","content":"Children"})
    assert res.status_code ==403
def test_authorized_user_update_post(authorized_client,test_posts):
    res = authorized_client.patch(f"/posts/{test_posts[0]['id']}",json={"title":"Doraemon","content":"Children"})
    assert res.status_code == 202