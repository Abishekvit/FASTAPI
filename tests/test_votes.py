import pytest
import app.schemas

def test_vote_on_post(authorized_client,test_votes):
   res = authorized_client.post("/vote/",json=test_votes[0])
   assert res.status_code == 409

def test_unvote_empty(authorized_client,test_votes):
    res = authorized_client.post("/vote/",json=test_votes[2])
    assert res.status_code == 404
